"""change Contact table to composite primary key

Revision ID: 20251225_change_contact_to_composite_primary_key
Revises: 20251224_change_tables_to_composite_primary_keys
Create Date: 2025-12-25 00:04:41
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# ---- 識別子 ----
revision = "20251225_change_contact_to_composite_primary_key"
down_revision = "20251224_change_tables_to_composite_primary_keys"
branch_labels = None
depends_on = None


def upgrade():
    """Contactテーブルを複合主キーに変更（userId, createdAt）"""
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    # Contactテーブルが存在するか確認
    inspector = inspect(bind)
    contact_exists = "Contact" in inspector.get_table_names()
    
    if not contact_exists:
        return  # テーブルが存在しない場合は何もしない

    if dialect_name == "sqlite":
        # SQLite: テーブル再作成
        try:
            op.drop_constraint("Contact_pkey", "Contact", type_="primary")
        except Exception:
            pass

        op.execute("""
            CREATE TABLE _alembic_tmp_Contact (
                userId INTEGER NOT NULL,
                createdAt DATETIME NOT NULL,
                category VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                email VARCHAR(255),
                screenName VARCHAR(50),
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                updatedAt DATETIME,
                PRIMARY KEY (userId, createdAt),
                FOREIGN KEY(userId) REFERENCES "User"(id) ON DELETE CASCADE
            )
        """)
        op.execute("""
            INSERT INTO _alembic_tmp_Contact (
                userId, createdAt, category, message, email, screenName, status, updatedAt
            )
            SELECT userId, createdAt, category, message, email, screenName, status, updatedAt
            FROM Contact
        """)
        op.drop_table("Contact")
        op.rename_table("_alembic_tmp_Contact", "Contact")
        op.create_index("ix_contact_user_id", "Contact", ["userId"], unique=False)
        op.create_index("ix_contact_created_at", "Contact", ["createdAt"], unique=False)
    elif dialect_name == "postgresql":
        # PostgreSQL: ALTER TABLEで変更
        try:
            op.drop_constraint("Contact_pkey", "Contact", type_="primary")
        except Exception:
            pass
        # idカラムを削除
        op.drop_column("Contact", "id")
        # 複合主キーを設定
        op.create_primary_key("Contact_pkey", "Contact", ["userId", "createdAt"])
    else:
        # その他のデータベース: batch_alter_tableを使用
        with op.batch_alter_table("Contact", recreate="always") as batch_op:
            batch_op.drop_column("id")


def downgrade():
    """Contactテーブルをid主キーに戻す"""
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "sqlite":
        # SQLite: テーブル再作成
        try:
            op.drop_constraint("Contact_pkey", "Contact", type_="primary")
        except Exception:
            pass

        op.execute("""
            CREATE TABLE _alembic_tmp_Contact (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                userId INTEGER NOT NULL,
                createdAt DATETIME NOT NULL,
                category VARCHAR(20) NOT NULL,
                message TEXT NOT NULL,
                email VARCHAR(255),
                screenName VARCHAR(50),
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                updatedAt DATETIME,
                FOREIGN KEY(userId) REFERENCES "User"(id) ON DELETE CASCADE
            )
        """)
        op.execute("""
            INSERT INTO _alembic_tmp_Contact (
                userId, createdAt, category, message, email, screenName, status, updatedAt
            )
            SELECT userId, createdAt, category, message, email, screenName, status, updatedAt
            FROM Contact
        """)
        op.drop_table("Contact")
        op.rename_table("_alembic_tmp_Contact", "Contact")
        op.create_index("ix_contact_user_id", "Contact", ["userId"], unique=False)
        op.create_index("ix_contact_created_at", "Contact", ["createdAt"], unique=False)
    elif dialect_name == "postgresql":
        # PostgreSQL: ALTER TABLEで変更
        try:
            op.drop_constraint("Contact_pkey", "Contact", type_="primary")
        except Exception:
            pass
        # idカラムを追加（シーケンスも作成）
        op.execute("""
            ALTER TABLE "Contact"
            ADD COLUMN id SERIAL
        """)
        # 既存データにIDを割り当て
        op.execute("""
            UPDATE "Contact"
            SET id = nextval('"Contact_id_seq"')
        """)
        # idをNOT NULLに設定
        op.alter_column("Contact", "id", nullable=False)
        # idを主キーに設定
        op.create_primary_key("Contact_pkey", "Contact", ["id"])
    else:
        # その他のデータベース: batch_alter_tableを使用
        with op.batch_alter_table("Contact", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("id", sa.Integer(), autoincrement=True, nullable=False))
            batch_op.create_primary_key("Contact_pkey", ["id"])

