# specification-update

仕様書（Obsidian `DevProject/specifications`）は、コード・テスト・`AGENTS.md` に残らない決定の正本。スキーマ・API・スタック・閾値の写しは更新しない。
決定が変わったときだけ同じ作業で直す。既存の厚い本文は一括削除しない。手順は `SKILL.md`。統合作業スケジュール単体の編集は `integrated-schedule-update` SKILL を参照。

**タスク番号の正本**: **`DevProject/plans/スケジュール.md`** **以外の `DevProject/`** にはタスク番号を書かない（myrules）。仕様は **`[[スケジュール]]`** 参照のみ（旧名 `[[統合作業スケジュール]]` は別名）。

## タスク ID 混入の原因（要約）

- **計画書**に **Pxx／Fxx** が並んでいる状態で仕様を書くと、**参照を明確にする**ために ID を**仕様へコピー**しがち（仕様の正は**振る舞い**であり、**進捗 ID ではない**）。
- **`integrated-schedule-update`**（計画・ID）と **`specification-update`**（仕様・ID 禁止）の**境界**が、連続編集でぼやける。

## 対策（必須）

- 仕様に「どの作業か」を書くときは **`[[スケジュール]]` ＋ プロダクト名／節名**に留め、**タスク番号は書かない**（詳細は `SKILL.md`「仕様書本文に書かないもの」「典型パターン」）。旧名 `[[統合作業スケジュール]]` は別名で開く。
- **`specifications` 配下を編集したら**、報告前に **`dev-workspace/scripts/check_spec_task_ids.py`** に `DevProject/specifications` のパスを渡して実行（**終了コード 1 なら修正してから報告**）。
