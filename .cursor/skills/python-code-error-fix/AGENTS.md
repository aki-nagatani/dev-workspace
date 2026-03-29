# python-code-error-fix

Always respond in Japanese when applying this skill.

## 発火条件（次のいずれかで、修正に着手する前に本 SKILL を使う）

- **Python の構文エラー**（`SyntaxError` / `IndentationError`、パーサが通らない）
- **Python の型チェッカー**（basedpyright、Pyright、Pylance、mypy 等）の指摘を直す
- **Python の Lint / 解析エラー**（未定義名、誤った import、引数・シグネチャ不一致など）
- **「このエラーを直して」「ビルド・テストが落ちる」** で原因が **Python ソース**にあるとき
- ユーザーが **言語を限定していないが**、対象が `.py` の修正であるとき

## 必須の最初アクション

**`SKILL.md` を Read ツールで読んでから**修正する。汎用フロー → 該当する節（構文 / 型 / 付録）の順。

## 対象外

- **Markdownlint** → `markdownlint-fix` SKILL
- **主にスタイルのみ**の整理 → プロジェクトの formatter / Lint 設定に従う（本 SKILL は必須ではない）
- **JavaScript / TypeScript 等** → 別途その言語の手順

## 適用範囲

dev-workspace および連携リポジトリ（MyPokedex、FishTrack、otayori-navi 等）の **Python コード**。
