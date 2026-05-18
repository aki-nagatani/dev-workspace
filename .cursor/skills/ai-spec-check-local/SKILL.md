---
name: ai-spec-check-local
description: >-
  ローカル Docker（FishTrack `docker compose` の `app`）のログから「AI補助スペック取り込みプレビュー結果」、
  「AI補助スペック取り込みLLM入出力」、およびプレビュー未到達時の「プレビュー失敗」1行JSONを取得し、
  本家ページと突き合わせてロッド／リールの取り込み品質を検証する（失敗時は原因整理中心）。差異は 🔴🟡🔵 に分類し、
  対策案を優先度（高／中／低）で具体化する（**FishTrack 実装・Obsidian 仕様を加味**。**正本 §6 は新規検討分のみ**・**実装済みの棚卸しは書かない**。共通 **`ai-spec-check-report` §8**）。
  **各対策に期待効果**を併記し、正本 **§4 は「対策 N」連番・§5 と対応**（**`ai-spec-check-report` §8.1**）して Obsidian `ai_spec_check_report.md` に書き、
  CursorLog を更新する。本番 SSH は不要。共通手順は `ai-spec-check-report/SKILL.md` が正本。
  ローカル docker プレビュー照合、dump_spec_import_preview、開発環境 fishtrack.log の依頼時に使用する。
---

# AI スペック取り込みプレビュー検証 SKILL（ローカル Docker）

## 概要

**手順の正本**は **二段構成**である（`ai-spec-check` と共通部を共有）。

- **本ファイル（`ai-spec-check-local/SKILL.md`）**: ローカル Docker の **§0〜3**（前提・`dump` まで）。**SSH / EC2 は使わない**
- **`ai-spec-check-report`**: `d:\OneDrive\git_work\dev-workspace\.cursor\skills\ai-spec-check-report\SKILL.md` の **§3.1** および **§4〜13**
- **実行順・実装の境界**: **`ai-spec-check-report`** の **「実行順：dump 検証を先に・対策の実施はユーザー決定」** を正とする（**dump 照合・レポート検証を先に**、**対策の実施はユーザー判断**・無断実施禁止）。

**エージェントは** 本ファイルを **Read** したうえで **`ai-spec-check-report` を Read** し、ターミナル実行・本家突き合わせ・Obsidian 正本・markdownlint・作業用 `temp/` の後片付け・**obsidian-cursor-log** まで行う。手順の提示だけで終わらない。

**🚨 見逃し禁止（ブラウザ操作・同一チャット）**: **`src/`**（またはアプリが読み込む **`*.py`**）を **`StrReplace` / `Write` 等で変更した**うえで、**ユーザーがブラウザから FishTrack を操作する**（スペック取り込みプレビュー等）**流れに入る**ときは、\
**そのブラウザ操作より前**に **`docker compose -f docker-compose.yml restart app`** を**エージェント自身がターミナルで試行**する（**`local-docker-python-restart`** SKILL・**myrules**）。**ユーザーへの確認文だけで代用しない**。**推測で省略しない**。\
**`dump_spec_import_preview.py`** は**ログ読取のみ**で、**`dump` の実行・照合に `restart` は不要**（**`dump` 検証とは無関係**。既存ログだけを読むなら **`restart` はスキル上不要**）。

**本番ログ**で照合するときは **`ai-spec-check/SKILL.md`** を入口にする。

**人間向けパス（再掲）**:

- FishTrack ルート: `d:/OneDrive/git_work/FishTrack`
- レポート正本: `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`
- 突合用本家データ（`ai-spec-notes`）:
  `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai-spec-notes/`。\
  **`ai-spec-check-report` §5.1**（**DAIWA ロッド**は **`rod-daiwa/`**。取得元でフォルダを分けない）。URL本文の丸写しではなく、
  プレビュー `rows[]` と比較するための**本家側データ（数値・JAN 等）をノート内に必ず残す**。\
  **ルアー oz に加え**、本家に **ライン（lb）** 列があるページでは **行別の lb 原文**も **`ai-spec-notes`** に載せ、**`lineMinLb`／`lineMaxLb`** と照合する（**`ai-spec-check-report` §5.1・§6A B**）。\
  **ノートのファイル名**に **URL の一部**（`/product/` 末尾の短い ID 等）を**含めない**（同 §5.1 命名規則。同定は **`## メタ` の `resolvedUrl`** のみ）。
  **`## 行別スペック` を `ai_spec_check_report.md` への参照だけで埋めることは禁止**（§5.1 冒頭）。\
  **ロッド**は **`## 行別スペック`** に **`rows[].modelName` と突合する期待文字列（`modelName期待` 等）を行別に必ず書く**（同 §5.1）。\
  **ロッドで本家にジャンル列が無いページ**は **`ai-spec-notes`** に **FishTrack が確定する
  `genre`（`bait`／`spinning`）の行別表**を置く（**§5.1.1** 項 5。**`05`** の型番末尾ルールを根拠列に書く）。\
  **本家にパワー列・テーパー（アクション）列が無い DAIWA ロッド**は **`## 行別 Pattern 期待値`** に\
  **`infer_power…` / `infer_action…` の行別表**を置く（**§5.1.1** 項 4・**`ai-spec-check-report` §5.1**）。\
  実行ごとの判定はレポートのみ。
- **レポート本文の型**: 正本 **`ai_spec_check_report.md`** の **`## 1.`〜`## 6.`** と冒頭「**運用ルール（正本 §1〜§6 の固定）**」に従う。詳細は **`ai-spec-check-report` SKILL §11.1・§9**。\
  **`ai-spec-check-report` §8.1** の「**報告直前チェックリスト**」で **`## 4.`／`## 5.` 消込**を実行してから **markdownlint と報告・CursorLog** に進める（**lint 適合のみで §4 滞留が解消しない**。**反映完了済み `対策 N` は再プレビュー前でも §4 から除去可**・**§8.1・正本・myrules**）。
- 作業用出力先: FishTrack リポ内 `temp/`（完了後に当該作業分を削除。**`ai-spec-check-report` 本 SKILL §10（後片付け）**）

myrules を厳守して作業してください。

**用語（本文）**: 本 SKILL および **`ai-spec-check-report`** の追記・改稿では **「総覧」** を**使わない**（**`ai-spec-check-report` の「用語（本スキル群の本文）」節**に従う）。

**ユーザー指摘の反映**: ローカル dump・コンテナ名・文字コード・レポート §8 の書き分けなどへの**指摘**があった場合は、**同一セッションで**本 SKILL または **`ai-spec-check-report`** を修正する（dev-workspace **myrules**「**ユーザー指摘に基づくルール・SKILL の育成**」）。

**報告の出し分け**: 表・分類・対策の**全文**は **`ai-spec-check-report` §9** の Obsidian `ai_spec_check_report.md` にのみ書く。**チャット**には **§9.4** の要約で足りる。

**読み取り専用タスク**: **DB への接続・書き込みは行わない**。ローカル **EC2 / RDS には触れない**（コンテナログの読み取りのみ）。

## 使用タイミング

- ユーザーが AI 補助スペック取り込みのプレビュー品質を**ローカル Docker 上の FishTrack**で確認したいとき
- 本番ではなく **開発用 `docker compose`** のログだけで照合したいとき

## 0. 前提・環境（ローカル Docker）

- プロジェクトルート: `d:/OneDrive/git_work/FishTrack`（`scripts/dump_spec_import_preview.py` の実行元）
- **コンテナが起動**していること: `docker compose -f docker-compose.yml ps` で `app` が Up。ログはコンテナ内 `FISHTRACK_LOG_DIR` 配下（既定 `/app/instance/logs`）の `fishtrack.log` 等
- **`dump_spec_import_preview.py` の既定**はローカル Docker 経由: スクリプトが `docker exec` でログを **bytes 取得**する（PowerShell の `>` リダイレクトでログを保存しない）
- **コンテナ名**: スクリプト既定は `fishtrack-app-1`（`scripts/dump_spec_import_preview.py` の `DEFAULT_CONTAINER`）。`docker ps` で実名が異なる場合は `--container <名前>` を付ける
- **作業用ファイル**はすべて **`temp/`** 配下（例: `temp/tmp_latest_preview.json`）。\
  **作業完了後**に **`obsidian-cursor-log` SKILL** による **CursorLog 追記**を済ませたうえで、\
  **`ai-spec-check-report` SKILL §10（後片付け）** に従い **当該実行分を `temp/` から削除**する。
- プレビュー結果の出力条件・識別文字列・payload キー・`AI補助スペック取り込みLLM入出力:` の説明は **`ai-spec-check/SKILL.md` §0 と同趣旨**（ローカル `.env` / `docker-compose.yml` で `FISHTRACK_STANDALONE`・`FISHTRACK_SPEC_IMPORT_DEBUG_LOG` を確認）

## 🚨 `src/` 変更後のブラウザ操作と `dump`（`restart` の位置づけ）

- **`restart` が要る場面**: **`src/` 等アプリ用 Python を変更したあと**、**ユーザーがブラウザからアプリを操作する**（プレビュー含む）**までに**。**Gunicorn 等は既定でホットリロードしない**（**`local-docker-python-restart`**・**myrules**）。
- **`dump_spec_import_preview.py`**: コンテナ内 `fishtrack.log` 等を**読むだけ**。**スクリプトの成否・照合作業に `restart` は不要**（**`dump` 検証とは非関係**）。
- **接続**: **新コードのログ**を**ブラウザで再現してから** `dump` したいときだけ、順序として **`restart` →（ユーザー操作）→ `dump`**。**ログファイルが既にあり**、`--count` / `--latest` のみするなら **`restart` は不要**。
- **`myrules`**: **`src/` を変えたターン**の**ユーザー向け完了報告の前**の **`restart` 試行**は**継続**（**ブラウザ検証に絡むとき**と整合）。
- **対象条件を満たす**とき、**ユーザーが既に restart したかもしれない**という**推測で省略しない**。迷うときは **restart を重ねてよい**（冪等）。

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
- **`--kind` / `--order` / 0 件時の切り分け**の詳細は **`ai-spec-check-report` §3.1**

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

**※** `ai-spec-check-report` の **§3.1** は **`dump_spec_import_preview.py` CLI** 用。本節は **レポート義務**。

- **`ai-spec-check-report` §6A B** および **同 SKILL §11.1・Obsidian 正本 §2.2（全長）**に従い、`category = "rod"` かつ**プレビュー成功**のときは、\
  Obsidian 正本 **`ai_spec_check_report.md`** に **本家 全長（m）** と **`rows[]` の `lengthFt` / `lengthIn`** の\
  **行別照合**を **必ず**記載する（**`##` 見出し付きの専用表**、または **数値表へ列追加**のいずれか）。\
  **本照合を省略したレポートは未完成**（**「未実施」一言でのスキップ禁止**）。
- **換算・一致判定**の正本は **`ai-spec-check-report` §6A B** に従う（**`(lengthFt * 12 + lengthIn) * 0.0254` m** と本家 **m**、\
  本家表が **小数第 2 位まで**のみの場合の **丸め**）。

## ルアー重量照合の必須要件（ロッド）

- **`ai-spec-check-report` §6A B** および **§11.1・正本 §2.4（ルアー重量）**に従い、**本家製品スペック表にルアー重量列がある**\
  **`category = rod`** かつ**プレビュー成功**のときは、Obsidian 正本 **`ai_spec_check_report.md`** に\
  **本家ルアー重量**と **`rows[]` の `lureWeightMinOz` / `lureWeightMaxOz`** の**行別照合**を**必ず**記載する。\
  **DAIWA で g／ジグ g／oz が併在する場合は oz 列のみ**。**帯分数／小数同値**・**画面整形**は **§6A B**。\
  **本照合を省略したレポートは未完成**（**「未実施」一言でのスキップ禁止**）。\
  **本家にルアー重量列が無い**ページでは**当該表は不要**。
- **`ai-spec-notes`**: **`## 行別スペック`** に **本家側ルアー重量**を**行別で含める**（**`ai-spec-check-report` §5.1**）。**PE 列**のみ **`## 任意項目・比較除外`** に回してよいが、**ルアー重量を突合から外してノート表で省略することは禁止**。

## テーパー／アクション照合の必須要件（DAIWA ロッド）

- **正本**: **`ai-spec-check-report` §6A B**（**テーパー／アクション**）および **§11.1・正本 §2.3**。\
  本家表にテーパー列があるときの**行別表**・**判定（`XF→S` 等は原文どおり）**・**比率 prose と型番 Pattern**の扱いは **§6A B** に集約する。
- **`ai-spec-notes`**: **プレビュー `rows[]` と突合するための本家側データ**
  （**`ai-spec-check-report` §5.1**）。**`modelName` 期待（行別）**・**期待 `power` / `action`**・**ルアー重量（本家表にある場合）**・**ロッドでジャンル列が無いときは FishTrack が確定する `genre`（`bait`／`spinning`）の行別表**（§5.1.1。**根拠は `05` の型番ルール**）・\
  本家側の `blankMaterial` / `technologyLabels` 期待値は、
  根拠付きの突合データとしてノートへ記載してよい。\
  🔴🟡🔵 判定・実行ごとのプレビュー値・対策は **`ai_spec_check_report.md`** にのみ記載する。

## パワー照合の必須要件（ロッド）

- **`ai-spec-check-report` §6A B** および **§11.1・正本 §2.3（`power`）** に従い、`category = "rod"` かつ**プレビュー成功**のときは、Obsidian 正本 **`ai_spec_check_report.md`** に次を **必ず**含める（**「未実施」一言でのスキップ禁止**）。
  - 本家表に **パワー**（または硬度・調子相当の正本列）があるとき: **本家パワー（原文）** と **`rows[].power`** の**行別照合表**。
  - 本家表に **パワー列が無い**とき（DAIWA で型番・サーバ補完が主となるページ）: **期待 `power`（根拠）** と **`rows[].power`** の**行別照合表**（仕様 `05_ai_spec_import.md` の `power` ヒント・🔵 条件と整合）。
- **換算・一致判定**の正本は **§6A B** と **`05_ai_spec_import.md`**（本家セルがある場合は**原文優先**、無い場合は**型番 Pattern / サーバ補完の説明**を期待値列に書く）。

## DAIWA ロッド・照合の補足（X45／`pieces`）

- **`X45` と `X45フルシールド`** は**トレードオフではなく併記しうる**。**併記のみ**で **🔴／🟡** としない（詳細は **`ai-spec-check-report` §6A C**）。
- **`pieces` の `N（テレスコピック）`**: **製品表の継数が数値のみ**かつ **型番コアがテレスコ振出**（全長ブロック直後が **`T`**）のとき、プレビューが **`6（テレスコピック）`** 等でも **FishTrack 仕様**（**`05_ai_spec_import.md`**）。\
  **🟡（表記ゆれ）とはしない**。**詳細は `ai-spec-check-report` §6A E**。

## 4. 以降の手順（共通・正本）

**`ai-spec-check-report` SKILL** を **Read** し、**§3.1**（必要時）から **§4** 順に実行する。**Obsidian の章番号 §1〜§6** と混同しない（**詳細は同 SKILL の冒頭「実行順」・§11.1**）。

`d:\OneDrive\git_work\dev-workspace\.cursor\skills\ai-spec-check-report\SKILL.md`

**補足**: レポート正本パス・markdownlint・CursorLog・禁止事項は **`ai-spec-check` と同一**（本番専用の禁止例は **`ai-spec-check-report` §12** に明記）。

## Markdownlint（lint 無効化の禁止）

- **無断での lint 無効化は禁止**（`markdownlint-disable` コメント、設定の勝手な緩和・除外など）。**正本・手順は `ai-spec-check-report` §9.0.1**。違反は**本文修正等で解消**し、必要なときは**ユーザーの明示承認**のうえで限定的に対応する。
