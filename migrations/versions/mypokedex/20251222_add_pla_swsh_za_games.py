"""add PLA, SwSh, Z-A games and expand DexType to include HISUI, GALAR, ZA

Revision ID: 20251222_add_pla_swsh_za_games
Revises: 20251220_add_box_party_user_fk_constraints
Create Date: 2025-12-22
"""
from alembic import op
import sqlalchemy as sa


# ---- 識別子 ----
revision = "20251222_add_pla_swsh_za_games"
down_revision = "20251220_add_box_party_user_fk_constraints"
branch_labels = None
depends_on = None


# 旧: NATIONAL / PALDEA / BLUEBERRY / KITAKAMI
old_enum = sa.Enum(
    "NATIONAL", "PALDEA", "BLUEBERRY", "KITAKAMI",
    name="dextype",
    native_enum=False,
    validate_strings=True,
)

# 新: NATIONAL / PALDEA / BLUEBERRY / KITAKAMI / HISUI / GALAR / ZA
new_enum = sa.Enum(
    "NATIONAL", "PALDEA", "BLUEBERRY", "KITAKAMI", "HISUI", "GALAR", "ZA",
    name="dextype",
    native_enum=False,
    validate_strings=True,
)


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    dialect_name = conn.dialect.name

    # 1) GameTitle テーブルへの追加（PLA, Z-A）
    # SwShは既に登録済み（id=2）のため追加不要
    if dialect_name == 'sqlite':
        op.execute(
            "INSERT OR IGNORE INTO GameTitle (id, key, nameJa, sortOrder) "
            "VALUES (3, 'PLA', 'レジェンズ アルセウス', 3)"
        )
        op.execute(
            "INSERT OR IGNORE INTO GameTitle (id, key, nameJa, sortOrder) "
            "VALUES (4, 'Z-A', 'レジェンズ Z-A', 4)"
        )
    elif dialect_name == 'postgresql':
        op.execute(
            """
            INSERT INTO "GameTitle" ("id", "key", "nameJa", "sortOrder") 
            VALUES (3, 'PLA', 'レジェンズ アルセウス', 3)
            ON CONFLICT ("key") DO NOTHING
            """
        )
        op.execute(
            """
            INSERT INTO "GameTitle" ("id", "key", "nameJa", "sortOrder") 
            VALUES (4, 'Z-A', 'レジェンズ Z-A', 4)
            ON CONFLICT ("key") DO NOTHING
            """
        )
    else:
        # その他のデータベース用のフォールバック
        try:
            op.execute(
                "INSERT INTO GameTitle (id, key, nameJa, sortOrder) "
                "VALUES (3, 'PLA', 'レジェンズ アルセウス', 3)"
            )
        except Exception:
            pass
        try:
            op.execute(
                "INSERT INTO GameTitle (id, key, nameJa, sortOrder) "
                "VALUES (4, 'Z-A', 'レジェンズ Z-A', 4)"
            )
        except Exception:
            pass

    # 2) DexType Enumの拡張（HISUI, GALAR, ZA追加）
    if dialect_name == "sqlite":
        # SQLite は列の CHECK 更新が ALTER でできないため、batch_alter_table で再作成
        with op.batch_alter_table("Regist", recreate="always") as batch_op:
            batch_op.alter_column(
                "dexType",
                existing_type=old_enum,
                type_=new_enum,
                existing_nullable=False,
            )
    else:
        # 非SQLite（MySQL/PostgreSQL）でも native_enum=False のため CHECK 再生成が必要
        # 互換的に batch_alter_table で再作成してしまうのが安全
        with op.batch_alter_table("Regist", recreate="always") as batch_op:
            batch_op.alter_column(
                "dexType",
                existing_type=old_enum,
                type_=new_enum,
                existing_nullable=False,
            )


def downgrade():
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    # 1) DexType Enumの縮小（HISUI, GALAR, ZAを削除）
    # HISUI / GALAR / ZA を持つデータがあるとダウングレード不可
    # 安全のため存在チェック＆警告
    res = bind.execute(sa.text("""
        SELECT COUNT(*) FROM Regist
        WHERE dexType IN ('HISUI','GALAR','ZA')
    """)).scalar()
    if res and int(res) > 0:
        raise RuntimeError(
            "Cannot downgrade: Regist has rows with dexType HISUI/GALAR/ZA."
        )

    if dialect_name == "sqlite":
        with op.batch_alter_table("Regist", recreate="always") as batch_op:
            batch_op.alter_column(
                "dexType",
                existing_type=new_enum,
                type_=old_enum,
                existing_nullable=False,
            )
    else:
        with op.batch_alter_table("Regist", recreate="always") as batch_op:
            batch_op.alter_column(
                "dexType",
                existing_type=new_enum,
                type_=old_enum,
                existing_nullable=False,
            )

    # 2) GameTitle テーブルから PLA, Z-A を削除
    # 外部キー制約があるため、関連データを先に削除する必要がある可能性がある
    # ただし、UserGameSetting の CASCADE により自動削除される想定
    if dialect_name == 'sqlite':
        op.execute("DELETE FROM GameTitle WHERE key IN ('PLA', 'Z-A')")
    elif dialect_name == 'postgresql':
        op.execute("DELETE FROM \"GameTitle\" WHERE \"key\" IN ('PLA', 'Z-A')")
    else:
        try:
            op.execute("DELETE FROM GameTitle WHERE key IN ('PLA', 'Z-A')")
        except Exception:
            pass

