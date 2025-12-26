#!/usr/bin/env python3
"""
MyPokedexとFishTrackのデータを統合データベース（shared-db）に移行するスクリプト

使用方法:
    # 環境変数を設定
    export MYPDEX_SOURCE_DATABASE_URL="postgresql://user:pass@source:5432/mypokedex_db"
    export FISHTRACK_SOURCE_DATABASE_URL="postgresql://user:pass@source:5432/fishtrack_db"
    export SHARED_DATABASE_URL="postgresql://user:pass@shared-db:5432/shared_db"
    
    python scripts/migrate_to_shared_db.py
"""

import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Any

# プロジェクトのルートディレクトリをパスに追加
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mypokedex_root = os.path.join(workspace_root, '..', 'MyPokedex')
fishtrack_root = os.path.join(workspace_root, '..', 'FishTrack')

sys.path.insert(0, os.path.join(mypokedex_root, 'src'))
sys.path.insert(0, os.path.join(fishtrack_root, 'src'))

# MyPokedexモデルのインポート
from mypokedex.models.user import User
from mypokedex.models.pokemon import Pokemon
from mypokedex.models.game_title import GameTitle
from mypokedex.models.dex_entry import DexEntry
from mypokedex.models.regist import Regist
from mypokedex.models.party import BoxMember, PartyMember
from mypokedex.models.placement import Placement
from mypokedex.models.user_game_setting import UserGameSetting
from mypokedex.models.evolution import Evolution
from mypokedex.models.contact import Contact

# FishTrackモデルのインポート
from fishtrack.models.user import FishTrackUser
from fishtrack.models.manufacturer import Manufacturer
from fishtrack.models.rod_series import RodSeries
from fishtrack.models.reel_series import ReelSeries
from fishtrack.models.rod_model import RodModel
from fishtrack.models.reel_model import ReelModel
from fishtrack.models.rod_holding import RodHolding
from fishtrack.models.reel_holding import ReelHolding
from fishtrack.models.tackle_spec_import_log import TackleSpecImportLog
from fishtrack.models.ops_monitoring import OpsMonitoring

# 環境変数から接続情報を取得
MYPDEX_SOURCE_URL = os.environ.get(
    "MYPDEX_SOURCE_DATABASE_URL",
    os.environ.get("MYPDEX_DATABASE_URL", "")
)
FISHTRACK_SOURCE_URL = os.environ.get(
    "FISHTRACK_SOURCE_DATABASE_URL",
    os.environ.get("FISHTRACK_DATABASE_URL", "")
)
SHARED_DB_URL = os.environ.get(
    "SHARED_DATABASE_URL",
    os.environ.get("SHARED_DB_URL", "")
)

# MyPokedexのテーブル定義（移行順序を考慮）
MYPDEX_TABLES = [
    ("User", User),
    ("GameTitle", GameTitle),
    ("Pokemon", Pokemon),
    ("DexEntry", DexEntry),
    ("evolution", Evolution),
    ("UserGameSetting", UserGameSetting),
    ("Regist", Regist),
    ("party_members", PartyMember),
    ("box_members", BoxMember),
    ("placement", Placement),
    ("Contact", Contact),
]

# FishTrackのテーブル定義（移行順序を考慮）
FISHTRACK_TABLES = [
    ("fishtrack_user", FishTrackUser),
    ("manufacturer", Manufacturer),
    ("rod_series", RodSeries),
    ("reel_series", ReelSeries),
    ("rod_model", RodModel),
    ("reel_model", ReelModel),
    ("rod_holding", RodHolding),
    ("reel_holding", ReelHolding),
    ("tackle_spec_import_log", TackleSpecImportLog),
    ("ops_monitoring", OpsMonitoring),
]


def check_table_conflicts(target_engine):
    """テーブル名の競合をチェック"""
    inspector = inspect(target_engine)
    existing_tables = set(inspector.get_table_names())
    
    mypokedex_table_names = {table_name for table_name, _ in MYPDEX_TABLES}
    fishtrack_table_names = {table_name for table_name, _ in FISHTRACK_TABLES}
    
    conflicts = mypokedex_table_names & fishtrack_table_names
    if conflicts:
        print(f"ERROR: Table name conflicts detected: {conflicts}")
        return False
    
    print(f"✓ No table name conflicts found")
    print(f"  MyPokedex tables: {len(mypokedex_table_names)}")
    print(f"  FishTrack tables: {len(fishtrack_table_names)}")
    return True


def migrate_table(
    source_session,
    target_session,
    table_name: str,
    model_class,
    source_engine,
    target_engine,
):
    """単一テーブルのデータを移行"""
    print(f"  Migrating table: {table_name}...")
    
    try:
        # ソースからデータを取得
        source_inspector = inspect(source_engine)
        if table_name not in source_inspector.get_table_names():
            print(f"    Table {table_name} not found in source, skipping.")
            return 0
        
        # モデルのテーブル定義を使用してデータを取得
        source_data = source_session.query(model_class).all()
        
        if not source_data:
            print(f"    No data in {table_name}, skipping.")
            return 0
        
        print(f"    Found {len(source_data)} rows in source.")
        
        # ターゲットにデータを挿入
        # 既存データを削除（冪等性のため）
        target_session.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE'))
        
        # データをコピー
        count = 0
        for instance in source_data:
            # 新しいインスタンスを作成（IDをリセットしない）
            data_dict = {}
            for column in model_class.__table__.columns:
                value = getattr(instance, column.name)
                data_dict[column.name] = value
            
            new_instance = model_class(**data_dict)
            target_session.add(new_instance)
            count += 1
        
        target_session.flush()
        print(f"    Inserted {count} rows into target.")
        return count
        
    except Exception as e:
        print(f"    ERROR migrating {table_name}: {e}")
        import traceback
        traceback.print_exc()
        raise


def migrate_mypokedex_data(source_url: str, target_url: str):
    """MyPokedexのデータを移行"""
    print("\n" + "=" * 60)
    print("Migrating MyPokedex data...")
    print("=" * 60)
    
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    
    # スキーマを作成（MyPokedexのテーブル）
    print("Creating MyPokedex schema in target database...")
    from mypokedex.app_factory import createApp
    from mypokedex.extensions import db as mypokedex_db
    
    app = createApp({"SQLALCHEMY_DATABASE_URI": target_url})
    with app.app_context():
        # MyPokedexのテーブルのみ作成
        mypokedex_db.create_all()
        print("✓ MyPokedex schema created.")
    
    source_session = sessionmaker(bind=source_engine)()
    target_session = sessionmaker(bind=target_engine)()
    
    try:
        total_rows = 0
        for table_name, model_class in MYPDEX_TABLES:
            rows = migrate_table(
                source_session,
                target_session,
                table_name,
                model_class,
                source_engine,
                target_engine,
            )
            total_rows += rows
        
        target_session.commit()
        print(f"\n✓ MyPokedex migration completed: {total_rows} total rows migrated")
        return total_rows
        
    except Exception as e:
        target_session.rollback()
        print(f"\n✗ MyPokedex migration failed: {e}")
        raise
    finally:
        source_session.close()
        target_session.close()
        source_engine.dispose()
        target_engine.dispose()


def migrate_fishtrack_data(source_url: str, target_url: str):
    """FishTrackのデータを移行"""
    print("\n" + "=" * 60)
    print("Migrating FishTrack data...")
    print("=" * 60)
    
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    
    # スキーマを作成（FishTrackのテーブル）
    print("Creating FishTrack schema in target database...")
    from flask import Flask
    from fishtrack.extensions import db as fishtrack_db
    from fishtrack.config import apply_fishtrack_config
    
    app = Flask(__name__)
    app.config["SQLALCHEMY_BINDS"] = {"fishtrack": target_url}
    app.config["TESTING"] = False
    fishtrack_db.init_app(app)
    apply_fishtrack_config(app)
    
    with app.app_context():
        # FishTrackのテーブルのみ作成（bind_keyを使用）
        fishtrack_db.create_all(bind_key="fishtrack")
        print("✓ FishTrack schema created.")
    
    source_session = sessionmaker(bind=source_engine)()
    target_session = sessionmaker(bind=target_engine)()
    
    try:
        total_rows = 0
        for table_name, model_class in FISHTRACK_TABLES:
            rows = migrate_table(
                source_session,
                target_session,
                table_name,
                model_class,
                source_engine,
                target_engine,
            )
            total_rows += rows
        
        target_session.commit()
        print(f"\n✓ FishTrack migration completed: {total_rows} total rows migrated")
        return total_rows
        
    except Exception as e:
        target_session.rollback()
        print(f"\n✗ FishTrack migration failed: {e}")
        raise
    finally:
        source_session.close()
        target_session.close()
        source_engine.dispose()
        target_engine.dispose()


def verify_migration(target_url: str):
    """移行後のデータ整合性を検証"""
    print("\n" + "=" * 60)
    print("Verifying migration...")
    print("=" * 60)
    
    target_engine = create_engine(target_url)
    inspector = inspect(target_engine)
    tables = inspector.get_table_names()
    
    print(f"Total tables in target database: {len(tables)}")
    
    # MyPokedexのテーブルが存在するか確認
    mypokedex_table_names = {table_name for table_name, _ in MYPDEX_TABLES}
    fishtrack_table_names = {table_name for table_name, _ in FISHTRACK_TABLES}
    
    missing_mypokedex = mypokedex_table_names - set(tables)
    missing_fishtrack = fishtrack_table_names - set(tables)
    
    if missing_mypokedex:
        print(f"✗ Missing MyPokedex tables: {missing_mypokedex}")
        return False
    
    if missing_fishtrack:
        print(f"✗ Missing FishTrack tables: {missing_fishtrack}")
        return False
    
    print(f"✓ All MyPokedex tables present: {len(mypokedex_table_names)}")
    print(f"✓ All FishTrack tables present: {len(fishtrack_table_names)}")
    
    # データ行数を確認
    with target_engine.connect() as conn:
        for table_name in sorted(mypokedex_table_names | fishtrack_table_names):
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
            count = result.scalar()
            print(f"  {table_name}: {count} rows")
    
    print("\n✓ Migration verification completed successfully!")
    return True


def main():
    """メイン処理"""
    print("=" * 60)
    print("MyPokedex and FishTrack Database Migration Script")
    print("=" * 60)
    
    # 環境変数の確認
    if not SHARED_DB_URL:
        print("ERROR: SHARED_DATABASE_URL environment variable is not set")
        sys.exit(1)
    
    if not MYPDEX_SOURCE_URL:
        print("WARNING: MYPDEX_SOURCE_DATABASE_URL not set, skipping MyPokedex migration")
        migrate_mypokedex = False
    else:
        migrate_mypokedex = True
    
    if not FISHTRACK_SOURCE_URL:
        print("WARNING: FISHTRACK_SOURCE_DATABASE_URL not set, skipping FishTrack migration")
        migrate_fishtrack = False
    else:
        migrate_fishtrack = True
    
    if not migrate_mypokedex and not migrate_fishtrack:
        print("ERROR: No source database URLs provided")
        sys.exit(1)
    
    print(f"\nSource databases:")
    if migrate_mypokedex:
        print(f"  MyPokedex: {MYPDEX_SOURCE_URL}")
    if migrate_fishtrack:
        print(f"  FishTrack: {FISHTRACK_SOURCE_URL}")
    print(f"Target database: {SHARED_DB_URL}")
    
    # ターゲットデータベースへの接続テスト
    print("\nTesting target database connection...")
    try:
        target_engine = create_engine(SHARED_DB_URL)
        with target_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Target database connection successful")
    except Exception as e:
        print(f"✗ Failed to connect to target database: {e}")
        sys.exit(1)
    
    # テーブル名の競合チェック
    print("\nChecking for table name conflicts...")
    if not check_table_conflicts(target_engine):
        sys.exit(1)
    
    # データ移行
    try:
        if migrate_mypokedex:
            migrate_mypokedex_data(MYPDEX_SOURCE_URL, SHARED_DB_URL)
        
        if migrate_fishtrack:
            migrate_fishtrack_data(FISHTRACK_SOURCE_URL, SHARED_DB_URL)
        
        # 検証
        verify_migration(SHARED_DB_URL)
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        target_engine.dispose()


if __name__ == "__main__":
    main()

