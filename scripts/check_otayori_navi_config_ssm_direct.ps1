# PowerShell用: おたよりナビ config.yaml確認（SSM経由・直接実行版）

Write-Host "=========================================="
Write-Host "おたよりナビ config.yaml確認（SSM経由・直接実行版）"
Write-Host "=========================================="
Write-Host ""

$INSTANCE_ID = "i-001cd3b0db58d9f78"
$REGION = "ap-northeast-1"

Write-Host "=== AWS Systems Manager Session Managerで接続 ==="
Write-Host ""
Write-Host "以下のコマンドを実行してください:"
Write-Host ""
Write-Host "aws ssm start-session --target $INSTANCE_ID --region $REGION"
Write-Host ""
Write-Host "接続後、以下のコマンドを実行（sudo -u ec2-userで実行）:"
Write-Host ""
Write-Host "sudo -u ec2-user bash -c 'cd /home/ec2-user/otayori-navi && docker compose --env-file .env exec -T app python3 -c \""
Write-Host "import os
Write-Host "import yaml
Write-Host "from pathlib import Path
Write-Host "config_path = Path('/app/config.yaml')
Write-Host "if not config_path.exists():
Write-Host "    print('Error: config.yaml not found')
Write-Host "    exit(1)
Write-Host "with open(config_path, 'r', encoding='utf-8') as f:
Write-Host "    config = yaml.safe_load(f)
Write-Host "print('=== config.yaml確認 ===')
Write-Host "print()
Write-Host "# Web設定
Write-Host "web = config.get('web', {})
Write-Host "print('Web設定:')
Write-Host "print(f\"  secret_key_env: {web.get('secret_key_env', 'NOT SET')}\")
Write-Host "print(f\"  session_cookie_name: { web.get('session_cookie_name', 'NOT SET') }\")
Write-Host "print()
Write-Host "# DB設定
Write-Host "db = config.get('db', {})
Write-Host "print('DB設定:')
Write-Host "print(f\"  url_env: {db.get('url_env', 'NOT SET')}\")
Write-Host "print()
Write-Host "# S3設定
Write-Host "s3 = config.get('s3', {})
Write-Host "print('S3設定:')
Write-Host "print(f\"  bucket: { s3.get('bucket', 'NOT SET') }\")
Write-Host "print(f\"  pdf_base_path: {s3.get('pdf_base_path', 'NOT SET')}\")
Write-Host "print(f\"  md_base_path: { s3.get('md_base_path', 'NOT SET') }\")
Write-Host "print()
Write-Host "# AWS設定
Write-Host "aws = config.get('aws', {})
Write-Host "print('AWS設定:')
Write-Host "print(f\"  region: {aws.get('region', 'NOT SET')}\")
Write-Host "print()
Write-Host "# AI設定
Write-Host "ai = config.get('ai', {})
Write-Host "print('AI設定:')
Write-Host "endpoint_url = ai.get('endpoint_url', 'NOT SET')
Write-Host "if 'example.com' in str(endpoint_url):
Write-Host "    print(f\"  ⚠️  endpoint_url: { endpoint_url } (プレースホルダーのまま)\")
Write-Host "else:
Write-Host "    print(f\"  endpoint_url: { endpoint_url }\")
Write-Host "print(f\"  api_key_env: {ai.get('api_key_env', 'NOT SET')}\")
Write-Host "print(f\"  model: { ai.get('model', 'NOT SET') }\")
Write-Host "print(f\"  timeout_seconds: {ai.get('timeout_seconds', 'NOT SET')}\")
Write-Host "\"'"
Write-Host ""
Write-Host "=========================================="
