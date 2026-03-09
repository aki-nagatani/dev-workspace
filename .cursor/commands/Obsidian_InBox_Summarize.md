# Obsidian InBox Summarize

myrulesを厳守して作業してください

`obsidian-inbox-summarize` SKILLを使用して、ObsidianのInBoxにあるノートを要約してナレッジとして保存してください。

## 入出力ディレクトリ

- **InBoxディレクトリ**: `D:\OneDrive\アプリ\remotely-save\Obsidian\InBox\`
- **Knowledge保存先ディレクトリ**: `D:\OneDrive\アプリ\remotely-save\Obsidian\Notes\Knowledge\`

**重要**: このコマンドの1回の実行では「1件だけ」処理し、処理完了後に作業を中断してください。次のノートは、このコマンドを再実行して処理してください。

## Cursorログ更新（必須）

**🚨 処理完了後、必ずCursorログを更新してください。**

- `obsidian-cursor-log` SKILLを使用して、当日のCursorLogに作業内容を記録する
- 記録内容: 作業名、プロジェクト名、変更ファイル、実施内容、結果
- タグは作業内容に応じて適宜追加（例: `#obsidian`、`#inbox-summarize`、処理したジャンルのタグなど）
