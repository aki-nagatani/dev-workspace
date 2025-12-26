"""Add FishTrackUser table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b84f8d8f4ef1"
down_revision = "74387003a93b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "fishtrack_user" in inspector.get_table_names():
        return
    op.create_table(
        "fishtrack_user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "username",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("TRUE"),
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
        sa.UniqueConstraint("username", name="uq_fishtrack_user_username"),
    )
    op.create_index(
        "ix_fishtrack_user_username",
        "fishtrack_user",
        ["username"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "fishtrack_user" not in inspector.get_table_names():
        return
    existing_indexes = {idx["name"] for idx in inspector.get_indexes("fishtrack_user")}
    if "ix_fishtrack_user_username" in existing_indexes:
        op.drop_index("ix_fishtrack_user_username", table_name="fishtrack_user")
    op.drop_table("fishtrack_user")
