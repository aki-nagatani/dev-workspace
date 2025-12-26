# migrations/versions/20250912_add_dexentry_and_backfill.py
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "20250912_add_dexentry_and_backfill"
down_revision = "3eb89a6ae1fc"

def upgrade():
    op.create_table(
        "DexEntry",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nationalNo", sa.Integer(), nullable=False),
        sa.Column("dexType", sa.String(20), nullable=False),
        sa.Column("dexNo", sa.Integer(), nullable=False),
        sa.UniqueConstraint("nationalNo", "dexType", name="uq_DexEntry_nat_dexType"),
    )
    op.create_index("ix_DexEntry_nationalNo", "DexEntry", ["nationalNo"])
    op.create_index("ix_DexEntry_dexType_dexNo", "DexEntry", ["dexType", "dexNo"], unique=False)

    # データ移行（存在する列のみを安全に投入）
    conn = op.get_bind()
    from sqlalchemy import inspect
    inspector = inspect(conn)

    def col_exists(table, col):
        try:
            columns = [col_info["name"] for col_info in inspector.get_columns(table)]
            return col in columns
        except Exception:
            return False

    for dexType, col in [("PALDEA","paldeaNo"), ("BLUEBERRY","blueberryNo"), ("KITAKAMI","kitakamiNo")]:
        if col_exists("Pokemon", col):
            conn.exec_driver_sql(f"""
                INSERT INTO "DexEntry" ("nationalNo", "dexType", "dexNo")
                SELECT "nationalNo", '{dexType}', "{col}"
                FROM "Pokemon"
                WHERE "{col}" IS NOT NULL
            """)

    # 互換VIEW（任意：残すと既存UIがすぐ動く）
    conn.exec_driver_sql('DROP VIEW IF EXISTS "PokemonLegacyView";')
    conn.exec_driver_sql("""
        CREATE VIEW "PokemonLegacyView" AS
        SELECT
          p.*,
          (SELECT "dexNo" FROM "DexEntry" d WHERE d."nationalNo"=p."nationalNo" AND d."dexType"='PALDEA')   AS paldeaNo,
          (SELECT "dexNo" FROM "DexEntry" d WHERE d."nationalNo"=p."nationalNo" AND d."dexType"='BLUEBERRY') AS blueberryNo,
          (SELECT "dexNo" FROM "DexEntry" d WHERE d."nationalNo"=p."nationalNo" AND d."dexType"='KITAKAMI')  AS kitakamiNo
        FROM "Pokemon" p;
    """)

def downgrade():
    op.drop_index("ix_DexEntry_dexType_dexNo", table_name="DexEntry")
    op.drop_index("ix_DexEntry_nationalNo", table_name="DexEntry")
    op.execute("DROP VIEW IF EXISTS PokemonLegacyView;")
    op.drop_table("DexEntry")