---
name: datetime-jst
description: >-
  ドキュメント・計画書・ソースコメント等への日付・時刻記載。JST 実日時必須、
  プレースホルダー禁止、PowerShell/Python 取得例。CursorLog は obsidian-cursor-log に委譲。
  計画書メタ行・CursorLog・仕様更新で日付を書くときに使用。
---

# 日付・時刻記載（datetime-jst）

**myrules**「日付・時刻記載ルール」と同一趣旨。**一般ドキュメント・計画書・コメント**向け。**CursorLog 追記**は **`obsidian-cursor-log`** SKILL「日時の必須手順」が正本（本 SKILL と重複するが、Log 専用手順はそちらを優先）。

## 絶対ルール

**記載する日付・時刻は、その時点の実値を使う。プレースホルダー・仮の日付は禁止。**

- **禁止例**: `2025-01-XX`、`YYYY-MM-DD`、`--:--:--`、`00:00:00`（仮）、会話要約の日付のそのまま流用

## 発火条件

- Obsidian **計画書・仕様・CursorLog 以外**の Markdown に日付を書くとき
- **ソースコメント**に日付を残すとき
- **統合作業スケジュール**の `最終更新日` 等（詳細は **`integrated-schedule-update`** SKILL「計画書メタ行」）

## 形式

| 用途 | 形式 |
| --- | --- |
| 日付のみ | `YYYY-MM-DD`（例: `2025-11-20`） |
| 日時 | `YYYY-MM-DD HH:MM:SS` または `HH:mm:ss`（文脈に合わせる） |
| タイムゾーン | 特別指示がなければ **JST（UTC+9）** |
| 日付不明 | **現在日付を取得**するか、**省略**（プレースホルダー不可） |

## AI エージェントでの取得（必須）

**追記・記載の直前にターミナルで取得**する。推測・固定値・IDE 上の別日ファイル名を使わない。

### PowerShell（日付＋時刻を一括取得・推奨）

```powershell
$jst = [TimeZoneInfo]::ConvertTimeFromUtc((Get-Date).ToUniversalTime(), [TimeZoneInfo]::FindSystemTimeZoneById('Tokyo Standard Time'))
"date=$($jst.ToString('yyyy-MM-dd')) time=$($jst.ToString('HH:mm:ss'))"
```

日付のみ: `Get-Date -Format 'yyyy-MM-dd'`（JST が必要なら上記 `$jst` を使う）

### Python

```python
from datetime import datetime, timezone, timedelta
JST = timezone(timedelta(hours=9))
datetime.now(JST).strftime('%Y-%m-%d')
datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')
```

## CursorLog との分担

- **CursorLog 追記**: **`obsidian-cursor-log`** SKILL — 取得日付の `YYYY-MM-DD.md`、エントリ `HH:mm:ss`、**同一ターミナル実行で日付と時刻をまとめて取得**
- **計画書 `最終更新日`**: **`integrated-schedule-update`** — **`YYYY-MM-DD` のみ**（括弧に変更内容を書かない）

## 関連

- **myrules**: プレースホルダ禁止の横断原則
- **markdown-editing** / **obsidian-cursor-log**: Markdown 編集・Log 手順
