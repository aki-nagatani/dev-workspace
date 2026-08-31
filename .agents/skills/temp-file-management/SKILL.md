---
name: temp-file-management
description: >-
  一時ファイルは各リポジトリの temp/ 配下のみ。プロジェクト直下禁止（coverage.xml は例外）。
  FishTrack temp-spec-crawl/ は汎用 temp/ と別（他チャットの temp 掃除では消さない）。
  チャット作業完了時に temp/ を空にする。coverage.xml は消さずリポ直下に残す（次の diff-cover でフル pytest 省略）。
  commit_msg・調査用 check_*.py 等の例、.gitignore 確認。
  一時ファイル作成・作業完了・セッション終了・coverage.xml の残置／再利用時に使用。
---

# 一時ファイル管理（temp-file-management）

**myrules**「一時ファイル管理」と同一趣旨。**配置・再利用先・クリーンアップの正本は本 SKILL**。

## 理想状態

**AI による作業完了後、`temp/` は空であること**（当該チャットで触ったリポジトリすべて）。

- `temp/` は**そのチャット内だけの作業用スクラッチ**であり、成果物の置き場ではない
- **1 チャットの作業の最後**（ユーザー報告の直前）に必ずクリーンアップする

## 絶対ルール

1. **一時ファイルは必ず `temp/` 配下に作成する**（プロジェクト直下禁止）。**例外**: pytest が出す **`coverage.xml`**（および同位置の **`.coverage`**）はリポ直下に置く（下記「coverage.xml」）。**例外（FishTrack spec-crawl）**: CLI 生成物は **`temp-spec-crawl/`**（下記「FishTrack `temp-spec-crawl/`」）
2. **次回以降も使う可能性があるものは `temp/` に置かない**（下記「再利用するものの置き場」）。**`coverage.xml` は `temp/` へ移さない**（`diff_cover_gate.sh` の既定パスは直下）
3. **作業完了時に `temp/` を空にする**（削除。移動先が必要なら先に `scripts/` 等へ昇格）。**`coverage.xml` は消さない**。**`temp-spec-crawl/` は汎用掃除の対象外**
4. **`temp/` および FishTrack `temp-spec-crawl/` への書き込み**はシェル・スクリプト可。**そこから正本（ソース・Obsidian 等）へ**は **Read のみ** → 正本は **`Write` / `StrReplace`**（**myrules**「ファイル修正と差分確認」）

## 発火条件

- カバレッジ JSON/XML、コミットメッセージ用テキスト、調査用 `check_*.py` / `debug_*.py` 等を**新規作成**するとき
- プロジェクトルートに `coverage.json` 等が残っているのを見つけたとき
- **コミット・push 完了後**（`commit_msg.txt` 等の削除）
- **チャット内の作業を完了し、ユーザーへ報告するとき**（**temp クリーンアップ必須**）
- 触ったリポジトリの **`temp/` にファイルが残っている**とき（報告前ゲート）

## 配置場所

| 種別 | 置き場 |
| --- | --- |
| **その場限りの一時** | 当該リポジトリの **`temp/`** |
| **FishTrack spec-crawl CLI** | **`temp-spec-crawl/`**（`temp/` の子ではない。下記例外節） |
| **禁止** | リポジトリ直下（`commit_msg.txt`、`coverage.json` 等）。**例外: `coverage.xml` / `.coverage`** |
| **次回も使う調査・ユーティリティ** | **`scripts/`**（リポに無ければ作成可・Git 管理の意図あるスクリプト） |
| **dev-workspace 横断ツール** | **`dev-workspace/scripts/`** |
| **永続ナレッジ・仕様** | Obsidian **`DevProject/`** 等（**temp 禁止**） |

- `temp/` ディレクトリが無ければ作成（**`.gitignore` に `temp/` があるか確認**）
- **`temp/` に「とりあえず置いて後で整理」はしない**。再利用見込みがある時点で **`scripts/` 等へ最初から置く**

## 一時ファイルの例（`temp/` のみ・作業後削除）

- カバレッジ（消す）: `coverage_*.json`、`coverage_temp.json`（`temp/` のみ。**完了後削除**）。**`coverage.xml` は対象外**（消さない）
- コミットメッセージ: `commit_msg.txt`、`commit_msg_*.txt`（**コミット完了後必ず削除**）
- 調査・検証: `debug_*.py`、`check_*.py`（一時）、`test_*.py`（一時）、`compare_*.py`、`fix_*.py`（一時）
- 中間データ: 実データを含まない `*.db`、`*.sql`、ダミー `*.json`、`*_schema.json` / `*_schema.py`

## チャット完了時の temp クリーンアップ（必須）

**ユーザー向け最終報告の前**に、当該チャットで作成・更新したリポジトリの `temp/` を確認し、**中身を空にする**。

**禁止**: 汎用掃除で FishTrack **`temp-spec-crawl/`** を空にする・削除する（他チャットの spec-crawl 正本反映中に消える）。空にするのは **`spec-crawl` SKILL**（当該 `/spec-crawl` セッションの検証 0 後のみ）。

### 手順

1. 触った各リポジトリで `temp/` を一覧（残存ファイルの有無を確認）。**`temp-spec-crawl/` は一覧しても消さない**
2. **削除**: 上記「一時ファイルの例」に該当するものはすべて削除（**`temp-spec-crawl/` 配下は対象外**）
3. **昇格**: まだ必要で次回も使うスクリプト・データは **`scripts/`**（または適切な正本パス）へ移し、**`temp/` からは除去**
4. **空確認**: `temp/` にファイルが残っていないこと（空ディレクトリのみ可）
5. リポジトリ直下に誤配置した一時ファイルがあれば**削除または `temp/` 経由で整理後削除**。**`coverage.xml` / `.coverage` は誤配置ではない。削除禁止**

### 報告

- クリーンアップ実施時、報告文に **`temp/` を空にした**旨を 1 行記載してよい（残ファイルがある場合は理由を明示し、ユーザー判断を仰ぐ）

### 順序（obsidian-cursor-log との関係）

ファイル変更ありの作業完了時:

1. ファイル変更・テスト
2. **`temp/` クリーンアップ**（本 SKILL・**本節**）
3. CursorLog 更新
4. ユーザーへの報告

## 実行ルール（作成〜削除）

1. 作成時は **`temp/`** 配下（再利用見込みがあるなら最初から **`scripts/`**）。**FishTrack spec-crawl CLI は `temp-spec-crawl/`**
2. **作業完了後**、再利用しないものは**削除**（`temp/` に残さない）
3. 直下に誤作成したファイルは**削除**、または一時的に `temp/` へ移したうえで**完了時に削除**（**`coverage.xml` / `.coverage` を除く**）

## FishTrack `temp-spec-crawl/`（例外・他チャットは消さない）

**目的**: spec-crawl の L2 JSON・メーカー別下書き MD・マニフェストを、他チャットの `temp/` 掃除から守る。

- **置き場**: FishTrack リポ直下の **`temp-spec-crawl/`**（定数 `SPEC_CRAWL_WORK_DIR`）。**`temp/` の子ではない**
- **gitignore**: `temp-spec-crawl/`（Git に入れない）
- **シェル書き込み**: 可（`temp/` と同じ例外）。正本へは **Read のみ** → **`Write` / `StrReplace`**
- **汎用掃除禁止**: 他チャット・他作業の完了ゲートでは **削除しない・空にしない**
- **空にするタイミング**: **`/spec-crawl` を実行した当該チャット**で、正本反映と `verify_canonical_report_reflection.py` 終了 **0** のあと、ユーザー報告の直前のみ（**`spec-crawl` SKILL**）

## coverage.xml（残す・再利用・必須）

**目的**: フル pytest は重い。有効な `coverage.xml` があれば **diff-cover のために再実行しない**。

- **置き場**: 各製品リポ直下の **`coverage.xml`**（pytest `--cov-report=xml` の既定。`.gitignore` 済み。**Git に入れない**）
- **完了時**: **削除しない**。`temp/` へ移さない。報告で「消した」と書かない
- **`.coverage`**: 直下に残ってよい（gitignore）。diff-cover には不要。わざわざ消さない
- **再利用してよい（有効）**: 直下に `coverage.xml` があり、計測対象の **`src/**/*.py`・`tests/**/*.py`** とカバレッジ設定（`pyproject.toml` / `pytest.ini`）の更新時刻が **xml と同じかより古い**
- **作り直す（無効・欠落）**: ファイルが無い／上記より新しいソース・テスト・設定がある／このセッションで `src/` または `tests/` を変えた直後で xml 未再生成／ユーザーが再計測を指示
- **無効な xml で `diff_cover_gate.sh` だけ走らせるのは禁止**（通る／落ちるが嘘になる）
- 再利用時はフル pytest を省略し、**`bash scripts/diff_cover_gate.sh WORKTREE`**（またはコミット時のフック）だけ実行してよい
- 手順の併用: **`test-code-generator` SKILL**（変更行 100%）

## 注意事項

- プロジェクト直下の **`commit_msg.txt` 等**は削除。**`coverage.xml` は残す**
- **myrules 正本**: `dev-workspace/.cursor/rules/myrules.mdc` **1 箇所のみ**（他リポに myrules を置かない）

## 関連

- **作業完了フロー**: `obsidian-cursor-log` SKILL（CursorLog 前の temp 空確認）
- **変更行カバレッジ**: `test-code-generator` SKILL（有効な xml の再利用）
- **コミットメッセージ**: `commit-message` SKILL（PowerShell 文字化け防止）
- **スクリプト一括置換禁止**: myrules「ファイル修正と差分確認」
- **spec-crawl 作業ディレクトリ**: FishTrack **`spec-crawl` SKILL**（`temp-spec-crawl/`）
