"""add FK constraints to placement table"""

from __future__ import annotations

from typing import Iterable, Mapping

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import Connection
from sqlalchemy.engine.reflection import Inspector


revision = "20251220_add_placement_fk_constraints"
down_revision = "add_contact_table"
branch_labels = None
depends_on = None

PLACEMENT_TABLE = "placement"
USER_TABLE = "User"


def _table_exists(inspector: Inspector, table_name: str) -> bool:
    try:
        return inspector.has_table(table_name)
    except Exception:  # pragma: no cover - defensive fallback
        return False


def _fk_names(inspector: Inspector, table_name: str) -> set[str]:
    try:
        return {fk["name"] for fk in inspector.get_foreign_keys(table_name)}
    except Exception:
        return set()


def _assert_no_orphans(
    conn: Connection,
    table: str,
    column: str,
    parent_table: str,
    parent_column: str,
) -> None:
    child_col = f'"{column}"'
    parent_col = f'"{parent_column}"'
    criterion = (
        f"NOT EXISTS ("
        f"SELECT 1 FROM \"{parent_table}\" AS parent "
        f"WHERE parent.{parent_col} = child.{child_col}"
        ")"
    )

    sample_sql = sa.text(
        f"""
        SELECT child.id AS row_id, child.{child_col} AS fk_value
        FROM "{table}" AS child
        WHERE child.{child_col} IS NOT NULL
          AND {criterion}
        LIMIT 10
        """
    )
    rows = conn.execute(sample_sql).fetchall()
    if not rows:
        return

    count_sql = sa.text(
        f"""
        SELECT COUNT(*)
        FROM "{table}" AS child
        WHERE child.{child_col} IS NOT NULL
          AND {criterion}
        """
    )
    total = conn.execute(count_sql).scalar() or 0
    preview = ", ".join(f"(id={r.row_id}, value={r.fk_value})" for r in rows)
    if total > len(rows):
        preview += f", ... total {total} rows"
    raise RuntimeError(
        f"Cannot add foreign key on {table}.{column}: orphan rows detected {preview}"
    )


def _ensure_foreign_keys(
    conn: Connection,
    table: str,
    fk_specs: Iterable[Mapping[str, object]],
) -> None:
    inspector = sa.inspect(conn)
    if not _table_exists(inspector, table):
        return

    existing = _fk_names(inspector, table)
    missing = [spec for spec in fk_specs if spec["name"] not in existing]
    if not missing:
        return

    with op.batch_alter_table(table, recreate="always") as batch:
        for spec in missing:
            batch.create_foreign_key(
                spec["name"],
                spec["referred_table"],
                spec["local_cols"],
                spec["remote_cols"],
                ondelete=spec.get("ondelete"),
            )


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # 該当テーブルが存在しない環境（古いテスト DB 等）では何もしない
    if not _table_exists(inspector, PLACEMENT_TABLE):
        return

    # 1. データ整合性確認（孤立レコードが存在する場合は明示的に失敗させる）
    _assert_no_orphans(conn, PLACEMENT_TABLE, "userId", USER_TABLE, "id")

    # 2. 外部キー追加（既に存在する環境ではスキップ）
    _ensure_foreign_keys(
        conn,
        PLACEMENT_TABLE,
        [
            {
                "name": "fk_placement_user",
                "referred_table": USER_TABLE,
                "local_cols": ["userId"],
                "remote_cols": ["id"],
                "ondelete": "CASCADE",
            },
        ],
    )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if not _table_exists(inspector, PLACEMENT_TABLE):
        return

    with op.batch_alter_table(PLACEMENT_TABLE, recreate="always") as batch:
        batch.drop_constraint("fk_placement_user", type_="foreignkey")

