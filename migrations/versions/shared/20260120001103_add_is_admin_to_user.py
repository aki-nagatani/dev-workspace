"""add is_admin to User

Revision ID: 20260120001103
Revises: 20260114104327
Create Date: 2026-01-20 00:11:03.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260120001103"
down_revision = "20260114104327"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Userテーブルにis_adminカラムを追加

    管理者権限フラグとしてis_adminを追加する。
    """
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "postgresql":
        op.add_column(
            "User",
            sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )
    else:
        op.add_column(
            "User",
            sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        )


def downgrade() -> None:
    """Userテーブルからis_adminカラムを削除"""
    op.drop_column("User", "is_admin")
