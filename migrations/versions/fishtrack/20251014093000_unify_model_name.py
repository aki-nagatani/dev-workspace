"""Unify rod/reel model identifiers under model_name."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "unify_model_name"
down_revision = "add_jan_code_to_tackle_models"
branch_labels = None
depends_on = None


def _has_column(inspector, table: str, column: str) -> bool:
    try:
        return any(col["name"] == column for col in inspector.get_columns(table))
    except Exception:  # pragma: no cover - defensive guard
        return False


def _has_constraint(inspector, table: str, constraint: str) -> bool:
    try:
        return any(
            entry.get("name") == constraint for entry in inspector.get_unique_constraints(table)
        )
    except Exception:  # pragma: no cover - defensive guard
        return False


def _drop_constraint(batch_op, name: str, constraint_type: str) -> None:
    try:
        batch_op.drop_constraint(name, type_=constraint_type)
    except Exception:  # pragma: no cover - constraint already absent
        pass


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if inspector.has_table("rod_model"):
        if not _has_column(inspector, "rod_model", "model_name"):
            op.add_column("rod_model", sa.Column("model_name", sa.String(length=128), nullable=True))
        fallback_columns = []
        if _has_column(inspector, "rod_model", "display_name"):
            fallback_columns.append("display_name")
        if _has_column(inspector, "rod_model", "model_code"):
            fallback_columns.append("model_code")

        if fallback_columns:
            coalesce_parts = ["NULLIF(TRIM(model_name), '')"]
            coalesce_parts.extend(f"NULLIF(TRIM({column}), '')" for column in fallback_columns)
            coalesce_parts.append("model_name")
            op.execute(
                f"""
                UPDATE rod_model
                   SET model_name = COALESCE(
                       {', '.join(coalesce_parts)}
                   )
                """
            )

        with op.batch_alter_table("rod_model") as batch_op:
            if _has_constraint(inspector, "rod_model", "uq_rod_model_series_code"):
                _drop_constraint(batch_op, "uq_rod_model_series_code", "unique")
            if _has_constraint(inspector, "rod_model", "uq_rod_model_series_name"):
                _drop_constraint(batch_op, "uq_rod_model_series_name", "unique")
            if _has_column(inspector, "rod_model", "model_code"):
                batch_op.drop_column("model_code")
            if _has_column(inspector, "rod_model", "display_name"):
                batch_op.drop_column("display_name")
            batch_op.alter_column(
                "model_name",
                existing_type=sa.String(length=128),
                nullable=False,
            )
            batch_op.create_unique_constraint(
                "uq_rod_model_series_name",
                ["series_id", "model_name"],
            )

    if inspector.has_table("reel_model"):
        if not _has_column(inspector, "reel_model", "model_name"):
            op.add_column("reel_model", sa.Column("model_name", sa.String(length=128), nullable=True))
        fallback_columns = []
        if _has_column(inspector, "reel_model", "display_name"):
            fallback_columns.append("display_name")
        if _has_column(inspector, "reel_model", "model_code"):
            fallback_columns.append("model_code")

        if fallback_columns:
            coalesce_parts = ["NULLIF(TRIM(model_name), '')"]
            coalesce_parts.extend(f"NULLIF(TRIM({column}), '')" for column in fallback_columns)
            coalesce_parts.append("model_name")
            op.execute(
                f"""
                UPDATE reel_model
                   SET model_name = COALESCE(
                       {', '.join(coalesce_parts)}
                   )
                """
            )

        with op.batch_alter_table("reel_model") as batch_op:
            if _has_constraint(inspector, "reel_model", "uq_reel_model_code_per_series"):
                _drop_constraint(batch_op, "uq_reel_model_code_per_series", "unique")
            if _has_constraint(inspector, "reel_model", "uq_reel_model_name_per_series"):
                _drop_constraint(batch_op, "uq_reel_model_name_per_series", "unique")
            if _has_column(inspector, "reel_model", "model_code"):
                batch_op.drop_column("model_code")
            if _has_column(inspector, "reel_model", "display_name"):
                batch_op.drop_column("display_name")
            batch_op.alter_column(
                "model_name",
                existing_type=sa.String(length=128),
                nullable=False,
            )
            batch_op.create_unique_constraint(
                "uq_reel_model_name_per_series",
                ["series_id", "model_name"],
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if inspector.has_table("rod_model"):
        with op.batch_alter_table("rod_model") as batch_op:
            _drop_constraint(batch_op, "uq_rod_model_series_name", "unique")
            batch_op.add_column(
                sa.Column("display_name", sa.String(length=128), nullable=True)
            )
            batch_op.add_column(
                sa.Column("model_code", sa.String(length=64), nullable=True)
            )
            batch_op.create_unique_constraint(
                "uq_rod_model_series_code",
                ["series_id", "model_code"],
            )
        op.execute(
            """
            UPDATE rod_model
               SET display_name = COALESCE(display_name, model_name),
                   model_code = COALESCE(model_code, model_name)
            """
        )

    if inspector.has_table("reel_model"):
        with op.batch_alter_table("reel_model") as batch_op:
            _drop_constraint(batch_op, "uq_reel_model_name_per_series", "unique")
            batch_op.add_column(
                sa.Column("display_name", sa.String(length=128), nullable=True)
            )
            batch_op.add_column(
                sa.Column("model_code", sa.String(length=64), nullable=True)
            )
            batch_op.create_unique_constraint(
                "uq_reel_model_code_per_series",
                ["series_id", "model_code"],
            )
        op.execute(
            """
            UPDATE reel_model
               SET display_name = COALESCE(display_name, model_name),
                   model_code = COALESCE(model_code, model_name)
            """
        )
