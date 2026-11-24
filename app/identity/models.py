"""Tabellene `bruker` og `sesjon`, eid av identity (AD-1, AD-4, AD-8, NFR-9).

`bruker` har bare navn, e-post, passord-hash, telefon, postnummer, fødselsdato
og tidspunkter, aldri adresse (NFR-9). Personfeltene kan være NULL, fordi en
slettet bruker blir en gravstein med samme id (AD-8).
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

# Importeres for å registrere `postnummer` i metadataen, slik at fremmednøkkelen finnes.
from app.core import postnummer as _postnummer  # noqa: F401
from app.core.db import Base, UtcDateTime


class Bruker(Base):
    __tablename__ = "bruker"

    id: Mapped[int] = mapped_column(primary_key=True)
    navn: Mapped[str | None] = mapped_column(String(80))
    epost: Mapped[str | None] = mapped_column(String(320), unique=True)
    passord_hash: Mapped[str | None] = mapped_column(String(100))
    telefon: Mapped[str | None] = mapped_column(String(8))
    postnummer: Mapped[str | None] = mapped_column(String(4), ForeignKey("postnummer.nummer"))
    fodselsdato: Mapped[date | None] = mapped_column(Date)
    opprettet: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False)
    slettet_tidspunkt: Mapped[datetime | None] = mapped_column(UtcDateTime)


class Sesjon(Base):
    __tablename__ = "sesjon"

    nokkel: Mapped[str] = mapped_column(String(64), primary_key=True)
    bruker_id: Mapped[int] = mapped_column(ForeignKey("bruker.id"), nullable=False, index=True)
    opprettet: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False)
    utloper: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False)
