"""Tabellene `oppdrag` og `oppdragsbilde`, eid av oppdrag (AD-1, AD-2, AD-13, AD-18, AR-12, NFR-9).

- Kategori og status lagres som koder fra `core/domene.py`. CHECK-constraints
  avviser andre verdier i begge databasene (AD-10).
- `belop` er NULL for «Uten betaling», ellers 1–10 000 (FR-5).
- `versjon` økes av hver statusavhengige skriving (AD-2).
- `skjema_id` er unik og stopper dobbel innsending (AD-2, NFR-5).
- Ingen adresse (NFR-9), og ingen `ON DELETE CASCADE` (AD-2).
- `oppdragsbilde` (story 2.7, FR-27, AD-18): høyst ett bilde per oppdrag,
  med `oppdrag_id` som primærnøkkel og fremmednøkkel. `bilde` og `miniatyr` er
  JPEG-er laget av `oppdrag/bilde.py` og lastes bare når de leses eksplisitt
  (`deferred=True`), så lister og kort aldri henter binærdata. Barnet slettes
  eksplisitt før oppdraget (`slett_bilde`), uten `ON DELETE CASCADE`.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

# Importeres for å registrere `postnummer` og `bruker` i metadataen, så fremmednøklene finnes.
import app.identity.models  # noqa: F401
from app.core import postnummer as _postnummer  # noqa: F401
from app.core.db import Base, UtcDateTime
from app.core.domene import BELOP_MAKS, BELOP_MIN, KATEGORIER, STATUSER


def _i_lista(kolonne: str, par: tuple[tuple[str, str], ...]) -> str:
    koder = ", ".join(f"'{kode}'" for kode, _ in par)
    return f"{kolonne} IN ({koder})"


SJEKK_STATUS = _i_lista("status", STATUSER)
SJEKK_KATEGORI = _i_lista("kategori", KATEGORIER)
SJEKK_BELOP = f"belop IS NULL OR (belop >= {BELOP_MIN} AND belop <= {BELOP_MAKS})"


class Oppdrag(Base):
    __tablename__ = "oppdrag"
    __table_args__ = (
        CheckConstraint(SJEKK_STATUS, name="status"),
        CheckConstraint(SJEKK_KATEGORI, name="kategori"),
        CheckConstraint(SJEKK_BELOP, name="belop"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    oppdragsgiver_id: Mapped[int] = mapped_column(ForeignKey("bruker.id"), nullable=False, index=True)
    tittel: Mapped[str] = mapped_column(String(80), nullable=False)
    beskrivelse: Mapped[str] = mapped_column(String(1000), nullable=False)
    kategori: Mapped[str] = mapped_column(String(30), nullable=False)
    postnummer: Mapped[str] = mapped_column(String(4), ForeignKey("postnummer.nummer"), nullable=False)
    tidspunkt: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False, index=True)
    belop: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    valgt_hjelper_id: Mapped[int | None] = mapped_column(ForeignKey("bruker.id"))
    versjon: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    skjema_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    opprettet: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False)
    vesentlig_endret: Mapped[datetime | None] = mapped_column(UtcDateTime)


class Oppdragsbilde(Base):
    __tablename__ = "oppdragsbilde"

    oppdrag_id: Mapped[int] = mapped_column(
        ForeignKey("oppdrag.id"), primary_key=True, autoincrement=False
    )
    bilde: Mapped[bytes] = mapped_column(LargeBinary, nullable=False, deferred=True)
    miniatyr: Mapped[bytes] = mapped_column(LargeBinary, nullable=False, deferred=True)
    bildetekst: Mapped[str] = mapped_column(String(120), nullable=False)
    bredde: Mapped[int] = mapped_column(Integer, nullable=False)
    hoyde: Mapped[int] = mapped_column(Integer, nullable=False)
    opprettet: Mapped[datetime] = mapped_column(UtcDateTime, nullable=False)
