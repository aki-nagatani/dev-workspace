#!/bin/bash
# ============================================================
# 本番環境のusernameをメールアドレスに更新する対話型スクリプト
# ============================================================
# 
# 使用方法:
# 1. EC2にSSH接続
# 2. このスクリプトをEC2にアップロード
# 3. 実行権限を付与: chmod +x update_username_to_email_interactive.sh
# 4. 実行: ./update_username_to_email_interactive.sh
# ============================================================

DB_HOST="shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com"
DB_USER="shared_user"
DB_NAME="shared_db"

echo "=========================================="
echo "本番環境のusernameをメールアドレスに更新"
echo "=========================================="
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

# MyPokedex Userテーブルのユーザー一覧を表示
echo "=== MyPokedex Userテーブルのユーザー一覧 ==="
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT id, username FROM \"User\" ORDER BY id;"
echo ""

# FishTrack fishtrack_userテーブルのユーザー一覧を表示
echo "=== FishTrack fishtrack_userテーブルのユーザー一覧 ==="
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT id, username FROM fishtrack_user ORDER BY id;"
echo ""

echo "=========================================="
echo "更新を開始しますか？ (y/n)"
echo "=========================================="
read -p "> " confirm

if [ "$confirm" != "y" ]; then
    echo "中断しました。"
    exit 0
fi

# MyPokedex Userテーブルの更新
echo ""
echo "=== MyPokedex Userテーブルの更新 ==="
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" <<EOF
BEGIN;

-- ここにUPDATE文を追加してください
-- 例: UPDATE "User" SET username = 'user1@example.com' WHERE id = 1;

-- 更新結果を確認
SELECT id, username FROM "User" ORDER BY id;

-- 問題がなければCOMMIT、問題があればROLLBACK
-- COMMIT;
-- ROLLBACK;
EOF

# FishTrack fishtrack_userテーブルの更新
echo ""
echo "=== FishTrack fishtrack_userテーブルの更新 ==="
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" <<EOF
BEGIN;

-- ここにUPDATE文を追加してください
-- 例: UPDATE fishtrack_user SET username = 'user1@example.com' WHERE id = 1;

-- 更新結果を確認
SELECT id, username FROM fishtrack_user ORDER BY id;

-- 問題がなければCOMMIT、問題があればROLLBACK
-- COMMIT;
-- ROLLBACK;
EOF

echo ""
echo "=========================================="
echo "更新完了"
echo "=========================================="

