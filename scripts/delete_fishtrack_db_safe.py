#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fishtrack-db削除スクリプト（安全版）
スナップショットを指定して削除する
"""

import boto3
import sys
import io
import argparse
from botocore.exceptions import ClientError

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def get_rds_instance_info(db_identifier: str, region: str = 'ap-northeast-1'):
    """RDSインスタンスの情報を取得"""
    rds = boto3.client('rds', region_name=region)
    
    try:
        response = rds.describe_db_instances(DBInstanceIdentifier=db_identifier)
        if not response.get('DBInstances'):
            return None
        
        instance = response['DBInstances'][0]
        return {
            'identifier': instance.get('DBInstanceIdentifier'),
            'status': instance.get('DBInstanceStatus'),
            'class': instance.get('DBInstanceClass'),
            'engine': instance.get('Engine'),
            'endpoint': instance.get('Endpoint', {}).get('Address'),
            'port': instance.get('Endpoint', {}).get('Port'),
            'created_time': instance.get('InstanceCreateTime'),
            'allocated_storage': instance.get('AllocatedStorage'),
            'storage_type': instance.get('StorageType'),
            'arn': instance.get('DBInstanceArn')
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'DBInstanceNotFound':
            return None
        raise


def delete_db_instance(db_identifier: str, snapshot_identifier: str = None, region: str = 'ap-northeast-1'):
    """RDSインスタンスを削除"""
    rds = boto3.client('rds', region_name=region)
    
    print(f"  RDSインスタンス削除中: {db_identifier}")
    
    # 既存のスナップショットが指定されている場合は、削除時に新しいスナップショットは作成しない
    # （既にスナップショットが作成済みのため）
    delete_params = {
        'DBInstanceIdentifier': db_identifier,
        'SkipFinalSnapshot': True  # 既存スナップショットがあるため、新しいスナップショットは作成しない
    }
    
    if snapshot_identifier:
        print(f"  既存のスナップショット: {snapshot_identifier}")
        print("  （削除時に新しいスナップショットは作成しません）")
    else:
        print("  警告: スナップショットなしで削除します")
    
    try:
        response = rds.delete_db_instance(**delete_params)
        instance = response.get('DBInstance', {})
        print(f"  削除開始: ステータス = {instance.get('DBInstanceStatus')}")
        print(f"  削除ARN: {instance.get('DBInstanceArn')}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'DBInstanceNotFound':
            print(f"  インスタンス '{db_identifier}' は既に存在しません")
            return True
        else:
            print(f"  Error: インスタンス削除に失敗しました: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='fishtrack-dbを安全に削除する')
    parser.add_argument('--snapshot', type=str, help='最終スナップショットの識別子（オプション）')
    parser.add_argument('--no-snapshot', action='store_true', help='スナップショットなしで削除（非推奨）')
    parser.add_argument('--db-identifier', type=str, default='fishtrack-db', help='RDSインスタンス識別子')
    parser.add_argument('--region', type=str, default='ap-northeast-1', help='AWSリージョン')
    
    args = parser.parse_args()
    
    db_identifier = args.db_identifier
    region = args.region
    
    print("=" * 80)
    print(f"fishtrack-db削除スクリプト（安全版）")
    print("=" * 80)
    print()
    
    # インスタンス情報の確認
    print("【1. インスタンス情報の確認】")
    print("-" * 80)
    instance_info = get_rds_instance_info(db_identifier, region)
    
    if not instance_info:
        print(f"  RDSインスタンス '{db_identifier}' が見つかりませんでした。")
        print("  既に削除されている可能性があります。")
        return
    
    print(f"  識別子: {instance_info['identifier']}")
    print(f"  ステータス: {instance_info['status']}")
    print(f"  インスタンスクラス: {instance_info['class']}")
    print(f"  エンジン: {instance_info['engine']}")
    print(f"  エンドポイント: {instance_info['endpoint']}:{instance_info['port']}")
    print(f"  作成日時: {instance_info['created_time']}")
    print(f"  ストレージ: {instance_info['allocated_storage']} GB ({instance_info['storage_type']})")
    print()
    
    # スナップショットの確認
    snapshot_identifier = args.snapshot
    
    if args.no_snapshot:
        print("【2. 削除確認】")
        print("-" * 80)
        print("  警告: スナップショットなしで削除します！")
        print(f"  削除対象: {db_identifier}")
        snapshot_identifier = None
    elif snapshot_identifier:
        print("【2. スナップショット確認】")
        print("-" * 80)
        print(f"  使用するスナップショット: {snapshot_identifier}")
    else:
        print("【2. エラー】")
        print("-" * 80)
        print("  スナップショットが指定されていません。")
        print("  以下のいずれかを実行してください:")
        print("  1. スナップショットを作成: python scripts/create_fishtrack_db_snapshot.py")
        print("  2. 既存のスナップショットを指定: --snapshot <snapshot-id>")
        print("  3. スナップショットなしで削除（非推奨）: --no-snapshot")
        return
    
    print()
    
    # インスタンス削除
    print("【3. RDSインスタンス削除】")
    print("-" * 80)
    success = delete_db_instance(db_identifier, snapshot_identifier, region)
    
    if success:
        print()
        print("=" * 80)
        print("削除処理が開始されました")
        print("=" * 80)
        print()
        print("  注意事項:")
        print("  - インスタンスの完全な削除には数分かかる場合があります")
        print("  - AWSコンソールで削除状況を確認できます")
        if snapshot_identifier:
            print(f"  - 最終スナップショット '{snapshot_identifier}' が使用されました")
            print("  - スナップショットから必要に応じて復元できます")
        print()
    else:
        print()
        print("=" * 80)
        print("削除処理に失敗しました")
        print("=" * 80)
        print()
        print("  エラーの詳細を確認してください。")
        print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作がキャンセルされました。")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
