"""change BoxMember table to composite primary key

Revision ID: 20251225_change_boxmember_to_composite_primary_key
Revises: 20251225_change_contact_to_composite_primary_key
Create Date: 2025-12-25 00:15:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# ---- 識別子 ----
revision = "20251225_change_boxmember_to_composite_primary_key"
down_revision = "20251225_change_contact_to_composite_primary_key"
branch_labels = None
depends_on = None


def upgrade():
    """BoxMemberテーブルを複合主キーに変更（userId, gameId, nationalNo, createdAt）"""
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    # box_membersテーブルが存在するか確認
    inspector = inspect(bind)
    box_members_exists = "box_members" in inspector.get_table_names()
    
    if not box_members_exists:
        return  # テーブルが存在しない場合は何もしない

    if dialect_name == "sqlite":
        # SQLite: テーブル再作成
        try:
            op.drop_constraint("box_members_pkey", "box_members", type_="primary")
        except Exception:
            pass

        op.execute("""
            CREATE TABLE _alembic_tmp_box_members (
                userId INTEGER NOT NULL,
                gameId INTEGER NOT NULL DEFAULT 1,
                nationalNo INTEGER NOT NULL,
                createdAt DATETIME NOT NULL,
                PRIMARY KEY (userId, gameId, nationalNo, createdAt),
                FOREIGN KEY(userId) REFERENCES "User"(id) ON DELETE CASCADE,
                FOREIGN KEY(gameId) REFERENCES "GameTitle"(id),
                FOREIGN KEY(nationalNo) REFERENCES "Pokemon"(nationalNo) ON DELETE RESTRICT
            )
        """)
        op.execute("""
            INSERT INTO _alembic_tmp_box_members (
                userId, gameId, nationalNo, createdAt
            )
            SELECT userId, gameId, nationalNo, createdAt
            FROM box_members
        """)
        op.drop_table("box_members")
        op.rename_table("_alembic_tmp_box_members", "box_members")
        op.create_index("ix_box_user_game", "box_members", ["userId", "gameId"], unique=False)
        op.create_index("ix_box_user_game_nat_created", "box_members", ["userId", "gameId", "nationalNo", "createdAt"], unique=False)
        op.create_index("ix_box_members_userId", "box_members", ["userId"], unique=False)
        op.create_index("ix_box_members_nationalNo", "box_members", ["nationalNo"], unique=False)
    elif dialect_name == "postgresql":
        # PostgreSQL: ALTER TABLEで変更
        try:
            op.drop_constraint("box_members_pkey", "box_members", type_="primary")
        except Exception:
            pass
        # idカラムを削除
        op.drop_column("box_members", "id")
        # 複合主キーを設定
        op.create_primary_key("box_members_pkey", "box_members", ["userId", "gameId", "nationalNo", "createdAt"])
    else:
        # その他のデータベース: batch_alter_tableを使用
        with op.batch_alter_table("box_members", recreate="always") as batch_op:
            batch_op.drop_column("id")


def downgrade():
    """BoxMemberテーブルをid主キーに戻す"""
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "sqlite":
        # SQLite: テーブル再作成
        try:
            op.drop_constraint("box_members_pkey", "box_members", type_="primary")
        except Exception:
            pass

        op.execute("""
            CREATE TABLE _alembic_tmp_box_members (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                userId INTEGER NOT NULL,
                gameId INTEGER NOT NULL DEFAULT 1,
                nationalNo INTEGER NOT NULL,
                createdAt DATETIME NOT NULL,
                FOREIGN KEY(userId) REFERENCES "User"(id) ON DELETE CASCADE,
                FOREIGN KEY(gameId) REFERENCES "GameTitle"(id),
                FOREIGN KEY(nationalNo) REFERENCES "Pokemon"(nationalNo) ON DELETE RESTRICT
            )
        """)
        op.execute("""
            INSERT INTO _alembic_tmp_box_members (
                userId, gameId, nationalNo, createdAt
            )
            SELECT userId, gameId, nationalNo, createdAt
            FROM box_members
        """)
        op.drop_table("box_members")
        op.rename_table("_alembic_tmp_box_members", "box_members")
        op.create_index("ix_box_user_game", "box_members", ["userId", "gameId"], unique=False)
        op.create_index("ix_box_user_game_nat_created", "box_members", ["userId", "gameId", "nationalNo", "createdAt"], unique=False)
        op.create_index("ix_box_members_userId", "box_members", ["userId"], unique=False)
        op.create_index("ix_box_members_nationalNo", "box_members", ["nationalNo"], unique=False)
    elif dialect_name == "postgresql":
        # PostgreSQL: ALTER TABLEで変更
        try:
            op.drop_constraint("box_members_pkey", "box_members", type_="primary")
        except Exception:
            pass
        # idカラムを追加（シーケンスも作成）
        op.execute("""
            ALTER TABLE box_members
            ADD COLUMN id SERIAL
        """)
        # 既存データにIDを割り当て
        op.execute("""
            UPDATE box_members
            SET id = nextval('box_members_id_seq')
        """)
        # idをNOT NULLに設定
        op.alter_column("box_members", "id", nullable=False)
        # idを主キーに設定
        op.create_primary_key("box_members_pkey", "box_members", ["id"])
    else:
        # その他のデータベース: batch_alter_tableを使用
        with op.batch_alter_table("box_members", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("id", sa.Integer(), autoincrement=True, nullable=False))
            batch_op.create_primary_key("box_members_pkey", ["id"])

