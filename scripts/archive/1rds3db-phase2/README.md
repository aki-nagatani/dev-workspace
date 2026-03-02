# 1RDS 3DB Phase 2 移行スクリプト（アーカイブ）

**1RDS 3DB Phase 2 は 2026-03-02 に完了済み。** 本ディレクトリのスクリプトは履歴・参照用にアーカイブした。

## 含まれるスクリプト

| ファイル | 用途 |
|----------|------|
| `run_migrate_fishtrack_local.ps1` | ローカル Docker で FishTrack → fishtrack_db 移行 |
| `run_migrate_mypokedex_local.ps1` | ローカル Docker で MyPokedex → mypokedex_db 移行 |
| `run_migrate_fishtrack_rds_ec2.sh` | EC2 上で RDS FishTrack → fishtrack_db 移行 |
| `run_migrate_mypokedex_rds_ec2.sh` | EC2 上で RDS MyPokedex → mypokedex_db 移行 |
| `run_migrate_*_rds_ec2_inner.sh` | 上記 RDS 移行の内部スクリプト |
| `migrate_*_tables_to_*_db.py` | pg_dump/pg_restore による移行ロジック |
| `run_verify_*_rds_ec2.sh` | shared_db vs 専用DB の件数比較（整合性確認） |
| `verify_*.sql` | 整合性確認用 SQL |

## 実行方法（必要な場合）

**ローカル移行**（dev-workspace ルートから）:
```powershell
cd d:\OneDrive\git_work\dev-workspace
.\scripts\archive\1rds3db-phase2\run_migrate_fishtrack_local.ps1
.\scripts\archive\1rds3db-phase2\run_migrate_mypokedex_local.ps1
```

**本番RDS 移行**（EC2 上・Phase 2 完了済みのため通常は不要）:
```bash
export SOURCE_DATABASE_URL="postgresql://user:pass@host:5432/shared_db"
./run_migrate_fishtrack_rds_ec2.sh
./run_migrate_mypokedex_rds_ec2.sh
```

## 参照

- [[1RDS 3DB Phase 2 手順書]]
