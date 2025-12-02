param (
    [string]$PiHost = "raspberrypi.local",
    [string]$PiUser = "pi"
)

$ErrorActionPreference = "Stop"

# Configuration
$FishTrackEc2Host = "52.197.69.195"
$FishTrackEc2Key = "$env:USERPROFILE\.ssh\fishtrack_ec2_key"
$MyPokedexEc2Host = "18.179.162.82"
$MyPokedexEc2Key = "$env:USERPROFILE\.ssh\mypokedex_ec2_key"

# Temp directory setup (using dev-workspace/temp)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$TempDir = Join-Path $ScriptDir "..\temp\migration"
if (!(Test-Path $TempDir)) { New-Item -ItemType Directory -Force -Path $TempDir | Out-Null }

Write-Host "--- Starting Production Data Migration ---" -ForegroundColor Cyan
Write-Host "Target Pi: $PiUser@$PiHost"
Write-Host "Local Temp Dir: $TempDir"

# 1. Download from Raspberry Pi
Write-Host "`n[1/4] Downloading data from Raspberry Pi..." -ForegroundColor Yellow

# FishTrack
Write-Host "  Downloading FishTrack DB from $PiHost..."
try {
    scp "${PiUser}@${PiHost}:/home/pi/FishTrack/data/fishtrack.db" "$TempDir\fishtrack.db"
    if ($LASTEXITCODE -ne 0) { throw "SCP failed" }
    Write-Host "  FishTrack DB downloaded." -ForegroundColor Green
}
catch {
    Write-Error "Failed to download FishTrack DB. Please check Pi IP/User and ensure SSH is enabled."
    exit 1
}

# MyPokedex
Write-Host "  Downloading MyPokedex DB from $PiHost..."
try {
    scp "${PiUser}@${PiHost}:/home/pi/MyPokedex/data/mypokedex.db" "$TempDir\mypokedex.db"
    if ($LASTEXITCODE -ne 0) { throw "SCP failed" }
    Write-Host "  MyPokedex DB downloaded." -ForegroundColor Green
}
catch {
    Write-Error "Failed to download MyPokedex DB."
    exit 1
}

# 2. Upload to EC2
Write-Host "`n[2/4] Uploading data to EC2..." -ForegroundColor Yellow

# FishTrack
Write-Host "  Uploading to FishTrack EC2 ($FishTrackEc2Host)..."
scp -o StrictHostKeyChecking=no -i $FishTrackEc2Key "$TempDir\fishtrack.db" "ec2-user@${FishTrackEc2Host}:/home/ec2-user/fishtrack_import.db"
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to upload to FishTrack EC2"; exit 1 }

# MyPokedex
Write-Host "  Uploading to MyPokedex EC2 ($MyPokedexEc2Host)..."
scp -o StrictHostKeyChecking=no -i $MyPokedexEc2Key "$TempDir\mypokedex.db" "ec2-user@${MyPokedexEc2Host}:/home/ec2-user/mypokedex_import.db"
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to upload to MyPokedex EC2"; exit 1 }

# NEW: Upload fixed migration script to MyPokedex EC2
Write-Host "  Uploading fixed migration script to MyPokedex EC2..."
$LocalMyPokedexScriptPath = Join-Path $ScriptDir "..\..\MyPokedex\scripts\migrate_to_postgres.py"
if (!(Test-Path $LocalMyPokedexScriptPath)) { Write-Error "Migration script not found at $LocalMyPokedexScriptPath"; exit 1 }
scp -o StrictHostKeyChecking=no -i $MyPokedexEc2Key $LocalMyPokedexScriptPath "ec2-user@${MyPokedexEc2Host}:/home/ec2-user/migrate_to_postgres.py"
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to upload migration script to MyPokedex EC2"; exit 1 }

# 3. Execute Migration on FishTrack EC2
Write-Host "`n[3/4] Running Migration on FishTrack EC2..." -ForegroundColor Yellow
$FishTrackCmd = "cd /home/ec2-user/FishTrack; docker compose run --rm -v /home/ec2-user/fishtrack_import.db:/tmp/import.db -e SQLITE_DB_PATH=/tmp/import.db app python scripts/migrate_to_postgres.py"
ssh -o StrictHostKeyChecking=no -i $FishTrackEc2Key "ec2-user@${FishTrackEc2Host}" $FishTrackCmd
if ($LASTEXITCODE -ne 0) { Write-Error "Migration failed on FishTrack EC2"; exit 1 }

# 4. Execute Migration on MyPokedex EC2
Write-Host "`n[4/4] Running Migration on MyPokedex EC2..." -ForegroundColor Yellow
# Mount the uploaded script to overwrite the one in the container
$MyPokedexCmd = "cd /home/ec2-user/MyPokedex; docker compose run --rm -v /home/ec2-user/mypokedex_import.db:/tmp/import.db -v /home/ec2-user/migrate_to_postgres.py:/app/scripts/migrate_to_postgres.py -e MYPDEX_SQLITE_PATH=/tmp/import.db app python scripts/migrate_to_postgres.py"
ssh -o StrictHostKeyChecking=no -i $MyPokedexEc2Key "ec2-user@${MyPokedexEc2Host}" $MyPokedexCmd
if ($LASTEXITCODE -ne 0) { Write-Error "Migration failed on MyPokedex EC2"; exit 1 }

Write-Host "`n✅ Migration Completed Successfully!" -ForegroundColor Green
Write-Host "Note: Ensure to check the applications to verify data presence."
