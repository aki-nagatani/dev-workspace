-- ============================================================
-- 本番環境のusernameをメールアドレスに更新するSQLスクリプト
-- ============================================================
--
-- 使用方法:
-- 1. このスクリプト内のUPDATE文を、実際のユーザー情報に合わせて編集
-- 2. EC2にSSH接続（またはAWS Systems Manager Session Manager経由）
-- 3. psqlコマンドで実行:
--    psql -h shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com \
--         -U shared_user \
--         -d shared_db \
--         -f update_username_to_email_production.sql
--
-- 注意: 実行前に必ずバックアップを取得してください
-- ============================================================

-- トランザクション開始
BEGIN;

-- ============================================================
-- MyPokedex Userテーブルの更新
-- ============================================================
-- 以下、ユーザーIDごとにusernameをメールアドレスに更新
-- 実際のユーザー情報に合わせて編集してください
--
-- 例:
-- UPDATE "User" SET username = 'user1@example.com' WHERE id = 1;
-- UPDATE "User" SET username = 'user2@example.com' WHERE id = 2;

-- ============================================================
-- FishTrack fishtrack_userテーブルの更新
-- ============================================================
-- 以下、ユーザーIDごとにusernameをメールアドレスに更新
-- 実際のユーザー情報に合わせて編集してください
--
-- 例:
-- UPDATE fishtrack_user SET username = 'user1@example.com' WHERE id = 1;
-- UPDATE fishtrack_user SET username = 'user2@example.com' WHERE id = 2;

-- 更新結果を確認
SELECT id, username FROM "User" ORDER BY id;

SELECT id, username FROM fishtrack_user ORDER BY id;

-- 問題がなければコミット、問題があればロールバック
-- COMMIT;
-- ROLLBACK;