"""drop Pokemon.paldeaNo column now sourced via DexEntry

Revision ID: 20250920_remove_pokemon_paldeano
Revises: 20250920_drop_dexseed
Create Date: 2025-09-20 16:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20250920_remove_pokemon_paldeano"
down_revision = "20250920_drop_dexseed"
branch_labels = None
depends_on = None


def _drop_related_views(conn) -> None:
    """Drop views that reference Pokemon or DexSeed."""
    from sqlalchemy import text
    dialect_name = conn.dialect.name
    if dialect_name == 'sqlite':
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='view' AND (sql LIKE '%Pokemon%' OR sql LIKE '%DexSeed%');"
        ))
        rows = result.fetchall()
    elif dialect_name == 'postgresql':
        result = conn.execute(text(
            """
            SELECT viewname FROM pg_views 
            WHERE schemaname = 'public' 
            AND (definition LIKE '%Pokemon%' OR definition LIKE '%DexSeed%');
            """
        ))
        rows = result.fetchall()
    else:
        # その他のデータベース（必要に応じて対応）
        return
    
    for row in rows:
        name = row[0] if isinstance(row, (tuple, list)) else row
        conn.execute(text(f'DROP VIEW IF EXISTS "{name}";'))


def _cleanup_tmp_tables(conn) -> None:
    conn.exec_driver_sql("DROP TABLE IF EXISTS \"_alembic_tmp_Pokemon\";")


def upgrade() -> None:
    """Drop Pokemon.paldeaNo and refresh compatibility view."""
    conn = op.get_bind()
    # ビューを先に削除（カラム削除前に実行する必要がある）
    op.execute('DROP VIEW IF EXISTS "PokemonLegacyView";')
    _drop_related_views(conn)
    _cleanup_tmp_tables(conn)
    with op.batch_alter_table("Pokemon", schema=None) as batch_op:
        batch_op.drop_index("ix_Pokemon_paldeaNo")
        batch_op.drop_column("paldeaNo")
    op.execute(
        """
        CREATE VIEW "PokemonLegacyView" AS
        SELECT
          p.*,
          (SELECT "dexNo" FROM "DexEntry" d WHERE d."nationalNo"=p."nationalNo" AND d."dexType"='PALDEA')   AS paldeaNo,
          (SELECT "dexNo" FROM "DexEntry" d WHERE d."nationalNo"=p."nationalNo" AND d."dexType"='BLUEBERRY') AS blueberryNo,
          (SELECT "dexNo" FROM "DexEntry" d WHERE d."nationalNo"=p."nationalNo" AND d."dexType"='KITAKAMI')  AS kitakamiNo
        FROM "Pokemon" p;
        """
    )


def downgrade() -> None:
    """Recreate Pokemon.paldeaNo and restore legacy view."""
    conn = op.get_bind()
    _drop_related_views(conn)
    _cleanup_tmp_tables(conn)
    with op.batch_alter_table("Pokemon", schema=None) as batch_op:
        batch_op.add_column(sa.Column("paldeaNo", sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f("ix_Pokemon_paldeaNo"), ["paldeaNo"], unique=False)
    op.execute(
        """
        UPDATE "Pokemon" AS p
        SET "paldeaNo" = (
            SELECT d."dexNo"
            FROM "DexEntry" AS d
            WHERE d."nationalNo" = p."nationalNo"
              AND d."dexType" = 'PALDEA'
        )
        """
    )
    op.execute('DROP VIEW IF EXISTS "PokemonLegacyView";')
    op.execute(
        """
        CREATE VIEW "PokemonLegacyView" AS
        SELECT
          p.*,
          (SELECT "dexNo" FROM "DexEntry" d WHERE d."nationalNo"=p."nationalNo" AND d."dexType"='PALDEA')   AS paldeaNo,
          (SELECT "dexNo" FROM "DexEntry" d WHERE d."nationalNo"=p."nationalNo" AND d."dexType"='BLUEBERRY') AS blueberryNo,
          (SELECT "dexNo" FROM "DexEntry" d WHERE d."nationalNo"=p."nationalNo" AND d."dexType"='KITAKAMI')  AS kitakamiNo
        FROM "Pokemon" p;
        """
    )
