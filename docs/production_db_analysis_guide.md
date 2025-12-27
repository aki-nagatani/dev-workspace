# 本番環境（shared-db）のスキーマ分析ガイド

## 概要

本番環境（shared-db）のスキーマ分析を実行する方法を説明します。

## 方法1: EC2上で直接実行（推奨）

EC2インスタンスにSSH接続して、以下のコマンドを実行します：

```bash
# dev-workspaceディレクトリに移動
cd /home/ec2-user/dev-workspace || cd /home/ec2-user/FishTrack/../dev-workspace

# 最新のコードを取得
git fetch origin main
git reset --hard origin/main

# データベースURLを設定
export SHARED_DATABASE_URL="postgresql://shared_user:LwbxNlVBw7loKk-oQBB2tdD1XO_ZZf8B05uwSQTtF9A@shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com:5432/shared_db"

# スキーマ分析を実行
python3 scripts/analyze_db_schema.py \
  --environment "Production (shared-db)" \
  --output docs/db_schema_production.md
```

または、スクリプトを使用する場合：

```bash
# スクリプトに実行権限を付与
chmod +x scripts/analyze_production_db.sh

# スクリプトを実行
./scripts/analyze_production_db.sh
```

## 方法2: GitHub Actionsのワークフローを使用

1. `dev-workspace`リポジトリに`.github/workflows/analyze_production_db.yml`をコミット・プッシュ
2. GitHubのActionsタブから「Analyze Production Database Schema」ワークフローを選択
3. 「Run workflow」ボタンをクリックして実行
4. 実行完了後、Artifactsから`db_schema_production.md`をダウンロード

## 必要な環境

- Python 3.11以上
- `sqlalchemy`と`psycopg2-binary`パッケージがインストールされていること

## 注意事項

- 本番環境のデータベースに接続するため、適切な権限が必要です
- 分析には数分かかる場合があります
- 大量のテーブルがある場合、出力ファイルが大きくなる可能性があります

