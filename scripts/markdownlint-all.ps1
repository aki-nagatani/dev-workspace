# 全ワークスペースの Markdown 一括チェック・修正
# Usage: .\scripts\markdownlint-all.ps1 [-Fix]
#   -Fix を付けると --fix で自動修正を試行

param(
    [switch]$Fix
)

$ErrorActionPreference = "Stop"
$configPath = "$PSScriptRoot\..\.markdownlint.json"
$tempDir = "$PSScriptRoot\..\temp"
$reportPath = "$tempDir\markdownlint-report.txt"

# 対象ディレクトリ（node_modules は各所に .markdownlintignore を置くか、パス指定で回避）
# 注: FishTrack/MyPokedex/otayori-navi は node_modules を持つため、サブディレクトリは個別指定
$baseDir = (Resolve-Path "$PSScriptRoot\..").Path
$gitWork = "D:\OneDrive\git_work"
$obsidian = "D:\OneDrive\アプリ\remotely-save\Obsidian"

# 対象パス（node_modules/temp を除く。baseDir の代わりにサブディレクトリを個別指定）
$dirs = @(
    "$baseDir\.cursor\commands",
    "$baseDir\.cursor\rules",
    "$baseDir\migrations",
    "$baseDir\scripts",
    "$baseDir\.cursor\skills",
    "$baseDir\postgres-best-practices",
    "$baseDir\test-code-generator",
    "$gitWork\FishTrack\AGENTS.md",
    "$gitWork\FishTrack\README.md",
    "$gitWork\FishTrack\.cursor",
    "$gitWork\FishTrack\tests",
    "$gitWork\MyPokedex\AGENTS.md",
    "$gitWork\MyPokedex\README.md",
    "$gitWork\MyPokedex\.cursor",
    "$gitWork\MyPokedex\scripts",
    "$gitWork\MyPokedex\tests",
    "$gitWork\otayori-navi\README.md",
    "$gitWork\otayori-navi\scripts",
    "$gitWork\otayori-navi\infra",
    "$gitWork\otayori-navi\.cursor",
    "$baseDir\README.md",
    "$gitWork\personal-tools",
    $obsidian
)

# temp ディレクトリ作成
if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}

$fixArg = @()
if ($Fix) {
    $fixArg = @("--fix")
    Write-Host "Fix mode"
}

# カレントを dev-workspace に
$originalCwd = Get-Location
Set-Location "$PSScriptRoot\.."

# 存在するパスのみに絞る
$dirs = $dirs | Where-Object { Test-Path $_ }

try {
    & npx markdownlint-cli -c $configPath -o $reportPath @fixArg @dirs 2>$null
    $exitCode = $LASTEXITCODE
}
finally {
    Set-Location $originalCwd
}

# レポート読み込み
$result = @()
if (Test-Path $reportPath) {
    $result = Get-Content $reportPath -Encoding utf8
}
Write-Host "Report: $reportPath"

if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "Errors found (exit: $exitCode):"
    $result | Select-Object -First 50
    if (($result | Measure-Object -Line).Lines -gt 50) {
        Write-Host "... see $reportPath"
    }
}
else {
    Write-Host "No errors"
}

exit $exitCode
