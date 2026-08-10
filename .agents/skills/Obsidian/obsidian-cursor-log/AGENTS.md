# obsidian-cursor-log

Always respond in Japanese when applying this skill.

## 発火条件（いずれかで **SKILL.md を Read してから**着手）

- ワークスペース内ファイル変更後のユーザー報告前（CursorLog 必須）
- **当日初めて** `CursorLog/YYYY-MM/YYYY-MM-DD.md` に追記するとき（**Q0: `obsidian-cursor-monthly-report` を先に**）
- 製品 `*_pull-request` / `*_commit` が CursorLog を要求するとき

**日報作成**は **`obsidian-cursor-monthly-report`** SKILL（本 SKILL の対象外）。

手順の正本は **`SKILL.md`**。

**Lint（追記時）**: URL は `<https://...>`。追記後 **markdownlint**（**MD034 必須**・同一ファイル `Summary: 0`）。

**同時書き込み**: 複数エージェントが同じ日次ログを触るときは、既存 `YYYY-MM-DD.md` の **`Write` 全文置換禁止**・追記直前の再 Read・保全検証・失敗時は `.parts` 退避（詳細は **`SKILL.md`「🚨 同時書き込み対策」**）。
