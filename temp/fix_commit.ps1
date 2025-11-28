$files = @(
    "docs/guidelines/MCP_SERVERS.md",
    "docs/plans/completed/Slack_Webhook_MCPサーバー導入計画.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -Encoding UTF8
        $content = $content -replace 'https://hooks\.slack\.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX', '取得したURLは環境変数で管理（形式: `https://hooks.slack.com/services/...`）'
        Set-Content $file -Value $content -Encoding UTF8 -NoNewline
    }
}

