-- Phase 2a 整合性確認用（shared_db vs fishtrack_db の件数比較）
-- 手順書 2.3 Phase 2a 確認用クエリ
-- 実行: psql -h <HOST> -p 5432 -U <USER> -d <DB> -t -A -f verify_fishtrack.sql
SELECT 'manufacturer' AS tbl, COUNT(*) AS cnt FROM manufacturer
UNION ALL SELECT 'reel_model', COUNT(*) FROM reel_model
UNION ALL SELECT 'rod_model', COUNT(*) FROM rod_model
UNION ALL SELECT 'rod_series', COUNT(*) FROM rod_series
UNION ALL SELECT 'reel_series', COUNT(*) FROM reel_series
UNION ALL SELECT 'fishtrack_user', COUNT(*) FROM fishtrack_user
UNION ALL SELECT 'rod_holding', COUNT(*) FROM rod_holding
UNION ALL SELECT 'field', COUNT(*) FROM field
UNION ALL SELECT 'rental_boat_shop', COUNT(*) FROM rental_boat_shop
UNION ALL SELECT 'water_level_history', COUNT(*) FROM water_level_history
UNION ALL SELECT 'tackle_spec_import_log', COUNT(*) FROM tackle_spec_import_log
UNION ALL SELECT 'ops_monitoring', COUNT(*) FROM ops_monitoring
UNION ALL SELECT 'ops_job_log', COUNT(*) FROM ops_job_log
UNION ALL SELECT 'user_statistics_daily', COUNT(*) FROM user_statistics_daily
UNION ALL SELECT 'user_statistics_weekly', COUNT(*) FROM user_statistics_weekly
ORDER BY tbl;
