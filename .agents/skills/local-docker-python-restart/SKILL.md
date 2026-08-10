---
name: local-docker-python-restart
description: >-
  docker compose でアプリ（Gunicorn / uWSGI 等）をローカル起動しているとき、
  アプリ用 Python（例: src/ 配下の *.py）を変更したら検証・報告前に該当サービスを再起動する。
  **Docker が起動している場合に限る**（未導入・デーモン未起動では restart しない）。
  FishTrack / MyPokedex / otayori-navi に限らずワークスペース共通。サービス名の決め方・例外・再ビルド境界の正本。
---

# ローカル Docker：Python 変更後のアプリ再起動（local-docker-python-restart）

**ワークスペース全体の統一ルール**（特定プロダクト専用ではない）。**myrules** の「ローカル Docker と Python ソース変更」と**同一趣旨**で、**手順・チェックリストの正本は本 SKILL** とする。

## 発火条件（いずれか）

- **`src/`・`tests/` 以外を含む**、アプリランタイムが読み込む **`*.py`** を **`StrReplace` / `Write` 等で変更**した（またはシェルで当該リポの Python を書き換えた）。
- **FishTrack / MyPokedex / otayori-navi** で上記に該当し、**ユーザー向けの完了報告・検証結果の提示**をする直前まで来たとき（**下記「Docker の利用可否」**を満たす場合のみ **restart**）。

## Docker の利用可否（前提）

**`docker compose restart` は、Docker が起動している場合に限り実行する。**

- **起動しているとみなす条件**: シェルで **`docker info`** が**終了コード 0**（デーモン応答あり）。代替として **`docker compose version`** が 0 でもよい。
- **restart 対象外**（**試行不要**）:
  - **`docker` コマンドが PATH に無い**（未インストール等）
  - **`docker info` が失敗**（デーモン未起動・権限不足等）
  - ユーザーが **Docker を利用しない環境**であることが分かっているとき
- **対象外時の報告**: ユーザー報告に **「Docker 未起動（または未導入）のため restart を省略」** 等 **1 行**を書く（**沈黙は禁止**）。**Docker のインストールを促さない**（環境方針はユーザーが決める）。
- **起動している場合**: 下記「必須アクション」どおり **restart を実行**し、結果を報告に明記する。

## 省略されやすい主因（再発防止）

**Docker が起動しているのに** **`docker compose restart app` を実行しない**典型は次のとおり。**いずれも禁止**。

1. **検証がホストの `pytest` のみ**で済んだため、ローカル compose と結び付けず **restart を忘れる**（myrules は **依頼の種類にかかわらず** 同一。**ただし Docker 起動時のみ**）。
2. **完了報告の末尾に「任意で restart」と書き、ユーザ任せに降格**する（**Docker 起動時はエージェントが実行**が正本）。
3. **会話要約・長文実装のあと**、ソース変更ターンと報告ターンが分断され **チェックリストから外れる**（**報告直前**に必ず `local-docker-python-restart` を自問する）。

**Docker 未起動・未導入で restart を省略するのは正しい**（上記「利用可否」）。**起動しているのに省略するのは禁止**。

## 必須アクション（Docker 起動時・省略禁止）

1. **「Docker の利用可否」**を満たさないときは **本節 2〜5 をスキップ**し、報告に省略理由 **1 行**のみ書く。
2. **当該リポジトリのルート**（`docker-compose.yml` があるディレクトリ）に移動する。
3. そのリポの **`docker-compose.yml`（および override があればそれも）** を確認し、**アプリ用 Python を実行しているサービス名**を特定する（多くは **`app`**。複数サービスがある場合は**変更の影響が及ぶものすべて**）。
4. **検証・ユーザー報告の前に**、当該リポジトリ直下で **`docker compose restart <サービス名>`** を**ターミナルから実行**する（例: **`docker compose restart app`**）。**失敗した場合**は、**ユーザー報告にエラー要約 1 行**を書く。
5. **複数リポ**で同じセッションに触れた場合は、**Python を変えた各リポ**でそれぞれ必要なら再起動する。

6. **`ai-spec-check-virtual`**／**`ai-spec-import`** で続けて検証するときは、**Docker 起動時**かつ **プレビュー実行前**に上記 **restart** を済ませる（**`local-docker-python-restart`**・**FishTrack AGENTS**）。**ユーザーへの確認だけで代用しない**。

**手順の提示だけで終えない**（**Docker 起動時**はエージェントがターミナルで実行する）。

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
