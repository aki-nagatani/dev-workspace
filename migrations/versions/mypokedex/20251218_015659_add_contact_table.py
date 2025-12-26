"""create Contact table via migration"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_contact_table"
down_revision = "20250926160000_add_evolution_fk_constraints"
branch_labels = None
depends_on = None


def _has_table(conn, table_name: str) -> bool:
    inspector = sa.inspect(conn)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    conn = op.get_bind()
    if _has_table(conn, "Contact"):
        return

    op.create_table(
        "Contact",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("userId", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("screenName", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("createdAt", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updatedAt", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["userId"], ["User.id"], ondelete="CASCADE"),
    )
    with op.batch_alter_table("Contact") as batch:
        batch.create_index("ix_contact_user_id", ["userId"])
        batch.create_index("ix_contact_created_at", ["createdAt"])


def downgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn, "Contact"):
        return
    op.drop_table("Contact")

