#!/bin/bash
# AWS Systems Manager Session Managerを使用して本番環境を確認するスクリプト

set -e

INSTANCE_ID="i-023a1623e48cabf1d"
REGION="ap-northeast-1"

echo "=========================================="
echo "本番環境デプロイ状況確認（SSM経由）"
echo "=========================================="
echo ""

# Session Managerを使用して接続
echo "=== AWS Systems Manager Session Managerで接続 ==="
echo ""
echo "以下のコマンドを実行してください:"
echo ""
echo "aws ssm start-session --target $INSTANCE_ID --region $REGION"
echo ""
echo "接続後、以下のコマンドを実行:"
echo ""
echo "cd /home/ec2-user/MyPokedex"
echo "docker compose --env-file .env exec app sh -c '"
echo "  export SHARED_DATABASE_URL=\$MYPDEX_DATABASE_URL"
echo "  export PYTHONPATH=/app/src:/app/../dev-workspace:/app/../FishTrack/src:/app/../MyPokedex/src"
echo "  cd /app/../dev-workspace"
echo "  python3 scripts/check_production_deployment.py"
echo "'"
echo ""
