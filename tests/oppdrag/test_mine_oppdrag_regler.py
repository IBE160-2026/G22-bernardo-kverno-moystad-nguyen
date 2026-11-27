"""«Mine oppdrag» direkte mot servicen: sortering, merket og menykroken (story 2.4).

FR-8, FR-18, NFR-11, AD-3, AD-16. Radene «Sortering», «Grensen (AD-3)», «Andre
statuser» og «Andres utgåtte» i I/O-matrisen i spec 2.4. Klokka står fast på
tirsdag 24.11.2026 kl. 13:00 norsk tid.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import seed
from app.oppdrag.models import Oppdrag
from app.oppdrag.service import (
    TIDSPUNKTET_ER_PASSERT,
    OppdragRad,
    antall_trenger_handling,
    lagt_ut_av,
    merker_lagt_ut,
)

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
TIDSPUNKT = datetime(2026, 11, 20, 9, 0, tzinfo=timezone.utc)
SEKUND = timedelta(seconds=1)


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


@pytest.fixture
def kari(lag_bruker):
    return lag_bruker(navn="Kari Nordmann")


# ---------- radene (FR-18, AD-16) ----------


def test_raden_har_bare_feltene_malen_trenger() -> None:
    """AD-16: `OppdragRad` har ingen personfelt."""
    assert [f.name for f in dataclasses.fields(OppdragRad)] == ["id", "tittel", "status", "tidspunkt", "merker"]


def test_sortert_etter_tidspunkt_uten_andres(db: Session, kari, lag_oppdrag) -> None:
    """FR-18: tidligste tidspunkt først, uansett når oppdraget ble lagt ut, og bare egne."""
    senere = lag_oppdrag(oppdragsgiver=kari, tittel="Senere", tidspunkt=T0 + timedelta(days=3),
                         opprettet=T0 - timedelta(days=5))
    passert = lag_oppdrag(oppdragsgiver=kari, tittel="Passert", tidspunkt=T0 - timedelta(days=2),
                          opprettet=T0 - timedelta(days=1))
    snart = lag_oppdrag(oppdragsgiver=kari, tittel="Snart", tidspunkt=T0 + timedelta(hours=2))
    lag_oppdrag(tittel="Andres", tidspunkt=T0 + timedelta(hours=1))
    assert [r.id for r in lagt_ut_av(db, kari.id)] == [passert.id, snart.id, senere.id]


def test_samme_tidspunkt_sorteres_etter_lagt_ut_og_id(db: Session, kari, lag_oppdrag) -> None:
    """Som FR-10: likt tidspunkt gir eldste utlagte først, og så lavest id."""
    tid = T0 + timedelta(days=1)
    nyest = lag_oppdrag(oppdragsgiver=kari, tittel="Nyest", tidspunkt=tid, opprettet=T0 - timedelta(hours=1))
    eldst = lag_oppdrag(oppdragsgiver=kari, tittel="Eldst", tidspunkt=tid, opprettet=T0 - timedelta(days=2))
    likt_a = lag_oppdrag(oppdragsgiver=kari, tittel="Likt A", tidspunkt=tid, opprettet=T0 - timedelta(days=1))
    likt_b = lag_oppdrag(oppdragsgiver=kari, tittel="Likt B", tidspunkt=tid, opprettet=T0 - timedelta(days=1))
    assert [r.id for r in lagt_ut_av(db, kari.id)] == [eldst.id, likt_a.id, likt_b.id, nyest.id]


def test_raden_har_status_og_tidspunkt(db: Session, kari, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(oppdragsgiver=kari, status="utfort", tidspunkt=TIDSPUNKT)
    rad = lagt_ut_av(db, kari.id)[0]
    assert (rad.id, rad.tittel, rad.status, rad.tidspunkt, rad.merker) == (
        oppdrag.id, oppdrag.tittel, "utfort", TIDSPUNKT, ()
    )


# ---------- merket og grensen (FR-8, AD-3) ----------


def test_merker_lagt_ut_bruker_utgatt_som_grense() -> None:
    """AD-3: `utgatt` (`tidspunkt <= na`) er eneste definisjon av passert."""
    assert merker_lagt_ut("apen", TIDSPUNKT, na=TIDSPUNKT - SEKUND) == ()
    assert merker_lagt_ut("apen", TIDSPUNKT, na=TIDSPUNKT) == (TIDSPUNKTET_ER_PASSERT,)
    assert merker_lagt_ut("apen", TIDSPUNKT, na=TIDSPUNKT + timedelta(days=30)) == (TIDSPUNKTET_ER_PASSERT,)
    assert TIDSPUNKTET_ER_PASSERT == "Tidspunktet er passert"


@pytest.mark.parametrize(
    ("na", "merker", "antall"),
    [(TIDSPUNKT - SEKUND, (), 0), (TIDSPUNKT, (TIDSPUNKTET_ER_PASSERT,), 1)],
    ids=["ett-sekund-for", "likt-tidspunktet"],
)
def test_grensen_med_sett_na_pa_begge_sider(
    db: Session, kari, lag_oppdrag, sett_na, na: datetime, merker: tuple, antall: int
) -> None:
    """AD-3, FR-8: merket og tallet regnes ved lesing fra `klokke.na()`, og ingenting lagres."""
    sett_na(TIDSPUNKT - timedelta(days=1))
    oppdrag = lag_oppdrag(oppdragsgiver=kari, tidspunkt=TIDSPUNKT)
    sett_na(na)
    assert lagt_ut_av(db, kari.id)[0].merker == merker
    assert antall_trenger_handling(db, kari.id) == antall
    assert not db.new and not db.dirty and not db.deleted
    db.expire_all()
    lagret = db.get(Oppdrag, oppdrag.id)
    assert (lagret.status, lagret.versjon) == ("apen", 1)


@pytest.mark.parametrize("status", ["hjelper_valgt", "utfort", "avbrutt"])
def test_andre_statuser_med_passert_tidspunkt_har_ikke_merket(
    db: Session, kari, lag_bruker, lag_oppdrag, status: str
) -> None:
    """FR-8: «Tidspunktet er passert» gjelder bare status Åpen."""
    lag_oppdrag(oppdragsgiver=kari, status=status, tidspunkt=TIDSPUNKT, valgt_hjelper_id=lag_bruker().id)
    assert lagt_ut_av(db, kari.id)[0].merker == ()
    assert antall_trenger_handling(db, kari.id) == 0


def test_andres_utgatte_teller_ikke(db: Session, kari, lag_bruker, lag_oppdrag) -> None:
    """NFR-11: tallet gjelder bare brukerens egne oppdrag."""
    nora = lag_bruker(navn="Nora Berg")
    lag_oppdrag(oppdragsgiver=nora, tidspunkt=TIDSPUNKT)
    lag_oppdrag(oppdragsgiver=kari, tidspunkt=T0 + timedelta(days=1))
    assert antall_trenger_handling(db, kari.id) == 0
    assert antall_trenger_handling(db, nora.id) == 1


def test_uten_oppdrag_er_lista_tom_og_tallet_0(db: Session, kari) -> None:
    assert lagt_ut_av(db, kari.id) == []
    assert antall_trenger_handling(db, kari.id) == 0


def test_antallet_er_lik_antall_rader_med_merker(db: Session, kari, lag_oppdrag) -> None:
    """AD-3: lista og tallet bruker samme merkefunksjon, så de kan aldri vise forskjellig."""
    for dager in (-3, -2, -1, 1, 2):
        lag_oppdrag(oppdragsgiver=kari, tidspunkt=T0 + timedelta(days=dager))
    lag_oppdrag(oppdragsgiver=kari, status="avbrutt", tidspunkt=T0 - timedelta(days=4))
    rader = lagt_ut_av(db, kari.id)
    assert antall_trenger_handling(db, kari.id) == sum(1 for r in rader if r.merker) == 3


def test_seed_gir_kari_seks_rader_og_ett_merke(db: Session) -> None:
    """NFR-2: eksempeldataene gir Kari seks oppdrag, der bare «Bære ved …» er utgått."""
    seed.last_eksempeldata(db)
    db.commit()
    kari_id = db.scalar(select(Oppdrag.oppdragsgiver_id).where(Oppdrag.tittel == "Bære ved opp til tredje etasje"))
    rader = lagt_ut_av(db, kari_id)
    assert [(r.tittel, r.status, r.merker) for r in rader] == [
        ("Bytte lyspære i taket", "utfort", ()),
        ("Bære ved opp til tredje etasje", "apen", (TIDSPUNKTET_ER_PASSERT,)),
        ("Måke snø i innkjørselen", "apen", ()),
        ("Raking av løv i hagen", "apen", ()),
        ("Hjelp med nytt nettbrett", "apen", ()),
        ("Lufte hunden mens jeg er bortreist", "avbrutt", ()),
    ]
    assert antall_trenger_handling(db, kari_id) == 1
