#!/bin/bash
# マイグレーション状態を確認するスクリプト
# 実行場所: EC2インスタンス上またはローカル環境

set -e

echo "=========================================="
echo "マイグレーション状態確認"
echo "=========================================="
echo ""

# 環境変数の確認
if [ -z "${SHARED_DATABASE_URL:-}" ]; then
  echo "Error: SHARED_DATABASE_URL environment variable is not set"
  echo "Please set it before running this script:"
  echo "  export SHARED_DATABASE_URL='postgresql://user:password@host:port/database'"
  exit 1
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

