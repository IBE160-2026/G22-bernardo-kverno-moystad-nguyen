"""Testbrukere i seed og `app.admin nytt-passord` (NFR-2, NFR-4, AR-9, NFR-5)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app import admin, seed
from app.core.config import Settings
from app.core.db import lag_motor, url_uten_passord
from app.core.postnummer import finnes
from app.identity.models import Bruker, Innloggingsforsok, Sesjon
from app.identity.service import logg_inn, sjekk_passord

from .conftest import ROT, STANDARD_PASSORD


def test_testbrukerne_oppfyller_nfr2() -> None:
    """NFR-2: minst 6 oppdiktede brukere i 2–3 postnumre som finnes."""
    assert len(seed.TESTBRUKERE) == 6
    postnumre = {t.postnummer for t in seed.TESTBRUKERE}
    assert 2 <= len(postnumre) <= 3
    assert all(finnes(p) for p in postnumre)
    assert len({t.epost for t in seed.TESTBRUKERE}) == 6
    assert all(t.epost.endswith("@eksempel.no") for t in seed.TESTBRUKERE)


def test_seed_to_ganger_gir_seks_brukere_med_hash(db) -> None:
    """NFR-2/NFR-4: seed kan kjøres to ganger, og `passord_hash` inneholder ikke passordet."""
    assert seed.legg_inn_testbrukere(db) == 6
    assert seed.legg_inn_testbrukere(db) == 0
    eposter = [t.epost for t in seed.TESTBRUKERE]
    brukere = db.scalars(select(Bruker).where(Bruker.epost.in_(eposter))).all()
    assert len(brukere) == 6
    for testbruker in seed.TESTBRUKERE:
        bruker = next(b for b in brukere if b.epost == testbruker.epost)
        assert testbruker.passord not in bruker.passord_hash
        assert sjekk_passord(testbruker.passord, bruker.passord_hash)


def test_testbrukerne_star_i_readme() -> None:
    """NFR-2: README har tabellen, merket «bare for lokal testing»."""
    readme = (ROT / "README.md").read_text(encoding="utf-8")
    assert "bare for lokal testing" in readme
    for testbruker in seed.TESTBRUKERE:
        assert testbruker.navn in readme
        assert testbruker.epost in readme
        assert testbruker.passord in readme
    assert "uv run python -m app.admin nytt-passord" in readme


def test_seed_main_to_ganger_pa_ren_database(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    url = f"sqlite:///{(tmp_path / 'seed.db').as_posix()}"
    settings = Settings(_env_file=None, app_env="local", database_url=url)
    monkeypatch.setattr(seed, "hent_settings", lambda: settings)
    monkeypatch.setattr("app.core.config.hent_settings", lambda: settings)
    assert seed.main() == 0
    assert seed.main() == 0
    motor = lag_motor(url)
    try:
        with motor.connect() as tilkobling:
            assert tilkobling.scalar(select(func.count()).select_from(Bruker)) == 6
    finally:
        motor.dispose()


def test_url_uten_passord() -> None:
    assert url_uten_passord("postgresql+psycopg://u:hemmelig@h:5432/d") == "postgresql+psycopg://u:***@h:5432/d"


# ---------- admin ----------


def svar(*verdier):
    rest = list(verdier)
    return lambda _ledetekst: rest.pop(0)


def test_admin_nytt_passord(db, sesjonsfabrikk, lag_bruker, capsys) -> None:
    """AR-9: Kari kan logge inn med det nye passordet; gamle sesjoner og tellere er slettet."""
    kari = lag_bruker(epost="kari@eksempel.no")
    nokkel = logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).nokkel
    logg_inn(db, "kari@eksempel.no", "feil")
    db.commit()
    assert nokkel

    kode = admin.main(
        ["nytt-passord", " Kari@Eksempel.no "],
        sesjonsfabrikk=sesjonsfabrikk,
        les_passord=svar("nytt-passord-9", "nytt-passord-9"),
        spor=svar("ja"),
    )
    assert kode == 0
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Sesjon).where(Sesjon.bruker_id == kari.id)) == 0
    assert db.scalar(select(func.count()).select_from(Innloggingsforsok)) == 0
    assert logg_inn(db, "kari@eksempel.no", "nytt-passord-9").vellykket
    assert not logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).vellykket
    utskrift = capsys.readouterr()
    assert "Database: sqlite" in utskrift.out or "Database: postgresql" in utskrift.out
    assert "nytt-passord-9" not in utskrift.out + utskrift.err
    assert "kari@eksempel.no" not in utskrift.out + utskrift.err


@pytest.mark.parametrize(
    ("passord", "bekreftelse", "melding"),
    [
        (("kort", "kort"), "ja", "8–64 tegn"),
        (("        ", "        "), "ja", "bare være mellomrom"),
        (("nytt-passord-9", "annet-passord-9"), "ja", "ikke like"),
        (("nytt-passord-9", "nytt-passord-9"), "nei", "Avbrutt"),
    ],
    ids=["for-kort", "bare-mellomrom", "ulike", "ikke-ja"],
)
def test_admin_endrer_ingenting_ved_feil(
    db, sesjonsfabrikk, lag_bruker, capsys, passord, bekreftelse, melding
) -> None:
    kari = lag_bruker(epost="kari@eksempel.no")
    gammel_hash = kari.passord_hash
    kode = admin.main(
        ["nytt-passord", "kari@eksempel.no"],
        sesjonsfabrikk=sesjonsfabrikk,
        les_passord=svar(*passord),
        spor=svar(bekreftelse),
    )
    assert kode == 1
    utskrift = capsys.readouterr()
    assert melding in utskrift.out + utskrift.err
    assert "Ingenting er endret." in utskrift.out + utskrift.err
    db.expire_all()
    assert db.get(Bruker, kari.id).passord_hash == gammel_hash


def test_admin_ukjent_eller_slettet_bruker(db, sesjonsfabrikk, lag_bruker, capsys) -> None:
    lag_bruker(epost="borte@eksempel.no", slettet_tidspunkt=datetime(2026, 11, 1, tzinfo=timezone.utc))
    for epost in ("ukjent@eksempel.no", "borte@eksempel.no"):
        kode = admin.main(
            ["nytt-passord", epost],
            sesjonsfabrikk=sesjonsfabrikk,
            les_passord=svar("nytt-passord-9", "nytt-passord-9"),
            spor=svar("ja"),
        )
        assert kode == 1
    assert "Fant ingen aktiv bruker" in capsys.readouterr().err
