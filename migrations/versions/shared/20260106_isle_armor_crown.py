"""add Isle of Armor and Crown Tundra dex types

Revision ID: 20260106_isle_armor_crown
Revises: rename_rod_holding_constraints
Create Date: 2026-01-06
"""
from alembic import op
import sqlalchemy as sa


# ---- 識別子 ----
revision = "20260106_isle_armor_crown"
down_revision = "rename_rod_holding_constraints"
branch_labels = None
depends_on = None


# 旧: NATIONAL / PALDEA / BLUEBERRY / KITAKAMI / HISUI / GALAR / ZA
old_enum = sa.Enum(
    "NATIONAL", "PALDEA", "BLUEBERRY", "KITAKAMI", "HISUI", "GALAR", "ZA",
    name="dextype",
    native_enum=False,
    validate_strings=True,
)

# 新: NATIONAL / PALDEA / BLUEBERRY / KITAKAMI / HISUI / GALAR / ISLE_OF_ARMOR / CROWN_TUNDRA / ZA
new_enum = sa.Enum(
    "NATIONAL", "PALDEA", "BLUEBERRY", "KITAKAMI", "HISUI", "GALAR", "ISLE_OF_ARMOR", "CROWN_TUNDRA", "ZA",
    name="dextype",
    native_enum=False,
    validate_strings=True,
)


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    dialect_name = conn.dialect.name

    # DexType Enumの拡張（ISLE_OF_ARMOR, CROWN_TUNDRA追加）
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

    # DexType Enumの縮小（ISLE_OF_ARMOR, CROWN_TUNDRAを削除）
    # ISLE_OF_ARMOR / CROWN_TUNDRA を持つデータがあるとダウングレード不可
    # 安全のため存在チェック＆警告
    res = bind.execute(sa.text("""
        SELECT COUNT(*) FROM Regist
        WHERE dexType IN ('ISLE_OF_ARMOR','CROWN_TUNDRA')
    """)).scalar()
    if res and int(res) > 0:
        raise RuntimeError(
            "Cannot downgrade: Regist has rows with dexType ISLE_OF_ARMOR/CROWN_TUNDRA."
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

