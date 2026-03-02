#!/bin/sh
# 1RDS 3DB Phase 2b: EC2 上で RDS の MyPokedex テーブルを mypokedex_db へ移行
# Docker postgres イメージ使用（EC2 に psql/pg_dump が無い場合）
#
# 実行例（MyPokedex EC2 または FishTrack EC2 上）:
#   export SOURCE_DATABASE_URL="postgresql://user:pass@shared-db.xxx.rds.amazonaws.com:5432/shared_db"
#   export TARGET_DB_NAME="mypokedex_db"  # 省略時は mypokedex_db
#   ./run_migrate_mypokedex_rds_ec2.sh
#
# 実行後、alembic_version の修正が必要（手順書 5.2 参照）

set -e

if [ -z "$SOURCE_DATABASE_URL" ]; then
  echo "Error: SOURCE_DATABASE_URL is required." >&2
  echo "  export SOURCE_DATABASE_URL=\"postgresql://user:pass@host:5432/shared_db\"" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="${TARGET_DB_NAME:-mypokedex_db}"

echo "Running migration via Docker postgres:16-alpine..."
docker run --rm \
  -e SOURCE_DATABASE_URL \
  -e "TARGET_DB_NAME=${TARGET}" \
  -v "${SCRIPT_DIR}:/scripts:ro" \
  postgres:16-alpine sh /scripts/run_migrate_mypokedex_rds_ec2_inner.sh

echo ""
echo "=== 次の作業: alembic_version 修正・MyPokedex 接続切替 ==="
echo "mypokedex_db で UPDATE alembic_version SET version_num = '20260209150000' WHERE version_num = '20260227100000'; を実行"
echo "GitHub Secrets の MYPOKEDEX_DATABASE_URL を mypokedex_db 向けに更新し、再デプロイしてください。"
