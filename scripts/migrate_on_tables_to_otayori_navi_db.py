#!/usr/bin/env python3
"""1RDS 3DB Phase 1: shared_db の on_* テーブルを otayori_navi DB へ移行するスクリプト

移行対象テーブル: on_families, on_children, on_users, on_family_invites, on_documents

使用方法:
  ローカルDocker:
    export SOURCE_DATABASE_URL="postgresql://shared_user:shared_password@localhost:5434/shared_db"
    python scripts/migrate_on_tables_to_otayori_navi_db.py

  本番RDS（要確認）:
    export SOURCE_DATABASE_URL="postgresql://user:pass@rds-endpoint:5432/shared_db"
    python scripts/migrate_on_tables_to_otayori_navi_db.py

環境変数:
  SOURCE_DATABASE_URL: 移行元（shared_db）の接続URL（必須）
  TARGET_DB_NAME: 移行先DB名（デフォルト: otayori_navi）
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ON_TABLES = [
    "on_families",
    "on_children",
    "on_users",
    "on_family_invites",
    "on_documents",
]


def parse_db_url(url: str) -> dict:
    """PostgreSQL接続URLをパース"""
    if not url or not url.startswith("postgresql://"):
        raise ValueError(f"Invalid database URL: {url}")

    url = url.replace("postgresql://", "")
    auth, rest = url.split("@", 1) if "@" in url else ("", url)
    user, password = auth.split(":", 1) if ":" in auth else (auth, "")

    rest = rest.split("?")[0]  # クエリ除去
    if "/" in rest:
        host_port, dbname = rest.rsplit("/", 1)
    else:
        host_port, dbname = rest, ""
    host, port = host_port.split(":", 1) if ":" in host_port else (host_port, "5432")

    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "dbname": dbname,
    }


def run_cmd(cmd: list[str], env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """コマンド実行"""
    return subprocess.run(
        cmd,
        env=env or os.environ,
        check=check,
        capture_output=True,
        text=True,
    )


def main() -> int:
    source_url = os.environ.get("SOURCE_DATABASE_URL")
    target_db = os.environ.get("TARGET_DB_NAME", "otayori_navi")

    if not source_url:
        print("Error: SOURCE_DATABASE_URL is required.", file=sys.stderr)
        return 1

    try:
        info = parse_db_url(source_url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    base_url = f"postgresql://{info['user']}:{info['password']}@{info['host']}:{info['port']}"
    env = os.environ.copy()
    if info["password"]:
        env["PGPASSWORD"] = info["password"]

    # 1. 新DB作成（postgres DBへ接続して CREATE DATABASE）
    print(f"Creating database {target_db}...")
    create_sql = f"SELECT 1 FROM pg_database WHERE datname = '{target_db}'"
    result = run_cmd(
        ["psql", "-h", info["host"], "-p", info["port"], "-U", info["user"], "-d", "postgres", "-tAc", create_sql],
        env=env,
        check=False,
    )
    if result.returncode != 0:
        print(f"Error checking database: {result.stderr}", file=sys.stderr)
        return 1

    if result.stdout.strip() != "1":
        run_cmd(
            ["psql", "-h", info["host"], "-p", info["port"], "-U", info["user"], "-d", "postgres", "-c", f"CREATE DATABASE {target_db}"],
            env=env,
        )
    else:
        print(f"Database {target_db} already exists.")

    # 2. pg_dump で on_* テーブルのみエクスポート（スキーマ+データ）
    table_args = []
    for t in ON_TABLES:
        table_args.extend(["-t", t])

    dump_cmd = [
        "pg_dump",
        "-h", info["host"],
        "-p", info["port"],
        "-U", info["user"],
        "-d", info["dbname"],
        "--no-owner",
        "--no-acl",
        *table_args,
    ]

    print(f"Dumping {len(ON_TABLES)} tables from {info['dbname']}...")
    result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error pg_dump: {result.stderr}", file=sys.stderr)
        return 1

    # 3. 新DBへリストア
    print(f"Restoring to {target_db}...")
    restore = subprocess.Popen(
        ["psql", "-h", info["host"], "-p", info["port"], "-U", info["user"], "-d", target_db, "-q"],
        stdin=subprocess.PIPE,
        env=env,
    )
    restore.communicate(input=result.stdout)
    if restore.returncode != 0:
        print("Error during restore.", file=sys.stderr)
        return 1

    # 4. alembic_version をスタンプ（shared の head = 20260209140000）
    stamp_sql = """
    CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY);
    DELETE FROM alembic_version;
    INSERT INTO alembic_version (version_num) VALUES ('20260209140000');
    """
    run_cmd(
        ["psql", "-h", info["host"], "-p", info["port"], "-U", info["user"], "-d", target_db, "-c", stamp_sql],
        env=env,
    )

    print(f"Done. Tables migrated to {target_db}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
