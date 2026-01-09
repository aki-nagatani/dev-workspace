# PSScriptAnalyzer settings
# このファイルはPowerShellの構文要件により、else/catchを}と同じ行に配置する必要があります

# PowerShell用: 本番環境デプロイ状況確認スクリプト

Write-Host "=========================================="
Write-Host "本番環境デプロイ状況確認（PowerShell）"
Write-Host "=========================================="
Write-Host ""

# SSH鍵ファイルの確認
Write-Host "=== SSH鍵ファイルの確認 ==="
$sshKeyPath = "$env:USERPROFILE\.ssh\mypokedex-ec2-key.pem"
if (Test-Path $sshKeyPath) {
    Write-Host "OK: SSH鍵ファイルが見つかりました: $sshKeyPath"
    $fileInfo = Get-Item $sshKeyPath
    Write-Host "   ファイルサイズ: $($fileInfo.Length) bytes"
    Write-Host "   最終更新日時: $($fileInfo.LastWriteTime)"
}
else {
    Write-Host "NG: SSH鍵ファイルが見つかりません: $sshKeyPath"
    Write-Host "   他の場所を確認してください:"
    Write-Host "   - $env:USERPROFILE\.ssh\"
    Write-Host "   - ダウンロードフォルダ"
    Write-Host "   - プロジェクトディレクトリ"
}

Write-Host ""

# ネットワーク接続の確認
Write-Host "=== ネットワーク接続の確認 ==="
$targetIP = "54.249.50.253"
Write-Host "接続先: $targetIP"
Write-Host ""

# Pingテスト
Write-Host "Pingテストを実行中..."
$pingResult = Test-Connection -ComputerName $targetIP -Count 2 -Quiet
if ($pingResult) {
    Write-Host "OK: Ping成功: $targetIP に到達可能"
}
else {
    Write-Host "NG: Ping失敗: $targetIP に到達できません"
}

Write-Host ""

# SSH接続のテスト（ポート22）
Write-Host "=== SSH接続テスト（ポート22） ==="
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $connect = $tcpClient.BeginConnect($targetIP, 22, $null, $null)
    $wait = $connect.AsyncWaitHandle.WaitOne(3000, $false)
    
    if ($wait) {
        $tcpClient.EndConnect($connect)
        Write-Host "OK: ポート22への接続成功"
        $tcpClient.Close()
    }
    else {
        Write-Host "NG: ポート22への接続タイムアウト"
        $tcpClient.Close()
    }
}
catch {
    Write-Host "NG: ポート22への接続エラー: $_"
}

Write-Host ""

# SSH接続コマンドの表示
Write-Host "=== SSH接続コマンド ==="
if (Test-Path $sshKeyPath) {
    Write-Host "以下のコマンドでSSH接続を試行してください:"
    Write-Host ""
    $sshCmd = "ssh -i `"$sshKeyPath`" ec2-user@$targetIP"
    Write-Host $sshCmd
    Write-Host ""
    Write-Host "詳細なデバッグ情報を有効にする場合:"
    $sshCmdVerbose = "ssh -v -i `"$sshKeyPath`" ec2-user@$targetIP"
    Write-Host $sshCmdVerbose
}
else {
    Write-Host "SSH鍵ファイルが見つからないため、接続コマンドを表示できません。"
    Write-Host "まず、SSH鍵ファイルの場所を確認してください。"
}

Write-Host ""

# AWS Systems Manager Session Managerの確認
Write-Host "=== AWS Systems Manager Session Manager ==="
Write-Host "SSH接続ができない場合、以下のコマンドでSession Managerを使用できます:"
Write-Host ""
Write-Host "aws ssm start-session --target i-023a1623e48cabf1d --region ap-northeast-1"
Write-Host ""
Write-Host "接続後、以下のコマンドを実行:"
Write-Host "cd /home/ec2-user/MyPokedex"
Write-Host "docker compose --env-file .env exec app sh -c '"
Write-Host "  export SHARED_DATABASE_URL=`$MYPDEX_DATABASE_URL"
Write-Host "  export PYTHONPATH=/app/src:/app/../dev-workspace:/app/../FishTrack/src:/app/../MyPokedex/src"
Write-Host "  cd /app/../dev-workspace"
Write-Host "  python3 scripts/check_production_deployment.py"
Write-Host "'"
Write-Host ""

Write-Host "=========================================="
