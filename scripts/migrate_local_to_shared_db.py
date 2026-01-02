#!/usr/bin/env python3
"""
ローカル環境のFishTrackとMyPokedexのデータを統合データベース（shared-db）に移行するスクリプト

使用方法:
    # 1. 統合DBコンテナを起動
    cd dev-workspace
    docker compose --profile local up -d shared-db
    
    # 2. 環境変数を設定して実行
    $env:MYPDEX_SOURCE_DATABASE_URL="postgresql://mypokedex:mypokedex_password@localhost:5433/mypokedex_db"
    $env:FISHTRACK_SOURCE_DATABASE_URL="postgresql://fishtrack:fishtrack_pass@localhost:5432/fishtrack_db"
    $env:SHARED_DATABASE_URL="postgresql://shared_user:shared_password@localhost:5434/shared_db"
    
    python scripts/migrate_local_to_shared_db.py
"""

import os
import sys
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

# 既存のmigrate_to_shared_db.pyをインポート
from scripts.migrate_to_shared_db import main

if __name__ == "__main__":
    # デフォルトのローカル環境URLを設定（環境変数が未設定の場合）
    if not os.environ.get("MYPDEX_SOURCE_DATABASE_URL") and not os.environ.get("MYPDEX_DATABASE_URL"):
        os.environ["MYPDEX_SOURCE_DATABASE_URL"] = "postgresql://mypokedex:mypokedex_password@localhost:5433/mypokedex_db"
    
    if not os.environ.get("FISHTRACK_SOURCE_DATABASE_URL") and not os.environ.get("FISHTRACK_DATABASE_URL"):
        os.environ["FISHTRACK_SOURCE_DATABASE_URL"] = "postgresql://fishtrack:fishtrack_pass@localhost:5432/fishtrack_db"
    
    if not os.environ.get("SHARED_DATABASE_URL") and not os.environ.get("SHARED_DB_URL"):
        os.environ["SHARED_DATABASE_URL"] = "postgresql://shared_user:shared_password@localhost:5434/shared_db"
    
    print("=" * 60)
    print("Local Database Migration to Shared DB")
    print("=" * 60)
    print(f"MyPokedex source: {os.environ.get('MYPDEX_SOURCE_DATABASE_URL', 'Not set')}")
    print(f"FishTrack source: {os.environ.get('FISHTRACK_SOURCE_DATABASE_URL', 'Not set')}")
    print(f"Shared DB target: {os.environ.get('SHARED_DATABASE_URL', 'Not set')}")
    print("=" * 60)
    print()
    
    main()

