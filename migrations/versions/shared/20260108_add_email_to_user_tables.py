"""Add email column to User and fishtrack_user tables

Revision ID: 20260108_add_email_to_user_tables
Revises: 20260107143030
Create Date: 2026-01-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260108_add_email"
down_revision = "20260107143030"
branch_labels = None
depends_on = None


def upgrade():
    """Userテーブルとfishtrack_userテーブルにemailカラムを追加し、usernameの値をコピー"""
    
    # ===== MyPokedex Userテーブル =====
    # Step 1: emailカラムを追加（NULL許可）
    op.add_column("User", sa.Column("email", sa.String(255), nullable=True))
    
    # Step 2: usernameの値をemailにコピー（既にメールアドレスが入っている）
    op.execute("UPDATE \"User\" SET email = username")
    
    # Step 3: emailをNOT NULLに変更
    op.alter_column("User", "email", nullable=False)
    
    # Step 4: ユニーク制約をemailに変更
    # 既存のuxUserName制約を削除
    op.drop_constraint("uxUserName", "User", type_="unique")
    # emailにユニーク制約を追加（PostgreSQLでは自動的にインデックスが作成される）
    op.create_unique_constraint("ix_user_email", "User", ["email"])
    
    # ===== FishTrack fishtrack_userテーブル =====
    # Step 1: emailカラムを追加（NULL許可）
    op.add_column("fishtrack_user", sa.Column("email", sa.String(255), nullable=True))
    
    # Step 2: usernameの値をemailにコピー（既にメールアドレスが入っている）
    op.execute("UPDATE fishtrack_user SET email = username")
    
    # Step 3: emailをNOT NULLに変更
    op.alter_column("fishtrack_user", "email", nullable=False)
    
    # Step 4: ユニーク制約をemailに変更
    # 既存のix_fishtrack_user_usernameユニークインデックスを削除
    # （PostgreSQLではユニークインデックスとユニーク制約は別物だが、
    # この場合はインデックスのみが存在するため、drop_indexのみで削除）
    op.drop_index("ix_fishtrack_user_username", table_name="fishtrack_user")
    # emailにユニーク制約を追加（PostgreSQLでは自動的にインデックスが作成される）
    op.create_unique_constraint("ix_fishtrack_user_email", "fishtrack_user", ["email"])


def downgrade():
    """emailカラムを削除し、usernameのユニーク制約を復元"""
    
    # ===== FishTrack fishtrack_userテーブル =====
    # ユニーク制約を削除（PostgreSQLでは自動的にインデックスも削除される）
    op.drop_constraint("ix_fishtrack_user_email", "fishtrack_user", type_="unique")
    
    # usernameのユニークインデックスを復元
    op.create_index("ix_fishtrack_user_username", "fishtrack_user", ["username"], unique=True)
    
    # emailカラムを削除
    op.drop_column("fishtrack_user", "email")
    
    # ===== MyPokedex Userテーブル =====
    # ユニーク制約を削除（PostgreSQLでは自動的にインデックスも削除される）
    op.drop_constraint("ix_user_email", "User", type_="unique")
    
    # usernameのユニーク制約を復元
    op.create_unique_constraint("uxUserName", "User", ["username"])
    
    # emailカラムを削除
    op.drop_column("User", "email")

