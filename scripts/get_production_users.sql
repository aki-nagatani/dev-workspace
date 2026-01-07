-- ============================================================
-- 本番環境のユーザー情報を取得するSQLクエリ
-- ============================================================
--
-- 使用方法:
-- EC2にSSH接続して実行、またはAWS Systems Manager Session Manager経由で実行
--
-- psql -h shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com \
--      -U shared_user \
--      -d shared_db \
--      -f get_production_users.sql
-- ============================================================

-- MyPokedex Userテーブルのユーザー一覧
SELECT
    id,
    username,
    created_at,
    last_login_at
FROM "User"
ORDER BY id;

-- FishTrack fishtrack_userテーブルのユーザー一覧
SELECT
    id,
    username,
    created_at,
    last_login_at
FROM fishtrack_user
ORDER BY id;