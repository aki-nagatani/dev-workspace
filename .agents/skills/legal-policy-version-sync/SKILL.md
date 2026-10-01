---
name: legal-policy-version-sync
description: >-
  利用規約・プライバシーポリシーの本文（テンプレ HTML 等）を更新するときは、必ず同意の版キーを同じリリースで更新する。
  版キーは製品によりソース定数（FishTrack）または環境変数（MyPokedex）。
  規約・ポリシー・法的文言の編集、/legal/terms・/legal/privacy・再同意フロー、版キー運用の依頼時に発火する。
---

# 規約・プライバシーポリシー改定と版キーの同期

## 絶対原則（欠落禁止）

**利用規約またはプライバシーポリシーの本文に実質的な変更を入れた場合、その変更を本番・利用者に効かせるリリースでは、必ず「同意の版キー」を前回から変えた値に更新する。本文だけ更新して版キーを据え置かない。**

- 版キーは **semver 不要**。**日付文字列**（例: `2026-04-04`）や **`v1` のような運用ラベル**でよいが、**規約と PP で別キー**にできる（片方だけ改定なら、その側のキーだけ上げる）。
- **テンプレ上の「最終更新日」**と **版キー**は、利用者・保守者が誤解しないよう **同じ改定リリースで整合**させる（日付を倣うなら一致させる）。
    FishTrack の版キーはソース定数。MyPokedex は環境変数。

## いつ発火するか

- `terms.html` / `privacy.html`（または各プロダクトの相当テンプレ）を編集するとき
- 改定手続・同意 UI・再同意の仕様を議論・実装するとき
- 「規約を直した」「PP を直した」とユーザーが言及した直後（**版キーを触ったか必ず確認**）

## MyPokedex（実装済み・正本）

版の比較・DB 保存は `src/mypokedex/utils/legal_policy.py`、既定値と環境変数読みは `src/mypokedex/config.py`。

### MyPokedex 広告の対外文言（再発防止）

有料プランの導入は**未確定**。次は使わない。

- **「無料枠」**（有料と対比する前提になる）
- 規約・PP・フッターでの **有料プラン／広告非表示** の言及（未提供機能を前提に見せる）

正: 見出しは「広告」。表示箇所（図鑑・パーティ＆ボックス）を書く。フッターは「一部画面に広告を表示します」等。LP の「無料で始める」は登録 CTA であり、無料枠表記ではない。FishTrack は有料プラン方針があるため本節の対象外。

### 改定時チェックリスト（本文変更がある場合）

1. **利用規約の本文を変えたら**  
   - 本番・ステージング等: **`MYPDEX_TERMS_VERSION`** を **新しい文字列**に変更（未使用ならキー自体を追加）。  
   - リポジトリ内の開発既定: `config.py` の **`MYPDEX_TERMS_VERSION`** デフォルトを同じ方針で更新（必要なチームなら）。  
   - `legal_policy.py` の **`_DEFAULT_VERSION_KEY`** は、`app.config` が空のフォールバック用。**デフォルト運用と食い違わせない**（通常は `config.py` と同じ改定日付系に揃える）。
2. **プライバシーポリシーの本文を変えたら**  
   - 同様に **`MYPDEX_PRIVACY_VERSION`** と `config.py` のデフォルト、および必要なら `_DEFAULT_VERSION_KEY` の扱いを確認する。\
     規約のみ変更なら **PP 版キーは据え置き**でよい。
3. **Obsidian 仕様**（`DevProject/specifications/MyPokedex/decisions.md`）に計測・同意の決定がある。版キーの写しは仕様へ残さない。
4. **テスト**: 版キー不一致で再同意に進む経路を触ったら、`tests/blueprints/auth/test_legal_acceptance.py` 等の期待値を更新する。

### 環境変数の参照先（デプロイ時）

- **EC2 / Docker Compose**: 各環境の `.env` またはデプロイジョブで `MYPDEX_TERMS_VERSION` / `MYPDEX_PRIVACY_VERSION` を注入する運用なら、**その箇所を必ず同じ PR・同じリリース**に含める（本文だけマージしない）。

## FishTrack（実装済み）

版キーの正はソース定数 `LEGAL_POLICY_TERMS_VERSION` と `LEGAL_POLICY_PRIVACY_VERSION`（`src/fishtrack/utils/legal_policy.py`）。
`apply_fishtrack_config` が Flask 設定 `FISHTRACK_TERMS_VERSION` / `FISHTRACK_PRIVACY_VERSION` に載せる。
**.env および環境変数には置かない・読まない**（古い `.env` が残ると再同意が走らない）。

改定時:

1. **本文を変えた側の定数だけ**を同じリリースで更新する。規約本文を変えていなければ `LEGAL_POLICY_TERMS_VERSION` は据え置く。
2. **Obsidian 仕様**に版キーの写しは残さない。決定が変わるときだけ `decisions.md` を同じリリースで更新する。
3. **テスト**: 再同意経路を触ったら期待値を更新する。
4. **ホームお知らせには載せない**（`site-update-announce`）。
   全ユーザーがログイン後の再同意画面で目にする。

## おたよりナビ（これから実装）

実装時は FishTrack と同様にソース定数を正とし、`.env` に置かない。
再同意・公開ページの振る舞いは MyPokedex と同趣旨。計画は統合作業スケジュール。

## レビュー時の自問

- [ ] 本文（HTML）に差分があるか？ → あるなら **版キーに差分があるか**
- [ ] 片方ドキュメントだけ変えたか？ → **変えた側の版キーだけ**上げたか（もう片方を誤って上げていないか）
- [ ] `legal_policy` のフォールバック（MyPokedex `_DEFAULT_VERSION_KEY` / FishTrack `LEGAL_POLICY_DEFAULT_VERSION`）と本文の最終更新が矛盾していないか
- [ ] FishTrack で版キーを `.env` に足していないか
- [ ] 版キー更新だけをホームお知らせに載せる提案をしていないか（再同意画面で足りる）

## 参照（コード）

- MyPokedex: `MyPokedex/src/mypokedex/utils/legal_policy.py`
- MyPokedex: `MyPokedex/src/mypokedex/config.py`（`MYPDEX_TERMS_VERSION` / `MYPDEX_PRIVACY_VERSION`）
- FishTrack: `FishTrack/src/fishtrack/utils/legal_policy.py`（`LEGAL_POLICY_TERMS_VERSION` / `LEGAL_POLICY_PRIVACY_VERSION`）
- FishTrack: `FishTrack/src/fishtrack/config.py`（環境変数は読まない）
- 仕様・計画: Obsidian `DevProject/specifications/`、**`スケジュール.md`**
