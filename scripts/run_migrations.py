#!/usr/bin/env python3
"""
統合データベース（shared-db）のマイグレーションを実行するスクリプト

使用方法:
    # 環境変数を設定
    export SHARED_DATABASE_URL="postgresql://user:pass@shared-db:5432/shared_db"
    
    # マイグレーションを実行
    python scripts/run_migrations.py
"""

import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

# FishTrackとMyPokedexのsrcディレクトリをパスに追加（env.pyで使用）
fishtrack_src = workspace_root.parent / "FishTrack" / "src"
mypokedex_src = workspace_root.parent / "MyPokedex" / "src"
for src_dir in [fishtrack_src, mypokedex_src]:
    if src_dir.exists() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

# Alembicをインポート
try:
    from alembic import command
    from alembic.config import Config
except ImportError:
    print("Error: alembic is not installed. Please install it with: pip install alembic")
    sys.exit(1)


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


def check_alembic_version_table(db_url: str) -> bool:
    """alembic_versionテーブルが存在するか確認"""
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
            """))
            return result.scalar()
    except Exception:
        return False


def run_migrations(target_revision: str = "head"):
    """統合マイグレーションを実行
    
    Args:
        target_revision: 適用するマイグレーションのリビジョン（デフォルト: "head"）
                        マイグレーションリセット後の再適用の場合は "merge_fishtrack_mypokedex_heads" を指定
    """
    # Alembic設定ファイルのパス
    alembic_ini = workspace_root / "migrations" / "alembic.ini"
    
    if not alembic_ini.exists():
        raise FileNotFoundError(
            f"Alembic設定ファイルが見つかりません: {alembic_ini}\n"
            "統合マイグレーションディレクトリが正しく設定されているか確認してください。"
        )
    
    # Alembic設定を読み込み
    alembic_cfg = Config(str(alembic_ini))
    
    # データベースURLを設定
    db_url = get_database_url()
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    
    # 環境変数も設定（env.pyで使用）
    os.environ["SHARED_DATABASE_URL"] = db_url
    
    print(f"=== Running unified migrations ===")
    print(f"Database URL: {db_url.split('@')[1] if '@' in db_url else '***'}")
    print(f"Target revision: {target_revision}")
    print(f"Alembic config: {alembic_ini}")
    print()
    
    # alembic_versionテーブルの存在確認
    has_version_table = check_alembic_version_table(db_url)
    if not has_version_table:
        print("⚠️  Warning: alembic_version table does not exist")
        print("   This may be a fresh database or after migration reset.")
        if target_revision == "head":
            print("   Automatically switching to 'merge_fishtrack_mypokedex_heads' for migration reset recovery.")
            target_revision = "merge_fishtrack_mypokedex_heads"
        print()
    
    try:
        # マイグレーションを実行
        command.upgrade(alembic_cfg, target_revision)
        print(f"\n=== Migration to {target_revision} completed successfully ===")
    except Exception as e:
        print(f"\n=== Migration failed ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run unified database migrations")
    parser.add_argument(
        "--target",
        type=str,
        default="head",
        help="Target revision to upgrade to (default: head). Use 'merge_fishtrack_mypokedex_heads' for migration reset recovery."
    )
    
    args = parser.parse_args()
    run_migrations(target_revision=args.target)

