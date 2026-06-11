# work-folder-update

Always respond in Japanese when applying this skill.

## 発火条件（次のいずれかで、Work 配下を編集する前に本 SKILL を使う）

- **`Obsidian/Work/`** 配下の **`.md` / `.csv`** を **作成・更新・削除**する
- ユーザーが **`@Obsidian/Work`** または Work 内パスを指定した
- **`work-kadai-update`**・**`mokuhyo-*`**・**`work-knowledge-deepen`** で Work を変更する

## 必須の最初アクション

**`StrReplace` / `Write` / `Delete` 等を呼ぶ前に** **`SKILL.md` を Read ツールで全文読む**（**`AGENTS.md` のみ・要約だけでは不可**）。手順の正本は **`SKILL.md`**。

## 目的

Work に関する**ありとあらゆる業務情報**（人・案件・課題・手続き・暗黙知・数値・合意・訂正等）を、**依頼ファイル以外のチャットからも**拾い、**正本ノートへ振り分けて記録**する。詳細は **`SKILL.md` § 収集対象・Work フォルダ構成・記録の横断ルール**。

## 適用範囲

**「仕事」＝株式会社DTSにおける本職**。FishTrack・MyPokedex・おたよりナビ等の**副職・趣味**（`DevProject/`・製品リポ含む）は**対象外**。

## 記録先（要点）

- **本人（PL）**: `Work/メンバー情報/長谷晃英.md`
- **配下**: `Work/メンバー情報/`。**プロパー**は `{フルネーム}.md`（スペースなし）、**客員**は `{会社名}.md` が正本（索引ファイルなし。人数・構成は `所属・役割・プロジェクト概要`）

## 併用

- 課題ブロック: **`work-kadai-update`**
- 管理シート・CSV: **`mokuhyo-kanri-sheet-csv`** 等
- 暗黙知深掘り: **`work-knowledge-deepen`**
- Markdown: **`markdown-editing`** / **`markdownlint-fix`**
- 完了後: **`obsidian-cursor-log`**
