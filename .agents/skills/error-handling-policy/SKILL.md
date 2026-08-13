---
name: error-handling-policy
description: >-
  問題対応全般で「表面上の回避」ではなく根本原因を修正する手順（エラー・バグ・誤判定・UI・レポート等）。
  try/except 握りつぶし・閾値引き下げ・skip・type ignore・表示だけ直す等の禁止、必須フロー・自問チェック。
  「エラーを直して」「テストが落ちる」「回避しないで」「根本から」等の依頼時、または修正方針に迷うときに使用。
  Python 構文・型の詳細は python-code-error-fix SKILL と併用。
---

# エラー対応規律（error-handling-policy）

**myrules**「根本原因からの解決」「エラー対応規律」と同一趣旨。**禁止行為・フロー・自問チェックの正本は本 SKILL**。

## 絶対原則（根本原因）

**🚨 AI は「回避」「表面だけ直す」に走りがちである。これは絶対に禁止する。**

**問題を解決するときは、表面上の対症療法ではなく根本原因を特定して直す。エラーに限らず全作業に適用する。**

回避・抑制・無視・表示やレポートだけ直して原因ロジックを残すことは許されない。

## 発火条件（いずれか）

- スタックトレース・テスト失敗・CI 失敗・Lint エラーの**修正**に着手するとき
- バグ・誤判定・UI 不具合・レポート／突合の誤り・運用ずれなど**問題の修正**に着手するとき
- **`try/except` 追加**・**skip**・**`# type: ignore`**・**閾値変更**を検討するとき
- 症状だけ消す案（文言・CSS・手動フラグ・除外リスト追加のみ等）を検討するとき
- ユーザーが「回避しないで」「根本原因を」「表面ではなく」等と指示したとき

**Python の構文・型・import 不整合**は **`python-code-error-fix`** SKILL を **Read してから**本 SKILL に従う。

## 禁止行為（回避・表面対応の具体例）

以下は**厳禁**（「根本解決」ではない）。

| 禁止 | 正しい対応 |
| --- | --- |
| `except: pass` / `except Exception: pass` | 捕捉範囲を絞り、ログ＋呼び出し元または原因の修正 |
| 広範な `except Exception` で握りつぶし | 想定例外のみ捕捉、再 raise または適切な処理 |
| `@pytest.mark.skip` / `skipif`（一時検証以外） | 失敗原因を直すか、**技術的に実行不可**な理由を残して限定 skip |
| **`--cov-fail-under` を 99 未満に変更** | **テスト追加**のみ（myrules「テスト規律」・各 AGENTS.md） |
| 条件分岐でエラー経路を通らないようにするだけ | なぜエラーが出るかを修正 |
| `# type: ignore` / 安易な `cast` | 型定義・シグネチャ・実装を修正 |
| `logging.error()` のみで終了 | 原因修正まで続ける |
| エラー時に `None` / 空リストで「動いたように見せる」 | 呼び出し元が扱える例外・Result 型、または原因修正 |
| 「環境差」「既知の問題」として記録だけ | 再現・調査・修正 |
| レポート文言・件数表示だけ直して**照合／判定ロジック**を放置 | 誤判定の原因（キー・正規化・条件）を直す |
| UI の見た目だけ隠す／CSS だけで症状を消す（原因が JS・データ・レイアウト計算のとき） | レイアウトずれや誤表示の**発生源**を直す |
| 本番データ／フラグの手動修正だけで、**再発する自動判定・同期**を放置 | 判定・同期コードと必要ならデータ修正を**セット**で直す |
| 除外リストやハードコード特例だけで、一般化できるバグを隠蔽 | ルール・正規化・突合の本体を直す（特例はユーザー明示時のみ最小限） |

## 必須の対応フロー

1. **症状と因果の切り分け**: 何が見えているか／どの入力・条件で起きるか
2. **原因の特定**: スタックトレース・ログ・再現手順・関連コード／データ経路
3. **根本原因の修正**: 回避・迂回・表示だけではない
4. **検証**: 同条件で再発しないこと（テスト・手動確認）。必要なら再発経路も確認
5. **記録**: 必要に応じてコメント・仕様（**新規ドキュメント創作**は `document-creation-policy`）

## 判断に迷った場合

- **回避 vs 解決**: 両案を提示しユーザーに確認
- **根本解決が困難**: ワークアラウンド時は **TODO / Issue で根本対応を明示**。放置禁止
- **テスト skip**: **外部サービス依存・環境差で技術的に不可**の場合のみ。失敗の隠蔽は禁止
- **緊急の手動データ修正**: ユーザー指示があれば可。ただし**同一作業で再発原因の修正方針を明示**し、コード側未着手なら残作業に残す

## 自問チェック（報告・コミット前）

- [ ] 問題の**原因**を変えているか？表面（表示・文言・握りつぶし）だけ隠していないか？
- [ ] 同条件で再実行すると解消するか？
- [ ] 将来の類似ケースでも起きにくい設計か？
- [ ] 手動データ修正だけして、同じバグが次の同期／巡回で戻らないか？
- [ ] 99% カバレッジ運用リポで **`--cov-fail-under` を 99 未満に下げていないか**（該当なしはスキップ）
- [ ] FishTrack / MyPokedex で **`except` 内のログ**は **`log_caught_exception`** か？（`logger.exception`・手書き `exc_info=True` を新規追加していないか）
- [ ] バックグラウンドジョブは **`run_background_job`** ＋ **`app.logger`** か？（該当なしはスキップ）

**1 つでも「いいえ」なら不十分。やり直す。**

## 明示的 except（ログ形式）— FishTrack / MyPokedex

**実装の正本は各リポの `exception_logging.py` と `AGENTS.md`「例外ログ（catch 時）」**。本節は横断ルールと機械検査の要点。

### 導入済み製品

| 製品 | 共通モジュール | 機械検査 |
| --- | --- | --- |
| FishTrack | `src/fishtrack/utils/exception_logging.py` | `scripts/check_caught_exception_logging.py` |
| MyPokedex | `src/mypokedex/utils/exception_logging.py` | 同上 |
| おたよりナビ | **開発凍結中** — 横展開・機械検査の導入は**対象外**（再開時は FishTrack を雛形） | — |

### 記録形式（必須）

- **`log_caught_exception(logger, context, exc)`** → `logger.error("Error in %s: %s", context, exc, exc_info=True)` に統一
- **HTTP ルート**: `current_app.logger`（または `app.logger`）＋ `log_caught_exception`
- **APScheduler 等**: **`run_background_job(app, context, fn, on_error=...)`**。**`app.logger` 必須**（モジュール直下 `logger` だけでは Slack/SNS 通知に届かない）
- **`on_error`**: ドメイン補助のみ（例: spec-crawl 失敗 Slack）。追加の `logger.error` や失敗通知用の入れ子 `try/except` は書かない

### 禁止（握りつぶしと同列）

- 新規の **`logger.exception(...)`**
- allowlist 外での手書き **`exc_info=True`**
- 同一例外に対する **二重 `logger.error`**

### 機械検査（`check_caught_exception_logging.py`）

- **走査対象**: 各リポ `src/<パッケージ>/` 配下の `*.py`
- **検出**: `.exception(` と allowlist 外の `exc_info=True`
- **実行箇所**: **`.githooks/pre-commit`** と **`.github/workflows/deploy.yml`**（lint 段）
- **手動**: リポジトリ直下で `python scripts/check_caught_exception_logging.py`（exit 0 が必須）
- **allowlist**: 正本 `exception_logging.py`・グローバル 500 ハンドラ・WARNING 運用ログ等のみ。**追加はレビュー必須**（安易に広げない）
- **逸脱の一時許可**: 行末 **`# noqa: caught-exception-log`**（最小限・理由が説明できる場合のみ。恒久利用は禁止）

### 新規製品への導入手順（開発再開時）

**おたよりナビは開発凍結中のため、現時点では本手順の対象外。** 凍結解除後に他製品へ展開するときは FishTrack を雛形とする。

1. `exception_logging.py`（`log_caught_exception` / `run_background_job`）を追加
2. 既存の `logger.exception`・手書き `exc_info=True` を一括 `log_caught_exception` へ移行
3. `check_caught_exception_logging.py` を追加（走査ルート・allowlist を製品に合わせる）
4. `tests/test_check_caught_exception_logging.py` を追加
5. **pre-commit** と **deploy.yml** に検査を組み込む
6. 各 **`AGENTS.md`**「例外ログ（catch 時）」節を同期

## 関連

- **Python 構文・型・Lint**: `python-code-error-fix` SKILL
- **テスト追加・カバレッジ**: `test-code-generator` SKILL
- **myrules**: 「根本原因からの解決」（全作業）／「エラー対応規律」（本 SKILL への参照）
