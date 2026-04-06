# ローカルDocker DBマイグレーション（MyPokedex / FishTrack / otayori-navi）

myrulesを厳守して作業してください。

対象アプリのリポジトリルートで **Docker Compose** の **`app`** サービス内から **Alembic** を実行する（**エージェントがターミナルで実行**する。手順の提示だけで終わらない）。

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

- **Postgres**（通常は `dev-workspace` の **shared-db**）が起動していること。
- Compose の **`shared-db-network`**（`external: true`）が存在すること。
- 各アプリの **README** / **`docker-compose.yml`** に沿い、コンテナから DB に届くこと（環境変数・`.env`）。

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
