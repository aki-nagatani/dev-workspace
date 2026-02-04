#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fishtrack-db削除スクリプト
削除前にスナップショットを作成し、安全にRDSインスタンスを削除する
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
                    'Value': 'delete_fishtrack_db.py'
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


def wait_for_snapshot(snapshot_identifier: str, region: str = 'ap-northeast-1', timeout: int = 600):
    """スナップショットの完了を待機"""
    import time
    
    rds = boto3.client('rds', region_name=region)
    
    print("  スナップショットの完了を待機中...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = rds.describe_db_snapshots(DBSnapshotIdentifier=snapshot_identifier)
            snapshots = response.get('DBSnapshots', [])
            
            if snapshots:
                snapshot = snapshots[0]
                status = snapshot.get('Status', 'unknown')
                
                if status == 'available':
                    print(f"  スナップショット完了: {status}")
                    return True
                elif status == 'error':
                    print(f"  Error: スナップショット作成エラー: {status}")
                    return False
                else:
                    print(f"  ステータス: {status}... 待機中...")
            
            time.sleep(10)
            
        except ClientError as e:
            print(f"  Error: スナップショット状態の確認に失敗しました: {e}")
            return False
    
    print(f"  Warning: タイムアウト（{timeout}秒）")
    return False


def delete_db_instance(db_identifier: str, snapshot_identifier: str = None, region: str = 'ap-northeast-1'):
    """RDSインスタンスを削除"""
    rds = boto3.client('rds', region_name=region)
    
    print(f"  RDSインスタンス削除中: {db_identifier}")
    
    delete_params = {
        'DBInstanceIdentifier': db_identifier,
        'SkipFinalSnapshot': snapshot_identifier is None
    }
    
    if snapshot_identifier:
        delete_params['FinalDBSnapshotIdentifier'] = snapshot_identifier
        print(f"  最終スナップショット: {snapshot_identifier}")
    else:
        print("  警告: 最終スナップショットなしで削除します")
    
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
    db_identifier = 'fishtrack-db'
    region = 'ap-northeast-1'
    
    print("=" * 80)
    print(f"fishtrack-db削除スクリプト")
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
    
    # 確認プロンプト
    print("【2. 削除確認】")
    print("-" * 80)
    print("  警告: この操作は元に戻せません！")
    print(f"  削除対象: {db_identifier}")
    print(f"  月額コスト削減: 約$15-20")
    print()
    print("  削除前に最終スナップショットを作成しますか？ (推奨)")
    print("  [y/n]: ", end='', flush=True)
    
    create_snapshot = input().strip().lower() == 'y'
    
    if not create_snapshot:
        print("  警告: スナップショットなしで削除します。本当に続行しますか？ [y/n]: ", end='', flush=True)
        confirm = input().strip().lower()
        if confirm != 'y':
            print("  削除をキャンセルしました。")
            return
    
    print()
    
    # スナップショット作成
    snapshot_identifier = None
    if create_snapshot:
        print("【3. 最終スナップショット作成】")
        print("-" * 80)
        snapshot_identifier = create_final_snapshot(db_identifier, region)
        
        if snapshot_identifier:
            # スナップショットの完了を待機
            if wait_for_snapshot(snapshot_identifier, region):
                print("  スナップショット作成完了")
            else:
                print("  警告: スナップショットの作成が完了していませんが、削除を続行しますか？")
                print("  [y/n]: ", end='', flush=True)
                continue_delete = input().strip().lower() == 'y'
                if not continue_delete:
                    print("  削除をキャンセルしました。")
                    return
        else:
            print("  警告: スナップショット作成に失敗しました。削除を続行しますか？")
            print("  [y/n]: ", end='', flush=True)
            continue_delete = input().strip().lower() == 'y'
            if not continue_delete:
                print("  削除をキャンセルしました。")
                return
        
        print()
    
    # 最終確認
    print("【4. 最終確認】")
    print("-" * 80)
    print(f"  削除対象: {db_identifier}")
    if snapshot_identifier:
        print(f"  最終スナップショット: {snapshot_identifier}")
    else:
        print("  最終スナップショット: なし")
    print()
    print("  本当に削除しますか？ [yes/no]: ", end='', flush=True)
    final_confirm = input().strip().lower()
    
    if final_confirm != 'yes':
        print("  削除をキャンセルしました。")
        return
    
    print()
    
    # インスタンス削除
    print("【5. RDSインスタンス削除】")
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
            print(f"  - 最終スナップショット '{snapshot_identifier}' が作成されました")
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
