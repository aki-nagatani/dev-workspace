---
name: cursor-ide-browser-position
description: >-
  Cursor 内蔵ブラウザ（cursor-ide-browser MCP）の開き方。
  ブラウザはサイドで開かない。position: "side" 禁止。既定は position 省略（バックグラウンド）。
  ユーザーが明示で見せてほしいとき・内部ブラウザ指示・UI 監査レポート表示は position: "active"。
  実ブラウザの画面確認は cursor-ide-browser のみ。Playwright／Chrome 等の外部ブラウザは使わない。
  FishTrack プレビューの本家も同じ。
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
3. **ユーザーがチャットで「見せて」「最前面」「表示して」「内部ブラウザ」と明示したとき**、または **`ui-audit-html-report` のレポート表示**だけ、`position: "active"` を使う。
4. **禁止の言い換えも同じ**: `"side"` / `"beside"` / サイドパネル / 左右分割でブラウザを開くこと。

## 再発防止

- **誤**: 目視確認のために `position: "side"` を付ける（エディタ中央・横をブラウザが占有する）。
- **正**: 確認は `position` 省略で進める。見せる必要が明示されたときだけ `"active"`。

## 実ブラウザ確認（全製品）

画面の目視・操作・スクショは **`cursor-ide-browser` のみ**。

- **禁止**: Playwright MCP（`user-playwright`）、OS の Chrome / Edge 等の外部ブラウザ
- **ログイン済みでも切り替えない**: Cursor 内のタブがログイン中でも、未ログイン確認を Chrome で取り直さない。対象 URL は Cursor 内ブラウザで開く。未ログイン画面に入れないときは、その事実を報告する
- **配置**: 本 SKILL（`"side"` 禁止。既定は `position` 省略。見せるとき・「内部ブラウザ」指示時は `"active"`）
- **静的 HTML** のテキスト取得は `WebFetch` / httpx 可（ブラウザを開かない）
- **pytest の Playwright E2E** はテスト実行であり、本節の実ブラウザ確認ではない

## プレビュー／本家確認（FishTrack AI スペック）

本家ページを**ブラウザで開く**ときも、上記と同じく **`cursor-ide-browser` のみ**。

手順の正本は **`ai-spec-check-preview`** / **`ai-spec-import`**。

## 併用

- FishTrack / MyPokedex のログイン・アカウント: 各リポ **`local-browser-verify`**
- UI 監査レポートの最前面: **`ui-audit-html-report`**（こちらも `"side"` 禁止。表示時は `"active"`）
- FishTrack プレビュー本家: **`ai-spec-check-preview`**（Playwright／外部ブラウザ禁止）
