"""create UserGameSetting table via migration"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20250924_add_user_game_setting"
down_revision = "20250920_remove_pokemon_paldeano"
branch_labels = None
depends_on = None


def _has_table(conn, table_name: str) -> bool:
    inspector = sa.inspect(conn)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    conn = op.get_bind()
    if _has_table(conn, "UserGameSetting"):
        inspector = sa.inspect(conn)
        existing_uniques = {uc["name"] for uc in inspector.get_unique_constraints("UserGameSetting")}
        if "uq_user_game_setting" not in existing_uniques:
            with op.batch_alter_table("UserGameSetting") as batch:
                batch.create_unique_constraint("uq_user_game_setting", ["userId", "gameId"])
        return

    op.create_table(
        "UserGameSetting",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("userId", sa.Integer(), nullable=False),
        sa.Column("gameId", sa.Integer(), nullable=False),
        sa.Column("isEnabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["userId"], ["User.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["gameId"], ["GameTitle.id"], ondelete="CASCADE"),
    )
    with op.batch_alter_table("UserGameSetting") as batch:
        batch.create_unique_constraint("uq_user_game_setting", ["userId", "gameId"])


def downgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn, "UserGameSetting"):
        return
    op.drop_table("UserGameSetting")
