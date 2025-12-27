# データベーススキーマ分析ガイド

## 概要

本ドキュメントは、本番DBとローカルDockerのDBスキーマを分析し、差異を確認するための手順書です。

## 分析スクリプト

`scripts/analyze_db_schema.py` を使用してデータベースのスキーマを分析します。

## 実行手順

### 1. ローカルDocker環境の分析

```bash
# ローカルDocker環境のDB URLを設定
export SHARED_DATABASE_URL="postgresql://user:pass@localhost:5432/shared_db"

# 分析を実行
cd dev-workspace
python scripts/analyze_db_schema.py \
  --environment "Local Docker" \
  --output docs/db_schema_local.md
```

### 2. 本番環境の分析

本番環境では、EC2インスタンス上で実行するか、デプロイワークフローに統合する必要があります。

#### 方法A: EC2インスタンス上で直接実行

```bash
# EC2インスタンスにSSH接続
ssh user@production-server

# dev-workspaceをクローン/更新
cd /path/to/dev-workspace
git pull origin main

# 環境変数を設定（.envファイルから読み込む）
export SHARED_DATABASE_URL="postgresql://user:pass@shared-db:5432/shared_db"

# 分析を実行
python scripts/analyze_db_schema.py \
  --environment "Production" \
  --output docs/db_schema_production.md

# 結果をローカルにコピー
scp user@production-server:/path/to/dev-workspace/docs/db_schema_production.md ./docs/
```

#### 方法B: デプロイワークフローに統合

GitHub Actionsのワークフローに一時的なジョブを追加して実行します。

## 比較方法

1. 両方の分析結果を取得
2. テーブル一覧を比較
3. 各テーブルのカラム定義を比較
4. 制約（主キー、外部キー、インデックス、ユニーク制約）を比較
5. レコード数を比較
6. 仕様書との差異を確認

## 期待される結果

- 本番DBとローカルDBのスキーマが一致していること
- 仕様書に記載されているテーブルとカラムが存在すること
- 仕様書に記載されていないテーブルやカラムがないこと（または、その理由が明確であること）

