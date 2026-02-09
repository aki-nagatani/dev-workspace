"""otayori-navi: add on_children, migrate from configured_children, drop configured_children

on_children テーブルを新設し、on_families.configured_children のデータを移行したうえで
configured_children カラムを削除する。

Revision ID: 20260209120000
Revises: 20260209110000
Create Date: 2026-02-09 12:00:00

"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "20260209120000"
down_revision = "20260209110000"
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
    if not _has_table("on_families"):
        return

    # 1. on_children テーブルを作成
    if not _has_table("on_children"):
        op.create_table(
            "on_children",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("family_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("institution_type", sa.String(32), nullable=False),
            sa.Column("entrance_year", sa.Integer(), nullable=True),
            sa.Column("graduation_year", sa.Integer(), nullable=True),
            sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["family_id"], ["on_families.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_on_children_family_id", "on_children", ["family_id"], unique=False)

    # 2. configured_children から on_children へデータ移行
    if _has_column("on_families", "configured_children"):
        conn = op.get_bind()
        result = conn.execute(
            sa.text("SELECT id, configured_children FROM on_families")
        )
        now = datetime.now(timezone.utc)
        for row in result:
            family_id, configured = row[0], row[1]
            if configured is None:
                continue
            if isinstance(configured, str):
                try:
                    names = json.loads(configured)
                except (json.JSONDecodeError, TypeError):
                    names = []
            elif isinstance(configured, list):
                names = configured
            else:
                names = []
            for i, name in enumerate(names):
                if not name or not str(name).strip():
                    continue
                conn.execute(
                    sa.text(
                        "INSERT INTO on_children (family_id, name, institution_type, display_order, created_at) "
                        "VALUES (:fid, :name, 'elementary', :ord, :now)"
                    ),
                    {"fid": family_id, "name": str(name).strip(), "ord": i, "now": now},
                )

    # 3. on_families から configured_children を削除
    if _has_column("on_families", "configured_children"):
        op.drop_column("on_families", "configured_children")


def downgrade() -> None:
    if not _has_table("on_families"):
        return

    # 1. on_families に configured_children を復元
    if not _has_column("on_families", "configured_children"):
        bind = op.get_bind()
        default = sa.text("'[]'::jsonb") if bind.dialect.name == "postgresql" else sa.text("'[]'")
        op.add_column(
            "on_families",
            sa.Column(
                "configured_children",
                sa.JSON(),
                nullable=False,
                server_default=default,
            ),
        )

    # 2. on_children のデータを configured_children に戻す（集約）
    if _has_table("on_children"):
        conn = op.get_bind()
        result = conn.execute(
            sa.text(
                "SELECT family_id, name FROM on_children ORDER BY family_id, display_order, id"
            )
        )
        by_family: dict[int, list[str]] = {}
        for row in result:
            fid, name = row[0], row[1]
            by_family.setdefault(fid, []).append(name)
        for fid, names in by_family.items():
            conn.execute(
                sa.text(
                    "UPDATE on_families SET configured_children = :json WHERE id = :fid"
                ),
                {"json": json.dumps(names), "fid": fid},
            )

    # 3. on_children テーブルを削除
    if _has_table("on_children"):
        op.drop_index("ix_on_children_family_id", "on_children")
        op.drop_table("on_children")
