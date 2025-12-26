"""Rename rod table to rod_model.

Revision ID: 2f071de95ac3
Revises: a43ff432f78e
Create Date: 2025-09-24 09:30:00.000000+00:00

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2f071de95ac3"
down_revision = "a43ff432f78e"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("rod", "rod_model")


def downgrade():
    op.rename_table("rod_model", "rod")
