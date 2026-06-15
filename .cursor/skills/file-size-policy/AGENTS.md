# file-size-policy

Always respond in Japanese when applying this skill.

## 発火条件

- 大きなソース・テスト・CSS/JS ファイルの追加・分割検討時
- `check_file_size.py` / pre-commit 失敗時
- **コミット時の行数上限超過**でファイル分割が必要なとき（**少量移動でギリギリ回避しない** — 機能単位・**各分割先は理想500行以内**を原則。**`*_diff_cover` 等の計測名ファイル禁止** — `SKILL.md`「テストファイル分割」）
- **Task サブエージェントに分割を渡す／受け取る**とき（`SKILL.md`「委譲時」— **tests/*.py の分割本体は親が実施**が原則）
- 手順の正本は **`SKILL.md`**
