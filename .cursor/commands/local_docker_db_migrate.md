# ローカルDocker DBマイグレーション（MyPokedex / FishTrack / otayori-navi）

myrulesを厳守して作業してください。

対象アプリのリポジトリルートで **Docker Compose** の **`app`** サービス内から **Alembic** を実行する（**エージェントがターミナルで実行**する。手順の提示だけで終わらない）。

## 0. ローカルDocker・DBの早見（名称で迷わない）

### Postgres（共有DBコンテナ）の場所

- **定義ファイル**: `dev-workspace/docker-compose.yml` のサービス **`shared-db`**（Compose の **profile `local`** 付き）。
- **起動例**（`dev-workspace` ルート）:

  ```bash
  docker compose --profile local up -d shared-db
  ```

- **Docker ネットワーク名**: **`shared-db-network`**（初回起動で `dev-workspace` の Compose が作成。各アプリの `docker-compose.yml` では `external: true` で同じ名前を参照）。
- **コンテナ間のホスト名**: アプリの `app` から DB へは **`shared-db`**（サービス名。`docker ps` で表示されるコンテナ名 `…-shared-db-1` ではなく、この名前を URL に使う）。
- **ホスト（Windows）から直接 psql 等で繋ぐ場合**: **`localhost:5434`**（コンテナ内の 5432 をホスト 5434 にマッピング。他ローカル Postgres とポート衝突を避けるため）。
- **クラスタログインロール**: ユーザー **`shared_user`** / パスワード **`shared_password`**（`POSTGRES_*` と一致）。
- **イメージ起動時の既定データベース名（`POSTGRES_DB`）**: **`shared_db`**（Postgres の「接続先 DB 名」としての初期 DB。各アプリ用の **論理 DB** はこれと別名）。

### アプリ別・論理DB名と接続URL用の環境変数

マイグレーションは **各アプリが接続する URL の末尾の DB 名** にスキーマを載せる。compose 既定 URL は概ね次のとおり（上書きは各 `.env` / `docker-compose.yml` を正とする）。

| プロダクト | 論理DB名（URL の `/` 以降） | 主な環境変数 | アプリ HTTP（compose 既定の例） |
| --- | --- | --- | --- |
| MyPokedex | `mypokedex_db` | `MYPDEX_DATABASE_URL` | `http://localhost:5002` |
| FishTrack | `fishtrack_db` | `FISHTRACK_DATABASE_URL` | `http://localhost:5001` |
| otayori-navi | `otayori_navi` | ローカルは **`OTAYORI_DB_URL`**（`.env` で `shared-db` を指定。未設定時は本番向け・config 側） | `http://localhost:5003`（既定） |

- **URL 例（コンテナ内から）**: `postgresql://shared_user:shared_password@shared-db:5432/<論理DB名>`
- **URL 例（ホストから）**: `postgresql://shared_user:shared_password@localhost:5434/<論理DB名>`

### よくある勘違い

- **`shared_db` と `mypokedex_db` / `fishtrack_db` は別物**。Alembic は通常 **各アプリの論理DB** を向く（compose の `DATABASE_URL` 既定を確認）。
- **論理DBが未作成**のままだと接続に失敗する。初回のみ `CREATE DATABASE <論理名>` が必要な環境がある（各リポジトリ README・`dev-workspace/scripts` の手順を参照）。
- **otayori-navi** の README に **実コンテナ名**（例: `…-shared-db-1`）が載ることがある。\
    **`app` から接続する DNS 名は `shared-db`**（同一 `shared-db-network`）。

## 1. 対象リポジトリの特定

次のいずれかで **`MyPokedex` / `FishTrack` / `otayori-navi` のルート** を決める。

- ユーザーメッセージ・チャット文脈
- 開いているワークスペース・カレントファイルのパス

曖昧なときだけ、**どれに対して実行するか** を一言確認する。

**作業ディレクトリ例（Windows）**:

- `d:\OneDrive\git_work\MyPokedex`
- `d:\OneDrive\git_work\FishTrack`
- `d:\OneDrive\git_work\otayori-navi`

## 2. 共通前提（不足なら短くユーザーへ）

- **Postgres**（`dev-workspace` の **`shared-db`**）が起動していること（**セクション0** の `docker compose --profile local up -d shared-db`）。
- ネットワーク **`shared-db-network`** が存在すること（各アプリ側 compose は `external: true`。未作成なら `dev-workspace` で shared-db を一度起動するか、`docker network create shared-db-network`）。
- 各アプリの **`app`** が参照する **DB URL**（**セクション0** の論理DB名・環境変数）が、マイグレーションと一致していること（**README** / **`docker-compose.yml`** / **`.env`**）。

## 3. 実行コマンド（リポジトリルートで）

いずれも **`app` を常時起動していなくてよい** 既定形:

```bash
docker compose run --rm app …
```

**`app` がすでに起動している**場合の代替:

```bash
docker compose exec app …
```

### MyPokedex

コンテナの **`WORKDIR` は `/app`**。ルートに **`alembic.ini`** がある。

```bash
docker compose run --rm app alembic upgrade head
```

（`exec` のときも同じく `alembic upgrade head`。本番デプロイと同様の形に揃えるなら\
`sh -c "cd /app && alembic upgrade head"` でもよい。）

### FishTrack

MyPokedex と同じく **`alembic upgrade head`**（`/app`）。

```bash
docker compose run --rm app alembic upgrade head
```

### otayori-navi

専用ラッパー **`scripts/run_migrations.py`** を使う（`migrations/alembic.ini`・補正処理あり）。

```bash
docker compose run --rm app python scripts/run_migrations.py
```

詳細は **`scripts/run_migrations.py` 先頭の docstring** を正とする。

## 4. 結果の報告

標準出力・終了コードを踏まえ、成功／失敗をユーザーに報告する。
