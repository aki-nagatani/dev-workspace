#!/bin/sh
# 1RDS 3DB Phase 1: Docker 内で pg_dump/psql により on_* を otayori_navi へ移行
# 環境変数: PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE (shared_db), TARGET_DB_NAME (otayori_navi)

set -e
TARGET="${TARGET_DB_NAME:-otayori_navi}"

echo "Creating database $TARGET..."
exists=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$TARGET'" 2>/dev/null || true)
if [ "$exists" != "1" ]; then
  psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "CREATE DATABASE $TARGET"
else
  echo "Database $TARGET already exists."
fi

echo "Dumping on_* tables from $PGDATABASE..."
pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" \
  --no-owner --no-acl \
  -t on_families -t on_children -t on_users -t on_family_invites -t on_documents \
  | psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$TARGET" -q

echo "Stamping alembic_version..."
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$TARGET" -c "
  CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY);
  DELETE FROM alembic_version;
  INSERT INTO alembic_version (version_num) VALUES ('20260209140000');
"

echo "Done. Tables migrated to $TARGET."
