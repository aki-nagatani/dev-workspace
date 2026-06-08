---
name: temp-file-management
description: >-
  一時ファイルは各リポジトリの temp/ 配下のみ。プロジェクト直下禁止。
  カバレッジ・commit_msg・check_*.py 等の例、作業後削除・temp クリーンアップ、.gitignore 確認。
  一時ファイル作成・coverage.xml 配置・commit メッセージファイル作成時に使用。
---

# 一時ファイル管理（temp-file-management）

**myrules**「一時ファイル管理」と同一趣旨。**配置・例・クリーンアップの正本は本 SKILL**。

## 絶対ルール

**一時ファイルは必ず専用ディレクトリ配下に作成する。プロジェクト直下に作成してはならない。**

## 発火条件

- カバレッジ JSON/XML、コミットメッセージ用テキスト、調査用 `check_*.py` 等を**新規作成**するとき
- プロジェクトルートに `coverage.json` 等が残っているのを見つけたとき
- **コミット・push 完了後**（`commit_msg.txt` 等の削除）

## 配置場所

- **推奨**: 当該リポジトリの **`temp/`** 配下
- **禁止**: リポジトリ直下（`**/commit_msg.txt`、`**/coverage.json` 等）
- ディレクトリが無ければ作成（**`.gitignore` に `temp/` があるか確認**）

## 一時ファイルの例

- カバレッジ: `coverage_*.json`、`coverage_temp.json`、`coverage.xml`（必要なら `temp/` に）
- コミットメッセージ: `commit_msg.txt`、`commit_msg_*.txt`（**完了後必ず削除**）
- 調査・検証: `check_*.py`、`test_*.py`（一時）、`compare_*.py`、`fix_*.py`（一時）
- 中間データ: 実データを含まない `*.db`、`*.sql`、`*.json`、`*_schema.json` / `*_schema.py`

## 実行ルール

1. 作成時は **`temp/`** 配下
2. **作業完了後**、再利用しないものは**削除**
3. 直下に誤作成したファイルは**削除または `temp/` へ移動**

## temp クリーンアップ

**再利用しない一時ファイルは定期的に削除する。**

| 削除対象 | 保持 |
| --- | --- |
| `commit_msg*.txt`、一時 `check_*.py` / `test_*.py` / `compare_*.py` / `fix_*.py` | 実データ入り DB・画像・動画 |
| 一時 `coverage.*`、ダミー `*.json` / `*.sql` | 再利用するスクリプト |

**タイミング**: 作業完了時、またはセッション終了前に `temp/` を確認

## 注意事項

- **`coverage.xml`**: pytest の diff-cover 用にリポ直下に出る場合がある。運用上は生成後 **`temp/` へ移す**か、リポの慣習（`.gitignore`）に従う
- プロジェクト直下に残存があれば**削除**
- **myrules 正本**: `dev-workspace/.cursor/rules/myrules.mdc` **1 箇所のみ**（他リポに myrules を置かない）

## 関連

- **コミットメッセージ**: `commit-message` SKILL（PowerShell 文字化け防止）
- **スクリプト一括置換禁止**: myrules「ファイル修正と差分確認」
