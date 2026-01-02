# ローカルDB統合手順

## 概要

ローカル環境のFishTrackとMyPokedexのデータベースを、本番環境と同様に1つの統合データベース（shared-db）に統合する手順です。

## 前提条件

- DockerとDocker Composeがインストールされていること
- 既存のFishTrackとMyPokedexのDockerコンテナが起動していること（データ移行のため）

## 手順

### 1. 統合データベースコンテナの起動

```bash
cd dev-workspace
docker compose --profile local up -d shared-db
```

これにより、以下の設定でPostgreSQLコンテナが起動します：
- **ポート**: 5434（ホスト側）
- **データベース名**: `shared_db`
- **ユーザー名**: `shared_user`
- **パスワード**: `shared_password`

### 2. 既存データのバックアップ（推奨）

統合前に、既存のデータをバックアップしておくことを推奨します。

```bash
# FishTrackのデータをバックアップ
docker exec -t fishtrack-db-1 pg_dump -U fishtrack fishtrack_db > backups/fishtrack_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# MyPokedexのデータをバックアップ
docker exec -t mypokedex-db-1 pg_dump -U mypokedex mypokedex_db > backups/mypokedex_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql
```

### 3. データ移行の実行

統合データベースに既存データを移行します。

```powershell
# PowerShellの場合
cd dev-workspace

# 環境変数を設定
$env:MYPDEX_SOURCE_DATABASE_URL="postgresql://mypokedex:mypokedex_password@localhost:5433/mypokedex_db"
$env:FISHTRACK_SOURCE_DATABASE_URL="postgresql://fishtrack:fishtrack_pass@localhost:5432/fishtrack_db"
$env:SHARED_DATABASE_URL="postgresql://shared_user:shared_password@localhost:5434/shared_db"

# 移行スクリプトを実行
python scripts/migrate_local_to_shared_db.py
```

```bash
# Bashの場合
cd dev-workspace

# 環境変数を設定
export MYPDEX_SOURCE_DATABASE_URL="postgresql://mypokedex:mypokedex_password@localhost:5433/mypokedex_db"
export FISHTRACK_SOURCE_DATABASE_URL="postgresql://fishtrack:fishtrack_pass@localhost:5432/fishtrack_db"
export SHARED_DATABASE_URL="postgresql://shared_user:shared_password@localhost:5434/shared_db"

# 移行スクリプトを実行
python scripts/migrate_local_to_shared_db.py
```

### 4. ネットワークの統合

統合DBコンテナを起動すると、`shared-db-network`が作成されます。FishTrackとMyPokedexのアプリコンテナを、このネットワーク経由で統合DBにアクセスできるように設定します。

#### 4.1 docker-compose.ymlの更新

各アプリの`docker-compose.yml`の`app`サービスの`networks`セクションに`shared-db-network`を追加します。

**FishTrack/docker-compose.yml**:
```yaml
services:
  app:
    # ... 他の設定 ...
    networks:
      - fishtrack-net
      - shared-db-network  # 追加
```

**MyPokedex/docker-compose.yml**:
```yaml
services:
  app:
    # ... 他の設定 ...
    networks:
      - mypokedex-network
      - shared-db-network  # 追加
```

**networksセクション**（既に定義されている場合）:
```yaml
networks:
  fishtrack-net:  # または mypokedex-network
    driver: bridge
  shared-db-network:
    name: shared-db-network
    external: true
```

#### 4.2 アプリコンテナの再起動

設定を反映するため、アプリコンテナを再起動します：

```bash
# FishTrackの場合
cd FishTrack
docker compose up -d app

# MyPokedexの場合
cd MyPokedex
docker compose up -d app
```

#### 4.3 ネットワーク接続の確認

以下のコマンドで、アプリコンテナが`shared-db-network`に接続されているか確認します：

```bash
docker network inspect shared-db-network --format '{{range .Containers}}{{.Name}} {{end}}'
```

出力に`dev-workspace-shared-db-1`、`fishtrack-app-1`、`mypokedex-app-1`が含まれていれば正常です。

### 5. 環境変数の設定

統合データベースを使用するように、各アプリの環境変数を設定します。

#### 方法1: .envファイルで永続化（推奨）

各アプリの`.env`ファイルにデータベースURLを設定することで、環境変数を永続化できます。

**FishTrack/.env**:
```env
# ローカル統合データベース（shared-db）への接続
# docker-compose.ymlのデフォルト値（本番RDS）を上書きします
FISHTRACK_DATABASE_URL=postgresql://shared_user:shared_password@shared-db:5432/shared_db
```

**MyPokedex/.env**:
```env
# ローカル統合データベース（shared-db）への接続
# docker-compose.ymlのデフォルト値（本番RDS）を上書きします
MYPDEX_DATABASE_URL=postgresql://shared_user:shared_password@shared-db:5432/shared_db
```

**注意**: 
- `.env`ファイルは`.gitignore`で管理されているため、Gitにコミットされません
- `shared-db`はコンテナ名です。Dockerネットワーク内では、コンテナ名で接続できます
- `.env`ファイルを変更した後は、`docker compose up -d app`でアプリコンテナを再起動してください

#### 方法1-2: セッション単位の環境変数（一時的）

一時的に環境変数を設定する場合（現在のセッションでのみ有効）：

```powershell
# PowerShellの場合
$env:FISHTRACK_DATABASE_URL="postgresql://shared_user:shared_password@shared-db:5432/shared_db"
$env:MYPDEX_DATABASE_URL="postgresql://shared_user:shared_password@shared-db:5432/shared_db"
```

```bash
# Bashの場合
export FISHTRACK_DATABASE_URL="postgresql://shared_user:shared_password@shared-db:5432/shared_db"
export MYPDEX_DATABASE_URL="postgresql://shared_user:shared_password@shared-db:5432/shared_db"
```

**注意**: この方法は現在のセッションでのみ有効です。新しいセッションでは再設定が必要です。

#### 方法2: docker-compose.ymlのデフォルト値を変更

各アプリのdocker-compose.ymlで、デフォルト値を統合DBに変更することも可能です（本番環境のURLを上書きする場合）。

**注意**: 現在のdocker-compose.ymlは本番環境のshared-dbをデフォルトで使用しています。ローカル環境で統合DBを使用する場合は、環境変数で上書きしてください。

### 6. 動作確認

統合後、以下のコマンドでデータが正しく移行されたか、アプリが正常に接続できているか確認します。

#### 6.1 データベースの確認

```bash
# 統合DBに接続
docker exec dev-workspace-shared-db-1 psql -U shared_user -d shared_db

# テーブル一覧を確認
\dt

# レコード数を確認（PowerShellの場合、引用符のエスケープに注意）
docker exec dev-workspace-shared-db-1 psql -U shared_user -d shared_db -c 'SELECT ''MyPokedex'' as app, COUNT(*) as count FROM "User" UNION ALL SELECT ''FishTrack'' as app, COUNT(*) FROM fishtrack_user;'
```

#### 6.2 アプリコンテナの接続確認

```bash
# ネットワーク接続の確認
docker network inspect shared-db-network --format '{{range .Containers}}{{.Name}} {{end}}'
# 出力に dev-workspace-shared-db-1, fishtrack-app-1, mypokedex-app-1 が含まれていれば正常

# データベース接続テスト（FishTrack）
docker exec fishtrack-app-1 python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://shared_user:shared_password@shared-db:5432/shared_db'); conn = engine.connect(); print('Connection successful!'); conn.close()"

# データベース接続テスト（MyPokedex）
docker exec mypokedex-app-1 python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://shared_user:shared_password@shared-db:5432/shared_db'); conn = engine.connect(); print('Connection successful!'); conn.close()"
```

#### 6.3 アプリケーションの動作確認

ブラウザで以下のURLにアクセスして、アプリが正常に動作しているか確認します：

- **FishTrack**: http://localhost:5001
- **MyPokedex**: http://localhost:5002

アプリが正常に動作し、データベースからデータを取得できていれば統合は成功です。

## 注意事項

1. **既存データの保持**: 統合後も、元のFishTrackとMyPokedexのデータベースコンテナは停止せずに保持しておくことを推奨します（バックアップとして）。

2. **ポート番号**: 
   - FishTrack DB: 5432
   - MyPokedex DB: 5433
   - 統合DB: 5434

3. **マイグレーション**: 統合後は、`dev-workspace`のマイグレーションを使用してスキーマを管理します。

4. **環境変数**: 各アプリの環境変数で統合DBのURLを指定するか、docker-compose.ymlのデフォルト値を更新してください。

## トラブルシューティング

### 接続エラーが発生する場合

#### エラー: "could not translate host name 'shared-db' to address"

このエラーは、アプリコンテナが`shared-db-network`に接続されていない場合に発生します。

**対処法**:

1. アプリコンテナが`shared-db-network`に接続されているか確認：
   ```bash
   docker network inspect shared-db-network --format '{{range .Containers}}{{.Name}} {{end}}'
   ```
   `fishtrack-app-1`と`mypokedex-app-1`が含まれていない場合は、手順4を実行してください。

2. `docker-compose.yml`の`networks`セクションを確認：
   - `app`サービスの`networks`に`shared-db-network`が含まれているか確認
   - `networks`セクションで`shared-db-network`が`external: true`で定義されているか確認

3. アプリコンテナを再起動：
   ```bash
   cd FishTrack  # または MyPokedex
   docker compose up -d app
   ```

#### その他の接続エラー

1. 統合DBコンテナが起動しているか確認：
   ```bash
   docker compose --profile local ps shared-db
   ```

2. ネットワークが正しく設定されているか確認：
   ```bash
   docker network ls
   docker network inspect shared-db-network
   ```

3. ポートが正しく公開されているか確認：
   ```bash
   docker compose --profile local port shared-db 5432
   ```

4. 環境変数が正しく設定されているか確認：
   ```bash
   # FishTrackの場合
   docker exec fishtrack-app-1 env | grep FISHTRACK_DATABASE_URL
   
   # MyPokedexの場合
   docker exec mypokedex-app-1 env | grep MYPDEX_DATABASE_URL
   ```

5. データベース接続をテスト：
   ```bash
   # FishTrackの場合
   docker exec fishtrack-app-1 python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://shared_user:shared_password@shared-db:5432/shared_db'); conn = engine.connect(); print('Connection successful!'); conn.close()"
   
   # MyPokedexの場合
   docker exec mypokedex-app-1 python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://shared_user:shared_password@shared-db:5432/shared_db'); conn = engine.connect(); print('Connection successful!'); conn.close()"
   ```

### データ移行が失敗する場合

1. ソースDBが起動しているか確認
2. 環境変数が正しく設定されているか確認
3. バックアップから復元して再試行

## ロールバック

統合に問題が発生した場合、元の構成に戻すことができます：

1. FishTrackとMyPokedexのdocker-compose.ymlを元に戻す
2. 各アプリの環境変数を元のDB URLに設定
3. 元のDBコンテナを起動

