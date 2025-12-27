#!/usr/bin/env python3
"""
2つのデータベーススキーマ分析結果を比較するスクリプト

使用方法:
    python scripts/compare_db_schemas.py \
      --production docs/db_schema_production.md \
      --local docs/db_schema_local.md \
      --output docs/db_schema_comparison.md
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


def parse_markdown_schema(file_path: Path) -> Dict[str, Any]:
    """Markdown形式のスキーマ分析結果をパース"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    schema = {
        "analyzed_at": None,
        "environment": None,
        "total_tables": 0,
        "total_records": 0,
        "tables": {},
    }
    
    # 環境情報を抽出
    env_match = re.search(r"\*\*環境\*\*: (.+)", content)
    if env_match:
        schema["environment"] = env_match.group(1)
    
    analyzed_match = re.search(r"\*\*分析日時\*\*: (.+)", content)
    if analyzed_match:
        schema["analyzed_at"] = analyzed_match.group(1)
    
    # サマリーを抽出
    total_tables_match = re.search(r"\*\*テーブル数\*\*: (\d+)", content)
    if total_tables_match:
        schema["total_tables"] = int(total_tables_match.group(1))
    
    total_records_match = re.search(r"\*\*総レコード数\*\*: ([\d,]+)", content)
    if total_records_match:
        schema["total_records"] = int(total_records_match.group(1).replace(",", ""))
    
    # テーブル一覧を抽出
    table_section_match = re.search(r"## テーブル一覧\s*\n\n(.*?)\n\n##", content, re.DOTALL)
    if table_section_match:
        table_section = table_section_match.group(1)
        # テーブル行を抽出
        table_rows = re.findall(r"\| `([^`]+)` \| (\d+) \| ([\d,]+) \|", table_section)
        for table_name, col_count, record_count in table_rows:
            schema["tables"][table_name] = {
                "column_count": int(col_count),
                "record_count": int(record_count.replace(",", "")),
            }
    
    # テーブル詳細を抽出
    detail_sections = re.finditer(r"### ([^\n]+)\n\n(.*?)(?=\n### |\Z)", content, re.DOTALL)
    for match in detail_sections:
        table_name = match.group(1).strip()
        detail_content = match.group(2)
        
        if table_name not in schema["tables"]:
            schema["tables"][table_name] = {
                "column_count": 0,
                "record_count": 0,
            }
        
        # レコード数を抽出
        record_match = re.search(r"\*\*レコード数\*\*: ([\d,]+)", detail_content)
        if record_match:
            schema["tables"][table_name]["record_count"] = int(record_match.group(1).replace(",", ""))
        
        # カラム定義を抽出
        columns = []
        column_section_match = re.search(r"#### カラム定義\n\n(.*?)(?=\n#### |\Z)", detail_content, re.DOTALL)
        if column_section_match:
            column_table = column_section_match.group(1)
            column_rows = re.findall(r"\| `([^`]+)` \| `([^`]+)` \| ([✓✗]) \| ([^\|]+) \|", column_table)
            for col_name, col_type, nullable, default in column_rows:
                columns.append({
                    "name": col_name,
                    "type": col_type,
                    "nullable": nullable == "✓",
                    "default": default.strip() if default.strip() != "-" else None,
                })
        
        schema["tables"][table_name]["columns"] = columns
        schema["tables"][table_name]["column_count"] = len(columns)
        
        # 主キーを抽出
        pk_match = re.search(r"#### 主キー\n\n- (.+)", detail_content)
        if pk_match:
            pk_str = pk_match.group(1)
            schema["tables"][table_name]["primary_keys"] = [k.strip().strip("`") for k in pk_str.split(",")]
        else:
            schema["tables"][table_name]["primary_keys"] = []
        
        # 外部キーを抽出
        fks = []
        fk_section_match = re.search(r"#### 外部キー\n\n(.*?)(?=\n#### |\Z)", detail_content, re.DOTALL)
        if fk_section_match:
            fk_lines = fk_section_match.group(1).strip().split("\n")
            for line in fk_lines:
                if line.startswith("- **"):
                    fk_match = re.search(r"- \*\*([^\*]+)\*\*: (.+) → `([^`]+)`\(([^\)]+)\)", line)
                    if fk_match:
                        fks.append({
                            "name": fk_match.group(1),
                            "constrained_columns": [c.strip().strip("`") for c in fk_match.group(2).split(",")],
                            "referred_table": fk_match.group(3),
                            "referred_columns": [c.strip().strip("`") for c in fk_match.group(4).split(",")],
                        })
        schema["tables"][table_name]["foreign_keys"] = fks
        
        # インデックスを抽出
        indexes = []
        idx_section_match = re.search(r"#### インデックス\n\n(.*?)(?=\n#### |\Z)", detail_content, re.DOTALL)
        if idx_section_match:
            idx_lines = idx_section_match.group(1).strip().split("\n")
            for line in idx_lines:
                if line.startswith("- **"):
                    idx_match = re.search(r"- \*\*([^\*]+)\*\*: (.+?)( \(UNIQUE\))?$", line)
                    if idx_match:
                        indexes.append({
                            "name": idx_match.group(1),
                            "columns": [c.strip().strip("`") for c in idx_match.group(2).split(",")],
                            "unique": idx_match.group(3) is not None,
                        })
        schema["tables"][table_name]["indexes"] = indexes
    
    return schema


def compare_schemas(prod_schema: Dict[str, Any], local_schema: Dict[str, Any]) -> Dict[str, Any]:
    """2つのスキーマを比較"""
    comparison = {
        "production": {
            "analyzed_at": prod_schema.get("analyzed_at"),
            "total_tables": prod_schema.get("total_tables", 0),
            "total_records": prod_schema.get("total_records", 0),
        },
        "local": {
            "analyzed_at": local_schema.get("analyzed_at"),
            "total_tables": local_schema.get("total_tables", 0),
            "total_records": local_schema.get("total_records", 0),
        },
        "differences": {
            "tables_missing_in_local": [],
            "tables_missing_in_production": [],
            "tables_with_differences": [],
        },
    }
    
    prod_tables = set(prod_schema.get("tables", {}).keys())
    local_tables = set(local_schema.get("tables", {}).keys())
    
    # テーブルの存在差異
    comparison["differences"]["tables_missing_in_local"] = list(prod_tables - local_tables)
    comparison["differences"]["tables_missing_in_production"] = list(local_tables - prod_tables)
    
    # 共通テーブルの詳細比較
    common_tables = prod_tables & local_tables
    for table_name in common_tables:
        prod_table = prod_schema["tables"][table_name]
        local_table = local_schema["tables"][table_name]
        
        table_diff = {
            "table_name": table_name,
            "column_differences": [],
            "record_count_diff": prod_table.get("record_count", 0) - local_table.get("record_count", 0),
            "primary_key_diff": False,
            "foreign_key_diff": False,
        }
        
        # カラム比較
        prod_cols = {col["name"]: col for col in prod_table.get("columns", [])}
        local_cols = {col["name"]: col for col in local_table.get("columns", [])}
        
        for col_name in set(prod_cols.keys()) | set(local_cols.keys()):
            if col_name not in prod_cols:
                table_diff["column_differences"].append({
                    "column": col_name,
                    "issue": "Missing in production",
                })
            elif col_name not in local_cols:
                table_diff["column_differences"].append({
                    "column": col_name,
                    "issue": "Missing in local",
                })
            else:
                prod_col = prod_cols[col_name]
                local_col = local_cols[col_name]
                
                if prod_col["type"] != local_col["type"]:
                    table_diff["column_differences"].append({
                        "column": col_name,
                        "issue": f"Type mismatch: prod={prod_col['type']}, local={local_col['type']}",
                    })
                
                if prod_col["nullable"] != local_col["nullable"]:
                    table_diff["column_differences"].append({
                        "column": col_name,
                        "issue": f"Nullable mismatch: prod={prod_col['nullable']}, local={local_col['nullable']}",
                    })
        
        # 主キー比較
        prod_pk = set(prod_table.get("primary_keys", []))
        local_pk = set(local_table.get("primary_keys", []))
        if prod_pk != local_pk:
            table_diff["primary_key_diff"] = True
        
        # 外部キー比較（簡易）
        if len(prod_table.get("foreign_keys", [])) != len(local_table.get("foreign_keys", [])):
            table_diff["foreign_key_diff"] = True
        
        if (table_diff["column_differences"] or 
            table_diff["record_count_diff"] != 0 or
            table_diff["primary_key_diff"] or
            table_diff["foreign_key_diff"]):
            comparison["differences"]["tables_with_differences"].append(table_diff)
    
    return comparison


def generate_comparison_report(comparison: Dict[str, Any], output_path: Path):
    """比較レポートをMarkdown形式で生成"""
    md = f"""# データベーススキーマ比較レポート

## 分析日時

- **作成日時**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 環境情報

### 本番環境
- **分析日時**: {comparison['production']['analyzed_at'] or 'N/A'}
- **テーブル数**: {comparison['production']['total_tables']}
- **総レコード数**: {comparison['production']['total_records']:,}

### ローカルDocker環境
- **分析日時**: {comparison['local']['analyzed_at'] or 'N/A'}
- **テーブル数**: {comparison['local']['total_tables']}
- **総レコード数**: {comparison['local']['total_records']:,}

## サマリー

| 項目 | 本番 | ローカル | 差異 |
|------|------|----------|------|
| テーブル数 | {comparison['production']['total_tables']} | {comparison['local']['total_tables']} | {comparison['production']['total_tables'] - comparison['local']['total_tables']} |
| 総レコード数 | {comparison['production']['total_records']:,} | {comparison['local']['total_records']:,} | {comparison['production']['total_records'] - comparison['local']['total_records']:,} |

## 差異の詳細

### 本番にのみ存在するテーブル

"""
    
    if comparison["differences"]["tables_missing_in_local"]:
        for table in comparison["differences"]["tables_missing_in_local"]:
            md += f"- `{table}`\n"
    else:
        md += "- なし\n"
    
    md += "\n### ローカルのみに存在するテーブル\n\n"
    
    if comparison["differences"]["tables_missing_in_production"]:
        for table in comparison["differences"]["tables_missing_in_production"]:
            md += f"- `{table}`\n"
    else:
        md += "- なし\n"
    
    md += "\n### 差異があるテーブル\n\n"
    
    if comparison["differences"]["tables_with_differences"]:
        for table_diff in comparison["differences"]["tables_with_differences"]:
            md += f"#### {table_diff['table_name']}\n\n"
            
            if table_diff["column_differences"]:
                md += "**カラム差異**:\n"
                for col_diff in table_diff["column_differences"]:
                    md += f"- `{col_diff['column']}`: {col_diff['issue']}\n"
                md += "\n"
            
            if table_diff["record_count_diff"] != 0:
                md += f"**レコード数差異**: {table_diff['record_count_diff']:,}\n\n"
            
            if table_diff["primary_key_diff"]:
                md += "**主キー差異**: あり\n\n"
            
            if table_diff["foreign_key_diff"]:
                md += "**外部キー差異**: あり\n\n"
    else:
        md += "- なし\n"
    
    md += "\n## 推奨事項\n\n"
    md += "1. 差異があるテーブルについては、マイグレーションで同期する必要があります。\n"
    md += "2. 本番にのみ存在するテーブルは、ローカル環境にも作成する必要があります。\n"
    md += "3. ローカルのみに存在するテーブルは、本番環境に反映するか、削除する必要があります。\n"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)
    
    print(f"✓ Comparison report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="2つのデータベーススキーマ分析結果を比較"
    )
    parser.add_argument(
        "--production",
        "-p",
        type=str,
        required=True,
        help="本番環境の分析結果ファイル（Markdown）",
    )
    parser.add_argument(
        "--local",
        "-l",
        type=str,
        required=True,
        help="ローカル環境の分析結果ファイル（Markdown）",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="比較レポートの出力ファイルパス（Markdown）",
    )
    
    args = parser.parse_args()
    
    prod_path = Path(args.production)
    local_path = Path(args.local)
    output_path = Path(args.output)
    
    if not prod_path.exists():
        print(f"Error: Production schema file not found: {prod_path}")
        sys.exit(1)
    
    if not local_path.exists():
        print(f"Error: Local schema file not found: {local_path}")
        sys.exit(1)
    
    print("Parsing production schema...")
    prod_schema = parse_markdown_schema(prod_path)
    
    print("Parsing local schema...")
    local_schema = parse_markdown_schema(local_path)
    
    print("Comparing schemas...")
    comparison = compare_schemas(prod_schema, local_schema)
    
    print("Generating comparison report...")
    generate_comparison_report(comparison, output_path)
    
    print("\n=== Comparison completed ===")
    print(f"Tables missing in local: {len(comparison['differences']['tables_missing_in_local'])}")
    print(f"Tables missing in production: {len(comparison['differences']['tables_missing_in_production'])}")
    print(f"Tables with differences: {len(comparison['differences']['tables_with_differences'])}")


if __name__ == "__main__":
    import sys
    main()

