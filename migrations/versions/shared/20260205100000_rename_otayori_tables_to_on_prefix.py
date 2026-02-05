"""rename otayori-navi tables to on_ prefix

既存DBの families / users / family_invites / documents を
on_families / on_users / on_family_invites / on_documents にリネームする。
新規環境で既に on_* が存在する場合はスキップする。

Revision ID: 20260205100000
Revises: 20260204001210
Create Date: 2026-02-05 10:00:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260205100000"
down_revision = "20260204001210"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return inspector.has_table(table_name)


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        return False
    return column_name in [c["name"] for c in inspector.get_columns(table_name)]


def upgrade() -> None:
    # 既に on_* がある（新規環境で models が先に create_all した等）なら何もしない
    if _has_table("on_families"):
        return

    # 旧テーブルが無い（未適用のDB）なら何もしない
    if not _has_table("families"):
        return

    # 依存順: families → users → family_invites → documents
    op.execute(sa.text("ALTER TABLE families RENAME TO on_families"))
    op.execute(sa.text("ALTER TABLE users RENAME TO on_users"))

    # 初回マイグレーション(20260204001210)に無かった configured_children を追加
    if not _has_column("on_families", "configured_children"):
        op.add_column(
            "on_families",
            sa.Column(
                "configured_children",
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
        )
    op.execute(sa.text("ALTER TABLE family_invites RENAME TO on_family_invites"))
    op.execute(sa.text("ALTER TABLE documents RENAME TO on_documents"))

    # インデックス・UNIQUE 制約名はそのまま（DB 内部名の違いで失敗するため省略。アプリはテーブル名のみ参照）


def downgrade() -> None:
    if _has_table("families"):
        return
    if not _has_table("on_families"):
        return

    # configured_children を削除（20260204001210 の状態に戻す）
    if _has_column("on_families", "configured_children"):
        op.drop_column("on_families", "configured_children")

    # テーブル名を元に戻す（依存の逆順）
    op.execute(sa.text("ALTER TABLE on_documents RENAME TO documents"))
    op.execute(sa.text("ALTER TABLE on_family_invites RENAME TO family_invites"))
    op.execute(sa.text("ALTER TABLE on_users RENAME TO users"))
    op.execute(sa.text("ALTER TABLE on_families RENAME TO families"))
