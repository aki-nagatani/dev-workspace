---
name: frontend-html-template
description: >-
  Jinja/HTML テンプレートのフロント規律。インライン script/style 禁止、
  static/js・static/css への分離、CDN と1行初期化の例外。
  FishTrack / MyPokedex / otayori-navi のテンプレ・静的ファイル編集時に使用。
---

# HTML テンプレート規律（frontend-html-template）

**myrules**「HTMLテンプレート規律」と同一趣旨。**FishTrack / MyPokedex / otayori-navi** の Jinja テンプレート向け。

## 発火条件

- **`templates/`** 配下の HTML/Jinja を編集・新規作成するとき
- テンプレに **JavaScript / CSS** を足す依頼があるとき
- **CSP**・保守性・Jest 単体テストの観点でインラインコードを検討するとき

## インラインスクリプト禁止

- HTML 内に `<script>...</script>` で **JS 本体を直接書かない**
- JS は **`static/js/`** に置き **`<script src="...">`** で読み込む

### 許容例外（script）

- **外部 CDN**（例: `<script src="https://js.hcaptcha.com/1/api.js">`）
- **初期化の 1 行**（例: `<script>initFunction('param');</script>`）

## インラインスタイル禁止

- 要素に **`style="..."`** を書かない
- スタイルは **`static/css/`** のクラスで定義し **`class`** で適用

### 許容例外（style）

- **スタンドアロン**で外部 CSS を読めないページ（例: メンテナンス画面）の **`<head>` 内 `<style>`** ブロック

## 理由（要約）

- 再利用・保守性、外部 JS の単体テスト、CSP 対応、キャッシュ効率

## 関連

- **ファイルサイズ**: `file-size-policy` SKILL（`static/` の CSS/JS）
- **FishTrack AGENTS.md**: タックル UI 共通化（テンプレ・JS・CSS の共通化方針）
