#!/bin/sh
# 1RDS 3DB Phase 2a: EC2 上で RDS の FishTrack テーブルを fishtrack_db へ移行（アーカイブ）
# Docker postgres イメージ使用（EC2 に psql/pg_dump が無い場合）
#
# 実行例（FishTrack EC2 上）:
#   export SOURCE_DATABASE_URL="postgresql://user:pass@shared-db.xxx.rds.amazonaws.com:5432/shared_db"
#   export TARGET_DB_NAME="fishtrack_db"  # 省略時は fishtrack_db
#   ./run_migrate_fishtrack_rds_ec2.sh
#
# SOURCE_DATABASE_URL は FishTrack EC2 の .env から取得、または GitHub Secrets 経由で設定

set -e

if [ -z "$SOURCE_DATABASE_URL" ]; then
  echo "Error: SOURCE_DATABASE_URL is required." >&2
  echo "  export SOURCE_DATABASE_URL=\"postgresql://user:pass@host:5432/shared_db\"" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="${TARGET_DB_NAME:-fishtrack_db}"

echo "Running migration via Docker postgres:16-alpine..."
docker run --rm \
  -e SOURCE_DATABASE_URL \
  -e "TARGET_DB_NAME=${TARGET}" \
  -v "${SCRIPT_DIR}:/scripts:ro" \
  postgres:16-alpine sh /scripts/run_migrate_fishtrack_rds_ec2_inner.sh

echo ""
echo "=== 次の作業: FishTrack の接続切替 ==="
echo "GitHub Secrets の FISHTRACK_DATABASE_URL を fishtrack_db 向けに更新し、再デプロイしてください。"
