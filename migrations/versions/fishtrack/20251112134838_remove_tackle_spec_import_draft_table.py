"""Remove tackle_spec_import_draft table (cleanup after draft functionality removal)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "remove_tackle_draft_table"
down_revision = "add_carbon_rate_to_rod_model"
branch_labels = None
depends_on = None


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    """Check if a table exists."""
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Remove tackle_spec_import_draft table and its indexes."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    draft_exists = _table_exists(inspector, "tackle_spec_import_draft")

    if draft_exists:
        # インチE��クスを削除
        existing_idx = {idx["name"] for idx in inspector.get_indexes("tackle_spec_import_draft")}
        for idx_name in ("idx_tsi_draft_category", "idx_tsi_draft_status"):
            if idx_name in existing_idx:
                try:
                    op.drop_index(idx_name, table_name="tackle_spec_import_draft")
                except Exception:
                    # インチE��クスが既に存在しなぁE��合�EスキチE�E
                    pass

        # チE�Eブルを削除
        op.drop_table("tackle_spec_import_draft")


def downgrade() -> None:
    """Recreate tackle_spec_import_draft table (for rollback purposes)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    draft_exists = _table_exists(inspector, "tackle_spec_import_draft")
    if draft_exists:
        # 既に存在する場合�E何もしなぁE
        return

    _DRAFT_CATEGORY_CONSTRAINT = "category IN ('rod_model','reel_model','lure')"
    _DRAFT_MODE_CONSTRAINT = "mode IN ('create','update','hold')"
    _DRAFT_STATUS_CONSTRAINT = "status IN ('pending','committed','expired','discarded')"

    op.create_table(
        "tackle_spec_import_draft",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("mode", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default=sa.text("'pending'")),
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

