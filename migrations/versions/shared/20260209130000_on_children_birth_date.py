"""otayori-navi: on_children を生年月日(birth_date)に変更

entrance_year, graduation_year を廃止し、birth_date (DATE NULL) に統一する。

Revision ID: 20260209130000
Revises: 20260209120000
Create Date: 2026-02-09 13:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260209130000"
down_revision = "20260209120000"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        return False
    return column_name in [c["name"] for c in inspector.get_columns(table_name)]


def upgrade() -> None:
    if not _has_table("on_children"):
        return

    if not _has_column("on_children", "birth_date"):
        op.add_column(
            "on_children",
            sa.Column("birth_date", sa.Date(), nullable=True),
        )

    if _has_column("on_children", "entrance_year"):
        op.drop_column("on_children", "entrance_year")
    if _has_column("on_children", "graduation_year"):
        op.drop_column("on_children", "graduation_year")


def downgrade() -> None:
    if not _has_table("on_children"):
        return

    if not _has_column("on_children", "entrance_year"):
        op.add_column(
            "on_children",
            sa.Column("entrance_year", sa.Integer(), nullable=True),
        )
    if not _has_column("on_children", "graduation_year"):
        op.add_column(
            "on_children",
            sa.Column("graduation_year", sa.Integer(), nullable=True),
        )

    if _has_column("on_children", "birth_date"):
        op.drop_column("on_children", "birth_date")
