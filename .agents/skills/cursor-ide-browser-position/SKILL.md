---
name: cursor-ide-browser-position
description: >-
  Cursor 内蔵ブラウザ（cursor-ide-browser MCP）の開き方。
  ブラウザはサイドで開かない。position: "side" 禁止。既定は position 省略（バックグラウンド）。
  ユーザーが明示で見せてほしいときと UI 監査レポート表示だけ position: "active"。
  browser_navigate / browser_tabs の position、サイドパネル、エディタ分割時に使用。
---

# Cursor ブラウザはサイドで開かない

**ブラウザはサイドで開かないこと。** 全作業共通。FishTrack / MyPokedex / おたよりナビ / UI 監査 / その他を問わない。

## 発火条件

次のいずれかで、**`browser_navigate` / `browser_tabs` を呼ぶ前に**本 SKILL に従う。

- Cursor 内蔵ブラウザ（`cursor-ide-browser` MCP）でページを開く・タブを新規作成する
- `position` 引数を付けようとする
- 画面確認・スクショ・ログイン操作・UI 監査レポート表示

## 必須（具体動作）

1. **`position: "side"` を付けない**（`browser_navigate`・`browser_tabs` の `action: "new"` とも）。
2. **既定**: `position` を**省略**する（バックグラウンド。エディタをサイドパネルで割らない。フォーカスを奪わない）。
3. **ユーザーがチャットで「見せて」「最前面」「表示して」と明示したとき**、または **`ui-audit-html-report` のレポート表示**だけ、`position: "active"` を使う。
4. **禁止の言い換えも同じ**: `"side"` / `"beside"` / サイドパネル / 左右分割でブラウザを開くこと。

## 再発防止

- **誤**: 目視確認のために `position: "side"` を付ける（エディタ中央・横をブラウザが占有する）。
- **正**: 確認は `position` 省略で進める。見せる必要が明示されたときだけ `"active"`。

## 併用

- FishTrack / MyPokedex のログイン・アカウント: 各リポ **`local-browser-verify`**
- UI 監査レポートの最前面: **`ui-audit-html-report`**（こちらも `"side"` 禁止。表示時は `"active"`）
