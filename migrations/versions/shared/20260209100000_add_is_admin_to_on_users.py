"""add is_admin to on_users (otayori-navi)

おたよりナビの管理者権限をDBで管理するため、on_users に is_admin を追加する。
既にカラムがある（新規環境で models が先に create_all した等）場合はスキップする。

Revision ID: 20260209100000
Revises: 20260205100000
Create Date: 2026-02-09 10:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260209100000"
down_revision = "20260205100000"
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
    if not _has_table("on_users"):
        return
    if _has_column("on_users", "is_admin"):
        return

    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "postgresql":
        op.add_column(
            "on_users",
            sa.Column(
                "is_admin",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )
    else:
        op.add_column(
            "on_users",
            sa.Column(
                "is_admin",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
            ),
        )


def downgrade() -> None:
    if not _has_table("on_users"):
        return
    if not _has_column("on_users", "is_admin"):
        return
    op.drop_column("on_users", "is_admin")
