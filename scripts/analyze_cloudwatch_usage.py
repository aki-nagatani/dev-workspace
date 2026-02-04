#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CloudWatchメトリクスによるリソース使用率分析スクリプト
RDSとEC2インスタンスの使用率を分析し、Right Sizingの提案を行う
"""

import boto3
import sys
import io
from datetime import datetime, timedelta
from collections import defaultdict

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def get_rds_metrics(db_identifier: str, region: str = 'ap-northeast-1', days: int = 30):
    """RDSインスタンスのCloudWatchメトリクスを取得"""
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    metrics = {
        'CPUUtilization': {
            'Namespace': 'AWS/RDS',
            'MetricName': 'CPUUtilization',
            'Statistic': 'Average',
            'Unit': 'Percent'
        },
        'DatabaseConnections': {
            'Namespace': 'AWS/RDS',
            'MetricName': 'DatabaseConnections',
            'Statistic': 'Average',
            'Unit': 'Count'
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
            'Statistic': 'Average',
            'Unit': 'Count/Second'
        },
        'WriteIOPS': {
            'Namespace': 'AWS/RDS',
            'MetricName': 'WriteIOPS',
            'Statistic': 'Average',
            'Unit': 'Count/Second'
        }
    }
    
    results = {}
    
    for metric_name, metric_config in metrics.items():
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
                values = [dp[metric_config['Statistic']] for dp in datapoints]
                results[metric_name] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'latest': values[-1] if values else None,
                    'data_points': len(datapoints)
                }
            else:
                results[metric_name] = None
                
        except Exception as e:
            print(f"  Warning: {metric_name}の取得に失敗: {e}", file=sys.stderr)
            results[metric_name] = None
    
    return results


def get_ec2_metrics(instance_id: str, region: str = 'ap-northeast-1', days: int = 30):
    """EC2インスタンスのCloudWatchメトリクスを取得"""
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    metrics = {
        'CPUUtilization': {
            'Namespace': 'AWS/EC2',
            'MetricName': 'CPUUtilization',
            'Statistic': 'Average',
            'Unit': 'Percent'
        },
        'NetworkIn': {
            'Namespace': 'AWS/EC2',
            'MetricName': 'NetworkIn',
            'Statistic': 'Average',
            'Unit': 'Bytes'
        },
        'NetworkOut': {
            'Namespace': 'AWS/EC2',
            'MetricName': 'NetworkOut',
            'Statistic': 'Average',
            'Unit': 'Bytes'
        }
    }
    
    results = {}
    
    for metric_name, metric_config in metrics.items():
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace=metric_config['Namespace'],
                MetricName=metric_config['MetricName'],
                Dimensions=[
                    {'Name': 'InstanceId', 'Value': instance_id}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1時間ごと
                Statistics=[metric_config['Statistic']],
                Unit=metric_config['Unit']
            )
            
            datapoints = response.get('Datapoints', [])
            if datapoints:
                values = [dp[metric_config['Statistic']] for dp in datapoints]
                results[metric_name] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'latest': values[-1] if values else None,
                    'data_points': len(datapoints)
                }
            else:
                results[metric_name] = None
                
        except Exception as e:
            print(f"  Warning: {metric_name}の取得に失敗: {e}", file=sys.stderr)
            results[metric_name] = None
    
    return results


def analyze_rds_usage(db_identifier: str, instance_class: str, metrics: dict):
    """RDSインスタンスの使用率を分析"""
    print(f"  【{db_identifier} ({instance_class})】")
    print(f"    期間: 直近30日間")
    print()
    
    if not metrics or not any(metrics.values()):
        print("    ⚠️ メトリクスデータが取得できませんでした")
        print()
        return
    
    # CPU使用率
    if metrics.get('CPUUtilization'):
        cpu = metrics['CPUUtilization']
        print(f"    CPU使用率:")
        print(f"      - 平均: {cpu['avg']:.2f}%")
        print(f"      - 最大: {cpu['max']:.2f}%")
        print(f"      - 最小: {cpu['min']:.2f}%")
        print(f"      - 最新: {cpu['latest']:.2f}%")
        
        if cpu['avg'] < 10:
            print(f"      → ⚠️ 平均CPU使用率が10%未満です。ダウンサイズを検討してください")
        elif cpu['avg'] < 30:
            print(f"      → 💡 平均CPU使用率が30%未満です。Right Sizingを検討してください")
        elif cpu['max'] > 80:
            print(f"      → ⚠️ 最大CPU使用率が80%を超えています。パフォーマンスに注意してください")
        print()
    
    # データベース接続数
    if metrics.get('DatabaseConnections'):
        conn = metrics['DatabaseConnections']
        print(f"    データベース接続数:")
        print(f"      - 平均: {conn['avg']:.2f}")
        print(f"      - 最大: {conn['max']:.2f}")
        print(f"      - 最小: {conn['min']:.2f}")
        print(f"      - 最新: {conn['latest']:.2f}")
        print()
    
    # ストレージ使用率
    if metrics.get('FreeStorageSpace'):
        free_space = metrics['FreeStorageSpace']
        # ストレージサイズを取得する必要があるが、ここでは簡易的に表示
        print(f"    空きストレージ:")
        print(f"      - 平均: {free_space['avg'] / (1024**3):.2f} GB")
        print(f"      - 最小: {free_space['min'] / (1024**3):.2f} GB")
        print(f"      - 最新: {free_space['latest'] / (1024**3):.2f} GB")
        print()
    
    # IOPS
    if metrics.get('ReadIOPS') or metrics.get('WriteIOPS'):
        print(f"    IOPS:")
        if metrics.get('ReadIOPS'):
            read_iops = metrics['ReadIOPS']
            print(f"      - 読み取り平均: {read_iops['avg']:.2f} IOPS")
        if metrics.get('WriteIOPS'):
            write_iops = metrics['WriteIOPS']
            print(f"      - 書き込み平均: {write_iops['avg']:.2f} IOPS")
        print()


def analyze_ec2_usage(instance_id: str, instance_name: str, instance_type: str, metrics: dict):
    """EC2インスタンスの使用率を分析"""
    print(f"  【{instance_name} ({instance_id})】")
    print(f"    インスタンスタイプ: {instance_type}")
    print(f"    期間: 直近30日間")
    print()
    
    if not metrics or not any(metrics.values()):
        print("    ⚠️ メトリクスデータが取得できませんでした")
        print()
        return
    
    # CPU使用率
    if metrics.get('CPUUtilization'):
        cpu = metrics['CPUUtilization']
        print(f"    CPU使用率:")
        print(f"      - 平均: {cpu['avg']:.2f}%")
        print(f"      - 最大: {cpu['max']:.2f}%")
        print(f"      - 最小: {cpu['min']:.2f}%")
        print(f"      - 最新: {cpu['latest']:.2f}%")
        
        if cpu['avg'] < 10:
            print(f"      → ⚠️ 平均CPU使用率が10%未満です。ダウンサイズを検討してください")
        elif cpu['avg'] < 30:
            print(f"      → 💡 平均CPU使用率が30%未満です。Right Sizingを検討してください")
        elif cpu['max'] > 80:
            print(f"      → ⚠️ 最大CPU使用率が80%を超えています。パフォーマンスに注意してください")
        print()
    
    # ネットワーク使用量
    if metrics.get('NetworkIn') or metrics.get('NetworkOut'):
        print(f"    ネットワーク使用量:")
        if metrics.get('NetworkIn'):
            net_in = metrics['NetworkIn']
            print(f"      - 受信平均: {net_in['avg'] / (1024**2):.2f} MB/時")
        if metrics.get('NetworkOut'):
            net_out = metrics['NetworkOut']
            print(f"      - 送信平均: {net_out['avg'] / (1024**2):.2f} MB/時")
        print()


def main():
    print("=" * 80)
    print("CloudWatchメトリクスによるリソース使用率分析レポート")
    print("=" * 80)
    print()
    
    region = 'ap-northeast-1'
    
    # RDSインスタンスの分析
    print("【RDSインスタンス使用率分析】")
    print("-" * 80)
    
    rds = boto3.client('rds', region_name=region)
    try:
        response = rds.describe_db_instances()
        instances = response.get('DBInstances', [])
        
        if not instances:
            print("  RDSインスタンスが見つかりませんでした。")
            print()
        else:
            for instance in instances:
                db_identifier = instance.get('DBInstanceIdentifier')
                instance_class = instance.get('DBInstanceClass')
                
                print(f"\n  RDSインスタンス: {db_identifier}")
                metrics = get_rds_metrics(db_identifier, region, days=30)
                analyze_rds_usage(db_identifier, instance_class, metrics)
                
    except Exception as e:
        print(f"  Error: RDSインスタンスの取得に失敗しました: {e}")
        print()
    
    # EC2インスタンスの分析
    print("【EC2インスタンス使用率分析】")
    print("-" * 80)
    
    ec2 = boto3.client('ec2', region_name=region)
    try:
        response = ec2.describe_instances()
        
        instances_info = []
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId')
                state = instance.get('State', {}).get('Name', 'N/A')
                
                if state == 'running':
                    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    name = tags.get('Name', 'N/A')
                    instance_type = instance.get('InstanceType', 'N/A')
                    
                    instances_info.append({
                        'id': instance_id,
                        'name': name,
                        'type': instance_type
                    })
        
        if not instances_info:
            print("  実行中のEC2インスタンスが見つかりませんでした。")
            print()
        else:
            for inst_info in instances_info:
                print(f"\n  EC2インスタンス: {inst_info['name']}")
                metrics = get_ec2_metrics(inst_info['id'], region, days=30)
                analyze_ec2_usage(inst_info['id'], inst_info['name'], inst_info['type'], metrics)
                
    except Exception as e:
        print(f"  Error: EC2インスタンスの取得に失敗しました: {e}")
        print()
    
    # 総合的な推奨事項
    print("=" * 80)
    print("【総合的な推奨事項】")
    print("=" * 80)
    print()
    print("1. **低使用率リソースの確認**")
    print("   - CPU使用率が平均10%未満のリソースは、ダウンサイズを検討してください")
    print("   - ただし、本番環境のため、可用性を優先し、慎重に判断してください")
    print()
    print("2. **高使用率リソースの監視**")
    print("   - CPU使用率が最大80%を超えるリソースは、パフォーマンスに注意してください")
    print("   - 必要に応じて、スケールアップを検討してください")
    print()
    print("3. **継続的な監視**")
    print("   - CloudWatchメトリクスを定期的に確認し、使用率の傾向を把握してください")
    print("   - 使用率の変動が大きい場合は、ピーク時の使用率を重視してください")
    print()
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
