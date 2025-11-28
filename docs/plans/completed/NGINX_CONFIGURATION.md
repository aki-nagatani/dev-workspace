# Nginx Configuration Guide for FishTrack & MyPokedex

このドキュメントでは、FishTrackとMyPokedexをサブディレクトリ（`/fishtrack/` および `/mypokedex/`）で運用するためのNginx設定について説明します。

## 重要な変更点（2025年11月）

以前の設定では `rewrite` ディレクティブを使用してURLプレフィックス（`/fishtrack`など）を削除してアプリケーションに転送していましたが、これによって静的ファイル（CSS/JS）のパス解決に問題が発生していました。

現在は、**URLプレフィックスを削除せずに**アプリケーションに転送し、アプリケーション側でプレフィックスを認識する構成に変更しています。

これに伴い、以下の対応が必要です：
1. アプリケーション設定で `STANDALONE=false` を設定する（`/etc/fishtrack.env`, `/etc/mypokedex.env`）
2. Nginx設定で `rewrite` を無効化する

## 共通の基本設定

リバースプロキシの基本的な設定は以下の通りです。

```nginx
# プロキシヘッダーの基本設定
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;

# タイムアウト設定（必要に応じて調整）
proxy_connect_timeout 120s;
proxy_send_timeout 120s;
proxy_read_timeout 120s;
```

## FishTrackの設定例

`/etc/nginx/sites-available/default` または `/etc/nginx/conf.d/fishtrack.conf` に記述します。

```nginx
location /fishtrack/ {
    # 重要: rewriteによるプレフィックス削除を行わないこと
    # rewrite ^/fishtrack/?(.*)$ /$1 break;  <-- コメントアウトまたは削除
    
    # Unixドメインソケットへの転送
    proxy_pass http://unix:/run/fishtrack/gunicorn.sock;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # バッファリング設定（SSEなどのためオフ推奨）
    proxy_buffering off;
    proxy_request_buffering off;
}
```

### 対応する環境変数（/etc/fishtrack.env）

```bash
# Nginxが/fishtrack/プレフィックス付きで転送するため、
# アプリ側でプレフィックスを処理するように設定
FISHTRACK_STANDALONE=false
```

## MyPokedexの設定例

`/etc/nginx/sites-available/default` または `/etc/nginx/conf.d/mypokedex.conf` に記述します。

```nginx
location /mypokedex/ {
    # 重要: rewriteによるプレフィックス削除を行わないこと
    # rewrite ^/mypokedex/?(.*)$ /$1 break;  <-- コメントアウトまたは削除
    
    # Unixドメインソケットへの転送
    proxy_pass http://unix:/run/mypokedex/gunicorn.sock;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # バッファリング設定
    proxy_buffering off;
    proxy_request_buffering off;
}
```

### 対応する環境変数（/etc/mypokedex.env）

```bash
# Nginxが/mypokedex/プレフィックス付きで転送するため、
# アプリ側でプレフィックスを処理するように設定
MYPDEX_STANDALONE=false
```

## 設定反映手順

1. **環境変数の更新**
   ```bash
   sudo nano /etc/fishtrack.env  # FISHTRACK_STANDALONE=false を追加/変更
   sudo nano /etc/mypokedex.env  # MYPDEX_STANDALONE=false を追加/変更
   ```

2. **Nginx設定の更新**
   ```bash
   sudo nano /etc/nginx/sites-available/default
   # rewrite行をコメントアウト
   ```

3. **サービスの再起動**
   ```bash
   # 設定テスト
   sudo nginx -t
   
   # Nginxリロード
   sudo systemctl reload nginx
   
   # アプリケーション再起動
   sudo systemctl restart fishtrack.service
   sudo systemctl restart mypokedex.service
   ```

## トラブルシューティング

### CSS/JSが読み込まれない場合（404エラー）
- **現象**: HTMLは表示されるがデザインが崩れる。ブラウザコンソールで `/static/...` への404エラーが出ている。
- **原因**: `rewrite` が有効になっているか、`STANDALONE=true` になっている可能性があります。
- **確認**:
  - Nginx設定で `rewrite` がコメントアウトされているか
  - 環境変数で `STANDALONE=false` になっているか
  - HTMLソースの `<link>` タグが `/fishtrack/static/...` のようになっているか（`/static/...` ならアプリ設定が間違っています）

### Redirect loop または 404エラー（ページが見つからない）
- **現象**: アプリにアクセスするとリダイレクトループが発生するか、Flaskの404ページが表示される。
- **原因**: アプリが期待するプレフィックスとNginxが転送するパスが不一致。
- **確認**:
  - Nginxが `/fishtrack/` 付きで転送しているのに、アプリが `STANDALONE=true` （プレフィックスなし想定）で動作していると、アプリは `/fishtrack/` というルートを探して404になります。
  - 逆の場合（rewriteあり、STANDALONE=false）は、アプリは `/` にアクセスが来たのに `/fishtrack/` を期待してリダイレクトループする可能性があります。

