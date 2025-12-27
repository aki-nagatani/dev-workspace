# データベーススキーマ分析と比較

## 概要

本番DBとローカルDockerのDBスキーマを分析し、差異を確認するためのツールセットです。

## ファイル構成

- `scripts/analyze_db_schema.py`: データベースのスキーマを分析してMarkdown形式で出力
- `scripts/compare_db_schemas.py`: 2つの分析結果を比較してレポートを生成
- `docs/db_schema_analysis_guide.md`: 分析手順の詳細ガイド
- `docs/db_schema_comparison_template.md`: 比較レポートのテンプレート

## 実行手順

### ステップ1: ローカルDocker環境の分析

```bash
cd dev-workspace

# ローカルDocker環境のDB URLを設定
# docker-compose.ymlから確認したDB URLを使用
export SHARED_DATABASE_URL="postgresql://user:pass@localhost:5432/shared_db"

# 分析を実行
python scripts/analyze_db_schema.py \
  --environment "Local Docker" \
  --output docs/db_schema_local.md
```

### ステップ2: 本番環境の分析

#### 方法A: EC2インスタンス上で直接実行（推奨）

```bash
# EC2インスタンスにSSH接続
ssh user@production-server

# dev-workspaceをクローン/更新
cd /path/to/dev-workspace
git pull origin main

# 環境変数を設定（.envファイルから読み込むか、直接指定）
export SHARED_DATABASE_URL="postgresql://user:pass@shared-db:5432/shared_db"

# 分析を実行
python scripts/analyze_db_schema.py \
  --environment "Production" \
  --output docs/db_schema_production.md

# 結果をローカルにコピー
# ローカルマシンから実行:
scp user@production-server:/path/to/dev-workspace/docs/db_schema_production.md ./docs/
```

#### 方法B: GitHub Actionsワークフローで実行

一時的なワークフロージョブを追加して実行します（詳細は `db_schema_analysis_guide.md` を参照）。

### ステップ3: 比較レポートの生成

```bash
cd dev-workspace

# 2つの分析結果を比較
python scripts/compare_db_schemas.py \
  --production docs/db_schema_production.md \
  --local docs/db_schema_local.md \
  --output docs/db_schema_comparison.md
```

### ステップ4: 仕様書との比較

生成された分析結果を仕様書と比較します：

1. `FishTrack/docs/specifications/06_database.md` を参照
2. `MyPokedex/docs/specifications/06_database.md` を参照
3. 仕様書に記載されているテーブルとカラムが存在するか確認
4. 仕様書に記載されていないテーブルやカラムがないか確認

## 出力ファイル

- `docs/db_schema_production.md`: 本番環境のスキーマ分析結果
- `docs/db_schema_local.md`: ローカル環境のスキーマ分析結果
- `docs/db_schema_comparison.md`: 比較レポート

## 注意事項

1. **データベースURLの取り扱い**: 本番環境のDB URLは機密情報です。分析結果には含めないように注意してください。
2. **実行タイミング**: 本番環境の分析は、メンテナンス時間帯や低負荷時に行うことを推奨します。
3. **バックアップ**: 分析前にデータベースのバックアップを取得することを推奨します。

## トラブルシューティング

### 接続エラー

- データベースURLが正しいか確認
- ネットワーク接続が確立されているか確認
- ファイアウォール設定を確認

### パースエラー

- Markdownファイルの形式が正しいか確認
- スクリプトのバージョンが最新か確認

## 次のステップ

分析結果を確認した後：

1. 差異がある場合は、マイグレーションで同期する
2. 仕様書との差異がある場合は、仕様書を更新するか、データベースを修正する
3. マイグレーションをリセットする場合は、`scripts/stamp_current.py` を使用

