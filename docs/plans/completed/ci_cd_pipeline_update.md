# CI/CDパイプライン更新記録（2025-11-28）

## 概要
- FishTrack と MyPokedex の各リポジトリで `ci.yml` を統合管理し、CI（lint/test）と CD（deploy / rollback）を単一ワークフローにまとめた。
- 本番分割後の初回デプロイ（2025-11-26）から self-hosted runner 経由の GitHub Actions を唯一のデプロイ経路とし、手動SSHは障害対応時のみとする。
- デプロイジョブは `rsync` ベースの差分転送 → 依存関係の整備 → Alembic適用 → `current` シンボリックリンク更新 → systemd再起動 → ヘルスチェック を自動化。

## FishTrack リポジトリ
### ワークフロー構成
| ジョブ名 | 目的 | トリガー |
| --- | --- | --- |
| `lint` / `test` | flake8 / black / isort / pytest（`--cov=fishtrack --cov-fail-under=99`） | `push` / `pull_request` / `workflow_dispatch` |
| `deploy_fishtrack` | `/home/pi/FishTrack/releases/<sha>` への展開と `fishtrack.service` 再起動 | `push` (main) / `workflow_dispatch` |
| `rollback_fishtrack` | 直前コミットへ `current` を張り替えて systemd をロールバック | `workflow_dispatch` |

### デプロイ手順（ジョブ内ステップ）
1. `actions/checkout@v4`
2. `rsync` でリポジトリを `/home/pi/FishTrack/releases/${GITHUB_SHA}` に同期（`.venv`, `data` などは除外）
3. SSH 経由で以下を順次実行  
   - `pip install -r requirements.txt`（venvキャッシュを利用）  
   - `alembic upgrade head`  
   - `ln -sfn releases/${GITHUB_SHA} current`
4. `sudo systemctl restart fishtrack` → `sudo systemctl status --no-pager fishtrack`
5. `curl https://www.yume-eita.com/fishtrack/healthz || true` で外形監視（現在は404を許容）

### 必須 Secrets
| Secret | 用途 |
| --- | --- |
| `FISHTRACK_SSH_HOST`, `FISHTRACK_SSH_USER`, `FISHTRACK_SSH_KEY`, `FISHTRACK_SSH_PASSPHRASE` | self-hosted runner → 本番サーバーへのSSH |
| `FISHTRACK_SECRET_KEY`, `FISHTRACK_DATABASE_URL`, `FISHTRACK_ENABLE_SELF_REGISTER` | `.env` テンプレート生成と CI 実行時の環境変数 |

## MyPokedex リポジトリ
### ワークフロー構成
| ジョブ名 | 目的 | トリガー |
| --- | --- | --- |
| `lint` / `test` | flake8 / black / isort / pytest（`--cov=mypokedex --cov-fail-under=99`） | `push` / `pull_request` / `workflow_dispatch` |
| `deploy_mypokedex` | `/home/pi/MyPokedex/releases/<sha>` への展開と `mypokedex.service` 再起動 | `push` (main) / `workflow_dispatch` |
| `rollback_mypokedex` | 直前コミットへ `current` を張り替えて systemd をロールバック | `workflow_dispatch` |

### デプロイ手順（ジョブ内ステップ）
FishTrack と同一フローで、対象ディレクトリ・サービス名・ヘルスチェックURLのみ `MyPokedex` 用に切り替え。`curl https://www.yume-eita.com/mypokedex/healthz` は `ok` を期待し、失敗時はジョブをエラー扱いにする。

### 必須 Secrets
| Secret | 用途 |
| --- | --- |
| `MYPDEX_SSH_HOST`, `MYPDEX_SSH_USER`, `MYPDEX_SSH_KEY`, `MYPDEX_SSH_PASSPHRASE` | self-hosted runner → 本番サーバーへのSSH |
| `MYPDEX_SECRET_KEY`, `MYPDEX_DATABASE_URL`, `ENABLE_SELF_REGISTER` | `.env` テンプレート生成と CI 実行時の環境変数 |

## 共通運用ガイド
- Runner: Raspberry Pi 上の self-hosted runner（ラベル `self-hosted, linux, MyHobbySite`）を共有。
- タグ付け: `workflow_dispatch` の入力で `target_commit` と `reason` を記録し、Slack通知と一致させる。
- ロールバック: `rollback_*` ジョブは `current.previous` シンボリックリンクを参照した単純復旧。データベースのロールバックは別途手順書に従う。
- 監査: デプロイ結果は `FishTrack/docs/deployment/DEPLOYMENT.md` / `MyPokedex/docs/deployment/DEPLOYMENT.md` の運用ログ欄に追記する。

## 今後の保守項目
1. GitHub Actions キャッシュ肥大化を避けるため、`actions/cache` で `pip` キャッシュTTLを30日に設定。
2. `deploy_*` 失敗時は `rollback_*` を即時実行せず、状況に応じて `workflow_dispatch` で手動判断。
3. Runner障害時の代替として、将来的に `dev-workspace` に dockerized runner を追加する計画を Phase 5 で検討する。

