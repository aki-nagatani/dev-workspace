#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スナップショット状態確認スクリプト
"""

import boto3
import sys
import io
import argparse

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def check_snapshot_status(snapshot_identifier: str, region: str = 'ap-northeast-1'):
    """スナップショットの状態を確認"""
    rds = boto3.client('rds', region_name=region)
    
    try:
        response = rds.describe_db_snapshots(DBSnapshotIdentifier=snapshot_identifier)
        snapshots = response.get('DBSnapshots', [])
        
        if not snapshots:
            print(f"  スナップショット '{snapshot_identifier}' が見つかりませんでした。")
            return None
        
        snapshot = snapshots[0]
        return {
            'identifier': snapshot.get('DBSnapshotIdentifier'),
            'status': snapshot.get('Status'),
            'progress': snapshot.get('PercentProgress'),
            'created_time': snapshot.get('SnapshotCreateTime'),
            'arn': snapshot.get('DBSnapshotArn')
        }
        
    except Exception as e:
        print(f"  Error: スナップショット状態の確認に失敗しました: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='スナップショットの状態を確認する')
    parser.add_argument('snapshot_identifier', type=str, help='スナップショット識別子')
    parser.add_argument('--region', type=str, default='ap-northeast-1', help='AWSリージョン')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("スナップショット状態確認")
    print("=" * 80)
    print()
    
    snapshot_info = check_snapshot_status(args.snapshot_identifier, args.region)
    
    if snapshot_info:
        print("【スナップショット情報】")
        print("-" * 80)
        print(f"  識別子: {snapshot_info['identifier']}")
        print(f"  ステータス: {snapshot_info['status']}")
        if snapshot_info['progress'] is not None:
            print(f"  進捗: {snapshot_info['progress']}%")
        print(f"  作成日時: {snapshot_info['created_time']}")
        print(f"  ARN: {snapshot_info['arn']}")
        print()
        
        if snapshot_info['status'] == 'available':
            print("  ✓ スナップショットは利用可能です")
        elif snapshot_info['status'] == 'creating':
            print("  ⏳ スナップショット作成中です")
        elif snapshot_info['status'] == 'error':
            print("  ✗ スナップショット作成エラー")
        else:
            print(f"  ? ステータス: {snapshot_info['status']}")
    else:
        print("  スナップショット情報を取得できませんでした。")
    
    print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
