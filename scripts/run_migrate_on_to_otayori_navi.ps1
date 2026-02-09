# 1RDS 3DB Phase 1: ローカルDockerで on_* を otayori_navi DB へ移行
# dev-workspace の shared-db コンテナ内で pg_dump / psql を実行する
#
# 実行前: cd d:\OneDrive\git_work\dev-workspace
#         docker compose --profile local up -d

$ErrorActionPreference = "Stop"

$containers = docker ps --filter "name=shared-db" --format "{{.Names}}"
if (-not $containers) {
    Write-Error "shared-db コンテナが見つかりません。dev-workspace で 'docker compose --profile local up -d' を実行してください。"
}
$containerName = ($containers -split "`n")[0].Trim()

$env:PGPASSWORD = "shared_password"

Write-Host "Creating database otayori_navi..."
$exists = docker exec $containerName psql -U shared_user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = 'otayori_navi'" 2>$null
if ($exists.Trim() -ne "1") {
    docker exec $containerName psql -U shared_user -d postgres -c "CREATE DATABASE otayori_navi"
} else {
    Write-Host "Database otayori_navi already exists."
}

Write-Host "Dumping and restoring on_* tables..."
docker exec $containerName sh -c "pg_dump -U shared_user -d shared_db --no-owner --no-acl -t on_families -t on_children -t on_users -t on_family_invites -t on_documents | psql -U shared_user -d otayori_navi -q"
if ($LASTEXITCODE -ne 0) {
    Write-Error "pg_dump/restore failed."
}

Write-Host "Stamping alembic_version..."
$stampSql = "CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY); DELETE FROM alembic_version; INSERT INTO alembic_version (version_num) VALUES ('20260209140000');"
docker exec $containerName psql -U shared_user -d otayori_navi -c $stampSql

Write-Host "Migration completed. Tables migrated to otayori_navi."
