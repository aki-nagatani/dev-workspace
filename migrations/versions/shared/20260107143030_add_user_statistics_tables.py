"""add user statistics tables and last_login_at fields

Revision ID: 20260107143030
Revises: 20260106_add_za_dimension
Create Date: 2026-01-07 14:30:30
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260107143030"
down_revision = "20260106_add_za_dimension"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    dialect_name = conn.dialect.name

    # 1. MyPokedex Userテーブルにcreated_atとlast_login_atを追加
    if dialect_name == "sqlite":
        with op.batch_alter_table("User", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now())
            )
            batch_op.add_column(
                sa.Column("last_login_at", sa.DateTime(), nullable=True)
            )
            batch_op.create_index("ix_user_created_at", ["created_at"], unique=False)
            batch_op.create_index("ix_user_last_login_at", ["last_login_at"], unique=False)
    else:
        # PostgreSQL
        op.add_column("User", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
        op.add_column("User", sa.Column("last_login_at", sa.DateTime(), nullable=True))
        op.create_index("ix_user_created_at", "User", ["created_at"], unique=False)
        op.create_index("ix_user_last_login_at", "User", ["last_login_at"], unique=False)

    # 2. FishTrack fishtrack_userテーブルにlast_login_atを追加（created_atは既存）
    if dialect_name == "sqlite":
        with op.batch_alter_table("fishtrack_user", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("last_login_at", sa.DateTime(), nullable=True)
            )
            batch_op.create_index("ix_fishtrack_user_last_login_at", ["last_login_at"], unique=False)
    else:
        # PostgreSQL
        op.add_column("fishtrack_user", sa.Column("last_login_at", sa.DateTime(), nullable=True))
        op.create_index("ix_fishtrack_user_last_login_at", "fishtrack_user", ["last_login_at"], unique=False)

    # 3. user_statistics_dailyテーブルを作成（MyPokedexとFishTrackで共有）
    op.create_table(
        "user_statistics_daily",
        sa.Column("service_name", sa.String(length=20), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("new_user_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("service_name", "date"),
        sa.CheckConstraint("new_user_count >= 0", name="check_new_user_count_non_negative"),
        sa.CheckConstraint("service_name IN ('mypokedex', 'fishtrack')", name="check_service_name_valid"),
    )
    op.create_index("ix_user_stats_daily_service_date", "user_statistics_daily", ["service_name", "date"], unique=False)

    # 4. user_statistics_weeklyテーブルを作成（MyPokedexとFishTrackで共有）
    op.create_table(
        "user_statistics_weekly",
        sa.Column("service_name", sa.String(length=20), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("active_user_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("service_name", "week_start"),
        sa.CheckConstraint("active_user_count >= 0", name="check_active_user_count_non_negative"),
        sa.CheckConstraint("service_name IN ('mypokedex', 'fishtrack')", name="check_service_name_valid"),
    )
    op.create_index("ix_user_stats_weekly_service_week", "user_statistics_weekly", ["service_name", "week_start"], unique=False)


def downgrade():
    conn = op.get_bind()
    dialect_name = conn.dialect.name

    # 4. user_statistics_weeklyテーブルを削除
    op.drop_index("ix_user_stats_weekly_service_week", table_name="user_statistics_weekly")
    op.drop_table("user_statistics_weekly")

    # 3. user_statistics_dailyテーブルを削除
    op.drop_index("ix_user_stats_daily_service_date", table_name="user_statistics_daily")
    op.drop_table("user_statistics_daily")

    # 2. FishTrack fishtrack_userテーブルからlast_login_atを削除
    if dialect_name == "sqlite":
        with op.batch_alter_table("fishtrack_user", schema=None) as batch_op:
            batch_op.drop_index("ix_fishtrack_user_last_login_at")
            batch_op.drop_column("last_login_at")
    else:
        # PostgreSQL
        op.drop_index("ix_fishtrack_user_last_login_at", table_name="fishtrack_user")
        op.drop_column("fishtrack_user", "last_login_at")

    # 1. MyPokedex Userテーブルからcreated_atとlast_login_atを削除
    if dialect_name == "sqlite":
        with op.batch_alter_table("User", schema=None) as batch_op:
            batch_op.drop_index("ix_user_last_login_at")
            batch_op.drop_index("ix_user_created_at")
            batch_op.drop_column("last_login_at")
            batch_op.drop_column("created_at")
    else:
        # PostgreSQL
        op.drop_index("ix_user_last_login_at", table_name="User")
        op.drop_index("ix_user_created_at", table_name="User")
        op.drop_column("User", "last_login_at")
        op.drop_column("User", "created_at")

