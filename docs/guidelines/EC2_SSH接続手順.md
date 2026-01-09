# EC2へのSSH接続手順書

## 概要

このドキュメントでは、AWS EC2インスタンスへのSSH接続方法を説明します。
FishTrackとMyPokedexの本番環境はそれぞれ別のEC2インスタンスで動作しています。

> **💡 Session Managerについて**
> 
> Session Managerが導入されている場合は、SSHの代わりにSession Managerを使用することを推奨します。
> 
> **Session Managerの利点:**
> - SSH鍵不要
> - インバウンドポート不要
> - IAMによる一元管理
> - セッションログ自動記録
> 
> **使用方法は下記の「Session Manager接続方法」セクションを参照してください。**

## EC2インスタンス情報

### FishTrack EC2

- **ホスト名/IP**: `52.197.69.195`
- **インスタンスID**: `i-0cc5625e58feb39b8`
- **ユーザー名**: `ec2-user`
- **SSH鍵パス**: `$env:USERPROFILE\.ssh\fishtrack_ec2_key` (Windows)
- **SSH鍵パス**: `~/.ssh/fishtrack_ec2_key` (Linux/macOS)

### MyPokedex EC2

- **ホスト名/IP**: `18.179.162.82`
- **インスタンスID**: `i-023a1623e48cabf1d`
- **ユーザー名**: `ec2-user`
- **SSH鍵パス**: `$env:USERPROFILE\.ssh\mypokedex_ec2_key` (Windows)
- **SSH鍵パス**: `~/.ssh/mypokedex_ec2_key` (Linux/macOS)

## 前提条件

### 1. SSH鍵の確認

接続前に、SSH鍵ファイルが存在することを確認してください。

#### Windows (PowerShell)

```powershell
# FishTrack EC2の鍵を確認
Test-Path "$env:USERPROFILE\.ssh\fishtrack_ec2_key"

# MyPokedex EC2の鍵を確認
Test-Path "$env:USERPROFILE\.ssh\mypokedex_ec2_key"
```

#### Linux/macOS

```bash
# FishTrack EC2の鍵を確認
test -f ~/.ssh/fishtrack_ec2_key && echo "存在します" || echo "存在しません"

# MyPokedex EC2の鍵を確認
test -f ~/.ssh/mypokedex_ec2_key && echo "存在します" || echo "存在しません"
```

### 2. SSH鍵のパーミッション確認（Linux/macOSのみ）

Linux/macOSでは、SSH鍵のパーミッションが適切に設定されている必要があります：

```bash
chmod 600 ~/.ssh/fishtrack_ec2_key
chmod 600 ~/.ssh/mypokedex_ec2_key
```

## 基本的な接続方法

### Windows (PowerShell)

#### FishTrack EC2への接続

```powershell
ssh -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195
```

#### MyPokedex EC2への接続

```powershell
ssh -i "$env:USERPROFILE\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no ec2-user@18.179.162.82
```

### Linux/macOS

#### FishTrack EC2への接続

```bash
ssh -i ~/.ssh/fishtrack_ec2_key -o StrictHostKeyChecking=no ec2-user@52.197.69.195
```

#### MyPokedex EC2への接続

```bash
ssh -i ~/.ssh/mypokedex_ec2_key -o StrictHostKeyChecking=no ec2-user@18.179.162.82
```

### 接続オプションの説明

- `-i <鍵ファイルパス>`: 使用するSSH秘密鍵を指定
- `-o StrictHostKeyChecking=no`: 初回接続時のホスト鍵確認をスキップ（セキュリティ警告を抑制）
- `ec2-user@<IP>`: 接続先のユーザー名とIPアドレス

---

## Session Manager接続方法（推奨）

Session Managerは、SSH鍵不要でEC2インスタンスに安全に接続できるAWSのサービスです。

### 前提条件

1. **Session Manager Pluginのインストール**
   - Windows: [SessionManagerPluginSetup.exe](https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe)をダウンロードしてインストール
   - インストール確認: `session-manager-plugin --version`

2. **IAMポリシー**
   - 接続するユーザーに`ssm:StartSession`権限が必要

3. **EC2インスタンス側の設定**
   - IAMロールに`AmazonSSMManagedInstanceCore`ポリシーがアタッチされていること
   - SSM Agentがインストール・実行されていること（Amazon Linux 2023はデフォルトでインストール済み）

### 基本的な接続方法

#### MyPokedex EC2への接続

```bash
aws ssm start-session --target i-023a1623e48cabf1d --region ap-northeast-1
```

#### FishTrack EC2への接続

```bash
aws ssm start-session --target i-0cc5625e58feb39b8 --region ap-northeast-1
```

### セッション終了方法

- `exit` と入力
- または `Ctrl+D` を押す

### Session Managerで実行できる作業

Session Managerは、SSHと同等の操作が可能です：

- ✅ コマンド実行（`ls`, `cd`, `cat`, `grep`, `vim`, `nano`など）
- ✅ ファイル操作（作成、編集、削除、移動、コピー）
- ✅ プロセス管理（`ps`, `top`, `kill`など）
- ✅ システム管理（`systemctl`, `journalctl`など）
- ✅ Docker操作（`docker ps`, `docker exec`, `docker compose`など）
- ✅ ログ確認
- ✅ 設定ファイル編集

### ファイル転送の代替方法

Session Managerでは直接SCP/SFTPは使用できませんが、以下の代替方法があります：

#### 方法1: S3を経由した転送（推奨）

```bash
# ローカルでS3にアップロード
aws s3 cp file.txt s3://your-bucket/temp/file.txt

# Session Managerセッション内でS3からダウンロード
aws s3 cp s3://your-bucket/temp/file.txt /home/ec2-user/file.txt
```

#### 方法2: base64エンコード/デコード（小さいファイル用）

**アップロード:**
```bash
# ローカルでファイルをbase64エンコード
cat file.txt | base64

# Session Managerセッション内で
echo "base64エンコードされた文字列" | base64 -d > file.txt
```

**ダウンロード:**
```bash
# Session Managerセッション内で
cat file.txt | base64

# ローカルでbase64デコード
echo "base64エンコードされた文字列" | base64 -d > file.txt
```

#### 方法3: ポートフォワーディング + ローカルSCP

```bash
# Session Managerでポートフォワーディング（別ターミナルで実行）
aws ssm start-session --target i-023a1623e48cabf1d --region ap-northeast-1 \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["22"],"localPortNumber":["2222"]}'

# 別のターミナルで、ローカルポート経由でSCP
scp -P 2222 -o StrictHostKeyChecking=no file.txt ec2-user@localhost:/home/ec2-user/
```

### ポートフォワーディング

```bash
# リモートポート5002をローカルポート8080に転送
aws ssm start-session --target i-023a1623e48cabf1d --region ap-northeast-1 \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["5002"],"localPortNumber":["8080"]}'
```

### インスタンスの状態確認

```bash
# Managed instancesに表示されているか確認
aws ssm describe-instance-information --region ap-northeast-1 --filters "Key=InstanceIds,Values=i-023a1623e48cabf1d"
```

### Session Managerの利点

- **SSH鍵不要**: 鍵ファイルの管理が不要
- **インバウンドポート不要**: セキュリティグループでSSHポートを開く必要がない
- **IAMによる一元管理**: IAMポリシーでアクセス制御
- **セッションログ自動記録**: すべてのセッション活動が自動記録される
- **セキュリティ向上**: すべての通信がTLS 1.2で暗号化

### Session Manager vs SSH 比較

| 項目 | SSH | Session Manager |
|------|-----|----------------|
| シェルアクセス | ✅ | ✅ |
| コマンド実行 | ✅ | ✅ |
| ファイル操作 | ✅ | ✅ |
| SCP/SFTP転送 | ✅ | ⚠️ 代替方法あり |
| ポートフォワーディング | ✅ | ✅ |
| SSH鍵管理 | 必要 | 不要 |
| インバウンドポート | 必要 | 不要 |
| セッションログ | 手動設定 | 自動記録 |

---

## よく使うコマンド

### 接続テスト

接続が成功すると、EC2インスタンスのシェルプロンプトが表示されます：

```bash
[ec2-user@ip-xxx-xxx-xxx-xxx ~]$
```

### 基本的なコマンド

```bash
# 現在のディレクトリを確認
pwd

# ホームディレクトリに移動
cd ~

# ファイル一覧を表示
ls -la

# システム情報を確認
uname -a

# ディスク使用量を確認
df -h

# メモリ使用量を確認
free -h
```

### dev-workspaceへの移動

```bash
# dev-workspaceディレクトリに移動
cd ~/dev-workspace

# または、FishTrackディレクトリから相対パスで移動
cd ~/FishTrack/../dev-workspace
```

## ファイル転送（scp）

### Windows (PowerShell)

#### ファイルをEC2にアップロード

```powershell
# FishTrack EC2にファイルをアップロード
scp -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no `
  "ローカルファイルパス" `
  "ec2-user@52.197.69.195:/home/ec2-user/リモートファイルパス"

# MyPokedex EC2にファイルをアップロード
scp -i "$env:USERPROFILE\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no `
  "ローカルファイルパス" `
  "ec2-user@18.179.162.82:/home/ec2-user/リモートファイルパス"
```

#### EC2からファイルをダウンロード

```powershell
# FishTrack EC2からファイルをダウンロード
scp -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no `
  "ec2-user@52.197.69.195:/home/ec2-user/リモートファイルパス" `
  "ローカルファイルパス"

# MyPokedex EC2からファイルをダウンロード
scp -i "$env:USERPROFILE\.ssh\mypokedex_ec2_key" -o StrictHostKeyChecking=no `
  "ec2-user@18.179.162.82:/home/ec2-user/リモートファイルパス" `
  "ローカルファイルパス"
```

### Linux/macOS

#### ファイルをEC2にアップロード

```bash
# FishTrack EC2にファイルをアップロード
scp -i ~/.ssh/fishtrack_ec2_key -o StrictHostKeyChecking=no \
  ローカルファイルパス \
  ec2-user@52.197.69.195:/home/ec2-user/リモートファイルパス

# MyPokedex EC2にファイルをアップロード
scp -i ~/.ssh/mypokedex_ec2_key -o StrictHostKeyChecking=no \
  ローカルファイルパス \
  ec2-user@18.179.162.82:/home/ec2-user/リモートファイルパス
```

#### EC2からファイルをダウンロード

```bash
# FishTrack EC2からファイルをダウンロード
scp -i ~/.ssh/fishtrack_ec2_key -o StrictHostKeyChecking=no \
  ec2-user@52.197.69.195:/home/ec2-user/リモートファイルパス \
  ローカルファイルパス

# MyPokedex EC2からファイルをダウンロード
scp -i ~/.ssh/mypokedex_ec2_key -o StrictHostKeyChecking=no \
  ec2-user@18.179.162.82:/home/ec2-user/リモートファイルパス \
  ローカルファイルパス
```

## よく使う作業

### 1. 本番環境のデータベーススキーマ分析

#### SSH接続の場合

```bash
# EC2に接続
ssh -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195

# dev-workspaceに移動
cd ~/dev-workspace

# スキーマ分析スクリプトを実行
bash scripts/analyze_production_db.sh
```

#### Session Manager接続の場合（推奨）

```bash
# EC2に接続
aws ssm start-session --target i-0cc5625e58feb39b8 --region ap-northeast-1

# セッション内で
cd ~/dev-workspace
bash scripts/analyze_production_db.sh
```

分析結果は `~/dev-workspace/docs/db_schema_production.md` に保存されます。

### 2. 分析結果をローカルにダウンロード

#### SSH (SCP)の場合

```powershell
# FishTrack EC2から分析結果をダウンロード
scp -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no `
  ec2-user@52.197.69.195:/home/ec2-user/dev-workspace/docs/db_schema_production.md `
  docs/db_schema_production.md
```

#### Session Managerの場合

**方法1: S3を経由（推奨）**

```bash
# Session Managerセッション内で
aws s3 cp ~/dev-workspace/docs/db_schema_production.md s3://your-bucket/temp/db_schema_production.md

# ローカルでS3からダウンロード
aws s3 cp s3://your-bucket/temp/db_schema_production.md docs/db_schema_production.md
```

**方法2: base64エンコード/デコード**

```bash
# Session Managerセッション内で
cat ~/dev-workspace/docs/db_schema_production.md | base64

# 出力されたbase64文字列をコピーして、ローカルで
echo "base64文字列" | base64 -d > docs/db_schema_production.md
```

### 3. Dockerコンテナの状態確認

**SSHまたはSession Managerセッション内で実行:**

```bash
# 実行中のコンテナを確認
docker ps

# すべてのコンテナ（停止中も含む）を確認
docker ps -a

# コンテナのログを確認
docker logs <コンテナ名>

# 最新の100行のログを確認
docker logs --tail 100 <コンテナ名>
```

### 4. アプリケーションのログ確認

**SSHまたはSession Managerセッション内で実行:**

```bash
# FishTrackのログを確認
cd ~/FishTrack
docker compose logs -f app

# MyPokedexのログを確認
cd ~/MyPokedex
docker compose logs -f app
```

### 5. データベース接続確認

**SSHまたはSession Managerセッション内で実行:**

```bash
# PostgreSQLに接続（shared-db）
psql -h shared-db.cty4osc6gw6k.ap-northeast-1.rds.amazonaws.com \
     -U shared_user \
     -d shared_db

# 接続後、テーブル一覧を確認
\dt

# 特定のテーブルのレコード数を確認
SELECT COUNT(*) FROM fishtrack_user;
```

### 6. 本番環境デプロイ状況の確認

**Session Managerセッション内で実行:**

```bash
# Session Managerで接続
aws ssm start-session --target i-023a1623e48cabf1d --region ap-northeast-1

# セッション内で
cd ~/dev-workspace
export SHARED_DATABASE_URL=$MYPDEX_DATABASE_URL
export PYTHONPATH=/app/src:/app/../dev-workspace:/app/../FishTrack/src:/app/../MyPokedex/src
python3 scripts/check_production_deployment.py
```

## トラブルシューティング

### SSH接続できない場合

#### 1. SSH鍵のパスを確認

```powershell
# Windows
Test-Path "$env:USERPROFILE\.ssh\fishtrack_ec2_key"
```

```bash
# Linux/macOS
ls -la ~/.ssh/fishtrack_ec2_key
```

#### 2. 接続タイムアウト

- EC2インスタンスが起動しているか確認（AWSコンソールで確認）
- セキュリティグループでSSH（ポート22）が許可されているか確認
- ネットワーク接続を確認

#### 3. 認証エラー

- SSH鍵のパーミッションを確認（Linux/macOS: `chmod 600`）
- 正しいSSH鍵を使用しているか確認
- ユーザー名が `ec2-user` であることを確認

#### 4. ホスト鍵の確認エラー

初回接続時にホスト鍵の確認を求められる場合があります。`-o StrictHostKeyChecking=no` オプションを使用することで回避できますが、セキュリティ上のリスクがあるため、本番環境では注意が必要です。

### Session Manager接続できない場合

#### 1. Session Manager Pluginの確認

```powershell
# Windows
session-manager-plugin --version
```

インストールされていない場合は、[SessionManagerPluginSetup.exe](https://s3.amazonaws.com/session-manager-downloads/plugin/latest/windows/SessionManagerPluginSetup.exe)をダウンロードしてインストールしてください。

#### 2. インスタンスがManaged instancesに表示されない

```bash
# インスタンスの状態を確認
aws ssm describe-instance-information --region ap-northeast-1 --filters "Key=InstanceIds,Values=i-023a1623e48cabf1d"
```

**考えられる原因:**
- IAMロールに`AmazonSSMManagedInstanceCore`ポリシーがアタッチされていない
- SSM Agentがインストールされていない、または停止している
- インスタンスがインターネットに接続できていない
- セキュリティグループでアウトバウンド通信が許可されていない

#### 3. セッション開始時にエラーが発生する

**エラー: "User is not authorized to perform: ssm:StartSession"**

- ユーザーのIAMポリシーに`ssm:StartSession`権限があるか確認
- インスタンスIDが正しいか確認

**エラー: "Target instance is not in a valid state"**

- インスタンスが`running`状態であることを確認
- インスタンスがManaged instancesに表示されているか確認

#### 4. PowerShellスクリプトでの確認

```powershell
cd D:\OneDrive\git_work\dev-workspace
.\scripts\check_session_manager_setup.ps1
```

### よくあるエラーメッセージ

#### "Permission denied (publickey)"

- SSH鍵のパスが正しいか確認
- SSH鍵のパーミッションを確認（Linux/macOS: `chmod 600`）
- 正しいユーザー名（`ec2-user`）を使用しているか確認

#### "Connection timed out"

- EC2インスタンスが起動しているか確認
- セキュリティグループでSSH（ポート22）が許可されているか確認
- ネットワーク接続を確認

#### "Host key verification failed"

- `-o StrictHostKeyChecking=no` オプションを使用
- または、`~/.ssh/known_hosts` から該当するホスト鍵を削除

## セキュリティの注意事項

### 1. SSH鍵の管理

- SSH鍵は機密情報です。他人と共有しないでください
- SSH鍵は安全な場所に保管してください
- 鍵が漏洩した場合は、すぐに新しい鍵を生成して置き換えてください

### 2. 接続時の注意

- 本番環境への接続は必要最小限に留めてください
- 接続後は、不要なファイルやコマンド履歴を削除してください
- 接続ログを定期的に確認してください

### 3. StrictHostKeyCheckingについて

`-o StrictHostKeyChecking=no` オプションは、ホスト鍵の確認をスキップします。
これは便利ですが、中間者攻撃（Man-in-the-Middle attack）のリスクがあります。

**推奨**: 初回接続時のみ `StrictHostKeyChecking=no` を使用し、2回目以降は通常の接続を使用してください。

```powershell
# 初回接続（ホスト鍵を確認しない）
ssh -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" -o StrictHostKeyChecking=no ec2-user@52.197.69.195

# 2回目以降（通常の接続）
ssh -i "$env:USERPROFILE\.ssh\fishtrack_ec2_key" ec2-user@52.197.69.195
```

## 参考情報

### 関連ドキュメント

- `docs/plans/completed/github_secrets_setup.md`: GitHub Secrets設定（Raspberry PiへのSSH接続手順も含む）
- `scripts/migrate_prod_data.ps1`: データ移行スクリプト（EC2接続の実装例）
- `scripts/analyze_production_db.sh`: 本番環境スキーマ分析スクリプト

### 関連スクリプト

- `scripts/analyze_production_db.sh`: 本番環境のデータベーススキーマを分析
- `scripts/check_production_deployment.py`: 本番環境デプロイ状況確認スクリプト
- `scripts/check_session_manager_setup.ps1`: Session Manager設定確認スクリプト
- `.github/workflows/analyze_production_db.yml`: GitHub Actionsでの自動実行例

### AWS公式ドキュメント

- [Session Manager公式ドキュメント](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [Session Managerポートフォワーディング](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions.html)
- [EC2インスタンスへの接続方法](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-with-systems-manager-session-manager.html)

## 更新履歴

- **2026-01-01**: 初版作成
- **2026-01-09**: Session Manager接続方法を追加

---

**注意**: このドキュメントは、EC2インスタンスへのSSH接続方法を説明しています。本番環境への接続は、適切な権限を持つユーザーのみが実行してください。

