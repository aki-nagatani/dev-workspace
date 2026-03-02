#!/bin/sh
# 1RDS 3DB Phase 2a: Docker postgres コンテナ内で実行する移行ロジック
# run_migrate_fishtrack_rds_ec2.sh から呼ばれる。単体では実行しない。

set -e

if [ -z "$SOURCE_DATABASE_URL" ]; then
  echo "Error: SOURCE_DATABASE_URL is required." >&2
  exit 1
fi

TARGET="${TARGET_DB_NAME:-fishtrack_db}"

# SOURCE_DATABASE_URL から postgres DB 用 URL と 移行先 URL を生成
SOURCE_BASE="${SOURCE_DATABASE_URL%/*}"
POSTGRES_URL="${SOURCE_BASE}/postgres"
TARGET_URL="${SOURCE_BASE}/${TARGET}"

# 移行対象テーブル（migrate_fishtrack_tables_to_fishtrack_db.py と一致）
TABLE_ARGS="-t manufacturer -t reel_model -t rod_model -t rod_series -t reel_series"
TABLE_ARGS="$TABLE_ARGS -t fishtrack_user -t rod_holding -t field -t rental_boat_shop"
TABLE_ARGS="$TABLE_ARGS -t water_level_history -t tackle_spec_import_log -t ops_monitoring -t ops_job_log"
TABLE_ARGS="$TABLE_ARGS -t user_statistics_daily -t user_statistics_weekly -t alembic_version"

echo "Creating database ${TARGET}..."
EXISTS=$(psql "$POSTGRES_URL" -tAc "SELECT 1 FROM pg_database WHERE datname = '${TARGET}'" 2>/dev/null || true)
if [ "$EXISTS" != "1" ]; then
  psql "$POSTGRES_URL" -c "CREATE DATABASE ${TARGET}"
else
  echo "Database ${TARGET} already exists."
fi

echo "Dumping FishTrack tables from shared_db..."
pg_dump "$SOURCE_DATABASE_URL" --no-owner --no-acl $TABLE_ARGS | psql "$TARGET_URL" -q

echo "Done. Tables migrated to ${TARGET}."
