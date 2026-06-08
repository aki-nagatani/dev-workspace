---
name: file-size-policy
description: >-
  ソース・テスト・CSS・JS のファイル行数上限（理想／許容／上限）。
  scripts/check_file_size.py と pre-commit 検査、超過時の分割方針。
  大きいファイルの分割検討、新規ファイル追加、リファクタ時に使用。
---

# ファイルサイズ規律（file-size-policy）

**myrules**「ファイルサイズ規律」と同一趣旨。**閾値表・超過時対応の正本は本 SKILL**。

## 発火条件

- **新規**に大きなモジュール・テスト・CSS/JS を追加するとき
- 既存ファイルが閾値に**近い／超過**しているとき（分割検討）
- pre-commit の **`check_file_size.py`** 失敗時

## 閾値一覧

| 種別 | 理想 | 許容 | 上限 | 備考 |
| --- | --- | --- | --- | --- |
| **`src/` Python 等** | 500行 | 1,000行 | 2,000行 | 超過時は分割を検討／推奨 |
| **`tests/`**（Python / JS 等） | 500行 | 1,000行 | 1,500行 | myrules「テスト規律」と整合 |
| **`src/` CSS** | 500行 | 1,000行 | 2,000行 | |
| **`static/` アプリ管理 CSS** | 同上 | 同上 | 同上 | `vendor` 配下は対象外 |
| **`src/`・`tests/` JS** | 500行 | 1,000行 | 2,000行 | |
| **`static/` アプリ管理 JS** | 同上 | 同上 | 同上 | `vendor` 配下は対象外 |

## 検査

- **`scripts/check_file_size.py`** および **pre-commit**（各リポの設定を正とする）
- 詳細背景: Obsidian `DevProject/guidelines/コーディング規約.md`（存在する場合）

## 超過時の対応

- **1,000行超**（src / static CSS・JS）: **分割を検討**
- **2,000行超**（src / static CSS・JS）: **分割を推奨**（機能別・責務別）
- **1,000行超**（tests）: **分割を検討**
- **1,500行超**（tests）: **分割を推奨**

分割時は既存 import・テスト実行パス・pre-commit が通る単位にする。

## 関連

- **テストカバレッジ・E2E**: `test-code-generator` SKILL
- **myrules**: 要点のみ（本 SKILL 参照）
