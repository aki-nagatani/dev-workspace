"""Make rod_model.series_id NOT NULL

This migration makes the rod_model.series_id column NOT NULL to match
the model definition and specification.

Revision ID: make_rod_model_series_id_not_null
Revises: add_user_id_to_holdings
Create Date: 2026-01-02 02:00:00.000000+00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "make_rod_model_series_id_not_null"
down_revision = "add_user_id_to_holdings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make rod_model.series_id NOT NULL."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Check if rod_model table exists
    if "rod_model" not in inspector.get_table_names():
        return
    
    # Check if series_id column exists
    columns = {col["name"] for col in inspector.get_columns("rod_model")}
    if "series_id" not in columns:
        return
    
    # Check if there are any NULL values in series_id
    result = bind.execute(sa.text("SELECT COUNT(*) FROM rod_model WHERE series_id IS NULL"))
    null_count = result.scalar()
    
    if null_count > 0:
        raise ValueError(
            f"Cannot make series_id NOT NULL: {null_count} rows have NULL values. "
            "Please update these rows before running this migration."
        )
    
    # Make series_id NOT NULL
    with op.batch_alter_table("rod_model", schema=None) as batch_op:
        batch_op.alter_column(
            "series_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade() -> None:
    """Make rod_model.series_id nullable (revert to previous state)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Check if rod_model table exists
    if "rod_model" not in inspector.get_table_names():
        return
    
    # Check if series_id column exists
    columns = {col["name"] for col in inspector.get_columns("rod_model")}
    if "series_id" not in columns:
        return
    
    # Make series_id nullable
    with op.batch_alter_table("rod_model", schema=None) as batch_op:
        batch_op.alter_column(
            "series_id",
            existing_type=sa.Integer(),
            nullable=True,
        )

