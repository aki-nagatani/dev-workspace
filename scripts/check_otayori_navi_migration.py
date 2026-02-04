#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
おたよりナビ データベースマイグレーション確認スクリプト
本番環境（shared-db）でおたよりナビ用テーブルが作成されているか確認する
"""

import os
import sys
import io
from pathlib import Path

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトのルートディレクトリをパスに追加
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

try:
    from sqlalchemy import create_engine, text, inspect
    import boto3
except ImportError as e:
    print(f"Error: 必要なライブラリがインストールされていません: {e}")
    sys.exit(1)


def get_database_url_from_secrets_manager() -> str | None:
    """Secrets ManagerからデータベースURLを取得"""
    try:
        secrets_client = boto3.client('secretsmanager', region_name='ap-northeast-1')
        secret_name = "otayori/db-url"
        
        response = secrets_client.get_secret_value(SecretId=secret_name)
        db_url = response['SecretString']
        return db_url
    except Exception as e:
        print(f"  ⚠️  Secrets Managerからの取得に失敗: {e}")
        return None


def get_database_url() -> str:
    """環境変数またはSecrets ManagerからデータベースURLを取得"""
    # 環境変数から取得を試みる
    url = (
        os.getenv("SHARED_DATABASE_URL")
        or os.getenv("SHARED_DB_URL")
        or os.getenv("OTAYORI_NAVI_DATABASE_URL")
    )
    
    if url:
        return url
    
    # Secrets Managerから取得を試みる
    url = get_database_url_from_secrets_manager()
    if url:
        return url
    
    raise RuntimeError(
        "データベースURLが設定されていません。\n"
        "環境変数（SHARED_DATABASE_URL, SHARED_DB_URL, OTAYORI_NAVI_DATABASE_URL）を設定するか、\n"
        "Secrets Manager（otayori/db-url）に設定してください。"
    )


def check_table_exists(engine, table_name: str) -> bool:
    """テーブルが存在するか確認"""
    inspector = inspect(engine)
    return inspector.has_table(table_name)


def check_migration_status(db_url: str):
    """マイグレーション状態とテーブル存在を確認"""
    print("=" * 80)
    print("おたよりナビ データベースマイグレーション確認")
    print("=" * 80)
    print()
    
    # データベースURLをマスクして表示
    masked_url = db_url.split('@')[-1] if '@' in db_url else db_url
    print(f"データベース: {masked_url}")
    print()
    
    try:
        engine = create_engine(db_url)
        
        # 1. alembic_versionテーブルの確認
        print("【1. マイグレーション状態確認】")
        print("-" * 80)
        
        has_version_table = check_table_exists(engine, "alembic_version")
        if not has_version_table:
            print("  ⚠️  alembic_versionテーブルが存在しません")
            print("     マイグレーションが適用されていない可能性があります")
        else:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num"))
                versions = [row[0] for row in result]
                
                if versions:
                    print(f"  ✅ 現在のマイグレーション状態:")
                    for version in versions:
                        print(f"     - {version}")
                    
                    # おたよりナビ用マイグレーションの確認
                    target_migration = "20260204001210"
                    if target_migration in versions:
                        print(f"  ✅ おたよりナビ用マイグレーション（{target_migration}）が適用済み")
                    else:
                        print(f"  ❌ おたよりナビ用マイグレーション（{target_migration}）が未適用")
                else:
                    print("  ⚠️  マイグレーションが適用されていません")
        
        print()
        
        # 2. おたよりナビ用テーブルの存在確認
        print("【2. おたよりナビ用テーブル存在確認】")
        print("-" * 80)
        
        required_tables = [
            "families",
            "users",
            "family_invites",
            "documents",
        ]
        
        all_exist = True
        for table_name in required_tables:
            exists = check_table_exists(engine, table_name)
            status = "✅ 存在" if exists else "❌ 不存在"
            print(f"  {table_name}: {status}")
            if not exists:
                all_exist = False
        
        print()
        
        # 3. テーブル構造の確認（存在する場合）
        if all_exist:
            print("【3. テーブル構造確認】")
            print("-" * 80)
            
            inspector = inspect(engine)
            
            for table_name in required_tables:
                print(f"\n  [{table_name}]")
                columns = inspector.get_columns(table_name)
                print(f"    カラム数: {len(columns)}")
                for col in columns[:5]:  # 最初の5カラムのみ表示
                    nullable = "NULL可" if col['nullable'] else "NOT NULL"
                    print(f"      - {col['name']}: {col['type']} ({nullable})")
                if len(columns) > 5:
                    print(f"      ... 他 {len(columns) - 5} カラム")
                
                # インデックスの確認
                indexes = inspector.get_indexes(table_name)
                if indexes:
                    print(f"    インデックス数: {len(indexes)}")
                    for idx in indexes[:3]:  # 最初の3インデックスのみ表示
                        print(f"      - {idx['name']}: {', '.join(idx['column_names'])}")
                    if len(indexes) > 3:
                        print(f"      ... 他 {len(indexes) - 3} インデックス")
        
        print()
        
        # 4. サマリー
        print("=" * 80)
        print("【確認結果サマリー】")
        print("=" * 80)
        
        if has_version_table:
            if target_migration in versions:
                print("✅ マイグレーション状態: 正常（おたよりナビ用マイグレーション適用済み）")
            else:
                print("⚠️  マイグレーション状態: おたよりナビ用マイグレーションが未適用")
        else:
            print("❌ マイグレーション状態: alembic_versionテーブルが存在しない")
        
        if all_exist:
            print("✅ テーブル状態: 正常（すべてのテーブルが存在）")
        else:
            print("❌ テーブル状態: 異常（一部のテーブルが存在しない）")
        
        print()
        
        # 5. 推奨アクション
        if not all_exist or (has_version_table and target_migration not in versions):
            print("【推奨アクション】")
            print("-" * 80)
            print("  マイグレーションを実行してください:")
            print("  ")
            print("  export SHARED_DATABASE_URL=\"<データベースURL>\"")
            print("  cd dev-workspace")
            print("  python scripts/run_migrations.py")
            print()
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    try:
        db_url = get_database_url()
        check_migration_status(db_url)
    except RuntimeError as e:
        print(f"❌ {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
