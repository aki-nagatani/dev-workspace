"""Remove username column from User and fishtrack_user tables

Revision ID: 20260108083830_remove_username_from_user_tables
Revises: 20260108_add_email
Create Date: 2026-01-08 08:38:30
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260108083830_remove_username"
down_revision = "20260108_add_email"
branch_labels = None
depends_on = None


def upgrade():
    """Userテーブルとfishtrack_userテーブルからusernameカラムを削除"""
    
    # ===== FishTrack fishtrack_userテーブル =====
    # usernameカラムを削除（既にユニークインデックスは削除済み）
    op.drop_column("fishtrack_user", "username")
    
    # ===== MyPokedex Userテーブル =====
    # usernameカラムを削除（既にユニーク制約は削除済み）
    op.drop_column("User", "username")


def downgrade():
    """usernameカラムを復元（email対応前の状態に戻す）"""
    
    # ===== MyPokedex Userテーブル =====
    # usernameカラムを追加（NULL許可）
    op.add_column("User", sa.Column("username", sa.String(50), nullable=True))
    
    # emailの値をusernameにコピー（ダウングレード時はemailからusernameへ）
    op.execute("UPDATE \"User\" SET username = email")
    
    # usernameをNOT NULLに変更
    op.alter_column("User", "username", nullable=False)
    
    # usernameのユニーク制約を復元
    op.create_unique_constraint("uxUserName", "User", ["username"])
    
    # ===== FishTrack fishtrack_userテーブル =====
    # usernameカラムを追加（NULL許可）
    op.add_column("fishtrack_user", sa.Column("username", sa.String(64), nullable=True))
    
    # emailの値をusernameにコピー（ダウングレード時はemailからusernameへ）
    op.execute("UPDATE fishtrack_user SET username = email")
    
    # usernameをNOT NULLに変更
    op.alter_column("fishtrack_user", "username", nullable=False)
    
    # usernameのユニークインデックスを復元
    op.create_index("ix_fishtrack_user_username", "fishtrack_user", ["username"], unique=True)

