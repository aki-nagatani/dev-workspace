# MCPサーバー 統合ガイド

## 概要

このドキュメントは、Cursor等のAIエージェントで使用するMCP（Model Context Protocol）サーバーの導入方法と使用方法を説明します。

本プロジェクトでは、以下のMCPサーバーを使用しています：

1. **Git MCPサーバー** (`@cyanheads/git-mcp-server`): Gitリポジトリの操作を自然言語で実行
2. **Slack Webhook MCPサーバー** (`text2slack-mcp`): Slack Incoming Webhook経由でメッセージを送信

MCPサーバーを使用することで、AIエージェントが外部ツールやサービスと連携し、開発ワークフローが効率化されます。

## 前提条件

### 共通要件

- **Node.js**: v20.0.0 以降（推奨）
  - Git MCPサーバー: v24.11.1 以降（推奨）
  - Slack Webhook MCPサーバー: v20.0.0 以降（`text2slack-mcp`の要件）
- **npm**: 9.0.0 以降（推奨）
- **Cursor**: MCPサーバーをサポートするバージョン

### 各サーバーの追加要件

- **Git MCPサーバー**: Git 2.51.0 以降（推奨）
- **Slack Webhook MCPサーバー**: Slackアカウント（Incoming Webhook URLの取得に必要、無料プランで利用可能）

## Cursor設定ファイル

### 設定ファイルの場所

**Windows**:
```
C:\Users\<ユーザー名>\AppData\Roaming\Cursor\User\mcp.json
```

### 設定内容

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
- `SLACK_WEBHOOK_URL`は実際のWebhook URLに置き換えてください
- Webhook URLは機密情報のため、Gitリポジトリにコミットしないでください

### 設定後の再起動

設定ファイルを作成または変更した後は、Cursorを完全に再起動してください：
- すべてのCursorウィンドウを閉じる
- タスクマネージャーでCursorプロセスが残っていないか確認
- Cursorを起動し、プロジェクトを開く

---

## Git MCPサーバー

### 導入方法

#### インストール手順

1. **Node.jsのインストール確認**
   ```bash
   node --version
   npm --version
   ```
   Node.jsがインストールされていない場合は、[Node.js公式サイト](https://nodejs.org/)からインストールしてください。

2. **Cursor設定ファイルの設定**
   
   上記の設定ファイルに`git`サーバーの設定を追加します。`npx`経由で自動的にインストール・実行されるため、追加のインストールは不要です。

3. **動作確認**
   
   CursorのAIアシスタントに「現在のGitリポジトリの状態を確認してください」と依頼し、正常に動作することを確認してください。

### 使用方法

#### 基本的なGit操作

AIアシスタントに以下のような指示をすることで、Git操作を実行できます：

##### リポジトリの状態確認
```
現在のGitリポジトリの状態を確認してください
```
または
```
git statusを実行して、現在のブランチと変更されたファイルを教えてください
```

##### コミット履歴の確認
```
最新の5件のコミット履歴を表示してください
```
または
```
git logで最新のコミット履歴を教えてください
```

##### 変更内容の確認
```
現在の変更内容の差分を表示してください
```
または
```
git diffで変更された内容を教えてください
```

##### ファイルのステージング
```
dev-workspace/docs/plans/completed/Git_MCPサーバー導入計画.mdをステージングしてください
```

##### コミットの作成
```
変更をコミットしてください。コミットメッセージは「docs: 計画書の更新」としてください
```

##### リモートへのプッシュ
```
リモートリポジトリにプッシュしてください
```

#### よく使う操作の例

##### 1. 変更の確認とコミット
```
1. 現在の変更内容を確認してください
2. 変更をステージングしてください
3. 適切なコミットメッセージでコミットしてください
```

##### 2. コミット履歴の確認
```
最新の10件のコミット履歴を表示してください。各コミットのハッシュ、メッセージ、作成者、日時を含めてください
```

##### 3. 特定のコミットの詳細確認
```
コミットハッシュ c456c5a の詳細を表示してください
```

##### 4. ブランチ操作
```
現在のブランチを確認してください
```
```
ブランチ一覧を表示してください
```

##### 5. リモート情報の確認
```
リモートリポジトリの情報を確認してください
```

#### AIアシスタントへの指示例

##### 例1: 計画書の更新とコミット
```
計画書（dev-workspace/docs/plans/completed/Git_MCPサーバー導入計画.md）を更新しました。
以下の手順でコミットしてください：
1. 変更内容を確認
2. 変更をステージング
3. コミットメッセージ「docs: Git MCPサーバー導入計画の更新」でコミット
4. リモートにプッシュ
```

##### 例2: 変更内容の確認
```
現在の変更内容を確認して、以下の情報を教えてください：
- 変更されたファイルのリスト
- 各ファイルの変更行数（追加・削除）
- 変更内容の概要
```

##### 例3: コミット履歴の分析
```
最新の20件のコミット履歴を分析して、以下の情報を教えてください：
- 最も頻繁に変更されているファイル
- コミットの傾向（機能追加、バグ修正、ドキュメント更新など）
- 最近の開発活動の概要
```

### セキュリティ設定

#### 1. Force Pushの制限

**問題**: `git push --force`は、リモートリポジトリの履歴を上書きする危険な操作です。

**対策**:

##### ローカルGit設定（推奨）

```bash
# push.defaultをsimpleに設定（デフォルトのブランチのみpush）
git config --global push.default simple

# followTagsを無効化（タグの自動pushを防止）
git config --global push.followTags false
```

**注意**: これらの設定はローカルでの誤操作を防ぐためのものであり、リモートリポジトリ（GitHub）でのforce pushを完全に防ぐものではありません。

##### GitHubブランチ保護設定（最重要）

GitHubのブランチ保護設定により、リモートリポジトリでのforce pushを制限できます：

1. **GitHub Web UIでの設定**:
   - リポジトリの **Settings** → **Branches** → **Branch protection rules**
   - `main`ブランチに対して以下を設定：
     - ✅ **Require a pull request before merging**（PR必須）
     - ✅ **Require status checks to pass before merging**（必須チェック通過）
     - ⚠️ **Restrict who can push to matching branches**（オプション、管理者のみ許可）

2. **Force Pushの制限**:
   - ブランチ保護設定により、`main`ブランチへのforce pushは自動的に拒否されます
   - 管理者でもforce pushは制限されます（設定による）

**参考**: 詳細は `docs/specifications/MyPokedex.md` の「ブランチ保護設定」セクションを参照してください。

#### 2. 本番ブランチ（main）への直接操作の制限

**問題**: 本番ブランチへの直接操作は、本番環境に影響を与える可能性があります。

**対策**:

##### プロジェクト方針

本プロジェクトでは、`docs/guidelines/AGENTS.md`に記載されている通り、**mainブランチのみを使用する運用**としています：

- **ブランチ作成の禁止**: 新規ブランチ（featureブランチ、developブランチ等）を作成しない
- **mainブランチへの直接コミット**: すべての変更はmainブランチに直接コミットする
- **PR（Pull Request）の使用**: PRは使用しない（mainブランチへの直接コミットのみ）

**注意**: この方針は、ソロ開発のため、ブランチ分岐による複雑性が不要であることを理由としています。

##### MCPサーバー経由での操作

MCPサーバー経由でGit操作を実行する際は、以下の点に注意してください：

1. **コミット前の確認**: コミット前に`git status`で変更内容を確認
2. **コミットメッセージの確認**: コミットメッセージが適切であることを確認
3. **プッシュ前の確認**: プッシュ前に`git log`でコミット履歴を確認

#### 3. ローカルリポジトリの保護設定

以下の設定により、ローカルリポジトリでの誤操作を防ぐことができます：

```bash
# 非fast-forwardマージを拒否（ローカルリポジトリのみ）
git config --global receive.denyNonFastForwards true

# ブランチ削除を拒否（ローカルリポジトリのみ）
git config --global receive.denyDeletes true
```

**注意**: これらの設定はローカルリポジトリ（`receive`）での操作を制限するものであり、リモートリポジトリ（GitHub）には適用されません。

#### 4. 機密情報の保護

##### 認証情報の管理

**問題**: Git操作時に認証情報（パスワード、トークンなど）がログに出力される可能性があります。

**対策**:

1. **Git認証情報の管理**:
   - Git認証情報は、環境変数またはGit Credential Managerで管理
   - 認証情報をコマンドライン引数やコミットメッセージに含めない

2. **MCPサーバーのログ出力**:
   - MCPサーバーは、認証情報をログに出力しない設計になっています
   - ただし、設定ファイルやコマンドライン引数に認証情報を含めないよう注意してください

##### 推奨設定

```bash
# Git Credential Managerを使用（Windows）
git config --global credential.helper manager-core

# 認証情報のキャッシュ時間を設定（オプション）
git config --global credential.helper 'cache --timeout=3600'
```

##### 設定ファイルの保護

**問題**: MCPサーバーの設定ファイル（`mcp.json`）に機密情報を含めないよう注意してください。

**対策**:

1. **設定ファイルの確認**:
   - `C:\Users\<ユーザー名>\AppData\Roaming\Cursor\User\mcp.json`に機密情報が含まれていないか確認
   - 現在の設定ファイルには機密情報は含まれていません（`npx`経由で実行）

2. **環境変数の使用**:
   - 必要に応じて、環境変数で認証情報を管理
   - 設定ファイルには環境変数の参照のみを含める

#### 5. 操作ログの記録

##### MCPサーバーのログ確認

**方法**:

1. **Cursor Developer Tools**:
   - `Help > Toggle Developer Tools` → `Console`タブ
   - MCPサーバー関連のログを確認

2. **MCPサーバーのログ出力**:
   - MCPサーバーは、stdio transportで動作しているため、ログはCursorのDeveloper Toolsに出力されます
   - エラーログや警告ログを定期的に確認してください

##### Git操作のログ記録

**方法**:

1. **Git操作の履歴確認**:
   ```bash
   # コミット履歴の確認
   git log --oneline

   # リモート操作の履歴確認
   git reflog
   ```

2. **MCPサーバー経由での操作履歴**:
   - MCPサーバー経由でのGit操作は、通常のGit操作と同じように履歴に記録されます
   - `git log`や`git reflog`で操作履歴を確認できます

#### セキュリティチェックリスト

##### 導入時

- [ ] Git設定でforce pushを制限（`push.default=simple`）
- [ ] GitHubブランチ保護設定を確認・設定
- [ ] MCPサーバーの設定ファイルに機密情報が含まれていないか確認
- [ ] Git認証情報の管理方法を確認

##### 定期的な確認

- [ ] Cursor Developer ToolsでMCPサーバーのエラーログを確認
- [ ] Git操作の履歴（`git log`、`git reflog`）を確認
- [ ] ブランチ保護設定が有効であることを確認
- [ ] 認証情報が適切に管理されていることを確認

### 注意事項

#### プロジェクト方針との整合性

本プロジェクトでは、`docs/guidelines/AGENTS.md`に記載されている通り、**mainブランチのみを使用する運用**としています：

- **ブランチ作成の禁止**: 新規ブランチ（featureブランチ、developブランチ等）を作成しない
- **mainブランチへの直接コミット**: すべての変更はmainブランチに直接コミットする
- **PR（Pull Request）の使用**: PRは使用しない（mainブランチへの直接コミットのみ）

MCPサーバー経由でGit操作を実行する際も、この方針に従ってください。

#### コミットメッセージ

- コミットメッセージは明確で、変更内容を適切に説明するものにしてください
- プロジェクトのコミットメッセージ規約に従ってください

---

## Slack Webhook MCPサーバー

### 導入方法

#### インストール手順

1. **Slack Incoming Webhook URLの取得**

   - [Slack App Directory](https://slack.com/apps) にアクセス
   - 「Incoming Webhook」を検索して追加
   - チャンネルを選択してWebhook URLを取得
   - 取得したURLは環境変数で管理（形式: `https://hooks.slack.com/services/...`）

2. **Cursor設定ファイルの設定**

   上記の設定ファイルに`text2slack`サーバーの設定を追加します。`npx`経由で自動的にインストール・実行されるため、追加のインストールは不要です。

   **設定例**:
   ```json
   {
     "mcpServers": {
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

3. **動作確認**

   CursorのAIアシスタントに「以下のメッセージをSlackに送信してください：テストメッセージ」と依頼し、正常に動作することを確認してください。

### 使用方法

#### 基本的な使用例

AIアシスタントに以下のように指示します：

```
以下のメッセージをSlackに送信してください：
「テストカバレッジ増強作業が完了しました。現在のカバレッジ: 98.65%」
```

#### メッセージフォーマット

**作業完了通知のフォーマット**（400文字基準）

作業完了通知は、**400文字程度（350-420文字を目安、許容範囲300-450文字）**で以下の情報を含めること：

```
✅ 作業完了: [作業名]
プロジェクト: [プロジェクト名]
変更ファイル: [ファイル数] ([主要なファイル名、詳細がある場合は説明])
実施内容: [実施内容の詳細説明 - 技術的な詳細、使用した技術、設計判断など]
結果: [結果・動作確認結果 - テスト結果、パフォーマンス改善、影響範囲など]
```

**含めるべき情報**:

1. **作業名**: 何をしたか（必須）
2. **プロジェクト名**: どのプロジェクトか（MyHobbySite、FishTrack、MyPokedexなど）
3. **変更ファイル**: ファイル数と主要なファイル名（長い場合は省略または代表的なもの）
4. **実施内容**: 何を実施したかの詳細説明
   - 技術的な詳細（使用したライブラリ、フレームワークなど）
   - 設計判断やアーキテクチャの変更
   - 修正内容の詳細
5. **結果**: 動作確認結果、テスト結果、パフォーマンス改善、エラーや警告の有無、本番環境への影響など

**文字数の目安**:

- **目標**: 350-420文字程度
- **最適範囲**: 380-420文字（推奨）
- **許容範囲**: 300-450文字
- **最大**: 500文字程度（読みやすさを優先）

**メッセージの構成比率（目安）**:

- **作業名**: 約20-30文字（5%）
- **プロジェクト名**: 約20-40文字（5-10%）
- **変更ファイル**: 約50-100文字（12-25%）
- **実施内容**: 約150-200文字（40-50%）
- **結果**: 約100-150文字（25-40%）

**Slack Incoming Webhookで使用可能な形式**:

- **テキストメッセージ**: 通常のテキスト（最大4000文字）
- **改行**: `\n`で改行可能
- **絵文字**: Unicode絵文字、Slack絵文字を使用可能
- **Markdown**: SlackのMarkdown記法が使用可能
  - `*太字*` → **太字**
  - `_イタリック_` → *イタリック*
  - `` `コード` `` → `コード`
  - `> 引用` → 引用ブロック

#### 使用例

##### 作業完了通知（推奨フォーマット）

**例1: nginx設定修正（367文字）**
```
✅ 作業完了: nginx設定修正
プロジェクト: MyHobbySite
変更ファイル: 1ファイル (docs/plans/temp/nginx_static_files_fix.md)
実施内容: nginx静的ファイル配信設定を追加。FishTrack/MyPokedexの静的ファイル(/static/)が正常に配信されるよう修正。locationブロックを追加し、キャッシュ設定（30日）やセキュリティヘッダー（X-Content-Type-Options）も設定。パーミッション調整も実施（/home/piを751に変更）。nginx設定のバックアップも作成。
結果: curlで確認済み、HTTP/2 200を確認。静的ファイル配信が正常に動作することを確認。nginx -tで設定検証も完了。本番環境への反映も完了。
```

**例2: テストカバレッジ増強（329文字）**
```
✅ 作業完了: テストカバレッジ増強
プロジェクト: MyPokedex
変更ファイル: 5ファイル（認証機能関連のテストを追加: test_auth_routes.py, test_auth_models.py等）
実施内容: ユーザー認証機能のテストを追加。ログイン/ログアウト/パスワードリセットのテストケースを実装。正常系・異常系の両方を網羅し、エッジケースもテスト。モックを使用して外部依存を排除。pytest fixturesも適切に設定。テストデータの準備も自動化。
結果: 全テスト通過（pytest -n autoで並列実行確認済み）、カバレッジ98.65%達成（目標95%超過）。テスト実行時間も30%短縮。カバレッジレポートも生成済み。
```

**例3: バグ修正とリファクタリング（353文字）**
```
✅ 作業完了: バグ修正とリファクタリング
プロジェクト: FishTrack
変更ファイル: 3ファイル (src/fishtrack/blueprints/auth/routes.py, src/fishtrack/models/user.py, src/fishtrack/services/auth_service.py)
実施内容: ログイン機能の不具合を修正。セッション管理の問題を特定し、ログイン状態が正しく保持されるよう修正。パスワード検証ロジックの改善も実施。認証処理をサービス層に分離し、コードの可読性を向上。DRY原則に従って重複コードを削減。
結果: 修正完了、動作確認済み。テストも更新し、全テスト通過を確認。本番環境への影響なし。コードレビューも実施済み。リンターエラーも解消。
```

**例4: 機能追加（379文字）**
```
✅ 作業完了: 機能追加 - ユーザー認証機能を実装
プロジェクト: MyPokedex
変更ファイル: 10ファイル（routes.py, models.py, forms.py, services/auth_service.py, templates/login.html, templates/register.html等）
実施内容: ユーザー認証機能を実装。ログイン/ログアウト/パスワードリセット機能を追加。Flask-Loginを使用してセッション管理を実装。パスワードハッシュ化も実装（bcrypt使用）。CSRF保護も追加。UIはBootstrapを使用してモダンなデザインに。レスポンシブ対応も実施。
結果: 機能実装完了、テストも追加（認証機能のテストカバレッジ95%達成）。動作確認済み。セキュリティテストも実施。ドキュメントも更新。
```

**例5: パフォーマンス改善（379文字）**
```
✅ 作業完了: エラー修正とパフォーマンス改善
プロジェクト: FishTrack
変更ファイル: 4ファイル（routes.py, services/tackle_service.py, models/tackle.py, templates/index.html）
実施内容: データベースクエリのN+1問題を修正。バルクロードを使用してクエリ数を削減。インデックスの追加も実施（tackleテーブルにuser_id, created_atにインデックス追加）。エラーハンドリングを改善し、適切なログ出力を実装。ページネーションも最適化。キャッシュの活用も検討。
結果: 修正完了、パフォーマンステスト実施。クエリ数が70%削減（100クエリ→30クエリ）。レスポンス時間も50%改善（2秒→1秒）。全テスト通過。動作確認済み。本番環境への反映準備完了。
```

##### 実装時の注意点

1. **情報の優先順位**: 重要な情報を優先的に含める
2. **読みやすさ**: 改行を適切に使用して読みやすくする（5行程度を推奨）
3. **省略の判断**: 
   - ファイル名が長すぎる場合は主要なものだけ記載
   - ファイルが多い場合は「等」で省略
   - 技術的な詳細は重要なものだけ記載
4. **エラー情報**: エラーが発生した場合は必ず含める
5. **数値の記載**: パフォーマンス改善などは具体的な数値を含める（例：70%削減、2秒→1秒）
6. **Markdown活用**: 必要に応じて太字（`*太字*`）を使用（ただし、絵文字で十分な場合は不要）

##### エラー通知（従来通り使用可能）

```
❌ *エラー発生*

エラー内容: テスト実行中にエラーが発生
発生時刻: 2025-01-XX 12:00
```

##### 進捗通知（従来通り使用可能）

```
📊 *進捗報告*

進捗: 75%
残りタスク: 5件
```

### セキュリティ設定

#### Webhook URLの管理

**問題**: Webhook URLは機密情報として扱う必要があります。

**対策**:

##### 方法1: Cursor設定ファイル（`mcp.json`）

```json
{
  "mcpServers": {
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
- `mcp.json`に直接URLを記載する場合は、ファイルの読み取り権限を適切に設定してください
- ファイルの権限設定（Windows）: ファイルのプロパティ → セキュリティ → アクセス許可を制限

##### 方法2: システム環境変数（推奨）

**Windows (PowerShell)**:
```powershell
# 一時的な設定（現在のセッションのみ）
$env:SLACK_WEBHOOK_URL = "your-webhook-url-here"

# 永続的な設定（ユーザー環境変数）
[System.Environment]::SetEnvironmentVariable("SLACK_WEBHOOK_URL", "your-webhook-url-here", "User")
```

**Linux/macOS**:
```bash
# 一時的な設定（現在のセッションのみ）
export SLACK_WEBHOOK_URL="your-webhook-url-here"

# 永続的な設定（~/.bashrc または ~/.zshrc に追加）
echo 'export SLACK_WEBHOOK_URL="your-webhook-url-here"' >> ~/.bashrc
```

#### Webhook URLが漏洩した場合

1. **Slackのアプリ管理からIncoming Webhookを削除**
   - ワークスペース名 → 「設定と管理」→ 「アプリを管理」
   - 「Incoming Webhook」を検索
   - 該当するWebhookを削除

2. **新しいWebhook URLを発行**
   - 同じ手順で新しいWebhook URLを取得

3. **環境変数や設定ファイルを更新**
   - 新しいWebhook URLに更新

---

## トラブルシューティング

### MCPサーバーが接続されない

**症状**: AIアシスタントがMCPサーバーの操作を実行できない、または「MCP server "xxx" is not available」というエラーが表示される

**対処法**:

1. **設定ファイルの確認**
   - `mcp.json`のパスが正しいか確認
   - JSON構文が正しいか確認（カンマ、引用符など）
   - ファイルのエンコーディングがUTF-8か確認
   - BOM（Byte Order Mark）が含まれていないか確認

2. **Node.js/npmの確認**
   ```bash
   node --version
   npm --version
   ```
   - Node.js v20.0.0以降、npm 9.0.0以降であることを確認

3. **Cursorの再起動**
   - Cursorを完全に終了
   - タスクマネージャーでCursorプロセスが残っていないか確認
   - Cursorを起動し直す

4. **Developer Toolsでログ確認**
   - `Help > Toggle Developer Tools` → `Console`タブ
   - MCPサーバー関連のエラーメッセージを確認

### Git操作が実行されない

**症状**: AIアシスタントにGit操作を依頼しても実行されない

**対処法**:

1. **リポジトリ内でCursorを開いているか確認**
   - GitリポジトリのルートディレクトリでCursorを開いていることを確認

2. **Gitのインストール確認**
   ```bash
   git --version
   ```
   - Gitがインストールされていることを確認

3. **Git設定の確認**
   ```bash
   git config --list
   ```
   - ユーザー名とメールアドレスが設定されていることを確認

### Git操作でエラーメッセージが表示される

**症状**: Git操作を実行するとエラーメッセージが表示される

**対処法**:

1. **エラーメッセージの内容を確認**
   - エラーメッセージの内容を記録
   - エラーメッセージから原因を特定

2. **通常のGitコマンドで確認**
   ```bash
   git status
   git log
   ```
   - 通常のGitコマンドで同じ操作が可能か確認
   - 通常のGitコマンドでもエラーが発生する場合は、Git環境の問題

3. **MCPサーバーのログ確認**
   - Cursor Developer ToolsでMCPサーバーのログを確認
   - エラーの詳細を確認

### ブランチ削除時のエラー

**症状**: `git_branch`でブランチを削除する際、スキーマエラーが発生する

**対処法**:
- 通常のgitコマンド（`git branch -d <ブランチ名>`）で削除可能
- この問題は軽微で、通常のgitコマンドで代替可能

### Slackメッセージが送信されない

**症状**: AIアシスタントにメッセージ送信を依頼しても送信されない

**対処法**:

1. **Webhook URLの確認**
   - Webhook URLが正しく設定されているか確認
   - Slackのアプリ管理でIncoming Webhookの状態を確認

2. **ネットワーク接続の確認**
   - インターネット接続を確認

3. **エラーメッセージの確認**
   - Cursor Developer Toolsでエラーメッセージを確認
   - `Help > Toggle Developer Tools` → `Console`タブ

### Slackメッセージ送信時にエラーメッセージが表示される

**症状**: メッセージ送信時にエラーメッセージが表示される

**対処法**:

1. **エラーメッセージの内容を確認**
   - エラーメッセージから原因を特定

2. **メッセージの長さ制限**
   - メッセージが4000文字以内か確認

3. **Webhook URLの権限**
   - Webhook URLが有効か確認
   - Incoming Webhookが削除されていないか確認

### 429エラー（レート制限）

**症状**: レート制限エラーが表示される

**対処法**:
- 1秒あたり1リクエスト以内に制限
- しばらく待ってから再試行

### Force Pushが必要な場合

**注意**: 通常、force pushは不要です。以下の場合のみ検討してください：

1. **ローカルブランチの履歴修正**:
   - ローカルブランチの履歴を修正した後、リモートに反映する必要がある場合
   - **推奨**: 新しいブランチを作成してpushする方が安全です

2. **緊急時の対応**:
   - 誤ってコミットした機密情報を削除する必要がある場合
   - **推奨**: GitHubのサポートに連絡するか、新しいコミットで機密情報を無効化

### 認証エラーが発生した場合

1. **認証情報の確認**:
   - Git Credential Managerで認証情報を確認
   - 必要に応じて認証情報を再設定

2. **MCPサーバーの再起動**:
   - Cursorを再起動してMCPサーバーを再起動
   - 設定ファイルを確認

---

## 参考資料

### Git MCPサーバー

- [Git MCPサーバー導入計画](../../dev-workspace/docs/plans/completed/Git_MCPサーバー導入計画.md)
- [@cyanheads/git-mcp-server GitHubリポジトリ](https://github.com/cyanheads/git-mcp-server)

### Slack Webhook MCPサーバー

- [text2slack-mcp npmパッケージ](https://www.npmjs.com/package/text2slack-mcp)
- [text2slack-mcp GitHub](https://github.com/yk-lab/text2slack-mcp)
- [Slack Incoming Webhook 公式ドキュメント](https://api.slack.com/messaging/webhooks)
- [Slack App Directory](https://slack.com/apps)
- [Slack Webhook MCPサーバー導入計画](../../dev-workspace/docs/plans/completed/Slack_Webhook_MCPサーバー導入計画.md)

### 共通

- [Model Context Protocol (MCP) 公式ドキュメント](https://modelcontextprotocol.io/)
- [AIエージェントの動作ルール](AGENTS.md)
- [MyPokedex仕様書 - ブランチ保護設定](../specifications/MyPokedex.md)

## 更新履歴

- 2025-01-XX: 初版作成（3つのドキュメントを統合）
  - Git MCPサーバー 導入・使用ガイド
  - Git MCPサーバー セキュリティ設定ガイド
  - Slack Webhook MCPサーバー 導入・使用ガイド

