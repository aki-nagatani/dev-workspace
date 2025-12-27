"""Add rod and reel series/model tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "74387003a93b"
down_revision = "2f071de95ac3"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    """Check if a table exists in the database."""
    return table_name in inspector.get_table_names()


def _has_column(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    try:
        return any(col["name"] == column_name for col in inspector.get_columns(table_name))
    except Exception:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Don't drop existing tables as they may have dependencies
    # Just create tables if they don't exist
    
    # Create tables only if they don't exist
    if not _table_exists(inspector, "rod_series"):
        op.create_table(
        "rod_series",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("manufacturer_id", sa.Integer(), nullable=False),
        sa.Column("series_name", sa.String(length=128), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["manufacturer_id"], ["manufacturer.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("manufacturer_id", "series_name", name="uq_rod_series_name_per_manufacturer"),
        )
    
    # Refresh inspector after potential table creation
    inspector = sa.inspect(bind)
    
    if not _table_exists(inspector, "reel_series"):
        op.create_table(
        "reel_series",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("manufacturer_id", sa.Integer(), nullable=False),
        sa.Column("series_name", sa.String(length=128), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["manufacturer_id"], ["manufacturer.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("manufacturer_id", "series_name", name="uq_reel_series_name_per_manufacturer"),
        )
    
    # Refresh inspector after potential table creation
    inspector = sa.inspect(bind)
    
    if not _table_exists(inspector, "reel_model"):
        op.create_table(
        "reel_model",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("manufacturer_id", sa.Integer(), nullable=False),
        sa.Column("series_id", sa.Integer(), nullable=False),
        sa.Column("model_code", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("gear_ratio", sa.String(length=32), nullable=True),
        sa.Column("weight_g", sa.Integer(), nullable=True),
        sa.Column("reel_type", sa.String(length=16), nullable=False),
        sa.Column("memo", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint("reel_type IN ('spinning','bait')", name="ck_reel_model_type"),
        sa.UniqueConstraint("series_id", "model_code", name="uq_reel_model_code_per_series"),
        sa.ForeignKeyConstraint(["manufacturer_id"], ["manufacturer.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["series_id"], ["reel_series.id"], ondelete="RESTRICT"),
        )
    
    # Refresh inspector after potential table creation
    inspector = sa.inspect(bind)
    
    # Only alter rod_model if it exists
    if _table_exists(inspector, "rod_model"):
        with op.batch_alter_table("rod_model") as batch_op:
            # Add columns only if they don't exist
            if not _has_column(inspector, "rod_model", "series_id"):
                batch_op.add_column(sa.Column("series_id", sa.Integer(), nullable=True))
            if not _has_column(inspector, "rod_model", "model_code"):
                batch_op.add_column(sa.Column("model_code", sa.String(length=64), nullable=True))
            if not _has_column(inspector, "rod_model", "display_name"):
                batch_op.add_column(sa.Column("display_name", sa.String(length=128), nullable=True))
            
            # Create foreign key only if series_id column exists, rod_series table exists, and constraint doesn't exist
            if _has_column(inspector, "rod_model", "series_id") and _table_exists(inspector, "rod_series"):
                existing_fks = {fk["name"] for fk in inspector.get_foreign_keys("rod_model")}
                if "fk_rod_model_series_id" not in existing_fks:
                    batch_op.create_foreign_key(
                        "fk_rod_model_series_id",
                        "rod_series",
                        ["series_id"],
                        ["id"],
                        ondelete="RESTRICT",
                    )
            
            # Create unique constraint only if both columns exist and constraint doesn't exist
            if _has_column(inspector, "rod_model", "series_id") and _has_column(inspector, "rod_model", "model_code"):
                existing_constraints = {uc["name"] for uc in inspector.get_unique_constraints("rod_model")}
                if "uq_rod_model_series_code" not in existing_constraints:
                    batch_op.create_unique_constraint(
                        "uq_rod_model_series_code",
                        ["series_id", "model_code"],
                    )
        
        # Refresh inspector after potential column additions
        inspector = sa.inspect(bind)
        if _has_column(inspector, "rod_model", "display_name") and _has_column(inspector, "rod_model", "model_name"):
            op.execute("UPDATE rod_model SET display_name = model_name WHERE display_name IS NULL")
    
    # Refresh inspector
    inspector = sa.inspect(bind)
    
    # Only alter rod_inventory if it exists
    if _table_exists(inspector, "rod_inventory"):
        with op.batch_alter_table("rod_inventory") as batch_op:
            # Alter rod_id column only if it's not nullable
            rod_id_col = next((col for col in inspector.get_columns("rod_inventory") if col["name"] == "rod_id"), None)
            if rod_id_col and rod_id_col.get("nullable") is False:
                batch_op.alter_column("rod_id", existing_type=sa.Integer(), nullable=True)
            
            # Add model_id column only if it doesn't exist
            if not _has_column(inspector, "rod_inventory", "model_id"):
                batch_op.add_column(sa.Column("model_id", sa.Integer(), nullable=True))
            
            # Create foreign key only if model_id column exists and constraint doesn't exist
            if _has_column(inspector, "rod_inventory", "model_id"):
                existing_fks = {fk["name"] for fk in inspector.get_foreign_keys("rod_inventory")}
                if "fk_rod_inventory_model_id" not in existing_fks:
                    batch_op.create_foreign_key(
                        "fk_rod_inventory_model_id",
                        "rod_model",
                        ["model_id"],
                        ["id"],
                        ondelete="SET NULL",
                    )
            
            # Create index only if model_id column exists and index doesn't exist
            if _has_column(inspector, "rod_inventory", "model_id"):
                existing_indexes = {idx["name"] for idx in inspector.get_indexes("rod_inventory")}
                if "ix_rod_inventory_model_id" not in existing_indexes:
                    batch_op.create_index("ix_rod_inventory_model_id", ["model_id"], unique=False)
        
        # Refresh inspector after potential column additions
        inspector = sa.inspect(bind)
        if _has_column(inspector, "rod_inventory", "model_id") and _has_column(inspector, "rod_inventory", "rod_id"):
            op.execute("UPDATE rod_inventory SET model_id = rod_id WHERE model_id IS NULL")


def downgrade() -> None:
    op.execute("UPDATE rod_inventory SET model_id = NULL")

    with op.batch_alter_table("rod_inventory") as batch_op:
        batch_op.drop_index("ix_rod_inventory_model_id")
        batch_op.drop_constraint("fk_rod_inventory_model_id", type_="foreignkey")
        batch_op.drop_column("model_id")
        batch_op.alter_column("rod_id", existing_type=sa.Integer(), nullable=False)

    with op.batch_alter_table("rod_model") as batch_op:
        batch_op.drop_constraint("uq_rod_model_series_code", type_="unique")
        batch_op.drop_constraint("fk_rod_model_series_id", type_="foreignkey")
        batch_op.drop_column("display_name")
        batch_op.drop_column("model_code")
        batch_op.drop_column("series_id")

    op.drop_table("reel_model")
    op.drop_table("reel_series")
    op.drop_table("rod_series")
