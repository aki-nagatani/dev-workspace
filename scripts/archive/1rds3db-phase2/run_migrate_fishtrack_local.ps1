# 1RDS 3DB Phase 2a: ローカルDocker で FishTrack を fishtrack_db へ移行（アーカイブ）
# 実行: cd d:\OneDrive\git_work\dev-workspace
#       .\scripts\archive\1rds3db-phase2\run_migrate_fishtrack_local.ps1

$ErrorActionPreference = "Stop"

$sourceUrl = "postgresql://shared_user:shared_password@localhost:5434/shared_db"
$targetDb = "fishtrack_db"
# archive/1rds3db-phase2 から dev-workspace ルートへ（3階層上）
$workspaceRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)))

# psql が使えるか確認
$useDocker = $false
try {
    $null = Get-Command psql -ErrorAction Stop
} catch {
    $useDocker = $true
}

if ($useDocker) {
    Write-Host "psql が PATH にないため、Docker で実行します..."
    $tempDir = Join-Path $workspaceRoot "temp"
    if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir -Force | Out-Null }
    $tempScript = Join-Path $tempDir "migrate_fishtrack_docker.sh"

    # migrate_fishtrack_tables_to_fishtrack_db.py と一致（reel_holding は移行対象外）
    $tables = @(
        "manufacturer", "reel_model", "rod_model", "rod_series", "reel_series",
        "fishtrack_user", "rod_holding", "field", "rental_boat_shop",
        "water_level_history", "tackle_spec_import_log", "ops_monitoring", "ops_job_log",
        "user_statistics_daily", "user_statistics_weekly", "alembic_version"
    )
    $tableArgs = ($tables | ForEach-Object { "-t $_" }) -join " "

    $scriptContent = @"
#!/bin/sh
set -e
TARGET=$targetDb
echo Creating database `$TARGET...
exists=`$(psql -h "`$PGHOST" -p "`$PGPORT" -U "`$PGUSER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$targetDb'" 2>/dev/null || true)
if [ "`$exists" != "1" ]; then
  psql -h "`$PGHOST" -p "`$PGPORT" -U "`$PGUSER" -d postgres -c "CREATE DATABASE `$TARGET"
else
  echo Database `$TARGET already exists.
fi
echo Dumping FishTrack tables...
pg_dump -h "`$PGHOST" -p "`$PGPORT" -U "`$PGUSER" -d "`$PGDATABASE" --no-owner --no-acl $tableArgs | psql -h "`$PGHOST" -p "`$PGPORT" -U "`$PGUSER" -d "`$TARGET" -q
echo Done.
"@

    [System.IO.File]::WriteAllText($tempScript, $scriptContent.Replace("`r`n", "`n").Replace("`r", "`n"), [System.Text.UTF8Encoding]::new($false))

    # host.docker.internal でホストの localhost:5434 に接続
    docker run --rm `
        -e PGHOST=host.docker.internal `
        -e PGPORT=5434 `
        -e PGUSER=shared_user `
        -e PGPASSWORD=shared_password `
        -e PGDATABASE=shared_db `
        -v "${tempDir}:/scripts:ro" `
        postgres:16-alpine sh /scripts/migrate_fishtrack_docker.sh

    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host ""
    Write-Host "=== 次の作業: FishTrack の接続切替 ===" -ForegroundColor Cyan
    Write-Host "環境変数を以下に変更してください:"
    Write-Host "  FISHTRACK_DATABASE_URL=postgresql://shared_user:shared_password@localhost:5434/fishtrack_db"
    Write-Host ""
} else {
    Write-Host "Running migrate script..."
    $env:SOURCE_DATABASE_URL = $sourceUrl
    $env:TARGET_DB_NAME = $targetDb
    Push-Location $workspaceRoot
    try {
        python scripts/archive/1rds3db-phase2/migrate_fishtrack_tables_to_fishtrack_db.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Write-Host ""
        Write-Host "=== 次の作業: FishTrack の接続切替 ===" -ForegroundColor Cyan
        Write-Host "環境変数を以下に変更してください:"
        Write-Host "  FISHTRACK_DATABASE_URL=postgresql://shared_user:shared_password@localhost:5434/fishtrack_db"
        Write-Host ""
    } finally {
        Pop-Location
    }
}
