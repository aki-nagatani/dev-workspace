# マイグレーション状態を確認するスクリプト（ローカル環境用）

$ErrorActionPreference = "Stop"

Write-Host "=========================================="
Write-Host "マイグレーション状態確認"
Write-Host "=========================================="
Write-Host ""

# dev-workspaceの統合マイグレーション
Write-Host "=== dev-workspace 統合マイグレーション ==="
Push-Location "D:\OneDrive\git_work\dev-workspace"
Write-Host "現在のマイグレーション状態:"
alembic current
Write-Host ""
Write-Host "マイグレーション履歴:"
alembic history --verbose | Select-Object -First 20
Write-Host ""
Pop-Location

# FishTrackのマイグレーション
Write-Host "=== FishTrack マイグレーション ==="
Push-Location "D:\OneDrive\git_work\FishTrack"
if (Test-Path "alembic.ini") {
    Write-Host "現在のマイグレーション状態:"
    alembic current
    Write-Host ""
    Write-Host "マイグレーション履歴:"
    alembic history --verbose | Select-Object -First 20
    Write-Host ""
}
Pop-Location

# MyPokedexのマイグレーション
Write-Host "=== MyPokedex マイグレーション ==="
Push-Location "D:\OneDrive\git_work\MyPokedex"
if (Test-Path "alembic.ini") {
    Write-Host "現在のマイグレーション状態:"
    alembic current
    Write-Host ""
    Write-Host "マイグレーション履歴:"
    alembic history --verbose | Select-Object -First 20
    Write-Host ""
}
Pop-Location

Write-Host "=========================================="
Write-Host "確認完了"
Write-Host "=========================================="

