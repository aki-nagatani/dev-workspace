#!/bin/sh
# 1RDS 3DB Phase 2a: shared_db vs fishtrack_db の件数比較（整合性確認）（アーカイブ）
# 実行例（FishTrack EC2 上）:
#   export SOURCE_DATABASE_URL="postgresql://user:pass@host:5432/shared_db"
#   ./run_verify_fishtrack_rds_ec2.sh

set -e

if [ -z "$SOURCE_DATABASE_URL" ]; then
  echo "Error: SOURCE_DATABASE_URL is required." >&2
  exit 1
fi

SOURCE_BASE="${SOURCE_DATABASE_URL%/*}"
TARGET_URL="${SOURCE_BASE}/fishtrack_db"
export SOURCE_DATABASE_URL TARGET_URL

if [ -z "$TARGET_URL" ]; then
  echo "ERROR: TARGET_URL is empty. SOURCE_DATABASE_URL=$SOURCE_DATABASE_URL" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

docker run --rm -v "${SCRIPT_DIR}:/scripts:ro" \
  -e SOURCE_DATABASE_URL -e TARGET_URL \
  postgres:16-alpine sh -c '
    echo "=== shared_db counts ==="
    psql "$SOURCE_DATABASE_URL" -t -A -f /scripts/verify_fishtrack.sql
    echo ""
    echo "=== fishtrack_db counts ==="
    psql "$TARGET_URL" -t -A -f /scripts/verify_fishtrack.sql
    echo ""
    echo "=== diff (empty=OK) ==="
    psql "$SOURCE_DATABASE_URL" -t -A -f /scripts/verify_fishtrack.sql > /tmp/shared.txt
    psql "$TARGET_URL" -t -A -f /scripts/verify_fishtrack.sql > /tmp/fish.txt
    if diff /tmp/shared.txt /tmp/fish.txt; then
      echo "OK: shared_db and fishtrack_db have identical row counts."
    else
      echo "WARNING: Difference detected. Review counts above."
      exit 1
    fi
  '
