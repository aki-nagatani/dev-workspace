"""Allow storing textual values in rod_model.pieces."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "allow_text_pieces_on_rod_model"
down_revision = "unify_model_name"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("rod_model", schema=None) as batch_op:
        batch_op.alter_column(
            "pieces",
            existing_type=sa.Integer(),
            type_=sa.String(length=32),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("rod_model", schema=None) as batch_op:
        batch_op.alter_column(
            "pieces",
            existing_type=sa.String(length=32),
            type_=sa.Integer(),
            existing_nullable=True,
        )
