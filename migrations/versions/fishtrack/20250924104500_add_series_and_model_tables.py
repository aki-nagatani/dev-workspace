"""Add rod and reel series/model tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "74387003a93b"
down_revision = "2f071de95ac3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS reel_model")
    op.execute("DROP TABLE IF EXISTS reel_series")
    op.execute("DROP TABLE IF EXISTS rod_series")

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

    with op.batch_alter_table("rod_model") as batch_op:
        batch_op.add_column(sa.Column("series_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("model_code", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("display_name", sa.String(length=128), nullable=True))
        batch_op.create_foreign_key(
            "fk_rod_model_series_id",
            "rod_series",
            ["series_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_unique_constraint(
            "uq_rod_model_series_code",
            ["series_id", "model_code"],
        )

    op.execute("UPDATE rod_model SET display_name = model_name WHERE display_name IS NULL")

    with op.batch_alter_table("rod_inventory") as batch_op:
        batch_op.alter_column("rod_id", existing_type=sa.Integer(), nullable=True)
        batch_op.add_column(sa.Column("model_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_rod_inventory_model_id",
            "rod_model",
            ["model_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index("ix_rod_inventory_model_id", ["model_id"], unique=False)

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
