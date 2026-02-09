"""otayori-navi: on_children から institution_type を削除

施設種別は生年月日から算出するため、入力・DB保持から削除する。

Revision ID: 20260209140000
Revises: 20260209130000
Create Date: 2026-02-09 14:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260209140000"
down_revision = "20260209130000"
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
    if _has_column("on_children", "institution_type"):
        op.drop_column("on_children", "institution_type")


def downgrade() -> None:
    if not _has_table("on_children"):
        return
    if not _has_column("on_children", "institution_type"):
        op.add_column(
            "on_children",
            sa.Column("institution_type", sa.String(32), nullable=False, server_default="elementary"),
        )
