"""merge heads: party_indexes_and_check + expand_dextype

Revision ID: 3eb89a6ae1fc
Revises: 20250903_party_indexes_and_check, 20250910_expand_dextype
Create Date: 2025-09-11 06:08:47.225459+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3eb89a6ae1fc'
down_revision = ('20250903_party_indexes_and_check', '20250910_expand_dextype')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass