"""Add user_id to rod_holding and reel_holding tables

This migration adds user_id columns to rod_holding and reel_holding tables
to associate each holding record with a specific user.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_user_id_to_holdings"
down_revision = "remove_tackle_draft_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Add user_id to rod_holding table
    if "rod_holding" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("rod_holding")}
        if "user_id" not in columns:
            # First, add the column as nullable to allow existing data
            op.add_column(
                "rod_holding",
                sa.Column("user_id", sa.Integer(), nullable=True),
            )
            
            # Set default user_id for existing records (use user_id=1 if exists, otherwise NULL)
            # This assumes there's at least one user in the system
            op.execute("""
                UPDATE rod_holding 
                SET user_id = (
                    SELECT id FROM fishtrack_user ORDER BY id LIMIT 1
                )
                WHERE user_id IS NULL
            """)
            
            # Now make it NOT NULL after setting default values
            # SQLite doesn't support ALTER COLUMN ... SET NOT NULL, so we need to recreate the table
            bind = op.get_bind()
            if bind.dialect.name == "sqlite":
                # For SQLite, we need to recreate the table
                # Get existing indexes to recreate them later
                existing_indexes = []
                try:
                    for idx in inspector.get_indexes("rod_holding"):
                        if idx["name"] not in ["idx_rod_holding_user_id"]:
                            existing_indexes.append((idx["name"], idx["column_names"]))
                except Exception:
                    pass
                
                # Create new table with user_id as NOT NULL
                op.execute("""
                    CREATE TABLE rod_holding_new (
                        id INTEGER NOT NULL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        rod_id INTEGER,
                        model_id INTEGER,
                        status VARCHAR(16) NOT NULL,
                        purchase_date DATE,
                        purchase_shop VARCHAR(128),
                        purchase_price INTEGER,
                        condition VARCHAR(16) NOT NULL,
                        memo TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        CHECK (status IN ('own', 'unowned')),
                        CHECK (condition IN ('new', 'used'))
                    )
                """)
                op.execute("""
                    INSERT INTO rod_holding_new 
                    SELECT id, user_id, rod_id, model_id, status, purchase_date, 
                           purchase_shop, purchase_price, condition, memo, created_at, updated_at
                    FROM rod_holding 
                    WHERE user_id IS NOT NULL
                """)
                op.execute("DROP TABLE rod_holding")
                op.execute("ALTER TABLE rod_holding_new RENAME TO rod_holding")
                
                # Recreate indexes
                op.create_index("idx_rod_holding_user_id", "rod_holding", ["user_id"])
                for idx_name, idx_columns in existing_indexes:
                    try:
                        op.create_index(idx_name, "rod_holding", idx_columns)
                    except Exception:
                        pass
            else:
                op.alter_column(
                    "rod_holding",
                    "user_id",
                    nullable=False,
                )
                # Add foreign key constraint
                op.create_foreign_key(
                    "fk_rod_holding_user_id",
                    "rod_holding",
                    "fishtrack_user",
                    ["user_id"],
                    ["id"],
                    ondelete="CASCADE",
                )
                # Add index for performance
                op.create_index(
                    "idx_rod_holding_user_id",
                    "rod_holding",
                    ["user_id"],
                )
    
    # Add user_id to reel_holding table
    if "reel_holding" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("reel_holding")}
        if "user_id" not in columns:
            # First, add the column as nullable to allow existing data
            op.add_column(
                "reel_holding",
                sa.Column("user_id", sa.Integer(), nullable=True),
            )
            
            # Set default user_id for existing records (use user_id=1 if exists, otherwise NULL)
            op.execute("""
                UPDATE reel_holding 
                SET user_id = (
                    SELECT id FROM fishtrack_user ORDER BY id LIMIT 1
                )
                WHERE user_id IS NULL
            """)
            
            # Now make it NOT NULL after setting default values
            # SQLite doesn't support ALTER COLUMN ... SET NOT NULL, so we need to recreate the table
            bind = op.get_bind()
            if bind.dialect.name == "sqlite":
                # For SQLite, we need to recreate the table
                # Get existing indexes to recreate them later
                existing_indexes = []
                try:
                    for idx in inspector.get_indexes("reel_holding"):
                        if idx["name"] not in ["idx_reel_holding_user_id"]:
                            existing_indexes.append((idx["name"], idx["column_names"]))
                except Exception:
                    pass
                
                op.execute("""
                    CREATE TABLE reel_holding_new (
                        id INTEGER NOT NULL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        model_id INTEGER NOT NULL,
                        status VARCHAR(16) NOT NULL,
                        purchase_date DATE,
                        purchase_shop VARCHAR(128),
                        purchase_price INTEGER,
                        condition VARCHAR(16) NOT NULL,
                        memo TEXT,
                        created_at TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP NOT NULL,
                        CHECK (status IN ('own', 'unowned')),
                        CHECK (condition IN ('new', 'used'))
                    )
                """)
                op.execute("""
                    INSERT INTO reel_holding_new 
                    SELECT id, user_id, model_id, status, purchase_date, 
                           purchase_shop, purchase_price, condition, memo, created_at, updated_at
                    FROM reel_holding 
                    WHERE user_id IS NOT NULL
                """)
                op.execute("DROP TABLE reel_holding")
                op.execute("ALTER TABLE reel_holding_new RENAME TO reel_holding")
                
                # Recreate indexes
                op.create_index("idx_reel_holding_user_id", "reel_holding", ["user_id"])
                for idx_name, idx_columns in existing_indexes:
                    try:
                        op.create_index(idx_name, "reel_holding", idx_columns)
                    except Exception:
                        pass
            else:
                op.alter_column(
                    "reel_holding",
                    "user_id",
                    nullable=False,
                )
                # Add foreign key constraint
                op.create_foreign_key(
                    "fk_reel_holding_user_id",
                    "reel_holding",
                    "fishtrack_user",
                    ["user_id"],
                    ["id"],
                    ondelete="CASCADE",
                )
                # Add index for performance
                op.create_index(
                    "idx_reel_holding_user_id",
                    "reel_holding",
                    ["user_id"],
                )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Remove user_id from reel_holding table
    if "reel_holding" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("reel_holding")}
        if "user_id" in columns:
            # Drop index first
            try:
                op.drop_index("idx_reel_holding_user_id", table_name="reel_holding")
            except Exception:
                pass
            
            # Drop foreign key constraint
            try:
                op.drop_constraint("fk_reel_holding_user_id", "reel_holding", type_="foreignkey")
            except Exception:
                pass
            
            # Drop column
            op.drop_column("reel_holding", "user_id")
    
    # Remove user_id from rod_holding table
    if "rod_holding" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("rod_holding")}
        if "user_id" in columns:
            # Drop index first
            try:
                op.drop_index("idx_rod_holding_user_id", table_name="rod_holding")
            except Exception:
                pass
            
            # Drop foreign key constraint
            try:
                op.drop_constraint("fk_rod_holding_user_id", "rod_holding", type_="foreignkey")
            except Exception:
                pass
            
            # Drop column
            op.drop_column("rod_holding", "user_id")

