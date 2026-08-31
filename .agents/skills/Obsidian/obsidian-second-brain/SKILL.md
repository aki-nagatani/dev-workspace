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

dev-workspace・FishTrack・MyPokedex・おたよりナビ・personal-tools 等、**すべての Cursor チャット・エージェント作業**で本原則を常に意識する。

## 原則

Obsidian ボールト（`D:/OneDrive/アプリ/remotely-save/Obsidian/`）はユーザーの**第二の脳**である。

AI チャット・調査・レビュー・設計判断・ユーザー訂正・外部資料の読解で**確定した情報**は、**チャット内だけに閉じず**、あとから辿れるよう **Obsidian の正本へ集約**する。

- **目的**: 第二の脳を開けば、**仕事・釣り・副業開発・学び・個人**のすべてについて、**いまの自分に使える情報**がそこにある状態を保つ
- **CursorLog** は作業の**証跡**（いつ何をしたか）。第二の脳の**すべてではない**（myrules「作業ログ」と併用）
- **Knowledge だけが脳ではない**。領域ごとの専用正本（`Work/`・`Fishing/`・`DevProject/` 等）へも反映する

## ドメイン別正本マップ（正本）

| 領域 | 正本の置き場 | 典型コンテンツ | 更新時に Read する SKILL（該当時） |
| --- | --- | --- | --- |
| **汎用知識・ツール** | `Notes/Knowledge/` | 技術・AI・運用の実用知見 | **`obsidian-inbox-summarize` §4**（Knowledge 集約・上書き方針） |
| **出典・原文** | `Notes/Knowledge/Articles/` | 記事全文・文字起こし原文 | **`obsidian-inbox-summarize` §1.5**（InBox／明示取り込み時） |
| **釣り** | `Fishing/`（釣行は `釣行メモ.md`） | 釣行記録・フィールド・タックル | **`obsidian-inbox-summarize` 1.4.1** 等 |
| **本職（仕事）** | `Work/` | 人・案件・課題・定例・人事・暗黙知 | **`work-folder-update`**（課題は **`work-kadai-update`** 等） |
| **副業開発** | `DevProject/` | 仕様・設計・計画・運用メモ | **`specification-update`**・**`integrated-schedule-update`**（計画のみ） |
| **作業ログ** | `CursorLog/` | AI セッションの作業記録 | **`obsidian-cursor-log`** |

- **Articles**: 出典の**エピソード記憶**（いつ何を読んだかの一次記録）
- **Knowledge**: 横断的な**統合理解**（現時点で信頼できる実用知見。**最新の正**に揃える。詳細は `obsidian-inbox-summarize` §4）
- **領域専用正本**: そのドメインの**最新の事実・判断・経験**（Knowledge に重複させず、正本へ直接反映）

## いつ正本へ反映するか

**ユーザーが「Obsidian に書いて」と言わなくても**、次に当てはまれば**同一セッション内**で正本を更新する（`work-folder-update`「能動的な正本更新」と同趣旨）。

| きっかけ | 例 | 主な反映先 |
| --- | --- | --- |
| **チャットで確定** | 合意・方針・訂正・数値・運用判断 | 領域マップに従う |
| **実装・設計変更** | 仕様と実装の差分、破壊的変更の意図 | `DevProject/specifications/`（**`specification-update`**） |
| **調査・学習** | 記事・ドキュメントから得た実用知見 | `Notes/Knowledge/`（出典は Articles） |
| **本職の事実** | メンバー・案件・課題・定例の内容 | `Work/`（**`work-folder-update`**） |
| **釣行・タックル** | 釣果・フィールドメモ | `Fishing/釣行メモ.md` 等 |
| **InBox 取り込み** | URL・PDF・音声・メモ | **`obsidian-inbox-summarize`** 一式 |
| **ユーザー明示** | 「Work に残して」「仕様を更新して」 | 指示どおり（本原則の具体化） |

## 反映しないもの（除外）

- **一時的なもの**: 単発 typo、デバッグ用の中間結果、再現不要な試行錯誤の羅列
- **ユーザーが記録不要と明示**したもの
- **ソースコードだけで足りる実装詳細**（ただし**設計判断・仕様変更・運用方針**は Obsidian へ）
- **`document-creation-policy`** に反する**無断の新規ドキュメント創作**（**既存正本の更新**・CursorLog・SKILL・仕様の同期は対象外）

## エージェントの姿勢

1. **チャットだけで収束させない**: 次回以降も参照する価値がある情報は、報告完了前に正本へ移す
2. **領域を問わず**: 仕事・釣り・開発・学びを漏らさない（該当 SKILL を Read してから編集）
3. **最新の正**: 古い記述を残したまま積み上げない（Knowledge は上書き・差し替え。`obsidian-inbox-summarize` §4）
4. **報告だけにしない**: 「使えそう」とチャットに書いて終わらず、**移したパスを報告**に含める
5. **判断不能時のみ確認**: 保存先・領域が一意に決まらないときだけユーザーに聞く
6. **未合意の方針を確定として書かない**: エージェントの推奨は「提案」と明記する。\
    ユーザーが「それでよい」等を言うまで、Knowledge / 計画に「採用」「確定」と書かない（比較表は書いてよい）

## 報告前の自己チェック（CursorLog とは別）

myrules「作業ログ」（**`obsidian-cursor-log`**）に加え、ファイル変更や substantive な作業完了前に次を確認する。

1. **Q1**: このセッションで**持続的な情報**（事実・合意・知見・設計判断）が確定したか？
2. **Q2**: それらを **Obsidian のドメイン正本**へ反映したか？（CursorLog のみで終えていないか）
3. **Q3**: 未反映で価値があるものは、**残作業・課題**に明記したか？

**CursorLog だけでは第二の脳は育たない。** 仕様・Knowledge・Work・釣行メモ等の**中身**も更新する。

## 専用 SKILL への委譲（重複実装しない）

| 状況 | 正本 SKILL |
| --- | --- |
| InBox の 1 件処理 | **`obsidian-inbox-summarize`** |
| `Work/` 配下の編集 | **`work-folder-update`**（先に Read） |
| `Work/課題.md` | **`work-kadai-update`** |
| `DevProject/specifications/` | **`specification-update`** |
| `DevProject/plans/統合作業スケジュール.md` | **`integrated-schedule-update`** |
| CursorLog | **`obsidian-cursor-log`** |
| Markdown 体裁 | **`markdown-editing`** / **`markdownlint-fix`** |
| Wiki リンク・タグ | **`obsidian-update-rules`** |

迷ったら **本 SKILL のドメイン別正本マップ**で保存先を決め、該当 SKILL を Read してから編集する。

## 関連

- **`obsidian-inbox-summarize`**: InBox を入口とした取り込み手順（本原則の**具体ワークフロー**の一つ）
- **`work-folder-update`**: 本職（`Work/`）の能動的な正本更新
- myrules「ドキュメント配置方針」: 仕様・設計は Obsidian `DevProject/` に集約
