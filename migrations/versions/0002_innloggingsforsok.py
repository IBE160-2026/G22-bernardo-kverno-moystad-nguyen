"""Innloggingsforsøk (story 1.2).

Ett mislykket forsøk per rad, knyttet til normalisert e-post (AD-4, AR-14).
Både `epost` og `tidspunkt` er indeksert: sperren teller per e-post, og
oppryddingen sletter alle rader eldre enn 15 minutter.

Revision ID: 0002
Revises: 0001
Opprettet: 2026-11-24
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.core.db import UtcDateTime

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "innloggingsforsok",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("epost", sa.String(320), nullable=False),
        sa.Column("tidspunkt", UtcDateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_innloggingsforsok"),
    )
    op.create_index("ix_innloggingsforsok_epost", "innloggingsforsok", ["epost"])
    op.create_index("ix_innloggingsforsok_tidspunkt", "innloggingsforsok", ["tidspunkt"])


def downgrade() -> None:
    op.drop_index("ix_innloggingsforsok_tidspunkt", table_name="innloggingsforsok")
    op.drop_index("ix_innloggingsforsok_epost", table_name="innloggingsforsok")
    op.drop_table("innloggingsforsok")
