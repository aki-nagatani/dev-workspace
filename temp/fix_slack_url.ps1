# Slack Webhook URL形式を修正するスクリプト
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
Set-Location $repoRoot

$files = @(
    "docs/guidelines/MCP_SERVERS.md",
    "docs/plans/completed/Slack_Webhook_MCPサーバー導入計画.md"
)

foreach ($file in $files) {
    $filePath = Join-Path $repoRoot $file
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw -Encoding UTF8
        $content = $content -replace 'https://hooks\.slack\.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX', '取得したURLは環境変数で管理（形式: `https://hooks.slack.com/services/...`）'
        Set-Content $filePath -Value $content -Encoding UTF8 -NoNewline
    }
}

