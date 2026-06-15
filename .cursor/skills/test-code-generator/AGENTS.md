# test-code-generator

pytest / Jest のテスト生成・カバレッジ 99% 手順は **`SKILL.md`** を正とする。

## Playwright E2E（必須シナリオ ID）

- **`SKILL.md`** の **「### 6. Playwright E2E と必須シナリオ ID」** に従う。\
  **FishTrack**・**MyPokedex**・**おたよりナビ** で **ユーザー向け機能を追加**する場合は、**原則** **`REQUIRED_E2E_SCENARIOS` に ID を追加**する（詳細は **本 SKILL §6**）。
- リポジトリ横断の規約は **dev-workspace** **`.cursor/rules/myrules.mdc`**（**テスト規律**・要点のみ）、各製品 **`AGENTS.md`**（**E2E 必須シナリオ ID** 節）を参照する。
- **テストの行数・分割**: **`SKILL.md` §5.5** と **`file-size-policy`**（tests 理想500行・`*_diff_cover` 禁止・**Task 委譲時は `file-size-policy`「委譲時」**）
