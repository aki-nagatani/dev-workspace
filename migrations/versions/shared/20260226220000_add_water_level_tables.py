"""add water level tables (field, rental_boat_shop, water_level_history)

Revision ID: 20260226220000
Revises: 20260209150000
Create Date: 2026-02-26 22:00:00.000000

水位推移機能用テーブルを追加。
- rental_boat_shop: レンタルボート店マスタ
- field: フィールドマスタ（水位取得用拡張カラム含む）
- water_level_history: リザーバー単位の日次水位履歴

06_database M, M-2, M-3 参照。
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "20260226220000"
down_revision = "20260209150000"
branch_labels = None
depends_on = None


def _has_table(inspector, table_name: str) -> bool:
    """Check if table exists."""
    try:
        return table_name in inspector.get_table_names()
    except Exception:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # 1. rental_boat_shop（field.rental_boat_shop_id が参照するため先に作成）
    if not _has_table(inspector, "rental_boat_shop"):
        op.create_table(
            "rental_boat_shop",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(128), nullable=False),
            sa.Column("website_url", sa.String(512), nullable=True),
            sa.Column("memo", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

    # 2. field（フィールドマスタ＋水位推移用拡張カラム）
    if not _has_table(inspector, "field"):
        op.create_table(
            "field",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(128), nullable=False),
            sa.Column("location", sa.String(256), nullable=True),
            sa.Column("lat", sa.Numeric(10, 7), nullable=True),
            sa.Column("lng", sa.Numeric(10, 7), nullable=True),
            sa.Column("altitude_m", sa.Numeric(7, 2), nullable=True),
            sa.Column("position_accuracy_m", sa.Numeric(6, 2), nullable=True),
            sa.Column("memo", sa.Text(), nullable=True),
            sa.Column("base_water_quality", sa.Integer(), nullable=False, server_default="3"),
            sa.Column("water_level_source_type", sa.String(32), nullable=True),
            sa.Column("obs_ofc_cd", sa.Integer(), nullable=True),
            sa.Column("obs_obs_cd", sa.Integer(), nullable=True),
            sa.Column(
                "rental_boat_shop_id",
                sa.Integer(),
                sa.ForeignKey("rental_boat_shop.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )
        op.create_index("idx_field_name", "field", ["name"], unique=True)
        op.create_index("idx_field_water_level_source", "field", ["water_level_source_type"])

    # 3. water_level_history
    if not _has_table(inspector, "water_level_history"):
        op.create_table(
            "water_level_history",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "field_id",
                sa.Integer(),
                sa.ForeignKey("field.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("observed_date", sa.Date(), nullable=False),
            sa.Column("water_level_m", sa.Numeric(6, 2), nullable=False),
            sa.Column("source", sa.String(32), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )
        op.create_index(
            "idx_water_level_field_date",
            "water_level_history",
            ["field_id", "observed_date"],
        )
        op.create_unique_constraint(
            "uq_water_level_field_date",
            "water_level_history",
            ["field_id", "observed_date"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if _has_table(inspector, "water_level_history"):
        op.drop_index("idx_water_level_field_date", table_name="water_level_history")
        op.drop_constraint(
            "uq_water_level_field_date",
            "water_level_history",
            type_="unique",
        )
        op.drop_table("water_level_history")

    if _has_table(inspector, "field"):
        op.drop_index("idx_field_water_level_source", table_name="field")
        op.drop_index("idx_field_name", table_name="field")
        op.drop_table("field")

    if _has_table(inspector, "rental_boat_shop"):
        op.drop_table("rental_boat_shop")
