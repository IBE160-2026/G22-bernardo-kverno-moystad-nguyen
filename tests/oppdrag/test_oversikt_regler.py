"""Reglene for oversikten og erfaringen, direkte mot servicen (FR-8, FR-10, FR-11, FR-21, AD-3, AD-16, AR-13).

Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid. «Utgått» testes med
`sett_na` på begge sider av tidspunktet.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.domene import Erfaring
from app.core.feil import Konflikt
from app.oppdrag.models import Oppdrag
from app.oppdrag.service import (
    OppdragKort,
    endre_status,
    erfaring,
    ledige_oppdrag,
    utgatt,
)

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


@pytest.fixture
def ola(lag_bruker):
    return lag_bruker(navn="Ola Hansen", postnummer="0571")


def titler(kort: list[OppdragKort]) -> list[str]:
    return [k.tittel for k in kort]


# ---------- utvalget (FR-10) ----------


def test_utvalget(db, ola, lag_bruker, lag_oppdrag) -> None:
    """FR-8, FR-10: åpne, ikke passert, i postnummeret og ikke egne."""
    kari = lag_bruker()
    lag_oppdrag(oppdragsgiver=kari, tittel="Vises")
    lag_oppdrag(oppdragsgiver=ola, tittel="Eget")
    lag_oppdrag(oppdragsgiver=kari, tittel="Avbrutt", status="avbrutt")
    lag_oppdrag(oppdragsgiver=kari, tittel="Hjelper valgt", status="hjelper_valgt")
    lag_oppdrag(oppdragsgiver=kari, tittel="Utført", status="utfort")
    lag_oppdrag(oppdragsgiver=kari, tittel="Utgått", tidspunkt=T0 - timedelta(hours=1))
    lag_oppdrag(oppdragsgiver=kari, tittel="Annet postnummer", postnummer="0572")
    kort = ledige_oppdrag(db, postnummer="0571", kategori=None, bruker_id=ola.id)
    assert titler(kort) == ["Vises"]


def test_kategori(db, ola, lag_oppdrag) -> None:
    """FR-11: med kategori vises bare den; `None` gir alle."""
    lag_oppdrag(tittel="Snø", kategori="snomaking")
    lag_oppdrag(tittel="Hage", kategori="hage", tidspunkt=T0 + timedelta(days=2))
    assert titler(ledige_oppdrag(db, postnummer="0571", kategori="hage", bruker_id=ola.id)) == ["Hage"]
    assert titler(ledige_oppdrag(db, postnummer="0571", kategori=None, bruker_id=ola.id)) == ["Snø", "Hage"]


def test_annet_postnummer(db, ola, lag_oppdrag) -> None:
    """FR-11: et annet postnummer erstatter eget."""
    lag_oppdrag(tittel="Bergen", postnummer="5006")
    lag_oppdrag(tittel="Oslo")
    assert titler(ledige_oppdrag(db, postnummer="5006", kategori=None, bruker_id=ola.id)) == ["Bergen"]


# ---------- sortering (FR-10) ----------


def test_sortering_etter_tidspunkt_lagt_ut_og_id(db, ola, lag_oppdrag) -> None:
    """FR-10: tidligste tidspunkt først; ved likt tidspunkt eldste utlagte først, så id."""
    samme = T0 + timedelta(days=2)
    lag_oppdrag(tittel="Senere", tidspunkt=T0 + timedelta(days=3))
    lag_oppdrag(tittel="Lagt ut sist", tidspunkt=samme, opprettet=T0 - timedelta(hours=1))
    lag_oppdrag(tittel="Lagt ut først", tidspunkt=samme, opprettet=T0 - timedelta(days=2))
    lag_oppdrag(tittel="Tidligst", tidspunkt=T0 + timedelta(days=1))
    lag_oppdrag(tittel="Likt med lavest id", tidspunkt=samme, opprettet=T0 - timedelta(minutes=30))
    lag_oppdrag(tittel="Likt med høyest id", tidspunkt=samme, opprettet=T0 - timedelta(minutes=30))
    assert titler(ledige_oppdrag(db, postnummer="0571", kategori=None, bruker_id=ola.id)) == [
        "Tidligst", "Lagt ut først", "Lagt ut sist", "Likt med lavest id", "Likt med høyest id", "Senere",
    ]


# ---------- grensen for passert (FR-8, AD-3) ----------


def test_grensen_for_passert(db, ola, lag_oppdrag, sett_na) -> None:
    """AD-3: lik klokka er passert (ikke vist), 1 s før er ikke passert (vist)."""
    tidspunkt = T0 + timedelta(hours=2)
    lag_oppdrag(tittel="Grensen", tidspunkt=tidspunkt)
    sett_na(tidspunkt - timedelta(seconds=1))
    assert titler(ledige_oppdrag(db, postnummer="0571", kategori=None, bruker_id=ola.id)) == ["Grensen"]
    sett_na(tidspunkt)
    assert ledige_oppdrag(db, postnummer="0571", kategori=None, bruker_id=ola.id) == []


def test_utgatt_med_verdi_og_kolonne(db, lag_oppdrag, sett_na) -> None:
    """AD-3: samme funksjon gir `bool` for en verdi og et SQL-uttrykk for kolonnen."""
    assert utgatt(T0) is True
    assert utgatt(T0 + timedelta(seconds=1)) is False
    assert utgatt(T0 - timedelta(seconds=1)) is True
    assert utgatt(T0, na=T0 - timedelta(seconds=1)) is False
    passert = lag_oppdrag(tidspunkt=T0)
    framtid = lag_oppdrag(tidspunkt=T0 + timedelta(seconds=1))
    ider = set(db.scalars(select(Oppdrag.id).where(utgatt(Oppdrag.tidspunkt))))
    assert passert.id in ider and framtid.id not in ider


def test_endre_status_har_samme_grense(db, lag_oppdrag) -> None:
    """AD-3: `endre_status(ikke_passert=True)` avviser et oppdrag med tidspunkt lik klokka."""
    oppdrag = lag_oppdrag(tidspunkt=T0)
    with pytest.raises(Konflikt):
        endre_status(db, oppdrag.id, fra="apen", til="avbrutt", ikke_passert=True)
    oppdrag = lag_oppdrag(tidspunkt=T0 + timedelta(seconds=1))
    endre_status(db, oppdrag.id, fra="apen", til="avbrutt", ikke_passert=True)


# ---------- kortet (AD-16) ----------


def test_kortet_har_det_kortet_viser(db, ola, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(tittel="Kort", belop=None, kategori="dyrepass")
    (kort,) = ledige_oppdrag(db, postnummer="0571", kategori=None, bruker_id=ola.id)
    assert (kort.id, kort.tittel, kort.kategori, kort.sted, kort.belop, kort.tidspunkt) == (
        oppdrag.id, "Kort", "dyrepass", "0571 Oslo", None, T0 + timedelta(days=1),
    )


def test_oppdragkort_har_ingen_personfelt() -> None:
    """AD-16: kortet har verken person- eller eierfelt."""
    felt = {f.name for f in dataclasses.fields(OppdragKort)}
    assert felt.isdisjoint({"telefon", "epost", "fodselsdato", "navn", "oppdragsgiver_id", "skjema_id"})


# ---------- erfaring (FR-21, AR-13) ----------


def test_erfaring(db, lag_bruker, lag_oppdrag) -> None:
    """FR-21: utførte oppdrag der brukeren var valgt hjelper, per kategori, i rekkefølgen i KATEGORIER."""
    amir, nora, jonas = lag_bruker(), lag_bruker(), lag_bruker()
    lag_oppdrag(status="utfort", valgt_hjelper_id=amir.id, kategori="hage")
    lag_oppdrag(status="utfort", valgt_hjelper_id=amir.id, kategori="snomaking")
    lag_oppdrag(status="utfort", valgt_hjelper_id=amir.id, kategori="hage")
    lag_oppdrag(status="hjelper_valgt", valgt_hjelper_id=amir.id, kategori="annet")  # ikke utført
    lag_oppdrag(status="avbrutt", valgt_hjelper_id=amir.id, kategori="annet")  # avbrutt
    lag_oppdrag(status="utfort", valgt_hjelper_id=nora.id, kategori="dyrepass")
    lag_oppdrag(oppdragsgiver=jonas, status="utfort", valgt_hjelper_id=nora.id)  # Jonas som eier teller ikke
    resultat = erfaring(db, [amir.id, nora.id, jonas.id, amir.id])
    assert resultat == {
        amir.id: Erfaring(3, (("snomaking", 1), ("hage", 2)), None, 0),
        nora.id: Erfaring(2, (("snomaking", 1), ("dyrepass", 1)), None, 0),
        jonas.id: Erfaring(0, (), None, 0),
    }


def test_erfaring_uten_ider(db) -> None:
    assert erfaring(db, []) == {}
