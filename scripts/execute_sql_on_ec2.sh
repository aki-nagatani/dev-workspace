#!/bin/bash
# ============================================================
# EC2上でSQLスクリプトを実行するヘルパースクリプト
# ============================================================
# 
# 使用方法:
# 1. このスクリプトをEC2にアップロード
# 2. 実行権限を付与: chmod +x execute_sql_on_ec2.sh
# 3. 実行: ./execute_sql_on_ec2.sh <SQLファイル名>
# ============================================================

if [ $# -eq 0 ]; then
    echo "使用方法: $0 <SQLファイル名>"
    echo "例: $0 update_username_to_email_production.sql"
    exit 1
fi

SQL_FILE="$1"
DB_HOST="shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com"
DB_USER="shared_user"
DB_NAME="shared_db"

if [ ! -f "$SQL_FILE" ]; then
    echo "エラー: ファイル '$SQL_FILE' が見つかりません。"
    exit 1
fi

echo "=========================================="
echo "SQLスクリプトを実行します"
echo "=========================================="
echo "ファイル: $SQL_FILE"
echo "データベース: $DB_HOST/$DB_NAME"
echo ""

# PostgreSQL接続確認
echo "データベース接続を確認しています..."
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "エラー: データベースに接続できませんでした。"
    echo "接続情報を確認してください。"
    exit 1
fi

echo "✓ データベース接続成功"
echo ""

# SQLスクリプトを実行
echo "SQLスクリプトを実行します..."
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ SQLスクリプトの実行が完了しました"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "✗ SQLスクリプトの実行中にエラーが発生しました"
    echo "=========================================="
    exit 1
fi

