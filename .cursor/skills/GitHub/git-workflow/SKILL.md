---
name: git-workflow
description: >-
  ブランチ運用（develop/main）、無断コミット禁止、コミット・PR 前の自問チェック、
  単発 SKILL 依頼の扱い、LF 改行。FishTrack/MyPokedex/otayori-navi の develop 運用。
  コミット・push・PR・マージの依頼時、または git 操作の可否判断時に使用。
---

# Git 運用（git-workflow）

**myrules**「Git運用」「ファイル改行ポリシー」と同一趣旨。**手順・自問チェックの正本は本 SKILL**。

## 発火条件

- **`git commit` / `git push` / `gh pr create` / `gh pr merge`** 等を実行しようとするとき
- ユーザーが「コミットして」「PR 作って」等と**明示**したとき（**コード修正のみ**の依頼では発火しない）
- ブランチ方針・改行コードの確認時

## ブランチ運用方針

**MyPokedex、FishTrack、otayori-navi の3リポジトリに限り**、`develop` を作業用とし、リリース時のみ `main` へマージする。（`dev-workspace`・`personal-tools` 等は対象外。）

- **`main`**: 本番（更新で即デプロイ）。**直接プッシュ禁止**
- **`develop`**: 日常のコミット・プッシュ先
- **フロー**: 開発は `develop` → リリース時に GitHub で `main` ← `develop` の PR をマージ
- **例外**: 新規プロジェクトで `develop` が無いときは初回のみ `main` で構築し、準備後 `develop` へ移行

各製品のコミット・PR 手順は **当該リポ** の SKILL が正本:

| 製品 | コミット | PR まで |
| --- | --- | --- |
| FishTrack | `FishTrack_commit` | `FishTrack_pull-request` |
| MyPokedex | `MyPokedex_commit` | `MyPokedex_pull-request` |
| otayori-navi | （`otayori-navi_pull-request` 内） | `otayori-navi_pull-request` |
| 複数リポ | — | `commit-all` |

**フィーチャーブランチは新規作成しない**（ユーザー明示時のみ例外）。製品 SKILL は **`develop` 上でコミット・push** を前提とする。

## コミット運用ポリシー

- **ユーザーの明示的な許可がない限り、コミット・プッシュを実行しない**
- 「コミットしてください」等の**明示依頼**がある場合に限りコミット
- **`*_pull-request` / `*_commit` / `commit-all` は 1 チャット 1 回限り**の依頼
  - **`git commit` 失敗時**: 原因を直し**成功まで**再試行可（未成功の間のみ継続有効）
  - **`git commit` が 1 回成功した時点**で、当該依頼内の**追加の新規コミット**は不可（同一フロー内の push / PR / マージは可）
  - フロー**完了後**は、新たな明示がない限り `git commit` / `git push` しない
- **コンベンショナルコミット**（feat:, fix:, docs:, test:, refactor:, chore:）
- **コミットメッセージは日本語**（PowerShell 文字化け防止は **`commit-message`** SKILL）
- **`commit_msg.txt` 等**はコミット・プッシュ完了後に**必ず削除**

## 🚨 コミット・PR・マージ・デプロイ実行前の自問チェック（必須）

**以下のいずれかを実行する直前に、3 項目を自問。1 つでも「YES」と確信できなければ実行しない。**

- 対象: `git commit` / `git push` / `gh pr create` / `gh pr merge` / `gh run watch`

1. **今回のユーザー指示**はコミット系の**明示依頼**か？
2. その依頼は**今回の修正内容**向けか？（前ターンの `*_pull-request` を暗黙継続していないか）
3. 迷えば**ユーザーに確認**したか？

**補足**:

- 「コードを直して」「バグを修正して」等は**修正のみ**（コミット依頼を含まない）
- 各ユーザー指示は**独立**。前ターンのコミット系 SKILL は**単発**（成功後は失効）
- 修正完了後は**「コミット/PR に進めてよろしいですか？」と確認のみ**で一旦停止

### 過去違反の記録（再発防止）

- **2026-04-21**: コード修正のみの指示で、前ターンの `FishTrack_pull-request` を暗黙継続し PR #154 / #155 を独断マージ・本番デプロイ。上記自問チェックで再発防止。

## ファイル改行ポリシー

- テキストファイルは改行 **`LF`** を維持（Windows でも CRLF に変換しない）
- **`.gitattributes`** の設定を尊重

## 関連 SKILL

- **`commit-message`**: メッセージ作成・PowerShell UTF-8
- **`commit-all`**: 複数リポ一括コミット
- **`github-actions-check`**: push / マージ後の CI 待機
