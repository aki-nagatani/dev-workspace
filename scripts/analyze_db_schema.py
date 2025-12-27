#!/usr/bin/env python3
"""
データベースのスキーマを分析してドキュメント化するスクリプト

本番DBとローカルDBのテーブル構造、カラム定義、レコード数を比較します。

使用方法:
    # 本番DBを分析
    export SHARED_DATABASE_URL="postgresql://user:pass@shared-db:5432/shared_db"
    python scripts/analyze_db_schema.py --output docs/db_schema_production.md
    
    # ローカルDBを分析
    export SHARED_DATABASE_URL="postgresql://user:pass@localhost:5432/local_db"
    python scripts/analyze_db_schema.py --output docs/db_schema_local.md
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# プロジェクトのルートディレクトリをパスに追加
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

try:
    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.engine import Engine
except ImportError:
    print("Error: sqlalchemy is not installed. Please install it with: pip install sqlalchemy psycopg2-binary")
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


def get_table_info(engine: Engine, table_name: str) -> Dict[str, Any]:
    """テーブルの詳細情報を取得"""
    inspector = inspect(engine)
    
    info = {
        "name": table_name,
        "columns": [],
        "primary_keys": [],
        "foreign_keys": [],
        "indexes": [],
        "unique_constraints": [],
        "check_constraints": [],
        "record_count": 0,
    }
    
    try:
        # カラム情報
        columns = inspector.get_columns(table_name)
        for col in columns:
            col_info = {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
                "default": str(col.get("default", "")) if col.get("default") else None,
                "autoincrement": col.get("autoincrement", False),
            }
            info["columns"].append(col_info)
        
        # 主キー
        pk_constraint = inspector.get_pk_constraint(table_name)
        if pk_constraint and pk_constraint.get("constrained_columns"):
            info["primary_keys"] = pk_constraint["constrained_columns"]
        
        # 外部キー
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            fk_info = {
                "name": fk.get("name", ""),
                "constrained_columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"],
            }
            info["foreign_keys"].append(fk_info)
        
        # インデックス
        indexes = inspector.get_indexes(table_name)
        for idx in indexes:
            idx_info = {
                "name": idx["name"],
                "columns": idx["column_names"],
                "unique": idx.get("unique", False),
            }
            info["indexes"].append(idx_info)
        
        # ユニーク制約
        unique_constraints = inspector.get_unique_constraints(table_name)
        for uc in unique_constraints:
            uc_info = {
                "name": uc.get("name", ""),
                "columns": uc["column_names"],
            }
            info["unique_constraints"].append(uc_info)
        
        # チェック制約（PostgreSQLの場合）
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT conname, pg_get_constraintdef(oid) as definition
                    FROM pg_constraint
                    WHERE conrelid = :table_name::regclass
                    AND contype = 'c'
                """), {"table_name": table_name})
                for row in result:
                    info["check_constraints"].append({
                        "name": row[0],
                        "definition": row[1],
                    })
        except Exception:
            pass
        
        # レコード数
        with engine.connect() as conn:
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
            info["record_count"] = result.scalar()
            
    except Exception as e:
        print(f"Warning: Failed to get info for table {table_name}: {e}")
    
    return info


def analyze_database(engine: Engine) -> Dict[str, Any]:
    """データベース全体を分析"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # alembic_versionテーブルは除外
    tables = [t for t in tables if t != "alembic_version"]
    
    database_info = {
        "analyzed_at": datetime.now().isoformat(),
        "tables": {},
        "total_tables": len(tables),
        "total_records": 0,
    }
    
    print(f"Analyzing {len(tables)} tables...")
    for table_name in sorted(tables):
        print(f"  - {table_name}")
        table_info = get_table_info(engine, table_name)
        database_info["tables"][table_name] = table_info
        database_info["total_records"] += table_info["record_count"]
    
    return database_info


def generate_markdown(database_info: Dict[str, Any], environment: str = "Unknown") -> str:
    """Markdown形式のドキュメントを生成"""
    md = f"""# データベーススキーマ分析レポート

## 環境情報

- **環境**: {environment}
- **分析日時**: {database_info['analyzed_at']}
- **テーブル数**: {database_info['total_tables']}
- **総レコード数**: {database_info['total_records']:,}

## テーブル一覧

"""
    
    # テーブルごとのサマリー
    md += "| テーブル名 | カラム数 | レコード数 | 主キー | 外部キー数 |\n"
    md += "|-----------|---------|-----------|--------|----------|\n"
    
    for table_name, table_info in sorted(database_info["tables"].items()):
        pk_str = ", ".join(table_info["primary_keys"]) if table_info["primary_keys"] else "-"
        fk_count = len(table_info["foreign_keys"])
        md += f"| `{table_name}` | {len(table_info['columns'])} | {table_info['record_count']:,} | {pk_str} | {fk_count} |\n"
    
    md += "\n## テーブル詳細\n\n"
    
    # 各テーブルの詳細
    for table_name, table_info in sorted(database_info["tables"].items()):
        md += f"### {table_name}\n\n"
        md += f"**レコード数**: {table_info['record_count']:,}\n\n"
        
        # カラム定義
        md += "#### カラム定義\n\n"
        md += "| カラム名 | 型 | NULL許可 | デフォルト | 自動増分 |\n"
        md += "|---------|-----|---------|-----------|---------|\n"
        
        for col in table_info["columns"]:
            nullable = "✓" if col["nullable"] else "✗"
            default = col["default"] if col["default"] else "-"
            autoinc = "✓" if col["autoincrement"] else "✗"
            md += f"| `{col['name']}` | `{col['type']}` | {nullable} | {default} | {autoinc} |\n"
        
        md += "\n"
        
        # 主キー
        if table_info["primary_keys"]:
            md += f"#### 主キー\n\n"
            md += f"- {', '.join(f'`{pk}`' for pk in table_info['primary_keys'])}\n\n"
        
        # 外部キー
        if table_info["foreign_keys"]:
            md += f"#### 外部キー\n\n"
            for fk in table_info["foreign_keys"]:
                constrained = ", ".join(f'`{c}`' for c in fk["constrained_columns"])
                referred = ", ".join(f'`{c}`' for c in fk["referred_columns"])
                md += f"- **{fk['name']}**: {constrained} → `{fk['referred_table']}`({referred})\n"
            md += "\n"
        
        # インデックス
        if table_info["indexes"]:
            md += f"#### インデックス\n\n"
            for idx in table_info["indexes"]:
                columns = ", ".join(f'`{c}`' for c in idx["columns"])
                unique = " (UNIQUE)" if idx["unique"] else ""
                md += f"- **{idx['name']}**: {columns}{unique}\n"
            md += "\n"
        
        # ユニーク制約
        if table_info["unique_constraints"]:
            md += f"#### ユニーク制約\n\n"
            for uc in table_info["unique_constraints"]:
                columns = ", ".join(f'`{c}`' for c in uc["columns"])
                md += f"- **{uc['name']}**: {columns}\n"
            md += "\n"
        
        # チェック制約
        if table_info["check_constraints"]:
            md += f"#### チェック制約\n\n"
            for cc in table_info["check_constraints"]:
                md += f"- **{cc['name']}**: `{cc['definition']}`\n"
            md += "\n"
        
        md += "---\n\n"
    
    return md


def main():
    parser = argparse.ArgumentParser(
        description="データベースのスキーマを分析してドキュメント化"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="出力ファイルパス（Markdown形式）",
    )
    parser.add_argument(
        "--environment",
        "-e",
        type=str,
        default="Unknown",
        help="環境名（例: Production, Local Docker）",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="JSON形式で出力",
    )
    
    args = parser.parse_args()
    
    # データベースURLを取得
    db_url = get_database_url()
    
    # データベース接続
    print(f"Connecting to database...")
    print(f"URL: {db_url.split('@')[1] if '@' in db_url else '***'}")
    
    try:
        engine = create_engine(db_url)
        
        # データベースを分析
        database_info = analyze_database(engine)
        
        # 出力
        if args.json:
            import json
            output = json.dumps(database_info, indent=2, ensure_ascii=False)
        else:
            output = generate_markdown(database_info, args.environment)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"\n[OK] Analysis saved to: {output_path}")
        else:
            print("\n" + output)
        
        print(f"\n=== Analysis completed ===")
        print(f"Tables: {database_info['total_tables']}")
        print(f"Total records: {database_info['total_records']:,}")
        
    except Exception as e:
        print(f"\n=== Analysis failed ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

