"""Bilde av oppdraget (story 2.7).

Tabellen `oppdragsbilde` med høyst ett bilde per oppdrag: `oppdrag_id` er både
primærnøkkel og fremmednøkkel. `bilde` og `miniatyr` er JPEG-er laget av
`oppdrag/bilde.py`, uten metadata (FR-27, AD-18). Ingen `ON DELETE CASCADE`
(AD-2): bildet slettes eksplisitt før oppdraget.

Bare et tillegg, så en tilbakerulling av koden er trygg (AD-13).

Revision ID: 0004
Revises: 0003
Opprettet: 2026-11-27
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.core.db import UtcDateTime

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "oppdragsbilde",
        sa.Column("oppdrag_id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("bilde", sa.LargeBinary(), nullable=False),
        sa.Column("miniatyr", sa.LargeBinary(), nullable=False),
        sa.Column("bildetekst", sa.String(120), nullable=False),
        sa.Column("bredde", sa.Integer(), nullable=False),
        sa.Column("hoyde", sa.Integer(), nullable=False),
        sa.Column("opprettet", UtcDateTime(), nullable=False),
        sa.PrimaryKeyConstraint("oppdrag_id", name="pk_oppdragsbilde"),
        sa.ForeignKeyConstraint(
            ["oppdrag_id"], ["oppdrag.id"], name="fk_oppdragsbilde_oppdrag_id_oppdrag"
        ),
    )


def downgrade() -> None:
    op.drop_table("oppdragsbilde")
