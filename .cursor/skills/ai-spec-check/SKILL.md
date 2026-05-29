---
name: ai-spec-check
description: >-
  本番 FishTrack のログから「AI補助スペック取り込みプレビュー結果」、
  「AI補助スペック取り込みLLM入出力」（API 呼び出しごとの入出力）、および
  プレビュー未到達時の「プレビュー失敗」1行JSON（必要時 `llmExchanges`）を取得し、
  本家ページと突き合わせてロッド／リールの取り込み品質を検証する（失敗時は原因整理中心）。差異は 🔴🟡🔵 に分類し、
  対策案を優先度（高／中／低）で具体化する（**FishTrack 実装・Obsidian 仕様を加味**。**正本 §6 は新規検討分のみ**・**実装済みの棚卸しは書かない**。共通 **`ai-spec-check-report` §8**）。
  **各対策に期待効果**を併記し、正本 **§4 は「対策 N」連番・§5 と対応**（**`ai-spec-check-report` §8.1**）して Obsidian `ai_spec_check_report.md` に書き、
  CursorLog を更新する。専用 Cursor Command はなく本 SKILL が正本。AI スペック取り込みプレビュー検証、
  spec import プレビュー照合、dump_spec_import_preview、本番 fishtrack.log プレビュー行の依頼時に使用する。
---

# AI スペック取り込みプレビュー検証 SKILL

## 概要

**手順の正本**は **二段構成**である（ダブルメンテ抑制のため共通化した）。

- **本ファイル（`ai-spec-check/SKILL.md`）**: 本番 EC2 からのログ取得を含む **§0〜3**（入口・前提・`dump` まで）
- **`ai-spec-check-report`（同ディレクトリ）**: **§3.1**（`dump` CLI 早見）および **§4〜13**（サマリ確認・本家照合・レポート・禁止事項・CursorLog）。**`ai-spec-check-local` も同一ファイルを参照**

- **実行順・実装の境界**: **`ai-spec-check-report`** の **「実行順：dump 検証を先に・対策の実施はユーザー決定」** に従う（**dump 照合・レポート検証を先に**、**対策の実施はユーザー判断**・無断実施禁止）。

**エージェントは** 本ファイルを **Read** したうえで **`ai-spec-check-report` を Read** し、ターミナル実行・本家突き合わせ・Obsidian 正本・markdownlint・作業用 `temp/` の後片付け・**obsidian-cursor-log** まで行う。手順の提示だけで終わらない。

**ローカル Docker のみ**で照合するときは **`ai-spec-check-local/SKILL.md`** を入口にする（本番 SSH は不要）。\
**`src/` 変更後**に**ユーザーがブラウザでアプリを操作する**（プレビュー含む）**前**の **`docker compose restart app`** は **ブラウザ側の要件**であり、**`dump` スクリプトとは無関係**（詳細は **`ai-spec-check-local`** 本文）。

**人間向けパス（再掲）**:

- FishTrack ルート: `d:/OneDrive/git_work/FishTrack`
- レポート正本: `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`
- 突合用本家データ（`ai-spec-notes`）:
  `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai-spec-notes/`。\
  **`ai-spec-check-report` §5.1**（**DAIWA ロッド**は **`rod-daiwa/`**。取得元でフォルダを分けない）。URL本文の丸写しではなく、
  プレビュー `rows[]` と比較するための**本家側データ（数値・JAN 等）をノート内に必ず残す**。\
  本家に **ライン（lb）** 列（**ナイロン lb レンジ**、または第三者 **`ライン(lb.)`** 型）があるときは **行別 lb 原文**を `ai-spec-notes` に載せ、**`lineMinLb`／`lineMaxLb`** と照合する（**`ai-spec-check-report` §6A B**）。\
  **ノートのファイル名**に **URL の一部**（`/product/` 末尾の短い ID 等）を**含めない**（同 §5.1 命名規則。同定は **`## メタ` の `resolvedUrl`** のみ）。
  **`## 行別スペック` を `ai_spec_check_report.md` への参照だけで埋めることは禁止**（§5.1 冒頭）。\
  **ロッド**は **`## 行別スペック`** に **`rows[].modelName` と突合する期待文字列（`modelName期待` 等）を行別に必ず書く**（同 §5.1）。\
  **シリーズ一覧からモデル個別 URL があるとき**は **§5.1「モデル個別ページ」**どおり**全モデル個別ページを確認**してからノートを完成扱いにする（**突合ノートの漏れ解消が最優先**）。\
  **ロッドで本家にジャンル列が無いページ**は **`ai-spec-notes`** に **FishTrack が確定する
  `genre`（`bait`／`spinning`）の行別表**を置く（**§5.1.1** 項 5。**`05`** の型番末尾ルールを根拠列に書く）。\
  **本家にパワー列・テーパー（アクション）列が無い DAIWA ロッド**は **`## 行別 Pattern 期待値`** に\
  **`infer_power…` / `infer_action…` の行別表**を置く（**§5.1.1** 項 4・**`ai-spec-check-report` §5.1**）。\
  実行ごとの判定・課題は **`ai_spec_check_report.md`** のみ。
- 作業用出力先: FishTrack リポ内 `temp/`（完了後に当該作業分を削除。**`ai-spec-check-report` 本 SKILL §10（後片付け）**）

myrules を厳守して作業してください。

**用語（本文）**: 本 SKILL および **`ai-spec-check-report`** の追記・改稿では **「総覧」** を**使わない**（**`ai-spec-check-report` の「用語（本スキル群の本文）」節**に従う）。

**ユーザー指摘の反映**: レポート構成・§8 の体裁・dump 手順・lint・CursorLog 連携などへの**指摘**があった場合は、**同一セッションで** **`ai-spec-check-report`** または **`ai-spec-check-local/SKILL.md`** を修正する（\
  dev-workspace **myrules**「**ユーザー指摘に基づくルール・SKILL の育成**」）。

**本番** FishTrack（EC2 上の Docker / `app` サービス）のログから、最新の
「AI補助スペック取り込みプレビュー結果」を取得し、ログ中の `resolvedUrl` に
アクセスして本家ページと突き合わせ、取り込み漏れ・想定外・誤変換がないかを
判定してください。問題があれば、根本原因と**対策案**（優先度：高／中／低）を**実装を加味し**、
**新たに**検討する**追加**対策に**絞って**（**`ai-spec-check-report` §8**・**§8.1**。**既存**実装の**列挙**は**正本 §6 に含めない**）具体的に
まとめ、**各対策の期待効果**を併記してください。エージェントがターミナルで実行すること。手順の提示だけで
終わらないでください。

**報告確定チェック**：Obsidian に **`ai_spec_check_report.md`** を **`Write` で上書き**する直前、`ai-spec-check-report` SKILL **§8.1 の「報告直前チェックリスト」**で **`## 4.`/`## 5.` 消込**を確認する。\
**§4 からの `対策 N` 削除**は **`FishTrack`/`src`・テストへの反映完了がトリガー**（**再プレビュー未取得でも可**。**正本「`対策 N` のクローズ削除」**・**§8.1**）。

**報告の出し分け**: 表・分類・対策の**全文**は **`ai-spec-check-report` §9** の
**Obsidian 上の** `ai_spec_check_report.md`（**固定絶対パス**、同 §9.0）にのみ書く。**チャット**には **§9.4**
の要約（パス・数行サマリ）で足りる。同一本文をチャットに再掲載しない。

**注意**: 旧来どおり FishTrack リポジトリルートにレポートを置かない。git 管理対象外の作業用ドキュメントは **Obsidian** に集約する。

**読み取り専用タスク**: 本番・ローカル **DB への接続・書き込みは行わない**。
本番 **EC2 へはログの読み取り**（SSM / SSH、コンテナ内ファイルまたは stdout）
のみとする。プレビュー結果（DB 未保存）を見る段階で、問題があれば確定前に
止めるための作業です。

## Markdownlint（lint 無効化の禁止）

- **無断での lint 無効化は禁止**（`markdownlint-disable` コメント、設定の勝手な緩和・除外など）。**正本・手順は `ai-spec-check-report` §9.0.1**。本文修正・折り返しで解消し、必要なときは**ユーザーの明示承認**のうえで限定的に対応する。

## 使用タイミング

- ユーザーが AI 補助スペック取り込みのプレビュー品質を**本番ログ**で確認したいとき
- `ai-spec-check`（本 SKILL）の実行依頼、「AI スペック取り込みプレビュー検証」、「プレビュー結果を本家と照合」等の指示があったとき（**本番**）
- **ローカル Docker**のみのときは **`ai-spec-check-local`** を使う

## 補足（DAIWA ロッド）

- **`X45` と `X45フルシールド`** は**併記しうる**（**トレードオフではない**）。照合・`ai_spec_check_report.md` で **🔴／🟡** の根拠に**しない**。\
  **詳細は `ai-spec-check-report` §6A C**。
- **`pieces` の `N（テレスコピック）`（全メーカー共通）**: テレスコピック（振出し）と確定し、本家 **継数が数値のみ**のとき、期待・プレビュー正は **`N（テレスコピック）`**（全角括弧・**`05_ai_spec_import.md`**）。\
  **DAIWA** は型番コア **`T`**、**LEGIT TELECAST** 等は振出し専用ページ等（判定例は **`ai-spec-check-report` §6A E**）。**数値のみのプレビュー**は不一致（**🟡 にしない**）。
- **`action`（テーパー略号・全メーカー共通）**: 突合ノート／CSV の期待およびプレビュー照合正は **`F`／`RF`／`RS`／`XF` 等**（**`Fast`・`Regular Fast` 長文は載せない**）。\
  本家 **Action** 列は原文のまま比較表に載せ、期待は略号（例: **`Regular Fast`／`Regular first`（typo）→ `RF`**）。詳細は **`ai-spec-check-report` §6A B**。
- **`releaseYear`（販売年・全メーカー共通）**: 本家に発売年根拠があるときは **`ai-spec-notes` の行別期待**と **`rows[].releaseYear`** を **§2.7** で突合（**根拠なしは全行 null 期待で 🔵**）。\
  **価格脚注の改定日だけ**は根拠にしない。詳細は **`ai-spec-check-report` §6A E**・**`05_ai_spec_import.md`**（横断フィールド **`releaseYear`**）。

## 0. 前提・環境

- プロジェクトルート: `d:/OneDrive/git_work/FishTrack`（**常設スクリプト**の実行元）
- **作業用ファイル**（`tmp_latest_preview.json`・`tmp_prod_preview_grep.log` 等）は
  リポジトリ直下に置かず、**`temp/`** 配下に集約する（例: `temp/tmp_latest_preview.json`）。
  `dump_spec_import_preview.py --out` は親ディレクトリを自動作成する。
  **本作業の作業完了後**（Obsidian レポートと **`obsidian-cursor-log` による CursorLog** まで済んだ時点）に、\
  当該実行で用いた **`temp/` 配下の作業用ファイルはすべて削除**する（**`ai-spec-check-report` SKILL §10（後片付け）**）。
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
- 上記を **`temp/_fetch_*.py`（数十行）**にまとめて試してもよい。
  myrules「一括置換用スクリプト」とは別（**単一ファイル**の補助に限る）。\
  **使い捨て**なら作業完了後 **`ai-spec-check-report` 本 SKILL §10（後片付け）** で削除する。

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

**`--kind` / `--count` / `--list` / `--order` / 0 件時の切り分け**の詳細は **`ai-spec-check-report` の §3.1** に集約した（本番・ローカル共通）。

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

**ロッド・全長照合（レポート必須）**: `category = "rod"` かつ成功プレビューの **`ai_spec_check_report.md`** では、\
**本家 全長（m）** と **`lengthFt` / `lengthIn`** の行別表を **必ず**書く。\
正本は **`ai-spec-check-report` §6A B**・**§11.1（本文構成）**・**Obsidian 正本 §2.2**・**`ai-spec-check-local` の「全長照合」**。

**ロッド・ルアー重量照合（レポート・`ai-spec-notes` 必須）**: **本家表にルアー重量列がある** `category = "rod"` 成功プレビューでは、\
**本家ルアー重量**（**DAIWA 複数列時は §6A B どおり oz 列のみ**）と **`lureWeightMinOz` / `lureWeightMaxOz`** の**行別表**を\
**`ai_spec_check_report.md`** に **必ず**書く。\
**`ai-spec-notes`** の **`## 行別スペック`** にも **本家値を行別で載せる**（**PE（号）列とライン lb を「いずれも突合不要」と一括しない**。**lb は §6A B**）。\
正本は **`ai-spec-check-report` §5.1**・**§6A B**・**§11.1（本文構成）**・**Obsidian §2.4**・**`ai-spec-check-local` の「ルアー重量照合」**。

**ロッド・ライン（lb）照合（`ai-spec-notes`・条件付き必須）**: 本家表に **lb レンジ列**（**適合ライン ナイロン（lb.）**、**第三者 `ライン(lb.)`** 等）がある\
`category = "rod"` 成功プレビューでは、**本家 lb 原文**と **`lineMinLb`／`lineMaxLb`** の**行別**照合を **`ai-spec-notes`**（およびレポート方針に従い正本）へ載せる。\
**PE（号）** だけを任意扱いする記述と **混同しない**。正本は **`ai-spec-check-report` §5.1**・**§6A B**。

**ロッド・テーパー／`action` 照合（レポート必須・DAIWA 等）**: 本家表に **テーパー**列がある \
`category = "rod"` 成功プレビューでは、**本家テーパー（原文）** と **`rows[].action`** の**行別表**を **必ず**書く。\
正本は **`ai-spec-check-report` §6A B**（**テーパー／アクション**）・**§11.1**・**Obsidian §2.3**。

**ロッド・`power` 照合（レポート必須）**: `category = "rod"` 成功プレビューでは、本家表に **パワー列があるときは本家原文 vs `rows[].power`**、**列が無いときは期待 `power`（根拠） vs `rows[].power`** の**行別表**を **必ず**書く（**テーパー／`action` と同義務**）。\
正本は **`ai-spec-check-report` §6A B**・**§11.1**・**Obsidian §2.3（power）**・**`ai-spec-check-local` の「パワー照合」**。

## 4. 以降の手順（共通・正本）

**§3.1**（CLI 早見・0 件切り分け）および **当該 SKILL §4〜§13（本 SKILL 内の章番号**。Obsidian **`ai_spec_check_report.md`** 本体は **§11.1**・**正本運用 §1〜§6**）は、\
**本番・ローカル Docker で共通**である。

次を **Read** し、**§3.1**（必要時）および **§4** から順に実行する。

`d:\OneDrive\git_work\dev-workspace\.cursor\skills\ai-spec-check-report\SKILL.md`

**補足**: **`ai-spec-check-local`** から実行するときも **同一の `ai-spec-check-report`** を参照する（パスは上記と同じ）。
