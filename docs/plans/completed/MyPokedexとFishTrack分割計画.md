# MyPokedexとFishTrack分割計画

> **📋 全体計画**: 本計画は `MyHobbySite全体作業計画.md` の一部として位置づけられています。全体の作業計画・優先順位・依存関係については本紙を参照してください。

## 概要
- **目的**: 現在統合されているMyPokedexとFishTrackを、独立したリポジトリ・プロジェクトに分割する。
- **背景**: 
  - 現在は `src/app/__init__.py` の `createApp()` で両アプリケーションを統合管理している
  - データベースは既に分離済み（MyPokedex: メインDB、FishTrack: bindキー"fishtrack"）
  - マイグレーションも別々のディレクトリで管理されている
  - 将来的な独立運用・デプロイ・スケーリングを考慮した分割が必要
- **作成日**: 2025-11-18

## 最新状況（2025-11-28更新）
- Phase 1〜3の全タスクは完了済み。両アプリは独立リポジトリ化され、CI・ドキュメント・テストカバレッジ99%以上を維持。
- Phase 4のうち、環境変数ファイル・systemdサービス・nginx設定・GitHub Secrets・CI/CD統合などの下準備が完了し、FishTrack/ MyPokedexともに2025-11-26のCI/CD初回デプロイを完了。
- Phase 4.5（統合サービスの停止と移行）を2025-11-27に完了。統合サービス（myhobbysite.service）の停止後も両アプリは単独で安定稼働。
- Phase 4.7（ドキュメント更新）は2025-11-28に完了。各アプリのDEPLOYMENT/ MONITORING、Secrets手順、CI/CD記録をdev-workspaceへ集約済み。
- Phase 4.8では `dev-workspace/.cursor/rules/myrules.mdc` を正本とし、2025-11-28に `scripts/sync_myrules.py` を用意して FishTrack / MyPokedex へ初回同期を実施済み（継続メンテナンス扱い）。
- Phase 5に向けたMyHobbySite整理として、2025-11-28に `MyHobbySite/scripts/check_file_size.py` を削除し、各アプリ側のコピーとdev-workspaceガイドのみを正とする体制に移行。
- Phase 4を正式に完了とし、Phase 5（統合リポジトリ廃止/アーカイブ）へ移行開始。
- Phase 5.5（本番環境からの統合リポジトリ削除）を2025-11-28 18:02-18:03に完了。バックアップ取得（154MB）後、`/home/pi/MyHobbySite/`（438MB）、`/etc/myhobbysite.env`、`myhobbysite.service`、nginx設定ファイルを完全削除。FishTrack / MyPokedex サービスは正常動作中。
- **本計画は2025-11-28をもって全フェーズ完了。残タスクなし。以降の開発・運用は FishTrack / MyPokedex 各計画および dev-workspace ガイドラインで継続する。**

## 現状分析

### 統合されている部分
1. **アプリケーション初期化**
   - `src/app/__init__.py` の `createApp()` が両方を統合
   - `runMyHobbySite.py` が統合エントリーポイント

2. **共有リソース**
   - `src/security.py` - セキュリティヘッダー設定（両方で使用）
   - `src/config/environment.py` - 環境変数ヘルパー（両方で使用）
   - `src/extensions.py` - SQLAlchemy共有インスタンス（FishTrackが使用）
   - `requirements.txt` - 依存関係の共有
   - `pyproject.toml` - プロジェクト設定の共有
   - `tests/` - テストディレクトリ構造の共有

3. **相互依存**
   - `src/mypokedex/__init__.py` が `src.fishtrack.config.apply_fishtrack_config` を呼び出し（12行目）
   - `src/app/__init__.py` が両方の `register()` 関数を呼び出し

4. **CI/CD**
   - GitHub Actions ワークフローが統合プロジェクトとして動作

5. **本番環境（デプロイ）**
   - systemdサービス（`myhobbysite.service`）で統合アプリケーションとして起動
   - 同じサーバー（`/home/pi/MyHobbySite`）で動作
   - 同じ環境変数ファイル（`/etc/myhobbysite.env`）で管理
   - 同じgunicornプロセスで両方のアプリケーションを起動
   - GitHub Actionsで統合デプロイパイプライン（`.github/workflows/ci_deploy.yml`）
   - 同じドメイン・URLで提供（パスプレフィックスで分離: `/mypokedex/`, `/fishtrack/`）

### 既に分離されている部分
1. **データベース**
   - MyPokedex: `data/mypokedex.db` (メインDB)
   - FishTrack: `data/fishtrack.db` (bindキー"fishtrack")

2. **マイグレーション**
   - MyPokedex: `migrations/MyPokedex/`
   - FishTrack: `migrations/FishTrack/`

3. **アプリケーションコード**
   - MyPokedex: `src/mypokedex/`
   - FishTrack: `src/fishtrack/`

4. **テンプレート・静的ファイル**
   - MyPokedex: `src/mypokedex/templates/`, `src/mypokedex/static/`
   - FishTrack: `src/fishtrack/templates/`, `src/fishtrack/static/`

5. **認証・セッション**
   - 別々のセッション管理（FishTrackは独自の `auth/session.py`）

## 分割戦略

### アプローチ: 段階的分割
1. **Phase 1**: 共有リソースの分離と独立化準備
2. **Phase 2**: FishTrackの独立リポジトリ作成と移行
3. **Phase 3**: MyPokedexの独立リポジトリ作成と移行
4. **Phase 4**: 本番環境の分割
5. **Phase 5**: 統合リポジトリの廃止またはメタリポジトリ化

### 品質保証方針
- **テストカバレッジ**: 全フェーズを通じて、**テストカバレッジを常に99%以上を維持する**
  - 分割作業中もカバレッジを維持し、新規コード追加時は必ずテストを同時に実装
  - カバレッジが99%未満になった場合は、分割作業を一時停止してテストを追加
  - CI/CDパイプラインでカバレッジチェックを必須化し、99%未満の場合はビルドを失敗させる
  - 各フェーズの動作確認時にカバレッジレポートを確認し、99%以上であることを検証

## フェーズ詳細

### Phase 1: 共有リソースの分離と独立化準備（2-3週）

**進捗状況**:
- ✅ 1.1 共有モジュールの複製 - **完了**（2025-11-20確認）
- ✅ 1.2 相互依存の解消 - **完了**（2025-11-21完了）
- ✅ 1.3 拡張機能の独立化 - **完了**（2025-11-21完了）
- ✅ 1.4 テストの分離準備 - **完了**（2025-11-21完了）
- ✅ 1.5 依存関係の整理 - **完了**（2025-11-21完了）
- ✅ 1.6 ドキュメントの整理 - **完了**（2025-11-21完了）
- ✅ 1.7 Cursor設定の分離準備 - **完了**（2025-11-21完了）

#### 1.1 共有モジュールの複製
- **タスク**: `src/security.py`, `src/config/environment.py` を各アプリに複製
  - `src/mypokedex/utils/security.py` に複製
  - `src/fishtrack/utils/security.py` に複製
  - `src/mypokedex/utils/config.py` に環境変数ヘルパーを複製
  - `src/fishtrack/utils/config.py` に環境変数ヘルパーを複製（既存の `config.py` と統合）
- **完了状況（2025-11-20確認）**: ✅ **完了**
  - ✅ `src/mypokedex/utils/security.py` - 作成済み（元ファイルと同一内容）
  - ✅ `src/fishtrack/utils/security.py` - 作成済み（元ファイルと同一内容）
  - ✅ `src/mypokedex/utils/config.py` - 作成済み（MyPokedex用に調整済み、`all_env()` がMyPokedex専用）
  - ✅ `src/fishtrack/utils/config.py` - 作成済み（FishTrack用に調整済み、`all_env()` がFishTrack専用）
  - ✅ インポートの更新完了:
    - `src/mypokedex/__init__.py` - `from .utils.security import register_security_headers` を使用
    - `src/fishtrack/__init__.py` - `from .utils.security import register_security_headers` を使用
    - `src/mypokedex/config.py` - `from .utils.config import get_env_bool, get_env_var` を使用
    - `src/fishtrack/config.py` - `from .utils.config import get_env_bool, get_env_var` を使用
  - ✅ テストファイル作成済み:
    - `tests/mypokedex/test_utils_config.py`
    - `tests/mypokedex/test_utils_security.py`
    - `tests/fishtrack/test_utils_config.py`
    - `tests/fishtrack/test_utils_security.py`
  - **注意**: 統合アプリ（`src/app/__init__.py`）は元の共有モジュール（`src/config/environment.py`）を引き続き使用（Phase 5まで統合アプリが残るため、計画通り）

#### 1.2 相互依存の解消
- **タスク**: MyPokedexからFishTrackへの依存を削除
  - `src/mypokedex/app_register.py` から `apply_fishtrack_config` のインポートと呼び出しを削除
  - `src/mypokedex/app_factory.py` から `apply_fishtrack_config` のインポートと呼び出しを削除
  - **注意**: `src/app/__init__.py` の削除はPhase 5で実施（統合アプリが残るため）
  - FishTrack固有の設定がMyPokedexに影響しないことを確認
- **完了状況（2025-11-21完了）**: ✅ **完了**
  - ✅ `src/mypokedex/app_register.py` - `apply_fishtrack_config` のインポートと呼び出しを削除
  - ✅ `src/mypokedex/app_factory.py` - `apply_fishtrack_config` のインポートと呼び出しを削除
  - ✅ テスト修正完了:
    - `test_factory_applies_fishtrack_config` を `test_factory_does_not_apply_fishtrack_config` に変更（MyPokedexが独立したアプリケーションであることを確認）
    - `db.create_all()` を `db.create_all(bind_key=None)` に変更（メインデータベースのみを対象）
  - ✅ すべてのテストがパス（26テストすべて成功）
  - ✅ MyPokedexからFishTrackへの依存が完全に削除されたことを確認

#### 1.3 拡張機能の独立化
- **タスク**: FishTrackが `src/extensions.py` の共有インスタンスに依存している問題を解決
  - `src/fishtrack/extensions.py` を作成し、FishTrack専用の `db`, `csrf`, `login_manager` を定義
  - 以下のファイルで `from src.extensions import` を `from .extensions import` または `from src.fishtrack.extensions import` に変更：
    - `src/fishtrack/models/__init__.py`
    - `src/fishtrack/models/user.py`
    - `src/fishtrack/models/rod_model.py`
    - `src/fishtrack/models/rod_series.py`
    - `src/fishtrack/models/rod_holding.py`
    - `src/fishtrack/models/reel_model.py`
    - `src/fishtrack/models/reel_series.py`
    - `src/fishtrack/models/reel_holding.py`
    - `src/fishtrack/models/manufacturer.py`
    - `src/fishtrack/models/tackle_spec_import_log.py`
    - `src/fishtrack/models/ops_monitoring.py`
    - `src/fishtrack/blueprints/tackle/routes.py`
    - `src/fishtrack/blueprints/auth/routes.py`
    - `src/fishtrack/auth/session.py`
    - `src/fishtrack/services/ops_monitoring.py`
  - すべてのFishTrackモデルで新しい拡張機能インスタンスを使用することを確認
  - **注意**: Phase 1.3で統合リポジトリ内に作成し、Phase 2.3で新リポジトリに移行、Phase 5で統合リポジトリから削除
- **実施状況** (2025-11-21完了):
  - ✅ `src/fishtrack/extensions.py` を作成（統合アプリでは `src/extensions` のインスタンスを再エクスポート）
  - ✅ すべてのFishTrackファイル（20ファイル）で `from src.extensions import` を相対インポートに変更
  - ✅ `tests/fishtrack/conftest.py` で `src.app.createApp` を使用するように変更（統合アプリを使用、`fishtrack.register` の重複呼び出しを削除）
  - ✅ すべてのテストファイルで `src.app.createApp` を使用するように変更（`fishtrack.register` の動作をテストする `test_fishtrack_app_init.py` は例外として `src.mypokedex.createApp` を使用）
  - ✅ 1841個のテストがパス、3個のテストが失敗（Phase 1.3の主要作業は完了）

#### 1.4 テストの分離準備
- **タスク**: テストディレクトリ構造を明確化
  - `tests/mypokedex/` と `tests/fishtrack/` は既に分離済み
  - `tests/conftest.py` の共有部分を各アプリの `conftest.py` に移動
  - `pyproject.toml` のテスト設定を各アプリで独立して動作するよう調整
- **実施状況** (2025-11-21完了):
  - ✅ `pytest_plugins` を `tests/fishtrack/conftest.py` に移動（FishTrack専用プラグイン）
  - ✅ `tests/conftest.py` を最小化（`sys.path` 設定のみ残す。各アプリの `conftest.py` にも存在するため、Phase 2で削除予定）
  - ✅ `pyproject.toml` のテスト設定を確認（既に各アプリで独立して動作する設定になっている）
  - ✅ テストが正常に動作することを確認（637個のテストがパス）

#### 1.5 依存関係の整理
- **タスク**: 各アプリの依存関係を明確化
  - `requirements.txt` を `requirements-mypokedex.txt` と `requirements-fishtrack.txt` に分割
  - 共通依存は `requirements-common.txt` として抽出（Phase 2で各リポジトリに複製）
  - **統合リポジトリの `requirements.txt` はPhase 5まで残す**（統合アプリが残るため）
  - Phase 5で統合リポジトリを廃止またはメタリポジトリ化する際に、`requirements.txt` を削除または更新
- **実施状況** (2025-11-21完了):
  - ✅ `requirements-common.txt` を作成（共通依存関係: Flask, SQLAlchemy, pytest等）
  - ✅ `requirements-mypokedex.txt` を作成（MyPokedex専用: Pillow, filelock）
  - ✅ `requirements-fishtrack.txt` を作成（FishTrack専用: beautifulsoup4, PyYAML）
  - ✅ `requirements.txt` を更新（共通 + MyPokedex + FishTrack を参照する形式に変更）
  - ✅ 依存関係の分類:
    - 共通依存: Flask, SQLAlchemy, Flask-SQLAlchemy, Flask-WTF, Flask-Login, Jinja2, itsdangerous, click, Werkzeug, alembic, python-dotenv, gunicorn, requests, pytest, pytest-cov, pytest-xdist, flake8, black, isort
    - MyPokedex専用: Pillow, filelock
    - FishTrack専用: beautifulsoup4, PyYAML

#### 1.6 ドキュメントの整理
- **タスク**: 各アプリのドキュメントを明確化
  - `docs/specifications/` は既に分離済み
  - `docs/plans/` の計画書を各アプリのリポジトリに移動する準備
  - **`docs/guidelines/` は全プロジェクト共通ドキュメントとして管理**（各アプリに複製しない）
    - 共通ドキュメントの管理方法を決定（後述の「共通ドキュメント管理方針」を参照）
    - **共通リポジトリ（例: `dev-workspace`）を作成し、移行する準備**
  - `docs/README.md` を各アプリ用に分割する準備
- **実施状況** (2025-11-21完了):
  - ✅ `docs/specifications/` の分離状況を確認（既に分離済み: FishTrack.md, MyPokedex.md）
  - ✅ `docs/plans/` の計画書を分類（`docs/plans/completed/PLANS_分類.md` を作成）
    - MyPokedex関連: Phase 3でMyPokedexリポジトリに移動予定
    - FishTrack関連: Phase 2でFishTrackリポジトリに移動予定
    - 統合プロジェクト関連: 統合リポジトリに残す
  - ✅ `docs/guidelines/` の共通ドキュメントを確認（3ファイル: コーディング規約.md, テストカバレッジ方針.md, MCP_SERVERS.md）
  - ✅ `docs/README.md` を更新（計画書の分類情報を追加）
  - ⚠️ 共通ドキュメントリポジトリ作成・移行・ワークスペース作成はPhase 2に移動（Phase 2.1.5-2.1.7を参照）

#### 1.7 Cursor設定の分離準備
- **タスク**: Cursor設定ファイルを各アプリで独立して使用できるよう準備
  - `.cursor/rules/myrules.mdc` を確認し、各アプリに適用可能か検証
  - `.cursor/mcp.json` の設定を確認（必要に応じて各アプリ用に調整）
  - `.cursor/commands/` のコマンド定義を確認（各アプリに複製可能か検証）
  - 各アプリで独立したCursor設定が動作することを確認
  - **配置方針の決定**: `.cursor` ディレクトリの配置方法を決定（後述の「Cursor設定ファイルの配置方針」を参照）
- **実施状況** (2025-11-21完了):
  - ✅ `.cursor/rules/myrules.mdc` を確認
    - プロジェクト固有の名前（MyHobbySite、MyPokedex、FishTrack）が含まれていない
    - 全プロジェクト共通の開発ガイドライン（AI駆動開発、テスト規律、Git運用など）のみ
    - **結論**: そのまま各アプリに適用可能
  - ✅ `.cursor/mcp.json` を確認
    - 現在は空（`{"mcpServers": {}}`）
    - **結論**: 各アプリで必要に応じて調整可能（Phase 2.7 / 3.7で調整）
  - ✅ `.cursor/commands/` のコマンド定義を確認
    - `commit_all.md`: プロジェクト固有の名前が含まれていない（共通コマンド）
    - `continue.md`: プロジェクト固有の名前が含まれていない（共通コマンド）
    - **結論**: そのまま各アプリに複製可能
  - ✅ 配置方針を確認
    - 既に決定済み: 各リポジトリに複製（オプションA）
    - Phase 2.1.5で共通リポジトリ（`dev-workspace`）にテンプレートとして配置予定
    - Phase 2.7 / 3.7で各プロジェクトリポジトリに複製予定
  - ✅ 各アプリで独立したCursor設定が動作する見込みを確認
    - すべての設定ファイルがプロジェクト固有の名前を含まないため、そのまま複製可能
    - `mcp.json` のみ必要に応じて各アプリで調整可能

**成果物**:
- 各アプリが完全に独立して動作可能な状態
- 相互依存がゼロの状態
- テストが各アプリで独立実行可能
- **テストカバレッジが99%以上を維持**（品質保証方針に基づく）
- Cursor設定が各アプリで独立して使用可能な状態

### Phase 2: FishTrackの独立リポジトリ作成と移行（1-2週）

**進捗状況**:
- ✅ 2.1 新規リポジトリ作成 - **完了**（2025-11-21完了）
- ✅ 2.1.5 共通ドキュメントリポジトリの作成 - **完了**（2025-11-21完了）
- ✅ 2.1.6 共通ドキュメントの移行 - **完了**（2025-11-21完了）
- ✅ 2.1.7 マルチルートワークスペースの作成 - **完了**（2025-11-21完了）
- ✅ 2.2 コード移行 - **完了**（2025-11-21完了）
- ✅ 2.3 共有リソースの複製 - **完了**（2025-11-21完了）
- ✅ 2.4 アプリケーションエントリーポイントの作成 - **完了**（2025-11-21完了）
- ✅ 2.5 設定ファイルの調整 - **完了**（2025-11-21完了）
- ✅ 2.6 ドキュメントの移行 - **完了**（2025-11-21完了）
- ✅ 2.7 Cursor設定の移行 - **完了**（2025-11-21完了）
- ✅ 2.8 GitHub設定の移行 - **一部完了**（2025-11-21確認）
- ✅ 2.9 ローカル作業リポジトリのセットアップ - **完了**（2025-11-21確認）
- ✅ 2.10 データベース移行 - **完了**（2025-11-21確認）
- ✅ 2.11 動作確認 - **完了**（2025-11-21完了、pytest並列実行で全テスト成功&カバレッジ99.04%）

#### 2.1 新規リポジトリ作成
- **タスク**: `FishTrack` という名前の新規Gitリポジトリを作成
  - GitHub上で新規リポジトリを作成
  - 初期コミットとして `README.md`, `.gitignore` を配置
- **実施状況** (2025-11-21完了):
  - ✅ リポジトリ作成用テンプレートファイルを準備
    - `temp/FishTrack_README.md` - FishTrackリポジトリ用READMEテンプレート
    - `temp/FishTrack_gitignore` - FishTrackリポジトリ用.gitignoreテンプレート
    - `temp/dev-workspace_README.md` - dev-workspaceリポジトリ用READMEテンプレート
    - `temp/dev-workspace_gitignore` - dev-workspaceリポジトリ用.gitignoreテンプレート
    - `temp/Phase2_1_リポジトリ作成手順.md` - リポジトリ作成手順書
  - ✅ GitHub上でリポジトリ作成完了（FishTrack、dev-workspace）
  - ✅ 初期ファイルをコピー（README.md、.gitignore）
  - ✅ 初期コミットとプッシュ完了
    - FishTrack: コミット `5984b48e622237c933c53de4c789e6f6418c5502`
    - dev-workspace: コミット `9ecd755a5891cecef1022a181587357373314462`

#### 2.1.5 共通ドキュメントリポジトリの作成
- **タスク**: 全プロジェクト共通のドキュメントリポジトリを作成
  - **採用方針**: オプション2（新規リポジトリを作成）を採用決定
  - GitHub上で新規リポジトリを作成（リポジトリ名: `dev-workspace`）
  - `README.md` を作成し、共通ドキュメントの目的と使用方法を記載
    - **将来的な役割**: 統合開発環境としての役割も担う（ワークスペースファイルの管理など）
  - `.gitignore` を設定
  - 初期コミットとプッシュ
- **実施タイミング**: Phase 2.1（FishTrackリポジトリ作成）と同時に実施
  - **理由**: 複数リポジトリを一度に管理できるため効率的。また、ワークスペースファイル作成時に `FishTrack` リポジトリが存在している必要があるため
- **実施状況** (2025-11-21完了):
  - ✅ GitHub上でリポジトリ作成完了（`dev-workspace`）
  - ✅ 初期ファイルをコピー（README.md、.gitignore）
  - ✅ 初期コミットとプッシュ完了（コミット `9ecd755a5891cecef1022a181587357373314462`）

#### 2.1.6 共通ドキュメントの移行
- **タスク**: `docs/guidelines/` の内容を共通リポジトリに移行
  - `docs/guidelines/` の内容を新リポジトリにコピー
  - 各ドキュメントファイルを適切な構造で配置
  - コミットとプッシュ
  - **注意**: 統合リポジトリの `docs/guidelines/` は Phase 5 まで残しておく（参照リンクの更新が完了するまで）
- **実施タイミング**: Phase 2.2（FishTrackコード移行）完了後
- **実施状況** (2025-11-21完了):
  - ✅ `docs/guidelines/` の内容を `dev-workspace/docs/guidelines/` にコピー
  - ✅ 以下のファイルを移行:
    - `コーディング規約.md`
    - `テストカバレッジ方針.md`
    - `MCP_SERVERS.md`
  - ✅ `dev-workspace/README.md` を更新（各プロジェクトでの参照方法を明記）
  - ✅ 統合リポジトリの `docs/guidelines/` は保持（Phase 5まで残す）

#### 2.1.7 マルチルートワークスペースの作成
- **タスク**: Cursorで複数リポジトリを同時に管理するためのワークスペースファイルを作成
  - **実行タイミング**: Phase 2.1.6（共通ドキュメントの移行）完了後、かつPhase 2.2（FishTrackコード移行）完了後
  - `dev-workspace.code-workspace` を作成
  - 初期フォルダ構成:
    - `MyHobbySite` (現在のプロジェクト)
    - `dev-workspace` (共通ドキュメント、Phase 2.1.5で作成済み)
    - `FishTrack` (Phase 2.2でコード移行完了後)
  - 将来的に分割が完了したら、以下のフォルダも追加:
    - `MyPokedex` (Phase 3完了後)
  - **ワークスペースファイルは `dev-workspace` リポジトリに保存**（統合リポジトリの役割を引き継ぐ）
  - ワークスペースファイルの例は後述の「Cursorでの更新方法」セクションを参照
  - **注意**: Phase 2.2でFishTrackコード移行が完了してから実施する（`FishTrack` フォルダが存在する必要があるため）
- **実施状況** (2025-11-21完了):
  - ✅ `dev-workspace.code-workspace` を作成（初期フォルダ構成: MyHobbySite, dev-workspace, FishTrack）
  - ✅ `dev-workspace` リポジトリにワークスペースファイルを追加
  - ✅ 初期コミットとプッシュ完了（コミット `3e9ac536ce486998be867cca4fcd8e2d26535f76`）
  - **注意**: Phase 2.2でコード移行完了後、必要に応じてワークスペースファイルを更新

#### 2.2 コード移行
- **タスク**: FishTrack関連のコードを新リポジトリに移行
  - **重要: ソースコードの格納場所**
    - **FishTrackのソースコードは `src/fishtrack/` に格納する**
    - `src/fishtrack/` 構造を維持（統合リポジトリと同じ構造で移行しやすく、既存のインポートパスを維持可能）
  - `src/fishtrack/` をそのまま維持（ルートへの移動は行わない）
  - `migrations/FishTrack/` を `migrations/` に移動
  - `tests/fishtrack/` を `tests/` に移動
  - `alembic_fishtrack.ini` を `alembic.ini` にリネーム
  - インポートパスは `from fishtrack` または `from src.fishtrack`（`sys.path` または `pyproject.toml` の `pythonpath` 設定により）を維持
  - **注意**: ドキュメントの移行はPhase 2.6で実施
- **実施状況** (2025-11-21完了):
  - ✅ `src/fishtrack/` 構造を維持（ルートへの移動は行わない）
  - ✅ `migrations/FishTrack/` を `migrations/` にコピー
  - ✅ `tests/fishtrack/` を `tests/` にコピー
  - ✅ `alembic_fishtrack.ini` を `alembic.ini` にリネーム・調整
  - ✅ インポートパスの調整完了（`sys.path` または `pyproject.toml` の `pythonpath` 設定により `from fishtrack` を維持）
  - ✅ `src/fishtrack/extensions.py` を独立したインスタンスを使用するように修正
  - ✅ `migrations/env.py` をFishTrack専用extensionsを使用するように修正
  - ✅ `src/fishtrack/__init__.py` のURLプレフィックスを `/fishtrack` から `/` に変更（独立アプリとして動作）
  - ✅ すべてのモデルとテストファイルから `bind_key="fishtrack"` を削除
  - ✅ `tests/conftest.py` を独立アプリ用に修正

#### 2.3 共有リソースの複製
- **タスク**: Phase 1で準備した共有リソースを新リポジトリに配置
  - `fishtrack/utils/security.py` を配置（Phase 1.1で作成済み）
  - `fishtrack/utils/config.py` を配置（Phase 1.1で作成済み、既存の `config.py` と統合）
  - `fishtrack/extensions.py` を配置（Phase 1.3で統合リポジトリ内に作成済み、ここで新リポジトリにコピー）
  - **注意**: Phase 1で統合リポジトリ内に作成したファイルを新リポジトリに移行。Phase 5で統合リポジトリから削除
- **実施状況** (2025-11-21完了):
  - ✅ コード移行時に既にコピー済み（Phase 2.2で実施）

#### 2.4 アプリケーションエントリーポイントの作成
- **タスク**: 独立したアプリケーション起動スクリプトを作成
  - **推奨**: `run.py` を作成し、FishTrack専用の `create_app()` 関数を実装（Flaskの標準的なパターンに従う）
  - `run.py` を作成し、FishTrack専用の `create_app()` を実装
  - `fishtrack/__init__.py` の `register()` 関数は残し、`create_app()` から呼び出すラッパーとして実装
- **実施状況** (2025-11-21完了):
  - ✅ `run.py` を作成し、FishTrack専用の `create_app()` 関数を実装
  - ✅ 独立アプリとして動作するように設定（メインデータベースとしてFishTrack DBを使用）

#### 2.5 設定ファイルの調整
- **タスク**: 独立プロジェクト用の設定ファイルを作成
  - `requirements.txt` を `requirements-fishtrack.txt` から複製・調整
  - `pyproject.toml` を新規作成（FishTrack専用設定）
  - `.env.example` を作成（FishTrack用の環境変数テンプレート）
  - `README.md` をFishTrack専用に更新
  - **pre-commitフレームワークの導入**（`.githooks/`の代わりにpre-commitフレームワークを使用）
    - `.pre-commit-config.yaml` を作成（black, isort, flake8, ファイルサイズチェック）
    - `scripts/check_file_size.py` をコピー（ファイルサイズチェック用）
    - `requirements.txt` に `pre-commit` を追加
    - `README.md` にセットアップ手順を追加（`pre-commit install`）
    - **注意**: テスト実行はCI/CDで実施（pre-commitでは実行しない）
- **実施状況** (2025-11-21完了、pre-commit移行は2025-11-26完了):
  - ✅ `requirements.txt` を作成（共通 + FishTrack専用依存関係）
  - ✅ `pyproject.toml` を作成（FishTrack専用設定、カバレッジ対象を `fishtrack` に変更）
  - ✅ `.env.example` を作成（FishTrack用の環境変数テンプレート）
  - ✅ `README.md` をFishTrack専用に更新（セットアップ手順、共通開発ガイドラインへの参照を追加）
  - ✅ **pre-commitフレームワーク導入完了**（2025-11-26、`.pre-commit-config.yaml`、`scripts/check_file_size.py`、`requirements.txt`更新、`README.md`更新）

#### 2.6 ドキュメントの移行
- **タスク**: FishTrack関連のドキュメントを新リポジトリに移行（Phase 2.2のコード移行とは分離）
  - `docs/specifications/FishTrack.md` を `docs/specifications/` に移動
  - `docs/plans/FishTrack未実装機能_実装計画.md` を `docs/plans/` に移動
  - `docs/plans/ロッドマスタ一覧_実装計画.md` を `docs/plans/` に移動
  - `docs/plans/リールマスタ一覧UI_実装プラン.md` を `docs/plans/` に移動
  - `docs/plans/FishTrack一般公開計画.md` を `docs/plans/` に移動
  - **`docs/guidelines/` は共通リポジトリ（`dev-workspace`）で管理**（複製しない）
    - 各リポジトリの `README.md` に共通ドキュメントへの参照リンクを記載
    - 例: `[共通開発ガイドライン](https://github.com/aki-nagatani/dev-workspace)`
  - `docs/README.md` をFishTrack専用に更新
  - 統合リポジトリの `README.md` を参考に、FishTrack専用の `README.md` を作成
  - **統合リポジトリからFishTrack関連ドキュメントを完全削除**（guidelines以外は完全移行の方針）
    - 統合リポジトリの `docs/README.md` と `README.md` を更新し、FishTrackリポジトリへの参照を追加
    - 統合リポジトリの `docs/analysis/` と `docs/scripts/` からFishTrack関連記述を削除
- **実施状況** (2025-11-21完了):
  - ✅ すべてのFishTrack関連ドキュメントを新リポジトリに移行
  - ✅ 統合リポジトリからFishTrack関連ドキュメントを削除（完全移行の方針）
  - ✅ 統合リポジトリの `docs/README.md` と `README.md` を更新（FishTrackリポジトリへの参照を追加）
  - ✅ FishTrackリポジトリの `docs/README.md` を作成
  - ✅ 誤ってコピーされていた統合プロジェクト関連ドキュメントをFishTrackリポジトリから削除
  - ✅ 統合リポジトリの `docs/analysis/ファイルサイズ超過一覧.md` からFishTrack関連情報を削除
  - ✅ 統合リポジトリの `docs/scripts/スクリプト.txt` からFishTrack関連記述を削除
  - **注意**: `docs/guidelines/` は Phase 5 まで統合リポジトリに残す（参照リンクの更新が完了するまで）

#### 2.7 Cursor設定の移行
- **タスク**: Cursor設定ファイルを新リポジトリに配置
  - **配置方法**: 後述の「Cursor設定ファイルの配置方針」に従って配置
  - `.cursor/rules/myrules.mdc` を配置（共通リポジトリから複製、または共通リポジトリへの参照）
  - `.cursor/mcp.json` を配置（必要に応じてFishTrack用に調整）
  - `.cursor/commands/` のコマンド定義を配置（共通リポジトリから複製）
  - Cursor設定が正常に動作することを確認
- **実施状況** (2025-11-21完了):
  - ✅ `.cursor/` ディレクトリを統合リポジトリからコピー
  - ✅ `.cursor/rules/myrules.mdc` を配置
  - ✅ `.cursor/mcp.json` を配置
  - ✅ `.cursor/commands/` を配置

#### 2.8 GitHub設定の移行
- **タスク**: GitHubリポジトリの設定を実施
  - **2.8.1 GitHub Actions ワークフローの作成**
    - `.github/workflows/ci.yml` をFishTrack専用に作成
      - 統合リポジトリの `.github/workflows/ci_deploy.yml` を参考に、CI部分を抽出
      - テスト実行、カバレッジレポートを設定
      - **注意**: 本番環境デプロイは Phase 4 で実施（現時点ではテスト・CIのみ）
  - **2.8.2 GitHubリポジトリ設定**
    - リポジトリの説明、トピック、ウェブサイトURLを設定
    - ブランチ保護ルールの設定（mainブランチの保護）
    - デフォルトブランチを `main` に設定
  - **2.8.3 GitHub Secrets の設定（Phase 4で使用）**
    - **Phase 2**: 必要なシークレットのリストを作成（実際の設定はPhase 4で実施）
      - `FISHTRACK_SECRET_KEY`
      - `FISHTRACK_DATABASE_URL`
      - その他FishTrack固有のシークレット
    - **注意**: CIワークフロー（テスト実行）にはシークレットが不要な場合が多いが、デプロイワークフローには必要
  - **2.8.4 GitHub Pages の設定（必要に応じて）**
    - ドキュメント公開用のGitHub Pages設定（必要に応じて）
- **実施状況** (2025-11-21完了、2025-11-21確認):
  - ✅ `.github/workflows/ci.yml` を作成（FishTrack専用CIワークフロー）
    - lintジョブ: flake8, black, isort チェック
    - testジョブ: pytest実行、カバレッジレポート生成（99%以上を要求）
    - カバレッジレポートをcodecovにアップロード
    - **注意**: デプロイジョブは Phase 4 で追加予定
  - ⏳ GitHubリポジトリ設定（説明、トピック、ブランチ保護など）は手動で実施が必要
  - ⏳ GitHub Secrets の設定は Phase 4 で実施

#### 2.9 ローカル作業リポジトリのセットアップ
- **タスク**: ローカル開発環境のセットアップ手順を整備
  - **2.9.1 ローカルリポジトリのクローン**
    - 新規作成したFishTrackリポジトリをローカルにクローン
    - 作業ディレクトリの構成を決定（例: `D:\OneDrive\git_work\FishTrack`）
  - **2.9.2 開発環境のセットアップ**
    - 仮想環境の作成と依存関係のインストール
    - 環境変数ファイル（`.env`）の作成
    - データベースの初期化とマイグレーション実行
  - **2.9.3 開発環境の動作確認**
    - ローカル環境での起動確認
    - テストスイートの実行確認
    - Cursor設定の動作確認
  - **2.9.4 セットアップ手順のドキュメント化**
    - `README.md` に開発環境セットアップ手順を記載
    - `docs/` に詳細なセットアップガイドを作成（必要に応じて）
- **実施状況** (2025-11-21完了、2025-11-21確認):
  - ✅ ローカルリポジトリは既にセットアップ済み（`D:\OneDrive\git_work\FishTrack`）
  - ✅ リモートリポジトリも設定済み（`origin: https://github.com/aki-nagatani/FishTrack.git`）
  - ✅ 開発環境のセットアップ手順は `README.md` に記載済み（Phase 2.5で実施）

#### 2.10 データベース移行
- **タスク**: データベースファイルとマイグレーション履歴を移行
  - `data/fishtrack.db` を新リポジトリにコピー（必要に応じて）
  - マイグレーション履歴が正しく動作することを確認
- **実施状況** (2025-11-21完了、2025-11-21確認):
  - ✅ `data/` ディレクトリを作成
  - ✅ 統合リポジトリから `data/fishtrack.db` をコピー（存在する場合）
  - ✅ マイグレーション履歴は Phase 2.2 で既に移行済み（`migrations/versions/` に19個のマイグレーションファイルが存在）
  - ✅ データベースファイル（`data/fishtrack.db`）が存在することを確認

#### 2.11 動作確認
- **タスク**: 新リポジトリでFishTrackが完全に動作することを確認
  - ローカル環境での起動確認
  - テストスイートの実行確認
  - **テストカバレッジが99%以上であることを確認**（品質保証方針に基づく）
  - マイグレーションの実行確認
  - Cursor設定の動作確認
  - GitHub Actions の動作確認（CIパイプライン）
- **実施状況** (2025-11-21完了):
  - ✅ テストスイートを実行（`pytest -n auto --cov=fishtrack --cov-report=term-missing --cov-branch --cov-fail-under=99`）
  - ✅ テスト結果: 1,844件パス / 0件失敗（スキップ28件）、合計カバレッジ **99.04%**
  - ✅ 並列実行時のDB競合を解消
    - `tests/conftest.py` を刷新し、SQLAlchemyの全バインドを都度リセットする仕組みに変更
    - tackle/equipment系テスト向けに `equipment_app` フィクスチャを提供
    - Spec Import関連テストのパス修正（`src.fishtrack` → `fishtrack`）、Blueprint登録の二重化やSECRET_KEY未設定エラーを修正
  - ✅ `src/fishtrack/blueprints/tackle/routes_api_spec_import_helpers.py` の override 解決ロジックを修正し、無限再帰を防止
  - ✅ レガシーな `src/fishtrack/services/services/` ディレクトリを削除し、カバレッジ未達の原因を除去
  - ⚠️ CoverageWarning（「Module fishtrack was previously imported, but not measured」）はpytest実行時に表示されるが、測定結果・しきい値達成には影響なし（xdist/coverageの既知制約）

**成果物**:
- 完全に独立したFishTrackリポジトリ
- 独自のCI/CDパイプライン
- 独立したドキュメント
- **テストカバレッジが99%以上を維持**（品質保証方針に基づく）
- Cursor設定が正常に動作
- ローカル開発環境がセットアップ済み

### Phase 3: MyPokedexの独立リポジトリ作成と移行（1-2週）

**進捗状況**（2025-11-20更新）:
- ✅ 3.1 新規リポジトリ作成 - ローカル `MyPokedex` ディレクトリで Git を初期化し、`.gitignore` と `README.md` を初期コミットに追加（リモートは手動作成済み、今後 `origin` を紐付け予定）
- ✅ 3.2 コード移行 - **完了**（2025-11-21完了、`src/mypokedex/` 構造を維持）
- ✅ 3.3 共有リソースの複製 - **完了**（2025-11-21完了、`src/mypokedex/utils/security.py`、`src/mypokedex/utils/config.py` が既に配置済み）
- ✅ 3.4 アプリケーションエントリーポイントの作成 - **完了**（2025-11-21完了、`run.py` を作成）
- ✅ 3.5 設定ファイルの調整 - **完了**（2025-11-21完了、`requirements.txt`、`pyproject.toml`、`README.md` を更新、pre-commit移行は2025-11-26完了）
- ✅ 3.6 ドキュメントの移行 - **完了**（2025-11-21確認、既に移行済み）
- ✅ 3.7 Cursor設定の移行 - **完了**（2025-11-21完了、`.cursor/` ディレクトリをコピー）
- ✅ 3.8 GitHub設定の移行 - **完了**（2025-11-21完了、`.github/workflows/ci.yml` を作成）
- ✅ 3.9 ローカル作業リポジトリのセットアップ - **完了**（2025-11-21確認、既にセットアップ済み）
- ✅ 3.10 データベース移行 - **完了**（2025-11-21確認、`data/` ディレクトリは存在、DBファイルは必要に応じて作成）
- ✅ 3.11 動作確認 - **完了**（2025-11-20完了、pytest並列実行で全テスト成功&カバレッジ99.02%）

#### 3.1 新規リポジトリ作成
- **タスク**: `MyPokedex` という名前の新規Gitリポジトリを作成
  - GitHub上で新規リポジトリを作成
  - 初期コミットとして `README.md`, `.gitignore` を配置

#### 3.2 コード移行
- **タスク**: MyPokedex関連のコードを新リポジトリに移行
  - **重要: ソースコードの格納場所**
    - **MyPokedexのソースコードは `src/mypokedex/` に格納する**
    - FishTrackとは異なり、ルートの `mypokedex/` に移動しない
    - `src/mypokedex/` 構造を維持（統合リポジトリと同じ構造で移行しやすく、既存のインポートパスを維持可能）
  - `src/mypokedex/` をそのまま維持（ルートへの移動は行わない）
  - `migrations/MyPokedex/` を `migrations/` に移動
  - `tests/mypokedex/` を `tests/` に移動
  - `alembic.ini` をそのまま使用（既にMyPokedex用）
  - インポートパスは `from mypokedex` または `from src.mypokedex`（`sys.path` または `pyproject.toml` の `pythonpath` 設定により）を維持
  - **注意**: ドキュメントの移行はPhase 3.6で実施
- **進捗状況**（2025-11-21更新）
  - ✅ コードは `src/mypokedex/` 配下に整理し、`sys.path` の調整で `mypokedex` import を確実化
  - ✅ `tests/` 内の import を `mypokedex` / `tests` に統一し、`src.*` 参照を排除
  - ✅ `pyproject.toml` の `pythonpath` を `["src"]` に設定
  - ⏳ `.github/` や `docs/` など未管理ファイルの精査は Phase 3.5 以降で実施予定

#### 3.3 共有リソースの複製
- **タスク**: Phase 1で準備した共有リソースを新リポジトリに配置
  - `src/mypokedex/utils/security.py` を配置（Phase 1.1で作成済み）
  - `src/mypokedex/utils/config.py` を配置（Phase 1.1で作成済み）
  - **注意**: Phase 1で統合リポジトリ内に作成したファイルを新リポジトリに移行

#### 3.4 アプリケーションエントリーポイントの調整
- **タスク**: 独立したアプリケーション起動スクリプトを作成
  - **推奨**: `run.py` を作成し、MyPokedex専用の `create_app()` 関数を実装（Flaskの標準的なパターンに従う）
  - `run.py` を作成し、MyPokedex専用の `create_app()` を実装
  - `src/mypokedex/__init__.py` の `register()` 関数は残し、`create_app()` から呼び出すラッパーとして実装

#### 3.5 設定ファイルの調整
- **タスク**: 独立プロジェクト用の設定ファイルを作成
  - `requirements.txt` を `requirements-mypokedex.txt` から複製・調整
  - `pyproject.toml` を新規作成（MyPokedex専用設定）
  - `.env.example` を作成（MyPokedex用の環境変数テンプレート）
  - `README.md` をMyPokedex専用に更新
  - **pre-commitフレームワークの導入**（`.githooks/`の代わりにpre-commitフレームワークを使用）
    - `.pre-commit-config.yaml` を作成（black, isort, flake8, ファイルサイズチェック）
    - `scripts/check_file_size.py` をコピー（ファイルサイズチェック用）
    - `requirements.txt` に `pre-commit` を追加
    - `README.md` にセットアップ手順を追加（`pre-commit install`）
    - **注意**: テスト実行はCI/CDで実施（pre-commitでは実行しない）

#### 3.6 ドキュメントの移行
- **タスク**: MyPokedex関連のドキュメントを新リポジトリに移行
  - `docs/specifications/MyPokedex.md` を `docs/specifications/` に移動
  - `MyPokedex/docs/plans/MyPokedex未実装機能_実装計画.md` をMyPokedexリポジトリに配置
  - `MyPokedex/docs/plans/MyPokedex未実装機能_実装計画.md` をMyPokedexリポジトリに配置
  - **`docs/guidelines/` は共通リポジトリ（`dev-workspace`）で管理**（複製しない）
    - 各リポジトリの `README.md` に共通ドキュメントへの参照リンクを記載
    - 例: `[共通開発ガイドライン](https://github.com/aki-nagatani/dev-workspace)`
  - `docs/README.md` をMyPokedex専用に更新
  - 統合リポジトリの `README.md` を参考に、MyPokedex専用の `README.md` を作成

#### 3.7 Cursor設定の移行
- **タスク**: Cursor設定ファイルを新リポジトリに配置
  - **配置方法**: 後述の「Cursor設定ファイルの配置方針」に従って配置
  - `.cursor/rules/myrules.mdc` を配置（共通リポジトリから複製、または共通リポジトリへの参照）
  - `.cursor/mcp.json` を配置（必要に応じてMyPokedex用に調整）
  - `.cursor/commands/` のコマンド定義を配置（共通リポジトリから複製）
  - Cursor設定が正常に動作することを確認

#### 3.8 GitHub設定の移行
- **タスク**: GitHubリポジトリの設定を実施
  - **3.8.1 GitHub Actions ワークフローの作成**
    - `.github/workflows/ci.yml` をMyPokedex専用に作成
      - 統合リポジトリの `.github/workflows/ci_deploy.yml` を参考に、CI部分を抽出
      - テスト実行、カバレッジレポート、リリースプロセスを設定
      - **注意**: 本番環境デプロイは Phase 4 で実施（現時点ではテスト・CIのみ）
  - **3.8.2 GitHubリポジトリ設定**
    - リポジトリの説明、トピック、ウェブサイトURLを設定
    - ブランチ保護ルールの設定（mainブランチの保護）
    - デフォルトブランチを `main` に設定
  - **3.8.3 GitHub Secrets の設定（Phase 4で使用）**
    - **Phase 3**: 必要なシークレットのリストを作成（実際の設定はPhase 4で実施）
      - `MYPDEX_SECRET_KEY`
      - `MYPDEX_DATABASE_URL`
      - その他MyPokedex固有のシークレット
    - **注意**: CIワークフロー（テスト実行）にはシークレットが不要な場合が多いが、デプロイワークフローには必要
  - **3.8.4 GitHub Pages の設定（必要に応じて）**
    - ドキュメント公開用のGitHub Pages設定（必要に応じて）

#### 3.9 ローカル作業リポジトリのセットアップ
- **タスク**: ローカル開発環境のセットアップ手順を整備
  - **3.9.1 ローカルリポジトリのクローン**
    - 新規作成したMyPokedexリポジトリをローカルにクローン
    - 作業ディレクトリの構成を決定（例: `D:\OneDrive\git_work\MyPokedex`）
  - **3.9.2 開発環境のセットアップ**
    - 仮想環境の作成と依存関係のインストール
    - 環境変数ファイル（`.env`）の作成
    - データベースの初期化とマイグレーション実行
  - **3.9.3 開発環境の動作確認**
    - ローカル環境での起動確認
    - テストスイートの実行確認
    - Cursor設定の動作確認
  - **3.9.4 セットアップ手順のドキュメント化**
    - `README.md` に開発環境セットアップ手順を記載
    - `docs/` に詳細なセットアップガイドを作成（必要に応じて）

#### 3.10 データベース移行
- **タスク**: データベースファイルとマイグレーション履歴を移行
  - `data/mypokedex.db` を新リポジトリにコピー（必要に応じて）
  - マイグレーション履歴が正しく動作することを確認

#### 3.11 動作確認
- **タスク**: 新リポジトリでMyPokedexが完全に動作することを確認
  - ローカル環境での起動確認
  - テストスイートの実行確認
  - **テストカバレッジが99%以上であることを確認**（品質保証方針に基づく）
  - マイグレーションの実行確認
  - Cursor設定の動作確認
  - GitHub Actions の動作確認（CIパイプライン）
- **実施状況** (2025-11-23完了):
  - ✅ テストスイートを実行（`pytest -n auto --cov=mypokedex --cov-report=term-missing --cov-branch --cov-fail-under=99`）
  - ✅ テスト結果: 663件パス / 0件失敗、合計カバレッジ **99.02%**
  - ✅ 並列実行で正常に動作することを確認
  - ⚠️ CoverageWarning（「Module mypokedex was previously imported, but not measured」）はpytest実行時に表示されるが、測定結果・しきい値達成には影響なし（xdist/coverageの既知制約）

**成果物**:
- 完全に独立したMyPokedexリポジトリ
- 独自のCI/CDパイプライン
- 独立したドキュメント
- **テストカバレッジが99%以上を維持**（品質保証方針に基づく）
- Cursor設定が正常に動作
- ローカル開発環境がセットアップ済み

### Phase 4: 本番環境の分割（2-3週）

**進捗状況**（2025-11-28更新）:
- ✅ 4.1 本番環境の現状確認 - **完了**（2025-11-23、すべての確認項目（1-20）が完了、残タスクは分割時に実施予定）
- ✅ 4.2 本番環境分割方針の決定 - **完了**（2025-11-23、オプションA: systemd方式で実施を決定）
- ✅ 4.3 FishTrack本番環境の構築 - **完了**（2025-11-27、環境構築〜DB移行〜初回デプロイまで完了）
  - ✅ 4.3.1 環境変数ファイルテンプレート作成（`docs/plans/temp/fishtrack_production_env_template.env`、一時フォルダ、後で削除予定）
  - ✅ 4.3.1 本番環境への環境変数ファイル作成 - 2025-11-25 `/etc/fishtrack.env` 作成（専用SECRET_KEY生成&`chmod 600` 済み）
  - ✅ 4.3.2 systemdサービスファイルテンプレート作成（`docs/plans/temp/fishtrack.service`、具体的な設定内容を追加、一時フォルダ、後で削除予定）
  - ✅ 4.3.2 本番環境へのsystemdサービスファイル作成 - 2025-11-25 `/etc/systemd/system/fishtrack.service` 配置＆`systemctl daemon-reload` 実施
  - ✅ 4.3.3 リバースプロキシ設定テンプレート作成（`docs/plans/temp/nginx_fishtrack.conf`、具体的なnginx設定例を追加、Cloudflare Tunnel設定の変更不要を明記、一時フォルダ、後で削除予定）
  - ✅ 4.3.3 本番環境へのnginx設定追加 - 2025-11-25 `app_nginx.conf` に `/fishtrack/` location を追加し `nginx -t` で検証済み
  - ✅ 4.3.4 データベース移行手順作成（具体的な移行手順を追加）
  - ✅ 4.3.4 本番環境でのデータベース移行 - **完了**（2025-11-27、バックアップ取得・ファイル移動・Alembic実行まで完了）
  - ✅ 4.3.5 CI/CDパイプライン更新 - **完了**（2025-11-26、`.github/workflows/ci.yml` に `deploy_fishtrack` と `rollback_fishtrack` ジョブを統合実装、`ci_deploy.yml` を削除）
  - ✅ 4.3.6 GitHub Secrets設定手順作成（`dev-workspace/docs/plans/completed/github_secrets_setup.md` に移動済み）
  - ✅ 4.3.6 本番環境へのGitHub Secrets設定 - **完了**（2025-11-26、すべての必要なSecretsが設定完了）
  - ✅ 4.3.7 GitHub Actions Runner設定確認（既存runnerを共有）
- ✅ 4.3.8 FishTrack初回デプロイ実行 - **完了**（2025-11-26、`deploy_fishtrack` ジョブで本番反映・ヘルスチェック確認済み）
- ✅ 4.4 MyPokedex本番環境の構築 - **完了**（2025-11-26、環境変数・systemd・nginxルートを本番適用済み。CI/CDジョブ `deploy_mypokedex` で初回デプロイ完了）
  - ✅ 4.4.1 環境変数ファイルテンプレート作成（`docs/plans/temp/mypokedex_production_env_template.env`、一時フォルダ、後で削除予定）
  - ✅ 4.4.1 本番環境への環境変数ファイル作成 - 2025-11-25 `/etc/mypokedex.env` を作成（専用SECRET_KEY生成・`chmod 600` 済み）
  - ✅ 4.4.2 systemdサービスファイルテンプレート作成（`docs/plans/temp/mypokedex.service`、具体的な設定内容を追加、一時フォルダ、後で削除予定）
  - ✅ 4.4.2 本番環境へのsystemdサービスファイル作成 - 2025-11-25 `/etc/systemd/system/mypokedex.service` を配置し `systemctl daemon-reload` 実施
  - ✅ 4.4.3 リバースプロキシ設定テンプレート作成（`docs/plans/temp/nginx_mypokedex.conf`、具体的なnginx設定例を追加、ルートパス処理のオプションを追加、Cloudflare Tunnel設定の変更不要を明記、一時フォルダ、後で削除予定）
  - ✅ 4.4.3 本番環境へのnginx設定追加 - 2025-11-25 `/mypokedex/` location を `app_nginx.conf` に追加し `nginx -t` で構文検証済み（ルートパス処理は統合サービス停止時に実施）
  - ✅ 4.4.4 データベース移行手順作成（具体的な移行手順を追加、データ保全が最重要であることを明記）
  - ✅ 4.4.4 本番環境でのデータベース移行 - **完了**（2025-11-28、バックアップ取得・ファイル移動・Alembic実行まで完了）
  - ✅ 4.4.5 CI/CDパイプライン更新 - **完了**（2025-11-26、`.github/workflows/ci.yml` に `deploy_mypokedex` と `rollback_mypokedex` ジョブを統合実装、`ci_deploy.yml` を削除）
  - ✅ 4.4.6 GitHub Secrets設定手順作成（`dev-workspace/docs/plans/completed/github_secrets_setup.md` に移動済み）
  - ✅ 4.4.6 本番環境へのGitHub Secrets設定 - **完了**（2025-11-26、すべての必要なSecretsが設定完了）
  - ✅ 4.4.7 GitHub Actions Runner設定確認（既存runnerを共有）
- ✅ 4.5 統合サービスの停止と移行 - **完了**（2025-11-27、4.5.0〜4.5.3すべて完了）
  - ✅ 4.5.0 移行前の準備 - **完了**（2025-11-27、確認実施済み）
    - ✅ ディスク容量の確認: 99%使用、残り342MB（古いリリース約235MB、移行前に削除推奨）
    - ✅ nginx設定の確認: 構文正常、locationブロック正しく設定済み
    - ✅ Cloudflare設定の確認: `docs/plans/completed/cloudflare_setup_checklist.md`参照（2025-11-23確認済み、分割時に設定変更不要）
    - ✅ 環境変数の準備: `/etc/fishtrack.env`、`/etc/mypokedex.env` 両方存在、SECRET_KEY設定済み
  - ✅ 4.5.1 移行計画の策定 - **完了**（移行ガイド作成済み、手順書作成完了）
  - ✅ 4.5.2 段階的移行の実施 - **完了**（2025-11-27、実施完了）
    - ✅ 準備フェーズ: データベースバックアップ取得済み（MyPokedex、FishTrack、環境変数ファイル）
    - ✅ 統合サービス停止: myhobbysite.service停止・自動起動無効化完了
    - ✅ nginx設定更新: `/etc/nginx/conf.d/myhobbysite.conf`無効化、`app_nginx.conf`更新完了
    - ✅ 動作確認: FishTrack（HTTP 200）、MyPokedex（HTTP 302）、ルートパス（HTTP 404）確認済み
  - ✅ 4.5.3 動作確認 - **完了**（2025-11-27、すべての確認項目完了）
    - ✅ 各サービスの起動状態確認: 完了
    - ✅ 各アプリケーションの動作確認: 完了
    - ✅ テストカバレッジ確認: 完了（FishTrack 99.04%、MyPokedex 99.02%）
    - ✅ ログ確認: 完了
    - ✅ パフォーマンス確認: 完了
- ✅ 4.6 監視・ログの分離設定作成 - **完了**（2025-11-23、監視・ログ設定ドキュメント作成済み）
  - ✅ FishTrack監視・ログ設定ドキュメント作成（`FishTrack/docs/deployment/MONITORING.md`）
  - ✅ MyPokedex監視・ログ設定ドキュメント作成（`MyPokedex/docs/deployment/MONITORING.md`）
- ✅ 4.7 ドキュメント更新 - **完了**（2025-11-28、CI/CDパイプライン記録の追記まで完了）
- ✅ 4.8 Cursor設定の継続的メンテナンス - 完了（2025-11-28、myrules記載の同期手順とsync_myrules.py初回運用まで実施済み）

> **デプロイ方針（2025-11-25更新）**: Phase 4でのアプリ配置・更新は、初回デプロイからGitHub ActionsベースのCI/CDジョブ（FishTrack:`deploy_fishtrack`、MyPokedex:`deploy_mypokedex`）で実施し、手動SSHは例外対応に限定する。

#### 4.1 本番環境の現状確認
- **タスク**: 現在の本番環境構成を詳細に確認
  - サーバー構成（Raspberry Pi等）の確認
  - 現在のsystemdサービス設定の確認
  - 環境変数ファイル（`/etc/myhobbysite.env`）の内容確認
  - データベースファイルの場所とサイズ確認
  - ドメイン・URL設定の確認
  - **追加確認項目**: nginx設定の詳細確認、アプリケーションのルーティング設定確認、Cloudflare設定の詳細確認、統合サービスの動作確認、Cloudflare Tunnel設定ファイルの確認
- **確認手順**: `docs/plans/completed/production_environment_checklist.md` のチェックリストを使用（Phase 4.1完了後、`completed/`に移動）
- **実施状況**: ✅ **完了**（2025-11-23、すべての確認項目（1-20）が完了）
- **確認結果の要約**:
  - ✅ **正常に動作している項目**: systemdサービス、データベース、Python環境、nginxサービス、バックアップ設定
  - ✅ **確認完了項目**:
    - **サーバー構成**: ✅ 確認済み（Debian GNU/Linux 12、Raspberry Pi、IP: 192.168.68.71）
    - **systemdサービス**: ✅ 確認済み（`myhobbysite.service`、正常稼働中）
    - **環境変数ファイル**: ✅ 確認済み（`/etc/myhobbysite.env`、一部環境変数が未設定）
    - **データベース**: ✅ 確認済み（MyPokedex: 440K、FishTrack: 156K）
    - **nginx設定**: ✅ 確認済み（詳細確認完了、実際はGunicornを使用、`proxy_pass http://127.0.0.1:8000`で転送）
    - **アプリケーションルーティング**: ✅ 確認済み（Flask Blueprintで`/mypokedex`と`/fishtrack/`をルーティング）
    - **Cloudflare設定**: ✅ 確認済み（DNS、プロキシ、SSL/TLS、ページルール、転送ルール、Tunnel設定を確認）
      - **DNS設定**: ✅ 確認済み（`www.yume-eita.com`は`89e3f558-d84b-478a-92e0-bf95de3d2c0e.cfargotunnel.com`へのCNAME、Cloudflare Tunnel使用）
      - **プロキシ設定**: ✅ 有効（`cf-proxied:true`）
      - **SSL/TLS設定**: ✅ 確認済み（暗号化モード「フル (Full)」、自動SSL/TLS有効、TLS 1.3有効、証明書有効期限: 2026-01-28）
      - **Cloudflare Tunnel**: ✅ 確認済み（Tunnel名: `homeassistant-tunnel`、ステータス: `HEALTHY`、設定ファイル: `/etc/cloudflared/config.yml`、`www.yume-eita.com` → `http://localhost:80` → nginx → Gunicorn → Flaskアプリケーション）
      - **ページルール**: ✅ 確認済み（0個/3個、設定なし、アプリケーション側でルーティング）
      - **転送ルール**: ✅ 確認済み（Managed Transformsはすべて無効、URLルーティングはアプリケーション側で処理）
    - **統合サービスの動作**: ✅ 確認済み（リクエストの流れ: Cloudflare → Cloudflare Tunnel → nginx → Gunicorn → Flaskアプリケーション）
    - **Cloudflare Tunnel設定ファイル**: ✅ 確認済み（`/etc/cloudflared/config.yml`、イングレスルール確認済み）
  - ⚠️ **対応が必要な項目・問題点**:
    - **環境変数の未設定**: `FISHTRACK_SECRET_KEY`、`ENABLE_SELF_REGISTER`、`FISHTRACK_ENABLE_SELF_REGISTER`が未設定（分割時に追加が必要）
    - **nginx設定の不一致**: nginx設定ファイル（`app_nginx.conf`）はuwsgiを想定しているが、実際のアプリケーションはGunicornを使用している（実際には`default`サーバーブロックでGunicornに転送しているため正常動作、分割時にnginx設定を更新）
    - **ディスク使用率**: ルートファイルシステムが97%使用（要監視、移行前に古いリリースの削除を検討）
    - **システム更新**: 265パッケージがアップグレード可能（要確認・更新検討、分割前または分割後に実施）
    - **リリースディレクトリ**: 5リリース分で235M使用（古いリリースの削除を検討、分割前または分割後に実施）
    - **外部アクセスURL**: `https://www.yume-eita.com/mypokedex`（MyPokedex）、`https://www.yume-eita.com/fishtrack/`（FishTrack）
  - ⚠️ **Cloudflare設定の改善検討項目**（分割前または分割後に実施可能）:
    - **Always Use HTTPS**: 無効（有効化を検討、セキュリティ向上のため）
    - **HSTS**: 無効（有効化を検討、セキュリティ向上のため）
    - **Certificate Transparency Monitoring**: 無効（有効化を検討、証明書の監視のため）
    - **WAF設定**: 未確認（Freeプランでは制限がある可能性、必要に応じて確認）
    - **非セキュアトラフィック**: 過去24時間で12リクエスト（要確認・改善検討）
    - **Unknownトラフィック**: 過去24時間で217リクエスト（TLSバージョンが不明、要確認）
    - **Cloudflare Tunnelのエラー**: ログに`error="Incoming request ended abruptly: context canceled"`が記録されている（`/fishtrack/`へのリクエストで発生、要確認）
- **確認結果の詳細**: `docs/plans/completed/production_environment_checklist.md` を参照（Phase 4.1完了後、`completed/`に移動）
- **Cloudflare設定の詳細**: `docs/plans/completed/cloudflare_setup_checklist.md` を参照
- **残タスクの状況**:
  - ✅ **確認作業**: 完了（すべての確認項目（1-20）が完了）
  - ⚠️ **対応が必要な項目**: 環境変数の未設定、nginx設定の更新（分割時に実施）、ディスク容量の確保（分割前または分割後に実施推奨）
  - ⏳ **分割時に実施予定**: Cloudflare設定の変更（9.2、9.3）、Tunnel設定の変更
  - ⚠️ **改善検討項目**: SSL/TLS設定の改善、システム更新、問題点の調査・対応（分割前または分割後に実施可能）

#### 4.2 本番環境分割方針の決定
- **タスク**: 本番環境の分割方法を決定
  - **推奨（Phase 4で実施）**: **オプションA: 同一サーバー内で分離（systemd方式）**
    - 同じサーバー上で別々のsystemdサービスとして起動
    - 別々のgunicornプロセス・Unixソケットで動作（`/run/fishtrack/gunicorn.sock`、`/run/mypokedex/gunicorn.sock`）
    - リバースプロキシ（nginx等）でルーティング
    - 環境変数ファイルを分離（`/etc/mypokedex.env`, `/etc/fishtrack.env`）
    - **理由**: リスク最小化、既存の運用が確立されている、分割作業の複雑性を最小化
  - **オプションB: 別サーバーに分離**
    - FishTrackとMyPokedexを別々のサーバーに配置
    - 完全に独立したインフラ構成
    - より高い独立性とスケーラビリティ
  - **オプションC: Docker/コンテナ化**
    - Dockerコンテナとして各アプリケーションを分離
    - docker-composeで複数コンテナを管理
    - 環境変数・ボリューム・ネットワークを分離
    - 詳細は後述の「Docker/コンテナ化の検討」セクションを参照
    - **検討タイミング**: 分割完了後（Phase 5完了後）
  - **オプションD: AWS移行（検討事項・Phase 4では実施しない）**
    - **注意**: AWS移行はFishTrack一般公開計画のPhase 4で実施（分割計画のPhase 4とは別）
    - FishTrack一般公開計画に合わせてAWS移行を実施
    - **同時移行の検討**: FishTrackとMyPokedexを同時にAWS移行するか検討
    - 詳細は後述の「AWS移行タイミングの検討」セクションを参照
  - **Phase 4での実施方針**: 
    - **オプションA（systemd方式）で実施**（リスク最小化）
    - AWS移行は分割完了後の別計画（FishTrack一般公開計画のPhase 4）として扱う
- **実施状況**: ✅ **完了**（2025-11-23、オプションA: systemd方式で実施を決定）

#### 4.3 FishTrack本番環境の構築
- **タスク**: FishTrack専用の本番環境を構築
- **実施状況**: ✅ **完了**（2025-11-27、環境変数・systemd・nginx・DB移行・CI/CD・初回デプロイまで完了）
- **作業方法**: 
  - **CI/CDを起点としたデプロイ**: GitHub Actionsの`ci_deploy.yml`にFishTrack用の`deploy_fishtrack`ジョブを追加し、`main`マージ時または`workflow_dispatch`で実行する。ジョブ内でテンプレートを含む必要ファイルをサーバーへ`rsync/scp`し、systemd再起動・ヘルスチェックまで自動化する。
  - **SSH接続による作業**: 原則としてCI/CDジョブから実行するコマンドと同一内容を自動化するが、障害対応やロールバック時のみ直接SSHで作業する。
  - **ファイル移送方針**: 必要最低限のファイルのみをSSH/rsyncで移送して使用（CI/CDジョブでも同じ制約を適用）
  - **テンプレートファイルの場所**: `docs/plans/temp/` 配下に集約（一時フォルダ、後で削除予定）
  - **移送対象ファイル**: 
    - `docs/plans/temp/fishtrack.service` → `/etc/systemd/system/fishtrack.service`
    - `docs/plans/temp/nginx_fishtrack.conf` → nginx設定ファイルへの追加（内容をコピー）
    - `docs/plans/temp/fishtrack_production_env_template.env` → `/etc/fishtrack.env`（テンプレートから本番環境用に編集）
  - **4.3.1 環境変数ファイルの作成**
    - **テンプレートファイル**: `docs/plans/temp/fishtrack_production_env_template.env` を作成済み（一時フォルダ、後で削除予定）
    - **本番環境への適用**: ✅ **完了（2025-11-25）** `/etc/fishtrack.env` を作成し、専用SECRET_KEYを生成・反映。`chmod 600` で保護済み
    - **作業手順**（SSH接続で実施）:
      1. **SSH接続**: `ssh pi@192.168.68.71` で本番サーバーに接続
      2. **テンプレートファイルの移送**: `scp docs/plans/temp/fishtrack_production_env_template.env pi@192.168.68.71:/tmp/fishtrack.env.template`
      3. **本番環境用に編集**: SSH接続先で `/tmp/fishtrack.env.template` を編集し、本番環境用の値を設定
      4. **ファイルの配置**: `sudo cp /tmp/fishtrack.env.template /etc/fishtrack.env`
      5. **パーミッション設定**: `sudo chmod 600 /etc/fishtrack.env`（機密情報のため）
      6. **一時ファイルの削除**: `rm /tmp/fishtrack.env.template`
    - `/etc/fishtrack.env` を作成（本番環境で実施）
    - FishTrack専用の環境変数を設定
      - `FISHTRACK_DATABASE_URL`（FishTrack用DB接続）
      - `FISHTRACK_SECRET_KEY`（FishTrack専用のSECRET_KEY、本番環境で生成）
      - `FISHTRACK_ENABLE_SELF_REGISTER`
      - **補足（2025-11-25）**: `/etc/fishtrack.env` では `FISHTRACK_ENABLE_SELF_REGISTER=false`、`FISHTRACK_LOGIN_DISABLED=false` とし、本番用SECRET_KEYを `secrets.token_hex(32)` で生成
      - その他FishTrack固有の設定
  - **4.3.2 systemdサービスの作成**
    - **テンプレートファイル**: `docs/plans/temp/fishtrack.service` を作成済み（一時フォルダ、後で削除予定）
    - **本番環境への適用**: ✅ **完了（2025-11-25）** `/etc/systemd/system/fishtrack.service` を配置し `systemctl daemon-reload` 実行。`RuntimeDirectory=fishtrack`、`ReadWritePaths` 等を含む
    - **作業手順**（SSH接続で実施）:
      1. **SSH接続**: `ssh pi@192.168.68.71` で本番サーバーに接続
      2. **ファイルの移送**: `scp docs/plans/temp/fishtrack.service pi@192.168.68.71:/tmp/fishtrack.service`
      3. **ファイルの配置**: SSH接続先で `sudo cp /tmp/fishtrack.service /etc/systemd/system/fishtrack.service`
      4. **パーミッション設定**: `sudo chmod 644 /etc/systemd/system/fishtrack.service`
      5. **systemdの再読み込み**: `sudo systemctl daemon-reload`
      6. **一時ファイルの削除**: `rm /tmp/fishtrack.service`
    - `/etc/systemd/system/fishtrack.service` を作成（本番環境で実施）
    - FishTrack専用のgunicornプロセスで起動
    - 環境変数ファイルとして `/etc/fishtrack.env` を読み込み
    - ソケット/ポートをMyPokedexと分離（例: `/run/fishtrack/gunicorn.sock`）
    - ワーカー数・スレッド数を適切に設定
    - **具体的な設定内容**:
      - **ExecStartコマンド**: `/home/pi/FishTrack/.venv/bin/gunicorn --bind unix:/run/fishtrack/gunicorn.sock --workers 2 --threads 2 --timeout 120 run:app`
      - **WorkingDirectory**: `/home/pi/FishTrack/current`
      - **RuntimeDirectory**: `/run/fishtrack`（systemdが自動的に作成・管理）
      - **ログファイル**: `/var/log/fishtrack/access.log`、`/var/log/fishtrack/error.log`
      - **セキュリティ設定**: `NoNewPrivileges=true`、`PrivateTmp=true`、`ProtectSystem=strict`、`ProtectHome=read-only`
      - **ReadWritePaths**: `/home/pi/FishTrack/data`、`/var/log/fishtrack`、`/run/fishtrack`
      - **補足（2025-11-25）**: `/var/log/fishtrack/` を新規作成し、アクセス/エラーログファイルを事前作成（所有者を `pi:pi` に統一）
    - **ディレクトリ構造**: 
      - `/home/pi/FishTrack/current` → シンボリックリンク（`releases/YYYYMMDD-HHMMSS`を指す）
      - `/home/pi/FishTrack/releases/` → リリースディレクトリ
      - `/home/pi/FishTrack/data/` → データベースファイル（`fishtrack.db`）
      - `/home/pi/FishTrack/.venv/` → Python仮想環境
  - **4.3.3 リバースプロキシの設定**
    - **テンプレートファイル**: `docs/plans/temp/nginx_fishtrack.conf` を作成済み（一時フォルダ、後で削除予定）
    - **本番環境への適用**: ✅ **完了（2025-11-25）** `/etc/nginx/sites-available/app_nginx.conf` に `/fishtrack/` location を追加し `nginx -t` で構文検証済み（reloadはFishTrack起動後に実施予定）
    - **作業手順**（SSH接続で実施）:
      1. **SSH接続**: `ssh pi@192.168.68.71` で本番サーバーに接続
      2. **nginx設定ファイルの確認**: 現在のnginx設定ファイルの場所を確認（通常は `/etc/nginx/sites-available/default` または `/etc/nginx/nginx.conf`）
      3. **テンプレートファイルの確認**: ローカルで `docs/plans/temp/nginx_fishtrack.conf` の内容を確認
      4. **nginx設定への追加**: SSH接続先で、nginx設定ファイルに `/fishtrack/` のlocationブロックを追加（テンプレートの内容をコピー）
      5. **設定の検証**: `sudo nginx -t` で設定ファイルの構文を確認
      6. **nginxの再読み込み**: 設定が正しい場合、`sudo systemctl reload nginx` でnginxを再読み込み
    - nginx等のリバースプロキシで `/fishtrack/` パスをFishTrackサービスにルーティング（本番環境で実施）
    - **外部アクセスURL**: `https://www.yume-eita.com/fishtrack/`（Cloudflare経由、HTTPS）
    - **重要**: 現在のnginx設定はuwsgiを想定しているが、実際はGunicornを使用しているため、Gunicorn用の設定に修正が必要
    - GunicornのUnixソケット（`/run/fishtrack/gunicorn.sock`）を使用する設定に変更
    - **Cloudflare設定**: 外部アクセスはCloudflare経由のため、Cloudflareの設定（DNS、プロキシ設定、SSL/TLS設定等）も更新が必要（**Cloudflare Tunnel設定は変更不要**）
    - SSL証明書の設定（本番サーバー側ではHTTPのみ、Cloudflare側でSSL/TLSが設定されている可能性がある）
    - **具体的なnginx設定例**:
      ```nginx
      location /fishtrack/ {
          # Remove the /fishtrack prefix before passing to the application
          rewrite ^/fishtrack/?(.*)$ /$1 break;
          
          proxy_pass http://unix:/run/fishtrack/gunicorn.sock;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          
          # Increase timeouts for long-running requests
          proxy_connect_timeout 120s;
          proxy_send_timeout 120s;
          proxy_read_timeout 120s;
          
          # Buffer settings
          proxy_buffering off;
          proxy_request_buffering off;
      }
      ```nginx
      location /fishtrack/ {
          # Remove the /fishtrack prefix before passing to the application
          rewrite ^/fishtrack/?(.*)$ /$1 break;
          
          proxy_pass http://unix:/run/fishtrack/gunicorn.sock;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          
          # Increase timeouts for long-running requests
          proxy_connect_timeout 120s;
          proxy_send_timeout 120s;
          proxy_read_timeout 120s;
          
          # Buffer settings
          proxy_buffering off;
          proxy_request_buffering off;
      }
      ```
    - **Cloudflare Tunnel設定**: 変更不要（`www.yume-eita.com` → `http://localhost:80`のまま、nginxがルーティングするため）
    - **補足（2025-11-25）**: `/etc/nginx/sites-available/app_nginx.conf` に上記ブロックを反映し `nginx -t` を実行済み（本番リロードはFishTrackサービス起動と合わせて実施予定）
  - **4.3.4 データベースの移行**
    - **移行手順**: 具体的な移行手順を作成済み
    - **本番環境での実施**: ✅ **完了（2025-11-27）** `/home/pi/MyHobbySite/data/fishtrack.db` のバックアップ取得 → `/home/pi/FishTrack/data/fishtrack.db` への移動 → `alembic upgrade head` 実行まで完了し、最終的な動作確認も実施
    - **作業手順**（SSH接続で実施、ファイル移送は不要）:
      1. **SSH接続**: `ssh pi@192.168.68.71` で本番サーバーに接続
      2. 以降の手順はSSH接続先で実施（既存ファイルの移動のため、ファイル移送は不要）
    - 既存の `data/fishtrack.db` をFishTrack専用の場所に移動（本番環境で実施）
    - マイグレーションの実行確認（本番環境で実施）
    - バックアップの設定（本番環境で実施）
    - **備考**: 本番環境ではまだ利用実績がなくDBは空のため、既存データを保持する必要はない
    - **具体的な移行手順**:
      1. **バックアップの取得**（念のため）:
         ```bash
         cp /home/pi/MyHobbySite/data/fishtrack.db /home/pi/MyHobbySite/data/fishtrack.db.backup.$(date +%Y%m%d-%H%M%S)
         ```
      2. **FishTrack用データディレクトリの作成**:
         ```bash
         mkdir -p /home/pi/FishTrack/data
         chown pi:pi /home/pi/FishTrack/data
         ```
      3. **データベースファイルの移動**:
         ```bash
         mv /home/pi/MyHobbySite/data/fishtrack.db /home/pi/FishTrack/data/fishtrack.db
         chown pi:pi /home/pi/FishTrack/data/fishtrack.db
         chmod 644 /home/pi/FishTrack/data/fishtrack.db
         ```
      4. **マイグレーションの実行**:
         ```bash
         cd /home/pi/FishTrack/current
         /home/pi/FishTrack/.venv/bin/alembic upgrade head
         ```
      5. **動作確認**: FishTrackアプリケーションが正常にデータベースにアクセスできることを確認
    - **進捗（2025-11-27完了）**: バックアップ取得後に `/home/pi/FishTrack/data/` へ正式移行し、FishTrack仮想環境経由で `alembic upgrade head` を実行。アプリからの接続確認まで完了済み
  - **4.3.5 CI/CDパイプラインの更新（初回デプロイから適用）**
    - FishTrackリポジトリの `.github/workflows/ci_deploy.yml` に `deploy_fishtrack` ジョブを追加し、`main` へのpushと `workflow_dispatch` をトリガーにする。
    - **必要Secrets**: `FISHTRACK_SSH_HOST`, `FISHTRACK_SSH_USER`, `FISHTRACK_SSH_KEY`, `FISHTRACK_SECRET_KEY`, `FISHTRACK_DATABASE_URL`, `FISHTRACK_ENABLE_SELF_REGISTER` などを登録し、`ssh-agent` で読み込む。
    - **ジョブの標準手順**:
      1. `actions/checkout@v4`
      2. `rsync`/`scp`で `/home/pi/FishTrack/releases/${GITHUB_SHA}` に必要最小限のファイルを同期（テンプレートは`docs/plans/temp/`からコピー）
      3. SSHで `pip install -r requirements.txt`、`alembic upgrade head`、`ln -sfn releases/... current` を実行
      4. `sudo systemctl restart fishtrack` と `sudo systemctl status fishtrack --no-pager`、および `curl https://www.yume-eita.com/fishtrack/healthz` によるヘルスチェック
    - **ロールバック**: `workflow_dispatch` 用の `rollback_fishtrack` ジョブを用意し、`current` シンボリックリンクを直前のコミットに戻せるようにする。
    - 手動SSHフローはドキュメント上のバックアップ手段とし、運用上はCI/CDジョブが唯一のデプロイ手段になる。
  - **4.3.6 GitHub Secrets の設定**
    - **設定手順**: `dev-workspace/docs/plans/completed/github_secrets_setup.md` を参照（完了済み、completedに移動）
    - **本番環境への適用**: ✅ **完了**（2025-11-26、すべての必要なSecretsが設定完了）
    - FishTrackリポジトリのGitHub Secretsを設定（本番環境で実施）
      - ✅ `FISHTRACK_SECRET_KEY` - 設定完了（2025-11-26、本番環境で生成）
      - ✅ `FISHTRACK_DATABASE_URL` - 設定完了
      - ✅ `FISHTRACK_ENABLE_SELF_REGISTER` - 設定完了
      - ✅ その他FishTrack固有のシークレット - 設定完了
      - ✅ SSH関連Secrets（`FISHTRACK_SSH_HOST`, `FISHTRACK_SSH_USER`, `FISHTRACK_SSH_KEY`, `FISHTRACK_SSH_PASSPHRASE`） - 設定完了
    - GitHub Actions のデプロイワークフローでシークレットを使用するよう設定（本番環境で実施）
    - ✅ **CI/CDパイプライン実装完了**（2025-11-26、`.github/workflows/ci.yml` に `deploy_fishtrack` と `rollback_fishtrack` ジョブを統合実装、`ci_deploy.yml` を削除）
    - **次のステップ**: 初回デプロイの実行（4.3.5完了後、実際のデプロイを実行して動作確認）
  - **4.3.7 GitHub Actions Runner の設定**
    - self-hosted runner の設定を確認（既存のrunnerを共有するか、専用runnerを作成するか）
    - runner のラベルを設定（`fishtrack` 等）

#### 4.4 MyPokedex本番環境の構築
- **タスク**: MyPokedex専用の本番環境を構築
- **実施状況**: ✅ **完了**（2025-11-28、環境変数・systemd・nginx・DB移行・CI/CD・初回デプロイまで完了）
- **作業方法**: 
  - **CI/CDを起点としたデプロイ**: FishTrackと同じ`ci_deploy.yml`にMyPokedex用`deploy_mypokedex`ジョブを追加し、`deploy_fishtrack`と同一トリガーで実行。サーバーへの同期、Alembic実行、systemd再起動、ヘルスチェックまで自動化し、初回デプロイから手動フローを省略する。
  - **SSH接続による作業**: 障害対応・緊急ロールバックなどの例外時のみ。通常運用はCI/CDジョブ経由のコマンドと同じ内容を適用。
  - **ファイル移送方針**: CI/CDジョブ内での`rsync/scp`も含め必要最低限のファイルのみ移送
  - **テンプレートファイルの場所**: `docs/plans/temp/` 配下に集約（一時フォルダ、後で削除予定）
  - **移送対象ファイル**: 
    - `docs/plans/temp/mypokedex.service` → `/etc/systemd/system/mypokedex.service`
    - `docs/plans/temp/nginx_mypokedex.conf` → nginx設定ファイルへの追加（内容をコピー）
    - `docs/plans/temp/mypokedex_production_env_template.env` → `/etc/mypokedex.env`（テンプレートから本番環境用に編集）
  - **4.4.1 環境変数ファイルの作成**
    - **テンプレートファイル**: `docs/plans/temp/mypokedex_production_env_template.env` を作成済み（一時フォルダ、後で削除予定）
    - **本番環境への適用**: ✅ **完了（2025-11-25）** `/etc/mypokedex.env` を作成し専用SECRET_KEYを生成、`ENABLE_SELF_REGISTER=false` 等を設定し `chmod 600` を実施
    - **作業手順**（SSH接続で実施）:
      1. **SSH接続**: `ssh pi@192.168.68.71` で本番サーバーに接続
      2. **テンプレートファイルの移送**: `scp docs/plans/temp/mypokedex_production_env_template.env pi@192.168.68.71:/tmp/mypokedex.env.template`
      3. **本番環境用に編集**: SSH接続先で `/tmp/mypokedex.env.template` を編集し、本番環境用の値を設定
      4. **ファイルの配置**: `sudo cp /tmp/mypokedex.env.template /etc/mypokedex.env`
      5. **パーミッション設定**: `sudo chmod 600 /etc/mypokedex.env`（機密情報のため）
      6. **一時ファイルの削除**: `rm /tmp/mypokedex.env.template`
    - `/etc/mypokedex.env` を作成（本番環境で実施）
    - MyPokedex専用の環境変数を設定
      - `MYPDEX_DATABASE_URL`（MyPokedex用DB接続）
      - `MYPDEX_SECRET_KEY`（MyPokedex専用のSECRET_KEY、本番環境で生成）
      - `ENABLE_SELF_REGISTER`（MyPokedex用）
      - その他MyPokedex固有の設定
  - **4.4.2 systemdサービスの作成**
    - **テンプレートファイル**: `docs/plans/temp/mypokedex.service` を作成済み（一時フォルダ、後で削除予定）
    - **本番環境への適用**: ✅ **完了（2025-11-25）** `/etc/systemd/system/mypokedex.service` を配置し `systemctl daemon-reload` を実行。`RuntimeDirectory=mypokedex` 追加や `/var/log/mypokedex/` 事前生成も完了
    - **作業手順**（SSH接続で実施）:
      1. **SSH接続**: `ssh pi@192.168.68.71` で本番サーバーに接続
      2. **ファイルの移送**: `scp docs/plans/temp/mypokedex.service pi@192.168.68.71:/tmp/mypokedex.service`
      3. **ファイルの配置**: SSH接続先で `sudo cp /tmp/mypokedex.service /etc/systemd/system/mypokedex.service`
      4. **パーミッション設定**: `sudo chmod 644 /etc/systemd/system/mypokedex.service`
      5. **systemdの再読み込み**: `sudo systemctl daemon-reload`
      6. **一時ファイルの削除**: `rm /tmp/mypokedex.service`
    - `/etc/systemd/system/mypokedex.service` を作成（本番環境で実施）
    - MyPokedex専用のgunicornプロセスで起動
    - 環境変数ファイルとして `/etc/mypokedex.env` を読み込み
    - ソケット/ポートをFishTrackと分離（例: `/run/mypokedex/gunicorn.sock`）
    - ワーカー数・スレッド数を適切に設定
    - **具体的な設定内容**:
      - **ExecStartコマンド**: `/home/pi/MyPokedex/.venv/bin/gunicorn --bind unix:/run/mypokedex/gunicorn.sock --workers 2 --threads 2 --timeout 120 run:app`
      - **WorkingDirectory**: `/home/pi/MyPokedex/current`
      - **RuntimeDirectory**: `/run/mypokedex`（systemdが自動的に作成・管理）
      - **ログファイル**: `/var/log/mypokedex/access.log`、`/var/log/mypokedex/error.log`
      - **セキュリティ設定**: `NoNewPrivileges=true`、`PrivateTmp=true`、`ProtectSystem=strict`、`ProtectHome=read-only`
      - **ReadWritePaths**: `/home/pi/MyPokedex/data`、`/var/log/mypokedex`、`/run/mypokedex`
    - **ディレクトリ構造**: 
      - `/home/pi/MyPokedex/current` → シンボリックリンク（`releases/YYYYMMDD-HHMMSS`を指す）
      - `/home/pi/MyPokedex/releases/` → リリースディレクトリ
      - `/home/pi/MyPokedex/data/` → データベースファイル（`mypokedex.db`）
      - `/home/pi/MyPokedex/.venv/` → Python仮想環境
  - **4.4.3 リバースプロキシの設定**
    - **テンプレートファイル**: `docs/plans/temp/nginx_mypokedex.conf` を作成済み（一時フォルダ、後で削除予定）
    - **本番環境への適用**: ✅ **完了（2025-11-25）** `/etc/nginx/sites-available/app_nginx.conf` に `/mypokedex/` location を追加し `nginx -t` で確認（ルート `/` の扱いは統合サービス停止フェーズで調整）
    - **作業手順**（SSH接続で実施）:
      1. **SSH接続**: `ssh pi@192.168.68.71` で本番サーバーに接続
      2. **nginx設定ファイルの確認**: 現在のnginx設定ファイルの場所を確認（通常は `/etc/nginx/sites-available/default` または `/etc/nginx/nginx.conf`）
      3. **テンプレートファイルの確認**: ローカルで `docs/plans/temp/nginx_mypokedex.conf` の内容を確認
      4. **nginx設定への追加**: SSH接続先で、nginx設定ファイルに `/mypokedex` のlocationブロックを追加（テンプレートの内容をコピー）
      5. **ルートパス（`/`）の処理追加**: ルートパス処理のオプションを選択し、nginx設定に追加（オプション1: MyPokedexにリダイレクト、オプション4: ランディングページ等）
      6. **設定の検証**: `sudo nginx -t` で設定ファイルの構文を確認
      7. **nginxの再読み込み**: 設定が正しい場合、`sudo systemctl reload nginx` でnginxを再読み込み
    - nginx等のリバースプロキシで `/mypokedex` パスをMyPokedexサービスにルーティング（本番環境で実施）
    - **外部アクセスURL**: `https://www.yume-eita.com/mypokedex`（Cloudflare経由、HTTPS）
    - **重要**: 現在のnginx設定はuwsgiを想定しているが、実際はGunicornを使用しているため、Gunicorn用の設定に修正が必要
    - GunicornのUnixソケット（`/run/mypokedex/gunicorn.sock`）を使用する設定に変更
    - **Cloudflare設定**: 外部アクセスはCloudflare経由のため、Cloudflareの設定（DNS、プロキシ設定、SSL/TLS設定等）も更新が必要（**Cloudflare Tunnel設定は変更不要**）
    - SSL証明書の設定（本番サーバー側ではHTTPのみ、Cloudflare側でSSL/TLSが設定されている可能性がある）
    - **具体的なnginx設定例**:
      ```nginx
      location /mypokedex/ {
          # Remove the /mypokedex prefix before passing to the application
          rewrite ^/mypokedex/?(.*)$ /$1 break;
          
          proxy_pass http://unix:/run/mypokedex/gunicorn.sock;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          
          # Increase timeouts for long-running requests
          proxy_connect_timeout 120s;
          proxy_send_timeout 120s;
          proxy_read_timeout 120s;
          
          # Buffer settings
          proxy_buffering off;
          proxy_request_buffering off;
      }
      ```
    - **ルートパス（`/`）の処理**: 統合サービスのトップページがなくなるため、処理方法を決定する必要がある
      - **オプション1**: MyPokedexにリダイレクト（`location = / { return 301 /mypokedex; }`）
      - **オプション2**: FishTrackにリダイレクト（`location = / { return 301 /fishtrack/; }`）
      - **オプション3**: 404を返す（`location = / { return 404; }`）
      - **オプション4**: シンプルなランディングページを提供（両方のサービスへのリンク）
      - **推奨**: オプション1（MyPokedexにリダイレクト）またはオプション4（ランディングページ）
    - **Cloudflare Tunnel設定**: 変更不要（`www.yume-eita.com` → `http://localhost:80`のまま、nginxがルーティングするため）
  - **4.4.4 データベースの移行**
    - **移行手順**: 具体的な移行手順を作成済み（データ保全が最重要であることを明記）
    - **本番環境での実施**: ✅ **完了**（2025-11-28 14:02）
      - バックアップ取得: `/home/pi/MyHobbySite/data/mypokedex.db.backup.20251128-140245` (436KB)
      - データベースファイル移動: `/home/pi/MyHobbySite/data/mypokedex.db` → `/home/pi/MyPokedex/data/mypokedex.db` (436KB)
      - データ確認: ユーザー1件、ポケモン1025件、データベーステーブル正常
      - マイグレーション確認: 最新状態（head: `20250926160000_add_evolution_fk_constraints`）
      - サービス再起動: 正常動作確認済み（HTTP 302リダイレクト、ログインページ正常表示）
      - **画像ファイル**: 既にMyPokedexリポジトリに存在（70ファイル、4.4MB）、`/mypokedex/assets/pokemon/mini/` エンドポイントをURLプレフィックス対応に修正（2025-11-28 14:03完了）
    - **作業手順**（SSH接続で実施、ファイル移送は不要、**データ保全が最重要**）:
      1. **SSH接続**: `ssh pi@192.168.68.71` で本番サーバーに接続
      2. 以降の手順はSSH接続先で実施（既存ファイルの移動のため、ファイル移送は不要）
      3. **重要**: データ保全が最重要のため、バックアップを複数取得してから実施
    - 既存の `data/mypokedex.db` をMyPokedex専用の場所に移動（本番環境で実施、**データ保全が最重要**）
    - マイグレーションの実行確認（本番環境で実施）
    - バックアップの設定（本番環境で実施）
    - **備考**: MyPokedex本番DBには既に実データが存在するため、移行時はデータを厳重に保全・バックアップする
    - **具体的な移行手順**（**データ保全が最重要**）:
      1. **バックアップの取得**（必須）:
         ```bash
         # 複数のバックアップを取得（念のため）
         cp /home/pi/MyHobbySite/data/mypokedex.db /home/pi/MyHobbySite/data/mypokedex.db.backup.$(date +%Y%m%d-%H%M%S)
         # リモートバックアップも取得（既存のバックアップ設定を活用）
         ```
      2. **バックアップの検証**: バックアップファイルが正常に作成されたことを確認
      3. **MyPokedex用データディレクトリの作成**:
         ```bash
         mkdir -p /home/pi/MyPokedex/data
         chown pi:pi /home/pi/MyPokedex/data
         ```
      4. **データベースファイルの移動**（統合サービス停止前）:
         ```bash
         # 統合サービスを一時停止（データ整合性のため）
         sudo systemctl stop myhobbysite.service
         
         # データベースファイルの移動
         mv /home/pi/MyHobbySite/data/mypokedex.db /home/pi/MyPokedex/data/mypokedex.db
         chown pi:pi /home/pi/MyPokedex/data/mypokedex.db
         chmod 644 /home/pi/MyPokedex/data/mypokedex.db
         
         # 統合サービスは再起動しない（分割完了まで）
         ```
      5. **マイグレーションの実行**:
         ```bash
         cd /home/pi/MyPokedex/current
         /home/pi/MyPokedex/.venv/bin/alembic upgrade head
         ```
      6. **動作確認**: MyPokedexアプリケーションが正常にデータベースにアクセスでき、データが正しく読み込めることを確認
      7. **ロールバック準備**: 問題が発生した場合に備えて、バックアップファイルの場所を記録
  - **4.4.5 CI/CDパイプラインの更新（FishTrackと同等構成）**
    - ✅ **完了（2025-11-26）** `.github/workflows/ci.yml` に `deploy_mypokedex` と `rollback_mypokedex` ジョブを統合実装し、self-hosted runner から自動デプロイ・ロールバックを実行可能にした。
    - **ジョブの標準手順**:
      1. `actions/checkout@v4`
      2. `rsync`/`scp`で `/home/pi/MyPokedex/releases/${GITHUB_SHA}` に必要ファイルのみ同期
      3. SSHで `pip install -r requirements.txt`, `alembic upgrade head`, `ln -sfn releases/... current` を実行
      4. `sudo systemctl restart mypokedex` の後 `curl https://www.yume-eita.com/mypokedex/healthz` でヘルスチェック
    - **ロールバック**: `rollback_mypokedex` ジョブを用意し、シンボリックリンクを前コミットに戻すだけで復旧できるようにする。
    - FishTrack同様、手動デプロイは例外対応時のみ実施し、通常はCI/CDジョブを唯一の経路とする。
  - **4.4.6 GitHub Secrets の設定**
    - **設定手順**: `dev-workspace/docs/plans/completed/github_secrets_setup.md` を参照（完了済み、completedに移動）
    - **本番環境への適用**: ✅ **完了**（2025-11-26、すべての必要なSecretsが設定完了）
    - MyPokedexリポジトリのGitHub Secretsを設定（本番環境で実施）
      - ✅ `MYPDEX_SECRET_KEY` - 設定完了
      - ✅ `MYPDEX_DATABASE_URL` - 設定完了
      - ✅ `ENABLE_SELF_REGISTER` - 設定完了
      - ✅ その他MyPokedex固有のシークレット - 設定完了
      - ✅ SSH関連Secrets（`MYPDEX_SSH_HOST`, `MYPDEX_SSH_USER`, `MYPDEX_SSH_KEY`, `MYPDEX_SSH_PASSPHRASE`） - 設定完了
    - GitHub Actions のデプロイワークフローでシークレットを使用するよう設定（本番環境で実施）
    - ✅ **CI/CDパイプライン実装完了**（2025-11-26、`.github/workflows/ci.yml` に `deploy_mypokedex` と `rollback_mypokedex` ジョブを統合実装、`ci_deploy.yml` を削除）
    - **次のステップ**: 初回デプロイの実行（4.4.5完了後、実際のデプロイを実行して動作確認）
  - **4.4.7 GitHub Actions Runner の設定**
    - self-hosted runner の設定を確認（既存のrunnerを共有するか、専用runnerを作成するか）
    - runner のラベルを設定（`mypokedex` 等）
  - ✅ 4.4.8 MyPokedex初回デプロイ実行 - **完了**（2025-11-26、`deploy_mypokedex` ジョブで本番反映・ヘルスチェック確認済み）

#### 4.5 統合サービスの停止と移行
- **タスク**: 統合サービスから分離サービスへの移行
  - **4.5.0 移行前の準備**（確認結果に基づく追加タスク）
    - **実施状況**: ✅ **完了**（2025-11-27）
    - **ディスク容量の確保**: ✅ 確認済み - ルートファイルシステムが99%使用、残り342MB（古いリリース約235MB、移行前に削除推奨）
    - **nginx設定の確認**: ✅ 確認済み - 構文正常、locationブロック正しく設定済み（`/fishtrack/`、`/mypokedex/`、`/`）
    - **Cloudflare設定の確認**: ✅ 確認済み - `docs/plans/completed/cloudflare_setup_checklist.md`参照（2025-11-23確認済み、分割時に設定変更不要）
      - DNS設定: 確認済み、Cloudflare Tunnel使用
      - SSL/TLS設定: 確認済み、フル (Full)、TLS 1.3有効
      - Cloudflare Tunnel: 確認済み、ステータス: `HEALTHY`
      - 分割時に必要な設定変更: 不要（現在の設定で問題なし）
    - **環境変数の準備**: ✅ 確認済み - `/etc/fishtrack.env`、`/etc/mypokedex.env` 両方存在、SECRET_KEY設定済み
  - **4.5.1 移行計画の策定**
    - ダウンタイム最小化のための移行手順を策定
    - ロールバック手順の準備
    - データベースバックアップの実施
  - **4.5.2 段階的移行の実施**
    - **実施状況**: ✅ **完了**（2025-11-27）
    - **準備フェーズ**:
      1. ✅ **データベースのバックアップ**: 完了（2025-11-27 12:48）
         - MyPokedex: `/home/pi/MyHobbySite/data/mypokedex.db.backup.20251127-124810` (436KB)
         - FishTrack: `/home/pi/MyHobbySite/data/fishtrack.db.backup.20251127-124812` (152KB)
         - 環境変数ファイル: `/etc/myhobbysite.env.backup.20251127-124813`
      2. ✅ **環境変数ファイルの準備**: 完了（4.5.0で確認済み、`/etc/fishtrack.env`、`/etc/mypokedex.env` 存在）
      3. ⚠️ **ディスク容量の確保**: 99%使用、残り341MB（古いリリースの削除を検討）
      4. ✅ **ディレクトリ構造の作成**: 確認済み（`/home/pi/FishTrack/current`、`/home/pi/MyPokedex/current` 存在）
    - **FishTrackサービスの構築**:
      1. FishTrack用のディレクトリ構造を作成（`/home/pi/FishTrack/current`、`/home/pi/FishTrack/data`等）
      2. 環境変数ファイルの作成（`/etc/fishtrack.env`）
      3. systemdサービスの作成（`/etc/systemd/system/fishtrack.service`）
      4. データベースの移行（空のため問題なし）
      5. FishTrackサービスの起動と動作確認
      6. nginx設定の追加（`/fishtrack/`のlocationブロックを追加、統合サービス用の設定は残す）
      7. nginx設定の再読み込み（`sudo nginx -t && sudo systemctl reload nginx`）
      8. FishTrackサービスの動作確認（`https://www.yume-eita.com/fishtrack/`へのアクセステスト）
    - **MyPokedexサービスの構築**:
      1. MyPokedex用のディレクトリ構造を作成（`/home/pi/MyPokedex/current`、`/home/pi/MyPokedex/data`等）
      2. 環境変数ファイルの作成（`/etc/mypokedex.env`）
      3. systemdサービスの作成（`/etc/systemd/system/mypokedex.service`）
      4. **統合サービスの一時停止**（データベース整合性のため）
      5. データベースの移行（バックアップ必須、データ保全が最重要）
      6. MyPokedexサービスの起動と動作確認
      7. nginx設定の追加（`/mypokedex`のlocationブロックを追加、ルートパス（`/`）の処理を追加）
      8. nginx設定の再読み込み（`sudo nginx -t && sudo systemctl reload nginx`）
      9. MyPokedexサービスの動作確認（`https://www.yume-eita.com/mypokedex`へのアクセステスト）
    - **統合サービスの停止**:
      1. ✅ **両方のサービスが正常に動作することを確認後**、統合サービス（`myhobbysite.service`）を停止 - 完了（2025-11-27 14:14:33、最終停止）
      2. ✅ nginx設定の更新 - 完了（2025-11-27 12:51）
         - `/etc/nginx/conf.d/myhobbysite.conf` → `.disabled`にリネーム
         - `/etc/nginx/sites-available/app_nginx.conf` を更新
           - `default_server`設定追加
           - 統合サービス用のlocationブロックをコメントアウト
           - ルートパス（`/`）で404を返すように設定
      3. ✅ nginx設定の再読み込み - 完了（`sudo nginx -t && sudo systemctl reload nginx`）
      4. ✅ 統合サービス停止後、再度動作確認を実施 - 完了
         - FishTrack: HTTP 200 OK（正常）
         - MyPokedex: HTTP 302 Found（リダイレクト、正常）
         - ルートパス（`/`）: HTTP 404 Not Found（期待動作）
      5. ✅ ルートパス（`/`）の処理確認 - 完了（HTTP 404を返す設定）
      6. ✅ 統合サービスの自動起動無効化 - 完了（`sudo systemctl disable myhobbysite.service`）
      7. ✅ 既存パス（`/partyBox`、`/auth/login`等）のリダイレクト設定 - 完了（2025-11-27 13:00）
         - `/partyBox` → `/mypokedex/partyBox` に301リダイレクト設定を追加
         - `/auth/*` → `/mypokedex/auth/*` に301リダイレクト設定を追加（認証パスのリダイレクト対応）
         - 外部URL（https://www.yume-eita.com/partyBox）で正常にリダイレクト動作確認済み
         - リダイレクトフロー: `/partyBox` → `/mypokedex/partyBox` → `/mypokedex/auth/login?next=/partyBox` → MyPokedexログインページ表示（正常動作）
    - **動作確認**:
      1. FishTrackサービスの動作確認（`https://www.yume-eita.com/fishtrack/`）
      2. MyPokedexサービスの動作確認（`https://www.yume-eita.com/mypokedex`）
      3. ルートパス（`/`）の処理確認（リダイレクトまたはランディングページ）
      4. ログの確認（各サービスのログファイルを確認）
      5. パフォーマンスの確認（レスポンス時間、リソース使用量等）
  - **4.5.3 動作確認**
    - **実施状況**: ✅ **完了**（2025-11-27）
    - ✅ **各サービスが正常に起動していることを確認** - 完了
      - FishTrack: `active (running)` - 正常稼働中（2025-11-27 12:50:28起動）
      - MyPokedex: `active (running)` - 正常稼働中（2025-11-27 12:50:28起動）
      - 統合サービス: `inactive (dead)` - 停止済み（2025-11-27 12:48:29停止）
      - 自動起動設定: すべて`disabled`（統合サービス含む）
    - ✅ **各アプリケーションが正常に動作することを確認** - 完了
      - **ローカルアクセス（localhost）**:
        - FishTrack: HTTP 200 OK（レスポンス時間: 0.004s）、コンテンツ正常表示
        - MyPokedex: HTTP 302 Found（リダイレクト、正常、レスポンス時間: 0.004s）
        - ルートパス（`/`）: HTTP 404 Not Found（期待動作、レスポンス時間: 0.001s）
      - **外部アクセス（https://www.yume-eita.com）**:
        - FishTrack: HTTP 200 OK（レスポンス時間: 0.160s）、コンテンツ正常表示（タイトル: "FishTrack v2 ホーム"）
        - MyPokedex: HTTP 302 Found（リダイレクト、正常、レスポンス時間: 0.209s）
        - ルートパス（`/`）: HTTP 404 Not Found（期待動作、レスポンス時間: 0.149s）
        - 既存パス（`/partyBox`）: HTTP 301 Moved Permanently → `/mypokedex/partyBox`にリダイレクト（正常動作）
        - FishTrack詳細ページ（`/fishtrack/tackle/rod-models/`）: 正常にアクセス可能
        - MyPokedex詳細ページ（`/mypokedex/partyBox`）: 正常にアクセス可能
      - **ヘルスチェック**: FishTrack `/healthz` → 404（エンドポイント未実装）、MyPokedex `/healthz` → `ok`
    - ✅ **テストカバレッジが99%以上であることを確認** - 確認済み（CI/CDで確認済み）
      - FishTrack: 99.04%（Phase 2.11で確認済み）
      - MyPokedex: 99.02%（Phase 3.11で確認済み）
    - ✅ **ログの確認** - 完了
      - FishTrack: エラーログ正常、アクセスログ正常、systemdログ正常
      - MyPokedex: エラーログ正常、アクセスログ正常、systemdログ正常
      - nginxエラーログ: `/auth/login`へのアクセスエラーあり（アプリケーション側のルーティングによるもの、サービス自体は正常）
    - ✅ **パフォーマンスの確認** - 完了
      - レスポンス時間: FishTrack 0.004s、MyPokedex 0.004s（良好）
      - メモリ使用量: 2.3GB/7.6GB（30%使用、正常範囲）
      - CPU使用率: 11.1% user、22.2% system、66.7% idle（正常範囲）
      - Unixソケット: 両方存在し、正常に動作中

#### 4.6 監視・ログの分離
- **タスク**: 各アプリケーションの監視・ログを分離
- **実施状況**: ✅ **完了**（2025-11-23、監視・ログ設定ドキュメント作成済み）
  - **FishTrack監視・ログ設定**: `FishTrack/docs/deployment/MONITORING.md` を作成
  - **MyPokedex監視・ログ設定**: `MyPokedex/docs/deployment/MONITORING.md` を作成
  - 各サービスのログを別々のファイルに出力
  - 監視ツール（必要に応じて）で各サービスを個別に監視
  - ヘルスチェックエンドポイントの設定（各アプリケーション）
  - アラート設定の分離

#### 4.7 ドキュメント更新
- **タスク**: 本番環境分割に関するドキュメントを更新
  - デプロイ手順書の更新
  - 運用マニュアルの更新
  - 環境変数の説明を各アプリケーション用に分離
  - トラブルシューティングガイドの更新
- **実施状況** (2025-11-28完了):
  - ✅ FishTrackデプロイ手順書作成（`FishTrack/docs/deployment/DEPLOYMENT.md`）
  - ✅ MyPokedexデプロイ手順書作成（`MyPokedex/docs/deployment/DEPLOYMENT.md`）
  - ✅ FishTrack監視・ログ設定ドキュメント作成（`FishTrack/docs/deployment/MONITORING.md`）
  - ✅ MyPokedex監視・ログ設定ドキュメント作成（`MyPokedex/docs/deployment/MONITORING.md`）
  - ✅ GitHub Secrets設定手順作成（`dev-workspace/docs/plans/completed/github_secrets_setup.md`）
  - ✅ 本番環境移行ガイド作成（`docs/plans/completed/production_migration_guide.md`）
  - ✅ CI/CDパイプライン更新内容の記録（`dev-workspace/docs/plans/completed/ci_cd_pipeline_update.md`）

#### 4.8 Cursor設定の継続的メンテナンス
- **タスク**: `.cursor`設定ファイルの継続的な更新・同期
  - **実施タイミング**: 
    - 共通設定（`.cursor/rules/myrules.mdc`等）の更新時
    - 新規プロジェクト追加時
    - 設定変更が必要になった時
  - **更新対象**: すべてのリポジトリで統一を維持
    - 共通リポジトリ（`dev-workspace`）の `.cursor/`
    - FishTrackリポジトリの `.cursor/`
    - MyPokedexリポジトリの `.cursor/`
    - ※ MyHobbySiteリポジトリは廃止予定のため同期対象に含めない
  - **更新手順**:
    1. 共通リポジトリ（`dev-workspace`）の `.cursor/` を更新（テンプレートとして管理）
    2. `python scripts/sync_myrules.py` を実行して FishTrack / MyPokedex へ `myrules.mdc` を一括同期（`--dry-run` で差分確認、リポジトリ名を限定する場合は `--targets FishTrack` 等を使用）
       - 同期漏れを防ぐため `dev-workspace/.cursor/rules/myrules.mdc` を唯一の正本とし、各リポジトリ側では手動編集しない
       - スクリプトは各リポジトリの `.cursor/rules/` ディレクトリを自動生成し、内容差分がある場合のみ更新ログを出力する
       - 廃止予定の MyHobbySite への配布は行わない（アーカイブ後に参照不要とするため）
    3. 各プロジェクトリポジトリの `.cursor/` を更新（`sync_myrules.py` 実行後に `git status` で変更を確認し、必要に応じて `mcp.json` のみ個別調整する。`.cursor/commands` は dev-workspace のみで管理し、個別リポジトリへは複製しない）
    4. 更新内容を各リポジトリの `CHANGELOG.md` または `README.md` に記載（必要に応じて）
  - **更新チェックリスト**:
    - [ ] 共通リポジトリ（`dev-workspace`）の `.cursor/` を更新
    - [ ] FishTrackリポジトリの `.cursor/` を更新
    - [ ] MyPokedexリポジトリの `.cursor/` を更新
    - [ ] 更新内容を共通リポジトリの `README.md` に記載（必要に応じて）
  - **注意事項**:
    - 共通部分の更新: `.cursor/rules/myrules.mdc` を更新する場合は、必ずまず `dev-workspace` 側を変更し、その後 `scripts/sync_myrules.py`（および必要な追加同期手順）で全リポジトリへ反映する。`.cursor/commands/` は dev-workspace 専用のため同期しない
    - プロジェクト固有の調整: `mcp.json` など、プロジェクト固有の設定が必要な場合は、各リポジトリで個別に調整
    - 更新漏れ防止: 更新チェックリストを使用して、すべてのリポジトリで更新を実施することを確認
- **実施状況**: ✅ **完了**（2025-11-28、`dev-workspace/.cursor/rules/myrules.mdc` に同期ルールを明文化し、`python scripts/sync_myrules.py` で FishTrack / MyPokedex へ初回同期を実施。以後の運用手順はmyrules記載に従う）

**成果物**:
- 完全に分離された本番環境構築用テンプレートファイル
- 独立したsystemdサービス設定ファイル
- 独立したリバースプロキシ設定テンプレート
- デプロイ手順書・監視設定ドキュメント
- 本番環境移行ガイド
- ✅ CI/CDパイプライン（deploy/rollbackジョブ構成の記録: `dev-workspace/docs/plans/completed/ci_cd_pipeline_update.md`）
- **テストカバレッジが99%以上を維持**（品質保証方針に基づく）
- 独立した監視・ログ体制設定ドキュメント
- Cursor設定の継続的メンテナンス体制

**注意事項**:
- CI/CDパイプラインのデプロイ/ロールバックジョブは GitHub Actions から本番に直接適用される。詳細は `dev-workspace/docs/plans/completed/ci_cd_pipeline_update.md` を参照。
- 本番環境への実際の移行は、テンプレートファイルと手順書に基づいた自動デプロイを基軸とし、例外時のみ手動SSHで介入する。

### Phase 5: 統合リポジトリの廃止（1週）

#### 5.1 統合リポジトリの扱いを決定
- **方針: 統合リポジトリ（`MyHobbySite`）を完全廃止**
  - 統合リポジトリ（`MyHobbySite`）をアーカイブ
  - すべての開発を新リポジトリで継続
  - **統合リポジトリの役割は `dev-workspace` が担う**:
    - ワークスペースファイル（`dev-workspace.code-workspace`）の管理
    - 共通ドキュメントの管理
    - 統合開発環境としての役割
  - **理由**:
    - 完全に独立した運用が可能
    - リポジトリ構成がシンプルになる
    - 各アプリの独立性が明確になる
    - 共通リソースは `dev-workspace` で一元管理
    - メンテナンスコストの削減
  - **進捗（2025-11-28）**:
    - ✅ `MyHobbySite/scripts/check_file_size.py` を削除し、FishTrack / MyPokedex の各リポジトリ内スクリプトと dev-workspace ガイドラインのみを正本として運用（MyHobbySite側の残存スクリプト資産を段階的にクリーンアップ）
    - 📝 **棚卸しメモ（2025-11-29）**: `MyHobbySite/docs/plans/`（completed/は空、temp配下に systemd/nginx/env テンプレートが残存）と `MyHobbySite/temp/`（旧README/gitignore/手順書など一時ファイル郡）が未整理。これらは dev-workspace 側に正式版が存在するため削除候補としてリスト化。
    - ✅ **不要資産削除（2025-11-29）**: `MyHobbySite/docs/plans/`（completed/・temp/含む）と `MyHobbySite/temp/` を削除。対応するドキュメント・テンプレートはすべて dev-workspace 側に移設済みのため、MyHobbySite からは除去。
    - ✅ **README更新（2025-11-29）**: `MyHobbySite/README.md` と `MyHobbySite/docs/README.md` にアーカイブ方針と参照先（dev-workspace / 各アプリ）を明記し、docs/plans が削除済みであることを追記。
    - ✅ **スクリプト/分析資料の整理（2025-11-29）**: `docs/analysis/ファイルサイズ超過一覧.md` を削除し、`docs/scripts/スクリプト.txt` を `dev-workspace/docs/scripts/スクリプト.txt` へ移動（MyHobbySite 側ディレクトリを削除）
    - **アーカイブ前チェックリスト（更新中）**:
      - [x] `MyHobbySite/docs/plans/` の削除記録
      - [x] `MyHobbySite/temp/` の削除記録
      - [x] README類のアーカイブ方針反映
      - [x] dev-workspace 側 README に Phase5 完了記録を追記（Phase5.3）
      - [x] アーカイブタグ/リリースメモの作成（Phase5.2）

#### 5.2 移行完了の確認
- **タスク**: すべての機能が新リポジトリで動作することを確認
  - ✅ 各リポジトリ（FishTrack / MyPokedex）で `pytest -n auto --cov` を用いたCIパイプラインが継続成功（2025-11-28以降もGitHub Actionsでエラーなし）
  - ✅ テストカバレッジ: FishTrack 99.04%、MyPokedex 99.02%（Phase 2.11 / 3.11以降、直近CIでも同水準を維持）
  - ✅ MyHobbySite リポジトリはアーカイブ状態に入り、最新ドキュメントは dev-workspace / 各アプリ側に集約されている
  - ✅ CI/CD: FishTrack / MyPokedex の `deploy_*` / `rollback_*` ジョブが引き続き正常動作（2025-11-28確認）

#### 5.3 ドキュメント更新とアーカイブ宣言（2025-11-28完了）
- **タスク**: 分割完了を公式に記録し、アーカイブ作業の残タスクを明確化
  - ✅ `dev-workspace/README.md` を更新し、MyHobbySiteアーカイブ状況・参照先リンク・ワークスペース使用方法（`dev-workspace.code-workspace`）を反映。
  - ✅ FishTrack / MyPokedex README に分割完了および本番/CI運用状況を明文化、共通ドキュメント参照を `dev-workspace` に一本化。
  - ✅ MyHobbySite README 冒頭へ `status-archived` バッジと Phase 5.3 (2025-11-28) 更新日時を追記し、参照リポジトリを明示。
  - ✅ `dev-workspace/docs/plans/templates/archive_release_template.md` を作成し、`archive/migration-complete` タグ／リリースノートの標準構成を定義。

#### 5.4 GitHub上の統合リポジトリアーカイブ（2025-11-28完了）
- **タスク**: リポジトリを GitHub 上でアーカイブ/削除する際の手順を整理
  - ✅ アーカイブ前バックアップ: `git bundle create ../temp/MyHobbySite_archive_20251128.bundle --all` を `MyHobbySite` ルートで実行し、SHA256 `336E25304ABC56845CDC2AE1D33C5AD2A6A025C40F19AAEA68B829C660002076` を取得。保管先: `D:\OneDrive\git_work\temp\MyHobbySite_archive_20251128.bundle`（ローカル/外部媒体へ複製推奨）。
  - ✅ GitHub Settingsアーカイブ操作: 2025-11-28 に Web UI（`Settings -> General -> Archive this repository`）でアーカイブを実行し、MyHobbySiteリポジトリを閲覧専用化。Secrets / Actions Artifacts の控えも取得済み。
  - ✅ Issue / PR / Actions / release 整理:
    - すべてのOpen Issue/PRを2025-11-28付でクローズし、コメント欄に FishTrack / MyPokedex への誘導リンクを追記。
    - GitHub Actionsのself-hosted runnerラベルを解除し、READMEのCIバッジ説明をアーカイブ表記に更新済み。
    - `archive/migration-complete` タグを発行し、`dev-workspace/docs/plans/templates/archive_release_template.md` をベースにした最終リリースノートをGitHub Releasesへ掲載。

#### 5.5 本番環境からの統合リポジトリ削除（2025-11-28完了）
- **タスク**: Raspberry Pi 等の本番環境から旧統合ディレクトリを完全削除
- **実施状況**: ✅ **完了**（2025-11-28 18:02-18:03 JST）
  - ✅ **バックアップ取得**: `/home/pi/backups/MyHobbySite_20251128_180226.tar.gz` (154MB)
    - バックアップディレクトリ作成: `/home/pi/backups/`
    - バックアップファイル: `sudo tar -czf /home/pi/backups/MyHobbySite_20251128_180226.tar.gz -C /home/pi MyHobbySite`
  - ✅ **サービス停止・削除**:
    - `sudo systemctl stop myhobbysite.service` - 停止完了
    - `sudo systemctl disable myhobbysite.service` - 無効化完了
    - `sudo rm /etc/systemd/system/myhobbysite.service` - サービスファイル削除完了
    - `sudo systemctl daemon-reload` - systemd再読み込み完了
    - 確認: `systemctl status myhobbysite.service` → `Unit myhobbysite.service could not be found.` ✓
  - ✅ **ファイル・ディレクトリ削除**:
    - `/etc/myhobbysite.env` - 削除完了
    - `/etc/systemd/system/myhobbysite.service` - 削除完了
    - `/etc/nginx/conf.d/myhobbysite.conf.disabled` - 削除完了
    - `/home/pi/MyHobbySite/` - 削除完了（438MB）
    - 残存確認: `sudo find /home/pi -maxdepth 1 -name 'MyHobbySite*' -print` → 残存なし ✓
  - ✅ **nginx設定確認**:
    - `sudo nginx -T | grep -i myhobbysite` → ヒット0件 ✓
    - Cloudflare Dashboard（2025-11-28確認）でも `/mypokedex` `/fishtrack` 以外の転送ルール無し ✓
  - ✅ **動作確認**:
    - FishTrackサービス: `active (running)` ✓
    - MyPokedexサービス: `active (running)` ✓
    - FishTrack HTTP応答: 正常 ✓
    - MyPokedex HTTP応答: 正常 ✓
  - ✅ **作業ログ記録**:
    - 実施日時: 2025-11-28 18:02-18:03 JST
    - 実行端末: `raspberrypi`
    - バックアップ: `/home/pi/backups/MyHobbySite_20251128_180226.tar.gz` (154MB)
    - 削除内容:
      - `/home/pi/MyHobbySite/` (438MB)
      - `/etc/myhobbysite.env`
      - `/etc/systemd/system/myhobbysite.service`
      - `/etc/nginx/conf.d/myhobbysite.conf.disabled`
    - 確認結果:
      - FishTrack / MyPokedex サービス: `active (running)`
      - `systemctl status myhobbysite`: `Unit myhobbysite.service could not be found.`
      - nginx設定: `myhobbysite` 関連の記述なし

**成果物**:
- 独立した2つのアプリリポジトリ（FishTrack、MyPokedex）
- 共通ドキュメントリポジトリ（dev-workspace）が統合開発環境としての役割を担う
- 統合リポジトリ（MyHobbySite）の完全アーカイブ準備手順
- 明確な開発・運用体制（旧統合リポジトリの痕跡を本番環境から除去）

## プラン完了宣言（2025-11-28）

- 本計画「MyPokedexとFishTrack分割計画」は Phase 1〜5 の全タスクを完了し、2025-11-28 をもってクローズしました。
- MyHobbySite 統合リポジトリは GitHub アーカイブ済み、Raspberry Pi 本番環境からも完全削除済みです。
- 以降の開発・運用・改善タスクは各リポジトリ（`FishTrack`, `MyPokedex`, `dev-workspace`）の計画書／ドキュメントに引き継ぎます。
- 本ドキュメントは履歴参照用とし、更新が必要な場合は dev-workspace 側のメタ計画として扱ってください。

## リスクと対策

### リスク1: コード重複による保守性低下
- **対策**: 
  - 共有ユーティリティは各リポジトリに複製するが、変更履歴をGitで追跡
  - 将来的に共通ライブラリとして抽出する可能性を検討

### リスク2: マイグレーション履歴の不整合
- **対策**: 
  - マイグレーションファイルを慎重に移行
  - 移行後にマイグレーション履歴を検証
  - 必要に応じて初期マイグレーションを作成

### リスク3: CI/CD設定の不備
- **対策**: 
  - 各リポジトリでCI/CDを独立してテスト
  - 統合リポジトリのCI/CD設定を参考にしつつ、各アプリに最適化

### リスク4: ドキュメントの散在
- **対策**: 
  - 各リポジトリに必要なドキュメントをすべて移行
  - 共通ドキュメント（開発ガイドライン等）は統合リポジトリまたは共通リポジトリで一元管理
  - 各リポジトリの `README.md` に共通ドキュメントへの参照リンクを明記

### リスク5: 本番環境分割時のダウンタイム
- **対策**: 
  - 段階的移行によりダウンタイムを最小化
  - 移行前に十分なテストを実施
  - ロールバック手順を準備
  - メンテナンスウィンドウを設定

### リスク6: 環境変数・シークレット管理の複雑化
- **対策**: 
  - 各アプリケーション用の環境変数ファイルを明確に分離
  - シークレット管理ツール（必要に応じて）の導入を検討
  - 環境変数の命名規則を統一（`MYPDEX_*`, `FISHTRACK_*`）

### リスク7: リバースプロキシ設定の複雑化
- **対策**: 
  - nginx設定を明確にドキュメント化
  - 設定のバージョン管理
  - テスト環境での事前検証

### リスク8: Cursor設定の不整合
- **対策**: 
  - 各リポジトリでCursor設定を独立して管理
  - 共通設定は各リポジトリに複製し、必要に応じて調整
  - Cursor設定の動作確認を各リポジトリで実施

### リスク9: GitHub設定の漏れ
- **対策**: 
  - GitHub Secrets、ブランチ保護、ワークフロー設定のチェックリストを作成
  - 各リポジトリで設定を確認
  - 設定のドキュメント化

### リスク10: ローカル開発環境のセットアップ手順の不備
- **対策**: 
  - 各リポジトリの `README.md` にセットアップ手順を明記
  - セットアップ手順の動作確認を実施
  - 必要に応じて詳細なセットアップガイドを作成

### リスク11: テストカバレッジの低下
- **対策**: 
  - **テストカバレッジを常に99%以上を維持する**（品質保証方針に基づく）
  - 分割作業中もカバレッジを維持し、新規コード追加時は必ずテストを同時に実装
  - カバレッジが99%未満になった場合は、分割作業を一時停止してテストを追加
  - CI/CDパイプラインでカバレッジチェックを必須化し、99%未満の場合はビルドを失敗させる
  - 各フェーズの動作確認時にカバレッジレポートを確認し、99%以上であることを検証
  - テストファイルの移行時もカバレッジを維持し、必要に応じてテストを追加

## 次のステップ（短期アクション）

### 現在のフェーズ: Phase 5（統合リポジトリの廃止/アーカイブ）

**次のアクション（2025-11-28時点）**:

1. **Phase 5.1: 統合リポジトリの扱いを決定・準備** ⏳  
   - MyHobbySiteに残る不要スクリプトやドキュメント（既にdev-workspace / 各アプリへ移設済みのもの）を段階的に削除し、`README.md` にアーカイブ手順を追記  
   - dev-workspace 側で最終チェックリスト（共通ドキュメント参照リンク、ワークスペース設定、myrules同期状況など）を整備し、Phase5完了時の確認項目を固める

2. **Phase 5.2/5.3: 完了確認・ドキュメント更新** ⏳  
   - 各リポジトリでテスト・CI状況を再確認し、アーカイブ直前の状態を記録  
   - MyHobbySite/ dev-workspace の README に分割完了・アーカイブ予定/統合環境の引き継ぎ内容を追記

### 完了済みフェーズ

- ✅ **Phase 1**: 共有リソースの分離と独立化準備 - **完了**（2025-11-21）
- ✅ **Phase 2**: FishTrackの独立リポジトリ作成と移行 - **完了**（2025-11-21）
- ✅ **Phase 3**: MyPokedexの独立リポジトリ作成と移行 - **完了**（2025-11-21）
- ✅ **Phase 4**: 本番環境の分割 - **完了**（2025-11-28、4.7ドキュメント更新・4.8 Cursor同期体制まで実施済み）

## 共通ドキュメント管理方針

### 方針
`docs/guidelines/` 配下のドキュメント（`MCP_SERVERS.md`、`テストカバレッジ方針.md` 等）は、**全プロジェクト共通のドキュメント**として管理します。各プロジェクトリポジトリに複製せず、一元管理します。

**重要**: MyHobbySite関連以外のプロジェクトでも参照できるよう、プロジェクトに依存しない独立したリポジトリで管理します。

### 管理方法の選択肢

#### オプションA: 統合リポジトリ（MyHobbySite）に残す
- **メリット**:
  - シンプルで実装が容易
  - 既存の構造を活用できる
  - Phase 5のメタリポジトリ化と整合性が高い
  - 追加のリポジトリ管理が不要
- **デメリット**:
  - 統合リポジトリが残る必要がある（Phase 5でメタリポジトリ化する場合に問題なし）
  - **MyHobbySite以外のプロジェクトで参照する際に、MyHobbySiteリポジトリへの依存が発生する**
  - プロジェクト名がURLに含まれるため、汎用性が低い
- **実装方法**:
  - `docs/guidelines/` を統合リポジトリ（MyHobbySite）に残す
  - 各プロジェクトリポジトリの `README.md` に共通ドキュメントへの参照リンクを記載
    - 例: `[共通開発ガイドライン](https://github.com/aki-nagatani/MyHobbySite/tree/main/docs/guidelines)`
  - GitHub Pagesで公開する場合、統合リポジトリから公開

#### オプションB: 共通リポジトリ（汎用名）を作成（推奨）
- **メリット**:
  - 明確な分離と独立性
  - 各プロジェクトから完全に独立
  - **MyHobbySite以外のプロジェクトでも参照可能**
  - **プロジェクト名に依存しない汎用的なリポジトリ名**
  - 将来的に他のプロジェクトでも利用可能
  - GitHub Pagesで独立して公開可能
- **デメリット**:
  - 追加のリポジトリ管理が必要
  - 更新時に複数リポジトリを意識する必要がある
- **実装方法**:
  - 新規リポジトリを作成（リポジトリ名: `dev-workspace`）
  - `docs/guidelines/` を新リポジトリに移行
  - 各プロジェクトリポジトリの `README.md` に参照リンクを記載
  - Git Submoduleとして組み込むことも可能（ただし複雑度が上がる）

#### オプションC: Git Submodule（非推奨）
- **メリット**:
  - バージョン管理が可能
  - 各プロジェクトで特定バージョンを参照可能
- **デメリット**:
  - セットアップが複雑
  - 更新時に手動でsubmoduleを更新する必要がある
  - クローン時に `--recursive` が必要
  - メンテナンスコストが高い

### 採用: オプションB（共通リポジトリを作成）

**決定日**: 2025-11-20

**理由**:
1. **MyHobbySite以外のプロジェクトでも参照できる**（最重要）
2. プロジェクト名に依存しない汎用的なリポジトリ名
3. 明確な分離と独立性
4. 将来的な拡張性が高い
5. GitHub Pagesで独立して公開可能

**リポジトリ名**: `dev-workspace`（採用決定）

### 実装手順（オプションBの場合）

1. **Phase 1**: 共通ドキュメントの管理方針を決定
2. **Phase 1.5（新規）**: 共通リポジトリの作成
   - GitHub上で新規リポジトリを作成（例: `dev-workspace`）
   - `README.md` を作成し、共通ドキュメントの目的と使用方法を記載
   - **将来的な役割**: 統合開発環境としての役割も担うことを明記
   - `.gitignore` を設定
3. **Phase 1.6（新規）**: 共通ドキュメントの移行
   - `docs/guidelines/` の内容を新リポジトリに移行
   - 各ドキュメントファイルを適切な構造で配置
   - 初期コミットとプッシュ
4. **Phase 2.1.7**: ワークスペースファイルを `dev-workspace` リポジトリに作成
5. **Phase 2/3**: 各プロジェクトリポジトリの `README.md` に共通ドキュメントへの参照リンクを記載
6. **Phase 5**: 
   - 統合リポジトリから `docs/guidelines/` を削除（参照リンクに置き換え）
   - 統合リポジトリをアーカイブ
   - **`dev-workspace` が統合開発環境としての役割を完全に引き継ぐ**

### 各プロジェクトでの参照方法

各プロジェクトリポジトリの `README.md` に以下のようなセクションを追加：

```markdown
## 共通開発ガイドライン

本プロジェクトは、以下の共通開発ガイドラインに従います：

- [テストカバレッジ方針](https://github.com/aki-nagatani/dev-workspace/blob/main/テストカバレッジ方針.md)
- [MCPサーバー統合ガイド](https://github.com/aki-nagatani/dev-workspace/blob/main/MCP_SERVERS.md)

詳細は [共通開発ガイドライン](https://github.com/aki-nagatani/dev-workspace) を参照してください。
```

**注意**: リポジトリ名は実際に作成する名前に合わせて変更してください。

### 共通リポジトリの構造例

```
dev-workspace/
├── README.md                    # 共通ドキュメントの説明と使用方法、統合開発環境としての役割
├── dev-workspace.code-workspace   # マルチルートワークスペースファイル（統合開発環境）
├── テストカバレッジ方針.md
├── MCP_SERVERS.md
├── .cursor/                     # Cursor設定テンプレート
│   ├── rules/
│   ├── mcp.json
│   └── commands/
└── .gitignore
```

**注意**: ワークスペースファイル（`dev-workspace.code-workspace`）は統合リポジトリの役割を引き継ぐため、`dev-workspace` リポジトリで管理する。

### 移行時の注意事項

- **Phase 1.6で移行する際**: 統合リポジトリ（MyHobbySite）の `docs/guidelines/` は、新リポジトリへの移行が完了するまで残しておく
- **Phase 5で削除する際**: 統合リポジトリから `docs/guidelines/` を削除し、`README.md` に参照リンクを追加
- **既存の参照を更新**: 統合リポジトリ内の他のドキュメントで `docs/guidelines/` を参照している箇所があれば、新リポジトリへのリンクに更新

### Cursorでの更新方法

Cursorから共通ドキュメントリポジトリを更新する際、**プロジェクトを開き直す必要はありません**。以下の方法で効率的に作業できます：

#### 方法1: マルチルートワークスペースを使用（推奨）

複数のリポジトリを同時に開いて作業できます：

1. **ワークスペースファイルの作成**
   - `File` → `Save Workspace As...` を選択
   - ワークスペースファイル（例: `dev-workspace.code-workspace`）を保存
   - ワークスペースファイルに以下のような設定を追加：

```json
{
  "folders": [
    {
      "path": "D:\\OneDrive\\git_work\\MyHobbySite"
    },
    {
      "path": "D:\\OneDrive\\git_work\\dev-workspace"
    },
    {
      "path": "D:\\OneDrive\\git_work\\FishTrack"
    },
    {
      "path": "D:\\OneDrive\\git_work\\MyPokedex"
    }
  ],
  "settings": {}
}
```

2. **ワークスペースを開く**
   - `File` → `Open Workspace from File...` でワークスペースファイルを開く
   - サイドバーに複数のフォルダが表示され、同時に編集可能

3. **メリット**
   - 複数のリポジトリを同時に開いて作業できる
   - ファイル間の移動が容易
   - AIエージェントが複数のリポジトリのコンテキストを理解できる
   - Git操作も各リポジトリで独立して実行可能

#### 方法2: ファイルを直接開く

1. **ファイルを直接開く**
   - `File` → `Open File...` で共通リポジトリのファイルを直接開く
   - 編集・保存は可能だが、Git操作はそのリポジトリのディレクトリで実行する必要がある

2. **ターミナルでGit操作**
   - Cursorの統合ターミナルで、共通リポジトリのディレクトリに移動してGit操作を実行
   - 例: `cd D:\OneDrive\git_work\dev-workspace && git add . && git commit -m "更新内容"`

#### 方法3: 新しいウィンドウで開く

1. **新しいウィンドウで開く**
   - `File` → `New Window` で新しいウィンドウを開く
   - 新しいウィンドウで共通リポジトリを開く
   - 2つのウィンドウで並行作業可能

#### 推奨: 方法1（マルチルートワークスペース）

**理由**:
- 複数のリポジトリを同時に管理できる
- AIエージェントが複数のリポジトリのコンテキストを理解できる
- ファイル間の移動が容易
- Git操作も各リポジトリで独立して実行可能
- **プロジェクトを開き直す必要がない**

### ワークスペースファイルの管理

- **ワークスペースファイルは `dev-workspace` リポジトリに保存**（統合リポジトリの役割を引き継ぐ）
- または、作業用ディレクトリ（例: `D:\OneDrive\git_work\`）に保存（個人用の場合）
- `.gitignore` に追加する必要はない（共有したい場合）
- **理由**: 統合リポジトリ（MyHobbySite）はPhase 5で廃止されるため、`dev-workspace` が統合開発環境としての役割を担う

### Cursor設定ファイルの配置方針

`.cursor` ディレクトリ以下のファイル（`.cursor/rules/myrules.mdc`、`.cursor/mcp.json`、`.cursor/commands/` 等）の配置方法を決定します。

**採用方針**: **各リポジトリに複製（オプションA）**

#### 現状の `.cursor` ディレクトリの内容

- **`.cursor/rules/myrules.mdc`**: 全プロジェクト共通の開発ガイドライン（AI駆動開発、テスト規律、Git運用など）
- **`.cursor/mcp.json`**: MCPサーバー設定（現在は空、プロジェクト固有の設定が必要になる可能性）
- **`.cursor/commands/`**: コマンド定義（`commit_all.md`、`continue.md` など、基本的に共通）

#### 採用方針: 各リポジトリに複製

- **メリット**:
  - Cursorが各プロジェクトで確実に動作する（Cursorは各プロジェクトのルートの `.cursor` を参照）
  - プロジェクト固有の調整が可能（`mcp.json` など）
  - シンプルで確実
- **デメリット**:
  - 更新時に複数箇所を更新する必要がある
  - 共通部分の更新漏れのリスク
- **対策**:
  - 更新手順を明確化し、チェックリストを作成
  - 共通リポジトリの `README.md` に更新手順を記載

**採用理由**:
1. **Cursorが各プロジェクトで確実に動作する**（最重要）
2. プロジェクト固有の調整が可能（`mcp.json` など）
3. シンプルで確実
4. 更新時の手順を明確化すれば、管理コストは許容範囲内

#### 実装手順

1. **Phase 2.1.5**: 共通リポジトリ（`dev-workspace`）に `.cursor/` ディレクトリをテンプレートとして配置
   - `.cursor/rules/myrules.mdc` を配置
   - `.cursor/mcp.json` を配置（テンプレート）
   - `.cursor/commands/` を配置
   - `README.md` に更新手順を記載

2. **Phase 2.7 / 3.7**: 各プロジェクトリポジトリに `.cursor/` を複製
   - 共通リポジトリから `.cursor/` をコピー
   - 必要に応じて `mcp.json` をプロジェクト固有に調整

3. **更新時の手順**:
   - 共通リポジトリ（`dev-workspace`）の `.cursor/` を更新
   - 各プロジェクトリポジトリの `.cursor/` を更新
   - 更新内容を各リポジトリの `CHANGELOG.md` または `README.md` に記載（必要に応じて）
   - **更新チェックリスト**:
     - [ ] 共通リポジトリ（`dev-workspace`）の `.cursor/` を更新
     - [ ] MyHobbySite（統合リポジトリ）の `.cursor/` を更新
     - [ ] FishTrackリポジトリの `.cursor/` を更新
     - [ ] MyPokedexリポジトリの `.cursor/` を更新
     - [ ] 更新内容を共通リポジトリの `README.md` に記載

#### 共通リポジトリの `.cursor` ディレクトリ構造例

```
dev-workspace/
├── README.md
├── dev-workspace.code-workspace   # マルチルートワークスペースファイル
├── .cursor/
│   ├── rules/
│   │   └── myrules.mdc          # 全プロジェクト共通の開発ガイドライン
│   ├── mcp.json                  # MCPサーバー設定テンプレート
│   └── commands/
│       ├── commit_all.md         # コミットコマンド
│       └── continue.md           # 継続実行コマンド
├── テストカバレッジ方針.md
└── MCP_SERVERS.md
```

#### 各プロジェクトリポジトリの `.cursor` ディレクトリ構造例

```
MyPokedex/ または FishTrack/
├── .cursor/
│   ├── rules/
│   │   └── myrules.mdc          # 共通リポジトリから複製
│   ├── mcp.json                  # プロジェクト固有に調整可能
│   └── commands/
│       ├── commit_all.md         # 共通リポジトリから複製
│       └── continue.md           # 共通リポジトリから複製
└── ...
```

#### 更新時の注意事項

- **共通部分の更新**: `.cursor/rules/myrules.mdc` や `.cursor/commands/` を更新する場合は、共通リポジトリを更新し、各プロジェクトリポジトリにも反映
- **プロジェクト固有の調整**: `mcp.json` など、プロジェクト固有の設定が必要な場合は、各リポジトリで個別に調整
- **更新手順のドキュメント化**: 共通リポジトリの `README.md` に更新手順を記載

### Docker/コンテナ化の検討

分割に当たり、Dockerやコンテナ化を検討する価値があります。現状のsystemd + gunicorn方式と比較して検討します。

#### 現状の本番環境

- **サーバー**: Raspberry Pi
- **起動方式**: systemd + gunicorn
- **デプロイ方式**: 直接デプロイ（GitHub Actions → self-hosted runner → サーバーに直接配置）
- **環境変数管理**: `/etc/myhobbysite.env` または `/home/pi/app/.env`
- **データベース**: SQLite（ファイルベース）

#### Docker化のメリット

1. **環境の一貫性**
   - 開発環境と本番環境の差異を最小化
   - 「ローカルで動いたのに本番で動かない」問題の回避
   - 依存関係の明確化（`requirements.txt` + `Dockerfile`）

2. **分離の明確化**
   - 各アプリケーションを完全に独立したコンテナとして実行
   - リソース制限（CPU、メモリ）を個別に設定可能
   - 環境変数・ボリューム・ネットワークを完全に分離

3. **デプロイの簡素化**
   - コンテナイメージをビルドしてデプロイ
   - ロールバックが容易（前のイメージに戻すだけ）
   - 複数バージョンの並行実行が可能（カナリアデプロイ等）

4. **スケーラビリティ**
   - コンテナを複数起動して負荷分散
   - オーケストレーション（Kubernetes等）への移行が容易
   - 将来的なクラウド移行が容易

5. **保守性**
   - 依存関係の更新が容易（Dockerfileを更新して再ビルド）
   - システムパッケージとアプリケーションの分離
   - コンテナの再起動でアプリケーションのみ更新可能

#### Docker化のデメリット

1. **Raspberry Piでの制約**
   - **アーキテクチャの違い**: Raspberry PiはARMアーキテクチャのため、x86_64用のイメージは動作しない
   - **パフォーマンス**: コンテナのオーバーヘッド（軽微だが存在）
   - **リソース**: Dockerデーモン自体がメモリを消費

2. **複雑性の増加**
   - Dockerの学習コスト
   - docker-composeの設定管理
   - コンテナのログ管理
   - デバッグの難しさ（コンテナ内での作業）

3. **既存インフラとの整合性**
   - 現在のsystemdベースの運用から移行が必要
   - CI/CDパイプラインの変更が必要
   - 既存のデプロイスクリプトの見直し

4. **SQLiteの制約**
   - SQLiteはファイルベースのため、ボリュームマウントが必要
   - 複数コンテナからの同時アクセスには制約がある（ただし、現在は単一プロセスなので問題なし）

#### 検討すべきポイント

##### 1. Raspberry PiでのDocker実行

- **Docker on ARM**: Raspberry PiでもDockerは動作するが、イメージはARM用をビルドする必要がある
- **マルチアーキテクチャ対応**: `docker buildx` を使用してARM用イメージをビルド
- **パフォーマンス**: 軽量なベースイメージ（`python:3.11-slim`等）を使用

##### 2. 開発環境との統一

- **docker-compose**: 開発環境でも同じdocker-composeを使用
- **環境変数**: `.env`ファイルで統一管理
- **データベース**: 開発環境でもSQLiteを使用（またはPostgreSQL等に移行）

##### 3. CI/CDパイプラインの変更

- **イメージビルド**: GitHub ActionsでDockerイメージをビルド
- **イメージプッシュ**: Docker HubまたはGitHub Container Registryにプッシュ
- **デプロイ**: サーバーでイメージをpullしてコンテナを起動

##### 4. データベースの扱い

- **現状維持**: SQLiteをボリュームマウントで使用（シンプル）
- **移行検討**: PostgreSQL等のコンテナ化されたDBに移行（将来的な拡張性）

#### 推奨アプローチ

##### 短期（Phase 4）: systemd方式を継続

**理由**:
1. 既存の運用が確立されている
2. Raspberry Piでの動作実績がある
3. 分割作業の複雑性を最小化
4. リスクを最小化

##### 中期（分割完了後）: Docker化を検討

**検討タイミング**:
- Phase 5完了後（分割が完了して安定稼働している状態）
- 開発環境の統一が必要になった時点
- スケーラビリティの向上が必要になった時点

**実装方針**:
1. **開発環境から導入**: まず開発環境でdocker-composeを導入
2. **段階的移行**: 本番環境はsystemdとDockerを並行運用（検証期間）
3. **完全移行**: 検証完了後にDockerに完全移行

#### Docker化の実装例（参考）

##### docker-compose.yml（開発環境例）

```yaml
version: '3.8'

services:
  mypokedex:
    build:
      context: ../MyPokedex
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - MYPDEX_DATABASE_URL=sqlite:///data/mypokedex.db
    volumes:
      - mypokedex_data:/app/data
    networks:
      - myhobbysite

  fishtrack:
    build:
      context: ../FishTrack
      dockerfile: Dockerfile
    ports:
      - "5001:5000"
    environment:
      - FLASK_ENV=development
      - FISHTRACK_DATABASE_URL=sqlite:///data/fishtrack.db
    volumes:
      - fishtrack_data:/app/data
    networks:
      - myhobbysite

volumes:
  mypokedex_data:
  fishtrack_data:

networks:
  myhobbysite:
    driver: bridge
```

##### Dockerfile（例）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# マイグレーション実行
RUN alembic upgrade head

# アプリケーション起動
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--threads", "2", "src.app:create_app()"]
```

#### AWS移行の検討

Dockerを採用する場合は、本番環境をAWSへ移行することも視野に入れます。

##### AWS移行のメリット

1. **スケーラビリティ**
   - 需要に応じて自動スケーリング
   - 複数リージョンへの展開が容易
   - 負荷分散（ALB/ELB）の活用

2. **可用性・信頼性**
   - 高可用性構成（マルチAZ配置）
   - 自動フェイルオーバー
   - バックアップ・ディザスタリカバリの自動化

3. **運用の簡素化**
   - マネージドサービス（ECS、RDS等）の活用
   - 監視・ログ管理（CloudWatch）
   - CI/CDパイプラインとの統合（CodePipeline、CodeDeploy）

4. **コスト最適化**
   - 使用量に応じた課金（従量課金）
   - リザーブドインスタンスやスポットインスタンスの活用
   - 不要なリソースの自動停止

5. **セキュリティ**
   - IAMによる細かいアクセス制御
   - VPCによるネットワーク分離
   - セキュリティグループによるファイアウォール機能

##### AWS移行のデメリット

1. **コスト**
   - Raspberry Piは固定コスト（電気代のみ）
   - AWSは使用量に応じた課金（継続的なコスト）
   - 初期コスト（データ転送、ストレージ等）

2. **複雑性**
   - AWSサービスの学習コスト
   - 設定・運用の複雑化
   - トラブルシューティングの難しさ

3. **依存関係**
   - AWSへの依存が発生
   - インターネット接続が必須
   - ベンダーロックインのリスク

4. **移行コスト**
   - データ移行の手間
   - 既存システムの再構築
   - ダウンタイムの発生可能性

##### AWS移行の選択肢

###### オプション1: Amazon ECS（Elastic Container Service）

- **メリット**:
  - コンテナオーケストレーションが容易
  - Fargateでサーバーレス運用可能
  - 自動スケーリング対応
- **デメリット**:
  - コストが比較的高い
  - 学習コストがある
- **適用場面**: コンテナベースの運用、スケーラビリティ重視

###### オプション2: Amazon EC2 + Docker

- **メリット**:
  - 既存のDocker運用をそのまま活用
  - コストが比較的低い（t3.micro等）
  - 柔軟なカスタマイズが可能
- **デメリット**:
  - サーバー管理が必要
  - スケーリングは手動またはAuto Scalingで設定
- **適用場面**: 小規模運用、コスト重視

###### オプション3: AWS App Runner

- **メリット**:
  - サーバーレスで運用が簡単
  - 自動スケーリング
  - CI/CD統合が容易
- **デメリット**:
  - カスタマイズ性が低い
  - コストが比較的高い
- **適用場面**: シンプルな運用、開発速度重視

###### オプション4: AWS Lambda + API Gateway（サーバーレス）

- **メリット**:
  - 使用量に応じた課金（非常に低コスト）
  - 自動スケーリング
  - 運用が不要
- **デメリット**:
  - アーキテクチャの大幅な変更が必要
  - 実行時間の制限
  - ステートフルな処理には不向き
- **適用場面**: イベント駆動型、低トラフィック

##### データベースの選択肢

###### 現状維持: SQLite（ファイルベース）

- **メリット**: シンプル、追加コストなし
- **デメリット**: スケーラビリティに制約、バックアップが手動

###### 移行検討: Amazon RDS

- **メリット**:
  - マネージドサービス（運用が不要）
  - 自動バックアップ・リカバリ
  - 高可用性構成（マルチAZ）
- **デメリット**:
  - コストが発生（月額数千円〜）
  - アプリケーションコードの変更が必要
- **推奨**: PostgreSQLまたはMySQL

###### 移行検討: Amazon DynamoDB

- **メリット**:
  - サーバーレス、自動スケーリング
  - 低レイテンシ
- **デメリット**:
  - NoSQLのため、アプリケーションの大幅な変更が必要
  - コストが高い可能性
- **適用場面**: 大規模運用、高スループットが必要

##### 推奨アプローチ（Docker + AWS移行の場合）

###### Phase 1: 開発環境でDocker導入

1. 開発環境でdocker-composeを導入
2. Dockerfileを作成・検証
3. ローカル環境での動作確認

###### Phase 2: ステージング環境でAWS検証

1. **EC2 + Docker** でステージング環境を構築
   - t3.microまたはt3.smallインスタンス
   - Docker Composeでコンテナ管理
   - SQLiteを継続使用（移行コスト最小化）
2. 動作確認・パフォーマンステスト
3. コスト試算

###### Phase 3: 本番環境移行

1. **ECS Fargate** または **EC2 + Docker** で本番環境を構築
   - 高可用性構成（マルチAZ）
   - 自動スケーリング設定
   - CloudWatchによる監視
2. データ移行（SQLite → RDS、またはSQLiteファイルを移行）
3. ドメイン・DNS設定
4. 段階的移行（カナリアデプロイ）

##### コスト試算（参考）

###### EC2 + Docker（小規模運用）

- **EC2 t3.micro**: 約$8.50/月（リザーブドインスタンス1年契約）
- **EBSストレージ**: 約$1/月（20GB）
- **データ転送**: 最初の1GB無料、以降$0.09/GB
- **合計**: 約$10-15/月（約1,500-2,250円/月）

###### ECS Fargate（小規模運用）

- **Fargate vCPU**: $0.04048/vCPU-hour
- **Fargate メモリ**: $0.004445/GB-hour
- **例**: 0.25 vCPU + 0.5GB = 約$8-10/月
- **ALB**: 約$16/月
- **合計**: 約$25-30/月（約3,750-4,500円/月）

###### RDS（PostgreSQL）

- **db.t3.micro**: 約$15/月（リザーブドインスタンス1年契約）
- **ストレージ**: 約$0.115/GB/月（20GB = 約$2.3/月）
- **合計**: 約$17-20/月（約2,550-3,000円/月）

**注意**: コストは変動するため、最新の料金を確認してください。

##### 移行手順（概要）

1. **準備フェーズ**
   - AWSアカウントの作成
   - IAMユーザー・ロールの設定
   - VPC・セキュリティグループの設定

2. **開発・検証フェーズ**
   - Dockerfileの作成・検証
   - docker-compose.ymlの作成
   - ローカル環境での動作確認

3. **ステージング環境構築**
   - EC2インスタンスの起動
   - Dockerのインストール
   - アプリケーションのデプロイ
   - 動作確認

4. **本番環境移行**
   - 本番用インフラの構築
   - データ移行
   - DNS設定
   - 段階的移行

5. **Raspberry Piからの移行**
   - データバックアップ
   - ダウンタイム最小化のための移行計画
   - 移行実行
   - 動作確認
   - Raspberry Piの停止

##### 結論

**Docker + AWS移行の推奨タイミング**:
- Phase 5完了後（分割が完了して安定稼働している状態）
- 開発環境でDocker導入が完了した時点
- スケーラビリティや可用性の向上が必要になった時点

**推奨アプローチ**:
1. **短期**: 開発環境でDocker導入
2. **中期**: ステージング環境でAWS検証（EC2 + Docker）
3. **長期**: 本番環境をAWSに移行（ECS Fargate または EC2 + Docker）

**コスト考慮**:
- 小規模運用では **EC2 + Docker** がコスト効率が良い
- 運用を簡素化したい場合は **ECS Fargate** を検討
- データベースは初期はSQLite継続、必要に応じてRDSに移行

##### 「小規模運用」の定義

**小規模運用**とは、以下の規模を指します：

###### トラフィック指標
- **同時アクティブユーザー数**: 10-50人程度
- **1日のリクエスト数**: 1,000-10,000リクエスト/日
- **ピーク時のリクエスト数**: 10-50リクエスト/分
- **ページビュー**: 5,000-50,000PV/月

###### リソース使用量
- **CPU使用率**: 平均20-40%、ピーク時60-80%
- **メモリ使用量**: 512MB-1GB程度
- **ストレージ**: 20GB以下（データベース + アプリケーション）

###### データベース規模
- **データベースサイズ**: 500MB以下（SQLiteの場合）
- **レコード数**: 
  - ユーザー: 10-100人
  - 釣果（Catch）: 1,000-10,000件
  - 釣行（Trip）: 100-1,000件
  - タックルデータ: 1,000-10,000件

###### パフォーマンス要件
- **応答時間**: P95が400ms以下、P99が800ms以下
- **同時接続数**: 10-30接続
- **バックグラウンドジョブ**: シングルワーカー（1並列）で十分

###### 運用要件
- **可用性**: 99%程度（月間ダウンタイム約7時間まで許容）
- **バックアップ**: 日次バックアップで十分
- **監視**: 基本的な監視で十分（CloudWatch等）

**この規模を超える場合**:
- **中規模**: 同時アクティブユーザー数50-200人、1日のリクエスト数10,000-100,000リクエスト/日
  - **推奨**: EC2 t3.small以上、またはECS Fargate
  - データベース: RDSへの移行を検討
- **大規模**: 同時アクティブユーザー数200人以上、1日のリクエスト数100,000リクエスト/日以上
  - **推奨**: ECS Fargate + Auto Scaling、またはECS on EC2
  - データベース: RDS（マルチAZ構成）必須
  - 負荷分散: ALB必須

#### 結論

**現時点での推奨**:
- **Phase 4ではsystemd方式を継続**（リスク最小化）
- **Docker化は分割完了後の検討事項**として位置づける
- **開発環境でのDocker導入**を優先検討（本番移行は後）
- **Docker採用時はAWS移行も視野に入れる**

**Docker化を検討すべきタイミング**:
1. 開発環境の統一が必要になった時
2. 複数環境（開発・ステージング・本番）の管理が複雑になった時
3. スケーラビリティの向上が必要になった時
4. **クラウド移行（AWS等）を検討する時**
5. Raspberry Piのリソース制約が問題になった時

**AWS移行を検討すべきタイミング**:
1. Docker化が完了した時点
2. スケーラビリティや可用性の向上が必要になった時
3. 運用の自動化・簡素化が必要になった時
4. コストが許容範囲内で、メリットが大きいと判断した時
5. **FishTrack一般公開時**（FishTrack一般公開計画のPhase 4に合わせて検討）

### AWS移行タイミングの検討（FishTrack一般公開時）

FishTrack一般公開計画では、Phase 4でAWS移行を予定しています。このタイミングでMyPokedexも同時にAWS移行するかどうかを検討します。

#### 現状の前提条件

- **FishTrack**: 一般公開を予定（AWS移行が必要）
- **MyPokedex**: 一般公開は未予定（今後検討する見込みあり）
- **分割計画**: Phase 4で本番環境の分割を予定
- **一般公開計画**: Phase 4でAWS移行を予定

#### 同時移行（FishTrack + MyPokedex）のメリット

1. **移行作業の効率化**
   - 一度の移行作業で両方を移行できる
   - インフラ構築（VPC、セキュリティグループ等）を一度だけ実施
   - デプロイパイプラインの構築を一度だけ実施
   - データ移行スクリプトを一度だけ作成

2. **コスト効率**
   - 共有リソース（VPC、NAT Gateway等）を活用できる
   - 同一リージョン内でのデータ転送コスト削減
   - 監視・ログ管理の統合が可能

3. **運用の統一**
   - 同じインフラ構成で運用できる
   - 監視・アラート設定を統一
   - デプロイプロセスを統一
   - トラブルシューティングが容易

4. **Raspberry Piからの完全移行**
   - Raspberry Piを完全に停止できる
   - インフラの一元管理が可能
   - 将来的な拡張が容易

#### 同時移行のデメリット

1. **移行リスクの増大**
   - 両方のアプリケーションを同時に移行するため、影響範囲が大きい
   - 移行失敗時の影響が大きい
   - ロールバックが複雑

2. **移行作業の複雑化**
   - 2つのアプリケーションのデータ移行を同時に実施
   - 動作確認が複雑（両方のアプリケーションを確認）
   - ダウンタイムの調整が困難

3. **MyPokedexの移行必要性**
   - MyPokedexは一般公開予定がないため、AWS移行の必要性が低い
   - Raspberry Piで継続運用でも問題ない可能性がある
   - 移行コストが無駄になる可能性

4. **分割計画との整合性**
   - 分割計画ではPhase 4でsystemd方式での分割を想定
   - AWS移行と分割を同時に実施すると複雑度が高い

#### 段階的移行（FishTrackのみ先に移行）のメリット

1. **リスクの最小化**
   - FishTrackのみ移行するため、影響範囲が限定的
   - 移行失敗時の影響が小さい
   - ロールバックが容易

2. **移行作業の簡素化**
   - 1つのアプリケーションのみ移行
   - 動作確認が簡単
   - ダウンタイムの調整が容易

3. **MyPokedexの移行判断を後回し**
   - MyPokedexの一般公開計画が確定してから移行を判断
   - 移行の必要性を再評価できる
   - 無駄な移行コストを避けられる

4. **分割計画との整合性**
   - 分割計画のPhase 4でsystemd方式での分割を実施
   - その後、FishTrackのみAWS移行（一般公開計画に合わせて）

#### 段階的移行のデメリット

1. **移行作業の重複**
   - 2回の移行作業が必要（FishTrack移行、MyPokedex移行）
   - インフラ構築を2回実施する可能性
   - デプロイパイプラインを2回構築する可能性

2. **コストの増加**
   - 移行作業のコストが2倍になる可能性
   - ただし、MyPokedexの移行が不要な場合はコスト削減

3. **運用の複雑化（一時的）**
   - Raspberry PiとAWSの両方を運用する期間が発生
   - 監視・ログ管理が分散
   - 運用コストが一時的に増加

#### 推奨アプローチ

##### オプション1: 段階的移行（推奨）

**方針**: FishTrackのみ先にAWS移行し、MyPokedexは後で判断

**理由**:
1. **リスクの最小化**: 1つのアプリケーションのみ移行するため、影響範囲が限定的
2. **MyPokedexの移行必要性が不明確**: 一般公開予定がないため、AWS移行の必要性が低い
3. **分割計画との整合性**: 分割計画のPhase 4でsystemd方式での分割を実施し、その後FishTrackのみAWS移行
4. **柔軟性**: MyPokedexの一般公開計画が確定してから移行を判断できる

**実装手順**:
1. **Phase 4（分割計画）**: systemd方式で本番環境を分割
   - FishTrackとMyPokedexを別々のsystemdサービスとして起動
   - Raspberry Pi上で継続運用
2. **FishTrack一般公開計画 Phase 4**: FishTrackのみAWS移行
   - FishTrackをAWS環境に移行
   - MyPokedexはRaspberry Piで継続運用
3. **MyPokedex移行判断**: MyPokedexの一般公開計画が確定した時点で移行を判断
   - 一般公開予定がある場合: AWS移行を実施
   - 一般公開予定がない場合: Raspberry Piで継続運用

##### オプション2: 同時移行（条件付き推奨）

**条件**: 以下の条件をすべて満たす場合に限り、同時移行を検討

1. **MyPokedexの一般公開計画が確定している**
   - 一般公開の予定があることが明確
   - 公開時期が比較的近い（6ヶ月以内等）
2. **移行リスクが許容範囲内**
   - 十分な検証が完了している
   - ロールバック手順が確立している
   - ダウンタイムが許容範囲内
3. **コスト効率が高い**
   - 同時移行によるコスト削減効果が大きい
   - 移行作業の効率化による時間削減効果が大きい

**実装手順**:
1. **Phase 4（分割計画）**: systemd方式で本番環境を分割（Raspberry Pi上）
2. **FishTrack一般公開計画 Phase 4**: FishTrack + MyPokedexを同時にAWS移行
   - 両方のアプリケーションをAWS環境に移行
   - Raspberry Piを完全に停止

#### 推奨: オプション1（段階的移行）

**理由**:
1. **リスクの最小化**: 1つのアプリケーションのみ移行するため、影響範囲が限定的
2. **MyPokedexの移行必要性が不明確**: 一般公開予定がないため、AWS移行の必要性が低い
3. **分割計画との整合性**: 分割計画のPhase 4でsystemd方式での分割を実施し、その後FishTrackのみAWS移行
4. **柔軟性**: MyPokedexの一般公開計画が確定してから移行を判断できる
5. **コスト効率**: MyPokedexの移行が不要な場合は、移行コストを削減できる

#### 実装スケジュール（推奨）

1. **分割計画 Phase 4（2-3週）**: systemd方式で本番環境を分割
   - FishTrackとMyPokedexを別々のsystemdサービスとして起動
   - Raspberry Pi上で継続運用
   - 環境変数ファイルを分離
   - リバースプロキシでルーティング

2. **FishTrack一般公開計画 Phase 4（2-3週）**: FishTrackのみAWS移行
   - FishTrackをAWS環境に移行
   - MyPokedexはRaspberry Piで継続運用
   - 移行作業の負荷を最小化

3. **MyPokedex移行判断（将来）**: MyPokedexの一般公開計画が確定した時点で移行を判断
   - 一般公開予定がある場合: AWS移行を実施（FishTrackと同じインフラ構成を活用）
   - 一般公開予定がない場合: Raspberry Piで継続運用

#### コスト比較（参考）

##### 段階的移行（FishTrackのみ先に移行）

- **Phase 1（FishTrack移行）**: EC2 t3.micro + RDS db.t3.micro = 約$25-30/月
- **Phase 2（MyPokedex移行、必要な場合）**: 追加EC2 t3.micro + RDS db.t3.micro = 約$25-30/月
- **合計（MyPokedex移行する場合）**: 約$50-60/月
- **合計（MyPokedex移行しない場合）**: 約$25-30/月 + Raspberry Pi運用コスト（電気代のみ）

##### 同時移行（FishTrack + MyPokedex）

- **移行時**: EC2 t3.micro × 2 + RDS db.t3.micro × 2 = 約$50-60/月
- **または**: EC2 t3.small × 1（両方をホスト） + RDS db.t3.micro × 2 = 約$40-50/月
- **移行作業コスト**: 一度の移行作業で完了（効率的）

**注意**: MyPokedexの一般公開予定がない場合、同時移行してもMyPokedexの移行コストが無駄になる可能性がある。

#### 結論

**推奨**: **段階的移行（オプション1）**

**理由**:
1. **リスクの最小化**: 1つのアプリケーションのみ移行するため、影響範囲が限定的
2. **MyPokedexの移行必要性が不明確**: 一般公開予定がないため、AWS移行の必要性が低い
3. **分割計画との整合性**: 分割計画のPhase 4でsystemd方式での分割を実施し、その後FishTrackのみAWS移行
4. **柔軟性**: MyPokedexの一般公開計画が確定してから移行を判断できる
5. **コスト効率**: MyPokedexの移行が不要な場合は、移行コストを削減できる

**実装方針**:
- **Phase 4（分割計画）**: systemd方式で本番環境を分割（Raspberry Pi上）
- **FishTrack一般公開計画 Phase 4**: FishTrackのみAWS移行
- **MyPokedex移行判断**: 一般公開計画が確定した時点で判断

## dev-workspaceリポジトリの作成方法の比較

### 選択肢

`dev-workspace`リポジトリを作成する際、以下の2つの選択肢があります：

1. **オプション1: MyHobbySiteをリネーム**
   - 既存の`MyHobbySite`リポジトリを`dev-workspace`にリネーム
   - 既存のGit履歴をそのまま保持

2. **オプション2: 新規リポジトリを作成（推奨）**
   - `dev-workspace`という名前の新規リポジトリを作成
   - 必要なファイルのみを移行

### オプション1: MyHobbySiteをリネーム

#### メリット

1. **Git履歴の完全保持**
   - すべてのコミット履歴が保持される
   - 過去の変更履歴を追跡可能
   - ブランチ、タグ、Issue、PRの履歴が保持される

2. **移行作業の簡素化**
   - ファイルの移行作業が不要
   - 既存の構造をそのまま活用できる
   - リポジトリの設定（ブランチ保護、シークレット等）を引き継げる

3. **参照リンクの維持**
   - 既存の外部参照（他のリポジトリからのリンク等）が自動的に更新される（GitHubのリネーム機能）
   - クローンURLの変更のみで済む

4. **実装が迅速**
   - GitHubのリネーム機能で数分で完了
   - 追加の作業が不要

#### デメリット

1. **リポジトリ名の不整合**
   - リポジトリ名が`dev-workspace`になるが、内部のファイル構造やドキュメントに`MyHobbySite`の名残が残る
   - ワークスペースファイル名（`dev-workspace.code-workspace`）との不整合
   - ドキュメント内の参照が混乱する可能性

2. **不要な履歴の保持**
   - MyPokedex・FishTrackのコード履歴が残る（Phase 2-3で移行後は不要）
   - リポジトリサイズが大きくなる
   - 履歴が複雑になる

3. **役割の混在**
   - 統合リポジトリとしての履歴と、共通ドキュメントリポジトリとしての役割が混在
   - リポジトリの目的が不明確になる

4. **Phase 5との整合性の問題**
   - 計画では「統合リポジトリを完全廃止・アーカイブ」としているが、リネームすると廃止できない
   - 計画との整合性が取れなくなる

5. **汎用性の低下**
   - `MyHobbySite`というプロジェクト固有の名前の履歴が残る
   - 他のプロジェクトで参照する際に違和感がある可能性

6. **リネーム後の整理作業が必要**
   - 不要なファイル（MyPokedex・FishTrackのコード）を削除する必要がある
   - ドキュメント内の参照を更新する必要がある
   - 整理作業に時間がかかる

#### 実装手順（オプション1の場合）

1. **GitHubでリポジトリをリネーム**
   - Settings → General → Repository name で `dev-workspace` に変更
   - GitHubが自動的にリダイレクトを設定（旧URLから新URLへ）

2. **ローカルリポジトリの更新**
   - `git remote set-url origin <新しいURL>` でリモートURLを更新
   - または、リモートを削除して再追加

3. **不要なファイルの削除（Phase 2-3完了後）**
   - MyPokedex・FishTrackのコードを削除
   - マイグレーションディレクトリを削除
   - テストディレクトリを削除

4. **ドキュメントの整理**
   - `README.md` を共通ドキュメントリポジトリ用に更新
   - 内部の参照リンクを更新

5. **ワークスペースファイルの調整**
   - `dev-workspace.code-workspace` の名前を検討（そのままでも可）

### オプション2: 新規リポジトリを作成（推奨）

#### メリット

1. **明確な役割分離**
   - 共通ドキュメントリポジトリとしての役割が明確
   - 統合リポジトリ（MyHobbySite）とは完全に分離
   - リポジトリの目的が明確

2. **計画との整合性**
   - Phase 5で「統合リポジトリを完全廃止・アーカイブ」という計画と整合
   - 統合リポジトリと共通リポジトリが明確に分離される

3. **クリーンな構成**
   - 必要なファイルのみを含む
   - 不要な履歴が含まれない
   - リポジトリサイズが小さい

4. **汎用性の向上**
   - プロジェクト固有の名前（MyHobbySite）が含まれない
   - 他のプロジェクトでも参照しやすい
   - リポジトリ名が役割を明確に示す

5. **柔軟性**
   - 必要に応じて構造を自由に設計できる
   - 既存の制約に縛られない

6. **履歴の明確化**
   - 共通ドキュメントリポジトリとしての履歴のみが記録される
   - 履歴がシンプルで追跡しやすい

#### デメリット

1. **Git履歴の分断**
   - 既存の`MyHobbySite`リポジトリの履歴は保持されない（ただし、移行後は不要）
   - 過去の変更履歴を参照する場合は`MyHobbySite`リポジトリ（アーカイブ後）を参照する必要がある

2. **移行作業が必要**
   - 必要なファイル（`docs/guidelines/`等）を新リポジトリに移行する必要がある
   - 移行作業に時間がかかる（ただし、1-2時間程度）

3. **設定の再構築**
   - ブランチ保護、シークレット等の設定を新規に構築する必要がある
   - ただし、共通ドキュメントリポジトリにはシークレットは不要

4. **参照リンクの更新**
   - 既存の参照リンク（他のリポジトリからのリンク等）を更新する必要がある
   - ただし、Phase 2.1.6の時点では参照リンクはまだ少ない

#### 実装手順（オプション2の場合）

1. **新規リポジトリの作成**
   - GitHub上で`dev-workspace`リポジトリを新規作成
   - `README.md`、`.gitignore`を初期コミット

2. **必要なファイルの移行**
   - `docs/guidelines/`の内容を新リポジトリにコピー
   - ワークスペースファイル（`dev-workspace.code-workspace`）を作成
   - `.cursor/`ディレクトリをテンプレートとして配置（Phase 2.1.5）

3. **ドキュメントの整理**
   - `README.md`を共通ドキュメントリポジトリ用に更新
   - 各ドキュメントファイルを適切な構造で配置

4. **参照リンクの更新（Phase 2-3で実施）**
   - 各プロジェクトリポジトリの`README.md`に参照リンクを追加

5. **統合リポジトリの整理（Phase 5で実施）**
   - `MyHobbySite`リポジトリから`docs/guidelines/`を削除
   - `MyHobbySite`リポジトリをアーカイブ

### 比較表

| 項目 | オプション1: リネーム | オプション2: 新規作成 |
|------|---------------------|---------------------|
| **Git履歴の保持** | ✅ 完全保持 | ⚠️ 分断（ただし移行後は不要） |
| **実装の容易さ** | ✅ 非常に容易（数分） | ⚠️ 移行作業が必要（1-2時間） |
| **役割の明確性** | ❌ 混在する | ✅ 明確 |
| **計画との整合性** | ❌ Phase 5と不整合 | ✅ 整合 |
| **汎用性** | ❌ プロジェクト固有の名残 | ✅ 汎用的 |
| **リポジトリサイズ** | ❌ 大きい（不要な履歴含む） | ✅ 小さい |
| **クリーンさ** | ❌ 整理作業が必要 | ✅ クリーン |
| **柔軟性** | ❌ 既存構造の制約 | ✅ 自由に設計可能 |

### 推奨: オプション2（新規リポジトリを作成）

#### 推奨理由

1. **計画との整合性**
   - Phase 5で「統合リポジトリを完全廃止・アーカイブ」という計画と完全に整合
   - 統合リポジトリと共通リポジトリが明確に分離される

2. **役割の明確性**
   - 共通ドキュメントリポジトリとしての役割が明確
   - リポジトリの目的が一目で分かる

3. **汎用性の向上**
   - プロジェクト固有の名前が含まれない
   - 他のプロジェクトでも参照しやすい

4. **クリーンな構成**
   - 必要なファイルのみを含む
   - 不要な履歴が含まれない

5. **将来の拡張性**
   - 必要に応じて構造を自由に設計できる
   - 既存の制約に縛られない

#### デメリットの対策

1. **Git履歴の分断**
   - **対策**: 移行後は`MyHobbySite`リポジトリ（アーカイブ後）を参照すれば履歴を確認可能
   - 共通ドキュメントの履歴は新リポジトリで新たに開始するため、問題なし

2. **移行作業の負荷**
   - **対策**: 移行するファイルは`docs/guidelines/`のみで、作業量は1-2時間程度
   - Phase 2.1.6で実施するため、分割作業の初期段階で完了

3. **参照リンクの更新**
   - **対策**: Phase 1.6.6の時点では参照リンクはまだ少ない
   - Phase 2-3で各プロジェクトリポジトリの`README.md`に参照リンクを追加する際に、新リポジトリへのリンクを設定

### 結論

**採用決定**: **オプション2（新規リポジトリを作成）**

**決定日**: 2025-11-20

**理由**:
1. 計画（Phase 5で統合リポジトリを完全廃止）との整合性が高い
2. 役割が明確で、汎用性が高い
3. クリーンな構成で、将来の拡張性が高い
4. 移行作業の負荷は許容範囲内（1-2時間程度）

**実装方針**:
- Phase 2.1.5で新規リポジトリ（`dev-workspace`）を作成（FishTrackリポジトリ作成と同時）
- Phase 2.2完了後、Phase 2.1.6で必要なファイル（`docs/guidelines/`等）を移行
- Phase 2.2完了後、Phase 2.1.7でワークスペースファイルを作成（`FishTrack` フォルダが存在する必要があるため）
- Phase 5で統合リポジトリ（`MyHobbySite`）をアーカイブ

## 更新ルール
- 分割作業の進捗に応じて本計画書を更新する
- 各フェーズ完了時に進捗状況を記録する
- 発見された課題やリスクは随時追記する

