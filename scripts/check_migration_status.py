#!/usr/bin/env python3
"""
マイグレーション状態を確認するスクリプト
データベースのalembic_versionテーブルを直接確認します
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# プロジェクトのルートディレクトリをパスに追加
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))


def get_database_url() -> str:
    """環境変数からデータベースURLを取得"""
    url = (
        os.getenv("SHARED_DATABASE_URL")
        or os.getenv("SHARED_DB_URL")
        or os.getenv("FISHTRACK_DATABASE_URL")
        or os.getenv("MYPDEX_DATABASE_URL")
        or os.getenv("DB_URL")
    )
    if not url:
        raise RuntimeError(
            "データベースURLが設定されていません。\n"
            "環境変数（SHARED_DATABASE_URL, SHARED_DB_URL, FISHTRACK_DATABASE_URL, "
            "MYPDEX_DATABASE_URL, DB_URL）のいずれかを設定してください。"
        )
    return url


def check_migration_status(db_url: str, environment_name: str):
    """マイグレーション状態を確認"""
    print("=" * 60)
    print(f"環境: {environment_name}")
    print(f"データベース: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print("=" * 60)
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # alembic_versionテーブルの存在確認
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("⚠️ alembic_versionテーブルが存在しません")
                print("   マイグレーションが適用されていない可能性があります")
                return
            
            # マイグレーション状態を取得
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            versions = [row[0] for row in result]
            
            if versions:
                print(f"✅ 現在のマイグレーション状態:")
                for version in versions:
                    print(f"   - {version}")
            else:
                print("⚠️ マイグレーションが適用されていません")
            
            # マイグレーションファイルの確認（dev-workspaceの場合）
            if "dev-workspace" in str(workspace_root):
                migrations_dir = workspace_root / "migrations" / "versions"
                if migrations_dir.exists():
                    print(f"\n📁 マイグレーションファイル数:")
                    fishtrack_count = len(list((migrations_dir / "fishtrack").glob("*.py"))) if (migrations_dir / "fishtrack").exists() else 0
                    mypokedex_count = len(list((migrations_dir / "mypokedex").glob("*.py"))) if (migrations_dir / "mypokedex").exists() else 0
                    shared_count = len(list((migrations_dir / "shared").glob("*.py"))) if (migrations_dir / "shared").exists() else 0
                    print(f"   - FishTrack: {fishtrack_count}ファイル")
                    print(f"   - MyPokedex: {mypokedex_count}ファイル")
                    print(f"   - Shared: {shared_count}ファイル")
                    print(f"   - 合計: {fishtrack_count + mypokedex_count + shared_count}ファイル")
            
    except OperationalError as e:
        print(f"❌ データベース接続エラー: {e}")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
    
    print()


def main():
    """メイン処理"""
    print("=" * 60)
    print("マイグレーション状態確認")
    print("=" * 60)
    print()
    
    # ローカル環境の確認
    environments = []
    
    # 統合DB（shared-db）ローカル
    if os.getenv("SHARED_DATABASE_URL") or os.getenv("SHARED_DB_URL"):
        db_url = get_database_url()
        check_migration_status(db_url, "ローカル統合DB (shared-db)")
    else:
        # デフォルトのローカル統合DB URL
        default_local_url = "postgresql://shared_user:shared_password@localhost:5434/shared_db"
        try:
            check_migration_status(default_local_url, "ローカル統合DB (shared-db)")
        except:
            pass
    
    # FishTrackローカルDB
    fishtrack_url = os.getenv("FISHTRACK_DATABASE_URL", "postgresql://fishtrack:fishtrack_pass@localhost:5432/fishtrack_db")
    try:
        check_migration_status(fishtrack_url, "ローカルFishTrack DB")
    except:
        pass
    
    # MyPokedexローカルDB
    mypokedex_url = os.getenv("MYPDEX_DATABASE_URL", "postgresql://mypokedex:mypokedex_password@localhost:5433/mypokedex_db")
    try:
        check_migration_status(mypokedex_url, "ローカルMyPokedex DB")
    except:
        pass
    
    print("=" * 60)
    print("確認完了")
    print("=" * 60)


if __name__ == "__main__":
    main()

