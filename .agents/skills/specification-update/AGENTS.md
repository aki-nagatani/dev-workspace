# specification-update

仕様書（Obsidian `DevProject/specifications`）の更新・実装同期は `SKILL.md` に従う。統合作業スケジュール単体の編集は `integrated-schedule-update` SKILL を参照。

**タスク番号の正本**: **`DevProject/plans/統合作業スケジュール.md`** **以外の `DevProject/`** にはタスク番号を書かない（myrules）。仕様は **`[[統合作業スケジュール]]`** 参照のみ。

## タスク ID 混入の原因（要約）

- **計画書**に **Pxx／Fxx** が並んでいる状態で仕様を書くと、**参照を明確にする**ために ID を**仕様へコピー**しがち（仕様の正は**振る舞い**であり、**進捗 ID ではない**）。
- **`integrated-schedule-update`**（計画・ID）と **`specification-update`**（仕様・ID 禁止）の**境界**が、連続編集でぼやける。

## 対策（必須）

- 仕様に「どの作業か」を書くときは **`[[統合作業スケジュール]]` ＋ プロダクト名／節名**に留め、**タスク番号は書かない**（詳細は `SKILL.md`「仕様書本文に書かないもの」「典型パターン」）。
- **`specifications` 配下を編集したら**、報告前に **`dev-workspace/scripts/check_spec_task_ids.py`** に `DevProject/specifications` のパスを渡して実行（**終了コード 1 なら修正してから報告**）。
