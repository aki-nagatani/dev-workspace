"""drop DexSeed staging table

Revision ID: 20250920_drop_dexseed
Revises: 20250912_game_title_and_game_ids
Create Date: 2025-09-20 15:30:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "20250920_drop_dexseed"
down_revision = "20250912_game_title_and_game_ids"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    insp = inspect(conn)

    if insp.has_table("DexSeed"):
        op.drop_table("DexSeed")


def downgrade():
    # 差し戻し時は DexSeed を空で再作成（データまでは復元しない）
    if not op.get_bind().dialect.has_table(op.get_bind(), "DexSeed"):
        op.create_table(
            "DexSeed",
            sa.Column("nationalNo", sa.Text, nullable=True),
            sa.Column("dexNo", sa.Text, nullable=True),
            sa.Column("dexType", sa.Text, nullable=True),
        )
