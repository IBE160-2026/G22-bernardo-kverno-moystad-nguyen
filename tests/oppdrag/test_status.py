"""Statusfunksjonen `endre_status` (AD-2, AR-12).

Én betinget `UPDATE` som endrer status og øker `versjon`. De tre utfallene:
endret, `FinnesIkke` (finnes ikke eller feil eier) og `Konflikt` (noen andre
har endret raden, eller tidspunktet er passert). Ulovlige overganger gir
`ValueError` før databasen røres.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.feil import FinnesIkke, Konflikt
from app.oppdrag.models import Oppdrag
from app.oppdrag.service import KONFLIKT, OVERGANGER, detaljer_url, endre_status

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


def les(db, oppdrag_id: int) -> tuple[str, int]:
    db.expire_all()
    rad = db.execute(select(Oppdrag.status, Oppdrag.versjon).where(Oppdrag.id == oppdrag_id)).one()
    return rad.status, rad.versjon


def test_endret_status_og_versjon(db, lag_oppdrag) -> None:
    """AD-2: status endres og `versjon` øker med 1."""
    oppdrag = lag_oppdrag()
    endre_status(db, oppdrag.id, fra="apen", til="avbrutt", oppdragsgiver_id=oppdrag.oppdragsgiver_id)
    assert les(db, oppdrag.id) == ("avbrutt", 2)


def test_fra_kan_vaere_flere_statuser(db, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(status="hjelper_valgt")
    endre_status(db, oppdrag.id, fra=("apen", "hjelper_valgt"), til="avbrutt")
    assert les(db, oppdrag.id) == ("avbrutt", 2)


def test_ikke_passert_godtar_tidspunkt_fram_i_tid(db, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(tidspunkt=T0 + timedelta(minutes=1))
    endre_status(db, oppdrag.id, fra="apen", til="avbrutt", ikke_passert=True)
    assert les(db, oppdrag.id) == ("avbrutt", 2)


def test_finnes_ikke(db) -> None:
    with pytest.raises(FinnesIkke):
        endre_status(db, 999_999, fra="apen", til="avbrutt")


def test_feil_eier_gir_finnes_ikke_og_ingen_endring(db, lag_oppdrag, lag_bruker) -> None:
    """FR-7, FR-9: en annen enn oppdragsgiveren får samme svar som om oppdraget ikke fantes."""
    oppdrag = lag_oppdrag()
    annen = lag_bruker()
    with pytest.raises(FinnesIkke):
        endre_status(db, oppdrag.id, fra="apen", til="avbrutt", oppdragsgiver_id=annen.id)
    assert les(db, oppdrag.id) == ("apen", 1)


def test_endret_av_andre_gir_konflikt(db, lag_oppdrag) -> None:
    """AD-2: andre gang samme overgang prøves, er statusen allerede endret."""
    oppdrag = lag_oppdrag()
    eier = oppdrag.oppdragsgiver_id
    endre_status(db, oppdrag.id, fra="apen", til="avbrutt", oppdragsgiver_id=eier)
    with pytest.raises(Konflikt) as konflikt:
        endre_status(db, oppdrag.id, fra="apen", til="avbrutt", oppdragsgiver_id=eier)
    assert konflikt.value.melding == KONFLIKT == "Oppdraget er endret. Last siden på nytt."
    assert konflikt.value.til_url == detaljer_url(oppdrag.id)
    assert les(db, oppdrag.id) == ("avbrutt", 2)


@pytest.mark.parametrize("tidspunkt", [T0, T0 - timedelta(days=1)], ids=["lik-naa", "passert"])
def test_passert_tidspunkt_gir_konflikt(db, lag_oppdrag, tidspunkt: datetime) -> None:
    """AD-2: `tidspunkt > nå` står i WHERE når handlingen krever at det ikke er passert."""
    oppdrag = lag_oppdrag(tidspunkt=tidspunkt)
    with pytest.raises(Konflikt):
        endre_status(db, oppdrag.id, fra="apen", til="avbrutt", ikke_passert=True)
    assert les(db, oppdrag.id) == ("apen", 1)


@pytest.mark.parametrize(
    ("fra", "til"),
    [("apen", "utfort"), ("avbrutt", "apen"), ("utfort", "apen"), ("apen", "apen"), ("apen", "ukjent")],
)
def test_ulovlig_overgang_gir_valueerror(db, lag_oppdrag, fra: str, til: str) -> None:
    oppdrag = lag_oppdrag(status=fra if fra != "ukjent" else "apen")
    with pytest.raises(ValueError):
        endre_status(db, oppdrag.id, fra=fra, til=til)
    assert les(db, oppdrag.id)[1] == 1


def test_tom_fra_gir_valueerror(db) -> None:
    with pytest.raises(ValueError):
        endre_status(db, 1, fra=(), til="avbrutt")


def test_overgangene_folger_statusmodellen() -> None:
    """PRD §4.0: Utført og Avbrutt er endelige; Hjelper valgt kan gå tilbake til Åpen."""
    assert not any(fra in ("utfort", "avbrutt") for fra, _ in OVERGANGER)
    assert ("hjelper_valgt", "apen") in OVERGANGER
    assert ("apen", "utfort") not in OVERGANGER
