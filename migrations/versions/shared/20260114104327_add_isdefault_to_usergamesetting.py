"""add isDefault to UserGameSetting

Revision ID: 20260114104327
Revises: 
Create Date: 2026-01-14 10:43:27.000000

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260114104327'
down_revision = '20260108083830_remove_username'  # 最新のマイグレーション
branch_labels = None
depends_on = None


def upgrade() -> None:
    """UserGameSettingテーブルにisDefaultカラムを追加
    
    P1-4-T18: 初期表示ゲームタイトルの設定機能の実装に伴い、
    UserGameSettingテーブルにisDefaultカラムを追加します。
    このカラムは、ユーザーが初期表示するゲームタイトルを指定するために使用されます。
    """
    # SQLite 3.2.0以降ではALTER TABLE ADD COLUMNがサポートされている
    # PostgreSQLではBOOLEAN型のデフォルト値は'false'またはFALSEを使用する必要がある
    # SQLiteでは'0'または'false'の両方が有効
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        # PostgreSQLの場合
        op.add_column(
            'UserGameSetting',
            sa.Column('isDefault', sa.Boolean(), nullable=False, server_default=sa.text('false'))
        )
    else:
        # SQLiteの場合
        op.add_column(
            'UserGameSetting',
            sa.Column('isDefault', sa.Boolean(), nullable=False, server_default=sa.text('0'))
        )


def downgrade() -> None:
    """UserGameSettingテーブルからisDefaultカラムを削除
    
    SQLite 3.25.0以降ではALTER TABLE DROP COLUMNがサポートされているため、
    直接カラムを削除できます。
    """
    op.drop_column('UserGameSetting', 'isDefault')
