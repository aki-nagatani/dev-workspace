---
name: obsidian-second-brain
description: >-
  Obsidian はユーザーの第二の脳。AI チャット・調査・実装・意思決定で得た持続的な情報は、
  InBox 処理に限らず常に適切な Obsidian 正本へ集約する。**すべての Cursor 利用時**の横断原則。
  手順の正本は本 SKILL。InBox 入口は obsidian-inbox-summarize、Work は work-folder-update 等を併用。
---

# Obsidian 第二の脳（横断原則）

## 適用範囲（重要）

**`obsidian-inbox-summarize` 実行時だけではない。**

dev-workspace・FishTrack・MyPokedex・personal-tools 等、**すべての Cursor チャット・エージェント作業**で本原則を常に意識する。

## 原則

Obsidian ボールト（`OneDrive/git_work/Obsidian/`）はユーザーの**第二の脳**である。

AI チャット・調査・レビュー・設計判断・ユーザー訂正・外部資料の読解で**確定した情報**は、**チャット内だけに閉じず**、あとから辿れるよう **Obsidian の正本へ集約**する。

- **目的**: 第二の脳を開けば、**仕事・釣り・副業開発・学び・個人**のすべてについて、**いまの自分に使える情報**がそこにある状態を保つ
- **CursorLog** は作業の**証跡**（いつ何をしたか）。第二の脳の**すべてではない**（myrules「作業ログ」と併用）
- 領域ごとの専用正本（`Work/`・`Fishing/`・`DevProject/` 等）へ直接反映する

## ネット上の一般知識を保存しない（最優先）

**ネットで検索すれば再取得できる一般知識・製品説明・比較・手順・記事全文は、
Obsidian に保存しない。** 汎用の `Knowledge` フォルダは設けず、
インターネットの写しやブックマーク集を持たない。

- URL・Webクリップ・公開PDFから得た内容は、採用済みの設計・運用判断だけを該当する領域正本へ要約する。
- 個人の一次記録（釣行・本職の事実・個人運用の決定）は、`Fishing/`・`Work/`・`DevProject/`・`GrokBot/` などの領域正本へ直接記録する。
- ユーザーが原文そのものの保存を明示した場合だけ、その指示した保存先・範囲に従う。
- この節は、他のSKILLにある原文アーカイブや汎用知識への通常保存規則より優先する。

## ドメイン別正本マップ（正本）

| 領域 | 正本の置き場 | 典型コンテンツ | 更新時に Read する SKILL（該当時） |
| --- | --- | --- | --- |
| **外部記事・公開資料** | 保存しない | URL・記事全文・公開PDFの写しは保持しない | 採用済みの判断だけを領域正本へ |
| **釣り** | `Fishing/`（釣行は `釣行メモ.md`） | 釣行記録・フィールド・タックル | **`obsidian-inbox-summarize` 1.4.1** 等 |
| **本職（仕事）** | `Work/` | 人・案件・課題・定例・人事・暗黙知 | **`work-folder-update`**（課題は **`work-kadai-update`** 等） |
| **副業開発** | `DevProject/` | 仕様・設計・計画・運用メモ | **`specification-update`**・**`integrated-schedule-update`**（計画のみ） |
| **作業ログ** | `CursorLog/` | AI セッションの作業記録 | **`obsidian-cursor-log`** |

- **汎用のKnowledge領域は作らない**: インターネットで再取得できないユーザー固有の判断も、対象ドメインの正本へ書く。
- **領域専用正本**: そのドメインの**最新の事実・判断・経験**を `DevProject/specifications/`、`GrokBot/`、`Work/` 等へ直接反映する。

## いつ正本へ反映するか

**ユーザーが「Obsidian に書いて」と言わなくても**、次に当てはまれば**同一セッション内**で正本を更新する（`work-folder-update`「能動的な正本更新」と同趣旨）。

| きっかけ | 例 | 主な反映先 |
| --- | --- | --- |
| **チャットで確定** | 合意・方針・訂正・数値・運用判断 | 領域マップに従う |
| **実装・設計変更** | 仕様と実装の差分、破壊的変更の意図 | `DevProject/specifications/`（**`specification-update`**） |
| **調査・学習** | 採用済みの設計・運用判断 | 各領域の正本（ネット上の一般知識は保存しない） |
| **本職の事実** | メンバー・案件・課題・定例の内容 | `Work/`（**`work-folder-update`**） |
| **釣行・タックル** | 釣果・フィールドメモ | `Fishing/釣行メモ.md` 等 |
| **InBox 取り込み** | URL・PDF・音声・メモ | **`obsidian-inbox-summarize`** 一式 |
| **ユーザー明示** | 「Work に残して」「仕様を更新して」 | 指示どおり（本原則の具体化） |

## 反映しないもの（除外）

- **一時的なもの**: 単発 typo、デバッグ用の中間結果、再現不要な試行錯誤の羅列
- **ネット上で得ただけの知識**: 一般知識・記事全文・公開資料の写しは、ユーザーが原文保存を明示しない限り保存しない。採用済みの設計・運用判断だけを、領域に合う正本へ反映する。
- **ユーザーが記録不要と明示**したもの
- **ソースコードだけで足りる実装詳細**（ただし**設計判断・仕様変更・運用方針**は Obsidian へ）
- **`document-creation-policy`** に反する**無断の新規ドキュメント創作**（**既存正本の更新**・CursorLog・SKILL・仕様の同期は対象外）

## エージェントの姿勢

1. **チャットだけで収束させない**: 採用済みの判断・運用知識は、報告完了前に領域正本へ移す。ネット上で得ただけの一般知識・原文を自動で保存しない
2. **領域を問わず**: 仕事・釣り・開発・学びを漏らさない（該当 SKILL を Read してから編集）
3. **最新の正**: 古い記述を残したまま積み上げず、領域正本を上書き・差し替えする。
4. **報告だけにしない**: 「使えそう」とチャットに書いて終わらず、**移したパスを報告**に含める
5. **判断不能時のみ確認**: 保存先・領域が一意に決まらないときだけユーザーに聞く
6. **未合意の方針を確定として書かない**: エージェントの推奨は「提案」と明記する。\
    ユーザーが「それでよい」等を言うまで、領域正本 / 計画に「採用」「確定」と書かない（比較表は書いてよい）

## Obsidian への書き込み手段（厳禁・再発防止）

ボールト（`OneDrive/git_work/Obsidian/`）への更新は **Cursor の `Write` / `StrReplace` / `Delete` のみ**。

- **禁止**: シェル／スクリプトでのコピー・生成・上書き（`Copy-Item`・`shutil.copy` / `copy2`・`write_text`・`Set-Content` 等）
- **禁止の典型**: `temp/` にノートを生成したあと **シェルで Obsidian へコピー**する（件数・サイズ・サブエージェント失敗を理由にしない）
- **理由**: シェル経由だと Cursor の Review／差分に載らず、レビュー不能になる（ユーザー明示の禁止）
- **原因（2026-10-22 調査）**: Vault は git 管理外。Review に出るのは編集ツール（`StrReplace`・`Write`・`Delete`）で行った変更だけ。ルール文言だけでは再発したため、以下で機械的に止める
  - **フック**: ユーザー全体の `~/.cursor/hooks.json`（`beforeShellExecution`）→ `dev-workspace/scripts/cursor_hooks/guard_obsidian_shell_write.py`。
  - **拒否対象**: temp/（`temp-spec-crawl/` 含む）以外への書き込み系シェル（`Set-Content`・`Copy-Item`・`WriteAllText`・リダイレクト先・`--fix` 等）と `markdownlint --fix`。終了コード 2 で拒否する。Vault に限らず全ファイルが対象
  - **拒否されたら**: シェルを諦めて `StrReplace`／`Write`／`Delete` で同じ変更を行う
  - **`markdownlint-all.ps1`**: `-Fix` は廃止（全対象に `--fix` を当てていた。チェックのみ）
  - **検証**: `python dev-workspace/scripts/cursor_hooks/guard_obsidian_shell_write.py --self-test`（25 ケース）
- **正しい流れ**: `temp/` 生成物は **Read** → 正本パスへ **`Write` / `StrReplace`**（1 ファイルずつ）
- **横断正本**: myrules「ファイル修正と差分確認」・**`temp-file-management`** SKILL

## 報告前の自己チェック（CursorLog とは別）

myrules「作業ログ」（**`obsidian-cursor-log`**）に加え、ファイル変更や substantive な作業完了前に次を確認する。

1. **Q1**: このセッションで**持続的な情報**（事実・合意・知見・設計判断）が確定したか？
2. **Q2**: それらを **Obsidian のドメイン正本**へ反映したか？（CursorLog のみで終えていないか）
3. **Q3**: 未反映で価値があるものは、**残作業・課題**に明記したか？

**CursorLog だけでは第二の脳は育たない。** 仕様・Work・釣行メモ等の**領域正本**も更新する。

## 専用 SKILL への委譲（重複実装しない）

| 状況 | 正本 SKILL |
| --- | --- |
| InBox の 1 件処理 | **`obsidian-inbox-summarize`** |
| `Work/` 配下の編集 | **`work-folder-update`**（先に Read） |
| `Work/課題.md` | **`work-kadai-update`** |
| `DevProject/specifications/` | **`specification-update`** |
| `DevProject/plans/スケジュール.md` | **`integrated-schedule-update`** |
| CursorLog | **`obsidian-cursor-log`** |
| Markdown 体裁 | **`markdown-editing`** / **`markdownlint-fix`** |
| Wiki リンク・タグ | **`obsidian-update-rules`** |

迷ったら **本 SKILL のドメイン別正本マップ**で保存先を決め、該当 SKILL を Read してから編集する。

## 関連

- **`obsidian-inbox-summarize`**: InBox を入口とした取り込み手順（本原則の**具体ワークフロー**の一つ）
- **`work-folder-update`**: 本職（`Work/`）の能動的な正本更新
- myrules「ドキュメント配置方針」: 仕様・設計は Obsidian `DevProject/` に集約
