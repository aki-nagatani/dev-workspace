"""Add carbon rate percentage column to rod_model."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "add_carbon_rate_to_rod_model"
down_revision = "update_lure_weight_precision"
branch_labels = None
depends_on = None


CHECK_CONSTRAINT_NAME = "ck_rod_carbon_rate_pct_range"


def upgrade() -> None:
    with op.batch_alter_table("rod_model", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("carbon_rate_pct", sa.Numeric(4, 1), nullable=True)
        )
        batch_op.create_check_constraint(
            CHECK_CONSTRAINT_NAME,
            "carbon_rate_pct IS NULL OR (carbon_rate_pct >= 0 AND carbon_rate_pct <= 100)",
        )


def downgrade() -> None:
    with op.batch_alter_table("rod_model", schema=None) as batch_op:
        batch_op.drop_constraint(CHECK_CONSTRAINT_NAME, type_="check")
        batch_op.drop_column("carbon_rate_pct")

