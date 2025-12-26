"""rename inventory tables to holding tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8c5396721e3d"
down_revision = "7ef0f2f6a924"
branch_labels = None
depends_on = None


_ROD_INDEXES = [
    ("ix_rod_inventory_model_id", "ix_rod_holding_model_id", ["model_id"]),
    ("ix_rod_inventory_status_updated_at", "ix_rod_holding_status_updated_at", ["status", "updated_at"]),
]


def _table_exists(inspector: sa.inspect, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "rod_inventory"):
        op.rename_table("rod_inventory", "rod_holding")
        inspector = sa.inspect(bind)
    if _table_exists(inspector, "reel_inventory"):
        op.rename_table("reel_inventory", "reel_holding")
        inspector = sa.inspect(bind)

    if _table_exists(inspector, "rod_holding"):
        if dialect == "sqlite":
            for old, new, columns in _ROD_INDEXES:
                op.execute(f"DROP INDEX IF EXISTS {old}")
                op.execute(f"DROP INDEX IF EXISTS {new}")
                op.create_index(new, "rod_holding", columns, unique=False)
        else:
            for old, new, _ in _ROD_INDEXES:
                op.execute(sa.text(f"ALTER INDEX IF EXISTS {old} RENAME TO {new}"))


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "rod_holding"):
        if dialect == "sqlite":
            for old, new, columns in _ROD_INDEXES:
                op.execute(f"DROP INDEX IF EXISTS {new}")
                op.create_index(old, "rod_inventory", columns, unique=False)
        else:
            for old, new, _ in _ROD_INDEXES:
                op.execute(sa.text(f"ALTER INDEX IF EXISTS {new} RENAME TO {old}"))

    inspector = sa.inspect(bind)
    if _table_exists(inspector, "rod_holding"):
        op.rename_table("rod_holding", "rod_inventory")
        inspector = sa.inspect(bind)
    if _table_exists(inspector, "reel_holding"):
        op.rename_table("reel_holding", "reel_inventory")

