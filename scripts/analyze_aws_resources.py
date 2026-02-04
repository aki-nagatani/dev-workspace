#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWSリソース詳細分析スクリプト
実際のリソース使用状況を確認し、コスト最適化の具体的な改善案を提案する
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


def analyze_rds_instances():
    """RDSインスタンスの詳細分析"""
    print("【RDSインスタンス分析】")
    print("-" * 80)
    
    rds = boto3.client('rds', region_name='ap-northeast-1')
    
    try:
        response = rds.describe_db_instances()
        instances = response.get('DBInstances', [])
        
        if not instances:
            print("  RDSインスタンスが見つかりませんでした。")
            print()
            return []
        
        rds_info = []
        for instance in instances:
            db_id = instance.get('DBInstanceIdentifier', 'N/A')
            status = instance.get('DBInstanceStatus', 'N/A')
            instance_class = instance.get('DBInstanceClass', 'N/A')
            engine = instance.get('Engine', 'N/A')
            engine_version = instance.get('EngineVersion', 'N/A')
            allocated_storage = instance.get('AllocatedStorage', 0)
            storage_type = instance.get('StorageType', 'N/A')
            multi_az = instance.get('MultiAZ', False)
            backup_retention = instance.get('BackupRetentionPeriod', 0)
            publicly_accessible = instance.get('PubliclyAccessible', False)
            
            # タグから環境情報を取得
            tags_response = rds.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])
            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
            environment = tags.get('Environment', tags.get('environment', 'N/A'))
            
            rds_info.append({
                'id': db_id,
                'status': status,
                'class': instance_class,
                'engine': engine,
                'version': engine_version,
                'storage': allocated_storage,
                'storage_type': storage_type,
                'multi_az': multi_az,
                'backup_retention': backup_retention,
                'publicly_accessible': publicly_accessible,
                'environment': environment
            })
            
            print(f"  DB識別子: {db_id}")
            print(f"    ステータス: {status}")
            print(f"    インスタンスクラス: {instance_class}")
            print(f"    エンジン: {engine} {engine_version}")
            print(f"    ストレージ: {allocated_storage} GB ({storage_type})")
            print(f"    Multi-AZ: {'有効' if multi_az else '無効'}")
            print(f"    バックアップ保持期間: {backup_retention} 日")
            print(f"    パブリックアクセス: {'有効' if publicly_accessible else '無効'}")
            print(f"    環境: {environment}")
            print()
        
        return rds_info
        
    except Exception as e:
        print(f"  Error: RDSインスタンスの取得に失敗しました: {e}")
        print()
        return []


def analyze_ec2_instances():
    """EC2インスタンスの詳細分析"""
    print("【EC2インスタンス分析】")
    print("-" * 80)
    
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    try:
        response = ec2.describe_instances()
        
        instances_info = []
        running_count = 0
        stopped_count = 0
        
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId', 'N/A')
                state = instance.get('State', {}).get('Name', 'N/A')
                instance_type = instance.get('InstanceType', 'N/A')
                launch_time = instance.get('LaunchTime', None)
                
                # タグから名前と環境情報を取得
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                name = tags.get('Name', 'N/A')
                environment = tags.get('Environment', tags.get('environment', 'N/A'))
                
                # セキュリティグループ
                security_groups = [sg['GroupName'] for sg in instance.get('SecurityGroups', [])]
                
                instances_info.append({
                    'id': instance_id,
                    'name': name,
                    'state': state,
                    'type': instance_type,
                    'launch_time': launch_time,
                    'environment': environment,
                    'security_groups': security_groups
                })
                
                if state == 'running':
                    running_count += 1
                elif state == 'stopped':
                    stopped_count += 1
                
                print(f"  インスタンスID: {instance_id}")
                print(f"    名前: {name}")
                print(f"    ステータス: {state}")
                print(f"    インスタンスタイプ: {instance_type}")
                print(f"    起動時刻: {launch_time}")
                print(f"    環境: {environment}")
                print(f"    セキュリティグループ: {', '.join(security_groups)}")
                print()
        
        print(f"  実行中: {running_count} 台")
        print(f"  停止中: {stopped_count} 台")
        print()
        
        return instances_info
        
    except Exception as e:
        print(f"  Error: EC2インスタンスの取得に失敗しました: {e}")
        print()
        return []


def analyze_nat_gateways():
    """NAT Gatewayの分析"""
    print("【NAT Gateway分析】")
    print("-" * 80)
    
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    try:
        response = ec2.describe_nat_gateways()
        nat_gateways = response.get('NatGateways', [])
        
        if not nat_gateways:
            print("  NAT Gatewayが見つかりませんでした。")
            print()
            return []
        
        nat_info = []
        for nat in nat_gateways:
            nat_id = nat.get('NatGatewayId', 'N/A')
            state = nat.get('State', 'N/A')
            subnet_id = nat.get('SubnetId', 'N/A')
            vpc_id = nat.get('VpcId', 'N/A')
            create_time = nat.get('CreateTime', None)
            
            # タグから名前を取得
            tags = {tag['Key']: tag['Value'] for tag in nat.get('Tags', [])}
            name = tags.get('Name', 'N/A')
            
            nat_info.append({
                'id': nat_id,
                'name': name,
                'state': state,
                'subnet_id': subnet_id,
                'vpc_id': vpc_id,
                'create_time': create_time
            })
            
            print(f"  NAT Gateway ID: {nat_id}")
            print(f"    名前: {name}")
            print(f"    ステータス: {state}")
            print(f"    VPC ID: {vpc_id}")
            print(f"    サブネット ID: {subnet_id}")
            print(f"    作成時刻: {create_time}")
            print()
        
        return nat_info
        
    except Exception as e:
        print(f"  Error: NAT Gatewayの取得に失敗しました: {e}")
        print()
        return []


def analyze_elastic_ips():
    """Elastic IPの分析"""
    print("【Elastic IP分析】")
    print("-" * 80)
    
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    try:
        response = ec2.describe_addresses()
        addresses = response.get('Addresses', [])
        
        if not addresses:
            print("  Elastic IPが見つかりませんでした。")
            print()
            return []
        
        allocated_count = 0
        associated_count = 0
        unassociated_count = 0
        
        for address in addresses:
            public_ip = address.get('PublicIp', 'N/A')
            allocation_id = address.get('AllocationId', 'N/A')
            association_id = address.get('AssociationId', None)
            instance_id = address.get('InstanceId', None)
            network_interface_id = address.get('NetworkInterfaceId', None)
            
            allocated_count += 1
            if association_id:
                associated_count += 1
            else:
                unassociated_count += 1
                print(f"  未関連付けのElastic IP: {public_ip} ({allocation_id})")
        
        print()
        print(f"  割り当て済み: {allocated_count} 個")
        print(f"  関連付け済み: {associated_count} 個")
        print(f"  未関連付け: {unassociated_count} 個")
        print()
        
        return {
            'total': allocated_count,
            'associated': associated_count,
            'unassociated': unassociated_count
        }
        
    except Exception as e:
        print(f"  Error: Elastic IPの取得に失敗しました: {e}")
        print()
        return {}


def generate_improvement_suggestions(rds_info, ec2_info, nat_info, eip_info):
    """改善案を生成"""
    print("=" * 80)
    print("【具体的な改善案（Reserved Instances除く）】")
    print("=" * 80)
    print()
    
    suggestions = []
    
    # RDSの改善案
    if rds_info:
        print("[1] RDSの最適化")
        print("-" * 80)
        
        for rds in rds_info:
            if rds['status'] != 'available':
                print(f"  - {rds['id']}: ステータスが '{rds['status']}' のため、確認が必要です")
                suggestions.append(f"RDS {rds['id']} のステータス確認")
        
        # Multi-AZの確認
        multi_az_count = sum(1 for rds in rds_info if rds['multi_az'])
        if multi_az_count > 0:
            print(f"  - Multi-AZが有効なインスタンス: {multi_az_count} 台")
            print(f"    → 開発・テスト環境ではMulti-AZを無効化することでコスト削減可能")
            print(f"    → 推定削減額: 約50%のコスト削減（Multi-AZ料金分）")
            suggestions.append("開発・テスト環境のMulti-AZ無効化検討")
        
        # バックアップ保持期間の確認
        long_retention = [rds for rds in rds_info if rds['backup_retention'] > 7]
        if long_retention:
            print(f"  - バックアップ保持期間が7日を超えるインスタンス: {len(long_retention)} 台")
            for rds in long_retention:
                print(f"    → {rds['id']}: {rds['backup_retention']} 日")
            print(f"    → 必要に応じて保持期間を短縮することでコスト削減可能")
            suggestions.append("バックアップ保持期間の見直し")
        
        # ストレージタイプの確認
        io1_instances = [rds for rds in rds_info if rds['storage_type'] == 'io1']
        if io1_instances:
            print(f"  - io1ストレージを使用しているインスタンス: {len(io1_instances)} 台")
            print(f"    → gp3への移行を検討（コスト削減の可能性）")
            suggestions.append("io1ストレージからgp3への移行検討")
        
        print()
    
    # EC2の改善案
    if ec2_info:
        print("[2] EC2の最適化")
        print("-" * 80)
        
        stopped_instances = [inst for inst in ec2_info if inst['state'] == 'stopped']
        if stopped_instances:
            print(f"  - 停止中のインスタンス: {len(stopped_instances)} 台")
            for inst in stopped_instances:
                print(f"    → {inst['id']} ({inst['name']}) - {inst['type']}")
            print(f"    → 長期停止中のインスタンスは削除を検討（EBSボリュームの料金が発生）")
            suggestions.append("停止中EC2インスタンスの削除検討")
        
        # 実行中のインスタンスの分析
        running_instances = [inst for inst in ec2_info if inst['state'] == 'running']
        if running_instances:
            print(f"  - 実行中のインスタンス: {len(running_instances)} 台")
            
            # インスタンスタイプ別の集計
            type_count = defaultdict(int)
            for inst in running_instances:
                type_count[inst['type']] += 1
            
            print(f"    → インスタンスタイプ別:")
            for inst_type, count in sorted(type_count.items()):
                print(f"      - {inst_type}: {count} 台")
            
            print(f"    → CloudWatchメトリクスでCPU/メモリ使用率を確認し、Right Sizingを検討")
            suggestions.append("EC2インスタンスタイプのRight Sizing検討")
        
        print()
    
    # NAT Gatewayの改善案
    if nat_info:
        print("[3] NAT Gatewayの最適化")
        print("-" * 80)
        
        active_nats = [nat for nat in nat_info if nat['state'] == 'available']
        print(f"  - アクティブなNAT Gateway: {len(active_nats)} 台")
        
        if len(active_nats) > 1:
            print(f"    → 複数のNAT Gatewayが存在します")
            print(f"    → 使用状況を確認し、統合の可能性を検討")
            suggestions.append("NAT Gatewayの統合検討")
        
        for nat in active_nats:
            print(f"    → {nat['id']} ({nat['name']})")
            print(f"      - VPC Endpointの活用を検討（S3、DynamoDB等へのアクセス）")
            print(f"      - これによりNAT Gateway経由のトラフィックを削減可能")
        
        print(f"    → NAT Gatewayの料金: 時間あたり$0.045 + データ転送料")
        print(f"    → 1台あたり月額約$32.4（固定料金のみ）")
        suggestions.append("VPC Endpointの活用検討")
        print()
    
    # Elastic IPの改善案
    if eip_info and eip_info.get('unassociated', 0) > 0:
        print("[4] Elastic IPの最適化")
        print("-" * 80)
        print(f"  - 未関連付けのElastic IP: {eip_info['unassociated']} 個")
        print(f"    → 未使用のElastic IPは削除を推奨（料金は発生しないが、リソース管理の観点から）")
        suggestions.append("未使用Elastic IPの削除")
        print()
    
    # 総合的な推奨事項
    print("[5] 総合的な推奨事項")
    print("-" * 80)
    print("  1. CloudWatchメトリクスでリソース使用率を確認")
    print("     - RDS: CPU、メモリ、接続数、ストレージ使用率")
    print("     - EC2: CPU、メモリ、ネットワーク使用率")
    print("     - 低使用率のリソースはダウンサイズを検討")
    print()
    print("  2. 開発・テスト環境の最適化")
    print("     - 営業時間外の自動停止スケジュール設定")
    print("     - 週末の自動停止設定")
    print("     - これにより約50-70%のコスト削減が可能")
    print()
    print("  3. データ転送コストの見直し")
    print("     - VPC Endpointの活用（S3、DynamoDB等）")
    print("     - CloudFrontの活用（静的コンテンツ）")
    print("     - 同一リージョン内でのデータ転送を優先")
    print()
    print("  4. モニタリングとアラートの設定")
    print("     - 予算アラートの設定")
    print("     - 異常なコストスパイクの検知")
    print("     - 未使用リソースの定期チェック")
    print()
    
    print("=" * 80)


def main():
    print("=" * 80)
    print("AWSリソース詳細分析レポート")
    print("=" * 80)
    print()
    
    rds_info = analyze_rds_instances()
    ec2_info = analyze_ec2_instances()
    nat_info = analyze_nat_gateways()
    eip_info = analyze_elastic_ips()
    
    generate_improvement_suggestions(rds_info, ec2_info, nat_info, eip_info)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
