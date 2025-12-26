"""expand Regist.dexType to include BLUEBERRY and KITAKAMI

Revision ID: 20250910_expand_dextype
Revises: 20250903_allow_box_duplicates
Create Date: 2025-09-10 00:00:00
"""
from alembic import op
import sqlalchemy as sa


# 直前のリビジョンIDに置き換えてください
revision = "20250910_expand_dextype"
down_revision = "20250903_allow_box_duplicates"
branch_labels = None
depends_on = None


# 旧: NATIONAL / PALDEA
old_enum = sa.Enum(
    "NATIONAL", "PALDEA",
    name="dextype",
    native_enum=False,
    validate_strings=True,
)

# 新: NATIONAL / PALDEA / BLUEBERRY / KITAKAMI
new_enum = sa.Enum(
    "NATIONAL", "PALDEA", "BLUEBERRY", "KITAKAMI",
    name="dextype",
    native_enum=False,
    validate_strings=True,
)


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
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
    # BLUEBERRY / KITAKAMI を持つデータがあるとダウングレード不可
    # 安全のため存在チェック＆警告
    res = bind.execute(sa.text("""
        SELECT COUNT(*) FROM Regist
        WHERE dexType IN ('BLUEBERRY','KITAKAMI')
    """)).scalar()
    if res and int(res) > 0:
        raise RuntimeError(
            "Cannot downgrade: Regist has rows with dexType BLUEBERRY/KITAKAMI."
        )

    if bind.dialect.name == "sqlite":
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