---
name: commit-all
description: >-
  ワークスペース内の複数リポジトリ（FishTrack、MyPokedex、personal-tools、dev-workspace 等）で、
  差分のあるものをまとめてコミット＆プッシュする。**otayori-navi は対象外**（本 SKILL では扱わない）。
  1チャット1回限りの依頼、
  pre-commit 必須・--no-verify 禁止、develop/main のブランチ方針、カバレッジ・E2E・
  test-code-generator 連携、完了後の CursorLog 追記（JST 実時刻）まで含む。コミットメッセージは
  commit-message SKILL。専用 Cursor Command（旧 commit_all.md）は廃止し本 SKILL が正本。
  commit_all、全リポコミット、一括コミット、マルチリポ push の依頼時に使用する。
---

# 全リポジトリコミット（commit-all）

## 概要

**旧 `.cursor/commands/commit_all.md` は廃止**し、手順の正本を本 SKILL に置く。`name` は **`commit-all`**（従来の **commit_all** コマンド相当）。

myrules を厳守して作業してください。

## 依頼の範囲（1回限り・成功後は無断コミット禁止）

- 本 SKILL による依頼は、このチャットにおける **各リポジトリへのコミット・プッシュの依頼を 1 回分だけ**許可する。
- **いずれかの `git commit` が失敗した場合**は、原因を修正し**成功するまで**再試行してよい（未成功の間だけ当該依頼は有効）。
- **対象リポジトリごとに `git commit` が少なくとも 1 回成功した後**は、**同じ依頼での追加コミットは禁止**。本文の push は**同一フロー内**で続けてよい。
- 本文の一連作業が**完了した後**は、**新たな明示がない限り** `git commit` / `git push` を行わない（**無断コミット禁止**に戻る）。

**スコープ**: **`otayori-navi` は対象外**（差分があっても**コミット・プッシュしない**）。おたよりナビは **`otayori-navi_pull-request` SKILL** 等で**別依頼**とする。

対象内リポジトリのファイルをコミット＆プッシュしてください。

コミットメッセージの作成・確認・修正は **`commit-message` SKILL** を参照してください。

直近の作業内容にかかわらず、差分があるファイルはすべてコミットすること。

ただし、差分がないプロジェクトへのコミットはスキップしても構わない。

FishTrack / MyPokedex / personal-tools のコミット前に必ず、`.githooks/pre-commit` を実行し、テストをスキップしないでください。

また、カバレッジ要件の無断での緩和も禁止とします。

（pre-commit は「`git commit`」で自動実行されます。コマンドから個別で呼び出す必要はありません。）

テストでエラーとなった場合は、原因究明を行ってください。

ただし、pre-commit 内で設定している「md の修正のみの場合はテストスキップ」などの条件に当てはまる場合は、pre-commit の記述に沿ってテストをスキップしても構いません。

テストエラーやカバレッジ不足などで、pre-commit が失敗した場合は、コミットせずに対応を行ってください。

失敗の原因を確認し、その原因の解消を始めてください。

カバレッジ不足が原因の場合、**`test-code-generator` SKILL** を呼び出してテストコードを生成し、カバレッジを改善してください。

E2E テストでアプリの起動が求められた場合は、Docker を起動してテストを実施してください。

## 絶対禁止: `--no-verify` によるコミットは厳禁です

- いかなる理由があっても `git commit --no-verify` を使用してはいけません
- pre-commit が失敗した場合は、必ず原因を解消してからコミットしてください
- カバレッジ不足やテストエラーがある場合は、それらを解決してからコミットしてください
- 一時的な回避策として `--no-verify` を使用することは許可されません

FishTrack、MyPokedex のコミット先は **「develop」ブランチ**です（**`otayori-navi` は本 SKILL 対象外**のためここに含めない）。

**「main」ブランチには適用しないでください。**

その他のプロジェクトは、**main** リポジトリにコミットしてください。

コミット時にコメント用の一時ファイルを作成した場合は削除してください。

## Cursor ログ更新（必須）

**コミット完了後、必ず Cursor ログを更新してください。**

- **`obsidian-cursor-log` SKILL**を使用して、当日の CursorLog に作業内容を記録する
- 記録内容: 作業名（コミット作業）、プロジェクト名、変更ファイル、実施内容（コミットした内容の概要）、結果（コミット・プッシュ完了の確認）
- タグは作業内容に応じて適宜追加（例: `#git`、`#commit`、プロジェクト名のタグなど）
- **タイムスタンプは必ず実時刻（JST）を記載すること**  
  追記の**直前**に、ターミナルで現在時刻を取得してから記載する。  
  `--:--:--` や仮の時刻は使用禁止。  
  取得例（PowerShell）:
  `[TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), [TimeZoneInfo]::FindSystemTimeZoneById('Tokyo Standard Time')).ToString('HH:mm:ss')`

## 使用タイミング

- ユーザーが「全リポコミット」`commit_all`、**`commit-all`**（本 SKILL）、一括コミット・全リポに push 等を依頼したとき（**1 回限り**の枠内）
