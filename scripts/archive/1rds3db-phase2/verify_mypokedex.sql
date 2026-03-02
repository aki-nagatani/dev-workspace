-- Phase 2b 整合性確認用（shared_db vs mypokedex_db の件数比較）
-- 手順書 2.3 Phase 2b 確認用クエリ
-- 実行: psql -h <HOST> -p 5432 -U <USER> -d <DB> -t -A -f verify_mypokedex.sql
SELECT 'User' AS tbl, COUNT(*) AS cnt FROM "User"
UNION ALL SELECT 'UserGameSetting', COUNT(*) FROM "UserGameSetting"
UNION ALL SELECT 'Regist', COUNT(*) FROM "Regist"
UNION ALL SELECT 'DexEntry', COUNT(*) FROM "DexEntry"
UNION ALL SELECT 'Pokemon', COUNT(*) FROM "Pokemon"
UNION ALL SELECT 'GameTitle', COUNT(*) FROM "GameTitle"
UNION ALL SELECT 'evolution', COUNT(*) FROM evolution
UNION ALL SELECT 'placement', COUNT(*) FROM placement
UNION ALL SELECT 'box_members', COUNT(*) FROM box_members
UNION ALL SELECT 'party_members', COUNT(*) FROM party_members
UNION ALL SELECT 'Contact', COUNT(*) FROM "Contact"
UNION ALL SELECT 'user_statistics_daily', COUNT(*) FROM user_statistics_daily
UNION ALL SELECT 'user_statistics_weekly', COUNT(*) FROM user_statistics_weekly
ORDER BY tbl;
