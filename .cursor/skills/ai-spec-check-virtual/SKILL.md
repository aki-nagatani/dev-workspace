---
name: ai-spec-check-virtual
description: >-
  ローカル Docker（FishTrack `docker compose` の `app`）上で AI 補助スペック取り込みプレビューを
  **DB 非保存**で実行し、その結果を `ai-spec-check-report/SKILL.md` に従って Obsidian の
  `ai_spec_check_report.md` まで仕上げる一気通貫 SKILL。ユーザーがチャットに
  「ai-spec-check-virtual `<URL>`」と書いた場合の入口。**URL を省略したときは** Obsidian 正本
  `ai_spec_check_report.md` フロントマターの **`resolvedUrl`** を **前回と同じ URL** として実行する
  （取得手順は本文「発火条件」）。Manufacturer の新規 INSERT も起きない（`db.session.rollback()` を
  必ず実行）。本番 SSH は使わない。
  ai-spec-check-virtual / virtual preview / ローカル Docker でスペック取り込みを試したい
  / プレビュー仮実行 の依頼時に使用する。
  **`ai-spec-check-report-action` 完了後の効果測定（必須。正本 `resolvedUrl` 継承）**。
  **本番 `ai-spec-check`・コミット・デプロイは行わない**（`ai-spec-check-report-action` SKILL 参照）。
---

# AI スペック取り込みプレビュー検証 SKILL（ローカル Docker・仮実行）

## 概要

- **入口**: 本ファイル（`ai-spec-check-virtual/SKILL.md`）
- **共通手順の正本**: `d:\OneDrive\git_work\dev-workspace\.cursor\skills\ai-spec-check-report\SKILL.md`
- **本 SKILL は `ai-spec-check-local` の派生**。`ai-spec-check-local` がコンテナ既存ログを
  事後に解析するのに対し、**本 SKILL は確定した入力 URL に対して `build_rod_spec_import_preview` を仮実行**
  してから同じ照合フロー（**共通 **`ai-spec-check-report` SKILL** の **§4〜§13**。**Obsidian 正本**の **`## N.` は §11.1・正本運用 §1〜§6**）を回す。**URL はチャット明示または**「発火条件」の **`resolvedUrl` 継承**で確定する。
- **DB へは保存しない**。新規メーカー候補があっても INSERT しない（transient `Manufacturer`）。
  既存マスタは読み取りのみ。終了時 `db.session.rollback()` を必ず実行（スクリプト内）。
- **本番 EC2 / RDS には触れない**。本 SKILL は完全にローカル Docker のみ。

### `ai-spec-check-report-action` からの呼び出し（効果測定・必須）

**`ai-spec-check-report-action` SKILL** で **§4 対策を `FishTrack` `src`／`tests` に反映した同一セッション**では、
ユーザーが **virtual を明示しなくても**、エージェントは **手順 7 として本 SKILL で効果測定を必ず実行する**
（正本 **`resolvedUrl`** 継承）。**実施不能時のみ** action SKILL の「効果測定の例外」に従う。

- **やること**: virtual 実行 → **`ai-spec-check-report` SKILL** で **§2〜§3・§6** 更新（§4 消込は action 側で済んでいる想定）。
- **やらないこと**: **`ai-spec-check`（本番ログ）**、**`git commit`／`push`**、**本番デプロイ**（action SKILL **「効果測定で禁止すること」**と同じ）。

エージェントは本ファイルを Read したうえで **`ai-spec-check-report` を Read** し、ターミナル実行・
本家突き合わせ・Obsidian 正本・markdownlint・作業用 `temp/` 後片付け・**obsidian-cursor-log**
まで一気通貫で行う。手順の提示だけで終わらない。

myrules を厳守して作業してください。

## 発火条件（ユーザー入力の例）

- 「ai-spec-check-virtual `<URL>`」「@ai-spec-check-virtual `<URL>`」
- 「`<URL>` を ai-spec-check-virtual で確認して」
- 「ローカル Docker でこの URL のスペック取り込みプレビューを試して」
- 「URL を渡してプレビューだけ実行し、レポートまで作って」
- 「ai-spec-check-virtual」「`/ai-spec-check-virtual`」（**URL 省略**）

### URL の決め方（エージェント必須）

1. **チャットに http(s) の URL が明示されていれば** それを **`--url`** に使う（正とする）。
2. **URL が無いときは「前回と同じ URL」**として次を **この順で**試し、**最初に得られた有効な URL** で続行する（推測で別ドメインを捏造しない）。
   - **A（正）**: Obsidian レポート正本のフロントマター **`resolvedUrl`**\
     `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`\
     （YAML の `resolvedUrl: "https://…"`。引用符内をそのまま使う）
   - **B（補助）**: FishTrack `temp/tmp_latest_preview.json` が存在し、JSON に **`sourceUrl`** または同等の入力 URL フィールドがあればそれを使う（失敗 JSON にも `sourceUrl` がありうる）。
   - **C（補助）**: 当日または直近の **`obsidian-cursor-log`** エントリで **`ai-spec-check-virtual`**／**入力 URL**として記録された URL。
3. **A〜C のいずれでも有効な URL が得られないときだけ**、作業に入らず **1 回だけ**ユーザーへ URL を確認する。

**ユーザーへの報告**: URL 省略で実行したときは、本文に **「使用 URL は正本 `resolvedUrl`（または B/C）から継承」** と **実際の URL 1 行**を書く（暗黙に進めない）。

**CursorLog**: §5 の記録項目に **入力 URL** を書く際、継承実行なら **`resolvedUrl` 継承**などと分かるように一行添える。

## 0. 前提・環境

- プロジェクトルート: `d:/OneDrive/git_work/FishTrack`
- 仮実行スクリプト（FishTrack 常設）: `scripts/spec_import_virtual_preview.py`
- レポート正本: `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`
- 突合用ノート（`ai-spec-notes`）:\
  `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai-spec-notes/`\
  （**配置**は **`ai-spec-check-report` §5.1**。**DAIWA ロッド**は **`rod-daiwa/`**。**ロッド**の **`## 行別スペック`** には **`modelName` 期待の行別記載を含める**。\
  **個別 URL があるシリーズ**は **§5.1「モデル個別ページ」**で**全モデル確認・ノート漏れなし**を先に済ませる。§5.1 参照）
- 作業用一時ファイル: FishTrack リポ内 `temp/`（完了後に当該作業分を削除。**`ai-spec-check-report` 本 SKILL §10（後片付け）**）
- bind-mount: `docker-compose.yml` の `volumes: - .:/app` により、コンテナ内 `/app/temp/foo.json`
  はホストの `temp/foo.json` と同一ファイル
- プレビュー結果ログの出力条件は `ai-spec-check-local` と同じ
  （`FISHTRACK_STANDALONE` / `FISHTRACK_SPEC_IMPORT_DEBUG_LOG`。`docker-compose.yml` 既定で有効）

## 1. URL とコンテナ起動の確認

エージェントは次を順に実行する。

1. **本章で使う `--url` を確定する**（上記「発火条件」どおり。チャット明示 → **無ければ**
   **`ai_spec_check_report.md` の `resolvedUrl`** → `temp/tmp_latest_preview.json` → CursorLog）
2. **URL の検証**
   - http(s) スキーム、空白なしを確認
   - 不正な場合は作業を止め、ユーザーへ短く再提示（推測補完しない）
3. **`app` 起動確認**

   ```powershell
   cd d:/OneDrive/git_work/FishTrack
   docker compose -f docker-compose.yml ps
   ```

   - `app` が `running` でない場合: `docker compose -f docker-compose.yml up -d app`
   - 起動できないとき（compose 未インストール等）は理由 1 行を報告に添えて作業を中断
4. **直前セッションで `src/` を変更していた場合**は `local-docker-python-restart` SKILL に従い
   `docker compose -f docker-compose.yml restart app` を**先に**試行する（仮実行は WSGI ではないが、
   推定 LLM・ページ取得は同じコード経路。**仮実行と本物プレビューの整合**のため。
   未起動なら 1 行で報告）。

## 2. 仮実行プレビューの起動（DB 非保存）

FishTrack ルートで、コンテナ内のスクリプトを直接呼ぶ。**プレビュー JSON はホストの
`temp/tmp_latest_preview.json` に直接書き出される**（bind-mount）。

```powershell
cd d:/OneDrive/git_work/FishTrack
docker compose -f docker-compose.yml exec -T app `
    python scripts/spec_import_virtual_preview.py `
    --url "<URL>" `
    --out /app/temp/tmp_latest_preview.json
```

- 任意モデル指定: `--model gpt-5.4-mini` 等（既定は `FISHTRACK_SPEC_IMPORT_MODEL`）
- 失敗時もスクリプトは `temp/tmp_latest_preview.json` に
  `"status": "error"` を含む 1 件 JSON を書く（スキーマは下記）
- 同時に fishtrack.log には次のいずれかが必ず出る:
  - 成功: `AI補助スペック取り込みプレビュー結果: { ... }`
  - 失敗: `AI補助スペック取り込みプレビュー失敗: { ... "virtual": true ... }`
- LLM 入出力ログ（`AI補助スペック取り込みLLM入出力:`）も通常実行と同様に出る
  （`FISHTRACK_SPEC_IMPORT_DEBUG_LOG=true` 前提。`docker-compose.yml` 既定で有効）

**🚨 DB 非保存の保証**:

- 本スクリプトは `_resolve_or_create_inferred_manufacturer` を**呼ばない**。代わりに
  `infer_manufacturer`（読み取りのみ）+ 既存検索のみ。新規候補は **transient `Manufacturer`**
  （`db.session.add` しない）として `build_rod_spec_import_preview` に渡す。
- 終了時に `db.session.rollback()` + `db.session.remove()` を必ず実行する。
- そのため、Web UI からの通常プレビューと違い、**新規メーカーが本仮実行で登録されることは無い**
  （既存メーカーへのプレビューも DB 行に変更を残さない）。

## 3. 仮実行 JSON の確認と分岐

`temp/tmp_latest_preview.json` を読み、次のいずれかに分岐する。

- 成功（rod プレビュー JSON。`category == "rod"` か）
  - そのまま **`ai-spec-check-report` SKILL の §4** に従い JSON サマリ確認 → §5 本家取得 → §6A 検証 →\
    §7 分類 → §8 対策 → §9 レポート → **§10 後片付け** → **`obsidian-cursor-log`（同 SKILL §13）**
- 成功だが `category` が `rod` 以外（reel / lure / unknown）
  - `ai-spec-check-report` 既定方針どおり「カテゴリ・`categoryReason` を報告して終了」
    （現行の `build_rod_spec_import_preview` は rod 専用。仮実行で reel が来たときは
    その旨を `ai_spec_check_report.md` の §1 に明記し、対象外で締める）
- 失敗（`status == "error"` を含む JSON、または `--latest` で `--kind failure` 由来の payload 形）
  - `ai-spec-check-report` の **§11.2「プレビュー未到達時」** テンプレに従う
  - `dump_spec_import_preview.py --kind failure --latest --out temp/tmp_latest_failure.json`
    で同じ失敗行を別途取得してもよい（共通 §3.1）

**フロントマター（§9.1）の補足**: 本 SKILL 経由のレポートでは、フロントマターに次の 1 行を
**追加**してもよい（識別用・任意。markdownlint には影響しない）。

```yaml
spec_check_mode: "virtual-local-docker"
```

`source_log_hint` は例として `"ai-spec-check-virtual / docker compose exec --url <URL>"`
等を入れる（共通 §9.1）。

## 4. 共通手順（正本）の参照

次を **Read** し、**§3.1**（必要時）および **§4** から順に実行する。

`d:\OneDrive\git_work\dev-workspace\.cursor\skills\ai-spec-check-report\SKILL.md`

特に次の節は**必ず**遵守する（仮実行でも変わらない）。

- §4 JSON サマリ確認（`manufacturer` / `seriesName` / `usage` / `previewBuildElapsedSeconds` 必須）→ **直後に §4「推定 API コスト」**で算定し **§1 に `estimatedLlmCost*` 4 項目**（**漏れ禁止**）
- §5.1 `ai-spec-notes`（**プレビュー突合用の本家データ**を必ずノート化。判定は書かない）
- §6A ロッド検証 5 観点（全長・ルアー重量・テーパー・パワーの**行別表必須**）
- §7 差異の分類（**本家との不一致はすべて 🔴**。🟡 / 🔵 へ降格しない）
- §8 / §8.1 対策の記述ルール（プロンプト → サーバ → テストの**多層防御**、各案に**期待効果**。**§8.1「対策 N」連番**で §4・§5 を対応付け。**オープン対策あり**で **「対策 N」欠落は禁止**。\
  **§8.1「正本 §4（対策案）のメンテナンス」**および**「報告直前チェックリスト」**に従い、反映完了済みの対策が **§4** に滞留していないか確認する。\
  **滞留**とは、**src** および **tests** への取り込みが済んでいるのに **「対策 N」** を §4 に残すこと。\
  **削除のトリガーは反映完了**（**再プレビュー未取得可**）。\
  **「効果確認まで §4 に残す」は誤り**（**§8.1・正本・myrules**。）
- §9 / §9.0.1 レポート書き出し + markdownlint 通過（lint 無効化禁止）
- **`ai-spec-check-report` 本 SKILL §10（後片付け）**（FishTrack `temp/` 配下の作業用ファイルのみ削除）
- **`ai-spec-check-report` SKILL §11.1／§11.2** に従った **Obsidian 正本 `## 1.`〜`## 6.`**
- **`obsidian-cursor-log` SKILL** による CursorLog（タグ例: `#fishtrack` …）

## 5. CursorLog（必須）

作業完了後、`obsidian-cursor-log` SKILL に従い当日のログ
（`D:/OneDrive/アプリ/remotely-save/Obsidian/CursorLog/YYYY-MM/YYYY-MM-DD.md`）に追記する。

記録項目（仮実行特有）:

- 入力 URL
- `manufacturer` / `seriesName` / category / rowsCount
- `usage` 合算・**推定 API コスト（USD・円・1 行）**・`previewBuildElapsedSeconds`
- 仮実行で利用した `previewRunId`
- 差異サマリ・提案した対策の要点
- レポートの絶対パス（共通 §9.0）
- DB 保存していないこと（本 SKILL の意義）

## 失敗時の出力 JSON（参考スキーマ）

`scripts/spec_import_virtual_preview.py` が `--out` に書く失敗時の JSON は次の形:

```json
{
  "status": "error",
  "stage": "manufacturer_inference | preview_build | unexpected",
  "code": "<SpecImportError.code または manufacturer_inference_failed / unexpected>",
  "message": "<日本語メッセージ>",
  "requestId": "<OpenAI request id があれば>",
  "sourceUrl": "<入力 URL>",
  "model": "<解決済みモデル名>",
  "previewRunId": "<UUID>",
  "elapsedSeconds": 12.345,
  "virtual": true
}
```

`ai-spec-check-virtual` で得た失敗 JSON は、共通 **§11.2** の「プレビュー未到達時」テンプレで
扱う。`requestId` が `req_…` 形式なら fishtrack.log の `LLM入出力:` 行と突き合わせて
`step` / `response` を確認する。

## 禁止事項

- DB への書き込み（本 SKILL は仮実行のため）
- 本番 EC2 / RDS への接続
- スクリプトの `--out` を介さず、PowerShell の `>` で UTF-8 ログを保存すること
  （CP932 解釈で破損しうる。共通 §3.1 / `ai-spec-check-local` の文字コード規律と同義）
- markdownlint 無効化（共通 §9.0.1。`<!-- markdownlint-disable -->` 等の注釈・設定緩和は
  ユーザーの明示承認なしに行わない）
