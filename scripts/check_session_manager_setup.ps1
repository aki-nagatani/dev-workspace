# Session Manager設定確認スクリプト

Write-Host "=========================================="
Write-Host "Session Manager設定確認"
Write-Host "=========================================="
Write-Host ""

$instanceId = "i-023a1623e48cabf1d"
$region = "ap-northeast-1"

Write-Host "=== EC2インスタンス情報 ==="
Write-Host "インスタンスID: $instanceId"
Write-Host "リージョン: $region"
Write-Host ""

# 1. インスタンスがManaged instancesに表示されるか確認
Write-Host "=== Managed instances確認 ==="
try {
    $instanceInfo = aws ssm describe-instance-information --region $region --filters "Key=InstanceIds,Values=$instanceId" --output json 2>&1
    if ($LASTEXITCODE -eq 0) {
        $info = $instanceInfo | ConvertFrom-Json
        if ($info.InstanceInformationList.Count -gt 0) {
            $inst = $info.InstanceInformationList[0]
            Write-Host "OK: インスタンスはManaged instancesに登録されています"
            Write-Host "   Ping状態: $($inst.PingStatus)"
            Write-Host "   最終Ping時刻: $($inst.LastPingDateTime)"
            Write-Host "   プラットフォーム: $($inst.PlatformType)"
        }
        else {
            Write-Host "NG: インスタンスがManaged instancesに登録されていません"
            Write-Host "   以下を確認してください:"
            Write-Host "   1. SSM Agentがインストールされているか"
            Write-Host "   2. IAMロールにAmazonSSMManagedInstanceCoreポリシーがアタッチされているか"
            Write-Host "   3. SSMエンドポイントへの接続が可能か"
        }
    }
    else {
        Write-Host "NG: コマンド実行エラー: $instanceInfo"
    }
}
catch {
    Write-Host "NG: エラー: $_"
}

Write-Host ""

# 2. IAMロールの確認
Write-Host "=== IAMロール確認 ==="
try {
    $iamProfile = aws ec2 describe-instances --instance-ids $instanceId --region $region --query 'Reservations[0].Instances[0].IamInstanceProfile.Arn' --output text 2>&1
    if ($LASTEXITCODE -eq 0 -and $iamProfile -ne "None") {
        Write-Host "OK: IAMインスタンスプロファイルが設定されています: $iamProfile"
        Write-Host ""
        Write-Host "以下のポリシーがアタッチされているか確認してください:"
        Write-Host "  - AmazonSSMManagedInstanceCore"
    }
    else {
        Write-Host "NG: IAMインスタンスプロファイルが設定されていません"
        Write-Host "   EC2インスタンスにIAMロールをアタッチしてください"
    }
}
catch {
    Write-Host "NG: エラー: $_"
}

Write-Host ""

# 3. Session Manager Pluginの確認
Write-Host "=== Session Manager Plugin確認 ==="
try {
    $pluginVersion = session-manager-plugin --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Session Manager Pluginがインストールされています"
        Write-Host "   バージョン: $pluginVersion"
    }
    else {
        Write-Host "NG: Session Manager Pluginがインストールされていません"
        Write-Host ""
        Write-Host "インストール方法:"
        Write-Host "  Windows: https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe"
        Write-Host "  Linux: sudo yum install -y https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm"
        Write-Host "  macOS: brew install --cask session-manager-plugin"
    }
}
catch {
    Write-Host "NG: Session Manager Pluginがインストールされていません"
}

Write-Host ""

# 4. セッション開始テスト
Write-Host "=== セッション開始テスト ==="
Write-Host "以下のコマンドでセッションを開始できます:"
Write-Host ""
Write-Host "aws ssm start-session --target $instanceId --region $region"
Write-Host ""

Write-Host "=========================================="
