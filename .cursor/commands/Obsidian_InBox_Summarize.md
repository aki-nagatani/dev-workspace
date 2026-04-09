# Obsidian InBox Summarize

myrulesを厳守して作業してください

`obsidian-inbox-summarize` SKILLを使用して、ObsidianのInBoxにあるノートを処理してください。

## 成果物（2段）

1. **原文全文（必須）**: 取得・読み込んだ内容を **Markdown の全文** として Obsidian に保存する（要約だけでなく、元記事相当の本文を残す）。
2. **Knowledge（必須）**: 従来どおり、実用的な知識をジャンル別ノートに追記・新規作成する。全文ノートへの `[[リンク]]` を参照に含める。

## 入出力ディレクトリ

- **InBoxディレクトリ**: `D:\OneDrive\アプリ\remotely-save\Obsidian\InBox\`
- **原文全文の保存先**: `D:\OneDrive\アプリ\remotely-save\Obsidian\Notes\Knowledge\Articles\`（存在しなければ作成する）
- **Knowledge保存先ディレクトリ**: `D:\OneDrive\アプリ\remotely-save\Obsidian\Notes\Knowledge\`

**重要**: このコマンドの1回の実行では「1件だけ」処理し、処理完了後に作業を中断してください。次のノートは、このコマンドを再実行して処理してください。

## Cursorログ更新（必須）

**🚨 処理完了後、必ずCursorログを更新してください。**

- `obsidian-cursor-log` SKILLを使用して、当日のCursorLogに作業内容を記録する
- 記録内容: 作業名、プロジェクト名、変更ファイル、実施内容、結果
- タグは作業内容に応じて適宜追加（例: `#obsidian`、`#inbox-summarize`、処理したジャンルのタグなど）
