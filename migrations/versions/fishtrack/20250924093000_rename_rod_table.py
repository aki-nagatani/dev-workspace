"""Rename rod table to rod_model.

Revision ID: 2f071de95ac3
Revises: a43ff432f78e
Create Date: 2025-09-24 09:30:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2f071de95ac3"
down_revision = "a43ff432f78e"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    """Check if a table exists in the database."""
    return table_name in inspector.get_table_names()


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Only rename if rod table exists and rod_model doesn't exist
    if _table_exists(inspector, "rod") and not _table_exists(inspector, "rod_model"):
        op.rename_table("rod", "rod_model")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Only rename if rod_model table exists and rod doesn't exist
    if _table_exists(inspector, "rod_model") and not _table_exists(inspector, "rod"):
        op.rename_table("rod_model", "rod")
