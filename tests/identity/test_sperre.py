"""Innlogging i servicen: sperre, opprydding og sesjoner (FR-2, AD-4, AR-14, NFR-5)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.sesjon import Innloggingsutfall
from app.identity import service
from app.identity.models import Innloggingsforsok, Sesjon
from app.identity.service import hash_sesjonsnokkel, logg_inn, logg_ut

from ..conftest import STANDARD_PASSORD

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)


def antall_forsok(db: Session, epost: str | None = None) -> int:
    sporring = select(func.count()).select_from(Innloggingsforsok)
    if epost is not None:
        sporring = sporring.where(Innloggingsforsok.epost == epost)
    return db.scalar(sporring)


def antall_sesjoner(db: Session, bruker_id: int) -> int:
    return db.scalar(select(func.count()).select_from(Sesjon).where(Sesjon.bruker_id == bruker_id))


@pytest.fixture
def kari(lag_bruker, sett_na):
    sett_na(T0)
    return lag_bruker(navn="Kari Nordmann", epost="kari@eksempel.no")


def test_riktig_innlogging_lager_sesjon_med_hash_og_7_dager(db, kari) -> None:
    """FR-2: ny tilfeldig nøkkel, bare hashen lagres, gyldig i 7 dager."""
    resultat = logg_inn(db, " Kari@Eksempel.no ", STANDARD_PASSORD)
    assert resultat.utfall is Innloggingsutfall.VELLYKKET
    sesjon = db.scalars(select(Sesjon).where(Sesjon.bruker_id == kari.id)).one()
    assert sesjon.nokkel == hash_sesjonsnokkel(resultat.nokkel)
    assert sesjon.nokkel != resultat.nokkel
    assert sesjon.utloper == T0 + timedelta(days=7)


def test_ny_nokkel_ved_hver_innlogging(db, kari) -> None:
    forste = logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).nokkel
    andre = logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).nokkel
    assert forste != andre


def test_gammel_sesjon_slettes_ved_ny_innlogging(db, kari) -> None:
    forste = logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).nokkel
    logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD, gammel_nokkel=forste)
    assert antall_sesjoner(db, kari.id) == 1


def test_feil_passord_og_ukjent_epost_gir_samme_utfall_og_telles(db, kari) -> None:
    """FR-2: samme utfall. Ukjente e-poster telles også (AD-4)."""
    assert logg_inn(db, "kari@eksempel.no", "feil-passord").utfall is Innloggingsutfall.FEIL
    assert logg_inn(db, "Ukjent@Eksempel.no", "feil-passord").utfall is Innloggingsutfall.FEIL
    assert antall_forsok(db, "kari@eksempel.no") == 1
    assert antall_forsok(db, "ukjent@eksempel.no") == 1


def test_ukjent_epost_kjorer_passordsjekken(db, kari, monkeypatch) -> None:
    """Svartiden skal ikke avsløre om kontoen finnes: bcrypt kjøres i begge tilfeller."""
    kall = []
    ekte = service.sjekk_passord

    def spion(passord, passord_hash):
        kall.append(passord_hash)
        return ekte(passord, passord_hash)

    monkeypatch.setattr(service, "sjekk_passord", spion)
    logg_inn(db, "ukjent@eksempel.no", "feil-passord")
    logg_inn(db, "kari@eksempel.no", "feil-passord")
    assert kall == [None, kari.passord_hash]


def test_dummy_hashen_har_samme_kostnad_som_ekte_hasher() -> None:
    assert service._dummy_hash().startswith("$2b$04$")


@pytest.mark.parametrize(("epost", "passord"), [("", STANDARD_PASSORD), ("kari@eksempel.no", ""), ("  ", "")])
def test_tomme_felt_telles_ikke(db, kari, epost, passord) -> None:
    assert logg_inn(db, epost, passord).utfall is Innloggingsutfall.FEIL
    assert antall_forsok(db) == 0


def test_sperre_etter_5_mislykkede_ogsa_med_riktig_passord(db, kari, sett_na) -> None:
    """FR-2: 5 mislykkede innen 15 min gir sperre, også for riktig passord."""
    for minutt in range(5):
        sett_na(T0 + timedelta(minutes=minutt))
        assert logg_inn(db, "kari@eksempel.no", "feil").utfall is Innloggingsutfall.FEIL
    sett_na(T0 + timedelta(minutes=5))
    assert logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).utfall is Innloggingsutfall.SPERRET
    # Avvist forsøk lagres ikke og sjekker ikke passordet.
    assert antall_forsok(db, "kari@eksempel.no") == 5
    assert antall_sesjoner(db, kari.id) == 0


def test_sperren_gjelder_per_epost(db, kari, lag_bruker) -> None:
    ola = lag_bruker(epost="ola@eksempel.no")
    for _ in range(5):
        logg_inn(db, "kari@eksempel.no", "feil")
    assert logg_inn(db, "ola@eksempel.no", STANDARD_PASSORD).vellykket
    assert antall_sesjoner(db, ola.id) == 1


def test_etter_15_minutter_gar_innloggingen_igjennom_og_tellerne_ryddes(db, kari, sett_na) -> None:
    """FR-2: sperren varer 15 minutter. Vellykket innlogging sletter tellerne."""
    for _ in range(5):
        logg_inn(db, "kari@eksempel.no", "feil")
    sett_na(T0 + timedelta(minutes=15))
    assert logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).utfall is Innloggingsutfall.SPERRET
    sett_na(T0 + timedelta(minutes=15, seconds=1))
    assert logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).vellykket
    assert antall_forsok(db, "kari@eksempel.no") == 0


def test_vellykket_innlogging_rydder_tellerne_for_eposten(db, kari) -> None:
    for _ in range(4):
        logg_inn(db, "kari@eksempel.no", "feil")
    logg_inn(db, "ukjent@eksempel.no", "feil")
    assert logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).vellykket
    assert antall_forsok(db, "kari@eksempel.no") == 0
    assert antall_forsok(db, "ukjent@eksempel.no") == 1


def test_hvert_forsok_sletter_alle_gamle_rader(db, kari, sett_na) -> None:
    """AD-4: feilskrevne e-poster blir ikke liggende (personvern)."""
    logg_inn(db, "feilskrevet@eksempel.no", "feil")
    logg_inn(db, "annen@eksempel.no", "feil")
    sett_na(T0 + timedelta(minutes=16))
    logg_inn(db, "kari@eksempel.no", "feil")
    assert antall_forsok(db) == 1
    assert antall_forsok(db, "kari@eksempel.no") == 1


def test_vellykket_innlogging_sletter_utlopte_sesjoner(db, kari, lag_bruker, sett_na) -> None:
    ola = lag_bruker(epost="ola@eksempel.no")
    logg_inn(db, "ola@eksempel.no", STANDARD_PASSORD)
    sett_na(T0 + timedelta(days=7))
    logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD)
    assert antall_sesjoner(db, ola.id) == 0


def test_slettet_bruker_kan_ikke_logge_inn(db, lag_bruker) -> None:
    lag_bruker(epost="borte@eksempel.no", slettet_tidspunkt=T0)
    assert logg_inn(db, "borte@eksempel.no", STANDARD_PASSORD).utfall is Innloggingsutfall.FEIL


def test_logg_ut_sletter_sesjonen(db, kari) -> None:
    nokkel = logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).nokkel
    logg_ut(db, nokkel)
    assert antall_sesjoner(db, kari.id) == 0
    logg_ut(db, None)  # uten cookie skjer ingenting


@pytest.mark.parametrize("epost", ["a" * 310 + "@eksempel.no", "kari\x00@eksempel.no"], ids=["over-320", "nul"])
def test_ugyldig_epost_gir_feil_uten_databasekall(db, kari, epost, monkeypatch) -> None:
    """E-post over 320 tegn eller med NUL når aldri databasen (ville gitt DataError i Postgres)."""

    def ingen_database(*args, **kwargs):
        raise AssertionError("skal ikke bruke databasen")

    monkeypatch.setattr(db, "execute", ingen_database)
    monkeypatch.setattr(db, "scalar", ingen_database)
    monkeypatch.setattr(db, "scalars", ingen_database)
    monkeypatch.setattr(db, "add", ingen_database)
    assert logg_inn(db, epost, STANDARD_PASSORD).utfall is Innloggingsutfall.FEIL


def test_dummy_hashen_lages_ved_oppstart(monkeypatch) -> None:
    """Første forsøk med ukjent e-post skal ikke koste en ekstra bcrypt-kjøring."""
    service._dummy_hash.cache_clear()
    service.IdentityAutentisering()
    assert service._dummy_hash.cache_info().currsize == 1
