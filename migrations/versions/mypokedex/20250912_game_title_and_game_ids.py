"""add GameTitle and gameId to PartyMember/BoxMember (SV/SWSH split)

Revision ID: 20250912_game_title_and_game_ids
Revises: 20250912_add_dexentry_and_backfill
Create Date: 2025-09-12

SQLite 注意:
- 既存制約の置き換え・外部キー追加は batch_alter_table を使用
"""

from alembic import op
import sqlalchemy as sa


# ---- 識別子 ----
revision = "20250912_game_title_and_game_ids"
down_revision = "20250912_add_dexentry_and_backfill"

branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # 1) GameTitle テーブル新規作成（存在チェックして二重作成を回避）
    dialect_name = conn.dialect.name
    if dialect_name == 'sqlite':
        exists = conn.exec_driver_sql(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='GameTitle'"
        ).fetchone()
    elif dialect_name == 'postgresql':
        exists = conn.exec_driver_sql(
            """
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'GameTitle'
            """
        ).fetchone()
    else:
        exists = inspector.has_table("GameTitle")
        exists = (1,) if exists else None

    if not exists:
        op.create_table(
            "GameTitle",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("key", sa.String(16), nullable=False, unique=True),   # 'SV', 'SWSH'
            sa.Column("nameJa", sa.String(50), nullable=False),             # 表示名
            sa.Column("sortOrder", sa.Integer, nullable=False, server_default="1"),
        )

    # 初期データ投入（idempotent）
    if dialect_name == 'sqlite':
        op.execute(
            "INSERT OR IGNORE INTO GameTitle (id, key, nameJa, sortOrder) "
            "VALUES (1, 'SV', 'スカーレット・バイオレット', 1)"
        )
        op.execute(
            "INSERT OR IGNORE INTO GameTitle (id, key, nameJa, sortOrder) "
            "VALUES (2, 'SWSH', 'ソード・シールド', 2)"
        )
    elif dialect_name == 'postgresql':
        op.execute(
            """
            INSERT INTO "GameTitle" ("id", "key", "nameJa", "sortOrder") 
            VALUES (1, 'SV', 'スカーレット・バイオレット', 1)
            ON CONFLICT ("key") DO NOTHING
            """
        )
        op.execute(
            """
            INSERT INTO "GameTitle" ("id", "key", "nameJa", "sortOrder") 
            VALUES (2, 'SWSH', 'ソード・シールド', 2)
            ON CONFLICT ("key") DO NOTHING
            """
        )
    else:
        # その他のデータベース用のフォールバック
        try:
            op.execute(
                "INSERT INTO GameTitle (id, key, nameJa, sortOrder) "
                "VALUES (1, 'SV', 'スカーレット・バイオレット', 1)"
            )
        except Exception:
            pass
        try:
            op.execute(
                "INSERT INTO GameTitle (id, key, nameJa, sortOrder) "
                "VALUES (2, 'SWSH', 'ソード・シールド', 2)"
            )
        except Exception:
            pass

    # 2) BoxMember に gameId を追加（NULL で追加 → 既存行を 1=SV に UPDATE → NOT NULL/FK/Index 付与）
    # テーブル未存在ならスキップ（初期化順序の違いで落ちるのを防止）
    if inspector.has_table("box_members"):
        op.execute("DROP INDEX IF EXISTS ix_box_user_poke")

        with op.batch_alter_table("box_members") as b:
            # まず NULL 可で追加（SQLite の batch 移行時に NOT NULL だとコピーで失敗するため）
            b.add_column(sa.Column("gameId", sa.Integer(), nullable=True))
        # 既存行を SV=1 に埋める
        op.execute("UPDATE box_members SET gameId = 1 WHERE gameId IS NULL")

        with op.batch_alter_table("box_members") as b:
            # NOT NULL に変更 + 外部キー + インデックス
            b.alter_column("gameId", existing_type=sa.Integer(), nullable=False)
            b.create_foreign_key("fk_box_members_game", "GameTitle", ["gameId"], ["id"])
            b.create_index("ix_box_user_game", ["userId", "gameId"])
            b.create_index("ix_box_user_game_nat_created", ["userId", "gameId", "nationalNo", "createdAt"])

    # 3) PartyMember に gameId を追加（NULL → UPDATE → NOT NULL/FK/Unique/Index）
    # テーブル未存在ならスキップ（初期化順序の違いで落ちるのを防止）
    if inspector.has_table("party_members"):
        with op.batch_alter_table("party_members") as b:
            b.add_column(sa.Column("gameId", sa.Integer(), nullable=True))
        # backfill
        op.execute("UPDATE party_members SET gameId = 1 WHERE gameId IS NULL")

        with op.batch_alter_table("party_members") as b:
            # 旧ユニーク制約を削除（存在しない場合は黙殺）
            try:
                b.drop_constraint("uq_party_user_slot", type_="unique")
            except Exception:
                pass

            # NOT NULL + 外部キー + 新ユニーク + インデックス
            b.alter_column("gameId", existing_type=sa.Integer(), nullable=False)
            b.create_foreign_key("fk_party_members_game", "GameTitle", ["gameId"], ["id"])
            b.create_unique_constraint("uq_party_user_game_slot", ["userId", "gameId", "slot"])
            b.create_index("ix_party_user_game", ["userId", "gameId"])
            b.create_index("ix_party_user_game_slot", ["userId", "gameId", "slot"])

            # 既存 index を冪等に再作成
            op.execute("DROP INDEX IF EXISTS ix_party_user_poke")
            b.create_index("ix_party_user_poke", ["userId", "nationalNo"])

    # 4) 既存行 backfill は server_default='1' により完了（上で default を解除済み）
    #    もし念のため明示反映したい場合は以下を許容（SQLiteでは不要）
    # conn.execute(sa.text("UPDATE box_members SET gameId = 1 WHERE gameId IS NULL"))
    # conn.execute(sa.text("UPDATE party_members SET gameId = 1 WHERE gameId IS NULL"))


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # PartyMember から巻き戻し
    if inspector.has_table("party_members"):
        with op.batch_alter_table("party_members") as b:
            try:
                b.drop_index("ix_party_user_game")
            except Exception:
                pass
            try:
                b.drop_index("ix_party_user_game_slot")
            except Exception:
                pass
            try:
                b.drop_constraint("uq_party_user_game_slot", type_="unique")
            except Exception:
                pass
            try:
                b.drop_constraint("fk_party_members_game", type_="foreignkey")
            except Exception:
                pass
            try:
                b.drop_column("gameId")
            except Exception:
                pass
            b.create_unique_constraint("uq_party_user_slot", ["userId", "slot"])
            op.execute("DROP INDEX IF EXISTS ix_party_user_poke")
            b.create_index("ix_party_user_poke", ["userId", "nationalNo"])

    # BoxMember から巻き戻し
    if inspector.has_table("box_members"):
        with op.batch_alter_table("box_members") as b:
            try:
                b.drop_index("ix_box_user_game")
            except Exception:
                pass
            try:
                b.drop_index("ix_box_user_game_nat_created")
            except Exception:
                pass
            try:
                b.drop_constraint("fk_box_members_game", type_="foreignkey")
            except Exception:
                pass
            try:
                b.drop_column("gameId")
            except Exception:
                pass
            b.create_index("ix_box_user_poke", ["userId", "nationalNo"])

    # GameTitle を削除（存在すれば）
    op.execute('DROP TABLE IF EXISTS "GameTitle"')