#!/bin/bash
# 1RDS 3DB Phase 1: EC2 上で本番 RDS の on_* を otayori_navi へ移行
# Secrets Manager から URL 取得し、Docker 内で pg_dump/psql を実行
set -e

SECRET_ID="otayori/db-url"
REGION="ap-northeast-1"

echo "Fetching SOURCE_DATABASE_URL from Secrets Manager..."
URL=$(aws secretsmanager get-secret-value --secret-id "$SECRET_ID" --region "$REGION" --query SecretString --output text)
URL="${URL/postgresql+psycopg:\/\//postgresql:\/\/}"

# Parse URL: postgresql://user:pass@host:port/dbname
if [[ ! "$URL" =~ postgresql://([^:]+):([^@]+)@([^:]+):([0-9]+)/(.+) ]]; then
  echo "Error: Invalid database URL format"
  exit 1
fi

PGUSER="${BASH_REMATCH[1]}"
PGPASSWORD="${BASH_REMATCH[2]}"
PGHOST="${BASH_REMATCH[3]}"
PGPORT="${BASH_REMATCH[4]}"
PGDATABASE="${BASH_REMATCH[5]}"

if [[ "$PGDATABASE" != "shared_db" ]]; then
  echo "Warning: PGDATABASE is $PGDATABASE, expected shared_db. Continue? (y/N)"
  read -r confirm
  [[ "$confirm" != "y" && "$confirm" != "Y" ]] && exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Running migration via Docker..."
docker run --rm \
  -e PGHOST="$PGHOST" -e PGPORT="$PGPORT" -e PGUSER="$PGUSER" -e PGPASSWORD="$PGPASSWORD" -e PGDATABASE="$PGDATABASE" \
  -v "$SCRIPT_DIR:/scripts:ro" \
  postgres:16-alpine sh /scripts/migrate_via_docker.sh

NEW_URL="${URL/shared_db/otayori_navi}"
NEW_URL="${NEW_URL/postgresql:\/\//postgresql+psycopg:\/\/}"

echo ""
echo "=== Migration completed ==="
echo "Next: Update Secrets Manager otayori/db-url to:"
echo "  $NEW_URL"
echo ""
echo "Then redeploy/restart otayori-navi."
