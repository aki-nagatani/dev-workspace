"""change Regist to composite primary key

Revision ID: 20251224_change_regist_to_composite_primary_key
Revises: 20251222_add_pla_swsh_za_games
Create Date: 2025-12-24 23:29:54
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite


# ---- 識別子 ----
revision = "20251224_change_regist_to_composite_primary_key"
down_revision = "20251222_add_pla_swsh_za_games"
branch_labels = None
depends_on = None


def upgrade():
    """Registテーブルを複合主キーに変更"""
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "sqlite":
        # SQLite: テーブル再作成が必要（手動で実行）
        # 1. 既存のUniqueConstraintを削除
        try:
            op.drop_constraint("uxRegistUnique", "Regist", type_="unique")
        except Exception:
            pass
        
        # 2. 既存の主キー制約を削除
        try:
            op.drop_constraint("Regist_pkey", "Regist", type_="primary")
        except Exception:
            pass
        
        # 3. 一時テーブルを作成（複合主キー付き）
        op.execute("""
            CREATE TABLE _alembic_tmp_Regist (
                userId INTEGER NOT NULL,
                nationalNo INTEGER NOT NULL,
                dexType VARCHAR NOT NULL,
                PRIMARY KEY (userId, nationalNo, dexType),
                CHECK ("userId" > 0),
                FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE,
                FOREIGN KEY (nationalNo) REFERENCES Pokemon(nationalNo) ON DELETE RESTRICT
            )
        """)
        
        # 4. データをコピー
        op.execute("""
            INSERT INTO _alembic_tmp_Regist (userId, nationalNo, dexType)
            SELECT userId, nationalNo, dexType FROM Regist
        """)
        
        # 5. 古いテーブルを削除
        op.drop_table("Regist")
        
        # 6. 一時テーブルをリネーム
        op.rename_table("_alembic_tmp_Regist", "Regist")
        
        # 7. インデックスを再作成
        op.create_index("ixRegistUserDex", "Regist", ["userId", "dexType"], unique=False)
        op.create_index("ixRegistNational", "Regist", ["nationalNo"], unique=False)
            
    elif dialect_name == "postgresql":
        # PostgreSQL: ALTER TABLEで直接変更可能
        
        # 1. 既存のUniqueConstraintを削除
        try:
            op.drop_constraint("uxRegistUnique", "Regist", type_="unique")
        except Exception:
            pass  # 制約が存在しない場合はスキップ
        
        # 2. 既存の主キー制約を削除
        try:
            op.drop_constraint("Regist_pkey", "Regist", type_="primary")
        except Exception:
            pass  # 制約が存在しない場合はスキップ
        
        # 3. idカラムを削除
        op.drop_column("Regist", "id")
        
        # 4. 複合主キーを追加
        op.create_primary_key(
            "Regist_pkey",
            "Regist",
            ["userId", "nationalNo", "dexType"]
        )
        
    else:
        # その他のDB: SQLiteと同様にテーブル再作成
        with op.batch_alter_table("Regist", recreate="always") as batch_op:
            try:
                batch_op.drop_constraint("uxRegistUnique", type_="unique")
            except Exception:
                pass
            batch_op.drop_column("id")


def downgrade():
    """Registテーブルを元の単一主キーに戻す"""
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == "sqlite":
        # SQLite: テーブル再作成が必要
        with op.batch_alter_table("Regist", recreate="always") as batch_op:
            # 複合主キーを削除（テーブル再作成時に自動的に削除される）
            # idカラムを追加
            batch_op.add_column(sa.Column("id", sa.Integer(), nullable=False))
            # 主キーをidに設定
            batch_op.create_primary_key("Regist_pkey", ["id"])
            # UniqueConstraintを追加
            batch_op.create_unique_constraint(
                "uxRegistUnique",
                ["userId", "nationalNo", "dexType"]
            )
            # idにautoincrementを設定（SQLiteではAUTOINCREMENTキーワードが必要）
            # ただし、batch_alter_tableでは直接設定できないため、
            # テーブル再作成時に自動的に設定される
            
    elif dialect_name == "postgresql":
        # PostgreSQL: ALTER TABLEで直接変更可能
        
        # 1. 既存の複合主キーを削除
        try:
            op.drop_constraint("Regist_pkey", "Regist", type_="primary")
        except Exception:
            pass
        
        # 2. idカラムを追加（シーケンスも作成）
        op.add_column("Regist", sa.Column("id", sa.Integer(), nullable=False))
        
        # 3. シーケンスを作成してidに設定
        op.execute("CREATE SEQUENCE IF NOT EXISTS \"Regist_id_seq\"")
        op.execute("ALTER TABLE \"Regist\" ALTER COLUMN \"id\" SET DEFAULT nextval('\"Regist_id_seq\"')")
        
        # 4. 既存データにIDを割り当て（ROW_NUMBERを使用）
        op.execute("""
            UPDATE "Regist"
            SET "id" = subquery.row_num
            FROM (
                SELECT 
                    "userId", "nationalNo", "dexType",
                    ROW_NUMBER() OVER (ORDER BY "userId", "nationalNo", "dexType") as row_num
                FROM "Regist"
            ) AS subquery
            WHERE "Regist"."userId" = subquery."userId"
              AND "Regist"."nationalNo" = subquery."nationalNo"
              AND "Regist"."dexType" = subquery."dexType"
        """)
        
        # 5. シーケンスを最大IDに設定
        op.execute("SELECT setval('\"Regist_id_seq\"', (SELECT MAX(\"id\") FROM \"Regist\"))")
        
        # 6. 主キーをidに設定
        op.create_primary_key("Regist_pkey", "Regist", ["id"])
        
        # 7. UniqueConstraintを追加
        op.create_unique_constraint(
            "uxRegistUnique",
            "Regist",
            ["userId", "nationalNo", "dexType"]
        )
        
    else:
        # その他のDB: SQLiteと同様にテーブル再作成
        with op.batch_alter_table("Regist", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("id", sa.Integer(), nullable=False))
            batch_op.create_primary_key("Regist_pkey", ["id"])
            batch_op.create_unique_constraint(
                "uxRegistUnique",
                ["userId", "nationalNo", "dexType"]
            )

