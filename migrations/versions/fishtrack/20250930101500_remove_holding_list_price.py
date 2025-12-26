"""Remove list_price from holding tables."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f1d7f8b8d6e"
down_revision = "8c5396721e3d"
branch_labels = None
depends_on = None


_DEFERRABLE = sa.text


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "rod_holding" in inspector.get_table_names():
        with op.batch_alter_table("rod_holding", schema=None) as batch_op:
            if any(col["name"] == "list_price" for col in inspector.get_columns("rod_holding")):
                batch_op.drop_column("list_price")
    if "reel_holding" in inspector.get_table_names():
        with op.batch_alter_table("reel_holding", schema=None) as batch_op:
            if any(col["name"] == "list_price" for col in inspector.get_columns("reel_holding")):
                batch_op.drop_column("list_price")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "rod_holding" in inspector.get_table_names():
        with op.batch_alter_table("rod_holding", schema=None) as batch_op:
            if not any(col["name"] == "list_price" for col in inspector.get_columns("rod_holding")):
                batch_op.add_column(sa.Column("list_price", sa.Integer(), nullable=True))
    if "reel_holding" in inspector.get_table_names():
        with op.batch_alter_table("reel_holding", schema=None) as batch_op:
            if not any(col["name"] == "list_price" for col in inspector.get_columns("reel_holding")):
                batch_op.add_column(sa.Column("list_price", sa.Integer(), nullable=True))
