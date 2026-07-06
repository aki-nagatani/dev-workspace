# temp-file-management

Always respond in Japanese when applying this skill.

## 発火条件

- 一時ファイル（coverage、commit_msg、調査用 `debug_*.py` / `check_*.py` 等）を**新規作成**するとき
- リポジトリ直下に一時ファイルが残っているとき
- **コミット・push 完了後**（`commit_msg.txt` 等の削除）
- **チャット作業の完了・ユーザー報告前**（触ったリポの **`temp/` を空にする**）
- **次回も使うスクリプト**を置くとき（**`temp/` ではなく `scripts/` 等**）
- 手順の正本は **`SKILL.md`**
