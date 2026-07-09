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
- **`static/css/`・`static/js/`** を**レイアウト**（見た目・配置・表・sticky・パネル・レスポンシブ）に影響させて変更するとき
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

## データ表の列スタイル（`:nth-child` 禁止）

**列の特定に `:nth-child` / `:nth-last-child` を使わない。** 列の追加・削除で番号がずれ、\
幅・sticky・一括編集レイアウトが壊れる（リール一覧のドラグクリック音列幅不具合等）。

### 必須パターン

1. **`colgroup` の `<col>`** に列クラスを付与（FishTrack: `ft-table__col--{field}`、MyPokedex: `pk-col--{field}`、取込: `spec-import-col--{field}`）
2. **`th` / `td`** に同名の列クラス（FishTrack: `ft-table__th--*` / `ft-table__cell--*`、MyPokedex: `pk-col--*`）を付与
3. **CSS の幅・sticky left/right** は **列クラス** と `colgroup` の `col` のみで指定
4. **JS で行を組み立てる**一覧・一括編集も、テンプレと**同じ列クラス**を付ける

### 行ストライプ（例外）

- **優先**: テンプレ／JS で `tr` に `is-odd` / `is-even` を付与し、`tr.is-odd td` で交互背景
- **`tbody tr:nth-child(even|odd)`** は、動的行で `is-odd` を付けられない場合のみ例外的に可（**列指定と併用禁止**）

### その他

- フォーム内の並びも **`__label` / `__value` 等の意味クラス**で指定（子要素番号に依存しない）
- 既存の `nth-child` 列指定を見つけたら、列クラスへ置換する（新規追加も同様）

## レイアウト変更後のブラウザ確認（必須）

**画面レイアウト**に触れた変更（テンプレ・CSS・レイアウト用 JS）は、テスト・ユーザー報告の**前**に**ローカル Docker**上の対象画面を**ブラウザで目視確認**する。省略しない。

| プロダクト | 手順の正本 |
| --- | --- |
| FishTrack | **`local-browser-verify`** SKILL（`FishTrack/.agents/skills/`）。AI 用アカウント・Cursor ブラウザ表示 |
| MyPokedex | **`local-browser-verify`** SKILL（`MyPokedex/.agents/skills/`）。AI 用アカウント・Cursor ブラウザ表示 |

- **確認観点**（代表）: ヘッダー・ナビ・表／フォーム配置・sticky・横スクロール・空状態・モーダル／パネル・主要ボタン
- **報告**: 確認した URL と気づいた点を短く記載する

## 関連

- **ブラウザ確認（FishTrack）**: **`local-browser-verify`** SKILL
- **ファイルサイズ**: `file-size-policy` SKILL（`static/` の CSS/JS）
- **FishTrack AGENTS.md**: タックル UI 共通化（テンプレ・JS・CSS の共通化方針）。**列幅・sticky は本 SKILL「データ表の列スタイル」**を正とする
- **MyPokedex AGENTS.md**: **`pk-col--*`** による図鑑・パーティ表の列指定
