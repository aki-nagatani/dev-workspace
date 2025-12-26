"""merge heads: fishtrack and mypokedex

Revision ID: merge_fishtrack_mypokedex_heads
Revises: add_user_id_to_holdings, 20251225_change_boxmember_to_composite_primary_key
Create Date: 2025-12-26 18:00:00.000000+00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "merge_fishtrack_mypokedex_heads"
down_revision = ("add_user_id_to_holdings", "20251225_change_boxmember_to_composite_primary_key")
branch_labels = None
depends_on = None


def upgrade():
    """Merge heads from FishTrack and MyPokedex.
    
    This migration merges the heads of both FishTrack and MyPokedex migration chains.
    After this migration, both projects' migrations will be unified in the shared database.
    """
    pass


def downgrade():
    """No-op downgrade for merge migration."""
    pass

