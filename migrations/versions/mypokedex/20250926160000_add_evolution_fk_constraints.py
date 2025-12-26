"""add FK constraints to evolution table"""

from __future__ import annotations

from typing import Iterable, Mapping

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import Connection
from sqlalchemy.engine.reflection import Inspector


revision = "20250926160000_add_evolution_fk_constraints"
down_revision = "20250926145000_add_party_box_fk_constraints"
branch_labels = None
depends_on = None

EVOLUTION_TABLE = "evolution"
POKEMON_TABLE = "Pokemon"


def _table_exists(inspector: Inspector, table_name: str) -> bool:
    try:
        return inspector.has_table(table_name)
    except Exception:  # pragma: no cover
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

    if not _table_exists(inspector, EVOLUTION_TABLE):
        return

    _assert_no_orphans(conn, EVOLUTION_TABLE, "fromNationalNo", POKEMON_TABLE, "nationalNo")
    _assert_no_orphans(conn, EVOLUTION_TABLE, "toNationalNo", POKEMON_TABLE, "nationalNo")

    _ensure_foreign_keys(
        conn,
        EVOLUTION_TABLE,
        [
            {
                "name": "fk_evolution_from_pokemon",
                "referred_table": POKEMON_TABLE,
                "local_cols": ["fromNationalNo"],
                "remote_cols": ["nationalNo"],
                "ondelete": "RESTRICT",
            },
            {
                "name": "fk_evolution_to_pokemon",
                "referred_table": POKEMON_TABLE,
                "local_cols": ["toNationalNo"],
                "remote_cols": ["nationalNo"],
                "ondelete": "RESTRICT",
            },
        ],
    )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if not _table_exists(inspector, EVOLUTION_TABLE):
        return

    with op.batch_alter_table(EVOLUTION_TABLE, recreate="always") as batch:
        for fk_name in ("fk_evolution_from_pokemon", "fk_evolution_to_pokemon"):
            batch.drop_constraint(fk_name, type_="foreignkey")
