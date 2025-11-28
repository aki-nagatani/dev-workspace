# Cloudflare設定確認チェックリスト

このドキュメントは、Phase 4で本番環境を分割する際に、Cloudflareの設定を確認・更新するためのチェックリストです。

## 確認実施情報

- **確認日時**: 2025-11-23
- **確認者**: AIエージェント
- **確認対象**: Cloudflareダッシュボード、DNS情報

## 確認手順

1. Cloudflareダッシュボードにログイン
2. 以下の各項目を確認し、結果を記録
3. 確認結果をこのドキュメントに記録

## 確認結果の要約

### 正常に動作している項目
- ✅ Cloudflareプロキシが有効（`cf-proxied:true`）
- ✅ DNSレコードが適切に設定されている
- ✅ Cloudflareのネームサーバーが使用されている
- ✅ `www.yume-eita.com`がCloudflare経由でアクセス可能
- ✅ SSL/TLS暗号化モード: **フル (Full)**（ブラウザからCloudflare、Cloudflareからオリジンサーバーまで完全に暗号化）
- ✅ 自動SSL/TLSモードが有効（Cloudflareの推奨設定を使用）
- ✅ TLS 1.3が有効
- ✅ Cloudflare Tunnelが正常稼働中（ステータス: `HEALTHY`、アップタイム: 19時間）

### 確認が必要な項目・問題点
- ⚠️ **Cloudflare Tunnelの使用**: `www.yume-eita.com`は`cfargotunnel.com`へのCNAMEレコード（Cloudflare Tunnelを使用している）
  - **Tunnel名**: `homeassistant-tunnel`（Home Assistant用のTunnel名だが、`www.yume-eita.com`も使用している）
  - **Tunnel ID**: `89e3f558-d84b-478a-92e0-bf95de3d2c0e`（確認済み）
  - **ステータス**: `HEALTHY`（正常稼働中）
  - **ルーティング**: ✅ **確認済み** - `www.yume-eita.com` → `http://localhost`（ポート80、nginx経由）
  - **`/mypokedex`と`/fishtrack/`のルーティング**: ✅ **確認済み** - アプリケーション側（Flask Blueprint）で処理
- ⚠️ **ページルール・転送ルールの確認**: `/mypokedex`と`/fishtrack/`のルーティングはアプリケーション側（Flask Blueprint）で処理されているため、Cloudflare側のページルール・転送ルールは不要（確認済み）
- ⚠️ **非セキュアトラフィック**: 過去24時間で「None (not secure)」が12リクエスト（要確認・改善検討）
- ⚠️ **Unknownトラフィック**: 過去24時間で「Unknown」が217リクエスト（TLSバージョンが不明、要確認）
- ⚠️ **Cloudflare Tunnelのエラー**: ログに`error="Incoming request ended abruptly: context canceled"`が記録されている（`/fishtrack/`へのリクエストで発生、要確認）

## 1. DNS設定の確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 1.1 ドメイン設定

**確認項目**:
- ドメイン名: ___________
- DNSレコードの設定
  - Aレコード: ___________
  - CNAMEレコード: ___________
  - その他のレコード: ___________

**確認結果**: ✅ **確認済み**
- ドメイン名: `yume-eita.com`
- DNSレコード:
  - **Aレコード**: `yume-eita.com` → `150.95.255.38`（`cf-proxied:true`、Cloudflareプロキシ有効）
  - **CNAMEレコード**: 
    - `www.yume-eita.com` → `89e3f558-d84b-478a-92e0-bf95de3d2c0e.cfargotunnel.com`（`cf-proxied:true`、Cloudflareプロキシ有効）
    - `home.yume-eita.com` → `89e3f558-d84b-478a-92e0-bf95de3d2c0e.cfargotunnel.com`（`cf-proxied:true`、Cloudflareプロキシ有効）
  - **NSレコード**: Cloudflareのネームサーバー（`gemma.ns.cloudflare.com`、`greg.ns.cloudflare.com`）
  - **TXTレコード**: `yume-eita.com` → `"v=spf1 -all"`（SPFレコード）
  - **その他のNSレコード**: 複数のサブドメインが別のネームサーバー（`dns1.onamae.com`、`dns2.onamae.com`）を使用

### 1.2 プロキシ設定

**確認項目**:
- Cloudflareプロキシの有効/無効設定
- プロキシモード（DNS only / Proxied）
- プロキシされたIPアドレス

**確認結果**: ✅ **確認済み**
- プロキシ設定: **有効**（`cf-proxied:true`が設定されている）
- プロキシモード: **Proxied**（Cloudflareプロキシ経由）
- プロキシされたIPアドレス: `150.95.255.38`（`yume-eita.com`のAレコード）
- **重要**: `www.yume-eita.com`は`cfargotunnel.com`へのCNAMEレコード（Cloudflare Tunnelを使用している可能性がある）

## 2. SSL/TLS設定の確認

**確認場所**: https://dash.cloudflare.com/70febcf8dc0a955097cd47329a2b4e70/yume-eita.com/ssl-tls

**確認状況**: ⚠️ **一部確認済み**（基本設定は確認済み、詳細設定は未確認）

### 2.1 SSL/TLSモード

**確認項目**:
- SSL/TLSモード（Off / Flexible / Full / Full (strict)）
- 証明書の種類（Universal SSL / Custom Certificate）
- 証明書の有効期限

**確認結果**: ✅ **確認済み**
- SSL/TLSモード: **フル (Full)**（確認済み: 2025-11-23）
- 自動モード: **有効**（5ヶ月前に有効化）
- 次回の自動スキャン: **11/24**
- 証明書の種類: **自動 SSL/TLS**（Cloudflareの推奨設定）
- 証明書の有効期限: ___________

### 2.2 証明書の詳細

**確認場所**: https://dash.cloudflare.com/70febcf8dc0a955097cd47329a2b4e70/yume-eita.com/ssl-tls/edge-certificates

**確認状況**: ✅ **確認済み**（2025-11-23）

**確認項目**:
- 証明書の種類
- 証明書の発行者
- 証明書の有効期限
- 証明書の更新設定
- 証明書のホスト名

**確認結果**: ✅ **確認済み**（2025-11-23確認）
- **証明書の種類**: **Universal SSL証明書**（共有Cloudflare Universal SSL証明書、Free プランに含まれる）
- **証明書の発行者**: Cloudflare（Universal証明書）
- **証明書のホスト名**: 
  - `*.yume-eita.com, yume-eita.com`（Universal証明書）
  - `*.yume-eita.com, yume-eita.com`（バックアップ証明書）
- **証明書の有効期限**: 
  - **Universal証明書**: **2026-01-28**（管理対象、Cloudflareが自動更新）
  - **バックアップ証明書**: **2026-02-03**（管理対象、Cloudflareが自動更新）
- **証明書の更新設定**: **自動更新**（Cloudflareが管理対象として自動更新）
- **Advanced Certificate Manager**: ⏳ **未アクティブ**（アクティブ化可能）

### 2.3 その他のSSL/TLS設定

**確認場所**: https://dash.cloudflare.com/70febcf8dc0a955097cd47329a2b4e70/yume-eita.com/ssl-tls

**確認状況**: ✅ **確認済み**（2025-11-23）

**確認項目**:
- Always Use HTTPS設定
- HSTS（HTTP Strict Transport Security）設定
- Minimum TLS Version設定
- Opportunistic Encryption設定
- TLS 1.3設定
- Automatic HTTPS Rewrites設定
- Certificate Transparency Monitoring設定

**確認結果**: ✅ **確認済み**（2025-11-23確認）
- **Always Use HTTPS**: ⏳ **無効**（オフ、有効化可能）
- **HSTS（HTTP Strict Transport Security）**: ⏳ **無効**（有効化ボタンあり、未設定）
- **Minimum TLS Version**: ✅ **確認済み** - **TLS 1.0 (デフォルト)**（現在の設定）
- **Opportunistic Encryption**: ✅ **確認済み** - **有効**（緑のチェックマーク）
- **TLS 1.3**: ✅ **確認済み** - **有効**（緑のチェックマーク、過去24時間でTLS v1.3が14リクエスト）
- **Automatic HTTPS Rewrites**: ✅ **確認済み** - **有効**（緑のチェックマーク）
- **Certificate Transparency Monitoring**: ⏳ **無効**（オフ、有効化可能）

### 2.4 TLS経由で配信されるトラフィック

**確認状況**: ✅ **確認済み**（2025-11-23）

**確認項目**:
- 過去24時間のトラフィック分布
- TLSバージョン別のトラフィック数

**確認結果**: ✅ **確認済み**（過去24時間、2025-11-23確認）
- **Unknown**: 217リクエスト
- **None (not secure)**: 12リクエスト
- **TLS v1.2**: 19リクエスト
- **TLS v1.3**: 14リクエスト
- **合計**: 262リクエスト

## 3. セキュリティ設定の確認

**確認場所**: https://dash.cloudflare.com/70febcf8dc0a955097cd47329a2b4e70/yume-eita.com/security/security-rules

**確認状況**: ⚠️ **一部確認済み**（セキュリティルールは確認済み、その他は未確認）

### 3.1 セキュリティレベル

**確認状況**: ⏸️ **分割計画には不要**（分割作業には直接関係しないため、必要に応じて後で確認）

**備考**: セキュリティレベル（ボット対策、DDoS保護）は分割作業には直接関係しないため、分割完了後に必要に応じて確認・調整する。

**確認項目**:
- セキュリティレベル（Off / Essentially Off / Low / Medium / High / I'm Under Attack!）
- ボット対策設定
- DDoS保護設定

**確認結果**: ⏸️ **分割計画には不要**（分割完了後に必要に応じて確認）

### 3.2 WAF（Web Application Firewall）設定

**確認状況**: ⚠️ **一部確認済み**（セキュリティルールは確認済み、WAF詳細設定は未確認）

**確認項目**:
- WAFの有効/無効
- WAFルールの設定
- カスタムルールの設定
- セキュリティルールの設定

**確認結果**: ⚠️ **一部確認済み**（2025-11-23確認）
- **セキュリティルール**: ✅ **確認済み**
  - **カスタムルール**: 0/5 使用済み、ルールは作成されていない
  - **レート制限ルール**: 0/1 使用済み、ルールは作成されていない
  - **管理ルール**: 0個アクティブ（Proプランにアップグレードが必要）
- WAF設定: ⏳ **未確認** ___________
- WAFルール: ⏳ **未確認** ___________
- カスタムルール: ✅ **確認済み** - 0/5 使用済み、ルールは作成されていない

## 4. パフォーマンス設定の確認

**確認状況**: ⏸️ **分割計画には不要**（分割作業には直接関係しないため、必要に応じて後で確認）

**備考**: パフォーマンス設定（キャッシュ、圧縮）は分割作業には直接関係しないため、分割完了後に必要に応じて確認・調整する。

### 4.1 キャッシュ設定

**確認状況**: ⏸️ **分割計画には不要**

**確認項目**:
- キャッシュレベル（Standard / Aggressive / Cache Everything）
- キャッシュの有効期限
- キャッシュのパージ設定

**確認結果**: ⏸️ **分割計画には不要**（分割完了後に必要に応じて確認）

### 4.2 圧縮設定

**確認状況**: ⏸️ **分割計画には不要**

**確認項目**:
- 圧縮の有効/無効
- 圧縮対象のファイルタイプ

**確認結果**: ⏸️ **分割計画には不要**（分割完了後に必要に応じて確認）

## 5. ページルールの確認

**確認場所**: https://dash.cloudflare.com/70febcf8dc0a955097cd47329a2b4e70/yume-eita.com/rules/page-rules

**確認状況**: ✅ **確認済み**（2025-11-23）

### 5.1 ページルールの設定

**確認状況**: ✅ **確認済み**

**確認項目**:
- ページルールの有無
- ページルールの内容
  - URLパターン: ___________
  - 設定内容: ___________
- 使用可能なページルール数

**確認結果**: ✅ **確認済み**（2025-11-23確認）
- **ページルール**: **0個/3個**（使用可能なページルール3個のうち0個を使用）
- **ページルールの有無**: **なし**（ページルールは作成されていない）
- **ページルールの内容**: **なし**（「データなし」と表示）
- **URLパターン**: **なし**（ページルールが存在しないため）
- **設定内容**: **なし**（ページルールが存在しないため）
- **備考**: Freeプランでは3個のページルールが使用可能。現在はページルールが設定されていないため、`/mypokedex`と`/fishtrack/`のルーティングはページルールではなく、Cloudflare Tunnelまたはアプリケーション側で処理されている可能性がある

## 6. 転送ルール（Transform Rules）の確認

**確認場所**: https://dash.cloudflare.com/70febcf8dc0a955097cd47329a2b4e70/yume-eita.com/rules/settings

**確認状況**: ✅ **確認済み**（2025-11-23）

### 6.1 転送ルールの設定

**確認状況**: ✅ **確認済み**

**確認項目**:
- 転送ルール（Managed Transforms）の有無
- 転送ルールの内容
  - URLパターン: ___________
  - 設定内容: ___________
- 一括リダイレクトの有無
- Managed Transformsの設定

**確認結果**: ✅ **確認済み**（2025-11-23確認）
- **一括リダイレクト**: ✅ **確認済み** - **0/5リスト、0/10,000項目**（一括リダイレクトリストは作成されていない）
- **Managed Transforms**: ✅ **確認済み** - **すべて無効**（HTTPリクエストヘッダー、HTTPレスポンスヘッダーの設定がすべて無効）
  - **HTTPリクエストヘッダー**: すべて無効（5つの設定項目すべてが無効）
    - TLS クライアント認証ヘッダーを追加する: 無効
    - 訪問者の Location ヘッダーを追加する: 無効
    - 訪問者の IP ヘッダーを削除する: 無効
    - "True-Client-IP" ヘッダーを追加します: 無効
    - 漏洩した資格情報チェック ヘッダーを追加する: 無効
  - **HTTPレスポンスヘッダー**: すべて無効（2つの設定項目すべてが無効）
    - 「X-Powered-By」ヘッダーを削除する: 無効
    - セキュリティ ヘッダーを追加する: 無効
- **転送ルール（URLルーティング）**: ⏳ **未確認**（Managed TransformsはHTTPヘッダーの調整機能で、URLルーティングとは別機能の可能性がある）
- **URL正規化設定**: ✅ **確認済み**（2025-11-23確認）
  - **正規化タイプ**: **Cloudflare**（選択されている）
    - バックスラッシュをフォワードスラッシュに正規化
    - 連続するフォワードスラッシュをマージ
  - **受信URLを正規化する**: ✅ **有効**（ON）
    - URLがエンコードされた受信URLがCloudflareのエッジに到達するときに正規化
    - Page Rules、WAF カスタムルール、Workers、AccessなどのURLが入力された製品に対して、正規化されたURLを使用
  - **オリジンへのURLを正規化する**: ⏳ **無効**（OFF）
    - CloudflareエッジでのURL正規化に加えて、オリジンへのトラフィックのURLを正規化する設定（現在は無効）
- **備考**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）
  - Managed TransformsはHTTPヘッダーの調整機能で、URLのルーティング（`/mypokedex`、`/fishtrack/`への転送）とは直接関係ない
  - URLルーティングの転送ルールは別の機能（Transform Rules）の可能性があるが、Freeプランでは利用できない可能性がある
  - **確認済み**: ページルールも転送ルールも設定されていないため、`/mypokedex`と`/fishtrack/`のルーティングは**アプリケーション側（Flask Blueprint）で処理されている**（本番サーバー上で確認済み）

## 7. 現在のアクセスURLの確認

**確認状況**: ✅ **確認済み**（2025-11-23）

### 7.1 統合サービスのURL

**確認項目**:
- 現在の統合サービスのURL
- MyPokedexのURL（統合サービス内）
- FishTrackのURL（統合サービス内）

**確認結果**: ✅ **確認済み**
- 統合サービスのURL: `https://www.yume-eita.com/`（統合サービスとして動作）
- MyPokedexのURL: `https://www.yume-eita.com/mypokedex`（Cloudflare経由、HTTPS）
- FishTrackのURL: `https://www.yume-eita.com/fishtrack/`（Cloudflare経由、HTTPS）

## 8. Cloudflare Tunnel設定の確認

**確認場所**: https://one.dash.cloudflare.com/70febcf8dc0a955097cd47329a2b4e70/networks/connectors

**確認状況**: ⚠️ **一部確認済み**（基本情報は確認済み、詳細設定は未確認）

### 8.1 Tunnelの基本情報

**確認状況**: ✅ **確認済み**（2025-11-23）

**確認項目**:
- Tunnel ID: `89e3f558-d84b-478a-92e0-bf95de3d2c0e`（DNS情報から確認済み）
- Tunnel名: ___________
- コネクタタイプ: ___________
- コネクタ ID: ___________
- Tunnelのステータス: ___________
- アップタイム: ___________
- Tunnelの設定場所（Networks > コネクタ）: ___________

**確認結果**: ✅ **確認済み**（2025-11-23確認、2025-11-23再確認）
- Tunnel ID: `89e3f558-d84b-478a-92e0-bf95de3d2c0e`
- Tunnel名: **`homeassistant-tunnel`**
- コネクタタイプ: **`cloudflared`**
- コネクタ ID: **`a55e850d-e84a-40ac-8715-1fe170b549ef`**
- コネクタバージョン: **`2025.6.1`**
- Tunnelのステータス: **`HEALTHY`**（正常稼働中）
- アップタイム: **20時間**（再確認時点、前回19時間から更新）
- 設定場所: **Networks > コネクタ > Cloudflare Tunnels**

### 8.2 Tunnelのルーティング設定

**確認状況**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）

**確認項目**:
- パブリックホスト名の設定
- `/mypokedex`のルーティング設定
- `/fishtrack/`のルーティング設定
- プライベートネットワークの設定
- 接続先のIPアドレス/ポート
- 接続先のプロトコル（HTTP/HTTPS）
- ルート設定
- Tunnelの構成方法（ローカル構成 / ダッシュボード管理）

**確認結果**: ✅ **確認済み**（2025-11-23確認、本番サーバー上で確認）
- **Tunnelの構成方法**: ✅ **確認済み** - **ローカル構成**（`homeassistant-tunnel`はローカルに構成されたトンネル）
  - Zero Trustダッシュボードから管理できない
  - 設定は本番サーバー上のローカル設定ファイル（`/etc/cloudflared/config.yml`）で管理されている
  - イングレスルールを移行することはできるが、その他の構成は移行されない
  - ローカルで行った変更はダッシュボードに反映されない
- **パブリックホスト名**: ✅ **確認済み** - `www.yume-eita.com`（DNS情報から確認済み）
- **イングレスルール**: ✅ **確認済み**（Tunnel設定ファイルで確認済み）
  - `hostname: home.yume-eita.com` → `service: http://localhost:8123`（Home Assistant用）
  - `hostname: www.yume-eita.com` → `service: http://localhost`（MyHobbySite用、ポート80）
  - `service: http_status:404`（デフォルト、マッチしないホスト名へのリクエスト）
- **`/mypokedex`のルーティング**: ✅ **確認済み** - **アプリケーション側（Flask Blueprint）で処理**
  - Tunnel設定では`www.yume-eita.com`全体を`http://localhost`（ポート80）に転送
  - nginxがポート80でリッスンし、`proxy_pass http://127.0.0.1:8000`でGunicornに転送
  - アプリケーション側（Flask Blueprint）で`/mypokedex`と`/fishtrack/`のルーティングを処理
- **`/fishtrack/`のルーティング**: ✅ **確認済み** - **アプリケーション側（Flask Blueprint）で処理**
  - Tunnel設定では`www.yume-eita.com`全体を`http://localhost`（ポート80）に転送
  - nginxがポート80でリッスンし、`proxy_pass http://127.0.0.1:8000`でGunicornに転送
  - アプリケーション側（Flask Blueprint）で`/mypokedex`と`/fishtrack/`のルーティングを処理
- **プライベートネットワーク**: ⏳ **未確認**（Tunnel設定ファイルには記載なし、デフォルト設定の可能性）
- **接続先**: ✅ **確認済み** - `http://localhost`（ポート80、本番サーバー上のnginx）
  - Tunnel設定: `www.yume-eita.com` → `http://localhost`（ポート80）
  - nginx設定: ポート80でリッスン → `proxy_pass http://127.0.0.1:8000`（Gunicorn）
  - Gunicorn: ポート8000でリッスン（`127.0.0.1:8000`）
- **プロトコル**: ✅ **確認済み** - **HTTP**（Tunnel設定ファイルで`http://localhost`と指定）
- **重要**: 
  - Tunnel名が`homeassistant-tunnel`となっているが、`www.yume-eita.com`へのCNAMEレコードがこのTunnelを指している
  - **Tunnelの設定は本番サーバー上のローカル設定ファイル（`/etc/cloudflared/config.yml`）で管理されている**
  - **`/mypokedex`と`/fishtrack/`のルーティングは、Tunnel設定ではなく、アプリケーション側（Flask Blueprint）で処理されている**
  - **リクエストの流れ**: Cloudflare → Cloudflare Tunnel → nginx (ポート80) → Gunicorn (ポート8000) → Flaskアプリケーション（Blueprintでルーティング）

### 8.3 Tunnelの接続先設定

**確認状況**: ✅ **確認済み**（2025-11-23、本番サーバー上で確認）

**確認方法**: 本番サーバーにSSH接続して、Tunnel設定ファイルを確認
```bash
# Tunnel設定ファイルの場所を確認
# 通常は以下のいずれか:
# - /etc/cloudflared/config.yml
# - ~/.cloudflared/config.yml
# - /home/pi/.cloudflared/config.yml

# 設定ファイルの内容を確認
cat /etc/cloudflared/config.yml
# または
cat ~/.cloudflared/config.yml
# または
cat /home/pi/.cloudflared/config.yml
```

**確認項目**:
- ローカルサーバーのIPアドレス
- ローカルサーバーのポート
- 接続先のパス
- アプリケーションのURL
- アプリケーションのポート
- アプリケーションのプロトコル
- イングレスルール（Ingress Rules）の設定

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
- **ローカルサーバー**: ✅ **確認済み** - `localhost`（本番サーバー自身）
- **ポート**: ✅ **確認済み** - **ポート80**（`www.yume-eita.com`の場合、`http://localhost`はポート80を指す）
- **接続先のパス**: ✅ **確認済み** - **ルートパス（`/`）**（Tunnel設定ではパス指定なし、アプリケーション側でルーティング）
- **アプリケーションURL**: ✅ **確認済み** - `http://localhost`（ポート80、nginx経由）
- **アプリケーションポート**: ✅ **確認済み** - **ポート8000**（Gunicornがリッスン、nginxが`proxy_pass http://127.0.0.1:8000`で転送）
- **プロトコル**: ✅ **確認済み** - **HTTP**（Tunnel設定ファイルで`http://localhost`と指定）
- **イングレスルール**: ✅ **確認済み**（Tunnel設定ファイルで確認済み）
  - `hostname: home.yume-eita.com` → `service: http://localhost:8123`（Home Assistant用）
  - `hostname: www.yume-eita.com` → `service: http://localhost`（MyHobbySite用、ポート80）
  - デフォルト: `service: http_status:404`（マッチしないホスト名へのリクエスト）
- **リクエストの流れ**: ✅ **確認済み**
  1. Cloudflare → Cloudflare Tunnel（`www.yume-eita.com`）
  2. Cloudflare Tunnel → nginx（`http://localhost:80`）
  3. nginx → Gunicorn（`proxy_pass http://127.0.0.1:8000`）
  4. Gunicorn → Flaskアプリケーション（Blueprintで`/mypokedex`と`/fishtrack/`をルーティング）

### 8.4 Tunnelのセキュリティ設定

**確認状況**: ⏸️ **分割計画には不要**（分割作業には直接関係しないため、必要に応じて後で確認）

**備考**: Tunnelのセキュリティ設定（アクセス制御、認証設定等）は分割作業には直接関係しないため、分割完了後に必要に応じて確認・調整する。

**確認項目**:
- アクセス制御の有効/無効
- アクセス制御のルール
- 認証設定
- セキュリティポリシーの設定
- WAF設定
- ボット対策設定

**確認結果**: ⏸️ **分割計画には不要**（分割完了後に必要に応じて確認）

### 8.5 Tunnelのパフォーマンス設定

**確認状況**: ⏸️ **分割計画には不要**（分割作業には直接関係しないため、必要に応じて後で確認）

**備考**: Tunnelのパフォーマンス設定（キャッシュ、圧縮）は分割作業には直接関係しないため、分割完了後に必要に応じて確認・調整する。

**確認項目**:
- キャッシュの有効/無効
- キャッシュの設定
- キャッシュの有効期限
- 圧縮の有効/無効
- 圧縮対象のファイルタイプ

**確認結果**: ⏸️ **分割計画には不要**（分割完了後に必要に応じて確認）

## 9. 分割後の設定計画

**確認状況**: ✅ **確認済み**（URL設計は確定済み）

### 9.1 分割後のURL設計

**確認状況**: ✅ **確認済み**

**確認項目**:
- MyPokedexの新URL: ___________
- FishTrackの新URL: ___________
- リダイレクト設定の必要性: ___________

**確認結果**: ✅ **確認済み**
- MyPokedexの新URL: `https://www.yume-eita.com/mypokedex`（分割後も同じURLを使用）
- FishTrackの新URL: `https://www.yume-eita.com/fishtrack/`（分割後も同じURLを使用）
- リダイレクト設定: 不要（分割後も同じURLを使用するため、リダイレクトは不要）

### 9.2 分割時に必要な設定変更

**確認状況**: ⏳ **未確認**（分割時に実施予定）

**確認項目**:
- DNSレコードの追加/変更: ___________
- ページルールの追加/変更: ___________
- 転送ルールの追加/変更: ___________
- SSL/TLS設定の変更: ___________
- Cloudflare Tunnel設定の変更: ___________

**確認結果**: ⏳ **未確認**（分割時に実施予定）
- DNSレコード: ___________
- ページルール: ___________
- 転送ルール: ___________
- SSL/TLS設定: ___________
- Cloudflare Tunnel設定: ___________

### 9.3 分割後のTunnel設定

**確認状況**: ⏳ **未確認**（分割時に実施予定）

**確認項目**:
- 分割後のTunnel設定
- MyPokedex用のTunnel設定
- FishTrack用のTunnel設定
- `/mypokedex`のルーティング変更
- `/fishtrack/`のルーティング変更
- 新しい接続先の設定

**確認結果**: ⏳ **未確認**（分割時に実施予定）
- 分割後の設定: ___________
- MyPokedex用の設定: ___________
- FishTrack用の設定: ___________
- `/mypokedex`のルーティング: ___________
- `/fishtrack/`のルーティング: ___________
- 新しい接続先: ___________

## 確認完了後の作業

1. このチェックリストの確認結果を記録
2. 確認結果を基に、Phase 4.3.3 / 4.4.3のリバースプロキシ設定を調整
3. 分割時に必要なCloudflare設定の変更を計画（DNS、ページルール、転送ルール、SSL/TLS、Cloudflare Tunnel）
4. 必要に応じて、確認結果を計画書に反映

## 注意事項

- **機密情報の取り扱い**: CloudflareのAPIキー、Cloudflare Tunnelのトークン等の機密情報は、このドキュメントに記録する際は必ずマスクしてください
- **設定変更前のバックアップ**: 設定変更前に、現在の設定をスクリーンショットまたはエクスポートしてバックアップを取得してください
- **変更禁止**: 確認作業中は、Cloudflareの設定（DNS、ページルール、転送ルール、SSL/TLS、Cloudflare Tunnel）を変更しないでください（確認のみ実施）

