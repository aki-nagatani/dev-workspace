"""Ensure reel_model.list_price column exists"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "7ef0f2f6a924"
down_revision = "5c9f4e1cfa0a"
branch_labels = None
depends_on = None


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    try:
        return any(col["name"] == column_name for col in inspector.get_columns(table_name))
    except Exception:  # pragma: no cover
        return False


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    if inspector.has_table("reel_model") and not _has_column(inspector, "reel_model", "list_price"):
        op.add_column("reel_model", sa.Column("list_price", sa.Integer(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    if inspector.has_table("reel_model") and _has_column(inspector, "reel_model", "list_price"):
        op.drop_column("reel_model", "list_price")
