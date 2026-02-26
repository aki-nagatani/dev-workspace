"""seed water level reservoirs (5 lakes: 亀山湖, 津久井湖, 相模湖, 三島湖, 戸面原湖)

Revision ID: 20260227100000
Revises: 20260226220000
Create Date: 2026-02-27 10:00:00.000000

水位推移の初期対象5湖を登録。
- rental_boat_shop: ともゑ釣り船、天羽土地改良区
- field: 亀山湖(public)、津久井湖(public)、相模湖(public)、三島湖(rental)、戸面原湖(rental)

06_database 6-9-3 参照。
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "20260227100000"
down_revision = "20260226220000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. rental_boat_shop: ともゑ釣り船、天羽土地改良区（存在しなければ挿入）
    conn.execute(
        text("""
        INSERT INTO rental_boat_shop (name, website_url)
        SELECT 'ともゑ釣り船', 'https://tomoeboat.jp/b-catch/'
        WHERE NOT EXISTS (SELECT 1 FROM rental_boat_shop WHERE website_url LIKE '%tomoeboat%')
        """)
    )
    conn.execute(
        text("""
        INSERT INTO rental_boat_shop (name, website_url)
        SELECT '天羽土地改良区', 'https://amaha-lid.sakura.ne.jp/cyosui/'
        WHERE NOT EXISTS (SELECT 1 FROM rental_boat_shop WHERE website_url LIKE '%amaha-lid%')
        """)
    )

    # 2. field: 川の防災情報（public）3湖
    for name, location, ofc, obs in [
        ("亀山湖", "千葉県", 3073, 1),
        ("津久井湖", "神奈川県", 3585, 1),
        ("相模湖", "神奈川県", 3585, 4),
    ]:
        conn.execute(
            text("""
            INSERT INTO field (name, location, water_level_source_type, obs_ofc_cd, obs_obs_cd)
            SELECT :name, :location, 'public', :ofc, :obs
            WHERE NOT EXISTS (SELECT 1 FROM field WHERE name = :name)
            """),
            {"name": name, "location": location, "ofc": ofc, "obs": obs},
        )

    # 3. field: レンタルボート店（rental_boat_shop）2湖
    conn.execute(
        text("""
        INSERT INTO field (name, location, water_level_source_type, rental_boat_shop_id)
        SELECT '三島湖', '静岡県', 'rental_boat_shop',
            (SELECT id FROM rental_boat_shop WHERE website_url LIKE '%tomoeboat%' LIMIT 1)
        WHERE NOT EXISTS (SELECT 1 FROM field WHERE name = '三島湖')
        AND EXISTS (SELECT 1 FROM rental_boat_shop WHERE website_url LIKE '%tomoeboat%')
        """)
    )
    conn.execute(
        text("""
        INSERT INTO field (name, location, water_level_source_type, rental_boat_shop_id)
        SELECT '戸面原湖', '千葉県', 'rental_boat_shop',
            (SELECT id FROM rental_boat_shop WHERE website_url LIKE '%amaha-lid%' LIMIT 1)
        WHERE NOT EXISTS (SELECT 1 FROM field WHERE name = '戸面原湖')
        AND EXISTS (SELECT 1 FROM rental_boat_shop WHERE website_url LIKE '%amaha-lid%')
        """)
    )


def downgrade() -> None:
    conn = op.get_bind()
    # 5湖のFieldを削除（water_level_source_type が public または rental_boat_shop のもの）
    conn.execute(
        text("""
        DELETE FROM field WHERE name IN ('亀山湖', '津久井湖', '相模湖', '三島湖', '戸面原湖')
        """)
    )
    # レンタルボート店を削除
    conn.execute(
        text("""
        DELETE FROM rental_boat_shop
        WHERE website_url LIKE '%tomoeboat%' OR website_url LIKE '%amaha-lid%'
        """)
    )
