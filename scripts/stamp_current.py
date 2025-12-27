#!/usr/bin/env python3
"""
現在のデータベースの状態をマイグレーションのベースラインとして設定するスクリプト

このスクリプトは、マイグレーション履歴をリセットして、現在のDBの状態を
最新のマイグレーション（head）としてマークします。

使用方法:
    # 環境変数を設定
    export SHARED_DATABASE_URL="postgresql://user:pass@shared-db:5432/shared_db"
    
    # 現在のDBの状態をheadとしてスタンプ
    python scripts/stamp_current.py
    
    # 特定のリビジョンとしてスタンプ
    python scripts/stamp_current.py --revision merge_fishtrack_mypokedex_heads
"""

import os
import sys
import argparse
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


def stamp_database(revision: str = "head"):
    """データベースのマイグレーション履歴を指定されたリビジョンとしてスタンプ"""
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
    
    print(f"=== Stamping database to revision: {revision} ===")
    print(f"Database URL: {db_url.split('@')[1] if '@' in db_url else '***'}")
    print(f"Alembic config: {alembic_ini}")
    print()
    print("⚠️  警告: この操作はマイグレーション履歴をリセットします。")
    print("   現在のデータベースの状態が指定されたリビジョンと一致していることを確認してください。")
    print()
    
    try:
        # データベースを指定されたリビジョンとしてスタンプ
        # これはマイグレーションを実行せず、alembic_versionテーブルを更新するだけ
        command.stamp(alembic_cfg, revision)
        print(f"\n=== Database stamped to revision: {revision} ===")
        print("マイグレーション履歴が更新されました。")
        print("次回のマイグレーション実行時は、このリビジョン以降の変更のみが適用されます。")
    except Exception as e:
        print(f"\n=== Stamping failed ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="現在のデータベースの状態をマイグレーションのベースラインとして設定"
    )
    parser.add_argument(
        "--revision",
        "-r",
        default="head",
        help="スタンプするリビジョン（デフォルト: head）",
    )
    
    args = parser.parse_args()
    stamp_database(args.revision)

