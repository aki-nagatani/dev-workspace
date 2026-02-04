#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fishtrack-dbスナップショット作成スクリプト
削除前にスナップショットを作成する
"""

import boto3
import sys
import io
from datetime import datetime
from botocore.exceptions import ClientError

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def create_final_snapshot(db_identifier: str, region: str = 'ap-northeast-1'):
    """最終スナップショットを作成"""
    rds = boto3.client('rds', region_name=region)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    snapshot_identifier = f"{db_identifier}-final-snapshot-{timestamp}"
    
    print(f"  スナップショット識別子: {snapshot_identifier}")
    print("  スナップショット作成中...")
    
    try:
        response = rds.create_db_snapshot(
            DBInstanceIdentifier=db_identifier,
            DBSnapshotIdentifier=snapshot_identifier,
            Tags=[
                {
                    'Key': 'Purpose',
                    'Value': 'Final snapshot before deletion'
                },
                {
                    'Key': 'CreatedBy',
                    'Value': 'create_fishtrack_db_snapshot.py'
                }
            ]
        )
        
        snapshot = response.get('DBSnapshot', {})
        print(f"  スナップショット作成開始: {snapshot.get('Status')}")
        print(f"  スナップショットARN: {snapshot.get('DBSnapshotArn')}")
        
        return snapshot_identifier
        
    except ClientError as e:
        print(f"  Error: スナップショット作成に失敗しました: {e}")
        return None


def main():
    db_identifier = 'fishtrack-db'
    region = 'ap-northeast-1'
    
    print("=" * 80)
    print(f"fishtrack-dbスナップショット作成スクリプト")
    print("=" * 80)
    print()
    
    print("【スナップショット作成】")
    print("-" * 80)
    snapshot_identifier = create_final_snapshot(db_identifier, region)
    
    if snapshot_identifier:
        print()
        print("=" * 80)
        print("スナップショット作成が開始されました")
        print("=" * 80)
        print()
        print(f"  スナップショット識別子: {snapshot_identifier}")
        print("  注意: スナップショットの完了には数分かかる場合があります")
        print("  AWSコンソールでスナップショットの状態を確認できます")
        print()
    else:
        print()
        print("=" * 80)
        print("スナップショット作成に失敗しました")
        print("=" * 80)
        print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
