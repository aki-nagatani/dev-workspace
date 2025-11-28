# GitHub Secrets 設定ガイド（FishTrack / MyPokedex）

本ドキュメントは、FishTrack と MyPokedex 各リポジトリの GitHub Actions で本番デプロイを行う際に必要な Secrets の一覧と登録手順をまとめたものです。既存の `FishTrack/docs/deployment/GITHUB_SECRETS.md` および `MyPokedex/docs/deployment/GITHUB_SECRETS.md` の内容を統合し、MyHobbySite リポジトリで一元管理します。

---

## 1. Secrets 一覧

### 1.1 FishTrack リポジトリ

| Secret 名 | 用途 | 推奨値の例 | 設定状況 |
| --- | --- | --- | --- |
| `FISHTRACK_SSH_HOST` | 本番サーバーのホスト名 / IP | `192.168.68.71` | ✅ 設定済み |
| `FISHTRACK_SSH_USER` | SSHユーザー名 | `pi` | ✅ 設定済み |
| `FISHTRACK_SSH_KEY` | SSH秘密鍵（PEM全文） | `-----BEGIN OPENSSH PRIVATE KEY----- ...` | ✅ 設定済み |
| `FISHTRACK_SECRET_KEY` | Flask SECRET_KEY | `python3 -c "import secrets; print(secrets.token_hex(32))"` | ✅ 設定済み (2025-11-26) |
| `FISHTRACK_DATABASE_URL` | DB接続文字列 | `sqlite:////home/pi/FishTrack/data/fishtrack.db` | ✅ 設定済み |
| `FISHTRACK_ENABLE_SELF_REGISTER` | 環境変数 | `false` | ✅ 設定済み |
| その他必要なENV | APIキー等 | 本番値 | ✅ 設定済み |

### 1.2 MyPokedex リポジトリ

| Secret 名 | 用途 | 推奨値の例 | 設定状況 |
| --- | --- | --- | --- |
| `MYPDEX_SSH_HOST` | 本番サーバーのホスト名 / IP | `192.168.68.71` | ✅ 設定済み |
| `MYPDEX_SSH_USER` | SSHユーザー名 | `pi` | ✅ 設定済み |
| `MYPDEX_SSH_KEY` | SSH秘密鍵（PEM全文） | `-----BEGIN OPENSSH PRIVATE KEY----- ...` | ✅ 設定済み |
| `MYPDEX_SECRET_KEY` | Flask SECRET_KEY | `python3 -c "import secrets; print(secrets.token_hex(32))"` | ✅ 設定済み |
| `MYPDEX_DATABASE_URL` | DB接続文字列 | `sqlite:////home/pi/MyPokedex/data/mypokedex.db` | ✅ 設定済み |
| `ENABLE_SELF_REGISTER` | 環境変数 | `false` | ✅ 設定済み |
| その他必要なENV | メール/APIキー等 | 本番値 | ✅ 設定済み |

> **メモ**: SECRET_KEY や DB URL は本番サーバー上の `/etc/fishtrack.env` / `/etc/mypokedex.env` と同じ値に揃えてください。

### 1.3 設定状況サマリー（2025-11-26 時点）

**✅ すべての Secrets が設定完了しました！**

**最新の設定完了項目:**
- `FISHTRACK_SECRET_KEY` - Flask SECRET_KEY（FishTrack）✅ 2025-11-26 設定完了
- `MYPDEX_SSH_PASSPHRASE` - SSH秘密鍵パスフレーズ（MyPokedex）✅ 2025-11-26 設定完了

**設定済みの Secrets:**
- FishTrack および MyPokedex のすべての必要な Secrets は GitHub に設定済み
- CI/CD デプロイの準備が整いました

---

## 2. GitHub Secrets 登録手順

1. 対象リポジトリ（例: `aki-nagatani/FishTrack`）の GitHub ページを開く  
2. `Settings` → `Secrets and variables` → `Actions` を選択  
3. `New repository secret` をクリック  
4. `Name` に上記の Secret 名を入力し、`Secret` に値を貼り付けて `Add secret`  
5. すべての必要な Secret について繰り返す  
6. self-hosted runner に `self-hosted`, `linux`, `fishtrack` / `mypokedex` などのラベルを設定し、Secrets にアクセスできる権限を確認

---

## 3. 値の準備と管理

### 3.1 SECRET_KEY 生成方法

SECRET_KEYは、FlaskアプリケーションでセッションやCSRFトークンの暗号化に使用される重要な秘密鍵です。**本番サーバー上の環境変数ファイル（`/etc/fishtrack.env` / `/etc/mypokedex.env`）と同じ値を使用する必要があります。**

#### 方法1: 本番サーバーで既存の値を確認（推奨）

既に本番サーバーにSECRET_KEYが設定されている場合は、その値をそのまま使用します：

```bash
# 本番サーバーにSSH接続して確認
ssh pi@192.168.68.71
cat /etc/fishtrack.env | grep SECRET_KEY
# または
cat /etc/mypokedex.env | grep SECRET_KEY
```

#### 方法2: 新しいSECRET_KEYを生成（本番環境で生成を推奨）

**⚠️ 重要: 新規生成は本番環境（Raspberry Piサーバー）で実施することを推奨します。**

**理由:**
- 本番環境で生成することで、そのまま `/etc/*.env` に設定でき、値の同期ミスを防げます
- 生成した値をそのままGitHub Secretsに登録すれば、両方の場所で同じ値が保証されます

**手順:**

1. **本番サーバーにSSH接続:**
   ```bash
   ssh pi@192.168.68.71
   ```

2. **本番サーバー上でSECRET_KEYを生成:**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **生成された値を控える:**
   ```
   a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
   ```

4. **本番サーバーの環境変数ファイルに設定:**
   ```bash
   # FishTrackの場合
   sudo nano /etc/fishtrack.env
   # SECRET_KEY=生成した値を追記または更新
   
   # MyPokedexの場合
   sudo nano /etc/mypokedex.env
   # SECRET_KEY=生成した値を追記または更新
   ```

5. **GitHub Secretsに同じ値を登録:**
   - `FISHTRACK_SECRET_KEY` または `MYPDEX_SECRET_KEY` に、上記で生成した値を登録

**代替方法: ローカル環境で生成する場合**

ローカル環境（Windows PowerShell等）で生成する場合も可能ですが、**必ず本番サーバーの環境変数ファイルとGitHub Secretsの両方に同じ値を設定してください。**

**Windows PowerShell:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**Linux / macOS / WSL:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### 方法3: Pythonスクリプトで生成

より詳細な制御が必要な場合（本番環境で実行）:

```python
import secrets
# 64文字の16進数文字列（32バイト）を生成
secret_key = secrets.token_hex(32)
print(secret_key)
```

#### 注意事項

- **既存の本番環境がある場合**: 必ず既存のSECRET_KEYを確認し、同じ値を使用してください。異なる値に変更すると、既存のセッションが無効になります。
- **新規環境の場合**: **本番環境で生成することを推奨**します。生成後、その値をGitHub Secretsにも登録してください。
- **値の保存**: 生成したSECRET_KEYは安全な場所に控えを保管してください（GitHub Secretsには再表示できないため）。
- **本番サーバーとの同期**: GitHub Secretsに登録した値は、必ず本番サーバーの環境変数ファイル（`/etc/fishtrack.env` / `/etc/mypokedex.env`）にも**同じ値**を設定してください。値が異なるとアプリケーションが正常に動作しません。

### 3.2 SSH鍵生成手順（パスフレーズ必須運用）  
  1. ローカル端末（PowerShell）で以下を実行し、必要に応じて `.ssh` ディレクトリを作成してから鍵を生成  
     ```powershell
     ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\fishtrack_ci" -C "fishtrack-ci"
     ```
     - 保存先とパスフレーズ入力を求められたら**必ずパスフレーズを設定**し、後述の Secret に控える  
     - 生成物: `C:\Users\<User>\.ssh\fishtrack_ci`（秘密鍵）と `C:\Users\<User>\.ssh\fishtrack_ci.pub`（公開鍵）  
  2. MyPokedex 用は `ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\mypokedex_ci" -C "mypokedex-ci"` のように別名で作成  
  3. 秘密鍵（`*.pub` が付かないファイル）を GitHub Secrets（`FISHTRACK_SSH_KEY` / `MYPDEX_SSH_KEY`）へ登録  
  4. 公開鍵（`*.pub`）の内容を本番サーバーの `~/.ssh/authorized_keys` へ追記し、`chmod 600 ~/.ssh/authorized_keys` を維持  
     - FishTrack / MyPokedex の公開鍵は 2025-11-25 時点で本番サーバーへ配置済み  
  5. 設定したパスフレーズは `FISHTRACK_SSH_PASSPHRASE` / `MYPDEX_SSH_PASSPHRASE` に登録し、Workflow 内で `ssh-agent` に渡す  
  6. 生成した鍵ペアはローカルの安全な場所に控えを残し、紛失時は必ず新しい鍵を再生成して登録し直す  
- **SQLite パス**: `sqlite:////home/pi/...` 形式（スラッシュ4個で絶対パスを指定）  
- **パスフレーズ付き鍵**を使う場合は別Secretに保存し、Workflowで `ssh-agent` に渡す  
- SecretsはGitHub UI上で一度登録すると値を再表示できないため、必ずローカルの安全な場所に控えを保管する  
- 値の更新時は、GitHub Secretsと `/etc/*.env` の両方を同日に入れ替え、CI/CDジョブのテストを実施

---

## 4. Workflow からの利用例

```yaml
- name: Setup SSH
  uses: webfactory/ssh-agent@v0.9.0
  with:
    ssh-private-key: ${{ secrets.FISHTRACK_SSH_KEY }}
    ssh-passphrase: ${{ secrets.FISHTRACK_SSH_PASSPHRASE }}

- name: Deploy FishTrack
  run: |
    rsync -az src/ ${{ secrets.FISHTRACK_SSH_USER }}@${{ secrets.FISHTRACK_SSH_HOST }}:/home/pi/FishTrack/releases/${GITHUB_SHA}/src
    ssh ${{ secrets.FISHTRACK_SSH_USER }}@${{ secrets.FISHTRACK_SSH_HOST }} 'cd /home/pi/FishTrack/current && sudo systemctl restart fishtrack'
```

> MyPokedex も同様に `secrets.MYPDEX_*` を参照すればよい構成です。

---

## 5. Runner / インフラ前提

- self-hosted runner は本番サーバーまたは同一ネットワーク上で稼働させ、`sudo systemctl restart ...` を実行できる権限を持たせる  
- Runner ラベルの例: `self-hosted`, `linux`, `fishtrack` / `mypokedex`  
- CI/CD ワークフローにはヘルスチェック（`curl https://www.yume-eita.com/fishtrack/healthz` 等）とロールバックジョブを実装し、Secrets の設定漏れを早期に検知する

以上で、Secrets に関する手順をMyHobbySiteリポジトリで集約管理できるようになりました。

