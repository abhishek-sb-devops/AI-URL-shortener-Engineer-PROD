"""Initial URL shortener schema.

Revision ID: 20261025_01
Revises: 
Create Date: 2026-10-25 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20261025_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "urls",
        sa.Column("short_code", sa.String(length=255), primary_key=True),
        sa.Column("original_url", sa.String(length=2048), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "sequence",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("sequence")
    op.drop_table("urls")
