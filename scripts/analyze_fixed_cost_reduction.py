#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
固定料金削減可能性分析スクリプト
Elastic IPなどの固定料金の削減可能性を詳細に分析する
"""

import boto3
import sys
import io
from datetime import datetime, timedelta

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
        
        # 関連付け先の情報を詳細に取得
        associated_resource = None
        resource_type = None
        is_free = False
        
        if instance_id:
            try:
                instances = ec2.describe_instances(InstanceIds=[instance_id])
                if instances.get('Reservations'):
                    instance = instances['Reservations'][0]['Instances'][0]
                    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    name = tags.get('Name', 'N/A')
                    resource_type = 'EC2'
                    # EC2インスタンスに関連付けられている場合は通常無料
                    is_free = True
                    associated_resource = {
                        'id': instance_id,
                        'name': name,
                        'type': 'EC2'
                    }
            except:
                pass
        
        if network_interface_id and not associated_resource:
            try:
                nics = ec2.describe_network_interfaces(NetworkInterfaceIds=[network_interface_id])
                if nics.get('NetworkInterfaces'):
                    nic = nics['NetworkInterfaces'][0]
                    attachment = nic.get('Attachment', {})
                    if attachment.get('InstanceId'):
                        resource_type = 'EC2'
                        is_free = True
                        associated_resource = {
                            'id': attachment.get('InstanceId'),
                            'name': 'N/A',
                            'type': 'EC2'
                        }
                    elif attachment.get('InstanceOwnerId') == 'amazon-aws':
                        resource_type = 'NAT Gateway'
                        # NAT Gatewayに割り当てられている場合は無料（NAT Gatewayの料金に含まれる）
                        is_free = True
                        associated_resource = {
                            'id': network_interface_id,
                            'name': 'NAT Gateway',
                            'type': 'NAT Gateway'
                        }
                    else:
                        # その他のリソース（Load Balancerなど）
                        resource_type = 'Other'
                        is_free = False
                        associated_resource = {
                            'id': network_interface_id,
                            'name': 'Other',
                            'type': 'Other'
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
            'resource_type': resource_type,
            'is_free': is_free
        })
    
    return eips


def get_vpc_cost_detail(start_date: str, end_date: str):
    """VPCコストの詳細内訳を取得"""
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
            ],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': ['Amazon Virtual Private Cloud']
                }
            }
        )
        
        usage_types = {}
        total_cost = 0
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                if len(group['Keys']) > 1:
                    usage_type = group['Keys'][1] if group['Keys'][1] else '(空)'
                else:
                    usage_type = '(N/A)'
                
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                if cost > 0:
                    if usage_type not in usage_types:
                        usage_types[usage_type] = 0
                    usage_types[usage_type] += cost
                    total_cost += cost
        
        return usage_types, total_cost
    except Exception as e:
        print(f"Error: Cost Explorer APIの呼び出しに失敗: {e}", file=sys.stderr)
        return {}, 0


def main():
    print("=" * 80)
    print("固定料金削減可能性分析レポート")
    print("=" * 80)
    print()
    
    # 直近1ヶ月の期間を設定
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"分析期間: {start_date} ～ {end_date}")
    print()
    
    # VPCコストの詳細内訳を取得
    usage_types, total_cost = get_vpc_cost_detail(start_date, end_date)
    
    print("【VPCコストの内訳】")
    print("-" * 80)
    print(f"  VPC総コスト: ${total_cost:.2f}/月")
    print()
    
    if usage_types:
        print("  使用タイプ別の内訳:")
        for usage_type, cost in sorted(usage_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {usage_type}: ${cost:.2f}")
        print()
    
    # Elastic IPの詳細を取得
    print("【Elastic IPの詳細分析】")
    print("-" * 80)
    
    eips = get_elastic_ip_details()
    
    print(f"  総Elastic IP数: {len(eips)}")
    print(f"  関連付け済み: {sum(1 for eip in eips if eip['is_associated'])} 個")
    print(f"  未関連付け: {sum(1 for eip in eips if not eip['is_associated'])} 個")
    print()
    
    # Elastic IPの料金体系
    print("  Elastic IPの料金体系:")
    print("    - EC2インスタンスに関連付け: 無料")
    print("    - NAT Gatewayに割り当て: 無料（NAT Gatewayの料金に含まれる）")
    print("    - 未関連付け（Idle）: 時間あたり$0.005（月額約$3.6）")
    print("    - その他のリソースに関連付け: 料金が発生する可能性あり")
    print()
    
    # 各Elastic IPの詳細
    print("  Elastic IPの詳細:")
    for eip in eips:
        print(f"    - {eip['public_ip']} ({eip['allocation_id']})")
        if eip['is_associated']:
            if eip['associated_resource']:
                print(f"      関連付け先: {eip['associated_resource']['type']} - {eip['associated_resource'].get('name', eip['associated_resource']['id'])}")
                if eip['is_free']:
                    print(f"      → 無料（EC2インスタンスまたはNAT Gatewayに関連付け）")
                else:
                    print(f"      → ⚠️ 料金が発生する可能性あり（その他のリソースに関連付け）")
            else:
                print(f"      関連付け先: 不明")
                print(f"      → ⚠️ 料金が発生する可能性あり")
        else:
            print(f"      未関連付け")
            print(f"      → 💰 削除により月額$3.6の削減が可能")
        print()
    
    # 固定料金の削減可能性を分析
    print("=" * 80)
    print("【固定料金の削減可能性】")
    print("=" * 80)
    print()
    
    # 未使用Elastic IPの削減可能性
    unassociated_count = sum(1 for eip in eips if not eip['is_associated'])
    unassociated_savings = unassociated_count * 3.6
    
    # 使用中だが無料でないElastic IPの削減可能性
    associated_not_free = [eip for eip in eips if eip['is_associated'] and not eip['is_free']]
    associated_not_free_savings = len(associated_not_free) * 3.6  # 概算
    
    print("1. **未使用Elastic IPの削除**")
    print("-" * 80)
    if unassociated_count > 0:
        print(f"   未関連付けのElastic IP: {unassociated_count} 個")
        print(f"   削減可能額: 月額${unassociated_savings:.2f}")
        print()
        print("   実施方法:")
        for eip in eips:
            if not eip['is_associated']:
                print(f"     aws ec2 release-address --allocation-id {eip['allocation_id']}")
        print()
    else:
        print("   ✅ 未使用のElastic IPはありません。")
        print()
    
    print("2. **使用中だが料金が発生しているElastic IP**")
    print("-" * 80)
    if associated_not_free:
        print(f"   料金が発生している可能性のあるElastic IP: {len(associated_not_free)} 個")
        print()
        print("   詳細:")
        for eip in associated_not_free:
            print(f"     - {eip['public_ip']}")
            if eip['associated_resource']:
                print(f"       関連付け先: {eip['associated_resource']['type']}")
            print(f"       → 関連付け先を確認し、EC2インスタンスに変更することで料金を削減可能")
        print()
        print(f"   推定削減可能額: 月額${associated_not_free_savings:.2f}（関連付け先をEC2インスタンスに変更した場合）")
        print()
    else:
        print("   ✅ すべてのElastic IPは無料で使用されています。")
        print()
    
    print("3. **その他の固定料金**")
    print("-" * 80)
    other_costs = {k: v for k, v in usage_types.items() if 'PublicIPv4' not in k}
    if other_costs:
        print("   その他の固定料金:")
        for usage_type, cost in sorted(other_costs.items(), key=lambda x: x[1], reverse=True):
            print(f"     - {usage_type}: ${cost:.2f}")
        print()
        print("   ⚠️ これらの固定料金は削減が困難な場合があります。")
        print("      各項目の詳細を確認してから削減を検討してください。")
    else:
        print("   ✅ その他の固定料金はありません。")
    print()
    
    # 総合的な削減可能性
    print("4. **総合的な削減可能性**")
    print("-" * 80)
    total_savings = unassociated_savings + associated_not_free_savings
    
    if total_savings > 0:
        print(f"   総削減可能額: 月額${total_savings:.2f}")
        print()
        print("   内訳:")
        if unassociated_savings > 0:
            print(f"     - 未使用Elastic IPの削除: ${unassociated_savings:.2f}/月")
        if associated_not_free_savings > 0:
            print(f"     - 使用中Elastic IPの最適化: ${associated_not_free_savings:.2f}/月（推定）")
        print()
        print("   ⚠️ 注意:")
        print("   - Elastic IPを削除する前に、本当に不要か確認してください")
        print("   - 削除後は同じIPアドレスを再取得することはできません")
        print("   - 本番環境のElastic IPは慎重に扱ってください")
        print("   - 使用中Elastic IPの最適化は、関連付け先を確認してから実施してください")
    else:
        print("   ✅ 削減可能な固定料金は見つかりませんでした。")
        print("   - すべてのElastic IPは適切に使用されています")
        print("   - その他の固定料金も最小限です")
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
