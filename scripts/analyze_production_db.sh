#!/bin/bash
# 本番環境（shared-db）のスキーマ分析を実行するスクリプト
# EC2インスタンス上で実行することを想定

set -euo pipefail

echo "=== Analyzing Production Database Schema ==="

# dev-workspaceのパスを確認
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ ! -d "$WORKSPACE_ROOT" ]; then
  echo "Error: dev-workspace directory not found at $WORKSPACE_ROOT"
  exit 1
fi

cd "$WORKSPACE_ROOT"

# Python環境を確認
if command -v python3 &> /dev/null; then
  PYTHON_CMD=python3
elif command -v python &> /dev/null; then
  PYTHON_CMD=python
else
  echo "Error: Python not found"
  exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"

# 必要なパッケージを確認
echo "=== Checking dependencies ==="
$PYTHON_CMD -c "import sqlalchemy" 2>/dev/null || {
  echo "Error: sqlalchemy is not installed"
  echo "Please install it with: pip install sqlalchemy psycopg2-binary"
  exit 1
}

# データベースURLを設定
if [ -z "${SHARED_DATABASE_URL:-}" ]; then
  export SHARED_DATABASE_URL="postgresql://shared_user:LwbxNlVBw7loKk-oQBB2tdD1XO_ZZf8B05uwSQTtF9A@shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com:5432/shared_db"
fi

echo "Database URL: ${SHARED_DATABASE_URL%@*}@***"

# 出力ディレクトリを作成
OUTPUT_DIR="$WORKSPACE_ROOT/docs"
mkdir -p "$OUTPUT_DIR"

# スキーマ分析を実行
echo "=== Running schema analysis ==="
$PYTHON_CMD scripts/analyze_db_schema.py \
  --environment "Production (shared-db)" \
  --output "$OUTPUT_DIR/db_schema_production.md"

if [ $? -eq 0 ]; then
  echo "=== Analysis completed successfully ==="
  echo "Output file: $OUTPUT_DIR/db_schema_production.md"
  if [ -f "$OUTPUT_DIR/db_schema_production.md" ]; then
    echo "File size: $(du -h "$OUTPUT_DIR/db_schema_production.md" | cut -f1)"
    echo "First 20 lines:"
    head -n 20 "$OUTPUT_DIR/db_schema_production.md"
  fi
else
  echo "Error: Schema analysis failed"
  exit 1
fi

