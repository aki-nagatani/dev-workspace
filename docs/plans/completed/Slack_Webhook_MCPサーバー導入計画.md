# Slack Webhook MCPサーバー導入計画

> **📋 全体計画**: 本計画は `dev-workspace/docs/plans/MyHobbySite全体作業計画.md` の一部として位置づけられています。全体の作業計画・優先順位・依存関係については本紙を参照してください。

## 概要
- **目的**: 既存のSlack MCPサーバー（`text2slack-mcp`）を導入し、Cursor等のAIエージェントがタスク完了時にSlackへメッセージを送信できるようにする。
- **背景**: 
  - AIエージェントによる開発効率化のため、タスク完了時の通知機能を追加
  - Cursor等のAIエージェントがMCPサーバー経由でSlackへ通知を送信できるようにする
  - 開発ワークフローの効率化を図る
  - **完全無料**: Slack Incoming Webhookは無料プランで利用可能
  - **既存サービス採用**: 自前実装ではなく、既存のnpmパッケージ（`text2slack-mcp`）を使用
- **作成日**: 2025-01-XX
- **完了日**: 2025-01-XX

## 技術スタック

### 使用パッケージ
- **text2slack-mcp**: 既存のnpmパッケージ（MCPサーバー実装済み）
  - GitHub: https://github.com/yk-lab/text2slack-mcp
  - npm: https://www.npmjs.com/package/text2slack-mcp
  - バージョン: 0.1.3（最新版を使用）

### 前提条件
- **Node.js**: v20.0.0 以降（`text2slack-mcp`の要件）
- **npm**: 9.0.0 以降（推奨）
- **Cursor**: MCPサーバーをサポートするバージョン
- **Slackアカウント**: Incoming Webhook URLの取得に必要（無料プランで利用可能）

## 導入計画

### Phase 1: 調査・設計
- **期間**: 1-2日
- **内容**:
  - Slack Incoming Webhook APIの仕様確認
  - MCPサーバーの実装方法の調査
  - セキュリティ要件の確認
  - 実装設計の作成
- **成果物**:
  - 実装設計書
  - セキュリティ要件書

### Phase 2: 既存サービスの選定・確認
- **期間**: 1日
- **内容**:
  - 既存のSlack MCPサーバーサービスの調査
  - `text2slack-mcp`の選定
  - 設定方法の確認
- **成果物**:
  - 既存サービスの選定結果
  - 設定方法の確認結果

### Phase 3: 設定・統合
- **期間**: 1-2日
- **内容**:
  - Cursor設定ファイル（`mcp.json`）への追加
  - Slack Incoming Webhook URLの取得・設定
  - 動作確認
- **成果物**:
  - 更新されたCursor設定ファイル
  - 動作確認結果

### Phase 4: ドキュメント化
- **期間**: 1-2日
- **内容**:
  - 導入・使用ガイドの作成（`docs/guidelines/MCP_SERVERS.md`に統合）
  - セキュリティ設定ガイドの作成
  - トラブルシューティングガイドの作成
  - 使用例の整理
- **成果物**:
  - `docs/guidelines/MCP_SERVERS.md`（統合ガイド）
  - 本計画書の完成

## 実装設計

### 使用する既存サービス
- **text2slack-mcp**: npmパッケージとして公開されているMCPサーバー
  - 自前実装不要
  - `npx`で直接実行可能
  - メンテナンス不要（パッケージの更新に追従）

### MCPサーバーの機能

#### 提供するツール
1. **`send_to_slack`**
   - **説明**: Slack Incoming Webhook経由でメッセージを送信
   - **パラメータ**:
     - `message` (string, 必須): 送信するメッセージ
   - **戻り値**: 送信結果（成功/失敗）

#### 実装のポイント
- **セキュリティ**: Webhook URLは環境変数で管理（`mcp.json`の`env`セクションに設定）
- **エラーハンドリング**: パッケージ側で実装済み
- **レート制限**: Slack Incoming Webhookのレート制限（1秒あたり1リクエスト程度）を考慮
- **完全無料**: Slack Incoming Webhookは無料プランで利用可能

### 設定ファイル例

#### Cursor設定ファイル（`mcp.json`）
```json
{
  "mcpServers": {
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@cyanheads/git-mcp-server"
      ],
      "enabled": true
    },
    "text2slack": {
      "command": "npx",
      "args": [
        "-y",
        "text2slack-mcp@latest"
      ],
      "enabled": true,
      "env": {
        "SLACK_WEBHOOK_URL": "your-webhook-url-here"
      }
    }
  }
}
```

**注意**: 
- `SLACK_WEBHOOK_URL`は環境変数で管理（`mcp.json`の`env`セクションに設定）
- `text2slack-mcp@latest`で最新版を使用
- `npx`で直接実行するため、事前のインストール不要

## Slack Incoming Webhook URLの取得方法

### 手順
1. **Slackアプリを開く**
   - [Slack](https://slack.com/)にログイン
   - 通知を送信したいワークスペースを選択

2. **Incoming Webhookアプリを追加**
   - ワークスペース名をクリック → 「設定と管理」→ 「アプリを管理」
   - または、直接 [Slack App Directory](https://slack.com/apps) にアクセス
   - 「Incoming Webhook」を検索して追加

3. **Incoming Webhookを設定**
   - 「Incoming Webhookを追加」をクリック
   - 通知を送信したいチャンネルを選択（例: #general, #notifications）
   - 「Incoming Webhook統合を追加」をクリック

4. **Webhook URLをコピー**
   - 表示された「Webhook URL」をコピー
   - 取得したURLは環境変数で管理（形式: `https://hooks.slack.com/services/...`）

5. **Webhook URLを保存**
   - コピーしたURLを安全に保管（再表示可能）

### セキュリティ注意事項
- Webhook URLは機密情報として扱う
- URLが漏洩した場合は、Slackのアプリ管理からIncoming Webhookを削除して再作成
- URLは環境変数で管理し、Gitリポジトリにコミットしない

## 使用方法

### 基本的な使用例

#### 例1: タスク完了時の通知
```
AIタスクが完了しました。以下のメッセージをSlackに送信してください：
「テストカバレッジ増強作業が完了しました。現在のカバレッジ: 98.65%」
```

#### 例2: エラー発生時の通知
```
エラーが発生しました。以下のメッセージをSlackに送信してください：
「エラー: テスト実行中にエラーが発生しました。詳細を確認してください。」
```

### メッセージフォーマット

Slack Incoming Webhookでは、以下の形式でメッセージを送信できます：

- **テキストメッセージ**: 通常のテキスト（最大4000文字）
- **改行**: `\n`で改行可能
- **絵文字**: Unicode絵文字、Slack絵文字を使用可能
- **Markdown**: SlackのMarkdown記法が使用可能
  - `*太字*` → **太字**
  - `_イタリック_` → *イタリック*
  - `` `コード` `` → `コード`
  - `> 引用` → 引用ブロック

### 使用例（メッセージテンプレート）

```javascript
// タスク完了通知
"✅ *タスク完了*\n\nタスク: {タスク名}\n完了時刻: {時刻}\n詳細: {詳細}"

// エラー通知
"❌ *エラー発生*\n\nエラー内容: {エラー内容}\n発生時刻: {時刻}"

// 進捗通知
"📊 *進捗報告*\n\n進捗: {進捗率}%\n残りタスク: {残りタスク数}"
```

## セキュリティ考慮事項

### 1. Webhook URLの管理
- **環境変数での管理**: Webhook URLは環境変数で管理（`.env`ファイルやシステム環境変数）
- **Git管理外**: URLを含むファイルは`.gitignore`に追加
- **権限設定**: `mcp.json`ファイルの読み取り権限を適切に設定

### 2. 送信先の制限
- Slack Incoming Webhookでは、Webhook URLに紐づいたチャンネルにのみ送信
- 誤送信を防ぐため、テスト用と本番用でWebhook URLを分けることを推奨

### 3. レート制限
- Slack Incoming Webhookのレート制限: 1秒あたり1リクエスト程度
- 個人利用では通常問題にならないが、大量送信の場合は考慮が必要

### 4. エラーハンドリング
- API呼び出し失敗時の適切なエラーメッセージ
- Webhook URL無効時の再作成案内

## トラブルシューティング

### MCPサーバーが接続されない
- **原因**: Node.jsのパスが正しくない、または依存関係がインストールされていない
- **対処**: 
  - Node.jsのパスを確認（`node --version`）
  - `npm install`で依存関係をインストール
  - Cursorを再起動

### メッセージが送信されない
- **原因**: Webhook URLが無効、またはネットワークエラー
- **対処**:
  - Webhook URLの有効性を確認
  - Slackのアプリ管理でIncoming Webhookの状態を確認
  - ネットワーク接続を確認

### エラーメッセージが表示される
- **原因**: API呼び出しエラー、またはパラメータエラー
- **対処**:
  - エラーメッセージの内容を確認
  - メッセージの長さ制限（4000文字）を確認
  - Webhook URLの権限を確認

### 429エラー（レート制限）
- **原因**: レート制限に達した
- **対処**:
  - 1秒あたり1リクエスト以内に制限
  - しばらく待ってから再試行

## 料金について

**Slack Incoming Webhookは無料プランで利用可能です。**

- **無料プラン**: 
  - メッセージ履歴: 最新90日間
  - アプリ統合: 10個まで
  - ストレージ: 5GB
  - **Incoming Webhook: 利用可能**
- **有料プラン**: メッセージ履歴の無制限保存など追加機能あり

## 完了状況

### ✅ Phase 1: 調査・設計（完了）
- [x] Slack Incoming Webhook APIの仕様確認
- [x] 既存のSlack MCPサーバーサービスの調査
- [x] セキュリティ要件の確認
- [x] 既存サービス（`text2slack-mcp`）の選定

### ✅ Phase 2: 既存サービスの選定・確認（完了）
- [x] 既存のSlack MCPサーバーサービスの調査
- [x] `text2slack-mcp`の選定
- [x] 設定方法の確認

### ✅ Phase 3: 設定・統合（完了）
- [x] Cursor設定ファイル（`mcp.json`）への追加（完了）
- [x] Slack Incoming Webhook URLの取得・設定（完了）
- [x] 動作確認（完了）

**注意**: Phase 3の設定作業は完了しました。Cursorを再起動後、MCPサーバーが認識されれば、AIアシスタントから直接メッセージを送信できます。

### ✅ Phase 4: ドキュメント化（完了）
- [x] 導入・使用ガイドの作成（`docs/guidelines/MCP_SERVERS.md`に統合）
- [x] セキュリティ設定ガイドの作成
- [x] トラブルシューティングガイドの作成
- [x] 使用例の整理
- [x] 計画書の更新（既存サービス使用に変更）

## 参考資料

- [text2slack-mcp npmパッケージ](https://www.npmjs.com/package/text2slack-mcp)
- [text2slack-mcp GitHub](https://github.com/yk-lab/text2slack-mcp)
- [Slack Incoming Webhook 公式ドキュメント](https://api.slack.com/messaging/webhooks)
- [Slack App Directory](https://slack.com/apps)
- [Model Context Protocol (MCP) 公式ドキュメント](https://modelcontextprotocol.io/)
- [Git MCPサーバー導入計画](./Git_MCPサーバー導入計画.md)
- [MCPサーバー 統合ガイド](../guidelines/MCP_SERVERS.md)

## 更新履歴

- 2025-01-XX: 初版作成（完全無料のSlack Incoming Webhook対応）
- 2025-01-XX: Phase 1, Phase 2完了。依存関係インストール完了。導入・使用ガイド作成完了。
- 2025-01-XX: 文字化け修正完了（Content-Typeヘッダーにcharset=utf-8を追加）。動作確認完了。
- 2025-01-XX: **既存サービス（text2slack-mcp）に切り替え**。自前実装を削除し、既存のnpmパッケージを使用する方式に変更。

