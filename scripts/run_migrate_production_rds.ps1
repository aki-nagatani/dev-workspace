# 1RDS 3DB Phase 1: 本番RDS で on_* を otayori_navi DB へ移行
#
# 前提:
#   - AWS CLI が設定済み（aws secretsmanager にアクセス可能）
#   - psql/pg_dump が PATH にある、または Docker が利用可能
#   - Secrets Manager otayori/db-url が shared_db を指している
#
# 実行: cd d:\OneDrive\git_work\dev-workspace
#       .\scripts\run_migrate_production_rds.ps1

$ErrorActionPreference = "Stop"

$secretId = "otayori/db-url"
$region = "ap-northeast-1"

Write-Host "Fetching SOURCE_DATABASE_URL from Secrets Manager ($secretId)..."
try {
    $secretValue = aws secretsmanager get-secret-value --secret-id $secretId --region $region --query SecretString --output text 2>$null
    if (-not $secretValue) {
        throw "Failed to get secret value"
    }
} catch {
    Write-Error "Secrets Manager から取得できません。aws configure とシークレット名を確認してください。: $_"
}

# SQLAlchemy形式 (postgresql+psycopg://) の場合は postgresql:// に変換
$sourceUrl = $secretValue -replace "^postgresql\+psycopg://", "postgresql://"

# shared_db を指しているか簡易確認
if ($sourceUrl -notmatch "shared_db") {
    Write-Warning "SOURCE_DATABASE_URL が shared_db を指していない可能性があります: $($sourceUrl -replace ':.*@', ':****@')"
    $confirm = Read-Host "続行しますか? (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        exit 1
    }
}

# URL をパース（postgresql://user:pass@host:port/dbname）
$urlNoScheme = $sourceUrl -replace "^postgresql://", ""
$authRest = $urlNoScheme -split "@", 2
$userPass = $authRest[0] -split ":", 2
$pgUser = $userPass[0]
$pgPassword = if ($userPass.Length -gt 1) { $userPass[1] } else { "" }
$hostDb = $authRest[1] -split "/", 2
$hostPort = $hostDb[0] -split ":", 2
$pgHost = $hostPort[0]
$pgPort = if ($hostPort.Length -gt 1) { $hostPort[1] } else { "5432" }
$pgDatabase = if ($hostDb.Length -gt 1) { $hostDb[1] -replace "\?.*", "" } else { "shared_db" }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Split-Path -Parent $scriptDir

function Show-NextSteps {
    param($newUrl, $newUrlSqlAlchemy)
    Write-Host ""
    Write-Host "=== 次の作業: Secrets Manager 更新 ===" -ForegroundColor Cyan
    Write-Host "以下で otayori/db-url を更新してください:"
    Write-Host ""
    Write-Host "  aws secretsmanager put-secret-value --secret-id `"$secretId`" --region $region --secret-string `"$newUrlSqlAlchemy`""
    Write-Host ""
    Write-Host "更新後、おたよりナビを再デプロイ/再起動して動作確認してください"
}

# psql が使える場合は Python スクリプト、否則 Docker を使用
$useDocker = $false
try {
    $null = Get-Command psql -ErrorAction Stop
} catch {
    $useDocker = $true
}

if ($useDocker) {
    Write-Host "psql が PATH にないため、Docker で実行します..."
    $tempScript = Join-Path $workspaceRoot "temp\migrate_docker.sh"
    $tempDir = Split-Path $tempScript
    if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir -Force | Out-Null }
    $scriptContent = @'
#!/bin/sh
TARGET=otayori_navi
echo Creating database $TARGET...
exists=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = 'otayori_navi'" 2>/dev/null || true)
if [ "$exists" != "1" ]; then psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d postgres -c "CREATE DATABASE $TARGET"; else echo Database $TARGET already exists.; fi
echo Dumping on_* tables...
pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" --no-owner --no-acl -t on_families -t on_children -t on_users -t on_family_invites -t on_documents | psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$TARGET" -q
echo Stamping alembic_version...
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$TARGET" -c "CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY); DELETE FROM alembic_version; INSERT INTO alembic_version (version_num) VALUES ('20260209140000');"
echo Done.
'@
    [System.IO.File]::WriteAllText($tempScript, $scriptContent.Replace("`r`n", "`n").Replace("`r", "`n"), [System.Text.UTF8Encoding]::new($false))
    docker run --rm `
        -e PGHOST=$pgHost -e PGPORT=$pgPort -e PGUSER=$pgUser -e PGPASSWORD=$pgPassword -e PGDATABASE=$pgDatabase `
        -v "${workspaceRoot}/temp:/scripts:ro" `
        postgres:16-alpine sh /scripts/migrate_docker.sh
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $newUrl = $sourceUrl -replace "shared_db", "otayori_navi"
    $newUrlSqlAlchemy = $newUrl -replace "^postgresql://", "postgresql+psycopg://"
    Show-NextSteps $newUrl $newUrlSqlAlchemy
} else {
    Write-Host "Running migrate script..."
    $env:SOURCE_DATABASE_URL = $sourceUrl
    Push-Location $workspaceRoot
    try {
        python scripts/migrate_on_tables_to_otayori_navi_db.py
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        $newUrl = $sourceUrl -replace "shared_db", "otayori_navi"
        $newUrlSqlAlchemy = $newUrl -replace "^postgresql://", "postgresql+psycopg://"
        Show-NextSteps $newUrl $newUrlSqlAlchemy
    } finally {
        Pop-Location
    }
}
