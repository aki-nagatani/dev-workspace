---
name: ai-spec-check
description: >-
  本番 FishTrack のログから「AI補助スペック取り込みプレビュー結果」、
  「AI補助スペック取り込みLLM入出力」（API 呼び出しごとの入出力）、および
  プレビュー未到達時の「プレビュー失敗」1行JSON（必要時 `llmExchanges`）を取得し、
  本家ページと突き合わせてロッド／リールの取り込み品質を検証する（失敗時は原因整理中心）。差異は 🔴🟡🔵 に分類し、
  対策を即時／中期／長期で具体化し**各対策に期待効果**を併記して Obsidian 正本 `ai_spec_check_report.md` に書き、
  CursorLog を更新する。専用 Cursor Command はなく本 SKILL が正本。AI スペック取り込みプレビュー検証、
  spec import プレビュー照合、dump_spec_import_preview、本番 fishtrack.log プレビュー行の依頼時に使用する。
---

# AI スペック取り込みプレビュー検証 SKILL

## 概要

**手順・セクション番号の正本は本 SKILL のみ**（旧 `.cursor/commands/AI_spec_check.md` は廃止し、当時の**入口用メモ**を本節に統合した）。

**エージェントは** `dev-workspace/.cursor/skills/ai-spec-check/SKILL.md`（本ファイル）を **Read** し、ターミナル実行・本家突き合わせ・Obsidian 正本・markdownlint・作業用 `temp/` の後片付け・**obsidian-cursor-log** まで行う。手順の提示だけで終わらない。

**人間向けパス（再掲）**:

- FishTrack ルート: `d:/OneDrive/git_work/FishTrack`
- レポート正本: `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`
- 作業用出力先: FishTrack リポ内 `temp/`（完了後に当該作業分を削除。セクション 10）

myrules を厳守して作業してください。

**本番** FishTrack（EC2 上の Docker / `app` サービス）のログから、最新の
「AI補助スペック取り込みプレビュー結果」を取得し、ログ中の `resolvedUrl` に
アクセスして本家ページと突き合わせ、取り込み漏れ・想定外・誤変換がないかを
判定してください。問題があれば、根本原因と対策（即時／中期／長期）を具体的に
まとめ、**各対策の期待効果**を併記してください。エージェントがターミナルで実行すること。手順の提示だけで
終わらないでください。

**報告の出し分け**: 表・分類・対策の**全文**は **セクション 9** の
**Obsidian 上の** `ai_spec_check_report.md`（**固定絶対パス**、下記 9.0）にのみ書く。**チャット**には **セクション 9.4**
の要約（パス・数行サマリ）で足りる。同一本文をチャットに再掲載しない。

**注意**: 旧来どおり FishTrack リポジトリルートにレポートを置かない。git 管理対象外の作業用ドキュメントは **Obsidian** に集約する。

**読み取り専用タスク**: 本番・ローカル **DB への接続・書き込みは行わない**。
本番 **EC2 へはログの読み取り**（SSM / SSH、コンテナ内ファイルまたは stdout）
のみとする。プレビュー結果（DB 未保存）を見る段階で、問題があれば確定前に
止めるための作業です。

## 使用タイミング

- ユーザーが AI 補助スペック取り込みのプレビュー品質を本番ログで確認したいとき
- `ai-spec-check`（本 SKILL）の実行依頼、「AI スペック取り込みプレビュー検証」、「プレビュー結果を本家と照合」等の指示があったとき

## 0. 前提・環境

- プロジェクトルート: `d:/OneDrive/git_work/FishTrack`（**常設スクリプト**の実行元）
- **作業用ファイル**（`tmp_latest_preview.json`・`tmp_prod_preview_grep.log` 等）は
  リポジトリ直下に置かず、**`temp/`** 配下に集約する（例: `temp/tmp_latest_preview.json`）。
  `dump_spec_import_preview.py --out` は親ディレクトリを自動作成する。
  **本作業の作業完了後**（Obsidian レポート・セクション 13 CursorLog まで済んだ時点）に、当該実行で用いた **`temp/` 配下の作業用ファイルはすべて削除**する（**セクション 10**）。
- 本番確認手順の詳細: dev-workspace `.cursor/skills/ec2-rds-connection/SKILL.md`、
  および（人間用）Obsidian `DevProject/guidelines/EC2_SSH接続手順.md`
- 本番 EC2 の**現行**インスタンス ID・ホスト: GitHub Secrets / AWS コンソールで
  確認（`ec2-rds-connection` の IP / ID は**例示**。実行前に**必ず**要確認。デプロイ
  ディレクトリ例: `/home/ec2-user/FishTrack`。コンテナ内ログは
  `docker compose -f docker-compose.yml exec -T app ...` 前提）
- Docker: 本番は `docker-compose.yml` 単体で起動。サービス名は `app`。
  コンテナ名は `docker ps` で確認（例: `*-app-1`）
- プレビュー用ログの**取得元**（どちらか、または併用）:
  1. **推奨**: コンテナ内 `FISHTRACK_LOG_DIR` 配下（既定 `/app/instance/logs`）
     の `fishtrack.log` および `fishtrack.log.YYYY-MM-DD`（`FISHTRACK_LOG_TO_FILE` が有効でファイルが出ている場合）
  2. **代替**: ファイルに出ていない本番は stdout のみのことがある。当該期間の
     `docker logs <コンテナ> --since ...` または CloudWatch Logs から、
     識別文字列 `AI補助スペック取り込みプレビュー結果:` を含む行を取得し、
     同じ手順で UTF-8 テキストとして `dump` に渡す
- プレビュー結果の出力条件（アプリ設定・両方満たすこと）:
  - `FISHTRACK_STANDALONE=true`（`docker-compose.yml` 本番想定で既定 on）
  - `FISHTRACK_SPEC_IMPORT_DEBUG_LOG=true`（本番では `.env` 要確認）
- プレビュー**成功**の識別文字列: `AI補助スペック取り込みプレビュー結果:`
- **プレビュー未到達・ジョブ失敗**（`store.set_error` 等でプレビュー JSON が出ない経路）の識別文字列: `AI補助スペック取り込みプレビュー失敗:`
  - 出力元: `src/fishtrack/blueprints/tackle/routes_master.py` の `_log_spec_import_preview_job_failure`（WARNING・1 行 JSON）
  - **本番に当該コードがデプロイされた後**の失敗のみファイルログに残る。過去の失敗で UI に出た OpenAI `requestId` だけでは、デプロイ前ログに**行が無い**ことがある
  - 失敗 payload のキー: `jobId`, `code`, `message`, `requestId`, `sourceUrl`, `model`
  - **dump**: `python scripts/dump_spec_import_preview.py --kind failure` と `--count` / `--list` / `--latest` / `--index` / `--out` を組み合わせる（成功時と同じく `--stdin` / `--file` / docker 経路）
  - UI の **OpenAI request id**（`req_…`）はログでは主に **`requestId`** で突き合わせる（`grep req_5826…` 等）。補助: `spec-import preview job failed` / `no_preview_rows` 等
- プレビュー（成功時）payload のキー:
  `manufacturer, resolvedUrl, pageTitle, requestId, category, categoryReason,
   rowsCount, usage, rows[]` に加え、**デバッグプレビューログ有効時**（`FISHTRACK_SPEC_IMPORT_DEBUG_LOG` 等）は
  **`llmPrompts`**（配列）が含まれることがある。各要素は `step`（例: `classify` / `rod_extract_1_of_3` /
  `verify` / `refine_<modelName>_1`）・`systemPrompt`・`userPrompt` で、**当該実行で API に送った
  system / user 本文**を再現する。
- **`AI補助スペック取り込みLLM入出力:`**（**同一のデバッグ条件**で、**OpenAI を 1 回呼ぶごとに 1 行**。成功は INFO、HTTP/JSON 失敗は WARNING）
  - 行末 JSON に **`step`**・**`model`**・**`requestId`**・**`systemPrompt` / `userPrompt`** に加え、
    成功時はパース済み **`response`**、失敗時は **`httpStatus`** / **`openaiErrorExcerpt`** / **`responseRaw`** 等（実装: `src/fishtrack/services/spec_import/tackle_spec_import_openai_client.py`）。
  - **照合・原因分析の必須参照**: **`llmPrompts`（入力のみ）だけに頼らず、可能な限り本マーカー行を読む**
    （**プロンプトと実際の LLM 出力の対応**・どの段（classify / extract / verify / refine / manufacturer_infer）で本家とズレたかを切り分ける）。同一実行の行は**ログ行先頭の日時**、**`requestId`**、**`step`** で
    `プレビュー結果:` / `プレビュー失敗:` 行と突き合わせる。
  - **プレビュー失敗** 1 行 JSON に **`llmExchanges`** 配列が付くことがある（ジョブ内の往復のコピー、上記と同型）。
    **失敗行だけで足りない**・ログが切り詰められている場合は、本番ログを **`grep LLM入出力:`**
    （または `AI補助スペック取り込みLLM入出力` の一部）で抜粋し **`temp/` に UTF-8 保存**して目視する（セクション 2）。
- 各 row のキー: **マージ済みプレビュー行の全フィールド**に加え、
  `row`（1 始まり行番号）・`missingRequired[]`・`missingOptional[]` が付く。
  ロッド例: `seriesName`, `modelName`, `genre`, `lengthFt`, `lengthIn`, `power`,
  `action`, `listPrice`, `weightG`, `lureWeightMinOz`, `lureWeightMaxOz`,
  `lineMinLb`, `lineMaxLb`, `pieces`, `blankMaterial`, `carbonRatePct`,
  `releaseYear`, `janCode`, `features`, `technologyLabels`,
  `matchedTechnologyLabels`, `newTechnologyLabels`, `matchedTechnologyIds` など。
  - 注意: リールプレビューで `lengthFt` / `lureWeightMinOz` 等が null のことはあり得る。
    本検証ではリールの主属性以外は**無視**してよい（埋まっていてもロッド観点では対象外）
- 対象カテゴリ:
  - `category = "rod"` → ロッド検証（主属性: power, action, length,
    lureWeight, line, pieces, carbon_rate, blank_material, release_year）
  - `category = "reel"` → リール検証（主属性: reel_type（spinning/bait）,
    gear_ratio, weight_g, list_price, jan_code）
  - `category` がそれ以外（lure, unknown 等）はスコープ外。対象外として報告。
- 関連ソース（必要時のみ参照・不要なら触らない）:
  - `src/fishtrack/services/spec_import/tackle_spec_import.py`（system_prompt / preview logger）
  - ロッド: `src/fishtrack/models/rod_model.py` / `rod_series.py`
  - リール: `src/fishtrack/models/reel_model.py` / `reel_series.py` /
    `reel_model_technology.py`
  - 共通: `src/fishtrack/models/tackle_technology_feature.py`
    （`category` 列で `rod` / `reel` が別管理されている点に注意）

## 🚨 文字コードの絶対ルール

PowerShell の標準リダイレクト（`> file.txt`）は日本語環境で UTF-8 を CP932
として解釈するため、ログを取得した瞬間にファイル破損させる（過去事故あり）。

- ログの解析は**常設スクリプト** `scripts/dump_spec_import_preview.py` を使う
  - **ローカル Docker**: スクリプト内部で `docker exec` の出力を bytes 取得
  - **本番（Windows エージェント）**: **優先**は `ssh` の stdout を **Python で
    `write_bytes`** し `--file`（セクション「Windows エージェント」）。**非推奨**:
    PowerShell 上の **`ssh | python --stdin` のみ**（0 件**偽陰性**の実績あり）
  - **本番（Linux シェル等）** または **上記 `write_bytes` 後**: `python ... --stdin`
    あるいは `--file`。**PowerShell の `>` だけで丸ごと保存**は禁止
- `docker exec ... > file` / `Get-Content -Raw` + 紛らわしいエンコード、等の
  「意図しない再エンコード」は禁止
- 詳細は `markdown-editing` / `obsidian-cursor-log` SKILL 参照

### Windows エージェント（PowerShell）での本番抜粋（再発防止・重要）

**予定通りに進まなかった主因**（本 SKILL 作業の実績）:

1. **`ssh ... | python scripts/dump_spec_import_preview.py --stdin` のみ**に頼ると、
   **0 件**（`プレビュー結果が見つかりませんでした`）になることがある。本番
   コンテナ内には **`grep` で行がある**のに、**パイプ経路で UTF-8 が壊れる・
   解釈差**で `dump` がマーカーに一致しない**偽陰性**。
2. **`python -c "...."` 内**に `2>/dev/null` 等を書くと、PowerShell が **`2>`** を
   **リダイレクト**と解釈し、**スクリプト全体が壊れる**（例: ドライブ不検出のエラー）。
   **リモート**に届かない。

**エージェントは次を既定とする（本番・Windows）**:

- **第1**: FishTrack ルートで **Python** の `subprocess.run` に **`ssh` を
  引数リスト**で渡し、`stdout=subprocess.PIPE` の **生バイト**を
  `pathlib.Path('temp/tmp_prod_preview_grep.log').write_bytes(...)` する。
  その後 `python scripts/dump_spec_import_preview.py --file temp/tmp_prod_preview_grep.log --list`。
- **リモート `grep` の文字列**は `dump` の正本と揃え、
  **`AI補助スペック取り込みプレビュー結果:`** を含む行に限定。失敗行は
  **`AI補助スペック取り込みプレビュー失敗:`** 同様。短い `プレビュー結果:`**のみ**は
  他行と**誤合致**しうる。
- **リモートで `2>/dev/null` は付けない**（`python -c` にシェルリダイレクトを含めない
  ため。stderr への grep 注意書きは無視し、常設 `dump` の入力を正しく保つ）。
- 上記を **1 回限りの `temp/_fetch_*.py`（数十行）**にまとめてもよい。
  myrules「一括置換用スクリプト」とは別。作業完了後 **セクション 10** で**必ず削除**。

**`ssh | python --stdin`**: **検証用・小ログ専用**。本番の多行 grep 抜粋では
**使わない**。0 件なら**疑わず**上記 `write_bytes` + `--file` へ切替。

### PowerShell で SSH する場合（引用符・メタ文字）

**二重引用符 `"..."` だけで `ssh` の最外層を囲むと**、文字列**内**の
`2>/dev/null` 等が **Windows 側**で解釈され、リモートに届かない:

- `2>/dev/null` や `2>&1`（**`2>`** も**リダイレクト**）
- `$(command)`（**PowerShell のコマンド置換**）。EC2 上の `ls` ではない

**併用ルール**:

- リモート 1 本を **`ssh` の最外層を単一引用符 `'...'`**（PowerShell 7）で
  囲むか、**Python `subprocess` + 引数リスト**でシェル解釈を避ける
- **Python** から `write_bytes` + `--file` する方が、日本語の**一致率**と**安定性**が高い

## 1. 本番でログ断片を取得

- SSM `send-command` または `ssh` で EC2 に入り、デプロイディレクトリ
  を特定したうえで次を行う（例。パスは環境に合わせる）:
  - `docker compose -f docker-compose.yml ps` で `app` が Up か確認
  - ファイルログを読む: `docker compose -f docker-compose.yml exec -T app sh -c 'cat /app/instance/logs/fishtrack.log'`
  - ローテ済みも含める場合: EC2 上で `sh -c` 内で
    `fishtrack.log.*` を**日付順（`ls ... | sort` 等）**に連結し、
    最後に**現在**の `fishtrack.log` を付けて 1 ストリームを stdout へ
    （連結は EC2 側のシェルで組み、日本語壊しを避ける。順序を誤ると
    `dump` の「末尾＝最新」解釈と食い違うが、**既定の `--order time`**
    でログ行の日時に基づき補正される）

**ローカル（開発 PC）**で **Linux 以外のシェル（PowerShell）**を挟む場合、
`ssh` の stdout → `python` の **パイプは UTF-8 を保証しない**。次節の
`--stdin` は、**WSL / Git Bash 等**、または**先に `write_bytes` したファイル**
の **`--file`** を正とする。

## 2. プレビュー結果ログの件数・一覧確認（常設スクリプト）

本作業では FishTrack 側の常設スクリプト
`scripts/dump_spec_import_preview.py` を使う。base64 ダンプ + ワンライナー
Python を廃し、日本語も UTF-8 のまま安全に扱える。

**本番（SSH）の例**（キー・ホスト・デプロイパスは差し替え）:

- **A. 抜粋＋`--file`（推奨・Windows エージェントでは必須に近い）**:
  本番上で `grep` 等で
  `AI補助スペック取り込みプレビュー結果:` 行**だけ**出し、**ローカルは必ず
  `write_bytes` 等**で **`temp/tmp_prod_preview_grep.log`** へ保存 →
  `python scripts/dump_spec_import_preview.py --file <path> --list`
  （`temp/` 配下。セクション「Windows エージェント」参照）。**失敗行**は別抜粋
  `temp/tmp_prod_fail_grep.log` / **`AI補助スペック取り込みプレビュー失敗:`** →
  `--kind failure`。**0 バイト**かつ本番に失敗が無い期間なら**正常**（`--kind failure` が
  0 件で**作業失敗としない**）。
- **B. パイプ**（`ssh | python --stdin`）: **WSL / Linux / 小規模検証**向け。Windows
  PowerShell の**単独手順**としては**非推奨**（0 件偽陰性の実績。セクション「Windows
  エージェント」）。巨大ログの**丸ごと `cat`**は遅延の要因。まず A。

```powershell
# 【B】検証用: WSL やパイプが信頼できる環境向け。Windows PowerShell 単体の本番作業では
# セクション「Windows エージェント」の write_bytes + --file を使う。
cd d:/OneDrive/git_work/FishTrack
ssh -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@<本番IP> 'cd <deploy-dir> && docker compose -f docker-compose.yml exec -T app sh -c "grep -h プレビュー結果: /app/instance/logs/fishtrack.log*"' | python scripts/dump_spec_import_preview.py --stdin --list --limit 5
```

```powershell
# プレビュー失敗行。リモート sh -c 内の 2>/dev/null は、PowerShell+python -c では避ける
#（メタ文字事故）。B と同じく、本番の既定は A（--file）。
ssh -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@<本番IP> 'cd <deploy-dir> && docker compose -f docker-compose.yml exec -T app sh -c "grep -h プレビュー失敗: /app/instance/logs/fishtrack.log*"' | python scripts/dump_spec_import_preview.py --stdin --kind failure --list --limit 10
```

```powershell
# LLM 往復ログ。多い場合は A と同様に抜粋を temp に write_bytes してから目視
ssh -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@<本番IP> 'cd <deploy-dir> && docker compose -f docker-compose.yml exec -T app sh -c "grep -h LLM入出力: /app/instance/logs/fishtrack.log* | tail -n 80"'
```

- 抜粋を **`temp/tmp_prod_llm_io_grep.log`** 等へ **Python / バイナリ書き込みで UTF-8 保存**し、エディタや `jq` で **`step` / `requestId` / `response`** を追う（常設 `dump` はプレビュー成功/失敗マーカー専用のため、LLM 入出力は **grep 目視または別スクリプト**でよい）。
- `--stdin` … 前段の**標準出力**をそのままログ本文として解析
- 0 件のとき、**PowerShell 上の** `ssh | python --stdin` で**マーカーに一致しない**
  （UTF-8 破壊・偽陰性）の可能性が高い → **A の `write_bytes` + `--file` へ必ず切替**
  （セクション「Windows エージェント」）
- 件数だけ: `... | python ... --stdin --count`

**補足（ローカル Docker での検証に切り替える場合）**: 同一リポをローカル
で起動しているときは `--stdin` なしで従来どおり `docker` 経路で可。

```powershell
cd d:/OneDrive/git_work/FishTrack
python scripts/dump_spec_import_preview.py --count
python scripts/dump_spec_import_preview.py --list --limit 5
python scripts/dump_spec_import_preview.py --kind failure --count
python scripts/dump_spec_import_preview.py --kind failure --list --limit 10
```

- `--kind` … `success`（既定）＝`プレビュー結果:` 行のみ。`failure` ＝`プレビュー失敗:` 行のみ
- `--count` … ヒット件数のみ表示
- `--list --limit N` … 成功時は `[index] timestamp  category=...  rows=...  url=...`。
  **失敗時**は `code` / `jobId` / `requestId` / `url`（`sourceUrl`）/ `message` 先頭。
  **「新しい」順**は既定で `--order time`（各ログ行先頭の
  `[YYYY-MM-DD HH:MM:SS]` を**記録日時**として比較し、**新しい順＝降順**）。
  `grep` のファイル順混在に依存しない
- `--order file` … 従来どおり、入力テキスト上の**出現の逆順**（特殊用途）
- 0 件だった場合の切り分け:
  - **`--kind success` で 0 件・UI は失敗表示** → `--kind failure` と
    `プレビュー失敗:` の grep を試す（未デプロイならログに無い）
  - 環境変数 2 つ（`FISHTRACK_STANDALONE`, `FISHTRACK_SPEC_IMPORT_DEBUG_LOG`）
    が本番 `.env` で有効か（**成功プレビュー行**の出力条件。**失敗行**は別経路で WARNING 出力）
  - ファイルに出ておらず **stdout** のみの可能性 → セクション 0 の (2) を参照
  - ローテーション後で別ファイルに移っている（ローカル `docker` 経路）
    → `--include-rotated` を付けて再実行、または本番 EC2 側で連結してから `--stdin`
  - まだ 1 度も本番でプレビューを実行していない → ユーザーの合意のもと
    本番 UI で再現依頼

## 3. 最新 1 件を JSON として取得

- **既定**の「最新」は **ログ行の日時**（`--order time`）が最大の 1 件。複数
  プレビューがあるとき、**`--list` で日付を目視**し、特定したい 1 件を
  `--index` で指す、という運用も可（index 0 ＝**記録日時**が**最新**の1件）。

本番（セクション 2 の `ssh` / `--file` のいずれかの後）:

```powershell
python scripts/dump_spec_import_preview.py --stdin --latest --out temp/tmp_latest_preview.json
# 抜粋をファイルに置いた場合
python scripts/dump_spec_import_preview.py --file temp/tmp_prod_preview_grep.log --latest --out temp/tmp_latest_preview.json
# 最新のプレビュー失敗 1 件（JSON に code / message / requestId / sourceUrl 等）
python scripts/dump_spec_import_preview.py --stdin --kind failure --latest --out temp/tmp_latest_failure.json
```

ローカル Docker のみ（`--stdin` / `--file` なし）の場合:

```powershell
python scripts/dump_spec_import_preview.py --latest --out temp/tmp_latest_preview.json
python scripts/dump_spec_import_preview.py --kind failure --latest --out temp/tmp_latest_failure.json
```

- 新しい順 **2 件目** など: `--index 1`（順序は `--order` 準拠）
- ローカル `docker` 経路でローテ済みログも対象にする: `--include-rotated`
- 出力 `temp/tmp_latest_preview.json` は UTF-8（BOM なし）。`--out` は
  スクリプト内で UTF-8 書き込み（PowerShell の `>` では書かない）

## 4. JSON サマリ確認

**成功プレビュー**（`temp/tmp_latest_preview.json`）:

```powershell
python -c "import json,sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8'); p=json.load(open('temp/tmp_latest_preview.json',encoding='utf-8')); print('category:', p.get('category')); print('resolvedUrl:', p.get('resolvedUrl')); print('rowsCount:', p.get('rowsCount'))"
```

**カテゴリ分岐**: `category` の値で検証内容を分岐する。

- `rod` → セクション 6A（ロッド検証）
- `reel` → セクション 6B（リール検証）
- `lure` / `unknown` → スコープ外。カテゴリと `categoryReason` を報告して終了

**プレビュー失敗**（`--kind failure` で得た JSON）:

- `resolvedUrl` / `rows[]` は無い。`sourceUrl`・`code`・`message`・`requestId` を確認する
- 付随する **`llmExchanges`** があれば **各要素の `step` / `response` / エラー項目**を読み、
  失敗直前までどの抽出段が通ったかを整理する。無い場合はセクション **2** の **`grep LLM入出力:`** で補う。
- **セクション 5〜6** の本家表との突き合わせは、プレビュー行が無いため**原則スキップ**
  （任意で `sourceUrl` を取得し、URL 妥当性・ページ構造の参考コメントに限る）
- **セクション 9・11** のレポートは「失敗系」テンプレに従う（下記）

**成功プレビュー**で **`llmPrompts` がある場合**も、**セクション 0** の **`AI補助スペック取り込みLLM入出力:`** 行を **同一実行・同一 URL 相当の時刻帯**で探し、**`response` と本家の突き合わせ**に使う（入力だけでは足りない差分の説明に必要）。

## 5. resolvedUrl の本家ページ取得

- `WebFetch` ツールで `resolvedUrl` を取得
- ロッドの場合は以下 3 箇所を抽出:
  1. 製品スペック表（表形式：アイテム／コードネーム／各数値列）
  2. 技術紹介セクション（ダイワテクノロジー等、ページ全体で共通）
  3. 各アイテム説明内の `TECHNOLOGY：...` 行（アイテムごとに個別）
- リールの場合は以下を抽出:
  1. 製品スペック表（アイテム／ギア比／自重／標準糸巻量／最大ドラグ力
     ／ハンドル長／ベアリング数 等）
  2. 機種タイプ（スピニング / ベイト の判別情報。商品名や
     カテゴリパンくずから決定）
  3. 技術紹介セクション（HYPERDRIVE DESIGN 等）
  4. 各アイテム説明内の `TECHNOLOGY：...` 行（個別）

## 6A. ロッド検証（5 観点）

`category = "rod"` の場合に適用。差異があれば観点ごとに一覧化する。

- **A. 件数**
  - `rowsCount` が本家製品スペック表の行数と一致するか
  - 過不足があれば該当 row と model を列挙
- **B. 数値の原文一致**
  - `lureWeightMinOz` / `lureWeightMaxOz`, `lengthFt` / `lengthIn` が本家の数値表記と一致するか
  - **帯分数と小数は同値なら一致**: 例として本家が `1 1/2oz` / `1-1/2 oz` /
    `1+1/2oz` 等、AI が `1.5oz` に**小数化**している場合は、数値として等しければ
    **差分ではなく一致**と判定する（逆も同様。単位 `oz` の有無・スペースの差は
    表記揺れとして許容し、**数値の等価性**で見る）
  - `約` / `〜` / `前後` / `程度` / `MAX` 等の**近似語混入**がないか
  - `1/7` のような分数が勝手に `約9/64` 等へ**別の分数へ近似変換**されていないか
    （上記の**同値な帯分数→小数**とは別問題）
- **C. 技術特性**
  - `technologyLabels` が**当該アイテムの TECHNOLOGY 行**と一致するか
  - ページ冒頭の技術紹介セクションを別アイテムに**誤付与**していないか
  - **不足**: 本家（技術紹介・※脚注・当該行 `TECHNOLOGY：` 等）に照らし**付くべき**ラベルが
    `technologyLabels` に無い・著しく欠ける場合は **🔴**（セクション 7）。「空でよい行」と判断できる根拠が本家に無いのに空なら同様。
  - **DAIWA（ロッド）・`TECHNOLOGY：` 行先頭のブランク素材（観点 C の例外）**:
    行内に併記されていても **`SVF NANOPLUS` / `SVF COMPILE-Xナノプラス`（等のブランク素材トークン）は
    技術特性には含めない**のが**実装・仕様の正**（素材は `blankMaterial` 等。`tackle_spec_import_technology` の
    除外方針と同趣旨）。**これらが `technologyLabels` に無いこと単体**をもって、本家スラッシュ列と
    の**集合不一致 🔴**とは**扱わない**。`previewHtmlTechnologyLabels` に先頭を含めて出ているが
    `technologyLabels` に無い**差**は、**表示用**と保存候補の役割違いとして **🟡 注記**または **🔵** に留める。
  - `matchedTechnologyLabels` / `newTechnologyLabels` の振り分けが妥当か
  - マスタ突き合わせは `tackle_technology_feature.category = 'rod'` のみ対象
- **D. シリーズ・型番**
  - `seriesName` が本家見出しどおりか（新旧世代混在がないか）
  - `modelName` が本家表記そのままか
    （中黒 `・`、`【コードネーム】` の扱いが一貫しているか）
- **E. その他スペック項目（payload の `rows[]` にも載る）**
  - `releaseYear`, `carbonRatePct`, `janCode`, `listPrice`
  - `lineMinLb`, `lineMaxLb`, `pieces`, `weightG`
  - `power`, `action`, `blankMaterial`
  - **`pieces`（継数とジョイント）**:
    本家製品スペック表で**継数が 2**かつ**ジョイント仕様がグリップジョイント**
    （又はメーカーが同等と分かる表記）のとき、プレビューが**ジョイント種別のみ**
    （例: `グリップジョイント`）であっても**本家と矛盾しない**。**差分（🔴）に含めない**
    （🔵 参考に留めてよい）。
    継数・ジョイントの**いずれかが本家と食い違う**場合は従来どおり 🔴。

**注**: リールプレビューでロッド用キー（全長・ルアー重量など）が null の場合は本観点では評価しない。

## 6B. リール検証（5 観点）

`category = "reel"` の場合に適用。ロッドとは主属性と注意点が異なる。

- **A. 件数**
  - `rowsCount` が本家製品スペック表の行数（番手ごとに別行）と一致するか
  - スピニングとベイトが同一ページに混在する場合、行の取りこぼしに注意
- **B. reel_type（必須・制約あり）**
  - `reel_type` が `spinning` / `bait` のどちらで返されているか
  - 本家ページのカテゴリ・商品名（例: `～SS AIR TW`, `EXIST` 等）と整合するか
  - DB 制約 `ck_reel_model_type` により `spinning` / `bait` 以外は**保存不可**
- **C. 主要数値項目の原文一致**
  - `gear_ratio`: 本家表記そのまま（例 `6.3`, `7.1` / `8.1`／ダブルハンドル表記含む）
  - `weight_g`: 整数 g
  - `list_price`: 本家表記とプレビューが食い違う場合は **🔴**。税抜／税込の**解釈方針**がページから一意に決まらない（比較不能）場合のみ **🟡**（不一致ではなく判定保留の別枠。セクション 7）
  - `jan_code`: 13 桁数字。欠落時は空で OK（`missingOptional`）
  - 近似語（`約` 等）混入禁止はロッドと同様
- **D. 技術特性**
  - `technologyLabels` が**当該アイテムの TECHNOLOGY 行**と一致するか
  - ページ冒頭の技術紹介セクションを別番手に**誤付与**していないか
  - **不足**: 本家に照らし**付くべき**ラベルが `technologyLabels` に無い・著しく欠ける場合は **🔴**（セクション 7）。
    ロッドの **C** と同様の解釈。
  - マスタ突き合わせは `tackle_technology_feature.category = 'reel'` のみ対象
    （ロッド用スラグ・ラベルを誤って再利用していないか）
- **E. シリーズ・型番 / その他項目**
  - `seriesName` が本家見出しどおりか（世代／XH・HG 等の派生統合に注意）
  - `modelName` が本家表記そのままか（番手・ハンドル仕様の記述一貫性）
  - `listPrice`, `janCode`, `gearRatio`, `weightG` 等はログ payload の `rows[]` に載る
    （キー名は実装どおり。ロッド現行は camelCase）。値が null でもキーは確認できる。
    本家に記載があるのに AI が拾えていないケースは **🔴**（セクション 7）

## 7. 差異の分類

**原則**: `resolvedUrl` の**本家ページ**とプレビュー JSON を突き合わせ、セクション 6A / 6B の**解釈ルール**（例: 帯分数と小数の同値、単位の表記揺れ）を適用したうえでなお残る**不一致はすべて 🔴**とする。🟡・🔵 は、**本家とプレビューが一致している**（または本家が比較対象外・欠損で「不一致」とは呼べない）前提で付す**別種**の注意・参考に限る。

見つけた差異は以下のいずれかに分類する:

- 🔴 **問題（保存前に修正必須）**: **本家との不一致すべて**（件数・数値・シリーズ／型番・技術特性の不足・誤付与・サマリ項目の取りこぼし等）、NOT NULL / 制約違反の懸念
- 🟡 **注意（運用判断）**: **本家一致が確認できたうえで**のマスタ整備、命名ポリシー、税抜／税込など**ページから一意に読めない**ときの方針保留、既存 DB との整合方針（不一致そのものではない注記）
- 🔵 **情報（参考）**: **本家一致**のうえでの補足、表記揺れの統合候補メモ、🔴🟡 に該当しない運用メモ（突き合わせ結果が一致している場合の付記）

## 8. 対策の 3 段整理

問題 (🔴) が 1 件以上ある場合、以下 3 段でユーザーに提示する。
**書き方は必ずセクション 8.1 に従う**（具体性・汎用性・**期待効果**）。

- **即時対応（コード変更・保存前に適用推奨）**
  - `spec_import/tackle_spec_import.py` の system_prompt へ禁則文言追加（例: 近似語禁止）
  - ロッド: `_parse_decimal_range_text` / `_format_preview_ounce`
    で近似語を正規化 or 拒否
  - リール: `reel_type` の値域（`spinning` / `bait`）を
    サーバ側で再チェックし、想定外値はプレビュー段階でエラー化
  - `tests/services/test_tackle_spec_import_*.py` に該当ケース追加
  - **期待効果（例）**: プレビュー上の当該種別の**誤変換・制約違反の再発を抑止**、回帰をテストで捕捉
- **中期対応（運用ポリシー）**
  - `tackle_technology_feature` の正典化（`category` 別に表記揺れ統合）
  - シリーズ命名ポリシー（新旧世代分離ルール）の文書化
  - リール価格の税抜／税込ポリシー統一
  - **期待効果（例）**: マスタ・表記の**一貫性**向上、解釈のばらつきによる 🟡 を減らす
- **長期対応（仕組み）**
  - プレビュー UI に警告バッジ表示
  - 本作業を定期バッチ化し、保存前に自動チェック
  - **期待効果（例）**: 利用者が**保存前**に不整合に気づきやすい、**品質の継続監視**が可能になる

### 8.1 対策の記述ルール（必須）

#### 具体性（何をどう変えるか）

- 「プロンプトを強化」「要確認」など**一文だけ**で終わらせない。
- 各項目に少なくとも次のいずれかを**箇条書きで**含める:
  - **ファイルパス**と**関数名・設定キー・プロンプト節の見出し**（推測なら「要調査」と明記し、調べ方を1行）
  - **入出力の例**（今回の 🔴 を再現する最小入力と、修正後に期待する出力・判定）
  - **テスト**: 追加するテストファイル名と、検証する**一般化した条件**（特定 SKU 名にハードコードしない）
- 🔴 が無く 🟡 のみのときも、**運用・マスタ**側は「誰が・どの画面／どのテーブルで・何を更新するか」まで落とす。

#### 汎用性（シリーズ横断）

- 対策の**主軸**は、今回の `resolvedUrl` や機種名に依存しない表現にする:
  - 例: 「脚注の `※` 列挙と `TECHNOLOGY：` 行の**突合ルール**」「分数・帯分数の**等価判定**と**禁止する近似パターン**」「`technology` マスタの **category スコープ**」など、**ルールとして書ける**もの。
- **特定シリーズ・特定 URL・特定型番だけ**の例外分岐（if URL == …）は**最終手段**とし、単独提案では足りない。採用する場合は必ず併記する:
  - なぜ一般ルールに落とせないか（ページ構造の限界など）1〜2文
  - 可能な**一般化**（同メーカー同型のページでも効く条件、正規表現・DOM パターンの抽象度）
- シリーズ固有の用語（商品固有名）だけを増やす対策は **🔵 情報**に留め、**即時対応の主対策**にしない（マスタ・別表で吸収する方を優先）。

#### 期待効果（各対策に併記・必須）

- 即時／中期／長期の**各項目**（箇条書きの一塊）に、**この対策を入れたら何が改善するか**を **1 行**で必ず付ける。書き方の例:
  - **品質・リスク**: 「プレビューにおける X の取りこぼしを減らす」「Y という 🔴 原因をサーバでブロック」
  - **観測性**: 「同種の不整合をテストで**回帰検知**」「運用で参照する**正典**が1つになる」
  - **利用者体験**: 「保存前に**警告**が出るため誤登録の手前で止まりやすい」
- 抽象語だけ（例:「品質が上がる」**のみ**）は避け、**どの失敗パターンが減るか**に紐づける。
- Obsidian 正本（セクション 11 の「6. 対策」）では、**対策文の直後**に `- **期待効果**:` または行末の括弧 `（期待効果: …）` のいずれかで統一してよい（同一ファイル内で表記を混在しすぎないこと）。

### 8.2 記載例（粒度の目安）

#### 悪い例（不十分）

- 即時: j1nnhzx の行だけ直す。中期: ダイワを見直す。

#### 良い例（具体かつ汎用＋期待効果）

- 即時: `spec_import/tackle_spec_import.py` の system_prompt 内「ルアー重量」節に、本家が分数 `1/96` のとき**別分数へ近似しない**旨を追記。
  サーバ側は `fractions.py`（または既存の oz 正規化）で `約` を拒否し、
  `test_tackle_spec_import_helpers.py` に「`1/96` 入力→`1/64` 化しない」**パラメタ化**したケースを追加。
  - **期待効果**: 同種の**分数誤変換**をプレビュー上で減らし、回帰をテストで捕捉できる。
- 中期: `tackle_technology_feature` でロッド用ラベルの表記揺れを統合し、プレビューは **当該行の TECHNOLOGY** と **脚注ブロック**の突合を優先する方針を SPEC に1段落で残す。
  - **期待効果**: マスタと本家表記の**揺れ**を抑え、技術名の**取り違い・不足**（🔴/🟡）の再発率を下げる。

## 9. 結果の Markdown ファイル出力（必須）

### 9.0 正本の保存先（Obsidian・固定）

- **絶対パス（1 箇所のみ）**:
  `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`
- **親ディレクトリ** `.../DevProject/FishTrack/`。無い場合は**作成**する。ファイルは**毎回このパスを上書き**（パスをコマンド内で増やさない）。
- **混同注意**: フォルダ名 `FishTrack` は**Obsidian 内**の分類用である。**git リポジトリ**
  `d:/OneDrive/git_work/FishTrack` とは**別物**（同一マシン上の**別パス**）。
- **上記 git リポジトリ**のルートには**本レポートを書かない**（作業用・git 外とする）。

**正本は上記 1 ファイルのみ**とする。セクション **11.1（成功）または 11.2（プレビュー未到達）** の本文構成（および URL 同一時の **「## 前回からの変化」**）を**すべて**ここへ UTF-8（BOM なし）で書き出す。
チャットに**同一本文を繰り返し載せる必要はない**（**9.4** の要約で足りる）。

`Write` ツール、または Python の `path.write_text(..., encoding="utf-8")` を用いる（**BOM なし**）。
**PowerShell の `>` で当該 `.md` を書かない**（エンコード事故防止。セクション 0 参照）。

### 9.0.1 Markdownlint（必須）

- 正本の `Write` / `path.write_text` 完了**後**、**同一応答内**で次を行う:
  1. **lint 実行**（`dev-workspace` のルール）:

     ```powershell
     Set-Location "d:\OneDrive\git_work\dev-workspace"
     npx markdownlint-cli -c .markdownlint.json "D:\OneDrive\アプリ\remotely-save\Obsidian\DevProject\FishTrack\ai_spec_check_report.md"
     ```

  2. **違反がある場合**:`dev-workspace` の `markdownlint-fix` SKILL（および `markdown-editing`）に従い、**同ファイル内の指摘をすべて**解消する。再実行して**エラー 0 件**にする。

- レポート作業の**完了条件**＝**lint 通過**（**終了コード 0**、指摘 0 件）。**lint 未実施のまま完了報告しない**。
- **MD041 対策**: フロントマター直後（`---` 閉じの次行）に **1 行の h1**（例:
  `# AI 補助スペック取り込み照合`）を置き、**本文**は `##` から続ける。
  `pageTitle` との**重複**は可（Obsidian 表示はフロントマターも併用される）。
- **補足**: 対象ファイルが Obsidian ルート配下の場合、上位の**別の** markdownlint 設定に
  引っ張られ得る。`-c` に **dev-workspace** の
  `d:\OneDrive\git_work\dev-workspace\.markdownlint.json`（絶対パス）を明示すると、
  **当リポのルール**に固定しやすい（上記 `Set-Location` 例と併用）。

### 9.0.2 旧パス・旧ファイル名（参考）

- 2026-04: `tmp_ai_spec_check_report.md` を `DevProject/` 直下や旧
  `d:/OneDrive/git_work/FishTrack/` に置いていた時期あり。**現行**は **セクション 9.0** の
  **`ai_spec_check_report.md`**（`DevProject/FishTrack/`）。**`tmp_` 接頭辞は廃止**。
  古い path の残ファイルは移動・削除可。

### 9.4 チャットへの返答（要約のみ）

チャットには次だけを書く（表・長文の対策全文は**書かない**。ファイルが正本）。

- **レポートの絶対パス**（`D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`）
- **1〜3 行サマリ**:
  - **成功時**: `resolvedUrl` / category / rowsCount / 🔴・🟡 の件数または要旨
  - **失敗のみ時**: `sourceUrl` / `code` / `requestId`（`req_…`）/ メッセージ要旨 / ログに行があったか
- **同一 URL の再チェック時**: 「前回からの変化」の**一文**（詳細はファイル内の当該見出し）
- ユーザーがファイルにアクセスできない事情がある場合のみ、チャット側に抜粋を足してよい（**原則不要**）

### 9.1 フロントマター（必須）

ファイル先頭に YAML を置く。続けて **セクション 9.0.1** の **h1 1 行**のあと、本文（`##` 見出し）を書く（**markdownlint 整合**用）。

```yaml
---
ai_spec_check_report: "1"
checked_at: "YYYY-MM-DDTHH:MM:SS+09:00"
resolvedUrl: "https://..."
category: "rod"
rowsCount: 13
pageTitle: "取得できた場合"
source_log_hint: "例: temp/tmp_prod_preview_grep.log / --index 0 / ssh パイプ"
---
```

例（本文直後）:

```markdown
# AI 補助スペック取り込み照合

## 1. 対象ログ
```

### 9.2 前回ファイルとの扱い（URL による分岐）

1. **セクション 9.0 の固定パス**に**既存**の `ai_spec_check_report.md` があるか読み、あればフロントマターの `resolvedUrl` を取り出す。
2. **ファイルが無い**、または `resolvedUrl` が**今回の JSON の `resolvedUrl` と異なる**場合:
   - **全文を置換**する（旧内容は残さない＝**クリア相当の上書き**）。
   - 本文先頭に 1 行程度の注記を付けてよい: 例「※ 前回と URL が異なるため、ベースラインを新規に記録した。」
3. **`resolvedUrl` が前回と同一**の場合:
   - 上書き前に、**旧ファイルの本文**（フロントマター直下から EOF まで）を読み、比較材料にする。
   - 新しい本文に **「## 前回からの変化」** を**必ず**含め、次を箇条書きで書く（該当なしなら「差分なし（主要観点ともに同等）」と明示）:
     - **改善**: 前回 🔴/🟡 だった事象が今回解消・緩和した具体（row / modelName / 観点）
     - **後退**: 前回は問題なし・軽微だったが今回 🔴/🟡 が増えた具体
     - **継続課題**: 前回から変わらない 🔴/🟡（行・項目を列挙）
   - 同一 URL の**連続実行**では、レポートは**最新 1 回分のフル内容**を本文に含め、**「前回からの変化」**で差分を吸収する（旧レポート全文をファイル末尾に無制限に積まない）。

### 9.3 本文の構成

次節「11. レポート本文の構成」の **11.1（成功）または 11.2（プレビュー未到達）** に従い、同じ順・同粒度で本文を書く（表・🔴🟡🔵・対策を省略しない）。
**「## 前回からの変化」**は、セクション 9.2 のとおり URL が同一のときのみ必須。URL が変わった初回は省略可。

## 10. 後片付け（必須）

**完了条件**: FishTrack リポ内の**作業用一時ファイルを残さない**こと（存在しなければスキップ可）。

```powershell
cd d:/OneDrive/git_work/FishTrack
Remove-Item temp/tmp_latest_preview.json, temp/tmp_latest_failure.json, temp/tmp_prod_preview_grep.log, temp/tmp_prod_fail_grep.log, temp/tmp_prod_llm_io_grep.log, temp/_fetch_prod_grep.py, temp/_fetch_prod_fail.py -ErrorAction SilentlyContinue
# 当該実行で temp/ に追加したその他の作業用ファイル（抜粋・短い取得用 .py 等）があれば同様に削除
```

EC2 上に一時ファイルを作った場合は、作業方針に従い削除する。常設スクリプト
`scripts/dump_spec_import_preview.py` は削除しないこと（本作業から毎回利用する）。

**Obsidian 正本**（**セクション 9.0**）の `ai_spec_check_report.md` は**削除しない**（次回の URL 比較・差分確認用）。
**`temp/` ディレクトリ自体**は残してよい（`.gitignore` 対象。空でも可）。

## 11. レポート本文の構成（`DevProject/FishTrack/ai_spec_check_report.md` 正本）

**セクション 9** で出力する Markdown の本文に、必ず以下の順で書く（**チャットには転記しない**。**9.4** の要約のみ）。

### 11.1 プレビュー成功時（従来）

1. **対象ログ**: 取得時刻 / category / resolvedUrl / pageTitle / rowsCount
   / 確定状態（DB 保存済みか）。**原因分析**では次を**併用**する（デバッグログ有効時・取得できた範囲で）。
   - **`llmPrompts`**（プレビュー結果 JSON 内）… 各 `step` の **system / user 入力**
   - **`AI補助スペック取り込みLLM入出力:`** ログ行… 各 `step` の **入力に加え `response`（またはエラー時の生/要約）**。
     **本家との差分の説明では `response` を優先的に参照**する（入力だけでは足りないことが多い）。
   - ログ断片の突合は **`requestId`**・**ログ行先頭日時**・`resolvedUrl` / `sourceUrl` で行う。
2. **件数整合**: rowsCount vs 本家表行数
3. **数値突き合わせ表**:
   - ロッド: row / modelName / 本家値（lureWeightOz, length 等）
     / AI 値 / 判定（**帯分数と小数が同値なら判定は「一致」**。例: `1 1/2oz` と `1.5`）
   - リール: row / modelName / 本家値（reel_type, gear_ratio, weight_g,
     list_price, jan_code 等）/ AI 値 / 判定
4. **技術特性突き合わせ表**（マスタ `category` と AI 出力カテゴリの一致確認を含む）
5. **差異の分類（🔴 / 🟡 / 🔵）** — **セクション 7** の原則どおり、**本家との不一致はすべて 🔴**（🟡・🔵 に降格しない）
6. **対策提案（即時 / 中期 / 長期）** — **セクション 8.1** どおり、**具体**（ファイル・関数・テスト・期待挙動）かつ**汎用**（シリーズ固有例外に頼らない主軸）で書き、**各対策に期待効果**（**セクション 8.1**「期待効果」）を**必ず併記**する。セクション **8.2** の悪い例・良い例に倣う。
7. **次アクション候補 (1)〜(n)** とおすすめ順

同一 `resolvedUrl` の再チェック時は、上記に加え **「## 前回からの変化」**（セクション 9.2）を**ファイル本文に**含める。チャットでは **9.4** に従い一文要約にとどめる。

### 11.2 プレビュー未到達時（`--kind failure` の JSON のみ）

本家との**行単位突き合わせは無い**。次の順で書く。

1. **対象ログ**: **ログ行先頭日時** / `jobId` / `code` / `message` / `requestId` / `sourceUrl` / `model` / ログ取得手段（`source_log_hint`）。
   **`llmExchanges` がある場合は**各要素の **`step`・`response`（または失敗時フィールド）**を要約して記載する。
   **無い場合**はセクション **2** の **`grep LLM入出力:`** 結果で同趣旨を補う。
2. **件数・表の整合**: 「プレビュー行未取得のため対象外」と明示
3. **数値・技術表**: 同上（対象外）
4. **差異の分類**: セクション 7 の「本家不一致 🔴」ではなく、**ジョブ失敗・品質ブロック**として整理する。
   - 例: `no_preview_rows` かつメッセージが「型番候補なし」→ 🔴（保存不能・要原因調査）
   - `manufacturer_inference_failed` → 🔴 または 🟡（`sourceUrl`・ページ内容による）
   - ログが無く追えない場合は 🟡「デプロイ前ログ／未出力」の注記と**再現手順**
5. **対策**: **セクション 8.1** どおり。`spec_import/tackle_spec_import.py` の抽出・分類・
   `routes_master` のエラーコード、`tests/services/test_tackle_spec_import_*.py` 等に**汎用的に**紐づける。**各項目に期待効果を1行**
6. **次アクション**: デプロイ確認・同一 `sourceUrl` での再試行・`grep` 手順の見直し 等

**フロントマター**（セクション 9.1）: `resolvedUrl` に **`sourceUrl` を入れてよい**（比較・再チェックのキー）。`category` は `failure` または `-`、`rowsCount` は `0`。`pageTitle` は空または手動取得時のみ。

**「前回からの変化」**（セクション 9.2）: 比較キーは **`sourceUrl` + `requestId`**（または `jobId`）。成功レポートとの切替時は URL 変更扱いでよい。

## 12. 禁止事項

- Windows エージェントで、**本番の多行 grep 抜粋**に **`ssh | python --stdin` のみ**
  を用い、**0 件で打ち切る**こと（**`write_bytes` + `--file`** を試さない。セクション
  「Windows エージェント」）
- PowerShell の直リダイレクト（`> file`）で UTF-8 ログの本文だけを**誤った
  エンコード**で受け取ること（`--out` またはパイプ先の Python 経路を用いる）
- 本番 **RDS / データベース**への接続、および **DB への書き込み**（本作業は
  ログ照会・取り込み前検証のみ）
- 作業用の一時ファイル・機密を**不用意に**残すこと
- プロンプト補強のみで満足し、サーバ側バリデーションやテスト追加を
  検討しないこと（プロンプトは AI 側の揺らぎで再発しうるので、保険の
  サーバ側対策まで必ず提案する）
- **対策が抽象的な一行**、または**特定シリーズ・URL・型番だけの例外**に
  終始すること（セクション **8.1** 違反）
- **対策だけを列挙し期待効果を書かない**こと（セクション **8.1**「期待効果」違反）
- **本家**ページとプレビューの**不一致**を 🟡 / 🔵 へ**格下げ**して報告すること（セクション **7** 違反）

## 13. CursorLog 更新（必須）

- 作業完了後、`obsidian-cursor-log` SKILL を使用して当日の CursorLog
  （`D:/OneDrive/アプリ/remotely-save/Obsidian/CursorLog/YYYY-MM/YYYY-MM-DD.md`）
  に記録する
- 記録内容: 対象 URL・対象シリーズ・差異サマリ・提案した対策の要点・
  **セクション 9.0** の **Obsidian 絶対パス**（`D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`）・同一 URL 時の「前回からの変化」要約・
  ユーザーの合意状況
- タグ候補: `#fishtrack` `#spec-import` `#ai-preview-check`
  `#データ品質`。カテゴリに応じて `#ロッド` または `#リール` を追加し、
  問題 🔴 があった場合は `#要対応` も付与する
