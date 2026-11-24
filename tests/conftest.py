"""Felles testoppsett (AR-29).

- `APP_ENV=test` settes før appen importeres.
- Databasen er en midlertidig SQLite-fil, eller `TEST_DATABASE_URL` (Postgres i CI).
- `alembic upgrade head` kjøres én gang per testkjøring.
- Hver test kjører i en ytre transaksjon som rulles tilbake. Appens
  sesjonsfabrikk byttes på `app.state`, så ruter og mellomvare bruker den samme
  tilkoblingen (`join_transaction_mode="create_savepoint"`).
- `sett_na` stiller klokka.
- Fabrikkene kommer i storyene som lager tabellene: `lag_bruker` og
  `logg_inn_som` i 1.2, `lag_oppdrag` i 2.1, `lag_interesse` i 3.1 og
  `lag_tilbakemelding` i 4.2. Fabrikkene committer bare sin egen SAVEPOINT, så
  alt rulles tilbake etter testen.
- bcrypt kjører med kostnad 4 fordi `APP_ENV=test` (AR-29).
"""

from __future__ import annotations

import atexit
import os
import shutil
import tempfile
import itertools
import secrets
from collections.abc import Callable, Iterator
from datetime import date, datetime
from pathlib import Path

os.environ["APP_ENV"] = "test"

_TEMP_MAPPE: str | None = None
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    _TEMP_MAPPE = tempfile.mkdtemp(prefix="nabolagshelten-test-")
    atexit.register(shutil.rmtree, _TEMP_MAPPE, ignore_errors=True)
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
from app.core.sesjon import SESJON_COOKIE  # noqa: E402
from app.identity.models import Bruker, Sesjon  # noqa: E402
from app.identity.service import (  # noqa: E402
    SESJON_VARIGHET,
    hash_passord,
    hash_sesjonsnokkel,
    normaliser_epost,
)

STANDARD_PASSORD = "test-passord-1"

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


_lopenummer = itertools.count(1)


@pytest.fixture
def lag_bruker(db: Session) -> Callable[..., Bruker]:
    """Lager en bruker. Feltene kan overstyres, og `passord` hashes med `hash_passord`.

    Standard: postnummer 0571, passord `STANDARD_PASSORD` og unik e-post.
    """

    def _lag(**felt) -> Bruker:
        nummer = next(_lopenummer)
        passord = felt.pop("passord", STANDARD_PASSORD)
        verdier = {
            "navn": f"Testbruker {nummer}",
            "epost": f"testbruker{nummer}@eksempel.no",
            "telefon": f"4{nummer:07d}",
            "postnummer": "0571",
            "fodselsdato": date(1980, 1, 1),
            "opprettet": klokke.na(),
            **felt,
        }
        verdier["epost"] = normaliser_epost(verdier["epost"]) if verdier["epost"] else None
        bruker = Bruker(passord_hash=hash_passord(passord) if passord else None, **verdier)
        db.add(bruker)
        db.commit()
        return bruker

    return _lag


@pytest.fixture
def logg_inn_som(db: Session) -> Callable[[TestClient, Bruker], str]:
    """Logger inn ved å lage sesjonsraden og sette cookien direkte. Gir nøkkelen."""

    def _logg_inn(klient: TestClient, bruker: Bruker) -> str:
        nokkel = secrets.token_urlsafe(32)
        na = klokke.na()
        db.add(
            Sesjon(
                nokkel=hash_sesjonsnokkel(nokkel),
                bruker_id=bruker.id,
                opprettet=na,
                utloper=na + SESJON_VARIGHET,
            )
        )
        db.commit()
        klient.cookies.set(SESJON_COOKIE, nokkel)
        return nokkel

    return _logg_inn
