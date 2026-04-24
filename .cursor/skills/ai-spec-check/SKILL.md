---
name: ai-spec-check
description: >-
  本番 FishTrack のログから「AI補助スペック取り込みプレビュー結果」を取得し、
  本家ページと突き合わせてロッド／リールの取り込み品質を検証する。差異は 🔴🟡🔵 に分類し、
  対策を即時／中期／長期で具体化して Obsidian 正本 `ai_spec_check_report.md` に書き、
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
まとめてください。エージェントがターミナルで実行すること。手順の提示だけで
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
  確認（SKILL 記載の ID は**例示**のため、実行前に要確認）
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
- プレビュー結果の識別文字列: `AI補助スペック取り込みプレビュー結果:`
- プレビュー payload のキー:
  `manufacturer, resolvedUrl, pageTitle, requestId, category, categoryReason,
   rowsCount, usage, rows[]`
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
  - `src/fishtrack/services/tackle_spec_import.py`（system_prompt / preview logger）
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
  - **本番**: `ssh` の**標準出力**を**パイプ**で `python ... --stdin` へ渡す、
    あるいは EC2 上で取得したログを**バイナリ近い**経路でローカルに置き
    `--file` する。いずれも「PowerShell の `>` だけで丸ごと保存」は禁止
- `docker exec ... > file` / `Get-Content -Raw` + 紛らわしいエンコード、等の
  「意図しない再エンコード」は禁止
- 詳細は `markdown-editing` / `obsidian-cursor-log` SKILL 参照

### PowerShell で SSH する場合（追加の注意）

**二重引用符 `"..."` だけで `ssh` の引数を囲まない**と、次が **Windows 側**で
解釈され、リモートに届かない・別の解釈になる:

- `2>/dev/null` や `2>&1`（**`2>`** も**リダイレクト**）
- `$(command)`（**PowerShell / cmd のコマンド置換**）。EC2 上の `ls` ではない

**推奨**:

- リモート 1 本にしたい部分は、**`ssh` の最外層引数を単一引用符 `'...'`**
  （PowerShell 7）で囲み、その中身は**Linux 向け**のまま渡す
- 難しければ **Python** の `subprocess.run([...], ...)` を使い、**引数のリスト**
  で `ssh` を起動し、シェル解釈を避ける
- 短い**プレビュー行だけ**抜き出すなら、本番上で
  `grep`（識別文字列の一部で可）し、**出力を Python から** UTF-8 バイトで
  `open(..., "wb")` してから `dump` に `--file` する方が、日本語の**一致率**
  も **パイプの遅延**も安定しやすい

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

**ローカル（開発 PC）**では、上記 `cat` 相当の**バイト列**がそのまま
`ssh` の stdout を経由して、次節の `python ... --stdin` に届く想定でよい
（`ssh` 経由のパイプ先が Python なら、PowerShell の `>` を挟まない）。

## 2. プレビュー結果ログの件数・一覧確認（常設スクリプト）

本作業では FishTrack 側の常設スクリプト
`scripts/dump_spec_import_preview.py` を使う。base64 ダンプ + ワンライナー
Python を廃し、日本語も UTF-8 のまま安全に扱える。

**本番（SSH）の例**（キー・ホスト・デプロイパスは差し替え）:

- **A. 抜粋＋`--file`（推奨）**: 本番上で `grep` 等で
  `AI補助スペック取り込みプレビュー` を含む行**だけ**出し、ローカルで
  バイナリ書き（UTF-8）→ `python scripts/dump_spec_import_preview.py --file <path> --list`
  （`<path>` は **`temp/tmp_prod_preview_grep.log`** 等、`temp/` 配下を推奨）
- **B. パイプ**（行数が少ないとき・検証用）: 下記。巨大ログの**丸ごと `cat`**
  は、環境によって**極端に遅い**場合がある。まず A を検討。

```powershell
cd d:/OneDrive/git_work/FishTrack
# 最外層を単一引用符にし、2> や $() がローカルで展開されないようにする
ssh -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@<本番IP> 'cd <deploy-dir> && docker compose -f docker-compose.yml exec -T app sh -c "grep -h プレビュー結果: /app/instance/logs/fishtrack.log* 2>/dev/null"' | python scripts/dump_spec_import_preview.py --stdin --list --limit 5
```

- `--stdin` … 前段の**標準出力**をそのままログ本文として解析
- 0 件のとき、PowerShell 直パイプで**マーカーに一致しない**（UTF-8 破壊）の
  可能性 → **A の `--file` へ切り替え**
- 件数だけ: `... | python ... --stdin --count`

**補足（ローカル Docker での検証に切り替える場合）**: 同一リポをローカル
で起動しているときは `--stdin` なしで従来どおり `docker` 経路で可。

```powershell
cd d:/OneDrive/git_work/FishTrack
python scripts/dump_spec_import_preview.py --count
python scripts/dump_spec_import_preview.py --list --limit 5
```

- `--count` … ヒット件数のみ表示
- `--list --limit N` … `[index] timestamp  category=...  rows=...  url=...` を
  N 件表示。**「新しい」順**は既定で `--order time`（ログ行先頭
  `[YYYY-MM-DD HH:MM:SS]` の**壁時刻**降順）。`grep` のファイル順混在に依存しない
- `--order file` … 従来どおり、入力テキスト上の**出現の逆順**（特殊用途）
- 0 件だった場合の切り分け:
  - 環境変数 2 つ（`FISHTRACK_STANDALONE`, `FISHTRACK_SPEC_IMPORT_DEBUG_LOG`）
    が本番 `.env` で有効か
  - ファイルに出ておらず **stdout** のみの可能性 → セクション 0 の (2) を参照
  - ローテーション後で別ファイルに移っている（ローカル `docker` 経路）
    → `--include-rotated` を付けて再実行、または本番 EC2 側で連結してから `--stdin`
  - まだ 1 度も本番でプレビューを実行していない → ユーザーの合意のもと
    本番 UI で再現依頼

## 3. 最新 1 件を JSON として取得

- **既定**の「最新」は **ログ行の日時**（`--order time`）が最大の 1 件。複数
  プレビューがあるとき、**`--list` で日付を目視**し、特定したい 1 件を
  `--index` で指す、という運用も可（index 0 ＝壁時刻で最新）。

本番（セクション 2 の `ssh` / `--file` のいずれかの後）:

```powershell
python scripts/dump_spec_import_preview.py --stdin --latest --out temp/tmp_latest_preview.json
# 抜粋をファイルに置いた場合
python scripts/dump_spec_import_preview.py --file temp/tmp_prod_preview_grep.log --latest --out temp/tmp_latest_preview.json
```

ローカル Docker のみ（`--stdin` / `--file` なし）の場合:

```powershell
python scripts/dump_spec_import_preview.py --latest --out temp/tmp_latest_preview.json
```

- 新しい順 **2 件目** など: `--index 1`（順序は `--order` 準拠）
- ローカル `docker` 経路でローテ済みログも対象にする: `--include-rotated`
- 出力 `temp/tmp_latest_preview.json` は UTF-8（BOM なし）。`--out` は
  スクリプト内で UTF-8 書き込み（PowerShell の `>` では書かない）

## 4. JSON サマリ確認

```powershell
python -c "import json,sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8'); p=json.load(open('temp/tmp_latest_preview.json',encoding='utf-8')); print('category:', p.get('category')); print('resolvedUrl:', p.get('resolvedUrl')); print('rowsCount:', p.get('rowsCount'))"
```

**カテゴリ分岐**: `category` の値で検証内容を分岐する。

- `rod` → セクション 6A（ロッド検証）
- `reel` → セクション 6B（リール検証）
- `lure` / `unknown` → スコープ外。カテゴリと `categoryReason` を報告して終了

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
**書き方は必ずセクション 8.1 に従う**（具体性・汎用性）。

- **即時対応（コード変更・保存前に適用推奨）**
  - `tackle_spec_import.py` の system_prompt へ禁則文言追加（例: 近似語禁止）
  - ロッド: `_parse_decimal_range_text` / `_format_preview_ounce`
    で近似語を正規化 or 拒否
  - リール: `reel_type` の値域（`spinning` / `bait`）を
    サーバ側で再チェックし、想定外値はプレビュー段階でエラー化
  - `tests/services/test_tackle_spec_import_*.py` に該当ケース追加
- **中期対応（運用ポリシー）**
  - `tackle_technology_feature` の正典化（`category` 別に表記揺れ統合）
  - シリーズ命名ポリシー（新旧世代分離ルール）の文書化
  - リール価格の税抜／税込ポリシー統一
- **長期対応（仕組み）**
  - プレビュー UI に警告バッジ表示
  - 本作業を定期バッチ化し、保存前に自動チェック

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

### 8.2 記載例（粒度の目安）

#### 悪い例（不十分）

- 即時: j1nnhzx の行だけ直す。中期: ダイワを見直す。

#### 良い例（具体かつ汎用）

- 即時: `tackle_spec_import.py` の system_prompt 内「ルアー重量」節に、本家が分数 `1/96` のとき**別分数へ近似しない**旨を追記。サーバ側は `fractions.py`（または既存の oz 正規化）で `約` を拒否し、`test_tackle_spec_import_helpers.py` に「`1/96` 入力→`1/64` 化しない」**パラメタ化**したケースを追加。
- 中期: `tackle_technology_feature` でロッド用ラベルの表記揺れを統合し、プレビューは **当該行の TECHNOLOGY** と **脚注ブロック**の突合を優先する方針を SPEC に1段落で残す。

## 9. 結果の Markdown ファイル出力（必須）

### 9.0 正本の保存先（Obsidian・固定）

- **絶対パス（1 箇所のみ）**:
  `D:/OneDrive/アプリ/remotely-save/Obsidian/DevProject/FishTrack/ai_spec_check_report.md`
- **親ディレクトリ** `.../DevProject/FishTrack/`。無い場合は**作成**する。ファイルは**毎回このパスを上書き**（パスをコマンド内で増やさない）。
- **混同注意**: フォルダ名 `FishTrack` は**Obsidian 内**の分類用である。**git リポジトリ**
  `d:/OneDrive/git_work/FishTrack` とは**別物**（同一マシン上の**別パス**）。
- **上記 git リポジトリ**のルートには**本レポートを書かない**（作業用・git 外とする）。

**正本は上記 1 ファイルのみ**とする。セクション 11「レポート本文の構成」の **1〜7**（および URL 同一時の **「## 前回からの変化」**）を**すべて**ここへ UTF-8（BOM なし）で書き出す。
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
- **1〜3 行サマリ**: `resolvedUrl` / category / rowsCount / 🔴・🟡 の件数または要旨
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

次節「11. レポート本文の構成」の **1〜7** と同じ順・同粒度で本文を書く（表・🔴🟡🔵・対策を省略しない）。
**「## 前回からの変化」**は、セクション 9.2 のとおり URL が同一のときのみ必須。URL が変わった初回は省略可。

## 10. 後片付け（必須）

**完了条件**: FishTrack リポ内の**作業用一時ファイルを残さない**こと（存在しなければスキップ可）。

```powershell
cd d:/OneDrive/git_work/FishTrack
Remove-Item temp/tmp_latest_preview.json, temp/tmp_prod_preview_grep.log -ErrorAction SilentlyContinue
# 当該実行で temp/ に追加したその他の作業用ファイル（例: 抜粋ログ・fetch スクリプト出力）があれば同様に削除
```

EC2 上に一時ファイルを作った場合は、作業方針に従い削除する。常設スクリプト
`scripts/dump_spec_import_preview.py` は削除しないこと（本作業から毎回利用する）。

**Obsidian 正本**（**セクション 9.0**）の `ai_spec_check_report.md` は**削除しない**（次回の URL 比較・差分確認用）。
**`temp/` ディレクトリ自体**は残してよい（`.gitignore` 対象。空でも可）。

## 11. レポート本文の構成（`DevProject/FishTrack/ai_spec_check_report.md` 正本）

**セクション 9** で出力する Markdown の本文に、必ず以下の順で書く（**チャットには転記しない**。**9.4** の要約のみ）。

1. **対象ログ**: 取得時刻 / category / resolvedUrl / pageTitle / rowsCount
   / 確定状態（DB 保存済みか）
2. **件数整合**: rowsCount vs 本家表行数
3. **数値突き合わせ表**:
   - ロッド: row / modelName / 本家値（lureWeightOz, length 等）
     / AI 値 / 判定（**帯分数と小数が同値なら判定は「一致」**。例: `1 1/2oz` と `1.5`）
   - リール: row / modelName / 本家値（reel_type, gear_ratio, weight_g,
     list_price, jan_code 等）/ AI 値 / 判定
4. **技術特性突き合わせ表**（マスタ `category` と AI 出力カテゴリの一致確認を含む）
5. **差異の分類（🔴 / 🟡 / 🔵）** — **セクション 7** の原則どおり、**本家との不一致はすべて 🔴**（🟡・🔵 に降格しない）
6. **対策提案（即時 / 中期 / 長期）** — **セクション 8.1** どおり、**具体**（ファイル・関数・テスト・期待挙動）かつ**汎用**（シリーズ固有例外に頼らない主軸）で書く。セクション **8.2** の悪い例・良い例に倣う。
7. **次アクション候補 (1)〜(n)** とおすすめ順

同一 `resolvedUrl` の再チェック時は、上記に加え **「## 前回からの変化」**（セクション 9.2）を**ファイル本文に**含める。チャットでは **9.4** に従い一文要約にとどめる。

## 12. 禁止事項

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
