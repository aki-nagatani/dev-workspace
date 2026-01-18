# 本番DB操作スキル（MyPokedex / FishTrack 共通）

## 概要
MyPokedexおよびFishTrackの本番環境（AWS RDS）のデータベースに、EC2インスタンス経由でアクセスする方法を提供します。

## 接続情報

### MyPokedex
| 項目 | 値 |
|------|-----|
| SSH鍵ファイル | `C:\Users\Akihide\.ssh\mypokedex_ec2_key` |
| EC2ホスト | `ec2-user@18.179.162.82` |
| EC2上のアプリパス | `/home/ec2-user/MyPokedex` |
| Dockerコンテナ名 | `mypokedex-app-1` |
| アプリモジュール | `mypokedex` |
| ファクトリ関数 | `createApp` |

### FishTrack
| 項目 | 値 |
|------|-----|
| SSH鍵ファイル | `C:\Users\Akihide\.ssh\fishtrack_ec2_key` |
| EC2ホスト | `ec2-user@52.197.69.195` |
| EC2上のアプリパス | `/home/ec2-user/FishTrack` |
| Dockerコンテナ名 | `fishtrack-app-1` |
| アプリモジュール | `fishtrack` |
| ファクトリ関数 | `create_app` |

## 接続方法

### 方法1: 簡単なクエリ（SSHコマンド直接実行）

```powershell
# MyPokedex
ssh -i "C:\Users\Akihide\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no ec2-user@18.179.162.82 "cd /home/ec2-user/MyPokedex && docker exec mypokedex-app-1 python -c 'Pythonコード'"

# FishTrack
ssh -i "C:\Users\Akihide\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195 "cd /home/ec2-user/FishTrack && docker exec fishtrack-app-1 python -c 'Pythonコード'"
```

**注意**: PowerShellでは複雑なPythonコードのエスケープが困難なため、簡単なクエリのみ推奨。

### 方法2: スクリプトファイル経由（推奨）

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
   scp -i "C:\Users\Akihide\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no "D:\OneDrive\git_work\MyPokedex\scripts\my_script.py" ec2-user@18.179.162.82:/home/ec2-user/MyPokedex/scripts/
   
   # FishTrack
   scp -i "C:\Users\Akihide\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no "D:\OneDrive\git_work\FishTrack\scripts\my_script.py" ec2-user@52.197.69.195:/home/ec2-user/FishTrack/scripts/
   ```

3. **EC2上でスクリプト実行**
   ```powershell
   # MyPokedex
   ssh -i "C:\Users\Akihide\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no ec2-user@18.179.162.82 "cd /home/ec2-user/MyPokedex && docker exec mypokedex-app-1 python scripts/my_script.py"
   
   # FishTrack
   ssh -i "C:\Users\Akihide\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195 "cd /home/ec2-user/FishTrack && docker exec fishtrack-app-1 python scripts/my_script.py"
   ```

4. **スクリプト削除（必要に応じて）**
   ```powershell
   # MyPokedex - ローカル
   Remove-Item "D:\OneDrive\git_work\MyPokedex\scripts\my_script.py"
   # MyPokedex - EC2
   ssh -i "C:\Users\Akihide\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no ec2-user@18.179.162.82 "rm /home/ec2-user/MyPokedex/scripts/my_script.py"
   
   # FishTrack - ローカル
   Remove-Item "D:\OneDrive\git_work\FishTrack\scripts\my_script.py"
   # FishTrack - EC2
   ssh -i "C:\Users\Akihide\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195 "rm /home/ec2-user/FishTrack/scripts/my_script.py"
   ```

## 利用可能なモデル

### MyPokedex
- `mypokedex.models.user.User` - ユーザー
- `mypokedex.models.game_title.GameTitle` - ゲームタイトル
- `mypokedex.models.party.Party`, `PartyMember` - パーティ
- `mypokedex.models.pokemon.Pokemon` - ポケモン
- `mypokedex.models.dex_entry.DexEntry` - 図鑑エントリ
- `mypokedex.models.regist.Regist` - 登録データ
- `mypokedex.models.user_game_setting.UserGameSetting` - ユーザーゲーム設定

### FishTrack
- `fishtrack.models.User` - ユーザー
- `fishtrack.models.FishingRecord` - 釣果記録
- `fishtrack.models.FishSpecies` - 魚種
- `fishtrack.models.FishingSpot` - 釣り場
- `fishtrack.models.Tackle` - タックル

## 注意事項

1. **本番DBへの書き込みは慎重に** - 必ずバックアップを確認してから実行
2. **タイムアウト** - 長時間かかる操作はタイムアウトする可能性あり
3. **スクリプトの削除** - 一時的なスクリプトは実行後に削除すること
4. **ローカルDBとの混同注意** - docker-compose.ymlの設定により、ローカル環境は共有DBに接続している場合がある
5. **アプリ名の違い** - MyPokedexは`createApp`、FishTrackは`create_app`（スネークケース）

## 関連ドキュメント

### MyPokedex
- `MyPokedex/docs/deployment/DEPLOYMENT_AWS.md` - AWSデプロイ手順
- `MyPokedex/docs/deployment/PRODUCTION_DATA_IMPORT.md` - 本番データインポート手順
- `MyPokedex/docs/deployment/ROLLBACK_PLAN.md` - ロールバック手順

### FishTrack
- `FishTrack/docs/deployment/DEPLOYMENT_AWS.md` - AWSデプロイ手順
