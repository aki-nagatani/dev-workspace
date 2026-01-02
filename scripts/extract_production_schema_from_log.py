#!/usr/bin/env python3
"""
GitHub ActionsのログからBase64エンコードされた分析結果を抽出するスクリプト

使用方法:
    python scripts/extract_production_schema_from_log.py <run_id>
    
または、ログファイルから直接抽出:
    python scripts/extract_production_schema_from_log.py --log-file <log_file>
"""

import sys
import base64
import argparse
import subprocess
from pathlib import Path


def extract_base64_from_log(log_content: str) -> bytes:
    """ログからBase64エンコードされた内容を抽出"""
    lines = log_content.split('\n')
    base64_lines = []
    in_base64_section = False
    
    for line in lines:
        if "=== Analysis Result (Base64 Encoded) ===" in line:
            in_base64_section = True
            continue
        if in_base64_section:
            if line.strip() == "":
                continue
            if line.startswith("To decode"):
                continue
            # Base64エンコードされた行を収集
            base64_lines.append(line.strip())
    
    if not base64_lines:
        raise ValueError("Base64エンコードされた内容が見つかりませんでした")
    
    # Base64文字列を結合
    base64_content = ''.join(base64_lines)
    
    # デコード
    try:
        decoded = base64.b64decode(base64_content)
        return decoded
    except Exception as e:
        raise ValueError(f"Base64デコードに失敗しました: {e}")


def get_log_from_github(run_id: str, repo: str = "aki-nagatani/FishTrack") -> str:
    """GitHub Actionsのログを取得"""
    try:
        result = subprocess.run(
            ["gh", "run", "view", run_id, "--log", "--repo", repo],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"GitHub CLIでログの取得に失敗しました: {e}")


def main():
    parser = argparse.ArgumentParser(description="GitHub Actionsのログから分析結果を抽出")
    parser.add_argument("run_id", nargs="?", help="GitHub Actionsの実行ID")
    parser.add_argument("--log-file", help="ログファイルのパス")
    parser.add_argument("--output", "-o", default="db_schema_production.md", help="出力ファイル名")
    parser.add_argument("--repo", default="aki-nagatani/FishTrack", help="リポジトリ名")
    
    args = parser.parse_args()
    
    # ログを取得
    if args.log_file:
        log_content = Path(args.log_file).read_text(encoding='utf-8')
    elif args.run_id:
        log_content = get_log_from_github(args.run_id, args.repo)
    else:
        parser.error("run_idまたは--log-fileを指定してください")
    
    # Base64エンコードされた内容を抽出
    try:
        decoded_content = extract_base64_from_log(log_content)
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)
    
    # ファイルに保存
    output_path = Path(args.output)
    output_path.write_bytes(decoded_content)
    
    print(f"[OK] 分析結果を {output_path} に保存しました")
    print(f"ファイルサイズ: {len(decoded_content)} bytes")


if __name__ == "__main__":
    main()

