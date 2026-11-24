"""Konfigurasjon og oppstartsvakt (AD-14, NFR-1, NFR-3)."""

from __future__ import annotations

import logging

import pytest

from app import lag_app
from app.core.config import STANDARD_NOKKEL, KonfigFeil, Settings, hent_settings, les_settings

EKTE_NOKKEL = "x" * 32


def lag(**verdier) -> Settings:
    return Settings(_env_file=None, **verdier)


def test_standardverdier_gir_lokal_kjoring_uten_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """NFR-1: appen starter uten `.env`, mot en SQLite-fil."""
    for navn in ("APP_ENV", "DATABASE_URL", "SECRET_KEY", "OPENROUTER_API_KEY", "OPENROUTER_MODEL"):
        monkeypatch.delenv(navn, raising=False)
    settings = lag()
    assert settings.app_env == "local"
    assert settings.database_url == "sqlite:///./nabolagshelten.db"
    assert settings.secret_key == STANDARD_NOKKEL
    assert settings.openrouter_api_key == ""


def test_tom_verdi_gir_standardverdien(monkeypatch: pytest.MonkeyPatch) -> None:
    """En kopi av `.env.example` med tomme verdier skal ikke stoppe oppstarten."""
    monkeypatch.setenv("APP_ENV", "")
    assert lag().app_env == "local"


@pytest.mark.parametrize(
    "verdier",
    [
        {"app_env": "foo"},
        {"app_env": "production"},  # standardnøkkelen
        {"app_env": "production", "secret_key": STANDARD_NOKKEL},
        {"app_env": "production", "secret_key": "x" * 31},
    ],
    ids=["ukjent-miljo", "produksjon-uten-nokkel", "produksjon-standardnokkel", "produksjon-kort-nokkel"],
)
def test_ugyldig_miljo_stopper(monkeypatch: pytest.MonkeyPatch, verdier: dict) -> None:
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValueError):
        lag(**verdier)


def test_produksjon_med_ekte_nokkel_godtas() -> None:
    settings = lag(app_env="production", secret_key=EKTE_NOKKEL)
    assert settings.produksjon


@pytest.mark.parametrize(
    ("miljo", "forventet_ord"),
    [("foo", "APP_ENV"), ("production", "SECRET_KEY")],
)
def test_oppstarten_logger_tydelig_melding(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture, miljo: str, forventet_ord: str
) -> None:
    monkeypatch.setenv("APP_ENV", miljo)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    caplog.set_level(logging.CRITICAL, logger="app.core.config")
    with pytest.raises(KonfigFeil):
        les_settings()
    assert "Oppstarten stopper" in caplog.text
    assert forventet_ord in caplog.text


def test_lag_app_stopper_ved_ugyldig_miljo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "foo")
    hent_settings.cache_clear()
    try:
        with pytest.raises(KonfigFeil):
            lag_app()
    finally:
        monkeypatch.undo()
        hent_settings.cache_clear()


def test_hemmelig_nokkel_vises_ikke_i_feilmeldingen(caplog: pytest.LogCaptureFixture, monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "kort-hemmelig")
    with pytest.raises(KonfigFeil) as feil:
        les_settings()
    assert "kort-hemmelig" not in str(feil.value)
    assert "kort-hemmelig" not in caplog.text


def test_postgres_url_bruker_psycopg() -> None:
    assert lag(database_url="postgresql://u@h:5432/d").database_url == "postgresql+psycopg://u@h:5432/d"
    assert lag(database_url="postgres://u@h/d").database_url == "postgresql+psycopg://u@h/d"


def test_lag_app_uten_autentisering_stopper() -> None:
    """AD-1: lag_app() nekter å starte uten koblingen til Autentisering."""
    with pytest.raises(KonfigFeil):
        lag_app(autentisering=None)
    with pytest.raises(KonfigFeil):
        lag_app(autentisering=object())


def test_ren_start_seed_og_oppstart_uten_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """NFR-1: seed på en tom SQLite-fil migrerer, og appen svarer på /logg-inn etterpå."""
    from fastapi.testclient import TestClient
    from sqlalchemy import func, select

    from app import seed
    from app.core.db import lag_motor
    from app.core.postnummer import les_tsv, postnummer_tabell

    url = f"sqlite:///{(tmp_path / 'ren.db').as_posix()}"
    settings = lag(app_env="local", database_url=url)
    monkeypatch.setattr(seed, "hent_settings", lambda: settings)
    monkeypatch.setattr("app.core.config.hent_settings", lambda: settings)

    assert seed.main() == 0

    motor = lag_motor(url)
    try:
        with motor.connect() as tilkobling:
            antall = tilkobling.scalar(select(func.count()).select_from(postnummer_tabell))
        assert antall == len(les_tsv())
    finally:
        motor.dispose()

    app = lag_app(settings=settings)
    try:
        with TestClient(app) as klient:
            assert klient.get("/logg-inn").status_code == 200
    finally:
        app.state.motor.dispose()


def test_seed_nekter_i_produksjon(monkeypatch: pytest.MonkeyPatch) -> None:
    """AD-14: ingen seed i produksjon."""
    from app import seed

    monkeypatch.setattr(seed, "hent_settings", lambda: lag(app_env="production", secret_key=EKTE_NOKKEL))
    kalt = []
    monkeypatch.setattr(seed.command, "upgrade", lambda *a, **k: kalt.append(a))
    assert seed.main() == 1
    assert kalt == []
