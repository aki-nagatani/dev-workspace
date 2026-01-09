#!/usr/bin/env python3
"""
本番環境へのデプロイ状況を確認するスクリプト

確認項目:
1. マイグレーションの現在のリビジョン
2. 統計テーブルの存在（user_statistics_daily, user_statistics_weekly）
3. Userテーブルとfishtrack_userテーブルのカラム構造（emailカラム、usernameカラムの有無）
4. last_login_atカラムの存在

使用方法:
    # 環境変数を設定
    export SHARED_DATABASE_URL="postgresql://user:pass@host:port/database"
    
    # 確認スクリプトを実行
    python scripts/check_production_deployment.py
"""

import os
import sys
from pathlib import Path
from typing import Optional

# プロジェクトのルートディレクトリをパスに追加
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

try:
    from sqlalchemy import create_engine, text, inspect
    from alembic.config import Config
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory
except ImportError:
    print("Error: Required packages are not installed.")
    print("Please install them with: pip install sqlalchemy alembic")
    sys.exit(1)


def get_database_url() -> str:
    """環境変数からデータベースURLを取得"""
    url = (
        os.getenv("SHARED_DATABASE_URL")
        or os.getenv("SHARED_DB_URL")
        or os.getenv("FISHTRACK_DATABASE_URL")
        or os.getenv("MYPDEX_DATABASE_URL")
        or os.getenv("DB_URL")
    )
    
    if not url:
        raise RuntimeError(
            "データベースURLが設定されていません。\n"
            "環境変数（SHARED_DATABASE_URL, SHARED_DB_URL, FISHTRACK_DATABASE_URL, "
            "MYPDEX_DATABASE_URL, DB_URL）のいずれかを設定してください。"
        )
    
    return url


def check_table_exists(engine, table_name: str) -> bool:
    """テーブルが存在するか確認"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_column_exists(engine, table_name: str, column_name: str) -> bool:
    """テーブルにカラムが存在するか確認"""
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return False
    
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def get_current_revision(db_url: str) -> Optional[str]:
    """現在のマイグレーションリビジョンを取得"""
    try:
        # Alembic設定ファイルのパス
        alembic_ini = workspace_root / "migrations" / "alembic.ini"
        
        if not alembic_ini.exists():
            return None
        
        alembic_cfg = Config(str(alembic_ini))
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        engine = create_engine(db_url)
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()
    except Exception as e:
        print(f"⚠️  Warning: Could not get current revision: {e}")
        return None


def get_migration_info(db_url: str) -> dict:
    """マイグレーション情報を取得"""
    try:
        alembic_ini = workspace_root / "migrations" / "alembic.ini"
        
        if not alembic_ini.exists():
            return {"error": "alembic.ini not found"}
        
        alembic_cfg = Config(str(alembic_ini))
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        script = ScriptDirectory.from_config(alembic_cfg)
        current_rev = get_current_revision(db_url)
        
        info = {
            "current_revision": current_rev,
            "head_revision": script.get_current_head(),
        }
        
        # 期待されるマイグレーションリビジョンを確認
        expected_revisions = [
            "20260107143030",  # add_user_statistics_tables
            "20260108_add_email",  # add_email_to_user_tables
            "20260108083830_remove_username",  # remove_username_from_user_tables
        ]
        
        if current_rev:
            # 適用されているマイグレーションを確認
            applied = []
            for rev_id in expected_revisions:
                try:
                    rev_obj = script.get_revision(rev_id)
                    if rev_obj:
                        # 現在のリビジョンから期待されるリビジョンまでのパスを確認
                        if current_rev == rev_id or script.iterate_revisions(current_rev, rev_id):
                            applied.append(rev_id)
                except Exception:
                    pass
            
            info["expected_revisions"] = expected_revisions
            info["applied_revisions"] = applied
        
        return info
    except Exception as e:
        return {"error": str(e)}


def check_production_deployment():
    """本番環境のデプロイ状況を確認"""
    db_url = get_database_url()
    
    print("=" * 60)
    print("本番環境デプロイ状況確認")
    print("=" * 60)
    print()
    print(f"データベース: {db_url.split('@')[1] if '@' in db_url else '***'}")
    print()
    
    engine = create_engine(db_url)
    
    # 1. マイグレーション状態の確認
    print("=" * 60)
    print("1. マイグレーション状態")
    print("=" * 60)
    migration_info = get_migration_info(db_url)
    
    if "error" in migration_info:
        print(f"❌ エラー: {migration_info['error']}")
    else:
        current_rev = migration_info.get("current_revision")
        head_rev = migration_info.get("head_revision")
        
        if current_rev:
            print(f"✅ 現在のリビジョン: {current_rev}")
        else:
            print("⚠️  マイグレーションが適用されていません")
        
        if head_rev:
            print(f"📋 最新リビジョン: {head_rev}")
        
        if current_rev == head_rev:
            print("✅ マイグレーションは最新です")
        elif current_rev:
            print(f"⚠️  マイグレーションが最新ではありません: {current_rev} → {head_rev}")
        
        # 期待されるマイグレーションの適用状況
        expected = migration_info.get("expected_revisions", [])
        applied = migration_info.get("applied_revisions", [])
        
        if expected:
            print()
            print("期待されるマイグレーション:")
            for rev_id in expected:
                status = "✅" if rev_id in applied or (current_rev and current_rev == rev_id) else "❌"
                print(f"  {status} {rev_id}")
    
    print()
    
    # 2. 統計テーブルの確認
    print("=" * 60)
    print("2. 統計テーブルの存在確認")
    print("=" * 60)
    
    stats_tables = [
        "user_statistics_daily",
        "user_statistics_weekly",
    ]
    
    for table_name in stats_tables:
        exists = check_table_exists(engine, table_name)
        status = "✅" if exists else "❌"
        print(f"{status} {table_name}: {'存在' if exists else '不存在'}")
    
    print()
    
    # 3. Userテーブルのカラム確認
    print("=" * 60)
    print("3. Userテーブル（MyPokedex）のカラム確認")
    print("=" * 60)
    
    user_table_exists = check_table_exists(engine, "User")
    if user_table_exists:
        email_exists = check_column_exists(engine, "User", "email")
        username_exists = check_column_exists(engine, "User", "username")
        last_login_at_exists = check_column_exists(engine, "User", "last_login_at")
        created_at_exists = check_column_exists(engine, "User", "created_at")
        
        print(f"✅ Userテーブル: 存在")
        print(f"  {'✅' if email_exists else '❌'} emailカラム: {'存在' if email_exists else '不存在'}")
        print(f"  {'✅' if not username_exists else '⚠️ '} usernameカラム: {'存在' if username_exists else '不存在（期待される状態）'}")
        print(f"  {'✅' if last_login_at_exists else '❌'} last_login_atカラム: {'存在' if last_login_at_exists else '不存在'}")
        print(f"  {'✅' if created_at_exists else '❌'} created_atカラム: {'存在' if created_at_exists else '不存在'}")
    else:
        print("❌ Userテーブル: 不存在")
    
    print()
    
    # 4. fishtrack_userテーブルのカラム確認
    print("=" * 60)
    print("4. fishtrack_userテーブル（FishTrack）のカラム確認")
    print("=" * 60)
    
    fishtrack_user_exists = check_table_exists(engine, "fishtrack_user")
    if fishtrack_user_exists:
        email_exists = check_column_exists(engine, "fishtrack_user", "email")
        username_exists = check_column_exists(engine, "fishtrack_user", "username")
        last_login_at_exists = check_column_exists(engine, "fishtrack_user", "last_login_at")
        created_at_exists = check_column_exists(engine, "fishtrack_user", "created_at")
        
        print(f"✅ fishtrack_userテーブル: 存在")
        print(f"  {'✅' if email_exists else '❌'} emailカラム: {'存在' if email_exists else '不存在'}")
        print(f"  {'✅' if not username_exists else '⚠️ '} usernameカラム: {'存在' if username_exists else '不存在（期待される状態）'}")
        print(f"  {'✅' if last_login_at_exists else '❌'} last_login_atカラム: {'存在' if last_login_at_exists else '不存在'}")
        print(f"  {'✅' if created_at_exists else '❌'} created_atカラム: {'存在' if created_at_exists else '不存在'}")
    else:
        print("❌ fishtrack_userテーブル: 不存在")
    
    print()
    
    # 5. サマリー
    print("=" * 60)
    print("5. サマリー")
    print("=" * 60)
    
    all_checks = []
    
    # マイグレーション
    if migration_info.get("current_revision") == migration_info.get("head_revision"):
        all_checks.append(("マイグレーション", True))
    else:
        all_checks.append(("マイグレーション", False))
    
    # 統計テーブル
    stats_ok = all(check_table_exists(engine, table) for table in stats_tables)
    all_checks.append(("統計テーブル", stats_ok))
    
    # Userテーブル
    if user_table_exists:
        user_ok = (
            check_column_exists(engine, "User", "email")
            and check_column_exists(engine, "User", "last_login_at")
            and check_column_exists(engine, "User", "created_at")
            and not check_column_exists(engine, "User", "username")
        )
        all_checks.append(("Userテーブル", user_ok))
    else:
        all_checks.append(("Userテーブル", False))
    
    # fishtrack_userテーブル
    if fishtrack_user_exists:
        fishtrack_ok = (
            check_column_exists(engine, "fishtrack_user", "email")
            and check_column_exists(engine, "fishtrack_user", "last_login_at")
            and check_column_exists(engine, "fishtrack_user", "created_at")
            and not check_column_exists(engine, "fishtrack_user", "username")
        )
        all_checks.append(("fishtrack_userテーブル", fishtrack_ok))
    else:
        all_checks.append(("fishtrack_userテーブル", False))
    
    for check_name, status in all_checks:
        icon = "✅" if status else "❌"
        print(f"{icon} {check_name}: {'OK' if status else 'NG'}")
    
    all_ok = all(status for _, status in all_checks)
    print()
    if all_ok:
        print("✅ すべての確認項目が正常です。本番環境へのデプロイは完了しています。")
    else:
        print("⚠️  一部の確認項目に問題があります。上記の詳細を確認してください。")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        check_production_deployment()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
