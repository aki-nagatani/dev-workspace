# PowerShell用: おたよりナビ マイグレーション状態確認（SSM send-command経由）

Write-Host "=========================================="
Write-Host "おたよりナビ マイグレーション状態確認（SSM send-command経由）"
Write-Host "=========================================="
Write-Host ""

# おたよりナビ用EC2インスタンスID
$INSTANCE_ID = "i-001cd3b0db58d9f78"
$REGION = "ap-northeast-1"

# 1. マイグレーション状態の確認（alembic_versionテーブル）
Write-Host "【1. マイグレーション状態確認】"
Write-Host "-" * 80
Write-Host ""

$command1 = @"
cd /home/ec2-user/otayori-navi && docker compose --env-file .env exec -T app sh -c 'export SHARED_DATABASE_URL=`$OTAYORI_NAVI_DATABASE_URL && export PYTHONPATH=/app/src:/app/../dev-workspace:/app/../FishTrack/src:/app/../MyPokedex/src:/app/../otayori-navi/src && cd /app/../dev-workspace && python3 -c "
import os
import sys
from sqlalchemy import create_engine, text
db_url = os.getenv(\"SHARED_DATABASE_URL\")
if not db_url:
    print(\"Error: SHARED_DATABASE_URL not set\")
    sys.exit(1)
engine = create_engine(db_url)
with engine.connect() as conn:
    result = conn.execute(text(\"SELECT version_num FROM alembic_version ORDER BY version_num\"))
    versions = [row[0] for row in result]
    if versions:
        print(\"Current migrations:\")
        for v in versions:
            print(f\"  - {v}\")
        if \"20260204001210\" in versions:
            print(\"✅ Otayori Navi migration (20260204001210) is applied\")
        else:
            print(\"❌ Otayori Navi migration (20260204001210) is NOT applied\")
    else:
        print(\"⚠️  No migrations found\")
"'
"@

Write-Host "実行コマンド:"
Write-Host $command1
Write-Host ""
Write-Host "AWS CLIコマンド:"
Write-Host "aws ssm send-command --instance-ids $INSTANCE_ID --region $REGION --document-name 'AWS-RunShellScript' --parameters 'commands=[$($command1 -replace "`"", "\`"")]'"
Write-Host ""

# 2. テーブル存在確認
Write-Host "【2. テーブル存在確認】"
Write-Host "-" * 80
Write-Host ""

$command2 = @"
cd /home/ec2-user/otayori-navi && docker compose --env-file .env exec -T app sh -c 'export SHARED_DATABASE_URL=`$OTAYORI_NAVI_DATABASE_URL && export PYTHONPATH=/app/src:/app/../dev-workspace:/app/../FishTrack/src:/app/../MyPokedex/src:/app/../otayori-navi/src && cd /app/../dev-workspace && python3 -c "
import os
import sys
from sqlalchemy import create_engine, inspect
db_url = os.getenv(\"SHARED_DATABASE_URL\")
if not db_url:
    print(\"Error: SHARED_DATABASE_URL not set\")
    sys.exit(1)
engine = create_engine(db_url)
inspector = inspect(engine)
tables = [\"families\", \"users\", \"family_invites\", \"documents\"]
print(\"Table existence check:\")
all_exist = True
for table in tables:
    exists = inspector.has_table(table)
    status = \"✅\" if exists else \"❌\"
    print(f\"  {status} {table}: {\"exists\" if exists else \"NOT exists\"}\")
    if not exists:
        all_exist = False
if all_exist:
    print(\"✅ All tables exist\")
else:
    print(\"❌ Some tables are missing\")
"'
"@

Write-Host "実行コマンド:"
Write-Host $command2
Write-Host ""
Write-Host "AWS CLIコマンド:"
Write-Host "aws ssm send-command --instance-ids $INSTANCE_ID --region $REGION --document-name 'AWS-RunShellScript' --parameters 'commands=[$($command2 -replace "`"", "\`"")]'"
Write-Host ""

Write-Host "=========================================="
Write-Host "注意: 上記のコマンドは複雑なため、SSM Session Manager経由での確認を推奨します"
Write-Host "=========================================="
