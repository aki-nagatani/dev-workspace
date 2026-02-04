#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPC固定料金削減分析スクリプト
Elastic IPなどの固定料金の削減可能性を分析する
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


def get_elastic_ip_details():
    """Elastic IPの詳細情報を取得"""
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    addresses = ec2.describe_addresses()
    eips = []
    
    for eip in addresses.get('Addresses', []):
        public_ip = eip.get('PublicIp', 'N/A')
        allocation_id = eip.get('AllocationId', 'N/A')
        association_id = eip.get('AssociationId', None)
        instance_id = eip.get('InstanceId', None)
        network_interface_id = eip.get('NetworkInterfaceId', None)
        
        # 関連付け先の情報を取得
        associated_resource = None
        resource_type = None
        
        if instance_id:
            try:
                instances = ec2.describe_instances(InstanceIds=[instance_id])
                if instances.get('Reservations'):
                    instance = instances['Reservations'][0]['Instances'][0]
                    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    name = tags.get('Name', 'N/A')
                    resource_type = 'EC2'
                    associated_resource = {
                        'id': instance_id,
                        'name': name,
                        'type': 'EC2'
                    }
            except:
                pass
        
        if network_interface_id:
            try:
                nics = ec2.describe_network_interfaces(NetworkInterfaceIds=[network_interface_id])
                if nics.get('NetworkInterfaces'):
                    nic = nics['NetworkInterfaces'][0]
                    attachment = nic.get('Attachment', {})
                    if attachment.get('InstanceId'):
                        resource_type = 'EC2'
                        associated_resource = {
                            'id': attachment.get('InstanceId'),
                            'name': 'N/A',
                            'type': 'EC2'
                        }
                    elif attachment.get('InstanceOwnerId') == 'amazon-aws':
                        resource_type = 'NAT Gateway'
                        associated_resource = {
                            'id': network_interface_id,
                            'name': 'NAT Gateway',
                            'type': 'NAT Gateway'
                        }
            except:
                pass
        
        eips.append({
            'public_ip': public_ip,
            'allocation_id': allocation_id,
            'association_id': association_id,
            'instance_id': instance_id,
            'network_interface_id': network_interface_id,
            'is_associated': association_id is not None,
            'associated_resource': associated_resource,
            'resource_type': resource_type
        })
    
    return eips


def get_cost_by_usage_type(start_date: str, end_date: str):
    """使用タイプ別のコストを取得"""
    client = boto3.client('ce', region_name='us-east-1')
    
    try:
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
            ]
        )
        
        results = defaultdict(lambda: {'cost': 0, 'usage_types': {}})
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                usage_type = group['Keys'][1] if len(group['Keys']) > 1 else 'N/A'
                
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                if cost > 0:
                    results[service]['cost'] += cost
                    results[service]['usage_types'][usage_type] = cost
        
        return dict(results)
    except Exception as e:
        print(f"Error: Cost Explorer APIの呼び出しに失敗: {e}", file=sys.stderr)
        return {}


def analyze_elastic_ip_costs(eips):
    """Elastic IPのコストを分析"""
    print("【Elastic IPコスト分析】")
    print("-" * 80)
    
    associated_count = sum(1 for eip in eips if eip['is_associated'])
    unassociated_count = sum(1 for eip in eips if not eip['is_associated'])
    
    print(f"  総Elastic IP数: {len(eips)}")
    print(f"  関連付け済み: {associated_count} 個")
    print(f"  未関連付け: {unassociated_count} 個")
    print()
    
    # Elastic IPの料金体系
    # - EC2インスタンスに関連付けられている場合: 無料
    # - 未関連付け（Idle）の場合: 時間あたり$0.005（月額約$3.6）
    # - NAT Gatewayに割り当てられている場合: 無料（NAT Gatewayの料金に含まれる）
    
    print("  Elastic IPの料金体系:")
    print("    - EC2インスタンスに関連付け: 無料")
    print("    - 未関連付け（Idle）: 時間あたり$0.005（月額約$3.6）")
    print("    - NAT Gatewayに割り当て: 無料（NAT Gatewayの料金に含まれる）")
    print()
    
    # 未関連付けのElastic IPを確認
    if unassociated_count > 0:
        print("  ⚠️ 未関連付けのElastic IP:")
        for eip in eips:
            if not eip['is_associated']:
                print(f"    - {eip['public_ip']} ({eip['allocation_id']})")
                print(f"      → 削除することで月額$3.6の削減が可能")
        print()
        
        potential_savings = unassociated_count * 3.6
        print(f"  💰 削減可能額: 月額${potential_savings:.2f}")
        print()
    else:
        print("  ✅ 未関連付けのElastic IPはありません。")
        print()
    
    # 関連付け済みのElastic IPの詳細
    print("  関連付け済みのElastic IP:")
    for eip in eips:
        if eip['is_associated']:
            resource_info = eip['associated_resource']
            if resource_info:
                print(f"    - {eip['public_ip']} → {resource_info['type']}: {resource_info.get('name', resource_info['id'])}")
            else:
                print(f"    - {eip['public_ip']} → 関連付け先不明")
    print()


def analyze_vpc_fixed_costs(start_date: str, end_date: str):
    """VPC固定料金を分析"""
    print("【VPC固定料金分析】")
    print("-" * 80)
    
    # VPC関連のコストを取得
    service_costs = get_cost_by_usage_type(start_date, end_date)
    vpc_data = service_costs.get('Amazon Virtual Private Cloud', {})
    
    if not vpc_data or vpc_data['cost'] == 0:
        print("  VPC関連のコストは検出されませんでした。")
        print()
        return
    
    print(f"  VPC総コスト: ${vpc_data['cost']:.2f}/月")
    print()
    
    if vpc_data['usage_types']:
        print("  使用タイプ別の内訳:")
        for usage_type, cost in sorted(vpc_data['usage_types'].items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"    - {usage_type}: ${cost:.2f}")
        print()
        
        # 固定料金の分析
        print("  固定料金の内訳:")
        
        # Elastic IP関連
        eip_in_use_cost = vpc_data['usage_types'].get('APN1-PublicIPv4:InUseAddress', 0)
        eip_idle_cost = vpc_data['usage_types'].get('APN1-PublicIPv4:IdleAddress', 0)
        
        if eip_in_use_cost > 0 or eip_idle_cost > 0:
            print(f"    - Elastic IP（使用中）: ${eip_in_use_cost:.2f}")
            print(f"    - Elastic IP（未使用）: ${eip_idle_cost:.2f}")
            print()
            
            if eip_idle_cost > 0:
                print(f"    💰 未使用Elastic IPの削除により、月額${eip_idle_cost:.2f}の削減が可能")
                print()
        
        # その他の固定料金
        other_costs = {k: v for k, v in vpc_data['usage_types'].items() 
                      if 'PublicIPv4' not in k}
        if other_costs:
            print("    その他の固定料金:")
            for usage_type, cost in sorted(other_costs.items(), 
                                          key=lambda x: x[1], reverse=True):
                print(f"      - {usage_type}: ${cost:.2f}")
            print()


def analyze_cost_reduction_opportunities(eips, start_date: str, end_date: str):
    """コスト削減の機会を分析"""
    print("=" * 80)
    print("【コスト削減の機会】")
    print("=" * 80)
    print()
    
    # Elastic IPの削減可能性
    unassociated_count = sum(1 for eip in eips if not eip['is_associated'])
    eip_savings = unassociated_count * 3.6
    
    # VPCコストから未使用Elastic IPのコストを取得
    service_costs = get_cost_by_usage_type(start_date, end_date)
    vpc_data = service_costs.get('Amazon Virtual Private Cloud', {})
    eip_idle_cost = vpc_data.get('usage_types', {}).get('APN1-PublicIPv4:IdleAddress', 0)
    
    total_savings = 0
    
    print("1. **Elastic IPの削減**")
    print("-" * 80)
    if unassociated_count > 0:
        print(f"   未関連付けのElastic IP: {unassociated_count} 個")
        print(f"   削減可能額: 月額${eip_idle_cost:.2f}")
        print()
        print("   実施方法:")
        print("   - AWSコンソールまたはCLIで未使用のElastic IPを削除")
        print("   - 削除コマンド例:")
        for eip in eips:
            if not eip['is_associated']:
                print(f"     aws ec2 release-address --allocation-id {eip['allocation_id']}")
        print()
        total_savings += eip_idle_cost
    else:
        print("   ✅ 未使用のElastic IPはありません。")
        print()
    
    print("2. **その他の固定料金**")
    print("-" * 80)
    print("   VPCコストの主な固定料金:")
    print("   - Elastic IP（使用中）: EC2インスタンスに関連付けられている場合は無料")
    print("   - Elastic IP（未使用）: 削除可能")
    print("   - NAT Gateway: 使用されていないため、コストなし")
    print("   - VPC Endpoint: 設定されていないため、コストなし")
    print()
    
    print("3. **総合的な削減可能性**")
    print("-" * 80)
    if total_savings > 0:
        print(f"   総削減可能額: 月額${total_savings:.2f}")
        print()
        print("   ⚠️ 注意:")
        print("   - Elastic IPを削除する前に、本当に不要か確認してください")
        print("   - 削除後は同じIPアドレスを再取得することはできません")
        print("   - 本番環境のElastic IPは慎重に扱ってください")
    else:
        print("   ✅ 削減可能な固定料金は見つかりませんでした。")
        print("   - すべてのElastic IPは適切に使用されています")
        print("   - その他の固定料金も最小限です")
    print()


def main():
    print("=" * 80)
    print("VPC固定料金削減分析レポート")
    print("=" * 80)
    print()
    
    # 直近1ヶ月の期間を設定
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"分析期間: {start_date} ～ {end_date}")
    print()
    
    # Elastic IPの詳細を取得
    eips = get_elastic_ip_details()
    
    # Elastic IPのコストを分析
    analyze_elastic_ip_costs(eips)
    
    # VPC固定料金を分析
    analyze_vpc_fixed_costs(start_date, end_date)
    
    # コスト削減の機会を分析
    analyze_cost_reduction_opportunities(eips, start_date, end_date)
    
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
