# 本番EC2接続・DB操作スキル（MyPokedex / FishTrack 共通）

## 概要

MyPokedexおよびFishTrackの本番EC2インスタンスへの接続方法と、本番データベース（AWS RDS）へのアクセス方法を提供します。

## 重要: 正しいEC2インスタンスの確認

**接続前に必ず正しいインスタンスを確認してください。**

各プロジェクトには複数のEC2インスタンスが存在する場合があります。停止中のインスタンスや古いインスタンスに接続しないよう注意が必要です。

### 現在の本番インスタンス情報

#### 本番インスタンス（MyPokedex）

| 項目 | 値 | 備考 |
| --- | --- | --- |
| **本番インスタンスID** | `i-023a1623e48cabf1d` | **現在稼働中** |
| **本番IPアドレス** | `54.249.50.253` | **デプロイ先** |
| EC2上のアプリパス | `/home/ec2-user/MyPokedex` | |
| Dockerコンテナ名 | `mypokedex-app-1` | |
| アプリモジュール | `mypokedex` | |
| ファクトリ関数 | `createApp` | |

#### 本番インスタンス（FishTrack）

| 項目 | 値 | 備考 |
| --- | --- | --- |
| **本番インスタンスID** | `i-05e573f245ca9e2d1` | **現在稼働中** |
| **本番IPアドレス** | `52.197.69.195` | **デプロイ先** |
| EC2上のアプリパス | `/home/ec2-user/FishTrack` | |
| Dockerコンテナ名 | `fishtrack-app-1` | |
| アプリモジュール | `fishtrack` | |
| ファクトリ関数 | `create_app` | |

### インスタンス情報の確認方法

GitHub Secretsの`*_EC2_HOST`に設定されているIPアドレスが正しい本番インスタンスです。

```powershell
# MyPokedex
gh secret list --repo aki-nagatani/MyPokedex | Select-String "EC2"

# FishTrack
gh secret list --repo aki-nagatani/FishTrack | Select-String "EC2"
```

または、deploy.ymlのコメントを確認：

```yaml
# deploy.yml内のコメント例
# Current running instance: i-023a1623e48cabf1d (54.249.50.253)
# Stopped instance: i-0b816de830482d542 (18.179.162.82) - DO NOT USE
```

## 接続方法

### 方法1: AWS Systems Manager (Session Manager) 経由（推奨）

**Session Managerを使用する利点：**

- SSH鍵の管理が不要
- セキュリティグループでSSHポート（22）を開放する必要がない
- 接続ログがCloudTrailに記録される
- IAM権限で接続を制御可能

#### 前提条件

- AWS CLIがインストール済み
- Session Managerプラグインがインストール済み
- 適切なIAM権限を持つプロファイルが設定済み

#### 対話型セッション（推奨）

```powershell
# MyPokedex
aws ssm start-session --target i-023a1623e48cabf1d

# FishTrack
aws ssm start-session --target i-05e573f245ca9e2d1
```

セッション開始後：

```bash
# ec2-userに切り替え
sudo su - ec2-user

# アプリディレクトリに移動
cd ~/MyPokedex  # または ~/FishTrack

# 環境変数確認
grep -E 'VERSION|CAPTCHA' .env

# Dockerコンテナ状態確認
docker compose ps

# コンテナ再起動
docker compose --env-file .env down && docker compose --env-file .env up -d
```

#### コマンド実行（SSM Run Command）

単発のコマンド実行に便利です。

```powershell
# MyPokedex - コマンド送信
aws ssm send-command `
  --instance-ids i-023a1623e48cabf1d `
  --document-name "AWS-RunShellScript" `
  --parameters 'commands=["cd /home/ec2-user/MyPokedex && cat .env | grep VERSION"]' `
  --output json

# FishTrack - コマンド送信
aws ssm send-command `
  --instance-ids i-05e573f245ca9e2d1 `
  --document-name "AWS-RunShellScript" `
  --parameters 'commands=["cd /home/ec2-user/FishTrack && cat .env | grep VERSION"]' `
  --output json

# 結果取得（CommandIdを指定）
aws ssm get-command-invocation --command-id <CommandId> --instance-id <InstanceId> --output json
```

### 方法2: SSH接続（Session Managerが使用できない場合）

**注意**: SSH接続を使用する場合は、必ず正しいIPアドレスを確認してください。

#### SSH鍵ファイル

| プロジェクト | SSH鍵ファイル |
| --- | --- |
| MyPokedex | `C:\Users\Akihide\.ssh\mypokedex_ec2_key` |
| FishTrack | `C:\Users\Akihide\.ssh\fishtrack_ec2_key` |

#### 接続コマンド

```powershell
# MyPokedex（正しいインスタンス）
ssh -i "C:\Users\Akihide\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no ec2-user@54.249.50.253

# FishTrack
ssh -i "C:\Users\Akihide\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195
```

#### 単発コマンド実行

```powershell
# MyPokedex - 環境変数確認
ssh -i "C:\Users\Akihide\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no ec2-user@54.249.50.253 "grep -E 'VERSION|CAPTCHA' /home/ec2-user/MyPokedex/.env"

# FishTrack - 環境変数確認
ssh -i "C:\Users\Akihide\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195 "grep VERSION /home/ec2-user/FishTrack/.env"
```

**注意**: PowerShellでは複雑なコマンドのエスケープが困難なため、対話型セッションまたはSession Managerの使用を推奨。

### 方法3: スクリプトファイル経由（複雑な操作向け）

複雑な操作の場合は、スクリプトファイルを作成してEC2に転送・実行する方法を推奨。

#### MyPokedex用スクリプトテンプレート

```python
# scripts/my_script.py
#!/usr/bin/env python
import sys
sys.path.insert(0, "src")

from mypokedex import createApp
from mypokedex.extensions import db
# 必要なモデルをインポート
from mypokedex.models.game_title import GameTitle

app = createApp()
with app.app_context():
    # ここにDB操作を記述
    games = GameTitle.query.all()
    for g in games:
        print(f"{g.id}: {g.key} ({g.nameJa})")
```

#### FishTrack用スクリプトテンプレート

```python
# scripts/my_script.py
#!/usr/bin/env python
import sys
sys.path.insert(0, "src")

from fishtrack import create_app
from fishtrack.extensions import db
# 必要なモデルをインポート
from fishtrack.models import User

app = create_app()
with app.app_context():
    # ここにDB操作を記述
    users = User.query.all()
    for u in users:
        print(f"{u.id}: {u.username}")
```

#### 実行手順

1. **ローカルでスクリプト作成**（上記テンプレートを参考）

2. **EC2にスクリプト転送**

   ```powershell
   # MyPokedex
   scp -i "C:\Users\Akihide\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no "D:\OneDrive\git_work\MyPokedex\scripts\my_script.py" ec2-user@54.249.50.253:/home/ec2-user/MyPokedex/scripts/
   
   # FishTrack
   scp -i "C:\Users\Akihide\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no "D:\OneDrive\git_work\FishTrack\scripts\my_script.py" ec2-user@52.197.69.195:/home/ec2-user/FishTrack/scripts/
   ```

3. **EC2上でスクリプト実行**

   ```powershell
   # MyPokedex
   ssh -i "C:\Users\Akihide\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no ec2-user@54.249.50.253 "cd /home/ec2-user/MyPokedex && docker exec mypokedex-app-1 python scripts/my_script.py"
   
   # FishTrack
   ssh -i "C:\Users\Akihide\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195 "cd /home/ec2-user/FishTrack && docker exec fishtrack-app-1 python scripts/my_script.py"
   ```

4. **スクリプト削除（必要に応じて）**

   ```powershell
   # MyPokedex - ローカル
   Remove-Item "D:\OneDrive\git_work\MyPokedex\scripts\my_script.py"
   # MyPokedex - EC2
   ssh -i "C:\Users\Akihide\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no ec2-user@54.249.50.253 "rm /home/ec2-user/MyPokedex/scripts/my_script.py"
   
   # FishTrack - ローカル
   Remove-Item "D:\OneDrive\git_work\FishTrack\scripts\my_script.py"
   # FishTrack - EC2
   ssh -i "C:\Users\Akihide\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195 "rm /home/ec2-user/FishTrack/scripts/my_script.py"
   ```

## よく使う操作

### 環境変数の確認・更新

```bash
# Session Manager接続後
cd ~/MyPokedex  # または ~/FishTrack

# 環境変数確認
cat .env

# 環境変数追加
echo "NEW_VAR=value" >> .env

# 環境変数更新（既存の値を置換）
sed -i 's|^OLD_VAR=.*|OLD_VAR=new_value|' .env

# Dockerコンテナ再起動（環境変数反映）
docker compose --env-file .env down && docker compose --env-file .env up -d
```

### Dockerコンテナ操作

```bash
# コンテナ状態確認
docker compose ps

# コンテナログ確認
docker compose logs app --tail 100

# コンテナ再起動
docker compose --env-file .env restart app

# コンテナ完全再起動（環境変数反映）
docker compose --env-file .env down && docker compose --env-file .env up -d

# コンテナ内でコマンド実行
docker exec mypokedex-app-1 python -c "print('hello')"
```

### Git操作

```bash
# 現在のバージョン確認
git log --oneline -1

# リモートとの差分確認
git fetch origin main
git log --oneline HEAD..origin/main
```

## 利用可能なモデル

### MyPokedex のモデル一覧

- `mypokedex.models.user.User` - ユーザー
- `mypokedex.models.game_title.GameTitle` - ゲームタイトル
- `mypokedex.models.party.Party`, `PartyMember` - パーティ
- `mypokedex.models.pokemon.Pokemon` - ポケモン
- `mypokedex.models.dex_entry.DexEntry` - 図鑑エントリ
- `mypokedex.models.regist.Regist` - 登録データ
- `mypokedex.models.user_game_setting.UserGameSetting` - ユーザーゲーム設定

### FishTrack のモデル一覧

- `fishtrack.models.User` - ユーザー
- `fishtrack.models.FishingRecord` - 釣果記録
- `fishtrack.models.FishSpecies` - 魚種
- `fishtrack.models.FishingSpot` - 釣り場
- `fishtrack.models.Tackle` - タックル

## 注意事項

1. **正しいインスタンスの確認** - 接続前に必ず本番インスタンスのIPアドレス/IDを確認すること。停止中や古いインスタンスに接続しないこと
2. **Session Managerの使用を推奨** - セキュリティとログ記録の観点からSession Managerの使用を推奨
3. **本番DBへの書き込みは慎重に** - 必ずバックアップを確認してから実行
4. **タイムアウト** - 長時間かかる操作はタイムアウトする可能性あり
5. **スクリプトの削除** - 一時的なスクリプトは実行後に削除すること
6. **ローカルDBとの混同注意** - docker-compose.ymlの設定により、ローカル環境は共有DBに接続している場合がある
7. **アプリ名の違い** - MyPokedexは`createApp`、FishTrackは`create_app`（スネークケース）

## 関連ドキュメント

### MyPokedex の関連ドキュメント

- `MyPokedex/docs/deployment/DEPLOYMENT_AWS.md` - AWSデプロイ手順
- `MyPokedex/docs/deployment/PRODUCTION_DATA_IMPORT.md` - 本番データインポート手順
- `MyPokedex/docs/deployment/ROLLBACK_PLAN.md` - ロールバック手順

### FishTrack の関連ドキュメント

- `FishTrack/docs/deployment/DEPLOYMENT_AWS.md` - AWSデプロイ手順
