# temp-file-management

Always respond in Japanese when applying this skill.

## 発火条件

- 一時ファイル（coverage JSON、commit_msg 等）を**新規作成**するとき
- **いずれかの SKILL 実行中に処理用 `.py`／CLI を新規したくなるとき**（不足は `scripts/` へ常設。`temp/**/*.py` 禁止。**SKILL へ使用方法も同じ作業で追記**）
- リポジトリ直下に一時ファイルが残っているとき（**`coverage.xml` は残置対象。消さない**）
- **コミット・push 完了後**（`commit_msg.txt` 等の削除。**`coverage.xml` は削除しない**）
- **チャット作業の完了・ユーザー報告前**（触ったリポの **`temp/` を空にする**。**`coverage.xml` は残す**。FishTrack **`temp-spec-crawl/` は消さない**）
- **diff-cover** の前に既存 `coverage.xml` を再利用するか判断するとき
- **次回も使う／不足補完のスクリプト**を置くとき（**`temp/` ではなく `scripts/` 等**。呼び出し元 SKILL の使い方も更新）
- 手順の正本は **`SKILL.md`**（**全 SKILL 共通**の配置・常設化・SKILL 追記・クリーンアップ）
