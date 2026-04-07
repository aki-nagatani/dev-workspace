---
name: commit-message
description: コミットメッセージの作成ガイドラインとベストプラクティス。コンベンショナルコミット形式に従い、日本語で記述し、PowerShellでは BOM なし UTF-8 でファイルに書いてから -F で読み込み、文字化けを防止する。コミットメッセージを作成・確認・修正する際に使用する。
---

# コミットメッセージ作成ガイドライン

## 基本原則

### コンベンショナルコミット形式（必須）

```text
<type>: <subject>

<body>

<footer>
```

### 主なタイプ

- `feat:` - 新機能の追加
- `fix:` - バグ修正
- `docs:` - ドキュメント変更
- `test:` - テスト追加・修正
- `refactor:` - リファクタリング（機能変更なし）
- `chore:` - ビルド・設定変更
- `style:` - コードスタイル（動作に影響しない）
- `perf:` - パフォーマンス改善

## コミットメッセージの構造

### 推奨構造

1. **タイトル行（50文字以内）**
   - タイプと簡潔な説明
   - 動詞で始める（追加、修正、削除など）
   - 句読点なし

2. **本文（必要に応じて）**
   - 変更の理由と内容
   - 変更前後の比較
   - 影響範囲
   - srcの修正箇所を中心に記載

3. **フッター（必要に応じて）**
   - 関連Issue番号（`Closes #123`）
   - 破壊的変更の説明（`BREAKING CHANGE:`）

### 良い例

```text
feat: CAPTCHA導入（不正登録対策・ログイン連続失敗対策）

- hCaptcha/reCAPTCHA v3対応のCAPTCHA検証ユーティリティを追加
- 新規登録フォームにCAPTCHAウィジェットを追加
- ログイン連続失敗時にCAPTCHAを要求する機能を追加

実装内容:
- utils/captcha.py: CAPTCHA検証ユーティリティ
- blueprints/auth/routes.py: 新規登録・ログイン処理にCAPTCHA検証を追加
- templates/auth/register.html: 新規登録フォームにCAPTCHAウィジェットを追加

Closes #123
```

### 悪い例

```text
fix: バグ修正
```

```text
update: いろいろ修正した
```

```text
feat: CAPTCHA機能を追加しました。これは不正登録対策とログイン連続失敗対策のために実装したもので、hCaptchaとreCAPTCHA v3の両方に対応しています。
```

## プロジェクト固有のルール

### 言語・エンコーディングと文字化け対策

- **コミットメッセージは日本語で記述**
- **エンコーディングは BOM なし UTF-8（必須）**  
  - タイトル先頭に **UTF-8 BOM（`EF BB BF`）** が付くと、不可視文字が混ざり、**先頭マッチする自動チェック**（Conventional Commits 等）や**文字列比較**で不整合の原因になりうる。  
  - Windows PowerShell 5.1 の `Out-File -Encoding utf8` は **既定で BOM 付き**になりやすいため、**コミット用メッセージファイルには使わない**（下記の **BOM なし** の書き方を正とする）。
- **PowerShellでの文字化け防止**: 内容を **BOM なし UTF-8** のファイルに書き、**`git commit -F`** で読み込む

**PowerShell で BOM なし UTF-8 に書く方法（推奨・どの版でも安全）**:

```powershell
# プロジェクト直下ではなく temp/ 配下に置く（リポジトリの一時ファイル規約に合わせる）
$content = @"
feat: 変更の要約

- 本文行1
- 本文行2
"@
[System.IO.File]::WriteAllText(
    "temp/commit_msg.txt",
    $content,
    [System.Text.UTF8Encoding]::new($false)
)
git commit -F temp/commit_msg.txt
Remove-Item temp/commit_msg.txt  # 必須：削除
```

**PowerShell 7+ の場合**（`utf8NoBOM` が使える環境のみ）:

```powershell
@"
feat: 変更の要約
"@ | Out-File -FilePath temp/commit_msg.txt -Encoding utf8NoBOM
git commit -F temp/commit_msg.txt
Remove-Item temp/commit_msg.txt
```

### コミットメッセージの確認

- コミット後に文字化けしていないか確認
- 文字化けしている場合は修正（`git commit --amend`）

### 一時ファイルの管理

- コミットメッセージ用テキストファイルは `temp/` 配下に作成
- コミット完了後は必ず削除

## ベストプラクティス

### 1. 1つのコミットは1つの変更に集中

- 複数の変更を1つのコミットにまとめない
- 関連する変更はまとめるが、無関係な変更は分離

### 2. タイトルは命令形で記述

- ✅ 良い: `feat: ユーザー認証機能を追加`
- ❌ 悪い: `feat: ユーザー認証機能を追加しました`

### 3. 本文では「なぜ」と「何を」を説明

- 変更の理由を明確に
- 変更内容を具体的に
- srcの修正箇所を中心に記載

### 4. 関連するIssueやPR番号を記載

- `Closes #123`
- `Refs #456`
- `Related to #789`

### 5. 破壊的変更は明示

```text
feat: APIエンドポイントの変更

BREAKING CHANGE: /api/v1/users エンドポイントが削除されました。
代わりに /api/v2/users を使用してください。
```

## 作成時のチェックリスト

- [ ] コンベンショナルコミット形式に従っているか
- [ ] タイトルは50文字以内か
- [ ] 日本語で記述されているか
- [ ] srcの修正箇所を中心に記載されているか
- [ ] 変更の理由と内容が明確か
- [ ] 関連するIssue番号が記載されているか（該当する場合）
- [ ] 破壊的変更がある場合は明示されているか（該当する場合）
- [ ] PowerShellでの文字化け対策が実施されているか（`-F` でファイルから読み込み、かつ **BOM なし UTF-8** で保存）
- [ ] 一時ファイルは `temp/` 配下に作成されているか
- [ ] コミット後に文字化けしていないか確認済みか

## 文字化け確認と修正

### コミット後の確認

1. `git log` でコミットメッセージを確認
2. 文字化けが発生している場合は修正

### 修正方法

```powershell
# コミットメッセージを修正（エディタ）
git commit --amend

# または、BOM なし UTF-8 のファイルから読み込んで修正
$content = @"
修正後のコミットメッセージ
"@
[System.IO.File]::WriteAllText(
    "temp/commit_msg.txt",
    $content,
    [System.Text.UTF8Encoding]::new($false)
)
git commit --amend -F temp/commit_msg.txt
Remove-Item temp/commit_msg.txt
```

## 実行ルール

- **コミットメッセージ作成時**: このSKILLを参照して適切な形式で作成
- **コミットメッセージ確認時**: 文字化けや形式の確認に使用
- **コミットメッセージ修正時**: 修正方法の参照に使用
