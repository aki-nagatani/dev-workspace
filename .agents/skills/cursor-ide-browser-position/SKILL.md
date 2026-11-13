---
name: cursor-ide-browser-position
description: >-
  Cursor 内蔵ブラウザを開く際の position 指定。サイドで開かない（"side" 禁止）。既定は省略、見せるときは "active"。browser_navigate・browser_tabs の指定時に使用。
---

# Cursor ブラウザはサイドで開かない

**ブラウザはサイドで開かないこと。** 全作業共通。FishTrack / MyPokedex / UI 監査 / その他を問わない。

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

人への表示は **`cursor-ide-browser`**。専用プロファイルの MCP 設定が終わるまでの操作確認も、同じ内蔵ブラウザで行う。

- **禁止**: Playwright MCP（`user-playwright`）、普段使いの Chrome / Edge
- **ログイン済みでも切り替えない**: 人への表示を、普段使いの Chrome で取り直さない。未ログイン画面に入れないときは、その事実を報告する
- **配置**: 本 SKILL（`"side"` 禁止。既定は `position` 省略。見せるとき・「内部ブラウザ」指示時は `"active"`）
- **静的 HTML** のテキスト取得は `WebFetch` / httpx 可（ブラウザを開かない）
- **pytest の Playwright E2E** はテスト実行であり、本節の実ブラウザ確認ではない

## 実装変更の画面操作確認

ユーザーが操作する画面に影響する実装を変えたときは、操作確認を専用プロファイルの Chrome DevTools MCP で行う。

- **対象**: クリック、入力、遷移、ファイル選択、画面サイズの切り替え。画面に影響しない変更だけでは、この節でブラウザを開かない
- **人への表示**: 内蔵ブラウザのまま。サイドでは開かない
- **接続**: 専用の user-data-dir、または `--isolated`。普段使いの Chrome、`--autoConnect`、普段使いのデバッグポートには繋がない。利用統計は切る
- **設定前**: 専用プロファイルの MCP 設定が終わるまでは、操作確認も内蔵ブラウザで行う。設定を先に変えない
- **pytest の Playwright E2E** はテスト実行であり、この節の操作確認ではない

## プレビュー／本家確認（FishTrack AI スペック）

本家ページを**ブラウザで開く**ときも、上記と同じく **`cursor-ide-browser` のみ**。

手順の正本は **`ai-spec-check-preview`** / **`ai-spec-import`**。

## 併用

- FishTrack / MyPokedex のログイン・アカウント: 各リポ **`local-browser-verify`**
- UI 監査レポートの最前面: **`ui-audit-html-report`**（こちらも `"side"` 禁止。表示時は `"active"`）
- FishTrack プレビュー本家: **`ai-spec-check-preview`**（Playwright／外部ブラウザ禁止）
