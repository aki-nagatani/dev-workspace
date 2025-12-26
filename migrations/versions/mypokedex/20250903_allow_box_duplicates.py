"""allow duplicates in BoxMember: drop UNIQUE(userId,nationalNo) and add composite index

Revision ID: 20250903_allow_box_duplicates
Revises: c4c6751c149f
Create Date: 2025-09-03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250903_allow_box_duplicates"
down_revision = "c4c6751c149f"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # --- Drop UNIQUE constraint if present (SQLite requires batch mode) ---
    unique_names = {u["name"] for u in inspector.get_unique_constraints("box_members")}
    if "uq_box_user_poke" in unique_names:
        with op.batch_alter_table("box_members") as batch_op:
            batch_op.drop_constraint("uq_box_user_poke", type_="unique")

    # Some projects created a unique INDEX instead of a table constraint—drop it if exists
    index_names = {i["name"] for i in inspector.get_indexes("box_members")}
    if "uq_box_user_poke" in index_names:
        op.drop_index("uq_box_user_poke", table_name="box_members")

    # --- Add non-unique composite index for performance ---
    index_names = {i["name"] for i in inspector.get_indexes("box_members")}
    if "ix_box_user_poke" not in index_names:
        op.create_index(
            "ix_box_user_poke",
            "box_members",
            ["userId", "nationalNo"],
            unique=False,
        )


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # --- Drop non-unique index if present ---
    index_names = {i["name"] for i in inspector.get_indexes("box_members")}
    if "ix_box_user_poke" in index_names:
        op.drop_index("ix_box_user_poke", table_name="box_members")

    # --- Recreate UNIQUE(userId, nationalNo) if it previously existed ---
    with op.batch_alter_table("box_members") as batch_op:
        # This will re-add the uniqueness guarantee
        batch_op.create_unique_constraint(
            "uq_box_user_poke", ["userId", "nationalNo"]
        )
"""allow duplicates in BoxMember: drop UNIQUE(userId,nationalNo) and add composite index

Revision ID: 20250903_allow_box_duplicates
Revises: c4c6751c149f
Create Date: 2025-09-03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250903_allow_box_duplicates"
down_revision = "c4c6751c149f"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_name = "box_members"

    # テーブル未存在なら何もしない（初期化順序の違いで落ちるのを防止）
    if not inspector.has_table(table_name):
        return

    # 既存 UNIQUE 制約名の探索
    unique_names = {u["name"] for u in inspector.get_unique_constraints(table_name)}

    # SQLite で安全に UNIQUE を外すため batch モードを使用（常に再作成）
    with op.batch_alter_table(table_name, recreate="always") as batch_op:
        if "uq_box_user_poke" in unique_names:
            batch_op.drop_constraint("uq_box_user_poke", type_="unique")

    # UNIQUE インデックスとして作られていた可能性にも対応
    index_names = {i["name"] for i in inspector.get_indexes(table_name)}
    if "uq_box_user_poke" in index_names:
        op.drop_index("uq_box_user_poke", table_name=table_name)

    # 非 UNIQUE 複合インデックスを付与（存在しなければ）
    index_names = {i["name"] for i in inspector.get_indexes(table_name)}
    if "ix_box_user_poke" not in index_names:
        op.create_index(
            "ix_box_user_poke",
            table_name,
            ["userId", "nationalNo"],
            unique=False,
        )


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_name = "box_members"

    if not inspector.has_table(table_name):
        return

    # 非 UNIQUE インデックスを削除
    index_names = {i["name"] for i in inspector.get_indexes(table_name)}
    if "ix_box_user_poke" in index_names:
        op.drop_index("ix_box_user_poke", table_name=table_name)

    # UNIQUE 制約を復元
    with op.batch_alter_table(table_name, recreate="always") as batch_op:
        batch_op.create_unique_constraint(
            "uq_box_user_poke", ["userId", "nationalNo"]
        )