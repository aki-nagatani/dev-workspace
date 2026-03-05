# Slack通知送信機能

## 概要

`send_slack_notification.py` は、Slack Webhook URLを使用してメッセージを送信するPythonスクリプトです。
MCP経由のSlack送信が不安定な場合のフォールバック手段として使用されます。

## セットアップ

### 1. 依存関係のインストール

`requests` ライブラリが必要です。以下のコマンドでインストールしてください：

```bash
pip install requests
```

### 2. Webhook URLの設定

Slack Webhook URLは以下の優先順位で取得されます：

1. **コマンドライン引数** (`--webhook-url` オプション)
2. **環境変数** (`SLACK_WEBHOOK_URL`)
3. **.envファイル** (プロジェクトルートの `.env` ファイル)
4. **MCP設定ファイル** (`~/.cursor/mcp.json` の `text2slack` MCPサーバーの環境変数)
5. **ローカル設定ファイル** (プロジェクトルートの `config.local.json` ファイル)

#### 方法1: 環境変数の設定

**Windows (PowerShell)**:

```powershell
$env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Windows (コマンドプロンプト)**:

```cmd
set SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Linux/Mac**:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

#### 方法2: MCP設定ファイルの利用（推奨）

MCP設定ファイル（`~/.cursor/mcp.json`）に `text2slack` MCPサーバーの環境変数として設定されている場合は、自動的に使用されます：

```json
{
  "mcpServers": {
    "text2slack": {
      "env": {
        "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
      }
    }
  }
}
```

この方法を使用すると、環境変数を設定する必要がなく、MCP設定と一元管理できます。

#### 方法3: .envファイルの利用（推奨・ローカル開発用）

プロジェクトルートに `.env` ファイルを作成し、以下のように設定します：

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**注意**: `.env` ファイルは `.gitignore` に含まれているため、Gitリポジトリには含まれません。安全に機密情報を管理できます。

**セットアップ手順**:

1. `.env.example` を `.env` にコピー
2. `.env` ファイル内の `YOUR/WEBHOOK/URL` を実際のWebhook URLに置き換え

```bash
# Windows (PowerShell)
Copy-Item .env.example .env
# その後、.envファイルを編集してWebhook URLを設定

# Linux/Mac
cp .env.example .env
# その後、.envファイルを編集してWebhook URLを設定
```

#### 方法4: ローカル設定ファイルの利用（推奨・ローカル開発用）

プロジェクトルートに `config.local.json` ファイルを作成し、以下のように設定します：

```json
{
  "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

**注意**: `config.local.json` ファイルは `.gitignore` に含まれているため、Gitリポジトリには含まれません。安全に機密情報を管理できます。

**セットアップ手順**:

1. `config.local.json.example` を `config.local.json` にコピー
2. `config.local.json` ファイル内の `YOUR/WEBHOOK/URL` を実際のWebhook URLに置き換え

```bash
# Windows (PowerShell)
Copy-Item config.local.json.example config.local.json
# その後、config.local.jsonファイルを編集してWebhook URLを設定

# Linux/Mac
cp config.local.json.example config.local.json
# その後、config.local.jsonファイルを編集してWebhook URLを設定
```

### 3. Slack Webhook URLの取得方法

1. Slackワークスペースにログイン
2. [Slack Apps](https://api.slack.com/apps) にアクセス
3. 「Create New App」をクリック
4. 「Incoming Webhooks」を有効化
5. 「Add New Webhook to Workspace」をクリック
6. 送信先チャンネルを選択
7. Webhook URLをコピー

## 使用方法

### 基本的な使用方法

```bash
python scripts/send_slack_notification.py "メッセージ本文"
```

### オプション指定

```bash
# チャンネルを指定
python scripts/send_slack_notification.py --channel "#general" "メッセージ本文"

# ユーザーに直接送信
python scripts/send_slack_notification.py --channel "@username" "メッセージ本文"

# ボット名を変更
python scripts/send_slack_notification.py --username "My Bot" "メッセージ本文"

# アイコンを変更
python scripts/send_slack_notification.py --icon-emoji ":rocket:" "メッセージ本文"

# Webhook URLを直接指定（環境変数の代わり）
python scripts/send_slack_notification.py --webhook-url "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" "メッセージ本文"
```

### ヘルプの表示

```bash
python scripts/send_slack_notification.py --help
```

## エラーハンドリング

スクリプトは以下のエラーを適切に処理します：

- **環境変数未設定**: `SLACK_WEBHOOK_URL` が設定されていない場合、エラーメッセージを表示して終了
- **ネットワークエラー**: タイムアウト（10秒）や接続エラーを検出してエラーメッセージを表示
- **HTTPエラー**: Slack APIからのエラーレスポンスを検出してエラーメッセージを表示

## 統合方法

`slack-final-report` SKILLから自動的に呼び出されます。MCP経由の送信が失敗した場合、以下の優先順位でフォールバックされます：

1. **MCP経由**: `mcp_text2slack_send_to_slack` または `send_to_slack` ツール
2. **Pythonスクリプト経由**: `run_terminal_cmd` ツールを使用してこのスクリプトを実行
3. **直接HTTPリクエスト**: `mcp_web_fetch` ツールを使用（最終手段）

## トラブルシューティング

### エラー: `SLACK_WEBHOOK_URL is not set`

**原因**: Webhook URLが設定されていない

**解決方法**: 上記の「Webhook URLの設定」を参照して、以下のいずれかの方法で設定してください：

- 環境変数 `SLACK_WEBHOOK_URL` を設定
- `.env` ファイルを作成して設定
- `config.local.json` ファイルを作成して設定
- MCP設定ファイルに設定
- コマンドライン引数 `--webhook-url` を使用

### エラー: `Failed to send Slack message: Connection timeout`

**原因**: ネットワーク接続の問題またはタイムアウト

**解決方法**:

- ネットワーク接続を確認
- ファイアウォール設定を確認
- Webhook URLが正しいか確認

### エラー: `Unexpected response from Slack: ...`

**原因**: Slack APIからの予期しないレスポンス

**解決方法**:

- Webhook URLが有効か確認
- Slackワークスペースの設定を確認
- Webhookが無効化されていないか確認

## セキュリティに関する注意事項

**重要**: Slack Webhook URLは機密情報です。以下の点に注意してください：

1. **コードにハードコードしない**: Webhook URLをソースコードに直接記述しないでください。GitHubのPush Protectionが検出してプッシュをブロックします。
2. **.gitignoreに含まれるファイルを使用**: `.env` や `config.local.json` は `.gitignore` に含まれているため、安全に使用できます。
3. **環境変数の使用**: 本番環境では環境変数を使用することを推奨します。
4. **Webhook URLの漏洩時**: Webhook URLが漏洩した場合は、Slackの設定から該当のWebhookを無効化し、新しいWebhook URLを生成してください。

## 関連ファイル

- `scripts/send_slack_notification.py`: メインスクリプト
- `.cursor/skills/slack-final-report/SKILL.md`: SKILL定義ファイル
- `.env.example`: .envファイルのテンプレート
- `config.local.json.example`: config.local.jsonファイルのテンプレート

## 更新履歴

- 2026-01-31: 初版作成（MCP経由のSlack送信が不安定な場合のフォールバック手段として実装）
- 2026-01-31: .envファイルとconfig.local.jsonファイルのサポートを追加（安全な機密情報管理のため）
