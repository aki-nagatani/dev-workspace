
"""Add is_admin flag to FishTrackUser"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f3b865cea1d0"
down_revision = "9f5e0b9f8a4c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "fishtrack_user" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("fishtrack_user")}
    if "is_admin" in columns:
        return
    op.add_column(
        "fishtrack_user",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
    )
    op.execute("UPDATE fishtrack_user SET is_admin = FALSE WHERE is_admin IS NULL")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "fishtrack_user" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("fishtrack_user")}
    if "is_admin" not in columns:
        return
    op.drop_column("fishtrack_user", "is_admin")
