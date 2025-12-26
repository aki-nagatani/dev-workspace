"""change multiple tables to composite primary keys

Revision ID: 20251224_change_tables_to_composite_primary_keys
Revises: 20251224_change_regist_to_composite_primary_key
Create Date: 2025-12-24 23:41:58
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# ---- 識別子 ----
revision = "20251224_change_tables_to_composite_primary_keys"
down_revision = "20251224_change_regist_to_composite_primary_key"
branch_labels = None
depends_on = None


def upgrade():
    """複数のテーブルを複合主キーに変更"""
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    # 1. DexEntry: (nationalNo, dexType) → 複合主キー
    if dialect_name == "sqlite":
        # SQLite: テーブル再作成
        # PokemonLegacyViewがDexEntryを参照しているため、先に削除
        try:
            op.execute('DROP VIEW IF EXISTS "PokemonLegacyView";')
        except Exception:
            pass
        
        try:
            op.drop_constraint("uq_DexEntry_nat_dexType", "DexEntry", type_="unique")
        except Exception:
            pass
        try:
            op.drop_constraint("DexEntry_pkey", "DexEntry", type_="primary")
        except Exception:
            pass
        
        op.execute("""
            CREATE TABLE _alembic_tmp_DexEntry (
                nationalNo INTEGER NOT NULL,
                dexType VARCHAR(20) NOT NULL,
                dexNo INTEGER NOT NULL,
                PRIMARY KEY (nationalNo, dexType)
            )
        """)
        op.execute("""
            INSERT INTO _alembic_tmp_DexEntry (nationalNo, dexType, dexNo)
            SELECT nationalNo, dexType, dexNo FROM DexEntry
        """)
        op.drop_table("DexEntry")
        op.rename_table("_alembic_tmp_DexEntry", "DexEntry")
        op.create_index("ix_DexEntry_nationalNo", "DexEntry", ["nationalNo"], unique=False)
        op.create_index("ix_DexEntry_dexType_dexNo", "DexEntry", ["dexType", "dexNo"], unique=False)
        
        # PokemonLegacyViewを再作成
        op.execute("""
            CREATE VIEW "PokemonLegacyView" AS
            SELECT 
                p."nationalNo",
                p."nameJa",
                p."type1",
                p."type2",
                p."hp",
                p."attack",
                p."defense",
                p."spAtk",
                p."spDef",
                p."speed",
                p."total",
                COALESCE(de."dexNo", 0) AS "paldeaNo"
            FROM "Pokemon" p
            LEFT JOIN "DexEntry" de ON p."nationalNo" = de."nationalNo" AND de."dexType" = 'PALDEA';
        """)
    elif dialect_name == "postgresql":
        # PokemonLegacyViewがDexEntryを参照しているため、先に削除
        try:
            op.execute('DROP VIEW IF EXISTS "PokemonLegacyView";')
        except Exception:
            pass
        
        try:
            op.drop_constraint("uq_DexEntry_nat_dexType", "DexEntry", type_="unique")
        except Exception:
            pass
        try:
            op.drop_constraint("DexEntry_pkey", "DexEntry", type_="primary")
        except Exception:
            pass
        op.drop_column("DexEntry", "id")
        op.create_primary_key("DexEntry_pkey", "DexEntry", ["nationalNo", "dexType"])
        
        # PokemonLegacyViewを再作成
        op.execute("""
            CREATE VIEW "PokemonLegacyView" AS
            SELECT 
                p."nationalNo",
                p."nameJa",
                p."type1",
                p."type2",
                p."hp",
                p."attack",
                p."defense",
                p."spAtk",
                p."spDef",
                p."speed",
                p."total",
                COALESCE(de."dexNo", 0) AS "paldeaNo"
            FROM "Pokemon" p
            LEFT JOIN "DexEntry" de ON p."nationalNo" = de."nationalNo" AND de."dexType" = 'PALDEA';
        """)
    else:
        with op.batch_alter_table("DexEntry", recreate="always") as batch_op:
            try:
                batch_op.drop_constraint("uq_DexEntry_nat_dexType", type_="unique")
            except Exception:
                pass
            batch_op.drop_column("id")

    # 2. Evolution: (fromNationalNo, toNationalNo) → 複合主キー
    # evolutionテーブルが存在するか確認
    bind = op.get_bind()
    inspector = inspect(bind)
    evolution_exists = "evolution" in inspector.get_table_names()
    
    if evolution_exists:
        if dialect_name == "sqlite":
            try:
                op.drop_constraint("uq_evo_from_to", "evolution", type_="unique")
            except Exception:
                pass
            try:
                op.drop_constraint("evolution_pkey", "evolution", type_="primary")
            except Exception:
                pass
            
            op.execute("""
                CREATE TABLE _alembic_tmp_evolution (
                    fromNationalNo INTEGER NOT NULL,
                    toNationalNo INTEGER NOT NULL,
                    conditionText VARCHAR(200) NOT NULL,
                    PRIMARY KEY (fromNationalNo, toNationalNo)
                )
            """)
            op.execute("""
                INSERT INTO _alembic_tmp_evolution (fromNationalNo, toNationalNo, conditionText)
                SELECT fromNationalNo, toNationalNo, conditionText FROM evolution
            """)
            op.drop_table("evolution")
            op.rename_table("_alembic_tmp_evolution", "evolution")
            op.create_index("ix_evolution_fromNationalNo", "evolution", ["fromNationalNo"], unique=False)
            op.create_index("ix_evolution_toNationalNo", "evolution", ["toNationalNo"], unique=False)
        elif dialect_name == "postgresql":
            try:
                op.drop_constraint("uq_evo_from_to", "evolution", type_="unique")
            except Exception:
                pass
            try:
                op.drop_constraint("evolution_pkey", "evolution", type_="primary")
            except Exception:
                pass
            op.drop_column("evolution", "id")
            op.create_primary_key("evolution_pkey", "evolution", ["fromNationalNo", "toNationalNo"])
        else:
            with op.batch_alter_table("evolution", recreate="always") as batch_op:
                try:
                    batch_op.drop_constraint("uq_evo_from_to", type_="unique")
                except Exception:
                    pass
                batch_op.drop_column("id")

    # 3. UserGameSetting: (userId, gameId) → 複合主キー
    user_game_setting_exists = "UserGameSetting" in inspector.get_table_names()
    
    if user_game_setting_exists:
        if dialect_name == "sqlite":
            try:
                op.drop_constraint("uq_user_game_setting", "UserGameSetting", type_="unique")
            except Exception:
                pass
            try:
                op.drop_constraint("UserGameSetting_pkey", "UserGameSetting", type_="primary")
            except Exception:
                pass
            
            op.execute("""
                CREATE TABLE _alembic_tmp_UserGameSetting (
                    userId INTEGER NOT NULL,
                    gameId INTEGER NOT NULL,
                    isEnabled BOOLEAN NOT NULL DEFAULT 1,
                    PRIMARY KEY (userId, gameId),
                    FOREIGN KEY (userId) REFERENCES User(id),
                    FOREIGN KEY (gameId) REFERENCES GameTitle(id)
                )
            """)
            op.execute("""
                INSERT INTO _alembic_tmp_UserGameSetting (userId, gameId, isEnabled)
                SELECT userId, gameId, isEnabled FROM UserGameSetting
            """)
            op.drop_table("UserGameSetting")
            op.rename_table("_alembic_tmp_UserGameSetting", "UserGameSetting")
        elif dialect_name == "postgresql":
            try:
                op.drop_constraint("uq_user_game_setting", "UserGameSetting", type_="unique")
            except Exception:
                pass
            try:
                op.drop_constraint("UserGameSetting_pkey", "UserGameSetting", type_="primary")
            except Exception:
                pass
            op.drop_column("UserGameSetting", "id")
            op.create_primary_key("UserGameSetting_pkey", "UserGameSetting", ["userId", "gameId"])
        else:
            with op.batch_alter_table("UserGameSetting", recreate="always") as batch_op:
                try:
                    batch_op.drop_constraint("uq_user_game_setting", type_="unique")
                except Exception:
                    pass
                batch_op.drop_column("id")

    # 4. PartyMember: (userId, gameId, slot) → 複合主キー
    party_members_exists = "party_members" in inspector.get_table_names()
    
    if party_members_exists:
        if dialect_name == "sqlite":
            try:
                op.drop_constraint("uq_party_user_game_slot", "party_members", type_="unique")
            except Exception:
                pass
            try:
                op.drop_constraint("party_members_pkey", "party_members", type_="primary")
            except Exception:
                pass
            
            op.execute("""
                CREATE TABLE _alembic_tmp_party_members (
                    userId INTEGER NOT NULL,
                    gameId INTEGER NOT NULL,
                    slot INTEGER NOT NULL,
                    nationalNo INTEGER NOT NULL,
                    createdAt DATETIME NOT NULL,
                    PRIMARY KEY (userId, gameId, slot),
                    CHECK (slot BETWEEN 1 AND 6),
                    FOREIGN KEY (userId) REFERENCES User(id) ON DELETE CASCADE,
                    FOREIGN KEY (gameId) REFERENCES GameTitle(id),
                    FOREIGN KEY (nationalNo) REFERENCES Pokemon(nationalNo) ON DELETE RESTRICT
                )
            """)
            op.execute("""
                INSERT INTO _alembic_tmp_party_members (userId, gameId, slot, nationalNo, createdAt)
                SELECT userId, gameId, slot, nationalNo, createdAt FROM party_members
            """)
            op.drop_table("party_members")
            op.rename_table("_alembic_tmp_party_members", "party_members")
            op.create_index("ix_party_user_game", "party_members", ["userId", "gameId"], unique=False)
            op.create_index("ix_party_user_game_slot", "party_members", ["userId", "gameId", "slot"], unique=False)
            op.create_index("ix_party_user_poke", "party_members", ["userId", "nationalNo"], unique=False)
        elif dialect_name == "postgresql":
            try:
                op.drop_constraint("uq_party_user_game_slot", "party_members", type_="unique")
            except Exception:
                pass
            try:
                op.drop_constraint("party_members_pkey", "party_members", type_="primary")
            except Exception:
                pass
            op.drop_column("party_members", "id")
            op.create_primary_key("party_members_pkey", "party_members", ["userId", "gameId", "slot"])
        else:
            with op.batch_alter_table("party_members", recreate="always") as batch_op:
                try:
                    batch_op.drop_constraint("uq_party_user_game_slot", type_="unique")
                except Exception:
                    pass
                batch_op.drop_column("id")

    # 5. Placement: (userId, slot, location) → 複合主キー
    placement_exists = "placement" in inspector.get_table_names()
    
    if placement_exists:
        if dialect_name == "sqlite":
            try:
                op.drop_constraint("uq_party_slot_per_user", "placement", type_="unique")
            except Exception:
                pass
            try:
                op.drop_constraint("placement_pkey", "placement", type_="primary")
            except Exception:
                pass
            
            op.execute("""
                CREATE TABLE _alembic_tmp_placement (
                    userId INTEGER NOT NULL,
                    slot INTEGER,
                    location VARCHAR(10) NOT NULL,
                    nationalNo INTEGER NOT NULL,
                    createdAt DATETIME NOT NULL,
                    PRIMARY KEY (userId, slot, location),
                    FOREIGN KEY (userId) REFERENCES User(id)
                )
            """)
            op.execute("""
                INSERT INTO _alembic_tmp_placement (userId, slot, location, nationalNo, createdAt)
                SELECT userId, slot, location, nationalNo, createdAt FROM placement
            """)
            op.drop_table("placement")
            op.rename_table("_alembic_tmp_placement", "placement")
            op.create_index("ix_placement_userId", "placement", ["userId"], unique=False)
            op.create_index("ix_placement_nationalNo", "placement", ["nationalNo"], unique=False)
        elif dialect_name == "postgresql":
            try:
                op.drop_constraint("uq_party_slot_per_user", "placement", type_="unique")
            except Exception:
                pass
            try:
                op.drop_constraint("placement_pkey", "placement", type_="primary")
            except Exception:
                pass
            op.drop_column("placement", "id")
            op.create_primary_key("placement_pkey", "placement", ["userId", "slot", "location"])
        else:
            with op.batch_alter_table("placement", recreate="always") as batch_op:
                try:
                    batch_op.drop_constraint("uq_party_slot_per_user", type_="unique")
                except Exception:
                    pass
                batch_op.drop_column("id")


def downgrade():
    """複数のテーブルを元の単一主キーに戻す"""
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    # 5. Placement: 元に戻す
    if dialect_name == "sqlite":
        with op.batch_alter_table("placement", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("id", sa.Integer(), nullable=False))
            batch_op.create_primary_key("placement_pkey", ["id"])
            batch_op.create_unique_constraint("uq_party_slot_per_user", ["userId", "slot", "location"])
    elif dialect_name == "postgresql":
        try:
            op.drop_constraint("placement_pkey", "placement", type_="primary")
        except Exception:
            pass
        op.add_column("placement", sa.Column("id", sa.Integer(), nullable=False))
        op.execute("CREATE SEQUENCE IF NOT EXISTS \"placement_id_seq\"")
        op.execute("ALTER TABLE \"placement\" ALTER COLUMN \"id\" SET DEFAULT nextval('\"placement_id_seq\"')")
        op.execute("""
            UPDATE "placement"
            SET "id" = subquery.row_num
            FROM (
                SELECT "userId", "slot", "location",
                    ROW_NUMBER() OVER (ORDER BY "userId", "slot", "location") as row_num
                FROM "placement"
            ) AS subquery
            WHERE "placement"."userId" = subquery."userId"
              AND ("placement"."slot" = subquery."slot" OR ("placement"."slot" IS NULL AND subquery."slot" IS NULL))
              AND "placement"."location" = subquery."location"
        """)
        op.execute("SELECT setval('\"placement_id_seq\"', (SELECT MAX(\"id\") FROM \"placement\"))")
        op.create_primary_key("placement_pkey", "placement", ["id"])
        op.create_unique_constraint("uq_party_slot_per_user", "placement", ["userId", "slot", "location"])

    # 4. PartyMember: 元に戻す
    if dialect_name == "sqlite":
        with op.batch_alter_table("party_members", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("id", sa.Integer(), nullable=False))
            batch_op.create_primary_key("party_members_pkey", ["id"])
            batch_op.create_unique_constraint("uq_party_user_game_slot", ["userId", "gameId", "slot"])
    elif dialect_name == "postgresql":
        try:
            op.drop_constraint("party_members_pkey", "party_members", type_="primary")
        except Exception:
            pass
        op.add_column("party_members", sa.Column("id", sa.Integer(), nullable=False))
        op.execute("CREATE SEQUENCE IF NOT EXISTS \"party_members_id_seq\"")
        op.execute("ALTER TABLE \"party_members\" ALTER COLUMN \"id\" SET DEFAULT nextval('\"party_members_id_seq\"')")
        op.execute("""
            UPDATE "party_members"
            SET "id" = subquery.row_num
            FROM (
                SELECT "userId", "gameId", "slot",
                    ROW_NUMBER() OVER (ORDER BY "userId", "gameId", "slot") as row_num
                FROM "party_members"
            ) AS subquery
            WHERE "party_members"."userId" = subquery."userId"
              AND "party_members"."gameId" = subquery."gameId"
              AND "party_members"."slot" = subquery."slot"
        """)
        op.execute("SELECT setval('\"party_members_id_seq\"', (SELECT MAX(\"id\") FROM \"party_members\"))")
        op.create_primary_key("party_members_pkey", "party_members", ["id"])
        op.create_unique_constraint("uq_party_user_game_slot", "party_members", ["userId", "gameId", "slot"])

    # 3. UserGameSetting: 元に戻す
    if dialect_name == "sqlite":
        with op.batch_alter_table("UserGameSetting", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("id", sa.Integer(), nullable=False))
            batch_op.create_primary_key("UserGameSetting_pkey", ["id"])
            batch_op.create_unique_constraint("uq_user_game_setting", ["userId", "gameId"])
    elif dialect_name == "postgresql":
        try:
            op.drop_constraint("UserGameSetting_pkey", "UserGameSetting", type_="primary")
        except Exception:
            pass
        op.add_column("UserGameSetting", sa.Column("id", sa.Integer(), nullable=False))
        op.execute("CREATE SEQUENCE IF NOT EXISTS \"UserGameSetting_id_seq\"")
        op.execute("ALTER TABLE \"UserGameSetting\" ALTER COLUMN \"id\" SET DEFAULT nextval('\"UserGameSetting_id_seq\"')")
        op.execute("""
            UPDATE "UserGameSetting"
            SET "id" = subquery.row_num
            FROM (
                SELECT "userId", "gameId",
                    ROW_NUMBER() OVER (ORDER BY "userId", "gameId") as row_num
                FROM "UserGameSetting"
            ) AS subquery
            WHERE "UserGameSetting"."userId" = subquery."userId"
              AND "UserGameSetting"."gameId" = subquery."gameId"
        """)
        op.execute("SELECT setval('\"UserGameSetting_id_seq\"', (SELECT MAX(\"id\") FROM \"UserGameSetting\"))")
        op.create_primary_key("UserGameSetting_pkey", "UserGameSetting", ["id"])
        op.create_unique_constraint("uq_user_game_setting", "UserGameSetting", ["userId", "gameId"])

    # 2. Evolution: 元に戻す
    if dialect_name == "sqlite":
        with op.batch_alter_table("evolution", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("id", sa.Integer(), nullable=False))
            batch_op.create_primary_key("evolution_pkey", ["id"])
            batch_op.create_unique_constraint("uq_evo_from_to", ["fromNationalNo", "toNationalNo"])
    elif dialect_name == "postgresql":
        try:
            op.drop_constraint("evolution_pkey", "evolution", type_="primary")
        except Exception:
            pass
        op.add_column("evolution", sa.Column("id", sa.Integer(), nullable=False))
        op.execute("CREATE SEQUENCE IF NOT EXISTS \"evolution_id_seq\"")
        op.execute("ALTER TABLE \"evolution\" ALTER COLUMN \"id\" SET DEFAULT nextval('\"evolution_id_seq\"')")
        op.execute("""
            UPDATE "evolution"
            SET "id" = subquery.row_num
            FROM (
                SELECT "fromNationalNo", "toNationalNo",
                    ROW_NUMBER() OVER (ORDER BY "fromNationalNo", "toNationalNo") as row_num
                FROM "evolution"
            ) AS subquery
            WHERE "evolution"."fromNationalNo" = subquery."fromNationalNo"
              AND "evolution"."toNationalNo" = subquery."toNationalNo"
        """)
        op.execute("SELECT setval('\"evolution_id_seq\"', (SELECT MAX(\"id\") FROM \"evolution\"))")
        op.create_primary_key("evolution_pkey", "evolution", ["id"])
        op.create_unique_constraint("uq_evo_from_to", "evolution", ["fromNationalNo", "toNationalNo"])

    # 1. DexEntry: 元に戻す
    if dialect_name == "sqlite":
        with op.batch_alter_table("DexEntry", recreate="always") as batch_op:
            batch_op.add_column(sa.Column("id", sa.Integer(), nullable=False))
            batch_op.create_primary_key("DexEntry_pkey", ["id"])
            batch_op.create_unique_constraint("uq_DexEntry_nat_dexType", ["nationalNo", "dexType"])
    elif dialect_name == "postgresql":
        try:
            op.drop_constraint("DexEntry_pkey", "DexEntry", type_="primary")
        except Exception:
            pass
        op.add_column("DexEntry", sa.Column("id", sa.Integer(), nullable=False))
        op.execute("CREATE SEQUENCE IF NOT EXISTS \"DexEntry_id_seq\"")
        op.execute("ALTER TABLE \"DexEntry\" ALTER COLUMN \"id\" SET DEFAULT nextval('\"DexEntry_id_seq\"')")
        op.execute("""
            UPDATE "DexEntry"
            SET "id" = subquery.row_num
            FROM (
                SELECT "nationalNo", "dexType",
                    ROW_NUMBER() OVER (ORDER BY "nationalNo", "dexType") as row_num
                FROM "DexEntry"
            ) AS subquery
            WHERE "DexEntry"."nationalNo" = subquery."nationalNo"
              AND "DexEntry"."dexType" = subquery."dexType"
        """)
        op.execute("SELECT setval('\"DexEntry_id_seq\"', (SELECT MAX(\"id\") FROM \"DexEntry\"))")
        op.create_primary_key("DexEntry_pkey", "DexEntry", ["id"])
        op.create_unique_constraint("uq_DexEntry_nat_dexType", "DexEntry", ["nationalNo", "dexType"])

