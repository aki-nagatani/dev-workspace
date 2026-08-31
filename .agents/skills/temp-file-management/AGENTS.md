# temp-file-management

Always respond in Japanese when applying this skill.

## 発火条件

- 一時ファイル（coverage JSON、commit_msg、調査用 `debug_*.py` / `check_*.py` 等）を**新規作成**するとき
- リポジトリ直下に一時ファイルが残っているとき（**`coverage.xml` は残置対象。消さない**）
- **コミット・push 完了後**（`commit_msg.txt` 等の削除。**`coverage.xml` は削除しない**）
- **チャット作業の完了・ユーザー報告前**（触ったリポの **`temp/` を空にする**。**`coverage.xml` は残す**。FishTrack **`temp-spec-crawl/` は消さない**）
- **diff-cover** の前に既存 `coverage.xml` を再利用するか判断するとき
- **次回も使うスクリプト**を置くとき（**`temp/` ではなく `scripts/` 等**）
- 手順の正本は **`SKILL.md`**
