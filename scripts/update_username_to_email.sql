-- ============================================================
-- 本番環境のusernameをメールアドレスに更新するSQLスクリプト
-- ============================================================
--
-- 使用方法:
-- 1. EC2にSSH接続
-- 2. このスクリプトをEC2にアップロード
-- 3. psqlコマンドで実行:
--    psql -h shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com \
--         -U shared_user \
--         -d shared_db \
--         -f update_username_to_email.sql
--
-- 注意: 実行前に必ずバックアップを取得してください
-- ============================================================

-- トランザクション開始
BEGIN;

-- ============================================================
-- MyPokedex Userテーブルの更新
-- ============================================================
-- ユーザーIDとusernameの対応を確認
SELECT id, username FROM "User" ORDER BY id;

-- 以下、ユーザーIDごとにusernameをメールアドレスに更新
-- 例: UPDATE "User" SET username = 'example@example.com' WHERE id = 1;
--
-- 実際の更新は、上記のSELECT結果を確認してから、以下のように実行してください:
--
-- UPDATE "User" SET username = 'user1@example.com' WHERE id = 1;
-- UPDATE "User" SET username = 'user2@example.com' WHERE id = 2;
-- ... (各ユーザーに対して実行)

-- ============================================================
-- FishTrack fishtrack_userテーブルの更新
-- ============================================================
-- ユーザーIDとusernameの対応を確認
SELECT id, username FROM fishtrack_user ORDER BY id;

-- 以下、ユーザーIDごとにusernameをメールアドレスに更新
-- 例: UPDATE fishtrack_user SET username = 'example@example.com' WHERE id = 1;
--
-- 実際の更新は、上記のSELECT結果を確認してから、以下のように実行してください:
--
-- UPDATE fishtrack_user SET username = 'user1@example.com' WHERE id = 1;
-- UPDATE fishtrack_user SET username = 'user2@example.com' WHERE id = 2;
-- ... (各ユーザーに対して実行)

-- 更新結果を確認
SELECT id, username FROM "User" ORDER BY id;

SELECT id, username FROM fishtrack_user ORDER BY id;

-- 問題がなければコミット、問題があればロールバック
-- COMMIT;
-- ROLLBACK;