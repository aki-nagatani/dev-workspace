# Git MCPサーバー導入計画

> **📋 全体計画**: 本計画は `dev-workspace/docs/plans/MyHobbySite全体作業計画.md` の一部として位置づけられています。全体の作業計画・優先順位・依存関係については本紙を参照してください。

## 概要
- **目的**: Git MCPサーバー（`@cyanheads/git-mcp-server`）を導入し、Cursor等のAIエージェントがGitリポジトリの操作を自然言語で実行できるようにする。
- **背景**: 
  - AIエージェントによる開発効率化のため、Git操作を自然言語で実行できる環境を構築する
  - Cursor等のAIエージェントがMCPサーバー経由でGit操作を実行できるようにする
  - 開発ワークフローの効率化を図る
- **作成日**: 2025-01-XX
- **完了日**: 2025-01-XX

## 導入計画

### Phase 1: 調査・検討
- **期間**: 1週間
- **内容**:
  - MCPサーバーの仕様・機能の調査
  - 利用可能なGit MCPサーバーパッケージの調査
  - セキュリティ評価の実施
  - 導入可否の判断
- **成果物**:
  - MCPサーバーの調査結果
  - セキュリティ評価レポート
  - 導入方針の決定

### Phase 2: 導入・設定
- **期間**: 1週間
- **内容**:
  - Node.js/npmのインストール確認
  - Cursor設定ファイル（`mcp.json`）の作成
  - MCPサーバーの設定
  - 動作確認
- **成果物**:
  - Cursor設定ファイル
  - 動作確認結果

### Phase 3: ドキュメント化
- **期間**: 1週間
- **内容**:
  - 導入・使用ガイドの作成（`docs/guidelines/MCP_SERVERS.md`に統合）
  - セキュリティ設定ガイドの作成（`docs/guidelines/MCP_SERVERS.md`に統合）
  - トラブルシューティングガイドの作成
  - 使用例の整理
- **成果物**:
  - `docs/guidelines/MCP_SERVERS.md`（統合ガイド）
  - 本計画書の完成

## 完了状況

### ✅ Phase 1: 調査・検討（完了）
- MCPサーバーの仕様・機能の調査完了
- `@cyanheads/git-mcp-server` の選定完了
- セキュリティ評価完了（詳細は `docs/plans/テストカバレッジ増強計画.md` の付録を参照）

### ✅ Phase 2: 導入・設定（完了）
- Node.js/npmのインストール確認完了
- Cursor設定ファイル（`mcp.json`）の作成完了
- MCPサーバーの設定完了
- 動作確認完了

### ✅ Phase 3: ドキュメント化（完了）
- 導入・使用ガイド（`docs/guidelines/MCP_SERVERS.md`に統合）作成完了
- セキュリティ設定ガイド（`docs/guidelines/MCP_SERVERS.md`に統合）作成完了
- トラブルシューティングガイド作成完了
- 本計画書完成

## 技術スタック

### 使用パッケージ
- **`@cyanheads/git-mcp-server`**: v2.5.8
  - Git操作をMCPサーバー経由で実行可能にするパッケージ
  - npx経由で自動インストール・実行

### 前提条件
- **Node.js**: v24.11.1 以降（推奨）
- **npm**: 11.6.2 以降（推奨）
- **Git**: 2.51.0 以降（推奨）
- **Cursor**: MCPサーバーをサポートするバージョン

## 設定ファイル

### Cursor設定ファイル（`mcp.json`）
```json
{
  "mcpServers": {
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@cyanheads/git-mcp-server"
      ]
    }
  }
}
```

**保存場所**:
- **Windows**: `C:\Users\<ユーザー名>\AppData\Roaming\Cursor\User\mcp.json`

## 参考資料

- [MCPサーバー 統合ガイド](../guidelines/MCP_SERVERS.md)
- [@cyanheads/git-mcp-server GitHubリポジトリ](https://github.com/cyanheads/git-mcp-server)
- [MyHobbySite全体作業計画](https://github.com/aki-nagatani/dev-workspace/blob/main/docs/plans/MyHobbySite全体作業計画.md)

## 更新履歴

- 2025-01-XX: 初版作成
- 2025-01-XX: Phase 3完了、計画書完成

