# 本番環境分割移行ガイド

このドキュメントは、統合サービス（MyHobbySite）から分離サービス（FishTrack、MyPokedex）への移行手順を説明します。

## 実施状況

**全体の実施状況**: ⏳ **未実施**（移行前の準備段階）

## 移行前の準備

**実施状況**: ⏳ **未実施**

### 1. バックアップの実施

**実施状況**: ⏳ **未実施**

```bash
# データベースのバックアップ
sudo cp /home/pi/MyHobbySite/data/mypokedex.db /home/pi/MyHobbySite/data/mypokedex.db.backup.$(date +%Y%m%d-%H%M%S)
sudo cp /home/pi/MyHobbySite/data/fishtrack.db /home/pi/MyHobbySite/data/fishtrack.db.backup.$(date +%Y%m%d-%H%M%S)

# 環境変数ファイルのバックアップ
sudo cp /etc/myhobbysite.env /etc/myhobbysite.env.backup.$(date +%Y%m%d-%H%M%S)
```

**実施結果**: ⏳ **未実施**
- データベースのバックアップ: ⏳ **未実施**
- 環境変数ファイルのバックアップ: ⏳ **未実施**

### 2. 移行計画の確認

**実施状況**: ⏳ **未実施**

- [ ] FishTrack本番環境の構築が完了している
- [ ] MyPokedex本番環境の構築が完了している
- [ ] リバースプロキシの設定が完了している
- [ ] データベースの移行が完了している
- [ ] ロールバック手順を確認している

**実施結果**: ⏳ **未実施**

## 移行手順

**実施状況**: ⏳ **未実施**（移行前の準備完了後に実施）

### ステップ1: FishTrackサービスの起動と動作確認

**実施状況**: ⏳ **未実施**

```bash
# FishTrackサービスを起動
sudo systemctl start fishtrack.service

# サービスステータスを確認
sudo systemctl status fishtrack.service

# ログを確認
sudo journalctl -u fishtrack.service -f
tail -f /var/log/fishtrack/error.log

# 動作確認（ローカルから）
curl http://localhost/fishtrack/
```

**確認事項**:
- [ ] サービスが正常に起動している
- [ ] エラーログに異常がない
- [ ] アプリケーションが正常に動作している

### ステップ2: MyPokedexサービスの起動と動作確認

**実施状況**: ⏳ **未実施**

```bash
# MyPokedexサービスを起動
sudo systemctl start mypokedex.service

# サービスステータスを確認
sudo systemctl status mypokedex.service

# ログを確認
sudo journalctl -u mypokedex.service -f
tail -f /var/log/mypokedex/error.log

# 動作確認（ローカルから）
curl http://localhost/mypokedex/
```

**確認事項**: ⏳ **未実施**
- [ ] サービスが正常に起動している
- [ ] エラーログに異常がない
- [ ] アプリケーションが正常に動作している
- [ ] 既存データが正常に表示されている

**実施結果**: ⏳ **未実施**

### ステップ3: リバースプロキシの設定更新

**実施状況**: ⏳ **未実施**

```bash
# nginx設定ファイルを編集
sudo nano /etc/nginx/sites-available/default
# または
sudo nano /etc/nginx/conf.d/fishtrack.conf
sudo nano /etc/nginx/conf.d/mypokedex.conf

# nginx設定をテスト
sudo nginx -t

# nginxをリロード
sudo systemctl reload nginx
```

**確認事項**: ⏳ **未実施**
- [ ] nginx設定のテストが成功している
- [ ] nginxが正常にリロードされている

**実施結果**: ⏳ **未実施**

### ステップ4: リバースプロキシ経由での動作確認

**実施状況**: ⏳ **未実施**

```bash
# 外部からアクセスして動作確認
curl http://your-server/fishtrack/
curl http://your-server/mypokedex/
```

**確認事項**: ⏳ **未実施**
- [ ] FishTrackが正常にアクセスできる
- [ ] MyPokedexが正常にアクセスできる
- [ ] 既存の機能が正常に動作している

**実施結果**: ⏳ **未実施**

### ステップ5: 統合サービスの停止

**実施状況**: ⏳ **未実施**

**⚠️ 重要**: すべての動作確認が完了してから実行してください。

```bash
# 統合サービスを停止
sudo systemctl stop myhobbysite.service

# サービスステータスを確認
sudo systemctl status myhobbysite.service
```

**確認事項**: ⏳ **未実施**
- [ ] 統合サービスが正常に停止している
- [ ] FishTrackとMyPokedexが引き続き正常に動作している

**実施結果**: ⏳ **未実施**

### ステップ6: 最終動作確認

**実施状況**: ⏳ **未実施**

```bash
# 各サービスのステータスを確認
sudo systemctl status fishtrack.service
sudo systemctl status mypokedex.service

# ログを確認
sudo journalctl -u fishtrack.service -n 50
sudo journalctl -u mypokedex.service -n 50
```

**確認事項**: ⏳ **未実施**
- [ ] FishTrackが正常に動作している
- [ ] MyPokedexが正常に動作している
- [ ] エラーログに異常がない
- [ ] すべての機能が正常に動作している

**実施結果**: ⏳ **未実施**

## ロールバック手順

**実施状況**: ⏳ **未実施**（問題発生時に実施）

問題が発生した場合、以下の手順でロールバックできます：

```bash
# 統合サービスを再起動
sudo systemctl start myhobbysite.service

# 分離サービスを停止
sudo systemctl stop fishtrack.service
sudo systemctl stop mypokedex.service

# リバースプロキシの設定を元に戻す
sudo systemctl reload nginx
```

## 移行後の確認事項

**実施状況**: ⏳ **未実施**（移行完了後に実施）

- [ ] 各サービスが正常に動作している
- [ ] ログが正常に出力されている
- [ ] データベースが正常にアクセスできる
- [ ] パフォーマンスに問題がない
- [ ] 監視・アラートが正常に動作している

**実施結果**: ⏳ **未実施**

## トラブルシューティング

### サービスが起動しない

```bash
# サービスステータスを確認
sudo systemctl status <service-name>

# ログを確認
sudo journalctl -u <service-name> -n 100
```

### データベースエラー

```bash
# データベースファイルのパーミッションを確認
ls -la /home/pi/<app>/data/<db>.db

# マイグレーションを再実行
cd /home/pi/<app>/current
source /home/pi/<app>/.venv/bin/activate
alembic upgrade head
```

### リバースプロキシエラー

```bash
# nginx設定をテスト
sudo nginx -t

# nginxログを確認
sudo tail -f /var/log/nginx/error.log
```

