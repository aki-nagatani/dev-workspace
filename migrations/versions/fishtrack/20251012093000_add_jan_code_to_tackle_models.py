"""Add jan_code columns to rod_model and reel_model"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "add_jan_code_to_tackle_models"
down_revision = "bf1a5ad8f4cd"
branch_labels = None
depends_on = None


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    try:
        return any(col["name"] == column_name for col in inspector.get_columns(table_name))
    except Exception:  # pragma: no cover - defensive fallback
        return False


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    if inspector.has_table("rod_model") and not _has_column(inspector, "rod_model", "jan_code"):
        op.add_column("rod_model", sa.Column("jan_code", sa.String(length=16), nullable=True))
    if inspector.has_table("reel_model") and not _has_column(inspector, "reel_model", "jan_code"):
        op.add_column("reel_model", sa.Column("jan_code", sa.String(length=16), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    if inspector.has_table("rod_model") and _has_column(inspector, "rod_model", "jan_code"):
        op.drop_column("rod_model", "jan_code")
    if inspector.has_table("reel_model") and _has_column(inspector, "reel_model", "jan_code"):
        op.drop_column("reel_model", "jan_code")
