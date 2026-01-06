"""add ZA_DIMENSION dex type

Revision ID: 20260106_add_za_dimension
Revises: 20260106_isle_armor_crown
Create Date: 2026-01-06
"""
from alembic import op
import sqlalchemy as sa


# ---- 識別子 ----
revision = "20260106_add_za_dimension"
down_revision = "20260106_isle_armor_crown"
branch_labels = None
depends_on = None


# 旧: NATIONAL / PALDEA / BLUEBERRY / KITAKAMI / HISUI / GALAR / ISLE_OF_ARMOR / CROWN_TUNDRA / ZA
old_enum = sa.Enum(
    "NATIONAL", "PALDEA", "BLUEBERRY", "KITAKAMI", "HISUI", "GALAR", "ISLE_OF_ARMOR", "CROWN_TUNDRA", "ZA",
    name="dextype",
    native_enum=False,
    validate_strings=True,
)

# 新: NATIONAL / PALDEA / BLUEBERRY / KITAKAMI / HISUI / GALAR / ISLE_OF_ARMOR / CROWN_TUNDRA / ZA / ZA_DIMENSION
new_enum = sa.Enum(
    "NATIONAL", "PALDEA", "BLUEBERRY", "KITAKAMI", "HISUI", "GALAR", "ISLE_OF_ARMOR", "CROWN_TUNDRA", "ZA", "ZA_DIMENSION",
    name="dextype",
    native_enum=False,
    validate_strings=True,
)


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    dialect_name = conn.dialect.name

    # DexType Enumの拡張（ZA_DIMENSION追加）
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

    # DexType Enumの縮小（ZA_DIMENSIONを削除）
    # ZA_DIMENSION を持つデータがあるとダウングレード不可
    # 安全のため存在チェック＆警告
    res = bind.execute(sa.text("""
        SELECT COUNT(*) FROM Regist
        WHERE dexType = 'ZA_DIMENSION'
    """)).scalar()
    if res and int(res) > 0:
        raise RuntimeError(
            "Cannot downgrade: Regist has rows with dexType ZA_DIMENSION."
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

