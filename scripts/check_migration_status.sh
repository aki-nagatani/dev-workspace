#!/bin/bash
# マイグレーション状態を確認するスクリプト
# 実行場所: EC2インスタンス上またはローカル環境

set -e

echo "=========================================="
echo "マイグレーション状態確認"
echo "=========================================="
echo ""

# 環境変数の設定
if [ -z "${SHARED_DATABASE_URL:-}" ]; then
  export SHARED_DATABASE_URL="postgresql://shared_user:LwbxNlVBw7loKk-oQBB2tdD1XO_ZZf8B05uwSQTtF9A@shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com:5432/shared_db"
fi

# dev-workspaceの統合マイグレーション
echo "=== dev-workspace 統合マイグレーション ==="
cd "$HOME/dev-workspace" || cd "$(dirname "$0")/.."
echo "現在のマイグレーション状態:"
alembic current || echo "マイグレーションが適用されていません"
echo ""
echo "マイグレーション履歴:"
alembic history --verbose | head -20
echo ""

# FishTrackのマイグレーション
if [ -d "$HOME/FishTrack" ] || [ -d "../FishTrack" ]; then
  echo "=== FishTrack マイグレーション ==="
  cd "$HOME/FishTrack" 2>/dev/null || cd "../FishTrack" 2>/dev/null || true
  if [ -f "alembic.ini" ]; then
    echo "現在のマイグレーション状態:"
    alembic current || echo "マイグレーションが適用されていません"
    echo ""
    echo "マイグレーション履歴:"
    alembic history --verbose | head -20
    echo ""
  fi
fi

# MyPokedexのマイグレーション
if [ -d "$HOME/MyPokedex" ] || [ -d "../MyPokedex" ]; then
  echo "=== MyPokedex マイグレーション ==="
  cd "$HOME/MyPokedex" 2>/dev/null || cd "../MyPokedex" 2>/dev/null || true
  if [ -f "alembic.ini" ]; then
    echo "現在のマイグレーション状態:"
    alembic current || echo "マイグレーションが適用されていません"
    echo ""
    echo "マイグレーション履歴:"
    alembic history --verbose | head -20
    echo ""
  fi
fi

echo "=========================================="
echo "確認完了"
echo "=========================================="

