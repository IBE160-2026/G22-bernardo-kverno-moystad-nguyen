"""Felles testoppsett (AR-29).

- `APP_ENV=test` settes før appen importeres.
- Databasen er en midlertidig SQLite-fil, eller `TEST_DATABASE_URL` (Postgres i CI).
- `alembic upgrade head` kjøres én gang per testkjøring.
- Hver test kjører i en ytre transaksjon som rulles tilbake. Appens
  sesjonsfabrikk byttes på `app.state`, så ruter og mellomvare bruker den samme
  tilkoblingen (`join_transaction_mode="create_savepoint"`).
- `sett_na` stiller klokka.
- Fabrikkene kommer i storyene som lager tabellene: `lag_bruker` og
  `logg_inn_som` i 1.2, `lag_oppdrag` i 2.1, `lag_bilde` i 2.7, `lag_interesse` i 3.1 og
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
from datetime import date, datetime, timedelta
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
from app.oppdrag.bilde import behandle  # noqa: E402
from app.oppdrag.models import Oppdrag, Oppdragsbilde  # noqa: E402
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


@pytest.fixture
def lag_oppdrag(db: Session, lag_bruker: Callable[..., Bruker]) -> Callable[..., Oppdrag]:
    """Lager et oppdrag med gyldige standardverdier. Feltene kan overstyres (AR-29).

    Standard: ny oppdragsgiver, i morgen på samme klokkeslett, 0571, 200 kr,
    status `apen` og unik `skjema_id`. `oppdragsgiver=<Bruker>` er en snarvei
    for `oppdragsgiver_id`. Committer bare sin egen SAVEPOINT, som `lag_bruker`.
    """

    def _lag(**felt) -> Oppdrag:
        oppdragsgiver = felt.pop("oppdragsgiver", None)
        if "oppdragsgiver_id" not in felt:
            felt["oppdragsgiver_id"] = (oppdragsgiver or lag_bruker()).id
        na = klokke.na()
        verdier = {
            "tittel": "Måke snø i innkjørselen",
            "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min i morgen.",
            "kategori": "snomaking",
            "postnummer": "0571",
            "tidspunkt": na + timedelta(days=1),
            "belop": 200,
            "status": "apen",
            "versjon": 1,
            "skjema_id": secrets.token_urlsafe(16),
            "opprettet": na,
            **felt,
        }
        oppdrag = Oppdrag(**verdier)
        db.add(oppdrag)
        db.commit()
        return oppdrag

    return _lag


@pytest.fixture
def lag_bilde(db: Session) -> Callable[..., Oppdragsbilde]:
    """Gir et oppdrag et bilde, behandlet av `oppdrag/bilde.py` (FR-27, story 2.7).

    Standard: en JPEG på 800 × 600 fra `tests/bilder.py` og bildeteksten
    «Snødekt innkjørsel med en spade». Committer bare sin egen SAVEPOINT.
    """
    from tests import bilder

    def _lag(oppdrag: Oppdrag, *, bildetekst: str = "Snødekt innkjørsel med en spade",
             data: bytes | None = None) -> Oppdragsbilde:
        bilde = behandle(data if data is not None else bilder.jpeg())
        rad = Oppdragsbilde(
            oppdrag_id=oppdrag.id,
            bilde=bilde.bilde,
            miniatyr=bilde.miniatyr,
            bildetekst=bildetekst,
            bredde=bilde.bredde,
            hoyde=bilde.hoyde,
            opprettet=klokke.na(),
        )
        db.add(rad)
        db.commit()
        return rad

    return _lag
