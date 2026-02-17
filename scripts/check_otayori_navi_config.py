#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
おたよりナビ config.yaml確認スクリプト
EC2上のDockerコンテナ内で実行することを想定
"""

import os
import sys
from pathlib import Path

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    print("=" * 80)
    print("おたよりナビ config.yaml確認")
    print("=" * 80)
    print()
    
    # config.yamlのパスを確認
    config_paths = [
        "/app/config.yaml",
        "/home/ec2-user/otayori-navi/config.yaml",
        "config.yaml",
    ]
    
    config_path = None
    for path in config_paths:
        if Path(path).exists():
            config_path = Path(path)
            break
    
    if not config_path:
        print("❌ config.yamlが見つかりません")
        print()
        print("確認したパス:")
        for path in config_paths:
            print(f"  - {path}")
        print()
        print("【推奨アクション】")
        print("config.example.yamlからconfig.yamlを作成してください:")
        print("  cp config.example.yaml config.yaml")
        sys.exit(1)
    
    print(f"✅ config.yamlが見つかりました: {config_path}")
    print()
    
    # config.yamlの内容を読み込んで確認
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        print("【1. 設定ファイルの内容確認】")
        print("-" * 80)
        
        # Web設定
        web_section = config_data.get("web", {})
        print("Web設定:")
        if "secret_key" in web_section:
            print(f"  secret_key: {'*' * 20} (直接指定)")
        elif "secret_key_env" in web_section:
            print(f"  secret_key_env: {web_section['secret_key_env']} ✅")
        else:
            print("  ⚠️  secret_keyまたはsecret_key_envが設定されていません")
        print(f"  session_cookie_name: {web_section.get('session_cookie_name', 'otayori')}")
        print(f"  max_upload_mb: {web_section.get('max_upload_mb', 50)}")
        print()
        
        # DB設定
        db_section = config_data.get("db", {})
        print("DB設定:")
        if "url" in db_section:
            masked_url = db_section["url"].split("@")[-1] if "@" in db_section["url"] else "***"
            print(f"  url: {masked_url} (直接指定)")
        elif "url_env" in db_section:
            print(f"  url_env: {db_section['url_env']} ✅")
        else:
            print("  ⚠️  urlまたはurl_envが設定されていません")
        print(f"  echo: {db_section.get('echo', False)}")
        print()
        
        # ストレージ設定
        storage_section = config_data.get("storage", {})
        if storage_section:
            print("ストレージ設定:")
            print(f"  type: {storage_section.get('type', 's3')}")
            if storage_section.get('type') == 's3':
                print(f"  s3_bucket: {storage_section.get('s3_bucket', 'N/A')}")
                if storage_section.get('s3_bucket') == 'otayori-navi-bucket':
                    print("    ✅ 正しいバケット名")
                else:
                    print("    ⚠️  バケット名が正しくない可能性があります")
            print(f"  pdf_base_path: {storage_section.get('pdf_base_path', 'otayori/pdf')}")
            print(f"  md_base_path: {storage_section.get('md_base_path', 'otayori/md')}")
        print()
        
        # AWS設定
        aws_section = config_data.get("aws", {})
        print("AWS設定:")
        print(f"  region: {aws_section.get('region', 'N/A')}")
        if aws_section.get('region') == 'ap-northeast-1':
            print("    ✅ 正しいリージョン")
        else:
            print("    ⚠️  リージョンが正しくない可能性があります")
        print()
        
        # AI設定
        ai_section = config_data.get("ai", {})
        print("AI設定:")
        endpoint_url = ai_section.get("endpoint_url", "N/A")
        print(f"  endpoint_url: {endpoint_url}")
        if "example.com" in endpoint_url or endpoint_url == "N/A":
            print("    ❌ プレースホルダーのままです。実際のエンドポイントURLに変更してください")
        else:
            print("    ✅ 実際のエンドポイントURLが設定されています")
        
        if "api_key" in ai_section:
            print(f"  api_key: {'*' * 20} (直接指定)")
        elif "api_key_env" in ai_section:
            print(f"  api_key_env: {ai_section['api_key_env']} ✅")
        else:
            print("  ⚠️  api_keyまたはapi_key_envが設定されていません")
        
        print(f"  model: {ai_section.get('model', 'N/A')}")
        print(f"  timeout_seconds: {ai_section.get('timeout_seconds', 'N/A')}")
        print()
        
        # サマリー
        print("=" * 80)
        print("【確認結果サマリー】")
        print("=" * 80)
        
        issues = []
        
        if not web_section.get("secret_key") and not web_section.get("secret_key_env"):
            issues.append("Web設定: secret_keyまたはsecret_key_envが設定されていません")
        
        if not db_section.get("url") and not db_section.get("url_env"):
            issues.append("DB設定: urlまたはurl_envが設定されていません")
        
        s3_bucket = storage_section.get("s3_bucket") if storage_section else None
        if s3_bucket != "otayori-navi-bucket":
            issues.append(f"ストレージ設定: S3バケット名が正しくありません（現在: {s3_bucket}）")
        
        if aws_section.get("region") != "ap-northeast-1":
            issues.append(f"AWS設定: リージョンが正しくありません（現在: {aws_section.get('region')}）")
        
        if "example.com" in endpoint_url or endpoint_url == "N/A":
            issues.append("AI設定: endpoint_urlがプレースホルダーのままです")
        
        if not ai_section.get("api_key") and not ai_section.get("api_key_env"):
            issues.append("AI設定: api_keyまたはapi_key_envが設定されていません")
        
        if issues:
            print("❌ 以下の問題が見つかりました:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ すべての設定が正しく設定されています")
        
        print()
        
        # 推奨アクション
        if issues:
            print("【推奨アクション】")
            print("-" * 80)
            if "example.com" in endpoint_url or endpoint_url == "N/A":
                print("1. AI設定のendpoint_urlを実際のエンドポイントURLに変更してください")
            print("2. 不足している設定を追加してください")
            print("3. config.yamlを保存後、アプリケーションを再起動してください")
            print()
        
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
