"""Add tackle spec import draft and log tables."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f5e0b9f8a4c"
down_revision = "8f1d7f8b8d6e"
branch_labels = None
depends_on = None


_DRAFT_CATEGORY_CONSTRAINT = "category IN ('rod_model','reel_model','lure')"
_DRAFT_MODE_CONSTRAINT = "mode IN ('create','update','hold')"
_DRAFT_STATUS_CONSTRAINT = "status IN ('pending','committed','expired','discarded')"
_LOG_CATEGORY_CONSTRAINT = "category IN ('rod_model','reel_model','lure')"
_LOG_MODE_CONSTRAINT = "mode IN ('create','update','hold')"
_LOG_RESULT_CONSTRAINT = "result IN ('success','failure','expired')"


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _table_exists(inspector, "tackle_spec_import_draft"):
        op.create_table(
            "tackle_spec_import_draft",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("category", sa.String(length=32), nullable=False),
            sa.Column("mode", sa.String(length=16), nullable=False),
            sa.Column(
                "status",
                sa.String(length=16),
                nullable=False,
                server_default=sa.text("'pending'"),
            ),
            sa.Column("source_url", sa.String(length=512), nullable=False),
            sa.Column("template_key", sa.String(length=128), nullable=True),
            sa.Column("target_master_id", sa.Integer(), nullable=True),
            sa.Column("preview_payload", sa.JSON(), nullable=False),
            sa.Column("raw_payload", sa.JSON(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column(
                "created_by",
                sa.Integer(),
                sa.ForeignKey("fishtrack_user.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "updated_by",
                sa.Integer(),
                sa.ForeignKey("fishtrack_user.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.CheckConstraint(_DRAFT_CATEGORY_CONSTRAINT, name="ck_tsi_draft_category"),
            sa.CheckConstraint(_DRAFT_MODE_CONSTRAINT, name="ck_tsi_draft_mode"),
            sa.CheckConstraint(_DRAFT_STATUS_CONSTRAINT, name="ck_tsi_draft_status"),
        )
        op.create_index(
            "idx_tsi_draft_status",
            "tackle_spec_import_draft",
            ["status", "expires_at"],
        )
        op.create_index(
            "idx_tsi_draft_category",
            "tackle_spec_import_draft",
            ["category", "status"],
        )

    if not _table_exists(inspector, "tackle_spec_import_log"):
        op.create_table(
            "tackle_spec_import_log",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "draft_id",
                sa.Integer(),
                sa.ForeignKey("tackle_spec_import_draft.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("category", sa.String(length=32), nullable=False),
            sa.Column("mode", sa.String(length=16), nullable=False),
            sa.Column("result", sa.String(length=16), nullable=False),
            sa.Column("target_master_id", sa.Integer(), nullable=True),
            sa.Column(
                "operator_user_id",
                sa.Integer(),
                sa.ForeignKey("fishtrack_user.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("error_detail", sa.Text(), nullable=True),
            sa.Column("committed_at", sa.DateTime(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.CheckConstraint(_LOG_CATEGORY_CONSTRAINT, name="ck_tsi_log_category"),
            sa.CheckConstraint(_LOG_MODE_CONSTRAINT, name="ck_tsi_log_mode"),
            sa.CheckConstraint(_LOG_RESULT_CONSTRAINT, name="ck_tsi_log_result"),
        )
        op.create_index(
            "idx_tsi_log_created",
            "tackle_spec_import_log",
            [sa.text("created_at DESC")],
        )
        op.create_index(
            "idx_tsi_log_category",
            "tackle_spec_import_log",
            ["category", "result"],
        )
        op.create_index(
            "idx_tsi_log_target",
            "tackle_spec_import_log",
            ["target_master_id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "tackle_spec_import_log"):
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("tackle_spec_import_log")}
        if "idx_tsi_log_target" in existing_indexes:
            op.drop_index("idx_tsi_log_target", table_name="tackle_spec_import_log")
        if "idx_tsi_log_category" in existing_indexes:
            op.drop_index("idx_tsi_log_category", table_name="tackle_spec_import_log")
        if "idx_tsi_log_created" in existing_indexes:
            op.drop_index("idx_tsi_log_created", table_name="tackle_spec_import_log")
        op.drop_table("tackle_spec_import_log")

    if _table_exists(inspector, "tackle_spec_import_draft"):
        existing_indexes = {idx["name"] for idx in inspector.get_indexes("tackle_spec_import_draft")}
        if "idx_tsi_draft_category" in existing_indexes:
            op.drop_index("idx_tsi_draft_category", table_name="tackle_spec_import_draft")
        if "idx_tsi_draft_status" in existing_indexes:
            op.drop_index("idx_tsi_draft_status", table_name="tackle_spec_import_draft")
        op.drop_table("tackle_spec_import_draft")
