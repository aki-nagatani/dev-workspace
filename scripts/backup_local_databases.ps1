# ローカル環境のデータベースバックアップスクリプト
# FishTrackとMyPokedexのローカルDockerデータベースをバックアップ

$ErrorActionPreference = "Stop"

# バックアップディレクトリの作成
$BackupDir = "backups"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

# タイムスタンプ
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=========================================="
Write-Host "ローカル環境データベースバックアップ"
Write-Host "=========================================="
Write-Host ""

# FishTrackローカルDBのバックアップ
Write-Host "FishTrackローカルDBのバックアップを開始..."
$FishTrackBackupFile = "$BackupDir\fishtrack_local_backup_${Timestamp}.dump"

# Dockerコンテナ名を確認
$FishTrackContainer = docker ps --filter "name=fishtrack-db" --format "{{.Names}}" | Select-Object -First 1
if (-not $FishTrackContainer) {
    Write-Host "⚠️ FishTrack DBコンテナが見つかりません。コンテナが起動しているか確認してください。"
}
else {
    Write-Host "コンテナ: $FishTrackContainer"
    docker exec $FishTrackContainer pg_dump -U fishtrack -d fishtrack_db -F c -f /tmp/fishtrack_backup.dump
    
    if ($LASTEXITCODE -eq 0) {
        docker cp "${FishTrackContainer}:/tmp/fishtrack_backup.dump" $FishTrackBackupFile
        docker exec $FishTrackContainer rm /tmp/fishtrack_backup.dump
        
        $FishTrackSize = (Get-Item $FishTrackBackupFile).Length / 1MB
        $FishTrackSizeMB = [math]::Round($FishTrackSize, 2)
        Write-Host "✅ FishTrackバックアップ完了: $FishTrackBackupFile ($FishTrackSizeMB MB)"
    }
    else {
        Write-Host "❌ FishTrackバックアップに失敗しました"
        exit 1
    }
}

Write-Host ""

# MyPokedexローカルDBのバックアップ
Write-Host "MyPokedexローカルDBのバックアップを開始..."
$MyPokedexBackupFile = "$BackupDir\mypokedex_local_backup_${Timestamp}.dump"

# Dockerコンテナ名を確認
$MyPokedexContainer = docker ps --filter "name=mypokedex-db" --format "{{.Names}}" | Select-Object -First 1
if (-not $MyPokedexContainer) {
    Write-Host "⚠️ MyPokedex DBコンテナが見つかりません。コンテナが起動しているか確認してください。"
}
else {
    Write-Host "コンテナ: $MyPokedexContainer"
    docker exec $MyPokedexContainer pg_dump -U mypokedex -d mypokedex_db -F c -f /tmp/mypokedex_backup.dump
    
    if ($LASTEXITCODE -eq 0) {
        docker cp "${MyPokedexContainer}:/tmp/mypokedex_backup.dump" $MyPokedexBackupFile
        docker exec $MyPokedexContainer rm /tmp/mypokedex_backup.dump
        
        $MyPokedexSize = (Get-Item $MyPokedexBackupFile).Length / 1MB
        $MyPokedexSizeMB = [math]::Round($MyPokedexSize, 2)
        Write-Host "✅ MyPokedexバックアップ完了: $MyPokedexBackupFile ($MyPokedexSizeMB MB)"
    }
    else {
        Write-Host "❌ MyPokedexバックアップに失敗しました"
        exit 1
    }
}

Write-Host ""
Write-Host "=========================================="
Write-Host "バックアップ完了"
Write-Host "=========================================="
Write-Host "FishTrack: $FishTrackBackupFile"
Write-Host "MyPokedex: $MyPokedexBackupFile"
Write-Host "=========================================="

