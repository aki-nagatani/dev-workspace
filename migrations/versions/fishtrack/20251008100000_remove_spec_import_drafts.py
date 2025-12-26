"""Remove tackle spec import draft table and reshape log."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bf1a5ad8f4cd"
down_revision = "f3b865cea1d0"
branch_labels = None
depends_on = None


_LOG_CATEGORY_CONSTRAINT = "category IN ('rod_model','reel_model','lure')"
_LOG_INTENT_CONSTRAINT = "intent IN ('create','update')"
_LOG_MODE_CONSTRAINT = "mode IN ('create','update','discard')"
_LOG_RESULT_CONSTRAINT = "result IN ('applied','discarded','failure')"

_DRAFT_CATEGORY_CONSTRAINT = _LOG_CATEGORY_CONSTRAINT
_DRAFT_MODE_CONSTRAINT = "mode IN ('create','update','hold')"
_DRAFT_STATUS_CONSTRAINT = "status IN ('pending','committed','expired','discarded')"

_OLD_LOG_MODE_CONSTRAINT = "mode IN ('create','update','hold')"
_OLD_LOG_RESULT_CONSTRAINT = "result IN ('success','failure','expired')"


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    log_exists = _table_exists(inspector, "tackle_spec_import_log")
    draft_exists = _table_exists(inspector, "tackle_spec_import_draft")

    if log_exists:
        op.create_table(
            "tackle_spec_import_log__new",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("category", sa.String(length=32), nullable=False),
            sa.Column("intent", sa.String(length=16), nullable=False),
            sa.Column("mode", sa.String(length=16), nullable=False),
            sa.Column("result", sa.String(length=16), nullable=False),
            sa.Column("target_master_id", sa.Integer(), nullable=True),
            sa.Column(
                "operator_user_id",
                sa.Integer(),
                sa.ForeignKey("fishtrack_user.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "source_url",
                sa.Text(),
                nullable=False,
                server_default=sa.text("'unknown'"),
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
            sa.CheckConstraint(_LOG_INTENT_CONSTRAINT, name="ck_tsi_log_intent"),
            sa.CheckConstraint(_LOG_MODE_CONSTRAINT, name="ck_tsi_log_mode"),
            sa.CheckConstraint(_LOG_RESULT_CONSTRAINT, name="ck_tsi_log_result"),
        )

        if draft_exists:
            op.execute(
                sa.text(
                    "INSERT INTO tackle_spec_import_log__new (id, category, intent, mode, result, target_master_id, operator_user_id, source_url, summary, error_detail, committed_at, created_at, updated_at) "
                    "SELECT l.id, l.category, CASE l.mode WHEN 'create' THEN 'create' ELSE 'update' END AS intent, "
                    "       CASE l.mode WHEN 'hold' THEN 'discard' ELSE l.mode END AS mode, "
                    "       CASE l.result WHEN 'success' THEN 'applied' WHEN 'expired' THEN 'discarded' ELSE 'failure' END AS result, "
                    "       l.target_master_id, l.operator_user_id, COALESCE(d.source_url, 'unknown') AS source_url, "
                    "       l.summary, l.error_detail, l.committed_at, l.created_at, l.updated_at "
                    "  FROM tackle_spec_import_log l "
                    "  LEFT JOIN tackle_spec_import_draft d ON l.draft_id = d.id"
                )
            )
        else:
            op.execute(
                sa.text(
                    "INSERT INTO tackle_spec_import_log__new (id, category, intent, mode, result, target_master_id, operator_user_id, source_url, summary, error_detail, committed_at, created_at, updated_at) "
                    "SELECT id, category, CASE mode WHEN 'create' THEN 'create' ELSE 'update' END, "
                    "       CASE mode WHEN 'hold' THEN 'discard' ELSE mode END, "
                    "       CASE result WHEN 'success' THEN 'applied' WHEN 'expired' THEN 'discarded' ELSE 'failure' END, "
                    "       target_master_id, operator_user_id, 'unknown', summary, error_detail, committed_at, created_at, updated_at "
                    "  FROM tackle_spec_import_log"
                )
            )

        existing_idx = {idx["name"] for idx in inspector.get_indexes("tackle_spec_import_log")}
        for idx in ("idx_tsi_log_target", "idx_tsi_log_category", "idx_tsi_log_entry", "idx_tsi_log_created"):
            if idx in existing_idx:
                op.drop_index(idx, table_name="tackle_spec_import_log")

        op.drop_table("tackle_spec_import_log")
        op.rename_table("tackle_spec_import_log__new", "tackle_spec_import_log")

        op.create_index(
            "idx_tsi_log_created",
            "tackle_spec_import_log",
            ["created_at"],
        )
        op.create_index(
            "idx_tsi_log_category",
            "tackle_spec_import_log",
            ["category", "result"],
        )
        op.create_index(
            "idx_tsi_log_operator",
            "tackle_spec_import_log",
            ["operator_user_id", "created_at"],
        )

    if draft_exists:
        existing_idx = {idx["name"] for idx in inspector.get_indexes("tackle_spec_import_draft")}
        for idx in ("idx_tsi_draft_category", "idx_tsi_draft_status"):
            if idx in existing_idx:
                op.drop_index(idx, table_name="tackle_spec_import_draft")
        op.drop_table("tackle_spec_import_draft")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

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

    if _table_exists(inspector, "tackle_spec_import_log"):
        op.create_table(
            "tackle_spec_import_log__old",
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
            sa.Column("entry_id", sa.String(length=128), nullable=True),
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
            sa.CheckConstraint(_OLD_LOG_MODE_CONSTRAINT, name="ck_tsi_log_mode"),
            sa.CheckConstraint(_OLD_LOG_RESULT_CONSTRAINT, name="ck_tsi_log_result"),
        )

        op.execute(
            sa.text(
                "INSERT INTO tackle_spec_import_log__old (id, draft_id, category, mode, result, target_master_id, operator_user_id, entry_id, summary, error_detail, committed_at, created_at, updated_at) "
                "SELECT id, NULL, category, CASE mode WHEN 'discard' THEN 'hold' ELSE mode END, "
                "       CASE result WHEN 'applied' THEN 'success' WHEN 'discarded' THEN 'expired' ELSE 'failure' END, "
                "       target_master_id, operator_user_id, NULL, summary, error_detail, committed_at, created_at, updated_at "
                "  FROM tackle_spec_import_log"
            )
        )

        existing_idx = {idx["name"] for idx in inspector.get_indexes("tackle_spec_import_log")}
        for idx in ("idx_tsi_log_operator", "idx_tsi_log_category", "idx_tsi_log_created"):
            if idx in existing_idx:
                op.drop_index(idx, table_name="tackle_spec_import_log")

        op.drop_table("tackle_spec_import_log")
        op.rename_table("tackle_spec_import_log__old", "tackle_spec_import_log")

        op.create_index(
            "idx_tsi_log_created",
            "tackle_spec_import_log",
            ["created_at"],
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
        op.create_index(
            "idx_tsi_log_entry",
            "tackle_spec_import_log",
            ["entry_id"],
        )
