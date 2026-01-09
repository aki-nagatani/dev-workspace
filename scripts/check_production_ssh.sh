#!/bin/bash
# 本番環境のデプロイ状況をSSH経由で確認するスクリプト

set -e

echo "=========================================="
echo "本番環境デプロイ状況確認（SSH経由）"
echo "=========================================="
echo ""

# MyPokedexの確認
echo "=== MyPokedex 本番環境確認 ==="
echo ""
echo "以下のコマンドを実行してください:"
echo ""
echo "ssh ec2-user@54.249.50.253 'cd /home/ec2-user/MyPokedex && docker compose --env-file .env exec app sh -c \""
echo "  export SHARED_DATABASE_URL=\\\$MYPDEX_DATABASE_URL"
echo "  export PYTHONPATH=/app/src:/app/../dev-workspace:/app/../FishTrack/src:/app/../MyPokedex/src"
echo "  cd /app/../dev-workspace"
echo "  python3 scripts/check_production_deployment.py"
echo "\"'"
echo ""
