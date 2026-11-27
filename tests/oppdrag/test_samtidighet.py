"""Samtidige forespørsler med hver sin tilkobling (AD-2, §4.0, spec 2.5).

Testene i resten av pakken deler én tilkobling (tests/conftest.py), så samtidighet syns
ikke der. Her får to tråder hver sin `Session` fra `motor`. Den første holder
transaksjonen åpen et øyeblikk etter den betingede `UPDATE`-en, så den andre må vente:
SQLite på låsen (`BEGIN IMMEDIATE`), Postgres på raden. Når den første har committet,
endrer den andres `UPDATE` 0 rader, og det gir `Konflikt`. Nøyaktig én lykkes.

Radene committes og slettes i `finally`. Kjøres mot SQLite lokalt og mot Postgres i
jobben `test-postgres` i CI (`TEST_DATABASE_URL`).
"""

from __future__ import annotations

import secrets
import threading
import time
from collections.abc import Callable, Iterator
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import Engine, delete, select
from sqlalchemy.orm import Session

from app.core import tid
from app.core.feil import Konflikt
from app.identity.models import Bruker
from app.oppdrag.models import Oppdrag
from app.oppdrag.service import avbryt_oppdrag, rediger_oppdrag

HOLD = 0.3  # sekunder den første holder transaksjonen åpen etter UPDATE-en
VENT = 10  # sekunder før testen gir opp en tråd


@pytest.fixture
def oppdrag_i_egen_tilkobling(motor: Engine) -> Iterator[tuple[int, int]]:
    """(oppdrag_id, eier_id): en bruker og et åpent oppdrag, committet. Slettes etterpå."""
    na = datetime.now(timezone.utc)
    with Session(motor) as db:
        bruker = Bruker(
            navn="Samtidig Kari",
            epost=f"samtidig-{secrets.token_hex(4)}@eksempel.no",
            telefon="40000000",
            postnummer="0571",
            fodselsdato=date(1954, 5, 3),
            opprettet=na,
            passord_hash=None,
        )
        db.add(bruker)
        db.flush()
        oppdrag = Oppdrag(
            oppdragsgiver_id=bruker.id,
            tittel="Måke snø i innkjørselen",
            beskrivelse="Trenger noen som kan måke snø i innkjørselen min i morgen.",
            kategori="snomaking",
            postnummer="0571",
            tidspunkt=na + timedelta(days=2),
            belop=200,
            status="apen",
            versjon=1,
            skjema_id=secrets.token_urlsafe(16),
            opprettet=na,
        )
        db.add(oppdrag)
        db.commit()
        ider = (oppdrag.id, bruker.id)
    try:
        yield ider
    finally:
        with Session(motor) as db:
            db.execute(delete(Oppdrag).where(Oppdrag.id == ider[0]))
            db.execute(delete(Bruker).where(Bruker.id == ider[1]))
            db.commit()


def _avbryt(oppdrag_id: int, eier_id: int) -> Callable[[Session], None]:
    return lambda db: avbryt_oppdrag(db, oppdrag_id, oppdragsgiver_id=eier_id)


def _rediger(oppdrag_id: int, eier_id: int) -> Callable[[Session], None]:
    dato, klokkeslett = tid.skjemaverdier(datetime.now(timezone.utc) + timedelta(days=3))
    felt = {
        "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min i morgen.",
        "tittel": "Endret samtidig",
        "kategori": "snomaking",
        "postnummer": "0571",
        "dato": dato,
        "klokkeslett": klokkeslett,
        "tilbud": "belop",
        "belop": "300",
    }
    return lambda db: rediger_oppdrag(db, oppdrag_id, oppdragsgiver_id=eier_id, **felt)


def kjor_samtidig(
    motor: Engine, forste: Callable[[Session], None], andre: Callable[[Session], None]
) -> tuple[list, float]:
    """Kjører handlingene i hver sin tråd og tilkobling.

    Gir utfallet per tråd ("ok" eller unntaket) og hvor lenge den andre tråden brukte på
    sin transaksjon. Den tiden viser at transaksjonene faktisk overlappet: den andre måtte
    vente på at den første committet.

    Begge starter ved samme `Barrier`. Den første gjør UPDATE-en, gir signal og holder
    transaksjonen åpen i `HOLD` sekunder. Den andre starter sin transaksjon etter signalet
    og må vente på den første.
    """
    start = threading.Barrier(2, timeout=VENT)
    oppdatert = threading.Event()
    utfall: list = [None, None]
    ventetid = [0.0]

    def trad(nr: int, handling: Callable[[Session], None]) -> None:
        try:
            start.wait()
            with Session(motor) as db:
                if nr == 1:
                    oppdatert.wait(VENT)
                start_tid = time.monotonic()
                try:
                    with db.begin():
                        handling(db)
                        if nr == 0:
                            oppdatert.set()
                            time.sleep(HOLD)
                finally:
                    if nr == 1:
                        ventetid[0] = time.monotonic() - start_tid
            utfall[nr] = "ok"
        except BaseException as feil:  # noqa: BLE001 – utfallet sjekkes i testen
            oppdatert.set()
            utfall[nr] = feil

    trader = [threading.Thread(target=trad, args=(nr, h)) for nr, h in enumerate((forste, andre))]
    for t in trader:
        t.start()
    for t in trader:
        t.join(VENT)
        assert not t.is_alive(), "en tråd ble ikke ferdig"
    return utfall, ventetid[0]


def les(motor: Engine, oppdrag_id: int) -> tuple[str, int, str]:
    with Session(motor) as db:
        rad = db.execute(
            select(Oppdrag.status, Oppdrag.versjon, Oppdrag.tittel).where(Oppdrag.id == oppdrag_id)
        ).one()
    return rad.status, rad.versjon, rad.tittel


def test_to_samtidige_avbrudd_gir_ett_avbrudd_og_en_konflikt(motor: Engine, oppdrag_i_egen_tilkobling) -> None:
    """AD-2, §4.0: «Ja, avbryt oppdraget» i to faner samtidig. Nøyaktig én lykkes."""
    oppdrag_id, eier_id = oppdrag_i_egen_tilkobling
    utfall, ventetid = kjor_samtidig(motor, _avbryt(oppdrag_id, eier_id), _avbryt(oppdrag_id, eier_id))
    assert ventetid >= HOLD * 0.8, ventetid  # transaksjonene overlappet
    assert utfall[0] == "ok", utfall
    assert isinstance(utfall[1], Konflikt), utfall
    assert les(motor, oppdrag_id) == ("avbrutt", 2, "Måke snø i innkjørselen")


def test_avbrudd_og_samtidig_redigering_gir_en_konflikt(motor: Engine, oppdrag_i_egen_tilkobling) -> None:
    """AD-2, FR-7: avbrudd i fane 1 og «Lagre endringer» i fane 2. Redigeringen gir `Konflikt`."""
    oppdrag_id, eier_id = oppdrag_i_egen_tilkobling
    utfall, ventetid = kjor_samtidig(motor, _avbryt(oppdrag_id, eier_id), _rediger(oppdrag_id, eier_id))
    assert ventetid >= HOLD * 0.8, ventetid  # transaksjonene overlappet
    assert utfall[0] == "ok", utfall
    assert isinstance(utfall[1], Konflikt), utfall
    assert les(motor, oppdrag_id) == ("avbrutt", 2, "Måke snø i innkjørselen")
