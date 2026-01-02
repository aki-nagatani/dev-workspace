#!/usr/bin/env python3
"""
データベースのチェック制約を確認し、モデル定義と比較するスクリプト

使用方法:
    # 本番環境
    export SHARED_DATABASE_URL="postgresql://user:pass@shared-db:5432/shared_db"
    python scripts/check_constraints.py --environment "Production" --output temp/check_constraints_production.md
    
    # ローカル環境
    export SHARED_DATABASE_URL="postgresql://shared_user:shared_password@localhost:5434/shared_db"
    python scripts/check_constraints.py --environment "Local Shared" --output temp/check_constraints_local.md
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# プロジェクトのルートディレクトリをパスに追加
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
except ImportError:
    print("Error: sqlalchemy is not installed. Please install it with: pip install sqlalchemy psycopg2-binary")
    sys.exit(1)


# モデル定義から期待されるチェック制約
EXPECTED_CHECK_CONSTRAINTS = {
    # FishTrack
    "rod_model": [
        ("ck_rod_length_in_range", "length_in BETWEEN 0 AND 11"),
        ("ck_rod_genre", "genre IN ('bait','spinning')"),
        ("ck_rod_carbon_rate_pct_range", "carbon_rate_pct IS NULL OR (carbon_rate_pct >= 0 AND carbon_rate_pct <= 100)"),
    ],
    "rod_holding": [
        ("ck_rod_holding_status", "status IN ('own','unowned')"),
        ("ck_rod_holding_condition", "condition IN ('new','used')"),
    ],
    "reel_model": [
        ("ck_reel_model_type", "reel_type IN ('spinning','bait')"),
    ],
    "reel_holding": [
        ("ck_reel_holding_status", "status IN ('own','unowned')"),
        ("ck_reel_holding_condition", "condition IN ('new','used')"),
    ],
    "tackle_spec_import_log": [
        ("ck_tsi_log_category", "category IN ('rod_model','reel_model','lure')"),
        ("ck_tsi_log_intent", "intent IN ('create','update','discard')"),
        ("ck_tsi_log_mode", "mode IN ('create','update','discard')"),
        ("ck_tsi_log_result", "result IN ('applied','discarded','failure')"),
    ],
    "ops_monitoring": [
        ("ck_ops_monitoring_status", "status IN ('OPEN','ACK','CLOSED')"),
    ],
    "ops_job_log": [
        ("ck_ops_job_log_status", "status IN ('SUCCESS','FAILURE','TIMEOUT','SKIPPED')"),
    ],
    # MyPokedex
    "regist": [
        ("ckRegistUserIdPositive", '"userId" > 0'),
    ],
    "party": [
        ("ck_party_slot_range", "slot BETWEEN 1 AND 6"),
    ],
}


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


def normalize_constraint_definition(definition: str) -> str:
    """制約定義を正規化して比較しやすくする"""
    # CHECK (...) の部分を抽出
    if definition.startswith("CHECK ("):
        definition = definition[7:]  # "CHECK (" を削除
    if definition.endswith(")"):
        definition = definition[:-1]  # 末尾の ")" を削除
    
    # 空白を正規化
    definition = " ".join(definition.split())
    
    # 大文字小文字を統一（IN句の値は小文字に）
    definition = definition.lower()
    
    return definition.strip()


def get_check_constraints(engine: Engine, table_name: str) -> List[Dict[str, str]]:
    """指定されたテーブルのチェック制約を取得"""
    constraints = []
    
    try:
        with engine.connect() as conn:
            # PostgreSQLのpg_constraintからチェック制約を取得
            # テーブル名を直接埋め込む（SQLインジェクション対策はテーブル名の検証で対応）
            result = conn.execute(text(f"""
                SELECT 
                    conname as constraint_name,
                    pg_get_constraintdef(oid) as constraint_definition
                FROM pg_constraint
                WHERE conrelid = '{table_name}'::regclass
                AND contype = 'c'
                ORDER BY conname
            """))
            
            for row in result:
                constraint_name = row[0]
                constraint_def = row[1]
                
                # CHECK (...) の部分を抽出
                if constraint_def.startswith("CHECK ("):
                    definition = constraint_def[7:-1]  # "CHECK (" と ")" を削除
                else:
                    definition = constraint_def
                
                constraints.append({
                    "name": constraint_name,
                    "definition": definition.strip(),
                    "full_definition": constraint_def,
                })
    except Exception as e:
        print(f"Warning: Failed to get check constraints for table {table_name}: {e}")
    
    return constraints


def compare_constraints(
    expected: List[Tuple[str, str]],
    actual: List[Dict[str, str]],
    table_name: str
) -> Dict[str, any]:
    """期待される制約と実際の制約を比較"""
    result = {
        "table": table_name,
        "expected_count": len(expected),
        "actual_count": len(actual),
        "matches": [],
        "missing": [],
        "extra": [],
        "mismatched": [],
    }
    
    # 実際の制約を辞書に変換（名前をキーに）
    actual_dict = {c["name"]: c for c in actual}
    
    # 期待される制約をチェック
    for expected_name, expected_def in expected:
        if expected_name in actual_dict:
            actual_def = actual_dict[expected_name]["definition"]
            # 定義を正規化して比較
            normalized_expected = normalize_constraint_definition(expected_def)
            normalized_actual = normalize_constraint_definition(actual_def)
            
            if normalized_expected == normalized_actual:
                result["matches"].append({
                    "name": expected_name,
                    "definition": actual_def,
                })
            else:
                result["mismatched"].append({
                    "name": expected_name,
                    "expected": expected_def,
                    "actual": actual_def,
                })
        else:
            result["missing"].append({
                "name": expected_name,
                "definition": expected_def,
            })
    
    # 余分な制約をチェック
    expected_names = {name for name, _ in expected}
    for actual_constraint in actual:
        if actual_constraint["name"] not in expected_names:
            result["extra"].append({
                "name": actual_constraint["name"],
                "definition": actual_constraint["definition"],
            })
    
    return result


def analyze_all_constraints(engine: Engine) -> Dict[str, any]:
    """すべてのテーブルのチェック制約を分析"""
    results = {}
    
    for table_name in EXPECTED_CHECK_CONSTRAINTS.keys():
        expected = EXPECTED_CHECK_CONSTRAINTS[table_name]
        actual = get_check_constraints(engine, table_name)
        results[table_name] = compare_constraints(expected, actual, table_name)
    
    return results


def generate_markdown_report(results: Dict[str, any], environment: str) -> str:
    """Markdownレポートを生成"""
    lines = []
    lines.append(f"# チェック制約確認レポート - {environment}")
    lines.append("")
    lines.append(f"**作成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # サマリー
    total_expected = sum(r["expected_count"] for r in results.values())
    total_actual = sum(r["actual_count"] for r in results.values())
    total_matches = sum(len(r["matches"]) for r in results.values())
    total_missing = sum(len(r["missing"]) for r in results.values())
    total_extra = sum(len(r["extra"]) for r in results.values())
    total_mismatched = sum(len(r["mismatched"]) for r in results.values())
    
    lines.append("## サマリー")
    lines.append("")
    lines.append(f"- **期待される制約数**: {total_expected}")
    lines.append(f"- **実際の制約数**: {total_actual}")
    lines.append(f"- **一致**: {total_matches} ✅")
    lines.append(f"- **不足**: {total_missing} ⚠️")
    lines.append(f"- **余分**: {total_extra} ⚠️")
    lines.append(f"- **不一致**: {total_mismatched} ❌")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # テーブルごとの詳細
    for table_name, result in results.items():
        lines.append(f"## テーブル: `{table_name}`")
        lines.append("")
        lines.append(f"- **期待される制約数**: {result['expected_count']}")
        lines.append(f"- **実際の制約数**: {result['actual_count']}")
        lines.append("")
        
        if result["matches"]:
            lines.append("### ✅ 一致した制約")
            lines.append("")
            for match in result["matches"]:
                lines.append(f"- **{match['name']}**: `{match['definition']}`")
            lines.append("")
        
        if result["missing"]:
            lines.append("### ⚠️ 不足している制約")
            lines.append("")
            for missing in result["missing"]:
                lines.append(f"- **{missing['name']}**: `{missing['definition']}`")
            lines.append("")
        
        if result["extra"]:
            lines.append("### ⚠️ 余分な制約")
            lines.append("")
            for extra in result["extra"]:
                lines.append(f"- **{extra['name']}**: `{extra['definition']}`")
            lines.append("")
        
        if result["mismatched"]:
            lines.append("### ❌ 定義が不一致な制約")
            lines.append("")
            for mismatch in result["mismatched"]:
                lines.append(f"- **{mismatch['name']}**:")
                lines.append(f"  - 期待: `{mismatch['expected']}`")
                lines.append(f"  - 実際: `{mismatch['actual']}`")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="データベースのチェック制約を確認")
    parser.add_argument(
        "--environment",
        type=str,
        default="Unknown",
        help="環境名（例: Production, Local Shared）"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="出力ファイルパス（指定しない場合は標準出力）"
    )
    
    args = parser.parse_args()
    
    try:
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        print(f"環境: {args.environment}")
        print(f"データベース: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        print("=" * 60)
        print()
        
        results = analyze_all_constraints(engine)
        
        report = generate_markdown_report(results, args.environment)
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"レポートを保存しました: {output_path}")
        else:
            print(report)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

