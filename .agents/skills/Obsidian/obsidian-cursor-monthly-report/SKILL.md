---
name: obsidian-cursor-monthly-report
description: >-
  CursorLog 日次記録を月次ファイル `CursorLog/YYYY-MM/YYYY-MM 日報.md` にジャンル別要約する正本。
  発火: ユーザーが「日報」「昨日の日報」「月次日報」「日報作成」を依頼したとき。
  当日初めて CursorLog に追記する直前の Q0 ゲート（前日分の未日報化を先に処理）。
  最初のアクションは本 SKILL を Read。対象日の YYYY-MM-DD.md を全文 Read してから要約（チャット要約禁止）。
  markdownlint 検証必須。完了報告に `## YYYY-MM-DD` 追記済みを明記。
---

# CursorLog 月次日報

日次 CursorLog（`CursorLog/YYYY-MM/YYYY-MM-DD.md`）を、月 1 ファイルの日報（`CursorLog/YYYY-MM/YYYY-MM 日報.md`）へ**ジャンル別に要約**する手順の正本。

**CursorLog 追記**（エントリ形式・タグ・時刻・重複防止）は **`obsidian-cursor-log`** SKILL が正本。本 SKILL は**日報化のみ**。

## 発火条件（いずれかで **本 SKILL.md を Read してから**着手）

- ユーザーが **「日報」「月次日報」「昨日の日報」「日報作成」** 等を依頼したとき（**独立タスク**）
- **`obsidian-cursor-log`** の **Q0 / 手順 0**: 当日初めて `YYYY-MM-DD.md` に追記する直前（前日分が未日報化なら先に本 SKILL を実行）
- **FishTrack_pull-request** 等で当日初めて CursorLog を書くとき（Q0 と同様）

**禁止**: チャット要約・開いている CursorLog タブ・前セッションの記憶だけで日報を書くこと。

## 保存形式

- 日報は**日単位のファイルにしない**。月ごとに 1 ファイルだけ。
- 保存先: `D:/OneDrive/アプリ/remotely-save/Obsidian/CursorLog/YYYY-MM/YYYY-MM 日報.md`\
  例: 2026 年 7 月 → `CursorLog/2026-07/2026-07 日報.md`
- H1 は `# YYYY-MM 日報`、各日分は `## YYYY-MM-DD` 見出しで追記。
- 同じ日付の見出しが既にある場合は**重複作成しない**。不足があれば既存節を更新。
- 1 日分の節は見出し・空行を含め **10 行程度**を目安（分類の明確さを優先して超えてよい）。
- 箇条書きは `### ジャンル名` で分類。下に完了事項・検証結果・残作業を記載。
- 大分類例: `FishTrack`、`MyPokedex`、`FaiNavi`、`MiteneKeeper`、`Work`、`Obsidian`、`dev-workspace`
- FishTrack 内は必要に応じて `####`（`AIスペック取り込み`、`ルアー管理`、`釣行メモ` 等）で細分化。
- **ファイル列挙や作業経過の再掲はしない**。

## 手順（ユーザー依頼時）

1. JST の現在日付をターミナルで取得する（**`datetime-jst`** SKILL 参照可）。
2. 依頼が「昨日」なら **前日（JST）** を対象日とする。日付が明示されていればそれを優先。
3. `YYYY-MM 日報.md` を Read し、対象日の `## YYYY-MM-DD` が**既にあるか**確認。
4. 未作成なら、対象日の `YYYY-MM-DD.md` を**全文 Read**して要約する。
5. `## YYYY-MM-DD` 節を `StrReplace` / `Write` で追記（myrules の編集ツール規律に従う）。
6. markdownlint を検証する（`dev-workspace` の `.markdownlint.json`）。
7. 同一セッションで **`obsidian-cursor-log`** に「月次日報作成」エントリを 1 件追記する。
8. 報告文に **`CursorLog/YYYY-MM/YYYY-MM 日報.md` に `## YYYY-MM-DD` を追記済み** と明記する。

## 手順（Q0・当日初回 CursorLog 追記前）

**発火**: 対象月の `YYYY-MM-DD.md` を**その日初めて**追記する直前（新規ファイル作成・当日最初の `##` の前）。\
**当日分の日報化は禁止**（前日以前のみ）。

1. JST の現在日付を取得する。
2. 当日より前の日次 CursorLog から、月次日報に同じ日付の節が**ない**ものを探す。\
   候補のうち**日付が最も新しい 1 日だけ**を選ぶ。
3. 対象日の `YYYY-MM-DD.md` を全文 Read。`YYYY-MM 日報.md` を Read して日付重複を確認。
4. ジャンル別に要約し `## YYYY-MM-DD` 節を追記。
5. markdownlint 検証後、**`obsidian-cursor-log`** の手順に戻り当日ログを追記する。

## 完了前の自己確認

```powershell
Select-String -Path "D:/OneDrive/アプリ/remotely-save/Obsidian/CursorLog/2026-07/2026-07 日報.md" -Pattern '^## 2026-07-17$'
```

（パス・日付は対象に合わせて置換。ヒットしなければ未作成）

## 禁止事項

- **当日分**を当日中に日報化しない。
- `YYYY-MM-DD_日報.md` など、**日単位の日報ファイル**を新規作成しない。
- 過去の日次 CursorLog がない、またはすべて日報化済みのときに**空の節**を作らない。

## 記録漏れ・違反事例

### 忘れやすいパターン（禁止）

- 「日報作成」依頼なのに本 SKILL を Read せず、会話内要約だけで終える
- 当日初回 CursorLog で Q0 をスキップし `YYYY-MM-DD.md` だけ新規作成（2026-07-16 事例）
- 手順が `obsidian-cursor-log` 後方に埋もれ、独立 SKILL として発火しない

### 違反事例（2026-07-16）

- **事象**: `2026-07-16.md` を新規作成したが、前日の月次日報節を追記しなかった
- **対策**: Q0 ゲートと本 SKILL を独立正本化（2026-07-18）

### 違反事例（2026-07-18）

- **事象**: 「昨日の日報作成」依頼で SKILL 未参照のまま着手しがち
- **対策**: 本 SKILL を `obsidian-cursor-log` から分離（本ファイル）

## 併用

- **Markdown 編集**: `markdown-editing` / `markdownlint-fix` SKILL
- **CursorLog エントリ追記**: 完了後は **`obsidian-cursor-log`** SKILL
- **日時取得**: JST はターミナル取得必須（CursorLog 専用手順は `obsidian-cursor-log`）

## ユーザー指摘に伴う更新

日報の粒度・ジャンル分類・発火条件についてユーザー指摘があった場合は、**同一セッションで本 SKILL を更新**する（myrules「ユーザー指摘に基づくルール・SKILL の育成」）。
