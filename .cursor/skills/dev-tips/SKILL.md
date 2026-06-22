---
name: dev-tips
description: 開発に関わるTIPSや注意点を短く整理して提示するスキル。設計・実装・テスト・運用・ドキュメント・レビューで迷った時や、品質/安全性/保守性/性能の観点を漏れなく整理したい時に使用する。特に入力検証、エラーハンドリング、ログ、設定管理、HTML/JS分離などの開発上の注意点をまとめる依頼で使用。
---

# 開発TIPS/注意点

## 概要

開発全般のTIPSや注意点を、設計・実装・テスト・運用・ドキュメントの観点で整理して提示する。迷いや漏れが出やすい観点を短く網羅し、判断の質を上げることに集中する。

## 判断の優先順位

- 正確性・安全性を最優先し、次に保守性、可読性、性能、体裁の順で判断する
- 変更の影響範囲を先に確認し、可逆性（ロールバック/feature flag）を確保する

## 設計・実装TIPS

- 失敗モード（入力不正、外部依存失敗、タイムアウト）を先に洗い出す
- 例外/エラーは握り潰さず、原因と再現条件が追える情報を残す
- 例外発生時は、例外の内容や原因をトレースできる情報を必ずログに出力する
- 例外を握りつぶすことはしない
- 入力検証は境界条件と型の整合性まで含める
- 設定値は環境変数や設定ファイルで管理し、ハードコードしない

## セキュリティ/運用TIPS

- 機密情報はログやレスポンスに出さない
- 権限や認可は「誰が」「何に」アクセスできるかを明示的に確認する
- 監視・アラートに必要なメトリクスやログを最初から決めておく

## テスト/検証TIPS

- 正常系だけでなく異常系・境界値・競合条件のテストを含める
- 再現性の低い失敗は、ログ強化と最小再現の設計で潰す

## ローカル Docker × Python 変更（必須運用）

- **`docker compose` + Gunicorn 等**でアプリを動かしているとき、**`*.py`（例: `src/`）を変えたら** bind-mount でも **プロセスは古いモジュールのまま**になりやすい
- **対応**: **Docker が起動している場合**、プロジェクト直下で **`docker compose restart <アプリサービス名>`**（例: FishTrack は多くの場合 `app`）。**変更のたび・検証前**に実行する（**myrules.mdc**「ローカル Docker と Python ソース変更」・**`local-docker-python-restart`** SKILL）。**未起動・未導入時は省略可**（報告に 1 行）
- **イメージや依存の変更**は `build` / `up` が主。`--reload` 開発サーバのみの構成は別

## ドキュメント/レビューTIPS

- 仕様書は実装と同時に更新し、実装との差分を残さない
- ソースコードの修正時は合わせてドキュメントも更新する
- 必ずドキュメントとソースコードが一致するようにする
- レビューは「仕様逸脱」「安全性」「可観測性」「将来の変更容易性」を優先して確認する
- このスキルは随時更新する

## フロントエンド注意点

- HTMLにJavaScriptの内容を含めず、必ず別ファイルに分離する
- HTMLは`<script src="...">`で読み込み、ロジックは`static/js/`配下に置く

## 例（HTML/JS分離）

`index.html`:

```html
<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8" />
    <title>Sample</title>
    <script src="/static/js/app.js" defer></script>
  </head>
  <body>
    <button id="save">保存</button>
  </body>
</html>
```

`static/js/app.js`:

```javascript
document.getElementById("save").addEventListener("click", () => {
  alert("保存しました");
});
```

## Windows × Cursor × `.sh`（Deploy on AWS フック等）

**発火**: Cursor でエージェントの Write のたびに「`.sh` を開くアプリを選ぶ」ダイアログや **黒いコンソール（`sh.exe` / `bash.exe`）が残る**。

**原因（典型）**:

- **Deploy on AWS** プラグインの PostToolUse が **`validate-drawio.sh`** を **Edit|Write のたび**実行する
- Windows で **`.sh` に関連付け**すると、フック実行のたびに **新しいコンソール**が開く（**`git-bash.exe` は GUI 窓**、**`bash.exe` でも黒窓は出うる**）
- `ftype` を `bash.exe` に直しても **窓が自動で閉じない**ことがある（stdin 待ち・`sh.exe` 単体起動など）

**対処（優先順 — FishTrack 突合など draw.io 不要なら 1 だけで足りる）**:

1. **AWS Deployments プラグインをアンインストール**（Cursor → Settings → Plugins → **AWS Deployments** → **Uninstall**。一覧に Disable が無い場合は Uninstall で同等）— **最優先・管理者権限不要**。再起動推奨
2. 残っている黒窓はタスクバーから **× で閉じる**、またはタスクマネージャで **`sh.exe` / `bash.exe` を終了**
3. **`.sh` 関連付けを外す**（管理者 CMD）: `assoc .sh=`（ダイアログは戻りうるがコンソール量産は止まりやすい）
4. draw.io 検証も使う場合のみ: 管理者 CMD で `ftype sh_auto_file="d:\Program Files\Git\bin\bash.exe" "%1" %*`（**`git-bash.exe` 不可**）。それでも窓が残るなら **1 に戻す**

**確認**: プラグイン無効化後、エージェントに小さな Write を 1 回させ、ダイアログ・黒窓が増えないこと。
