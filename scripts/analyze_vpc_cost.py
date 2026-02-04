#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPCコスト詳細分析スクリプト
VPC関連のコスト内訳を詳細に分析する
"""

import boto3
import sys
import io
from datetime import datetime

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def analyze_vpc_resources():
    """VPC関連リソースの詳細分析"""
    print("=" * 80)
    print("VPCコスト詳細分析")
    print("=" * 80)
    print()
    
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    # VPC一覧
    print("【VPC一覧】")
    print("-" * 80)
    vpcs = ec2.describe_vpcs()
    for vpc in vpcs.get('Vpcs', []):
        vpc_id = vpc.get('VpcId', 'N/A')
        cidr = vpc.get('CidrBlock', 'N/A')
        is_default = vpc.get('IsDefault', False)
        tags = {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])}
        name = tags.get('Name', 'N/A')
        print(f"  VPC ID: {vpc_id}")
        print(f"    名前: {name}")
        print(f"    CIDR: {cidr}")
        print(f"    デフォルトVPC: {'はい' if is_default else 'いいえ'}")
        print()
    
    # NAT Gateway
    print("【NAT Gateway】")
    print("-" * 80)
    nats = ec2.describe_nat_gateways()
    nat_gateways = nats.get('NatGateways', [])
    if nat_gateways:
        for nat in nat_gateways:
            nat_id = nat.get('NatGatewayId', 'N/A')
            state = nat.get('State', 'N/A')
            subnet_id = nat.get('SubnetId', 'N/A')
            vpc_id = nat.get('VpcId', 'N/A')
            tags = {tag['Key']: tag['Value'] for tag in nat.get('Tags', [])}
            name = tags.get('Name', 'N/A')
            print(f"  NAT Gateway ID: {nat_id}")
            print(f"    名前: {name}")
            print(f"    ステータス: {state}")
            print(f"    VPC ID: {vpc_id}")
            print(f"    サブネット ID: {subnet_id}")
            print()
    else:
        print("  NAT Gatewayは見つかりませんでした。")
        print()
    
    # VPC Endpoints
    print("【VPC Endpoints】")
    print("-" * 80)
    endpoints = ec2.describe_vpc_endpoints()
    vpc_endpoints = endpoints.get('VpcEndpoints', [])
    if vpc_endpoints:
        for endpoint in vpc_endpoints:
            endpoint_id = endpoint.get('VpcEndpointId', 'N/A')
            service_name = endpoint.get('ServiceName', 'N/A')
            state = endpoint.get('State', 'N/A')
            vpc_id = endpoint.get('VpcId', 'N/A')
            tags = {tag['Key']: tag['Value'] for tag in endpoint.get('Tags', [])}
            name = tags.get('Name', 'N/A')
            print(f"  VPC Endpoint ID: {endpoint_id}")
            print(f"    名前: {name}")
            print(f"    サービス: {service_name}")
            print(f"    ステータス: {state}")
            print(f"    VPC ID: {vpc_id}")
            print()
    else:
        print("  VPC Endpointは見つかりませんでした。")
        print()
    
    # Elastic IP
    print("【Elastic IP】")
    print("-" * 80)
    addresses = ec2.describe_addresses()
    eips = addresses.get('Addresses', [])
    associated_count = 0
    unassociated_count = 0
    
    for eip in eips:
        public_ip = eip.get('PublicIp', 'N/A')
        allocation_id = eip.get('AllocationId', 'N/A')
        association_id = eip.get('AssociationId', None)
        instance_id = eip.get('InstanceId', None)
        
        if association_id:
            associated_count += 1
            print(f"  関連付け済み: {public_ip} → {instance_id}")
        else:
            unassociated_count += 1
            print(f"  未関連付け: {public_ip} ({allocation_id})")
    
    print()
    print(f"  関連付け済み: {associated_count} 個")
    print(f"  未関連付け: {unassociated_count} 個")
    print()
    
    # データ転送の分析（概算）
    print("【VPCコストの主な要因】")
    print("-" * 80)
    print("  VPCコストの主な内訳:")
    print("  1. NAT Gateway: 時間あたり$0.045（月額約$32.4）+ データ転送料")
    print("  2. VPC Endpoint: 時間あたり$0.01（月額約$7.2）+ データ転送料")
    print("  3. データ転送料:")
    print("     - 同一リージョン内: $0.01/GB")
    print("     - インターネットへの送信: $0.09/GB（最初の10TB）")
    print("     - インターネットからの受信: 無料")
    print()
    
    if len(nat_gateways) == 0:
        print("  → NAT Gatewayが見つかりませんでした。")
        print("  → VPCコスト$10.90の原因はデータ転送料の可能性が高いです。")
        print("  → CloudWatchでデータ転送量を確認することを推奨します。")
    else:
        print(f"  → NAT Gatewayが{len(nat_gateways)}台存在します。")
        print(f"  → 固定料金のみで月額約${len(nat_gateways) * 32.4:.2f}が発生しています。")
    
    print()


if __name__ == '__main__':
    try:
        analyze_vpc_resources()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
