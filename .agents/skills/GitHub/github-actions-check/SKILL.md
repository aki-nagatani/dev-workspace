---
name: github-actions-check
description: GitHub Actionsの完了を待って結果を確認するSKILL。otayori-navi、FishTrack、MyPokedexなどのリポジトリでプッシュやマージ後にGitHub Actionsの実行完了を待機し、成功/失敗を確認する。プッシュやマージ後のCI/CD確認に使用する。
---

# GitHub Actions確認SKILL

## 概要

このSKILLは、GitHub Actionsのワークフロー実行が完了するまで待機し、結果を確認するための手順を提供します。

## 使用タイミング

以下の場合にこのSKILLを使用します：

- otayori-naviのプッシュ後
- FishTrack/MyPokedexのmainブランチへのマージ後（**lint / test**。**deploy は skipped が正常**）
- 緊急デプロイの待機は各リポ `*_emergency-deploy`（**`workflow_dispatch`**。本 SKILL の push 待ちは使わない）
- その他、GitHub Actionsが実行される操作の後

## 実行手順（必須）

### 1. リポジトリとブランチの確認

確認対象のリポジトリとブランチを特定します：

- **otayori-navi**: `aki-nagatani/otayori-navi`、通常は`main`ブランチ
- **FishTrack**: `aki-nagatani/FishTrack`、通常は`main`ブランチ
- **MyPokedex**: `aki-nagatani/MyPokedex`、通常は`main`ブランチ

### 2. GitHub Actionsの確認開始

**🚨 必須**: プッシュやマージ完了後、**即座にGitHub Actionsの確認を開始する**

### 3. ワークフロー実行の確認

最新のワークフロー実行を確認します：

#### 方法1: GitHub CLIを使用（推奨・最優先）

GitHub CLI（`gh`）がインストールされている場合、最も簡単に確認できます：

```powershell
# リポジトリディレクトリに移動（例: otayori-navi）
cd d:\OneDrive\git_work\otayori-navi

# マージ済みmainのコミットに紐づくpush実行だけを特定する
git fetch origin main
$commitSha = (git rev-parse origin/main).Trim()
$run = gh run list --branch main --event push --commit $commitSha --limit 1 `
  --json databaseId,status,conclusion,url | ConvertFrom-Json
if (-not $run) {
    throw "main の $commitSha に対応する GitHub Actions 実行が見つかりません。"
}

$runId = $run.databaseId
Write-Host "GitHub Actionsを待機中: $($run.url)"
gh run watch $runId --exit-status --interval 10
if ($LASTEXITCODE -ne 0) {
    gh run view $runId --log-failed
    exit $LASTEXITCODE
}

# 成功時もジョブ結果を確認する
gh run view $runId
```

#### 方法2: GitHub APIを使用

GitHub CLIが使用できない場合：

```powershell
$repo = "aki-nagatani/otayori-navi"  # 対象リポジトリに変更
$headers = @{'Accept'='application/vnd.github.v3+json'}
try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/actions/runs?per_page=1" -Headers $headers
    $latest = $response.workflow_runs[0]
    Write-Host "Status: $($latest.status)"
    Write-Host "Conclusion: $($latest.conclusion)"
    Write-Host "URL: $($latest.html_url)"
} catch {
    Write-Host "⚠️ GitHub APIエラー: $_"
    Write-Host "手動で確認してください: https://github.com/$repo/actions"
}
```

#### 方法3: ブラウザで確認

- GitHub Actionsのページを開く: `https://github.com/{repo}/actions`
- 最新のワークフロー実行を確認

### 4. 完了待機（実行中の場合）

**ワークフローが実行中（`status: "in_progress"`または`status: "queued"`）の場合**:

- **必ず完了するまで待機する**（最大20分程度、通常は5-10分）
- `gh run watch <run-id> --exit-status --interval 10` で対象runを待機する
- `status: "completed"`になるまで待機を継続する

### 5. 結果の確認（完了後）

**ワークフローが完了（`status: "completed"`）したら**:

- **必ず結果を確認する**:
  - `conclusion: "success"`の場合: 対象ジョブが成功したことを確認する。\
    **FishTrack / MyPokedex の main push** では **lint / test のみ**（deploy は skipped が正常）。\
    緊急デプロイと 03:00 定時では **deploy 成功**まで見る。
  - `conclusion: "failure"`または`conclusion: "cancelled"`の場合: **エラー内容を確認し、報告する**
- 失敗している場合は、エラー内容を確認し、必要に応じて修正を行う

### 6. 確認完了まで作業を終了しない

**重要**:

- **GitHub Actionsの確認をスキップしてはならない**
- **完了まで待機し、結果を確認することは必須**
- **失敗した場合は、エラー内容を確認して報告すること**
- **確認が完了するまで、作業を終了しないこと**

## リポジトリ別の確認ポイント

### otayori-navi

- **確認対象**: lint、test、deployジョブ
- **通常の実行時間**: 5-10分
- **確認URL**: <https://github.com/aki-nagatani/otayori-navi/actions>

### FishTrack

- **確認対象**: lint、testジョブ（**push では deploy しない**。本番は毎日 03:00 JST。緊急は `FishTrack_emergency-deploy`）
- **通常の実行時間**: 3-8分
- **確認URL**: <https://github.com/aki-nagatani/FishTrack/actions>

### MyPokedex

- **確認対象**: lint、testジョブ（**push では deploy しない**。本番は毎日 03:00 JST。緊急は `MyPokedex_emergency-deploy`）
- **通常の実行時間**: 3-8分
- **確認URL**: <https://github.com/aki-nagatani/MyPokedex/actions>

## エラーハンドリング

### GitHub CLIがインストールされていない場合

- GitHub CLIをインストール: <https://cli.github.com/>
- または、GitHub APIまたはブラウザでの確認方法を使用

### GitHub CLIで認証エラーが発生する場合

- `gh auth login` を実行して認証を設定
- または、GitHub APIまたはブラウザでの確認方法を使用

### GitHub APIが404を返す場合

- リポジトリ名が正しいか確認
- プライベートリポジトリの場合は認証が必要な可能性がある
- GitHub CLIまたはブラウザで手動確認を推奨

### タイムアウトした場合

- 最大待機時間（20分）を超過した場合は、手動で確認
- 長時間実行中の場合は、GitHub Actionsのページで直接確認

### ワークフローが失敗した場合

- エラーログを確認
- 失敗したジョブの詳細を確認
- 必要に応じて修正を実施

## 実行ルール

- **このSKILLを呼び出すタイミング**: プッシュやマージ完了後、即座に呼び出す
- **確認方法の優先順位**:
  1. GitHub CLI（`gh`コマンド）が使用可能な場合は最優先
  2. GitHub API（公開リポジトリの場合）
  3. ブラウザでの手動確認
- **確認をスキップする場合**: なし（必ず確認する）
- **作業完了の条件**: GitHub Actionsが成功（`conclusion: "success"`）するまで確認を継続する
