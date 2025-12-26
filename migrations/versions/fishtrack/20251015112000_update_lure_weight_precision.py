"""Expand lure weight precision to support sixty-fourth ounce"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "update_lure_weight_precision"
down_revision = "allow_text_pieces_on_rod_model"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("rod_model", schema=None) as batch_op:
        batch_op.alter_column(
            "lure_weight_min_oz",
            existing_type=sa.Numeric(5, 2),
            type_=sa.Numeric(10, 6),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "lure_weight_max_oz",
            existing_type=sa.Numeric(5, 2),
            type_=sa.Numeric(10, 6),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("rod_model", schema=None) as batch_op:
        batch_op.alter_column(
            "lure_weight_min_oz",
            existing_type=sa.Numeric(10, 6),
            type_=sa.Numeric(5, 2),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "lure_weight_max_oz",
            existing_type=sa.Numeric(10, 6),
            type_=sa.Numeric(5, 2),
            existing_nullable=True,
        )
