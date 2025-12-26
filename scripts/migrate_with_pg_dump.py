#!/usr/bin/env python3
"""
pg_dumpを使用してMyPokedexとFishTrackのデータを統合データベース（shared-db）に移行するスクリプト

このスクリプトは、既存のRDSインスタンスのパスワードが不明な場合に使用できます。
pg_dumpを使用してデータをエクスポートし、新しいデータベースにインポートします。

使用方法:
    # 環境変数を設定
    export MYPDEX_SOURCE_DATABASE_URL="postgresql://user:pass@source:5432/mypokedex_db"
    export FISHTRACK_SOURCE_DATABASE_URL="postgresql://user:pass@source:5432/fishtrack_db"
    export SHARED_DATABASE_URL="postgresql://user:pass@shared-db:5432/shared_db"
    
    python scripts/migrate_with_pg_dump.py
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# 環境変数から接続文字列を取得
MYPDEX_SOURCE_URL = os.environ.get("MYPDEX_SOURCE_DATABASE_URL")
FISHTRACK_SOURCE_URL = os.environ.get("FISHTRACK_SOURCE_DATABASE_URL")
SHARED_DB_URL = os.environ.get("SHARED_DATABASE_URL")


def parse_db_url(url: str) -> dict:
    """データベースURLをパース"""
    # postgresql://user:pass@host:port/dbname
    if not url.startswith("postgresql://"):
        raise ValueError(f"Invalid database URL format: {url}")
    
    url = url.replace("postgresql://", "")
    if "@" in url:
        auth, rest = url.split("@", 1)
        if ":" in auth:
            user, password = auth.split(":", 1)
        else:
            user = auth
            password = ""
    else:
        user = ""
        password = ""
        rest = url
    
    if ":" in rest:
        host_port, dbname = rest.rsplit("/", 1)
        if ":" in host_port:
            host, port = host_port.split(":", 1)
        else:
            host = host_port
            port = "5432"
    else:
        host = rest
        port = "5432"
        dbname = ""
    
    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "dbname": dbname
    }


def run_pg_dump(source_url: str, output_file: str) -> bool:
    """pg_dumpを実行してデータをエクスポート"""
    try:
        db_info = parse_db_url(source_url)
        env = os.environ.copy()
        if db_info["password"]:
            env["PGPASSWORD"] = db_info["password"]
        
        cmd = [
            "pg_dump",
            "-h", db_info["host"],
            "-p", db_info["port"],
            "-U", db_info["user"],
            "-d", db_info["dbname"],
            "-F", "c",  # custom format
            "-f", output_file
        ]
        
        print(f"Running pg_dump: {' '.join(cmd[:6])} ...")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ pg_dump failed: {result.stderr}")
            return False
        
        print(f"✓ pg_dump completed: {output_file}")
        return True
    except Exception as e:
        print(f"✗ pg_dump error: {e}")
        return False


def run_pg_restore(target_url: str, dump_file: str, schema_only: bool = False) -> bool:
    """pg_restoreを実行してデータをインポート"""
    try:
        db_info = parse_db_url(target_url)
        env = os.environ.copy()
        if db_info["password"]:
            env["PGPASSWORD"] = db_info["password"]
        
        cmd = [
            "pg_restore",
            "-h", db_info["host"],
            "-p", db_info["port"],
            "-U", db_info["user"],
            "-d", db_info["dbname"],
            "-v"  # verbose
        ]
        
        if schema_only:
            cmd.append("--schema-only")
        else:
            cmd.append("--data-only")
        
        cmd.append(dump_file)
        
        print(f"Running pg_restore: {' '.join(cmd[:6])} ...")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ pg_restore failed: {result.stderr}")
            return False
        
        print(f"✓ pg_restore completed")
        return True
    except Exception as e:
        print(f"✗ pg_restore error: {e}")
        return False


def main():
    """メイン処理"""
    print("=" * 60)
    print("MyPokedex and FishTrack Database Migration Script (pg_dump)")
    print("=" * 60)
    
    # 環境変数の確認
    if not SHARED_DB_URL:
        print("ERROR: SHARED_DATABASE_URL environment variable is not set")
        sys.exit(1)
    
    migrate_mypokedex = bool(MYPDEX_SOURCE_URL)
    migrate_fishtrack = bool(FISHTRACK_SOURCE_URL)
    
    if not migrate_mypokedex and not migrate_fishtrack:
        print("ERROR: No source database URLs provided")
        sys.exit(1)
    
    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp(prefix="db_migration_")
    print(f"\nUsing temporary directory: {temp_dir}")
    
    try:
        # MyPokedexの移行
        if migrate_mypokedex:
            print("\n" + "=" * 60)
            print("Migrating MyPokedex data...")
            print("=" * 60)
            
            dump_file = os.path.join(temp_dir, "mypokedex.dump")
            if not run_pg_dump(MYPDEX_SOURCE_URL, dump_file):
                print("✗ MyPokedex migration failed")
                sys.exit(1)
            
            # スキーマのみをインポート
            if not run_pg_restore(SHARED_DB_URL, dump_file, schema_only=True):
                print("✗ MyPokedex schema import failed")
                sys.exit(1)
            
            # データをインポート
            if not run_pg_restore(SHARED_DB_URL, dump_file, schema_only=False):
                print("✗ MyPokedex data import failed")
                sys.exit(1)
            
            print("✓ MyPokedex migration completed")
        
        # FishTrackの移行
        if migrate_fishtrack:
            print("\n" + "=" * 60)
            print("Migrating FishTrack data...")
            print("=" * 60)
            
            dump_file = os.path.join(temp_dir, "fishtrack.dump")
            if not run_pg_dump(FISHTRACK_SOURCE_URL, dump_file):
                print("✗ FishTrack migration failed")
                sys.exit(1)
            
            # スキーマのみをインポート
            if not run_pg_restore(SHARED_DB_URL, dump_file, schema_only=True):
                print("✗ FishTrack schema import failed")
                sys.exit(1)
            
            # データをインポート
            if not run_pg_restore(SHARED_DB_URL, dump_file, schema_only=False):
                print("✗ FishTrack data import failed")
                sys.exit(1)
            
            print("✓ FishTrack migration completed")
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
    finally:
        # 一時ファイルを削除
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\nCleaned up temporary directory: {temp_dir}")


if __name__ == "__main__":
    main()

