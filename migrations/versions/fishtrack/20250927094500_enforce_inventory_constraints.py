"""Tighten inventory constraints and backfill data."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "1b0dd6f9c9f3"
down_revision = "f3c86ad5df8c"
branch_labels = None
depends_on = None


def _backfill_purchase_dates(table_name: str) -> None:
    op.execute(sa.text(
        f"""
        UPDATE {table_name}
           SET purchase_date =
               COALESCE(
                   purchase_date,
                   CASE
                       WHEN created_at IS NOT NULL THEN CAST(created_at AS DATE)
                       ELSE DATE('1970-01-01')
                   END
               )
         WHERE purchase_date IS NULL
        """
    ))




def _table_exists(conn, table_name: str) -> bool:
    try:
        return inspect(conn).has_table(table_name)
    except Exception:  # pragma: no cover
        return False


def upgrade() -> None:
    op.execute(sa.text(
        """
        UPDATE rod_inventory
           SET model_id = rod_id
         WHERE model_id IS NULL AND rod_id IS NOT NULL
        """
    ))

    conn = op.get_bind()
    has_rod = _table_exists(conn, "rod_inventory")
    has_reel = _table_exists(conn, "reel_inventory")

    if has_rod:
        _backfill_purchase_dates("rod_inventory")
    else:
        return

    if has_reel:
        _backfill_purchase_dates("reel_inventory")

    missing_models = conn.execute(sa.text("SELECT COUNT(1) FROM rod_inventory WHERE model_id IS NULL")).scalar()
    if missing_models:
        raise RuntimeError("rod_inventory contains rows without model_id after backfill")

    missing_rod_dates = conn.execute(sa.text("SELECT COUNT(1) FROM rod_inventory WHERE purchase_date IS NULL")).scalar()
    missing_reel_dates = 0
    if has_reel:
        missing_reel_dates = conn.execute(sa.text("SELECT COUNT(1) FROM reel_inventory WHERE purchase_date IS NULL")).scalar()
    if missing_rod_dates or missing_reel_dates:
        raise RuntimeError("inventory tables still contain NULL purchase_date after backfill")

    with op.batch_alter_table("rod_inventory") as batch:
        batch.alter_column("model_id", existing_type=sa.Integer(), nullable=False)
        batch.alter_column("purchase_date", existing_type=sa.Date(), nullable=False)

    if has_reel:
        with op.batch_alter_table("reel_inventory") as batch:
            batch.alter_column("purchase_date", existing_type=sa.Date(), nullable=False)


def downgrade() -> None:
    conn = op.get_bind()
    has_reel = _table_exists(conn, "reel_inventory")
    has_rod = _table_exists(conn, "rod_inventory")

    if has_reel:
        with op.batch_alter_table("reel_inventory") as batch:
            batch.alter_column("purchase_date", existing_type=sa.Date(), nullable=True)

    if has_rod:
        with op.batch_alter_table("rod_inventory") as batch:
            batch.alter_column("purchase_date", existing_type=sa.Date(), nullable=True)
            batch.alter_column("model_id", existing_type=sa.Integer(), nullable=True)

        op.execute(sa.text(
            """
            UPDATE rod_inventory
               SET purchase_date = NULL
             WHERE purchase_date = DATE('1970-01-01')
            """
        ))

    if has_reel:
        op.execute(sa.text(
            """
            UPDATE reel_inventory
               SET purchase_date = NULL
             WHERE purchase_date = DATE('1970-01-01')
            """
        ))





