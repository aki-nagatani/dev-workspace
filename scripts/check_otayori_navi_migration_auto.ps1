# PowerShell用: おたよりナビ マイグレーション状態確認（自動実行版）

Write-Host "=========================================="
Write-Host "おたよりナビ マイグレーション状態確認（自動実行）"
Write-Host "=========================================="
Write-Host ""

$INSTANCE_ID = "i-001cd3b0db58d9f78"
$REGION = "ap-northeast-1"

# シンプルなコマンドに分割
$command1 = "cd /home/ec2-user/otayori-navi"
$command2 = "docker compose --env-file .env exec -T app sh -c 'export SHARED_DATABASE_URL=`$OTAYORI_NAVI_DATABASE_URL && python3 -c `"import os; from sqlalchemy import create_engine, text, inspect; db_url=os.getenv(\\`\"SHARED_DATABASE_URL\\`\"); engine=create_engine(db_url); conn=engine.connect(); result=conn.execute(text(\\`\"SELECT version_num FROM alembic_version ORDER BY version_num\\`\")); versions=[r[0] for r in result]; print(\\`\"=== Migration Status ===\\`\"); [print(f\\`\"  - { v }\\\`\") for v in versions]; print(\\`\"OK Applied\\`\" if \\`\"20260204001210\\`\" in versions else \\`\"NG NOT Applied\\`\"); inspector=inspect(engine); tables=[\\`\"families\\`\",\\`\"users\\`\",\\`\"family_invites\\`\",\\`\"documents\\`\"]; print(\\`\"\\n=== Table Existence ===\\`\"); [print(f\\`\" { \\`\"OK\\`\" if inspector.has_table(t) else \\`\"NG\\`\" } { t }\\\`\") for t in tables]; conn.close()`"'"

Write-Host "コマンドを送信しています..."
$commands = @($command1, $command2)
$params = @{
    commands = $commands
} | ConvertTo-Json

try {
    $result = aws ssm send-command --instance-ids $INSTANCE_ID --region $REGION --document-name "AWS-RunShellScript" --parameters $params --output json | ConvertFrom-Json
    $commandId = $result.Command.CommandId
    Write-Host "CommandId: $commandId"
    Write-Host ""
    Write-Host "コマンドの実行を待機しています（25秒）..."
    Start-Sleep -Seconds 25
    
    Write-Host ""
    Write-Host "結果を取得しています..."
    $invocation = aws ssm get-command-invocation --command-id $commandId --instance-id $INSTANCE_ID --region $REGION --output json | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "=== 実行結果 ==="
    Write-Host "Status: $($invocation.Status)"
    Write-Host ""
    
    if ($invocation.StandardOutputContent) {
        Write-Host "=== 標準出力 ==="
        Write-Host $invocation.StandardOutputContent
        Write-Host ""
    }
    
    if ($invocation.StandardErrorContent) {
        Write-Host "=== エラー出力 ==="
        Write-Host $invocation.StandardErrorContent
        Write-Host ""
    }
    
    if ($invocation.Status -eq "Success") {
        Write-Host "✅ コマンドが正常に完了しました"
    }
    else {
        Write-Host "❌ コマンドの実行に失敗しました"
    }
}
catch {
    Write-Host "❌ エラーが発生しました: $_"
    Write-Host ""
    Write-Host "手動で確認する場合は、以下のコマンドを実行してください:"
    Write-Host "aws ssm start-session --target $INSTANCE_ID --region $REGION"
}

Write-Host ""
Write-Host "=========================================="
Write-Host ""
Write-Host ""
