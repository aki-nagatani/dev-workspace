#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
おたよりナビ データベースマイグレーション確認スクリプト（シンプル版）
EC2上のDockerコンテナ内で実行することを想定
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    db_url = os.getenv("SHARED_DATABASE_URL")
    if not db_url:
        print("❌ Error: SHARED_DATABASE_URL not set")
        sys.exit(1)
    
    print("=" * 80)
    print("おたよりナビ データベースマイグレーション確認")
    print("=" * 80)
    print()
    
    try:
        engine = create_engine(db_url)
        
        # 1. マイグレーション状態確認
        print("【1. マイグレーション状態確認】")
        print("-" * 80)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num"))
            versions = [r[0] for r in result]
            
            if versions:
                print("現在のマイグレーション状態:")
                for v in versions:
                    print(f"  - {v}")
                
                if "20260204001210" in versions:
                    print("✅ おたよりナビ用マイグレーション（20260204001210）が適用済み")
                else:
                    print("❌ おたよりナビ用マイグレーション（20260204001210）が未適用")
            else:
                print("⚠️  マイグレーションが適用されていません")
        
        print()
        
        # 2. テーブル存在確認
        print("【2. テーブル存在確認】")
        print("-" * 80)
        
        inspector = inspect(engine)
        tables = ["families", "users", "family_invites", "documents"]
        all_exist = True
        
        for table in tables:
            exists = inspector.has_table(table)
            status = "✅" if exists else "❌"
            print(f"  {status} {table}: {'存在' if exists else '不存在'}")
            if not exists:
                all_exist = False
        
        print()
        
        # 3. サマリー
        print("=" * 80)
        print("【確認結果サマリー】")
        print("=" * 80)
        
        if "20260204001210" in versions:
            print("✅ マイグレーション状態: 正常（おたよりナビ用マイグレーション適用済み）")
        else:
            print("❌ マイグレーション状態: おたよりナビ用マイグレーションが未適用")
        
        if all_exist:
            print("✅ テーブル状態: 正常（すべてのテーブルが存在）")
        else:
            print("❌ テーブル状態: 異常（一部のテーブルが存在しない）")
        
        print()
        
        # 4. 推奨アクション
        if not all_exist or "20260204001210" not in versions:
            print("【推奨アクション】")
            print("-" * 80)
            print("マイグレーションを実行してください:")
            print("  cd /app/../dev-workspace")
            print("  python3 scripts/run_migrations.py")
            print()
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
