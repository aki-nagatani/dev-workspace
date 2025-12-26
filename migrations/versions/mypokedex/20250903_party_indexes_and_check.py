"""add PartyMember index (userId, nationalNo) and slot range check; drop legacy unique
Revision ID: 20250903_party_indexes_and_check
Revises: 20250903_allow_box_duplicates
Create Date: 2025-09-03
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250903_party_indexes_and_check"
down_revision = "20250903_allow_box_duplicates"
branch_labels = None
depends_on = None

# --- constants ---
TABLE = "party_members"
LEGACY_UNIQUE_CANDIDATES = {
    "uq_party_user_poke",                  # UNIQUE(userId, nationalNo)
    "party_members_userId_nationalNo_key", # auto-named in some envs
}
NEW_NONUNIQUE_INDEX = "ix_party_user_poke"  # (userId, nationalNo)
SLOT_CHECK_NAME = "ck_party_slot_range"     # keep original name for compatibility


def _has_table(inspector, table_name: str) -> bool:
    try:
        return inspector.has_table(table_name)
    except Exception:
        return False


def _has_column(inspector, table_name: str, col: str) -> bool:
    try:
        return any(c["name"] == col for c in inspector.get_columns(table_name))
    except Exception:
        return False


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # テーブル未作成の環境ではスキップ（初期導入順序の差異に対応）
    if not _has_table(inspector, TABLE):
        return

    # 1) 旧 UNIQUE(userId, nationalNo) を削除（存在するときのみ）
    uniq_names = {u["name"] for u in inspector.get_unique_constraints(TABLE)}
    with op.batch_alter_table(TABLE, recreate="always") as batch_op:
        for cand in LEGACY_UNIQUE_CANDIDATES:
            if cand in uniq_names:
                batch_op.drop_constraint(cand, type_="unique")
                break

    # UNIQUE インデックスとして作られていた可能性にも対応
    idx_names = {i["name"] for i in inspector.get_indexes(TABLE)}
    for cand in LEGACY_UNIQUE_CANDIDATES:
        if cand in idx_names:
            op.drop_index(cand, table_name=TABLE)
            break

    # 2) 非 UNIQUE 複合インデックス (userId, nationalNo) を作成（未作成なら）
    idx_names = {i["name"] for i in inspector.get_indexes(TABLE)}
    if NEW_NONUNIQUE_INDEX not in idx_names:
        op.create_index(NEW_NONUNIQUE_INDEX, TABLE, ["userId", "nationalNo"], unique=False)

    # 3) slot の範囲チェックを追加（列がある場合のみ）
    if _has_column(inspector, TABLE, "slot"):
        with op.batch_alter_table(TABLE, recreate="always") as batch_op:
            batch_op.create_check_constraint(SLOT_CHECK_NAME, "slot BETWEEN 1 AND 6")


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if not _has_table(inspector, TABLE):
        return

    # 1) slot チェックを削除（列がある場合のみ）
    if _has_column(inspector, TABLE, "slot"):
        with op.batch_alter_table(TABLE, recreate="always") as batch_op:
            try:
                batch_op.drop_constraint(SLOT_CHECK_NAME, type_="check")
            except Exception:
                # 無ければ無視
                pass

    # 2) 非 UNIQUE 複合インデックスを削除（存在時のみ）
    idx_names = {i["name"] for i in inspector.get_indexes(TABLE)}
    if NEW_NONUNIQUE_INDEX in idx_names:
        op.drop_index(NEW_NONUNIQUE_INDEX, table_name=TABLE)

    # 3) 旧 UNIQUE(userId, nationalNo) を復元
    with op.batch_alter_table(TABLE, recreate="always") as batch_op:
        batch_op.create_unique_constraint("uq_party_user_poke", ["userId", "nationalNo"])