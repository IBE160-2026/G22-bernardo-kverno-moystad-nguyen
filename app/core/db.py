"""Database: modellbase, tidstype, motor og én sesjon per forespørsel (AD-2, AD-9, AD-13, AD-17).

Samme kode kjører mot SQLite (lokalt og i test) og Postgres (CI og Supabase).
Skjemaet endres bare med Alembic, aldri med `create_all` (AD-13).
`laas_gir_konflikt` gjør «database is locked» fra SQLite om til `Konflikt` (AD-2).
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy import DateTime, Engine, MetaData, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.types import TypeDecorator

from app.core.feil import Konflikt

logger = logging.getLogger(__name__)

NAVNEKONVENSJON = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAVNEKONVENSJON)


class UtcDateTime(TypeDecorator[datetime]):
    """Lagrer tidspunkt i UTC og gir alltid tilbake aware UTC (AD-9).

    Naive tidspunkt avvises, så ingen kan lagre lokal tid ved en feil.
    SQLite har ingen tidssone-type, så verdien lagres der som naiv UTC.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("UtcDateTime krever et tidspunkt med tidssone (aware datetime).")
        utc = value.astimezone(timezone.utc)
        if dialect.name == "sqlite":
            return utc.replace(tzinfo=None)
        return utc

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


def lag_motor(url: str) -> Engine:
    """Lager motoren for SQLite eller Postgres.

    - SQLite: `PRAGMA foreign_keys=ON`, og skrivetransaksjoner starter med
      `BEGIN IMMEDIATE` (pysqlite-oppskriften i SQLAlchemy-dokumentasjonen), slik
      at to samtidige skrivinger ikke begge leser gammel tilstand (AD-2).
      Oppskriften gir også SAVEPOINT som virker (AD-17).
    - Postgres: `NullPool` og `prepare_threshold=None`, som Supabase sin
      transaction pooler krever (AD-13).
    """
    if url.startswith("sqlite"):
        motor = create_engine(url, connect_args={"check_same_thread": False})

        @event.listens_for(motor, "connect")
        def _ved_tilkobling(dbapi_tilkobling, _record) -> None:
            # Slå av pysqlite sin egen BEGIN, så SQLAlchemy styrer transaksjonene.
            dbapi_tilkobling.isolation_level = None
            markor = dbapi_tilkobling.cursor()
            markor.execute("PRAGMA foreign_keys=ON")
            markor.close()

        @event.listens_for(motor, "begin")
        def _ved_begin(tilkobling) -> None:
            tilkobling.exec_driver_sql("BEGIN IMMEDIATE")

        return motor

    return create_engine(url, poolclass=NullPool, connect_args={"prepare_threshold": None})


@contextmanager
def laas_gir_konflikt(melding: str, til_url: str) -> Iterator[None]:
    """Gjør «database is locked» fra SQLite om til `Konflikt(melding, til_url)` (AD-2).

    Med `BEGIN IMMEDIATE` venter en skriving på låsen til en annen er ferdig. Går
    ventetiden ut, er raden i praksis endret av noen andre, og brukeren skal få
    «Oppdraget er endret. Last siden på nytt.», ikke en 500. Alle andre feil,
    også andre `OperationalError`, slipper gjennom uendret.
    """
    try:
        yield
    except OperationalError as feil:
        if "database is locked" not in str(feil.orig if feil.orig is not None else feil):
            raise
        # Bare stien, aldri SQL-en eller verdiene, som kan inneholde personopplysninger (AR-30).
        logger.warning("Databasen var låst; Konflikt til %s", til_url)
        raise Konflikt(melding, til_url) from feil


def url_uten_passord(url: str) -> str:
    """Database-URL-en uten passord, til meldinger fra seed og admin."""
    return make_url(url).render_as_string(hide_password=True)


def lag_sesjonsfabrikk(motor: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


def hent_db(request: Request) -> Iterator[Session]:
    """Én `Session` per forespørsel, fra `app.state.sesjonsfabrikk` (AD-17).

    POST-ruter kjører service-kallene i `with db.begin():`. Services kaller aldri
    `commit()` eller `rollback()`. Sesjonen lukkes (og ruller tilbake det som
    ikke er committet) når forespørselen er ferdig.

    Sesjonen legges også i `request.state.db`, så `render` kan gi menykroken den
    samme sesjonen (AD-3). I SQLite starter hver transaksjon med `BEGIN
    IMMEDIATE`, også lesing, så en egen sesjon i `render` ville ventet på låsen
    som rutas sesjon holder, og fått «database is locked».
    """
    db: Session = request.app.state.sesjonsfabrikk()
    request.state.db = db
    try:
        yield db
    finally:
        db.close()
