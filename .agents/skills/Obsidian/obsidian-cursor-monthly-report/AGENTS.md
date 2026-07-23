# obsidian-cursor-monthly-report

Always respond in Japanese when applying this skill.

## 発火条件（いずれかで **SKILL.md を Read してから**着手）

- ユーザーが **「日報」「月次日報」「昨日の日報」「日報作成」** を依頼したとき
- **`obsidian-cursor-log` Q0**: 当日初めて `CursorLog/YYYY-MM/YYYY-MM-DD.md` に追記する直前（前日分が未日報化なら先に本 SKILL）

## 要点

- **正本**: `CursorLog/YYYY-MM/YYYY-MM 日報.md`（日単位ファイルは作らない）
- **入力**: 対象日の `YYYY-MM-DD.md` を**全文 Read**（チャット要約だけ禁止）
- **出力**: `## YYYY-MM-DD` 節をジャンル別（`###`）に要約追記
- **検証**: markdownlint 必須
- **報告**: `## YYYY-MM-DD` を追記済みと明記。続けて **`obsidian-cursor-log`** で作業エントリを追記

手順の正本は **`SKILL.md`**。
