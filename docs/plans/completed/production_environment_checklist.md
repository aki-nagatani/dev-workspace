# 本番環境現状確認チェックリスト

このドキュメントは、Phase 4.1「本番環境の現状確認」で確認すべき項目をまとめたチェックリストです。

## 確認実施情報

- **確認日時**: 2025-11-23
- **確認者**: AIエージェント
- **確認対象**: 本番サーバー（Raspberry Pi）
- **完了日**: 2025-11-26（Phase 4.1完了後、`completed/`に移動）

## 確認手順

1. 本番サーバー（Raspberry Pi等）にSSH接続
2. 以下の各項目を確認し、結果を記録
3. 確認結果をこのドキュメントに記録

## 確認結果の要約

### 正常に動作している項目
- ✅ systemdサービス（myhobbysite.service）は正常に稼働中
- ✅ データベースファイルは存在し、適切なサイズ
- ✅ Python環境と主要パッケージは正常にインストール済み
- ✅ nginxサービスは正常に稼働中
- ✅ バックアップ設定（cron）が設定済み

### 確認が必要な項目・問題点
- ⚠️ **nginx設定の不一致**: nginx設定ファイル（`app_nginx.conf`）はuwsgiを想定しているが、実際のアプリケーションはGunicornを使用している（ただし、Cloudflare経由でアクセスしているため正常に動作している可能性がある）
- ⚠️ **Cloudflare設定の確認**: 外部アクセスはCloudflare経由のため、Cloudflareの設定（DNS、プロキシ設定、SSL/TLS設定等）を確認する必要がある
- ⚠️ **SSL/TLS設定**: 本番サーバー側ではHTTPS未設定だが、Cloudflare経由でアクセスしているため、Cloudflare側でSSL/TLSが設定されている可能性がある
- ⚠️ **ディスク使用率**: ルートファイルシステムが97%使用（要監視）
- ⚠️ **過去のエラー**: 2025-11-17にWORKER TIMEOUTが発生（現在は正常稼働中）
- ⚠️ **環境変数**: `FISHTRACK_SECRET_KEY`、`ENABLE_SELF_REGISTER`、`FISHTRACK_ENABLE_SELF_REGISTER`が未設定
- ⚠️ **システム更新**: 265パッケージがアップグレード可能（要確認・更新検討）
- ⚠️ **リリースディレクトリ**: 5リリース分で235M使用（古いリリースの削除を検討）

## 1. サーバー構成の確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 1.1 基本情報

**確認状況**: ✅ **確認済み**

```bash
# OS情報
cat /etc/os-release

# ホスト名
hostname

# IPアドレス
hostname -I

# ディスク使用量
df -h

# メモリ情報
free -h

# CPU情報
lscpu | grep "Model name"
```

**確認結果**: ✅ **確認済み**
- OS: Debian GNU/Linux 12 (bookworm)
- ホスト名: raspberrypi
- IPアドレス: 192.168.68.71 (eth0), 172.30.32.1 (hassio), 172.17.0.1 (docker0)
- ディスク使用量: ルートファイルシステム 29G中27G使用（97%使用）、/boot/firmware 510M中77M使用（16%使用）
- メモリ: 7.6Gi 総容量、2.1Gi 使用中、5.5Gi 利用可能
- CPU: Cortex-A72

### 1.2 ネットワーク設定

```bash
# ネットワークインターフェース
ip addr show

# ファイアウォール設定（ufw使用時）
sudo ufw status
```

**確認結果**: ✅ **確認済み**
- ネットワークインターフェース: eth0 (192.168.68.71), wlan0 (DOWN), hassio (172.30.32.1), docker0 (172.17.0.1)
- ファイアウォール設定: ufw未インストール、iptables使用（DOCKER関連のルール設定あり）

## 2. systemdサービス設定の確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 2.1 現在のサービス設定

**確認状況**: ✅ **確認済み**

```bash
# サービスファイルの場所
ls -la /etc/systemd/system/myhobbysite.service

# サービスファイルの内容
cat /etc/systemd/system/myhobbysite.service

# サービスステータス
sudo systemctl status myhobbysite.service

# サービスが有効化されているか
systemctl is-enabled myhobbysite.service
```

**確認結果**: ✅ **確認済み**
- サービスファイルの場所: `/etc/systemd/system/myhobbysite.service`
- サービスステータス: active (running) - 2025-11-21 09:46:56 から稼働中
- 自動起動設定: enabled

**サービスファイルの内容**:
```
[Unit]
Description=MyHobbySite (Gunicorn)
After=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/MyHobbySite/current
EnvironmentFile=-/etc/myhobbysite.env
ExecStart=/home/pi/MyHobbySite/.venv/bin/gunicorn -w 3 -b 127.0.0.1:8000 src.app:createApp()
Restart=always
RestartSec=2
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target
```

### 2.2 サービスログ

```bash
# 最新のログ
sudo journalctl -u myhobbysite.service -n 50

# エラーログ
sudo journalctl -u myhobbysite.service -p err
```

**確認結果**: ✅ **確認済み**
- 最新のログ: サービスは正常に稼働中。最新の起動は2025-11-21 09:46:56。過去にWORKER TIMEOUTが発生した記録あり（2025-11-17 02:01:35）
- エラーログ: 現在のエラーログなし（-- No entries --）

## 3. 環境変数ファイルの確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 3.1 環境変数ファイルの場所と内容

**確認状況**: ✅ **確認済み**

```bash
# 環境変数ファイルの場所
ls -la /etc/myhobbysite.env

# 環境変数ファイルの内容（機密情報はマスクして記録）
cat /etc/myhobbysite.env
```

**確認結果**: ✅ **確認済み**
- 環境変数ファイルの場所: `/etc/myhobbysite.env`
- ファイルの存在: 存在（パーミッション: 600、所有者: pi）

**環境変数ファイルの内容**（機密情報は`***`でマスク）:
```
# 共通
FLASK_ENV=production
SECRET_KEY=***

# MyPokédex
MYPDEX_DATABASE_URL=sqlite:////home/pi/MyHobbySite/data/mypokedex.db
MYPDEX_DB_URL=sqlite:////home/pi/MyHobbySite/data/mypokedex.db
DATABASE_URL=sqlite:////home/pi/MyHobbySite/data/mypokedex.db
MYPDEX_LOGIN_DISABLED=0

# FishTrack
FISHTRACK_DATABASE_URL=sqlite:////home/pi/MyHobbySite/data/fishtrack.db
```

### 3.2 主要な環境変数

**確認状況**: ✅ **確認済み**

確認すべき環境変数:
- `MYPDEX_DATABASE_URL` / `DATABASE_URL`: `sqlite:////home/pi/MyHobbySite/data/mypokedex.db`（設定済み）
- `FISHTRACK_DATABASE_URL` / `FISHTRACK_DB_URL`: `sqlite:////home/pi/MyHobbySite/data/fishtrack.db`（設定済み）
- `SECRET_KEY` / `MYPDEX_SECRET_KEY`: `***`（存在確認済み）
- `FISHTRACK_SECRET_KEY`: 未設定（環境変数ファイルに存在しない）
- `ENABLE_SELF_REGISTER` / `FISHTRACK_ENABLE_SELF_REGISTER`: 未設定
- `FLASK_ENV`: `production`（設定済み）
- `LOGIN_DISABLED`: 未設定（`MYPDEX_LOGIN_DISABLED=0`は設定済み）

## 4. データベースファイルの確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 4.1 データベースファイルの場所とサイズ

**確認状況**: ✅ **確認済み**

```bash
# データベースファイルの場所
ls -lh /home/pi/MyHobbySite/data/*.db

# データベースファイルのサイズ
du -sh /home/pi/MyHobbySite/data/*.db

# データベースファイルのパーミッション
ls -la /home/pi/MyHobbySite/data/*.db
```

**確認結果**: ✅ **確認済み**
- MyPokedex DB: `/home/pi/MyHobbySite/data/mypokedex.db`
  - サイズ: 440K (446,464 bytes)
  - パーミッション: `-rw-r--r--` (644、所有者: pi)
- FishTrack DB: `/home/pi/MyHobbySite/data/fishtrack.db`
  - サイズ: 156K (155,648 bytes)
  - パーミッション: `-rw-r--r--` (644、所有者: pi)

### 4.2 データベースの内容確認（オプション）

```bash
# SQLiteデータベースのテーブル一覧（MyPokedex）
sqlite3 /home/pi/MyHobbySite/data/mypokedex.db ".tables"

# SQLiteデータベースのテーブル一覧（FishTrack）
sqlite3 /home/pi/MyHobbySite/data/fishtrack.db ".tables"
```

**確認結果**: ✅ **確認済み**
- MyPokedex テーブル数: 12テーブル（DexEntry, PokemonLegacyView, UserGameSetting, evolution, GameTitle, Regist, alembic_version, ops_monitoring, Pokemon, User, box_members, party_members）
- FishTrack テーブル数: 13テーブル（alembic_version, reel_holding, reel_model, reel_series, rod_holding, rod_model, rod_series, tackle_spec_import_draft, tackle_spec_import_log, manufacturer, fishtrack_user, ops_job_log, ops_monitoring）

## 5. アプリケーションディレクトリの確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 5.1 ディレクトリ構造

**確認状況**: ✅ **確認済み**

```bash
# アプリケーションディレクトリ
ls -la /home/pi/MyHobbySite/

# 現在のリリース
ls -la /home/pi/MyHobbySite/current

# リリースディレクトリ
ls -la /home/pi/MyHobbySite/releases/ | head -20
```

**確認結果**: ✅ **確認済み**
- アプリケーションディレクトリ: `/home/pi/MyHobbySite`
- 現在のリリース: `20251121-094637` (シンボリックリンク: `/home/pi/MyHobbySite/current -> /home/pi/MyHobbySite/releases/20251121-094637`)
- リリース数: 5リリース（20251111-233059, 20251111-234650, 20251116-231415, 20251120-010830, 20251121-094637）

### 5.2 Python環境

```bash
# Pythonバージョン
python3 --version

# 仮想環境の場所
ls -la /home/pi/MyHobbySite/.venv

# インストール済みパッケージ（主要なもの）
/home/pi/MyHobbySite/.venv/bin/pip list | grep -E "(flask|gunicorn|sqlalchemy)"
```

**確認結果**: ✅ **確認済み**
- Pythonバージョン: Python 3.11.2
- 仮想環境の場所: `/home/pi/MyHobbySite/.venv`（存在確認済み）
- 主要パッケージ: Flask 3.0.3, Flask-Login 0.6.3, Flask-SQLAlchemy 3.1.1, Flask-WTF 1.2.1, gunicorn 21.2.0, SQLAlchemy 2.0.32

## 6. リバースプロキシ（nginx）の設定確認

**確認状況**: ✅ **確認済み**（2025-11-23、詳細確認はセクション16を参照）

### 6.1 nginx設定ファイル

**確認状況**: ✅ **確認済み**（設定ファイルの内容は確認済み、ただしuwsgi設定でGunicornを使用している不一致あり）

```bash
# nginx設定ファイルの場所
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/

# nginx設定ファイルの内容
cat /etc/nginx/sites-available/default
# または
cat /etc/nginx/conf.d/*.conf
```

**確認結果**: ✅ **確認済み**
- nginx設定ファイルの場所: `/etc/nginx/sites-available/app_nginx.conf`（有効化済み: `/etc/nginx/sites-enabled/app_nginx.conf`）
- nginx設定ファイルの内容: uwsgi設定（ただし、実際のアプリケーションはGunicornを使用）

**nginx設定ファイルの内容**:
```
# Virtual Host configuration for example.com
server {
        listen 80;
        server_name example.com;        
        location / {
          include uwsgi_params;
          uwsgi_pass unix:/tmp/uwsgi.sock;
        }
}
```

**注意**: nginx設定はuwsgiを想定しているが、実際のアプリケーションはGunicornを使用しているため、設定の不一致が確認されました。

### 6.2 nginxステータス

```bash
# nginxステータス
sudo systemctl status nginx

# nginx設定のテスト
sudo nginx -t
```

**確認結果**: ✅ **確認済み**
- nginxステータス: active (running) - 2025-11-17 02:00:48 から稼働中
- 設定テスト結果: 設定ファイルの構文は正常（nginx: the configuration file /etc/nginx/nginx.conf syntax is ok）

## 7. ドメイン・URL設定の確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 7.1 ドメイン設定

**確認状況**: ✅ **確認済み**

```bash
# ホスト名解決
hostname -f

# DNS設定（/etc/hosts）
cat /etc/hosts | grep -v "^#"
```

**確認結果**: ✅ **確認済み**
- ホスト名: raspberrypi
- DNS設定: 標準的なlocalhost設定（127.0.0.1 localhost, 127.0.1.1 raspberrypi）

### 7.2 アクセスURL

**確認状況**: ✅ **確認済み**

**確認結果**: ✅ **確認済み**
- **外部アクセス**: Cloudflareのサービスを使用（Cloudflareがリバースプロキシとして機能）
- **MyPokedex URL**: `https://www.yume-eita.com/mypokedex`（Cloudflare経由、HTTPS）
- **FishTrack URL**: `https://www.yume-eita.com/fishtrack/`（Cloudflare経由、HTTPS）
- **統合サービスのURL**: 現在は統合サービスとして動作（MyPokedexとFishTrackが同一サービス内）

**注意**: 
- nginx設定と実際のアプリケーション構成（Gunicorn）に不一致があるが、Cloudflare経由でアクセスしているため正常に動作している可能性がある
- Cloudflareの設定（DNS、プロキシ設定、SSL/TLS設定等）を確認する必要がある
- 分割時には、Cloudflareの設定も更新する必要がある可能性がある
- 分割後も同じURL（`/mypokedex`、`/fishtrack/`）を使用する予定

## 8. ログファイルの確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 8.1 ログファイルの場所

**確認状況**: ✅ **確認済み**

```bash
# アプリケーションログ
ls -la /var/log/myhobbysite/ 2>/dev/null || echo "ログディレクトリが存在しません"

# nginxログ
ls -la /var/log/nginx/

# systemdログ
sudo journalctl -u myhobbysite.service --since "1 day ago" | head -20
```

**確認結果**: ✅ **確認済み**
- アプリケーションログ: `/var/log/myhobbysite/` ディレクトリは存在しない（systemdログを使用）
- nginxログ: `/var/log/nginx/` に存在（access.log, error.log等）
- systemdログ: `journalctl -u myhobbysite.service` で確認可能

## 9. バックアップ設定の確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 9.1 バックアップスクリプト

**確認状況**: ✅ **確認済み**

```bash
# バックアップスクリプトの場所
find /home/pi -name "*backup*" -type f 2>/dev/null
find /etc -name "*backup*" -type f 2>/dev/null

# cron設定（バックアップ関連）
crontab -l | grep -i backup
```

**確認結果**: ✅ **確認済み**
- バックアップスクリプト: 専用のバックアップスクリプトファイルは見つからず
- cron設定: バックアップ用のcron設定あり（毎日4時00分にrsyncで `/home/pi/MyHobbySite/` を `naga@192.168.68.58:/share/Public/PiBackup/Daily/MyHobbySite/` にバックアップ）

## 10. セキュリティ設定の確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 10.1 SSH設定

**確認状況**: ✅ **確認済み**

```bash
# SSH設定
cat /etc/ssh/sshd_config | grep -E "^[^#]" | grep -v "^$"
```

**確認結果**: ✅ **確認済み**
- SSH設定: 標準的な設定（KbdInteractiveAuthentication no, UsePAM yes, X11Forwarding yes, PrintMotd no）

### 10.2 ファイアウォール設定

```bash
# ufw設定
sudo ufw status verbose

# iptables設定（ufw未使用時）
sudo iptables -L -n
```

**確認結果**: ✅ **確認済み**
- ファイアウォール設定: iptables使用（INPUT/OUTPUTはACCEPT、FORWARDはDROP。DOCKER関連のルール設定あり）

### 10.3 SSL/TLS証明書の設定

```bash
# SSL証明書の確認
ls -la /etc/ssl/certs/ | grep -i "myhobby\|example"
```

**確認結果**: ✅ **確認済み**
- SSL証明書: カスタムSSL証明書は設定されていない（本番サーバー側ではHTTPS未設定、Cloudflare経由でアクセスしているためCloudflare側でSSL/TLSが設定されている可能性がある）

## 11. アプリケーション動作確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 11.1 ローカルアクセステスト

**確認状況**: ✅ **確認済み**

```bash
# ローカルホストからのアクセステスト
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/
```

**確認結果**: ✅ **確認済み**
- ローカルアクセス: HTTP 200（正常に応答）

### 11.2 外部アクセステスト

```bash
# 外部からのアクセステスト
curl -s http://192.168.68.71/ | head -20
```

**確認結果**: ✅ **確認済み**
- 外部アクセス: 正常に応答（myHobbySiteのトップページが表示される）

### 11.3 ポートの開放状況

```bash
# リスニングポートの確認
netstat -tlnp | grep -E ":(80|443|8000)"
# または
ss -tlnp | grep -E ":(80|443|8000)"
```

**確認結果**: ✅ **確認済み**
- ポート80: nginxがLISTEN（0.0.0.0:80）
- ポート8000: GunicornがLISTEN（127.0.0.1:8000）
- ポート443: 未使用（本番サーバー側ではHTTPS未設定、Cloudflare経由でアクセスしているためCloudflare側でSSL/TLSが設定されている可能性がある）

## 12. システム情報の確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 12.1 タイムゾーン設定

**確認状況**: ✅ **確認済み**

```bash
# タイムゾーン設定
timedatectl status
```

**確認結果**: ✅ **確認済み**
- タイムゾーン: Asia/Tokyo (JST, +0900)
- システムクロック同期: 有効（NTPサービス active）

### 12.2 システムのアップタイム

```bash
# システムのアップタイム
uptime
```

**確認結果**: ✅ **確認済み**
- アップタイム: 6日20時間27分
- ロードアベレージ: 0.23, 1.09, 0.90（1分、5分、15分）

### 12.3 システム更新状況

```bash
# アップグレード可能なパッケージ数
apt list --upgradable 2>/dev/null | wc -l
```

**確認結果**: ✅ **確認済み**
- アップグレード可能なパッケージ: 265パッケージ（要確認・更新検討）

## 13. ディスク容量の詳細確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 13.1 アプリケーションディレクトリの容量

**確認状況**: ✅ **確認済み**

```bash
# 各ディレクトリの容量確認
du -sh /home/pi/MyHobbySite/*
```

**確認結果**: ✅ **確認済み**
- `current`: 0（シンボリックリンク）
- `scripts`: 36K
- `data`: 5.3M
- `venv`: 22M
- `cache`: 173M
- `releases`: 235M（5リリース分）

### 13.2 ファイルパーミッションの確認

```bash
# 重要なディレクトリのパーミッション
ls -ld /home/pi/MyHobbySite/current /home/pi/MyHobbySite/data /home/pi/MyHobbySite/.venv
```

**確認結果**: ✅ **確認済み**
- `current`: `drwxr-xr-x` (755、シンボリックリンク)
- `data`: `drwxr-xr-x` (755、所有者: pi)
- `.venv`: `drwxr-xr-x` (755、所有者: pi)

## 14. ログローテーション設定の確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 14.1 ログローテーション設定

**確認状況**: ✅ **確認済み**

```bash
# ログローテーション設定の確認
logrotate -d /etc/logrotate.conf | grep -i "nginx\|myhobby"
```

**確認結果**: ✅ **確認済み**
- nginxログローテーション: 1日ごとにローテーション、14世代保持
- アプリケーションログローテーション: 設定なし（systemdログを使用）

### 14.2 ログファイルのサイズ

```bash
# ログファイルのサイズ確認
ls -lh /var/log/nginx/*.log
```

**確認結果**: ✅ **確認済み**
- nginx access.log: 15K
- nginx error.log: 0（エラーログなし）

## 15. アプリケーション情報の確認

**確認状況**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）

### 15.1 アプリケーションバージョン

**確認状況**: ✅ **確認済み**

```bash
# バージョン情報の確認
cat pyproject.toml | grep -E "version|name"
# または
cat setup.py | grep -E "version|name"
```

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **バージョン情報**: ✅ **確認済み** - `pyproject.toml`に`target-version = ["py311"]`が記載
  - アプリケーションのバージョン番号は`pyproject.toml`に記載されていない（`target-version`のみ）
  - Pythonバージョン: Python 3.11.2（システムで確認済み）
  - リリース番号: `20251121-094637`（現在のリリースディレクトリ名から確認）

## 16. nginx設定の詳細確認（追加確認項目）

**確認状況**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）

### 16.1 nginx設定ファイルの全体確認

**確認状況**: ✅ **確認済み**

```bash
# すべてのnginx設定ファイルを確認
cat /etc/nginx/nginx.conf
cat /etc/nginx/sites-available/*
cat /etc/nginx/sites-enabled/*
cat /etc/nginx/conf.d/*.conf 2>/dev/null || echo "conf.dディレクトリが存在しません"
```

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **nginxメイン設定ファイル（`/etc/nginx/nginx.conf`）**: ✅ **確認済み** - 標準的な設定
  - `worker_processes auto`
  - `events { worker_connections 768; }`
  - `http { ... }`ブロック
  - SSL設定: `ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3`
  - ログ設定: `access_log /var/log/nginx/access.log`
  - Gzip設定: `gzip on`
  - 設定ファイルのインクルード: `/etc/nginx/conf.d/*.conf`、`/etc/nginx/sites-enabled/*.conf`
- **有効化されている設定ファイル**: ✅ **確認済み** - `/etc/nginx/sites-enabled/app_nginx.conf`（シンボリックリンク: `/etc/nginx/sites-available/app_nginx.conf`）
  - **注意**: `app_nginx.conf`はuwsgi設定だが、実際には使用されていない
- **実際に使用されている設定**: ✅ **確認済み** - `default`サーバーブロック（`/etc/nginx/sites-enabled/default`またはメイン設定内）
  - `listen 80 default_server`
  - `server_name _`
  - `location = /healthz { return 200; }`（ヘルスチェック用）
  - `location / { proxy_pass http://127.0.0.1:8000; ... }`（Gunicornに転送）
  - `proxy_set_header Host $host;`
  - `proxy_set_header X-Real-IP $remote_addr;`
  - `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;`
- **その他の設定ファイル**: ✅ **確認済み** - `/etc/nginx/sites-available/default`（有効化されていない）

### 16.2 nginx設定の動作確認

**確認状況**: ✅ **確認済み**

```bash
# nginx設定の再読み込みテスト
sudo nginx -t

# nginx設定の詳細確認
nginx -T 2>/dev/null | head -100

# 実際に使用されている設定の確認
sudo nginx -T 2>/dev/null | grep -E "server_name|listen|location|proxy_pass|uwsgi_pass"
```

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **設定テスト結果**: ✅ **確認済み** - 設定ファイルの構文は正常（`nginx: the configuration file /etc/nginx/nginx.conf syntax is ok`）
- **実際に使用されている設定**: ✅ **確認済み**
  - `listen 80 default_server`（ポート80でリッスン）
  - `server_name _`（デフォルトサーバー）
  - `location = /healthz { return 200; }`（ヘルスチェック用）
  - `location / { proxy_pass http://127.0.0.1:8000; }`（Gunicornに転送）
  - `server_name example.com`（`app_nginx.conf`内、uwsgi設定だが実際には使用されていない可能性）

### 16.3 リクエストの流れの確認

**確認状況**: ✅ **確認済み**

```bash
# 実際のリクエストがどのように処理されているか確認
# nginxのアクセスログを確認
sudo tail -n 50 /var/log/nginx/access.log

# nginxのエラーログを確認
sudo tail -n 50 /var/log/nginx/error.log

# 実際のリクエストヘッダーを確認
curl -v http://127.0.0.1:8000/ 2>&1 | head -30
```

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **アクセスログの内容**: ✅ **確認済み** - 正常に記録されている
  - `/mypokedex/assets/`へのリクエストが記録されている
  - `/mypokedex/dex/`へのリクエストが記録されている
  - `/fishtrack/`へのリクエストが記録されている
  - `/robots.txt`へのリクエスト（404）が記録されている
  - `/`へのリクエストが記録されている
- **エラーログの内容**: ✅ **確認済み** - エラーログなし（`error.log`は0バイト）
- **リクエストヘッダー**: ✅ **確認済み** - 正常に応答（HTTP 200）

## 17. アプリケーションのルーティング設定確認（追加確認項目）

**確認状況**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）

### 17.1 Flaskアプリケーションのルーティング設定

**確認状況**: ✅ **確認済み**

```bash
# アプリケーションのルーティング設定を確認
grep -r "mypokedex\|fishtrack" /home/pi/MyHobbySite/current/src/ --include="*.py" | head -20

# Blueprintの登録を確認
grep -r "register_blueprint\|url_prefix" /home/pi/MyHobbySite/current/src/ --include="*.py" | head -20
```

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **ルーティング設定**: ✅ **確認済み** - Flask Blueprintを使用してルーティング
  - MyPokedex: `/mypokedex`でルーティング（複数のBlueprint: `/mypokedex/auth`、`/mypokedex/dex`、`/mypokedex/partyBox`、`/mypokedex/settings`）
  - FishTrack: `/fishtrack`でルーティング（複数のBlueprint: `/fishtrack/auth`、`/fishtrack/catch`、`/fishtrack/trip`、`/fishtrack/tackle`）
- **Blueprintの登録**: ✅ **確認済み**
  - MyPokedex: `app.register_blueprint(authBp, url_prefix="/mypokedex/auth")`、`app.register_blueprint(dexBp, url_prefix="/mypokedex/dex")`、`app.register_blueprint(partyBoxBp, url_prefix="/mypokedex/partyBox")`、`app.register_blueprint(settingsBp, url_prefix="/mypokedex/settings")`
  - FishTrack: `app.register_blueprint(base_bp, url_prefix="/fishtrack")`、`app.register_blueprint(auth_bp, url_prefix="/fishtrack/auth")`、`app.register_blueprint(catch_bp, url_prefix="/fishtrack/catch")`、`app.register_blueprint(trip_bp, url_prefix="/fishtrack/trip")`、`app.register_blueprint(tackle_bp, url_prefix="/fishtrack/tackle")`

### 17.2 アプリケーションのURL構造

**確認状況**: ✅ **確認済み**

```bash
# アプリケーションのURL構造を確認
# 実際のアプリケーションコードを確認
ls -la /home/pi/MyHobbySite/current/src/
find /home/pi/MyHobbySite/current/src/ -name "*.py" -type f | head -20
```

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **アプリケーションのURL構造**: ✅ **確認済み**
  - 統合サービスとして動作（MyPokedexとFishTrackが同一Flaskアプリケーション内）
  - ルートパス（`/`）: 統合サービスのトップページ（`myHobbySite`のリンクページ）
  - `/mypokedex`: MyPokedexアプリケーション（Blueprintでルーティング）
  - `/fishtrack/`: FishTrackアプリケーション（Blueprintでルーティング）
- **主要なファイル**: ✅ **確認済み**
  - `src/app.py`: メインアプリケーションファイル
  - `src/mypokedex/`: MyPokedexアプリケーション（Blueprint定義）
  - `src/fishtrack/`: FishTrackアプリケーション（Blueprint定義）
  - `src/api/`: API関連
  - `src/config/`: 設定関連

## 18. Cloudflare設定の詳細確認（追加確認項目）

**確認状況**: ✅ **確認済み**（2025-11-23、詳細は`dev-workspace/docs/plans/completed/cloudflare_setup_checklist.md`を参照）

### 18.1 Cloudflareダッシュボードでの確認

**確認状況**: ✅ **確認済み**（詳細は`dev-workspace/docs/plans/completed/cloudflare_setup_checklist.md`を参照）

**確認項目**:
- Cloudflareダッシュボードにログイン
- DNS設定の確認
- SSL/TLS設定の確認
- ページルールの確認
- 転送ルールの確認

**確認手順**: `dev-workspace/docs/plans/completed/cloudflare_setup_checklist.md` のチェックリストを使用

**確認結果**: ✅ **確認済み**（詳細は`dev-workspace/docs/plans/completed/cloudflare_setup_checklist.md`を参照）
- **DNS設定**: ✅ **確認済み**（2025-11-23）
  - `yume-eita.com` → `150.95.255.38`（Aレコード、`cf-proxied:true`）
  - `www.yume-eita.com` → `89e3f558-d84b-478a-92e0-bf95de3d2c0e.cfargotunnel.com`（CNAMEレコード、`cf-proxied:true`、Cloudflare Tunnel使用）
  - Cloudflareのネームサーバー使用（`gemma.ns.cloudflare.com`、`greg.ns.cloudflare.com`）
- **プロキシ設定**: ✅ **確認済み** - 有効（`cf-proxied:true`）
- **Cloudflare Tunnel**: ✅ **確認済み** - `www.yume-eita.com`がCloudflare Tunnelを使用（Tunnel名: `homeassistant-tunnel`、ステータス: `HEALTHY`）
- **SSL/TLS設定**: ✅ **確認済み**（詳細は`dev-workspace/docs/plans/completed/cloudflare_setup_checklist.md`を参照）
  - 暗号化モード: 「フル (Full)」（ブラウザからCloudflare、Cloudflareからオリジンサーバーまで完全に暗号化）
  - 自動SSL/TLS: 有効（Cloudflareの推奨設定を使用）
  - TLS 1.3: 有効
  - 証明書: Universal SSL証明書（有効期限: 2026-01-28、自動更新）
  - Always Use HTTPS: 無効（有効化可能）
  - HSTS: 無効（有効化可能）
  - Minimum TLS Version: TLS 1.0（デフォルト）
- **ページルール**: ✅ **確認済み** - 0個/3個（ページルールは設定されていない、アプリケーション側でルーティング）
- **転送ルール**: ✅ **確認済み** - Managed Transformsはすべて無効（URLルーティングはアプリケーション側で処理）

### 18.2 Cloudflare経由でのアクセステスト

**確認状況**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）

```bash
# Cloudflare経由でのアクセステスト
curl -v https://www.yume-eita.com/mypokedex 2>&1 | head -50
curl -v https://www.yume-eita.com/fishtrack/ 2>&1 | head -50

# レスポンスヘッダーの確認
curl -I https://www.yume-eita.com/mypokedex
curl -I https://www.yume-eita.com/fishtrack/
```

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **MyPokedex URLのレスポンス**: ✅ **確認済み** - **HTTP/2 302**（リダイレクト、`location: /mypokedex/partyBox`）
  - ステータスコード: 302（リダイレクト）
  - リダイレクト先: `/mypokedex/partyBox`
  - サーバー: `cloudflare`
  - セキュリティヘッダー: 適切に設定されている（CSP、X-Frame-Options、X-Content-Type-Options等）
- **FishTrack URLのレスポンス**: ✅ **確認済み** - **HTTP/2 200**（正常応答）
  - ステータスコード: 200（正常）
  - サーバー: `cloudflare`
  - セキュリティヘッダー: 適切に設定されている（CSP、X-Frame-Options、X-Content-Type-Options等）
- **レスポンスヘッダー**: ✅ **確認済み**
  - `server: cloudflare`（Cloudflare経由でアクセスされていることを確認）
  - `cf-cache-status: DYNAMIC`（動的コンテンツとして処理）
  - `cf-ray: 9a315ded1ff5a0b5-NRT`（Cloudflareのエッジサーバー: NRT）
  - セキュリティヘッダー: CSP、X-Frame-Options、X-Content-Type-Options、Referrer-Policy等が適切に設定されている

## 19. 統合サービスの動作確認（追加確認項目）

**確認状況**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）

### 19.1 統合サービスの動作フロー

**確認状況**: ✅ **確認済み**

**確認項目**:
- 現在の統合サービスがどのように動作しているか
- `/mypokedex`と`/fishtrack/`がどのように処理されているか
- アプリケーション側のルーティング設定

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **統合サービスの動作フロー**: ✅ **確認済み**
  1. **外部アクセス**: Cloudflare経由（`https://www.yume-eita.com`）
  2. **Cloudflare Tunnel**: `www.yume-eita.com` → `http://localhost`（ポート80）
  3. **nginx**: ポート80でリッスン → `proxy_pass http://127.0.0.1:8000`でGunicornに転送
  4. **Gunicorn**: ポート8000でリッスン（`127.0.0.1:8000`）→ Flaskアプリケーションに転送
  5. **Flaskアプリケーション**: Blueprintで`/mypokedex`と`/fishtrack/`をルーティング
- **ルーティング設定**: ✅ **確認済み**
  - `/mypokedex`: MyPokedexアプリケーション（Blueprint: `/mypokedex/auth`、`/mypokedex/dex`、`/mypokedex/partyBox`、`/mypokedex/settings`）
  - `/fishtrack/`: FishTrackアプリケーション（Blueprint: `/fishtrack/auth`、`/fishtrack/catch`、`/fishtrack/trip`、`/fishtrack/tackle`）
  - `/`: 統合サービスのトップページ（`myHobbySite`のリンクページ）

### 19.2 統合サービスのログ確認

**確認状況**: ✅ **確認済み**

```bash
# 統合サービスのログを確認
sudo journalctl -u myhobbysite.service --since "1 hour ago" | tail -50

# アプリケーションのログを確認（存在する場合）
ls -la /home/pi/MyHobbySite/current/logs/ 2>/dev/null || echo "ログディレクトリが存在しません"
```

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **統合サービスのログ**: ✅ **確認済み** - systemdログ（`journalctl -u myhobbysite.service`）で確認可能
  - サービスは正常に稼働中
  - 最新の起動: 2025-11-21 09:46:56
  - エラーログなし
- **アプリケーションのログ**: ✅ **確認済み** - `/home/pi/MyHobbySite/current/logs/`ディレクトリは存在しない（systemdログを使用）

## 20. Cloudflare Tunnel設定ファイルの確認（追加確認項目）

**確認状況**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）

### 20.1 Tunnel設定ファイルの場所と内容

**確認状況**: ✅ **確認済み**

**確認方法**: 本番サーバーにSSH接続して、Tunnel設定ファイルを確認
```bash
# cloudflaredプロセスの確認
ps aux | grep cloudflared

# Tunnel設定ファイルの場所を確認（cloudflaredプロセスのコマンドライン引数から）
ps aux | grep cloudflared | grep -o '\-c [^ ]*' || echo "設定ファイルの場所を確認できませんでした"

# 設定ファイルの内容を確認
# 通常は以下のいずれか:
cat /etc/cloudflared/config.yml 2>/dev/null || \
cat ~/.cloudflared/config.yml 2>/dev/null || \
cat /home/pi/.cloudflared/config.yml 2>/dev/null || \
echo "Tunnel設定ファイルが見つかりませんでした"

# cloudflaredサービスの確認（systemdサービスとして実行されている場合）
systemctl status cloudflared 2>/dev/null || echo "cloudflaredサービスが見つかりませんでした"
```

**確認項目**:
- Tunnel設定ファイルの場所
- Tunnel設定ファイルの内容
- イングレスルール（Ingress Rules）の設定
- `/mypokedex`のルーティング設定
- `/fishtrack/`のルーティング設定
- 接続先の設定（ポート、プロトコル等）

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **Tunnel設定ファイルの場所**: ✅ **確認済み** - `/etc/cloudflared/config.yml`
- **Tunnel設定ファイルの内容**: ✅ **確認済み**
  ```
  tunnel: homeassistant-tunnel
  credentials-file: /home/pi/.cloudflared/89e3f558-d84b-478a-92e0-bf95de3d2c0e.json
  
  ingress:
    - hostname: home.yume-eita.com
      service: http://localhost:8123
    - hostname: www.yume-eita.com
      service: http://localhost
    - service: http_status:404
  ```
- **イングレスルール**: ✅ **確認済み**（Tunnel設定ファイル内の`ingress`セクションで確認）
  - `hostname: home.yume-eita.com` → `service: http://localhost:8123`（Home Assistant用）
  - `hostname: www.yume-eita.com` → `service: http://localhost`（MyHobbySite用、ポート80）
  - デフォルト: `service: http_status:404`（マッチしないホスト名へのリクエスト）
- **`/mypokedex`のルーティング**: ✅ **確認済み** - **アプリケーション側（Flask Blueprint）で処理**
  - Tunnel設定では`www.yume-eita.com`全体を`http://localhost`（ポート80）に転送
  - nginxがポート80でリッスンし、`proxy_pass http://127.0.0.1:8000`でGunicornに転送
  - アプリケーション側（Flask Blueprint）で`/mypokedex`のルーティングを処理
- **`/fishtrack/`のルーティング**: ✅ **確認済み** - **アプリケーション側（Flask Blueprint）で処理**
  - Tunnel設定では`www.yume-eita.com`全体を`http://localhost`（ポート80）に転送
  - nginxがポート80でリッスンし、`proxy_pass http://127.0.0.1:8000`でGunicornに転送
  - アプリケーション側（Flask Blueprint）で`/fishtrack/`のルーティングを処理
- **接続先の設定**: ✅ **確認済み**（Tunnel設定ファイル内で確認）
  - **ポート**: ✅ **確認済み** - **ポート80**（`http://localhost`はポート80を指す）
  - **プロトコル**: ✅ **確認済み** - **HTTP**（`http://localhost`と指定）
  - **接続先URL**: ✅ **確認済み** - `http://localhost`（nginxがポート80でリッスン）
- **リクエストの流れ**: ✅ **確認済み**
  1. Cloudflare → Cloudflare Tunnel（`www.yume-eita.com`）
  2. Cloudflare Tunnel → nginx（`http://localhost:80`）
  3. nginx → Gunicorn（`proxy_pass http://127.0.0.1:8000`）
  4. Gunicorn → Flaskアプリケーション（Blueprintで`/mypokedex`と`/fishtrack/`をルーティング）

### 20.2 cloudflaredプロセスの確認

**確認状況**: ✅ **確認済み**

**確認方法**:
```bash
# cloudflaredプロセスの確認
ps aux | grep cloudflared

# cloudflaredサービスの確認（systemdサービスとして実行されている場合）
systemctl status cloudflared 2>/dev/null
systemctl list-units | grep cloudflared

# cloudflaredのバージョン確認
cloudflared --version 2>/dev/null || echo "cloudflaredコマンドが見つかりませんでした"
```

**確認項目**:
- cloudflaredプロセスの実行状況
- cloudflaredサービスの有無
- cloudflaredのバージョン
- 実行ユーザー
- コマンドライン引数

**確認結果**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
- **cloudflaredプロセスの実行状況**: ✅ **確認済み** - **実行中**（PID: 772、2025-11-17 02:00:42から稼働中）
- **cloudflaredサービスの有無**: ✅ **確認済み** - **存在**（systemdサービス: `cloudflared.service`）
  - ステータス: `active (running)`
  - 自動起動: `enabled`
  - 起動時刻: 2025-11-17 02:00:42 JST
  - アップタイム: 6日以上
- **cloudflaredのバージョン**: ✅ **確認済み** - **2025.6.1**（built 2025-06-17-1239 UTC）
- **実行ユーザー**: ✅ **確認済み** - **pi**（ユーザー: pi）
- **コマンドライン引数**: ✅ **確認済み** - `/usr/local/bin/cloudflared --config /etc/cloudflared/config.yml tunnel run homeassistant-tunnel`

## 確認完了後の作業

1. このチェックリストの確認結果を記録
2. 確認結果を基に、Phase 4.2以降の作業計画を調整
3. 必要に応じて、確認結果を計画書に反映
4. **追加確認項目（16-20）を完了してからPhase 4.2に進む**
5. **特に重要**: Cloudflare Tunnel設定ファイル（20.1）の確認は必須（Tunnelがローカル構成のため）

## 注意事項

- **機密情報の取り扱い**: SECRET_KEY等の機密情報は、このドキュメントに記録する際は必ずマスクしてください
- **バックアップ**: 確認作業前に、重要な設定ファイルのバックアップを取得してください
- **変更禁止**: 確認作業中は、本番環境の設定を変更しないでください
- **追加確認項目**: 16-20の追加確認項目を完了してからPhase 4.2に進むこと
- **Cloudflare Tunnel設定ファイル**: Tunnelがローカル構成のため、本番サーバー上の設定ファイル（20.1）の確認は必須

## 備考

- **Phase 4.1完了**: 2025-11-23にすべての確認項目（1-20）が完了
- **移動日**: 2025-11-26に`completed/`に移動（Phase 4.1完了後、参照用として保存）

