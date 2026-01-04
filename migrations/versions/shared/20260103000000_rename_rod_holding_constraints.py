"""Rename rod_holding check constraints from ck_rod_inventory_* to ck_rod_holding_*

This migration renames the check constraints on the rod_holding table to match
the current model definition. The constraints were created with the old table
name (rod_inventory) and were not updated when the table was renamed.

Revision ID: rename_rod_holding_constraints
Revises: merge_fishtrack_mypokedex_heads
Create Date: 2026-01-03 00:00:00.000000+00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "rename_rod_holding_constraints"
down_revision = "merge_fishtrack_mypokedex_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename check constraints from ck_rod_inventory_* to ck_rod_holding_*."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Check if rod_holding table exists
    if "rod_holding" not in inspector.get_table_names():
        return
    
    # Get existing constraints
    constraints = inspector.get_check_constraints("rod_holding")
    constraint_names = {c["name"] for c in constraints}
    
    # Use batch_alter_table for constraint operations
    with op.batch_alter_table("rod_holding", schema=None) as batch_op:
        # Drop old constraints if they exist
        if "ck_rod_inventory_status" in constraint_names:
            batch_op.drop_constraint("ck_rod_inventory_status", type_="check")
        
        if "ck_rod_inventory_condition" in constraint_names:
            batch_op.drop_constraint("ck_rod_inventory_condition", type_="check")
        
        # Create new constraints if they don't already exist
        if "ck_rod_holding_status" not in constraint_names:
            batch_op.create_check_constraint(
                "ck_rod_holding_status",
                "status IN ('own','unowned')",
            )
        
        if "ck_rod_holding_condition" not in constraint_names:
            batch_op.create_check_constraint(
                "ck_rod_holding_condition",
                "condition IN ('new','used')",
            )


def downgrade() -> None:
    """Revert constraint names back to ck_rod_inventory_*."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Check if rod_holding table exists
    if "rod_holding" not in inspector.get_table_names():
        return
    
    # Get existing constraints
    constraints = inspector.get_check_constraints("rod_holding")
    constraint_names = {c["name"] for c in constraints}
    
    # Use batch_alter_table for constraint operations
    with op.batch_alter_table("rod_holding", schema=None) as batch_op:
        # Drop new constraints if they exist
        if "ck_rod_holding_status" in constraint_names:
            batch_op.drop_constraint("ck_rod_holding_status", type_="check")
        
        if "ck_rod_holding_condition" in constraint_names:
            batch_op.drop_constraint("ck_rod_holding_condition", type_="check")
        
        # Recreate old constraints if they don't exist
        if "ck_rod_inventory_status" not in constraint_names:
            batch_op.create_check_constraint(
                "ck_rod_inventory_status",
                "status IN ('own','unowned')",
            )
        
        if "ck_rod_inventory_condition" not in constraint_names:
            batch_op.create_check_constraint(
                "ck_rod_inventory_condition",
                "condition IN ('new','used')",
            )

