#!/bin/bash
# AWS Systems Manager Session Managerを使用しておたよりナビのマイグレーション状態を確認するスクリプト

set -e

# おたよりナビ用EC2インスタンスID（確認スクリプトの結果から）
INSTANCE_ID="i-001cd3b0db58d9f78"
REGION="ap-northeast-1"

echo "=========================================="
echo "おたよりナビ マイグレーション状態確認（SSM経由）"
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
echo "cd /home/ec2-user/otayori-navi"
echo "docker compose --env-file .env exec -T app sh -c '"
echo "  export SHARED_DATABASE_URL=\$OTAYORI_NAVI_DATABASE_URL"
echo "  export PYTHONPATH=/app/src:/app/../dev-workspace:/app/../FishTrack/src:/app/../MyPokedex/src:/app/../otayori-navi/src"
echo "  cd /app/../dev-workspace"
echo "  python3 scripts/check_otayori_navi_migration.py"
echo "'"
echo ""
echo "または、直接SQLで確認する場合:"
echo ""
echo "docker compose --env-file .env exec -T app sh -c '"
echo "  export PGPASSWORD=\$(echo \$OTAYORI_NAVI_DATABASE_URL | sed -n \"s/.*:\\([^@]*\\)@.*/\\1/p\")"
echo "  psql -h shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com -U shared_user -d shared_db -c \""
echo "    SELECT version_num FROM alembic_version ORDER BY version_num;"
echo "  \""
echo "  psql -h shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com -U shared_user -d shared_db -c \""
echo "    SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('families', 'users', 'family_invites', 'documents');"
echo "  \""
echo "'"
echo ""
