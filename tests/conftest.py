"""Felles testoppsett (AR-29).

- `APP_ENV=test` settes før appen importeres.
- Databasen er en midlertidig SQLite-fil, eller `TEST_DATABASE_URL` (Postgres i CI).
- `alembic upgrade head` kjøres én gang per testkjøring.
- Hver test kjører i en ytre transaksjon som rulles tilbake. Appens
  sesjonsfabrikk byttes på `app.state`, så ruter og mellomvare bruker den samme
  tilkoblingen (`join_transaction_mode="create_savepoint"`).
- `sett_na` stiller klokka. Fabrikkene (`lag_bruker` osv.) kommer i storyene som
  lager tabellene: 1.2, 2.1, 3.1 og 4.2.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

os.environ["APP_ENV"] = "test"

_TEMP_MAPPE: str | None = None
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    _TEMP_MAPPE = tempfile.mkdtemp(prefix="nabolagshelten-test-")
    TEST_DATABASE_URL = f"sqlite:///{Path(_TEMP_MAPPE, 'test.db').as_posix()}"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import Connection, Engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app import lag_app  # noqa: E402
from app.core import klokke  # noqa: E402
from app.core.config import hent_settings  # noqa: E402
from app.core.db import lag_motor  # noqa: E402

ROT = Path(__file__).resolve().parents[1]


def alembic_config(tilkobling: Connection | None = None) -> Config:
    config = Config(str(ROT / "alembic.ini"))
    if tilkobling is not None:
        config.attributes["connection"] = tilkobling
    return config


@pytest.fixture(scope="session")
def motor() -> Iterator[Engine]:
    """Motoren mot test-databasen, migrert til `head` én gang."""
    url = hent_settings().database_url
    motor = lag_motor(url)
    with motor.begin() as tilkobling:
        command.upgrade(alembic_config(tilkobling), "head")
    yield motor
    motor.dispose()
    if _TEMP_MAPPE is not None:
        shutil.rmtree(_TEMP_MAPPE, ignore_errors=True)


@pytest.fixture
def tilkobling(motor: Engine) -> Iterator[Connection]:
    """En tilkobling med en ytre transaksjon som rulles tilbake etter testen."""
    tilkobling = motor.connect()
    transaksjon = tilkobling.begin()
    try:
        yield tilkobling
    finally:
        transaksjon.rollback()
        tilkobling.close()


@pytest.fixture
def sesjonsfabrikk(tilkobling: Connection) -> sessionmaker[Session]:
    return sessionmaker(
        bind=tilkobling,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )


@pytest.fixture
def db(sesjonsfabrikk: sessionmaker[Session]) -> Iterator[Session]:
    """En sesjon for testen selv, i samme transaksjon som appen."""
    with sesjonsfabrikk() as sesjon:
        yield sesjon


@pytest.fixture
def app(sesjonsfabrikk: sessionmaker[Session]) -> FastAPI:
    app = lag_app()
    app.state.sesjonsfabrikk = sesjonsfabrikk
    return app


@pytest.fixture
def klient(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as klient:
        yield klient


@pytest.fixture
def sett_na() -> Iterator:
    """Stiller klokka: `sett_na(datetime(..., tzinfo=timezone.utc))`."""

    def _sett(tidspunkt: datetime) -> None:
        klokke.sett_na(tidspunkt)

    yield _sett
    klokke.sett_na(None)
