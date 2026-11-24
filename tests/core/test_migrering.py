"""Migreringen og databasen mot SQLite og Postgres (AD-9, AD-13, AR-4).

I CI kjører de samme testene mot en Postgres-container (`TEST_DATABASE_URL`).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, event, inspect, select, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

import app.identity.models  # noqa: F401  (registrerer tabellene i metadataen)
from app.core.db import Base, UtcDateTime, lag_motor
from app.core.postnummer import les_tsv, postnummer_tabell
from app.identity.models import Bruker

from ..conftest import alembic_config


def test_ett_alembic_hode() -> None:
    """AD-13: nøyaktig ett hode."""
    assert len(ScriptDirectory.from_config(alembic_config()).get_heads()) == 1


def test_postnummer_har_alle_gateadressene(db: Session) -> None:
    rader = db.execute(select(postnummer_tabell).order_by(postnummer_tabell.c.nummer)).all()
    assert [(r.nummer, r.poststed) for r in rader] == les_tsv()


def test_tabellene_bruker_og_sesjon_finnes(tilkobling: Connection) -> None:
    inspektor = inspect(tilkobling)
    tabeller = set(inspektor.get_table_names())
    assert {"postnummer", "bruker", "sesjon", "alembic_version"} <= tabeller
    kolonner = {k["name"]: k for k in inspektor.get_columns("bruker")}
    assert set(kolonner) == {
        "id", "navn", "epost", "passord_hash", "telefon", "postnummer",
        "fodselsdato", "opprettet", "slettet_tidspunkt",
    }  # NFR-9: ingen adresse
    for personfelt in ("navn", "epost", "passord_hash", "telefon", "postnummer", "fodselsdato"):
        assert kolonner[personfelt]["nullable"], personfelt  # AD-8: gravstein
    assert {k["name"] for k in inspektor.get_columns("sesjon")} == {
        "nokkel", "bruker_id", "opprettet", "utloper",
    }


def test_epost_er_unik(db: Session) -> None:
    na = datetime(2026, 11, 24, tzinfo=timezone.utc)
    db.add(Bruker(navn="A", epost="a@eksempel.no", opprettet=na))
    db.flush()
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(Bruker(navn="B", epost="a@eksempel.no", opprettet=na))
            db.flush()


def test_fremmednokkel_til_postnummer_handheves(db: Session) -> None:
    """AD-2: `foreign_keys=ON` i SQLite, så begge databasene avviser ukjent postnummer."""
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(Bruker(navn="C", postnummer="0000", opprettet=datetime.now(timezone.utc)))
            db.flush()


def test_utcdatetime_gir_tilbake_aware_utc(db: Session) -> None:
    """AD-9: lagres i UTC, kommer tilbake som aware UTC."""
    oslo_sommertid = timezone(timedelta(hours=2))
    lagret = datetime(2026, 7, 1, 14, 30, tzinfo=oslo_sommertid)
    bruker = Bruker(navn="D", fodselsdato=date(1954, 5, 3), opprettet=lagret)
    db.add(bruker)
    db.flush()
    db.expire_all()
    lest = db.get(Bruker, bruker.id)
    assert lest.opprettet == datetime(2026, 7, 1, 12, 30, tzinfo=timezone.utc)
    assert lest.opprettet.utcoffset() == timedelta(0)
    assert lest.fodselsdato == date(1954, 5, 3)


def test_utcdatetime_avviser_naiv_tid() -> None:
    with pytest.raises(ValueError):
        UtcDateTime().process_bind_param(datetime(2026, 1, 1), None)


def test_savepoint_ruller_tilbake_bare_det_indre(db: Session) -> None:
    """AD-17: `begin_nested()` virker i begge databasene."""
    na = datetime(2026, 11, 24, tzinfo=timezone.utc)
    db.add(Bruker(navn="Ytre", opprettet=na))
    db.flush()
    try:
        with db.begin_nested():
            db.add(Bruker(navn="Indre", opprettet=na))
            db.flush()
            raise RuntimeError
    except RuntimeError:
        pass
    navn = set(db.scalars(select(Bruker.navn)).all())
    assert "Ytre" in navn and "Indre" not in navn


def test_sqlite_har_fremmednokler_pa(tilkobling: Connection) -> None:
    if tilkobling.dialect.name != "sqlite":
        pytest.skip("Gjelder bare SQLite")
    assert tilkobling.execute(text("PRAGMA foreign_keys")).scalar() == 1


def test_modellene_og_migreringene_stemmer(tilkobling: Connection) -> None:
    """AD-13: modellene og migreringene beskriver samme skjema."""
    forskjeller = compare_metadata(MigrationContext.configure(tilkobling), Base.metadata)
    assert forskjeller == []


def test_sqlite_starter_skrivetransaksjoner_med_begin_immediate(
    tilkobling: Connection, tmp_path
) -> None:
    """AD-2: en transaksjon i SQLite tar skrivelåsen med en gang, også før den skriver."""
    if tilkobling.dialect.name != "sqlite":
        pytest.skip("Gjelder bare SQLite")
    motor = lag_motor(f"sqlite:///{(tmp_path / 'laas.db').as_posix()}?timeout=0.1")
    try:
        with motor.connect() as a, motor.connect() as b:
            transaksjon_a = a.begin()  # skriver ingenting
            with pytest.raises(OperationalError):
                b.begin()
            transaksjon_a.rollback()
    finally:
        motor.dispose()


class _Stopp(Exception):
    pass


def test_postgres_motor_bruker_nullpool_og_ingen_prepared_statements() -> None:
    """AD-13: Supabase sin transaction pooler krever NullPool og prepare_threshold=None."""
    motor = lag_motor("postgresql+psycopg://u@h/d")
    fanget: dict = {}

    @event.listens_for(motor, "do_connect")
    def _fang(dialect, conn_rec, cargs, cparams):
        fanget.update(cparams)
        raise _Stopp  # ingen ekte tilkobling

    try:
        assert isinstance(motor.pool, NullPool)
        with pytest.raises(Exception):
            motor.connect()
        assert "prepare_threshold" in fanget
        assert fanget["prepare_threshold"] is None
    finally:
        motor.dispose()
