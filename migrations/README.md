# dev-workspace マイグレーション（レガシー）

**1RDS 3DB Phase 2 分離後、FishTrack と MyPokedex は各プロジェクト配下でマイグレーションを管理します。**

## 現状の役割

| DB | マイグレーション配置 | 実行方法 |
|----|----------------------|----------|
| **fishtrack_db** | `FishTrack/migrations/` | `cd FishTrack && alembic upgrade head` |
| **mypokedex_db** | `MyPokedex/migrations/` | `cd MyPokedex && alembic upgrade head` |
| **otayori_navi** | `otayori-navi/migrations/` | `cd otayori-navi && alembic -c migrations/alembic.ini upgrade head` |
| **shared_db** | 本ディレクトリ（レガシー） | 旧統合DB用。新規開発では使用しない |

## 本ディレクトリの用途

- **shared_db** が残っている環境でのみ使用（Phase 2 移行前、またはロールバック時）
- 新規マイグレーションは各プロジェクト（FishTrack/migrations, MyPokedex/migrations）に追加すること

## 環境変数

- `FISHTRACK_DATABASE_URL`: FishTrack 用（fishtrack_db 接続時）
- `MYPDEX_DATABASE_URL`: MyPokedex 用（mypokedex_db 接続時）
- `SHARED_DATABASE_URL`: 旧 shared_db 接続時
