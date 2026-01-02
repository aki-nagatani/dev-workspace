#!/bin/bash
# 本番環境（shared-db）のデータベースバックアップスクリプト
# 実行場所: EC2インスタンス上

set -e

# 環境変数の設定
if [ -z "${SHARED_DATABASE_URL:-}" ]; then
  export SHARED_DATABASE_URL="postgresql://shared_user:LwbxNlVBw7loKk-oQBB2tdD1XO_ZZf8B05uwSQTtF9A@shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com:5432/shared_db"
fi

# バックアップディレクトリの作成
BACKUP_DIR="$HOME/dev-workspace/backups"
mkdir -p "$BACKUP_DIR"

# バックアップファイル名（タイムスタンプ付き）
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/shared_db_backup_${TIMESTAMP}.dump"

# データベースURLから接続情報を抽出
# postgresql://user:password@host:port/database
DB_URL="${SHARED_DATABASE_URL#postgresql://}"
CREDENTIALS="${DB_URL%%@*}"
HOST_PORT="${DB_URL#*@}"
HOST_PORT="${HOST_PORT%%/*}"
DB_NAME="${DB_URL##*/}"

USERNAME="${CREDENTIALS%%:*}"
PASSWORD="${CREDENTIALS#*:}"
HOST="${HOST_PORT%%:*}"
PORT="${HOST_PORT#*:}"

# デフォルトポート
if [ "$PORT" = "$HOST_PORT" ]; then
  PORT="5432"
fi

echo "=========================================="
echo "本番環境データベースバックアップ"
echo "=========================================="
echo "データベース: $DB_NAME"
echo "ホスト: $HOST"
echo "ポート: $PORT"
echo "ユーザー: $USERNAME"
echo "バックアップ先: $BACKUP_FILE"
echo "=========================================="
echo ""

# pg_dumpでバックアップを実行
export PGPASSWORD="$PASSWORD"
pg_dump -h "$HOST" -p "$PORT" -U "$USERNAME" -d "$DB_NAME" \
  -F c \
  -f "$BACKUP_FILE" \
  -v

# バックアップファイルのサイズを確認
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo ""
echo "=========================================="
echo "バックアップ完了"
echo "=========================================="
echo "バックアップファイル: $BACKUP_FILE"
echo "ファイルサイズ: $BACKUP_SIZE"
echo "=========================================="

# バックアップファイルの整合性を確認（オプション）
echo ""
echo "バックアップファイルの整合性を確認中..."
pg_restore --list "$BACKUP_FILE" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ バックアップファイルの整合性確認完了"
else
  echo "⚠️ バックアップファイルの整合性確認に失敗しました"
  exit 1
fi

