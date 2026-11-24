"""Postnumre, bruker og sesjon (story 1.1).

- `postnummer` lastes fra `data/postnumre.tsv` med `les_tsv()`: bare postnumre
  for gateadresser (Brings kategori G og B) (AD-1, AD-10).
- `bruker` og `sesjon`, som mellomvaren trenger for å slå opp innlogging (AD-4).
  Personfeltene i `bruker` kan være NULL (AD-8, NFR-9).

Revision ID: 0001
Revises:
Opprettet: 2026-11-24
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.core.db import UtcDateTime
from app.core.postnummer import les_tsv

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    postnummer = op.create_table(
        "postnummer",
        sa.Column("nummer", sa.String(4), nullable=False),
        sa.Column("poststed", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("nummer", name="pk_postnummer"),
    )
    op.bulk_insert(postnummer, [{"nummer": n, "poststed": s} for n, s in les_tsv()])

    op.create_table(
        "bruker",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("navn", sa.String(80), nullable=True),
        sa.Column("epost", sa.String(320), nullable=True),
        sa.Column("passord_hash", sa.String(100), nullable=True),
        sa.Column("telefon", sa.String(8), nullable=True),
        sa.Column("postnummer", sa.String(4), nullable=True),
        sa.Column("fodselsdato", sa.Date(), nullable=True),
        sa.Column("opprettet", UtcDateTime(), nullable=False),
        sa.Column("slettet_tidspunkt", UtcDateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_bruker"),
        sa.UniqueConstraint("epost", name="uq_bruker_epost"),
        sa.ForeignKeyConstraint(
            ["postnummer"], ["postnummer.nummer"], name="fk_bruker_postnummer_postnummer"
        ),
    )

    op.create_table(
        "sesjon",
        sa.Column("nokkel", sa.String(64), nullable=False),
        sa.Column("bruker_id", sa.Integer(), nullable=False),
        sa.Column("opprettet", UtcDateTime(), nullable=False),
        sa.Column("utloper", UtcDateTime(), nullable=False),
        sa.PrimaryKeyConstraint("nokkel", name="pk_sesjon"),
        sa.ForeignKeyConstraint(["bruker_id"], ["bruker.id"], name="fk_sesjon_bruker_id_bruker"),
    )
    op.create_index("ix_sesjon_bruker_id", "sesjon", ["bruker_id"])


def downgrade() -> None:
    op.drop_index("ix_sesjon_bruker_id", table_name="sesjon")
    op.drop_table("sesjon")
    op.drop_table("bruker")
    op.drop_table("postnummer")
