#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スナップショット完了待機スクリプト
"""

import boto3
import sys
import io
import argparse
import time

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def wait_for_snapshot(snapshot_identifier: str, region: str = 'ap-northeast-1', timeout: int = 600):
    """スナップショットの完了を待機"""
    rds = boto3.client('rds', region_name=region)
    
    print(f"  スナップショット識別子: {snapshot_identifier}")
    print("  スナップショットの完了を待機中...")
    print(f"  タイムアウト: {timeout}秒")
    print()
    
    start_time = time.time()
    last_progress = -1
    
    while time.time() - start_time < timeout:
        try:
            response = rds.describe_db_snapshots(DBSnapshotIdentifier=snapshot_identifier)
            snapshots = response.get('DBSnapshots', [])
            
            if snapshots:
                snapshot = snapshots[0]
                status = snapshot.get('Status', 'unknown')
                progress = snapshot.get('PercentProgress')
                
                if progress is not None and progress != last_progress:
                    print(f"  進捗: {progress}% - ステータス: {status}")
                    last_progress = progress
                
                if status == 'available':
                    print()
                    print(f"  ✓ スナップショット完了: {status}")
                    return True
                elif status == 'error':
                    print()
                    print(f"  ✗ スナップショット作成エラー: {status}")
                    return False
            
            time.sleep(10)
            
        except Exception as e:
            print(f"  Error: スナップショット状態の確認に失敗しました: {e}")
            return False
    
    print()
    print(f"  ⚠ タイムアウト（{timeout}秒）")
    return False


def main():
    parser = argparse.ArgumentParser(description='スナップショットの完了を待機する')
    parser.add_argument('snapshot_identifier', type=str, help='スナップショット識別子')
    parser.add_argument('--region', type=str, default='ap-northeast-1', help='AWSリージョン')
    parser.add_argument('--timeout', type=int, default=600, help='タイムアウト（秒）')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("スナップショット完了待機")
    print("=" * 80)
    print()
    
    success = wait_for_snapshot(args.snapshot_identifier, args.region, args.timeout)
    
    print()
    print("=" * 80)
    if success:
        print("スナップショットが利用可能になりました")
    else:
        print("スナップショットの完了待機が失敗しました")
    print("=" * 80)
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
