#!/bin/sh
# 1RDS 3DB Phase 2b: Docker postgres コンテナ内で実行する移行ロジック（アーカイブ）
# run_migrate_mypokedex_rds_ec2.sh から呼ばれる。単体では実行しない。

set -e

if [ -z "$SOURCE_DATABASE_URL" ]; then
  echo "Error: SOURCE_DATABASE_URL is required." >&2
  exit 1
fi

TARGET="${TARGET_DB_NAME:-mypokedex_db}"

# SOURCE_DATABASE_URL から postgres DB 用 URL と 移行先 URL を生成
SOURCE_BASE="${SOURCE_DATABASE_URL%/*}"
POSTGRES_URL="${SOURCE_BASE}/postgres"
TARGET_URL="${SOURCE_BASE}/${TARGET}"

# 移行対象テーブル（migrate_mypokedex_tables_to_mypokedex_db.py と一致・大文字は pg_dump -t でダブルクォート）
echo "Creating database ${TARGET}..."
EXISTS=$(psql "$POSTGRES_URL" -tAc "SELECT 1 FROM pg_database WHERE datname = '${TARGET}'" 2>/dev/null || true)
if [ "$EXISTS" != "1" ]; then
  psql "$POSTGRES_URL" -c "CREATE DATABASE ${TARGET}"
else
  echo "Database ${TARGET} already exists."
fi

echo "Dumping MyPokedex tables from shared_db..."
pg_dump "$SOURCE_DATABASE_URL" --no-owner --no-acl \
  -t '"User"' -t '"UserGameSetting"' -t '"Regist"' -t '"DexEntry"' -t '"Pokemon"' -t '"GameTitle"' \
  -t evolution -t placement -t box_members -t party_members -t '"Contact"' \
  -t user_statistics_daily -t user_statistics_weekly -t alembic_version \
  | psql "$TARGET_URL" -q

echo "Done. Tables migrated to ${TARGET}."
