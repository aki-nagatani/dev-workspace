---
name: obsidian-update-rules
description: ObsidianのMarkdown更新ルールを適用し、主に D:/OneDrive/アプリ/remotely-save/Obsidian 配下の編集時にタグやリンクを適切に付与する。ユーザーがObsidianフォルダやノート編集を指示したときに使用する。
---

# Obsidian Update Rules

## 適用条件

- **主な対象**: `D:/OneDrive/アプリ/remotely-save/Obsidian` 配下（myrules の CursorLog・仕様書パスと同じボールト）
- **別ボールト**: ユーザーが編集対象として**別フォルダの絶対パスを明示**した場合のみ、そのパスに限定して適用する（存在しないパスを推測・例示しない）
- 上記いずれにも該当しないパスではこの SKILL を適用しない

## Markdown編集ルール

- **必須**: 本SKILL適用時は、`markdown-editing` SKILLのルールに従う
  （行長・URL表記・編集方針等は markdown-editing に集約済み）
- **仕様書**（例: `DevProject/specifications/` 配下）を編集するときは **`specification-update`** SKILL を優先し、Markdown 体裁は **`markdown-editing`** に従う

## 更新ルール（必須）※Obsidian固有

1. 既存のフロントマター（`---`）があれば内容を保全し、必要時のみ追記
2. 既存のリンク形式（Wikiリンク `[[...]]` / Markdownリンク `[text](url)`）を尊重

## タグ/リンク付与方針（自動付与）

- 重要語（固有名詞、システム名、機器名、手順名、プロジェクト名）が出たら、
  可能なら `[[既存ノート名]]` へのWikiリンクを優先
- 該当ノートが存在しない場合は、タグ `#keyword` を付与（英小文字・ハイフン推奨）
- 既存タグ体系がある場合はそれに合わせる（例: `#infra/raspi` のような階層タグ）
- 1ノート内のタグは過剰にならない範囲で付与（目安: 3〜8個）

## 追記・編集の優先順

1. 既存の関連リンクがあるか確認し、重複追加しない
2. 既存タグを再利用し、必要に応じて最小限の追加
3. 参照先が明確な場合はリンク、曖昧ならタグ

## 禁止事項

- ノート全体の書き換えや大幅な再構成
- 既存のリンク・タグの削除（明確な指示がある場合を除く）
- 規則のない新しいタグ体系の導入

## 例

**入力**: 「Raspberry Pi の運用手順を更新」
**対応**:

- `[[Raspberry Pi]]` へのリンク追加
- `#raspberry-pi` や既存タグ体系に合わせたタグ付与
