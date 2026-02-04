#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RDSインスタンスの使用状況確認スクリプト
特定のRDSインスタンスが実際に使用されているかを確認する
"""

import boto3
import sys
import io
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def get_rds_instance_info(db_identifier: str, region: str = 'ap-northeast-1'):
    """RDSインスタンスの基本情報を取得"""
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


def get_cloudwatch_metrics(db_identifier: str, region: str = 'ap-northeast-1', days: int = 30):
    """CloudWatchメトリクスを取得"""
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    metrics_to_check = {
        'DatabaseConnections': {
            'Namespace': 'AWS/RDS',
            'MetricName': 'DatabaseConnections',
            'Statistic': 'Average',
            'Unit': 'Count'
        },
        'CPUUtilization': {
            'Namespace': 'AWS/RDS',
            'MetricName': 'CPUUtilization',
            'Statistic': 'Average',
            'Unit': 'Percent'
        },
        'FreeStorageSpace': {
            'Namespace': 'AWS/RDS',
            'MetricName': 'FreeStorageSpace',
            'Statistic': 'Average',
            'Unit': 'Bytes'
        },
        'ReadIOPS': {
            'Namespace': 'AWS/RDS',
            'MetricName': 'ReadIOPS',
            'Statistic': 'Sum',
            'Unit': 'Count/Second'
        },
        'WriteIOPS': {
            'Namespace': 'AWS/RDS',
            'MetricName': 'WriteIOPS',
            'Statistic': 'Sum',
            'Unit': 'Count/Second'
        }
    }
    
    results = {}
    
    for metric_name, metric_config in metrics_to_check.items():
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace=metric_config['Namespace'],
                MetricName=metric_config['MetricName'],
                Dimensions=[
                    {'Name': 'DBInstanceIdentifier', 'Value': db_identifier}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1時間ごと
                Statistics=[metric_config['Statistic']],
                Unit=metric_config['Unit']
            )
            
            datapoints = response.get('Datapoints', [])
            if datapoints:
                if metric_config['Statistic'] == 'Average':
                    values = [dp['Average'] for dp in datapoints]
                elif metric_config['Statistic'] == 'Sum':
                    values = [dp['Sum'] for dp in datapoints]
                else:
                    values = []
                
                if values:
                    results[metric_name] = {
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'latest': values[-1] if values else None,
                        'data_points': len(datapoints)
                    }
                else:
                    results[metric_name] = None
            else:
                results[metric_name] = None
                
        except Exception as e:
            print(f"  Warning: {metric_name}の取得に失敗: {e}", file=sys.stderr)
            results[metric_name] = None
    
    return results


def analyze_usage(metrics):
    """使用状況を分析"""
    analysis = {
        'is_used': False,
        'usage_level': 'unknown',
        'details': []
    }
    
    # データベース接続数の確認
    if metrics.get('DatabaseConnections'):
        conn_metrics = metrics['DatabaseConnections']
        max_connections = conn_metrics['max']
        avg_connections = conn_metrics['avg']
        
        if max_connections > 0:
            analysis['is_used'] = True
            if avg_connections < 1:
                analysis['usage_level'] = 'very_low'
                analysis['details'].append(f"平均接続数: {avg_connections:.2f}（非常に低い）")
            elif avg_connections < 5:
                analysis['usage_level'] = 'low'
                analysis['details'].append(f"平均接続数: {avg_connections:.2f}（低い）")
            else:
                analysis['usage_level'] = 'normal'
                analysis['details'].append(f"平均接続数: {avg_connections:.2f}（通常）")
        else:
            analysis['details'].append("接続数: 0（未使用の可能性）")
    else:
        analysis['details'].append("接続数メトリクスが取得できませんでした")
    
    # CPU使用率の確認
    if metrics.get('CPUUtilization'):
        cpu_metrics = metrics['CPUUtilization']
        avg_cpu = cpu_metrics['avg']
        max_cpu = cpu_metrics['max']
        
        if avg_cpu > 0:
            analysis['is_used'] = True
            if avg_cpu < 1:
                analysis['usage_level'] = 'very_low'
                analysis['details'].append(f"平均CPU使用率: {avg_cpu:.2f}%（非常に低い）")
            elif avg_cpu < 5:
                analysis['usage_level'] = 'low'
                analysis['details'].append(f"平均CPU使用率: {avg_cpu:.2f}%（低い）")
            else:
                analysis['usage_level'] = 'normal'
                analysis['details'].append(f"平均CPU使用率: {avg_cpu:.2f}%（通常）")
        else:
            analysis['details'].append("CPU使用率: 0%（未使用の可能性）")
    else:
        analysis['details'].append("CPU使用率メトリクスが取得できませんでした")
    
    # IOPSの確認
    read_iops = metrics.get('ReadIOPS')
    write_iops = metrics.get('WriteIOPS')
    
    if read_iops or write_iops:
        avg_read = read_iops['avg'] if read_iops else 0
        avg_write = write_iops['avg'] if write_iops else 0
        
        if avg_read > 0 or avg_write > 0:
            analysis['is_used'] = True
            if read_iops:
                analysis['details'].append(f"平均Read IOPS: {read_iops['avg']:.2f}")
            if write_iops:
                analysis['details'].append(f"平均Write IOPS: {write_iops['avg']:.2f}")
        else:
            analysis['details'].append("IOPS: 0（読み書きなし）")
    else:
        analysis['details'].append("IOPSメトリクスが取得できませんでした")
    
    return analysis


def check_rds_usage(db_identifier: str, region: str = 'ap-northeast-1'):
    """RDSインスタンスの使用状況を確認"""
    print("=" * 80)
    print(f"RDSインスタンス使用状況確認: {db_identifier}")
    print("=" * 80)
    print()
    
    # 基本情報の取得
    print("【基本情報】")
    print("-" * 80)
    instance_info = get_rds_instance_info(db_identifier, region)
    
    if not instance_info:
        print(f"  Error: RDSインスタンス '{db_identifier}' が見つかりませんでした。")
        return
    
    print(f"  識別子: {instance_info['identifier']}")
    print(f"  ステータス: {instance_info['status']}")
    print(f"  インスタンスクラス: {instance_info['class']}")
    print(f"  エンジン: {instance_info['engine']}")
    print(f"  エンドポイント: {instance_info['endpoint']}:{instance_info['port']}")
    print(f"  作成日時: {instance_info['created_time']}")
    print(f"  ストレージ: {instance_info['allocated_storage']} GB ({instance_info['storage_type']})")
    print()
    
    # CloudWatchメトリクスの取得
    print("【過去30日間の使用状況（CloudWatchメトリクス）】")
    print("-" * 80)
    metrics = get_cloudwatch_metrics(db_identifier, region, days=30)
    
    if metrics.get('DatabaseConnections'):
        conn = metrics['DatabaseConnections']
        print(f"  データベース接続数:")
        print(f"    最小: {conn['min']:.2f}")
        print(f"    最大: {conn['max']:.2f}")
        print(f"    平均: {conn['avg']:.2f}")
        print(f"    最新: {conn['latest']:.2f}")
        print(f"    データポイント数: {conn['data_points']}")
    else:
        print("  データベース接続数: メトリクスが取得できませんでした")
    print()
    
    if metrics.get('CPUUtilization'):
        cpu = metrics['CPUUtilization']
        print(f"  CPU使用率:")
        print(f"    最小: {cpu['min']:.2f}%")
        print(f"    最大: {cpu['max']:.2f}%")
        print(f"    平均: {cpu['avg']:.2f}%")
        print(f"    最新: {cpu['latest']:.2f}%")
    else:
        print("  CPU使用率: メトリクスが取得できませんでした")
    print()
    
    if metrics.get('FreeStorageSpace'):
        storage = metrics['FreeStorageSpace']
        allocated_gb = instance_info['allocated_storage']
        free_gb = storage['avg'] / (1024**3)  # Bytes to GB
        used_gb = allocated_gb - free_gb
        usage_percent = (used_gb / allocated_gb * 100) if allocated_gb > 0 else 0
        
        print(f"  ストレージ使用状況:")
        print(f"    割り当て済み: {allocated_gb} GB")
        print(f"    使用中: {used_gb:.2f} GB ({usage_percent:.1f}%)")
        print(f"    空き: {free_gb:.2f} GB")
    else:
        print("  ストレージ使用状況: メトリクスが取得できませんでした")
    print()
    
    if metrics.get('ReadIOPS'):
        read_iops = metrics['ReadIOPS']
        print(f"  Read IOPS:")
        print(f"    平均: {read_iops['avg']:.2f}")
        print(f"    最大: {read_iops['max']:.2f}")
    else:
        print("  Read IOPS: メトリクスが取得できませんでした")
    print()
    
    if metrics.get('WriteIOPS'):
        write_iops = metrics['WriteIOPS']
        print(f"  Write IOPS:")
        print(f"    平均: {write_iops['avg']:.2f}")
        print(f"    最大: {write_iops['max']:.2f}")
    else:
        print("  Write IOPS: メトリクスが取得できませんでした")
    print()
    
    # 使用状況の分析
    print("【使用状況の分析】")
    print("-" * 80)
    analysis = analyze_usage(metrics)
    
    if analysis['is_used']:
        print("  結論: インスタンスは使用されています")
        if analysis['usage_level'] == 'very_low':
            print("  使用レベル: 非常に低い（削除を検討可能）")
        elif analysis['usage_level'] == 'low':
            print("  使用レベル: 低い（使用状況を継続監視）")
        else:
            print("  使用レベル: 通常")
    else:
        print("  結論: インスタンスは使用されていない可能性が高いです")
        print("  推奨: 削除を検討してください")
    
    print()
    print("  詳細:")
    for detail in analysis['details']:
        print(f"    - {detail}")
    print()
    
    # 推奨事項
    print("【推奨事項】")
    print("-" * 80)
    if not analysis['is_used']:
        print("  1. インスタンスの削除を検討してください")
        print("     - 月額約$15-20のコスト削減が可能です")
        print("     - 削除前にスナップショットを作成することを推奨します")
    elif analysis['usage_level'] == 'very_low':
        print("  1. 使用状況が非常に低いため、削除を検討してください")
        print("  2. または、より小さいインスタンスタイプへのダウンサイズを検討してください")
    elif analysis['usage_level'] == 'low':
        print("  1. 使用状況を継続的に監視してください")
        print("  2. 必要に応じて、より小さいインスタンスタイプへのダウンサイズを検討してください")
    else:
        print("  1. インスタンスは正常に使用されています")
        print("  2. 現在の設定を維持することを推奨します")
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    db_identifier = 'fishtrack-db'
    region = 'ap-northeast-1'
    
    try:
        check_rds_usage(db_identifier, region)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
