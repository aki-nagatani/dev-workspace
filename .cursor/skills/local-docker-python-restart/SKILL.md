---
name: local-docker-python-restart
description: >-
  docker compose でアプリ（Gunicorn / uWSGI 等）をローカル起動しているとき、
  アプリ用 Python（例: src/ 配下の *.py）を変更したら検証・報告前に必ず該当サービスを再起動する。
  FishTrack / MyPokedex / otayori-navi に限らずワークスペース共通。サービス名の決め方・例外・再ビルド境界の正本。
---

# ローカル Docker：Python 変更後のアプリ再起動（local-docker-python-restart）

**ワークスペース全体の統一ルール**（特定プロダクト専用ではない）。**myrules** の「ローカル Docker と Python ソース変更」と**同一趣旨**で、**手順・チェックリストの正本は本 SKILL** とする。

## 発火条件（いずれか）

- **`src/`・`tests/` 以外を含む**、アプリランタイムが読み込む **`*.py`** を **`StrReplace` / `Write` 等で変更**した（またはシェルで当該リポの Python を書き換えた）。
- **ローカルで `docker compose`（または `docker compose -f …`）によりアプリコンテナが起動中**であることが分かる、または起動している前提で検証する場合。

## 必須アクション（省略禁止）

1. **当該リポジトリのルート**（`docker-compose.yml` があるディレクトリ）に移動する。
2. そのリポの **`docker-compose.yml`（および override があればそれも）** を確認し、**アプリ用 Python を実行しているサービス名**を特定する（多くは **`app`**。複数サービスがある場合は**変更の影響が及ぶものすべて**）。
3. ローカルで Compose が動いていれば、**検証・ユーザー報告の前に** **`docker compose restart <サービス名>`** を実行する（例: **`docker compose restart app`**）。
4. **複数リポ**で同じセッションに触れた場合は、**Python を変えた各リポ**でそれぞれ必要なら再起動する。

5. **`ai-local-spec-check`**（**`dump_spec_import_preview.py`**）で続けて検証するときは、**dump 系コマンドより前に**上記 **restart** を済ませる（**`ai-local-spec-check` SKILL** の **「見逃し禁止」**・**「Python 変更と dump 前の再起動」**）。**ユーザーへの確認だけで代用しない**。

**手順の提示だけで終えない**（エージェントはターミナルで実行する）。

## サービス名の決め方

- **正本は各リポジトリの `docker-compose.yml`** の `services:`。`build` / `command` がアプリ（Flask/Gunicorn 等）になっているサービスを選ぶ。
- **不明なとき**: リポの **README** または **AGENTS.md** のローカル Docker 記述を優先する。
- **FishTrack / MyPokedex / otayori-navi** の多くのローカル手順では **`app`** がアプリサービス（**`docker compose restart app`** が典型）。

## 再ビルドが主なとき（restart だけでは足りない）

次の変更では **`docker compose build`** → **`up -d`**（またはプロジェクト手順の compose 更新）を正とし、**`restart` だけにしない**。

- **`Dockerfile`** / ベースイメージの変更
- **`requirements.txt`** / **`pyproject.toml`** の依存追加・更新で、イメージ内の **`pip install`** が必要なもの

## 例外（再起動が原則不要になりうるもの）

- **コンテナ内で `--reload` 付きの開発サーバのみ**を運用している構成では、ホットリロードが効くことがある。**本番相当の Gunicorn 既定 CMD** では当てにしない。
- **Python を一切変えていない**（ドキュメントのみ・フロントのみ・DB のみ等）場合は本 SKILLの対象外。

## 関連

- **DB マイグレーション**（Alembic 等）: **`local-docker-db-migrate`** SKILL。アプリ**再起動**と混同しない。
- **各リポ AGENTS.md**: プロダクト固有の一行（例: サービス名が `app` で固定のとき）を参照してよい。
