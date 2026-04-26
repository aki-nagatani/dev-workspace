---
name: MyPokedex_pull-request
description: >-
  MyPokedex リポジトリ向け: develop 上のコミット・push、main ← develop の PR 作成・マージ、
  マージ後の GitHub Actions 確認、CursorLog 追記（JST 実時刻）まで。1 チャット 1 回限り、
  pre-commit 必須・--no-verify 禁止。コミットメッセージは commit-message、CI 待機は
  github-actions-check。専用 Cursor Command（旧 MyPokedex/.cursor/commands/）は廃止し
  本 SKILL が正本。MyPokedex PR、MyPokedex デプロイ前マージ、develop push の依頼時に使う。
---

# MyPokedex プルリクエスト（`MyPokedex_pull-request`）

## 概要

**旧 `MyPokedex/.cursor/commands/MyPokedex_pull-request.md` は廃止**し、手順の正本を本 SKILL に置く。`name` は **`MyPokedex_pull-request`**（従来の Command 名と同じ）。

**リポジトリ作業**: `D:/OneDrive/git_work/MyPokedex`（`aki-nagatani/MyPokedex`）。myrules を厳守して作業してください。

## 依頼の範囲（1回限り・成功後は無断コミット禁止）

- 本 SKILL は、このチャットにおける **コミット・プッシュおよび本文の PR・マージ等の依頼を 1 回分だけ**許可する。
- **`git commit` が失敗した場合**は、原因を修正し**成功するまで**再試行してよい（未成功の間だけ当該依頼は有効）。
- **`git commit` が少なくとも 1 回成功した後**は、**同じ依頼での追加コミットは禁止**。本文の push / PR / マージは**同一フロー内**で続けてよい。
- 本文の一連作業が**完了した後**は、**新たな明示がない限り** `git commit` / `git push` を行わない（**無断コミット禁止**に戻る）。

MyPokedex リポジトリのファイルをコミット＆プッシュしてください。コミットメッセージの作成・確認・修正は **`commit-message` SKILL** を参照してください。

## Git ブランチ（最重要・再発防止）

**本 SKILL では、ユーザーがチャットで「ブランチを切って」と明示指示しない限り、`git checkout -b` やフィーチャーブランチの新規作成をしてはならない。**
「プルリクエストを作る」から **フィーチャーブランチが要る** と推測するのは誤り。

**既定の手順（この順で行う）**:

1. **`develop` にチェックアウトする**（`git checkout develop`）。作業ツリーに未コミットの変更があれば、そのまま **`develop` 上に載せて** コミットする。
2. 必要に応じて `git pull origin develop` で最新化する。
3. **差分があるファイルはすべて** ステージし、**`develop` 上で** `git commit`（pre-commit 通過を必ず待つ）。
4. **`git push origin develop`**。
5. **プルリクエスト**は **`base` = `main`**、**`head` = `develop`**（同一リポジトリ `aki-nagatani/MyPokedex`）。`head` に `fix/...` 等の別ブランチを指定しない。

直近の作業内容にかかわらず、差分があるファイルはすべてコミットすること。

## pre-commit・テスト・カバレッジ

コミット前に必ず、`.githooks/pre-commit` を実行し、テストをスキップしないでください。また、カバレッジ要件の無断での緩和も禁止とします（pre-commit は `git commit` で自動実行され、コマンドより個別で呼び出す必要はありません）。

**絶対禁止（品質ゲートの根幹）**: `pyproject.toml`・`.githooks/pre-commit`・`.github/workflows` 等における
**`--cov-fail-under` の引き下げ（99% の最終失敗未満へ変更）**。

**AGENTS.md の正本どおり最終 99% を維持**し、不足分は**テスト追加**のみで埋める。並列段の `--cov-fail-under=0` 等は
**AGENTS 記載の既存 CI 手順の範囲**に限る。「一時的に」や数値が僅差であることは理由にならない。

ただし、pre-commit 内で設定している「md の修正のみの場合はテストスキップ」などの条件に当てはまる場合は、
pre-commit の記述に沿ってテストをスキップしても構いません。

テストエラーやカバレッジ不足などで、pre-commit が失敗した場合は、コミットせずに対応を行ってください。失敗の原因を確認し、その原因の解消を始めてください。カバレッジ不足が原因の場合、**`test-code-generator` SKILL** を呼び出してテストコードを生成し、カバレッジを改善してください。

E2E テストでアプリの起動が求められた場合は、Docker を起動してテストを実施してください。

## PR 本文テンプレート（GitHub）

- リポジトリ既定の PR 本文は **`.github/pull_request_template.md`**
  （カバレッジ閾値の自己チェック含む；MyPokedex は**並列段 0 等**の**既存手順**との区別付き）。**PR 作成・マージ**の際、
  **チェックリストが実態と一致**していること、**不要な閾値行を差分に含めていない**ことを確認する。
  レビューで **`pyproject.toml` / pre-commit / workflow** の閾値行に注意する。

## 絶対禁止: --no-verify によるコミットは厳禁です

- いかなる理由があっても `git commit --no-verify` を使用してはなりません
- pre-commit が失敗した場合は、必ず原因を解消してからコミットしてください
- カバレッジ不足やテストエラーがある場合は、それらを解決してからコミットしてください
- 一時的な回避策として `--no-verify` を使用することは許可されません

**コミット・プッシュの対象ブランチは常に `develop` です。** `main` への直接コミット・直接プッシュは禁止。

コミット時にコメント用の一時ファイルを作成した場合は削除してください。

**`develop` → `main`** のプルリクエストを作成し、マージを実行してください（上記「Git ブランチ」と整合させる）。

## マージ完了後の GitHub Actions 確認（必須・絶対にスキップ禁止）

マージ完了後、**必ず GitHub Actions の完了を待って結果を確認してください。**

**実行方法**: **`github-actions-check` SKILL**を参照して、GitHub Actions の完了を待って結果を確認してください。

- SKILL の場所: `dev-workspace/.cursor/skills/github-actions-check/SKILL.md`
- リポジトリ: `aki-nagatani/MyPokedex`
- 確認対象: lint、test ジョブ

PR 作成時にコメント用の一時ファイルを作成した場合は削除してください

## Cursorログ更新（必須）

**コミット完了後、必ず Cursor ログを更新してください。**

- **`obsidian-cursor-log` SKILL**を使用して、当日の CursorLog に作業内容を記録する
- 記録内容: 作業名（コミット作業）、プロジェクト名、変更ファイル、実施内容（コミットした内容の概要）、結果（コミット・プッシュ完了の確認）
- タグは作業内容に応じて適宜追加（例: `#git`、`#commit`、プロジェクト名のタグなど）
- **タイムスタンプは必ず実時刻（JST）を記載すること**  
  追記の**直前**に、ターミナルで現在時刻を取得してから記載する。`--:--:--` や仮の時刻は使用禁止。  
  取得例（PowerShell）:

  ```text
  [TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), [TimeZoneInfo]::FindSystemTimeZoneById('Tokyo Standard Time')).ToString('HH:mm:ss')
  ```
