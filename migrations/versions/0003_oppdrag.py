"""Oppdrag (story 2.1).

Tabellen `oppdrag` med kategori og status som koder, CHECK-constraints for
status, kategori og beløp, og unik `skjema_id` mot dobbel innsending (AD-2,
AD-10, AR-12, NFR-5). Ingen adresse (NFR-9) og ingen `ON DELETE CASCADE` (AD-2).

Verdiene i CHECK-constraintene står her som tekst, så migreringen ikke endrer
seg om `core/domene.py` endres. En ny kategori krever en ny migrering.

Revision ID: 0003
Revises: 0002
Opprettet: 2026-11-26
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.core.db import UtcDateTime

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "oppdrag",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("oppdragsgiver_id", sa.Integer(), nullable=False),
        sa.Column("tittel", sa.String(80), nullable=False),
        sa.Column("beskrivelse", sa.String(1000), nullable=False),
        sa.Column("kategori", sa.String(30), nullable=False),
        sa.Column("postnummer", sa.String(4), nullable=False),
        sa.Column("tidspunkt", UtcDateTime(), nullable=False),
        sa.Column("belop", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("valgt_hjelper_id", sa.Integer(), nullable=True),
        sa.Column("versjon", sa.Integer(), nullable=False),
        sa.Column("skjema_id", sa.String(64), nullable=False),
        sa.Column("opprettet", UtcDateTime(), nullable=False),
        sa.Column("vesentlig_endret", UtcDateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_oppdrag"),
        sa.UniqueConstraint("skjema_id", name="uq_oppdrag_skjema_id"),
        sa.ForeignKeyConstraint(
            ["oppdragsgiver_id"], ["bruker.id"], name="fk_oppdrag_oppdragsgiver_id_bruker"
        ),
        sa.ForeignKeyConstraint(
            ["postnummer"], ["postnummer.nummer"], name="fk_oppdrag_postnummer_postnummer"
        ),
        sa.ForeignKeyConstraint(
            ["valgt_hjelper_id"], ["bruker.id"], name="fk_oppdrag_valgt_hjelper_id_bruker"
        ),
        sa.CheckConstraint(
            "status IN ('apen', 'hjelper_valgt', 'utfort', 'avbrutt')", name="ck_oppdrag_status"
        ),
        sa.CheckConstraint(
            "kategori IN ('snomaking', 'hage', 'baerehjelp-flytting', 'dyrepass', "
            "'teknologihjelp', 'annet')",
            name="ck_oppdrag_kategori",
        ),
        sa.CheckConstraint(
            "belop IS NULL OR (belop >= 1 AND belop <= 10000)", name="ck_oppdrag_belop"
        ),
    )
    op.create_index("ix_oppdrag_oppdragsgiver_id", "oppdrag", ["oppdragsgiver_id"])
    op.create_index("ix_oppdrag_tidspunkt", "oppdrag", ["tidspunkt"])


def downgrade() -> None:
    op.drop_index("ix_oppdrag_tidspunkt", table_name="oppdrag")
    op.drop_index("ix_oppdrag_oppdragsgiver_id", table_name="oppdrag")
    op.drop_table("oppdrag")
