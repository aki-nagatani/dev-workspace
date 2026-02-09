"""drop otayori-navi tables from shared_db

Revision ID: 20260209150000
Revises: 20260120001103
Create Date: 2026-02-09 15:00:00.000000

1RDS 3DB Phase 1 完了後、おたよりナビは otayori_navi DB に移行済み。
shared_db に残っている旧 on_* テーブルおよび otayori_navi_alembic_version を削除する。

実行タイミング: おたよりナビの接続切替・動作確認完了後、一定期間問題がないことを確認した後。
"""
from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "20260209150000"
down_revision = "20260120001103"
branch_labels = None
depends_on = None

# 削除対象: おたよりナビ用テーブル（otayori_navi DB へ移行済み）
# 外部キー依存を考慮し、子テーブルから順に DROP
OTAYORI_TABLES = [
    "on_documents",       # ドキュメント（on_families, on_users, on_children を参照）
    "on_family_invites",  # 招待コード（on_families を参照）
    "on_children",        # 子ども（on_families を参照）
    "on_users",           # ユーザー（on_families を参照）
    "on_families",        # 世帯
    "otayori_navi_alembic_version",  # おたよりナビ用 alembic_version（存在する場合のみ）
]


def upgrade() -> None:
    """shared_db からおたよりナビ用テーブルを削除"""
    for table in OTAYORI_TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")


def downgrade() -> None:
    """ダウングレード不可

    削除したテーブルは otayori_navi DB に移行済みのため、
    shared_db への復元は行わない。ロールバックが必要な場合は
    otayori/db-url を shared_db に戻し、アプリを再起動すること。
    """
    raise NotImplementedError(
        "on_* テーブルの削除は不可逆です。"
        "ロールバックが必要な場合は Secrets Manager の otayori/db-url を shared_db に戻してください。"
    )
