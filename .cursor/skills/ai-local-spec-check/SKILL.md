---
name: ai-local-spec-check
description: >-
  ローカル Docker（FishTrack `docker compose` の `app`）のログから「AI補助スペック取り込みプレビュー結果」、
  「AI補助スペック取り込みLLM入出力」、およびプレビュー未到達時の「プレビュー失敗」1行JSONを取得し、
  本家ページと突き合わせてロッド／リールの取り込み品質を検証する（失敗時は原因整理中心）。差異は 🔴🟡🔵 に分類し、
  対策案を即時／中期／長期で具体化する（**FishTrack 実装・Obsidian 仕様を加味**。**正本 §6 は新規検討分のみ**・**実装済みの棚卸しは書かない**。共通 **`SKILL-SHARED.md` §8**）。
  **各対策に期待効果**を併記して Obsidian 正本 `ai_spec_check_report.md` に書き、
  CursorLog を更新する。本番 SSH は不要。共通手順は `ai-spec-check/SKILL-SHARED.md` が正本。
  ローカル docker プレビュー照合、dump_spec_import_preview、開発環境 fishtrack.log の依頼時に使用する。
---

# AI スペック取り込みプレビュー検証 SKILL（ローカル Docker）

## 概要

**手順の正本**は **二段構成**である（`ai-spec-check` と共通部を共有）。

- **本ファイル（`ai-local-spec-check/SKILL.md`）**: ローカル Docker の **§0〜3**（前提・`dump` まで）。**SSH / EC2 は使わない**
- **`SKILL-SHARED.md`**: `d:\OneDrive\git_work\dev-workspace\.cursor\skills\ai-spec-check\SKILL-SHARED.md` の **§3.1** および **§4〜13**

**エージェントは** 本ファイルを **Read** したうえで **`SKILL-SHARED.md` を Read** し、ターミナル実行・本家突き合わせ・Obsidian 正本・markdownlint・作業用 `temp/` の後片付け・**obsidian-cursor-log** まで行う。手順の提示だけで終わらない。

**🚨 見逃し禁止（同一チャット・検証フロー）**: **当該セッションで先に** FishTrack **`src/`**（またはアプリが読み込む **`*.py`**）を\
**`StrReplace` / `Write` 等で変更した**うえで、本 SKILL に従い **`dump_spec_import_preview.py`**（**§2 の `--count` / `--list` を含む**）でログ検証に入るときは、\
**ユーザーに「restart しましたか」と聞いて省略してはならない**。**§2 より前に** **`docker compose -f docker-compose.yml restart app`** を\
**エージェント自身がターミナルで実行**する（下記 **「Python 変更と dump 前の再起動」**・**`local-docker-python-restart`** SKILL）。\
**SKILL を読んだのに restart を実行せず dump だけ進める**のは**手順違反**とする。

**本番ログ**で照合するときは **`ai-spec-check/SKILL.md`** を入口にする。

**人間向けパス（再掲）**:

- FishTrack ルート: `d:/OneDrive/git_work/FishTrack`
- レポート正本: `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`
- 本家取得本文（`ai-spec-notes`）: `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai-spec-notes/`（**`SKILL-SHARED.md` §5.1**。本家 URL 取得のみ。プレビューはレポートのみ。**差分なしならノート非更新**）
- **レポート本文の型**: 正本内 **`## 0. レポートの型（固定・分析ごとに維持）`** を読み、**見出し順・表列・フロントマター必須キー**に従って上書きする（分析ごとのブレ防止）。詳細は同ファイル §0 と **`SKILL-SHARED.md` §9・§11**。
- 作業用出力先: FishTrack リポ内 `temp/`（完了後に当該作業分を削除。**`SKILL-SHARED.md` §10**）

myrules を厳守して作業してください。

**用語（本文）**: 本 SKILL および **`SKILL-SHARED.md`** の追記・改稿では **「総覧」** を**使わない**（**`SKILL-SHARED.md` の「用語（本スキル群の本文）」節**に従う）。

**ユーザー指摘の反映**: ローカル dump・コンテナ名・文字コード・レポート §8 の書き分けなどへの**指摘**があった場合は、**同一セッションで**本 SKILL または **`SKILL-SHARED.md`** を修正する（dev-workspace **myrules**「**ユーザー指摘に基づくルール・SKILL の育成**」）。

**報告の出し分け**: 表・分類・対策の**全文**は **`SKILL-SHARED.md` §9** の Obsidian `ai_spec_check_report.md` にのみ書く。**チャット**には **§9.4** の要約で足りる。

**読み取り専用タスク**: **DB への接続・書き込みは行わない**。ローカル **EC2 / RDS には触れない**（コンテナログの読み取りのみ）。

## 使用タイミング

- ユーザーが AI 補助スペック取り込みのプレビュー品質を**ローカル Docker 上の FishTrack**で確認したいとき
- 本番ではなく **開発用 `docker compose`** のログだけで照合したいとき

## 0. 前提・環境（ローカル Docker）

- プロジェクトルート: `d:/OneDrive/git_work/FishTrack`（`scripts/dump_spec_import_preview.py` の実行元）
- **コンテナが起動**していること: `docker compose -f docker-compose.yml ps` で `app` が Up。ログはコンテナ内 `FISHTRACK_LOG_DIR` 配下（既定 `/app/instance/logs`）の `fishtrack.log` 等
- **`dump_spec_import_preview.py` の既定**はローカル Docker 経由: スクリプトが `docker exec` でログを **bytes 取得**する（PowerShell の `>` リダイレクトでログを保存しない）
- **コンテナ名**: スクリプト既定は `fishtrack-app-1`（`scripts/dump_spec_import_preview.py` の `DEFAULT_CONTAINER`）。`docker ps` で実名が異なる場合は `--container <名前>` を付ける
- **作業用ファイル**はすべて **`temp/`** 配下（例: `temp/tmp_latest_preview.json`）。**作業完了後**（**`SKILL-SHARED.md` §13** まで済んだら）当該実行分の作業用ファイルを **§10** で削除
- プレビュー結果の出力条件・識別文字列・payload キー・`AI補助スペック取り込みLLM入出力:` の説明は **`ai-spec-check/SKILL.md` §0 と同趣旨**（ローカル `.env` / `docker-compose.yml` で `FISHTRACK_STANDALONE`・`FISHTRACK_SPEC_IMPORT_DEBUG_LOG` を確認）

## 🚨 Python 変更と dump 前の再起動（必須・myrules 整合）

- **同一セッションまたは直前に** FishTrack の **`src/`**（例: `fishtrack/services/spec_import/`）など**アプリが読み込む Python** を変更し、\
  **続けて**本 SKILL の **`dump_spec_import_preview.py`** で**新実装の挙動**をログから検証する場合は、\
  **§2 の `--count` / `--list` / `--latest` いずれより前に**次を**必ず**実行する。
  - **`docker compose -f docker-compose.yml restart app`**（**ターミナル**。FishTrack リポ直下。**手順の提示のみ禁止**・**`local-docker-python-restart`** の「必須アクション」と同一）
  - 根拠: **dev-workspace** **`local-docker-python-restart`** SKILL・**myrules**「ローカル Docker と Python ソース変更」と同一。**Gunicorn は既定でホットリロードしない**ため、再起動なしの dump は**旧プロセスのログ**になり得る。
- **ユーザーが既に restart したかもしれない**という**推測で省略しない**。迷うときは **restart を重ねてよい**（冪等）。
- **Python を触っていない**（Obsidian レポートのみ・スクリプト引数のみ等）ときは本節の対象外。

## 🚨 文字コードの絶対ルール（ローカル）

- **プレビュー JSON の保存**は `python scripts/dump_spec_import_preview.py --out temp/...` に任せる（UTF-8・BOM なし）
- **PowerShell の `>`** で日本語ログや JSON を**いきなり保存**しない（CP932 解釈で破損しうる）
- 手動でコンテナからログをホストへ出す必要がある場合も、**バイナリ／UTF-8 明示の経路**にし、`dump` には `--file` で渡す（詳細は **`ai-spec-check/SKILL.md` の「文字コードの絶対ルール」**）

## 1. ローカルでログの有無を確認（任意）

- `docker compose -f docker-compose.yml exec -T app sh -c 'ls -la /app/instance/logs'` 等で `fishtrack.log` の有無・ローテーションを確認
- ファイルが無く **stdout のみ**の構成なら、**入口 §0 (2)** と同様に `docker logs` で該当マーカー行を取得し、UTF-8 テキストとして `dump` に `--stdin` で渡す

## 2. プレビュー結果ログの件数・一覧確認（常設スクリプト）

FishTrack ルートで、**SSH なし**・`--stdin` / `--file` なしの例（スクリプトが **docker exec** する）:

```powershell
cd d:/OneDrive/git_work/FishTrack
python scripts/dump_spec_import_preview.py --count
python scripts/dump_spec_import_preview.py --list --limit 5
python scripts/dump_spec_import_preview.py --kind failure --count
python scripts/dump_spec_import_preview.py --kind failure --list --limit 10
```

- コンテナ名が既定と違う場合: `--container <実名>`
- ローテ済み `fishtrack.log.YYYY-MM-DD` も見る: `--include-rotated`（一覧・最新取得の各コマンドに付与）
- **`--kind` / `--order` / 0 件時の切り分け**の詳細は **`SKILL-SHARED.md` §3.1**

## 3. 最新 1 件を JSON として取得

```powershell
cd d:/OneDrive/git_work/FishTrack
python scripts/dump_spec_import_preview.py --latest --out temp/tmp_latest_preview.json
python scripts/dump_spec_import_preview.py --kind failure --latest --out temp/tmp_latest_failure.json
```

- **2 件目**など: `--index 1`（順序は `--order` 準拠）
- ローテ済みログも対象: `--include-rotated`
- 出力先は **`temp/`**、`--out` で指定（PowerShell の `>` は使わない）

## 全長照合の必須要件（ロッド）

**※** `SKILL-SHARED.md` の **§3.1** は **`dump_spec_import_preview.py` CLI** 用。本節は **レポート義務**。

- **`SKILL-SHARED.md` §6A B** および **§11.1** に従い、`category = "rod"` かつ**プレビュー成功**のときは、\
  Obsidian 正本 **`ai_spec_check_report.md`** に **本家 全長（m）** と **`rows[]` の `lengthFt` / `lengthIn`** の\
  **行別照合**を **必ず**記載する（**`##` 見出し付きの専用表**、または **数値表へ列追加**のいずれか）。\
  **本照合を省略したレポートは未完成**（**「未実施」一言でのスキップ禁止**）。
- **換算・一致判定**の正本は **`SKILL-SHARED.md` §6A B** に従う（**`(lengthFt * 12 + lengthIn) * 0.0254` m** と本家 **m**、\
  本家表が **小数第 2 位まで**のみの場合の **丸め**）。

## テーパー／アクション照合の必須要件（DAIWA ロッド）

- **正本**: **`SKILL-SHARED.md` §6A B**（**Obsidian 正本 `ai_spec_check_report.md`（テーパー／アクション・DAIWA ロッド）**）および **§11.1** 項 3（ロッドの数値突き合わせ表）。\
  本家表にテーパー列があるときの**行別表**・**判定（`XF→S` 等は原文どおり）**・**比率 prose と型番 Pattern**の扱いは **§6A B** に集約する。
- **`ai-spec-notes`**: **本家 URL から取得した本文・表のみ**（**`SKILL-SHARED.md` §5.1**）。**期待 `power` / `action`**・**`technologyLabels` 等のプレビュー突合**・🔴🟡 は **`ai_spec_check_report.md`** にのみ記載する（ノートへ**書かない**）。

## DAIWA ロッド・X45 系（照合の補足）

- **`X45` と `X45フルシールド`** は**トレードオフではなく併記しうる**。**併記のみ**で **🔴／🟡** としない（詳細は **`SKILL-SHARED.md` §6A C**）。

## 4. 以降の手順（共通・正本）

**`SKILL-SHARED.md` の §3.1**（必要時）および **§4〜13** を **Read** し、§4 から順に実行する。

`d:\OneDrive\git_work\dev-workspace\.cursor\skills\ai-spec-check\SKILL-SHARED.md`

**補足**: レポート正本パス・markdownlint・CursorLog・禁止事項は **`ai-spec-check` と同一**（本番専用の禁止例は §12 に明記）。

## Markdownlint（lint 無効化の禁止）

- **無断での lint 無効化は禁止**（`markdownlint-disable` コメント、設定の勝手な緩和・除外など）。**正本・手順は `SKILL-SHARED.md` §9.0.1**。違反は**本文修正等で解消**し、必要なときは**ユーザーの明示承認**のうえで限定的に対応する。
