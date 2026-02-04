#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RDSインスタンス削除状態確認スクリプト
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


def check_db_status(db_identifier: str, region: str = 'ap-northeast-1'):
    """RDSインスタンスの状態を確認"""
    rds = boto3.client('rds', region_name=region)
    
    try:
        response = rds.describe_db_instances(DBInstanceIdentifier=db_identifier)
        if not response.get('DBInstances'):
            return None
        
        instance = response['DBInstances'][0]
        return {
            'identifier': instance.get('DBInstanceIdentifier'),
            'status': instance.get('DBInstanceStatus'),
            'arn': instance.get('DBInstanceArn')
        }
    except ClientError as e:
        if e.response['Error']['Code'] == 'DBInstanceNotFound':
            return None
        raise


def main():
    parser = argparse.ArgumentParser(description='RDSインスタンスの削除状態を確認する')
    parser.add_argument('--db-identifier', type=str, default='fishtrack-db', help='RDSインスタンス識別子')
    parser.add_argument('--region', type=str, default='ap-northeast-1', help='AWSリージョン')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("RDSインスタンス削除状態確認")
    print("=" * 80)
    print()
    
    instance_info = check_db_status(args.db_identifier, args.region)
    
    if instance_info:
        print("【インスタンス情報】")
        print("-" * 80)
        print(f"  識別子: {instance_info['identifier']}")
        print(f"  ステータス: {instance_info['status']}")
        print(f"  ARN: {instance_info['arn']}")
        print()
        
        if instance_info['status'] == 'deleting':
            print("  ⏳ インスタンスは削除中です")
        elif instance_info['status'] == 'available':
            print("  ✓ インスタンスは利用可能です（削除されていません）")
        else:
            print(f"  ? ステータス: {instance_info['status']}")
    else:
        print("【削除完了】")
        print("-" * 80)
        print(f"  ✓ インスタンス '{args.db_identifier}' は削除されました")
        print("  （または存在しません）")
    
    print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
