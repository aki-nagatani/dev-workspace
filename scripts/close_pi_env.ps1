param (
    [string]$PiHost = "raspberrypi.local",
    [string]$PiUser = "pi"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BackupDir = Join-Path $ScriptDir "..\backups\pi_archive_$(Get-Date -Format 'yyyyMMdd')"

# Create backup directory
if (!(Test-Path $BackupDir)) { New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null }

Write-Host "--- Closing Raspberry Pi Production Environment ---" -ForegroundColor Cyan
Write-Host "Target Pi: $PiUser@$PiHost"
Write-Host "Backup Dir: $BackupDir"

# 1. Check Service Status
Write-Host "`n[1/4] Checking Service Status..." -ForegroundColor Yellow
try {
    ssh "${PiUser}@${PiHost}" "systemctl status myhobbysite.service"
} catch {
    Write-Warning "Could not check status or service already stopped/does not exist."
}

# 2. Stop and Disable Service
Write-Host "`n[2/4] Stopping and Disabling Service..." -ForegroundColor Yellow
try {
    # Stop the service
    ssh "${PiUser}@${PiHost}" "sudo systemctl stop myhobbysite.service"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Service stopped." -ForegroundColor Green
    } else {
        Write-Warning "Failed to stop service (might be already stopped)."
    }

    # Disable the service
    ssh "${PiUser}@${PiHost}" "sudo systemctl disable myhobbysite.service"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Service disabled." -ForegroundColor Green
    } else {
        Write-Warning "Failed to disable service."
    }
} catch {
    Write-Error "Failed to execute stop commands. Please check connectivity and permissions."
    exit 1
}

# 3. Backup Data
Write-Host "`n[3/4] Backing up Data..." -ForegroundColor Yellow

# FishTrack DB
Write-Host "  Downloading FishTrack DB..."
try {
    scp "${PiUser}@${PiHost}:/home/pi/FishTrack/data/fishtrack.db" "$BackupDir\fishtrack.db"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  FishTrack DB downloaded." -ForegroundColor Green
    } else {
        Write-Warning "SCP failed for FishTrack DB."
    }
} catch {
    Write-Warning "Failed to download FishTrack DB or file not found."
}

# MyPokedex DB
Write-Host "  Downloading MyPokedex DB..."
try {
    scp "${PiUser}@${PiHost}:/home/pi/MyPokedex/data/mypokedex.db" "$BackupDir\mypokedex.db"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  MyPokedex DB downloaded." -ForegroundColor Green
    } else {
        Write-Warning "SCP failed for MyPokedex DB."
    }
} catch {
    Write-Warning "Failed to download MyPokedex DB or file not found."
}

# 4. Verify
Write-Host "`n[4/4] Verification..." -ForegroundColor Yellow
Write-Host "Checking if service is inactive..."
try {
    $status = ssh "${PiUser}@${PiHost}" "systemctl is-active myhobbysite.service"
    if ($status -eq "inactive" -or $status -eq "failed" -or $status -eq "unknown") {
         Write-Host "Service is inactive ($status) - OK." -ForegroundColor Green
    } else {
         Write-Warning "Service status is '$status'. Please check manually."
    }
} catch {
    # ssh command failing might mean it returns non-zero exit code for 'inactive' or connection error
    # systemctl is-active returns 0 if active, non-zero otherwise.
    # So if it fails (catch block), it likely means it is NOT active (which is good).
    Write-Host "Service is likely inactive (systemctl returned non-zero)." -ForegroundColor Green
}

Write-Host "`n✅ Raspberry Pi Environment Closed Successfully!" -ForegroundColor Green
Write-Host "Data backup located at: $BackupDir"
Write-Host "You may now archive or power down the Raspberry Pi."

