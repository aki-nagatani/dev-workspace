#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPCコスト詳細内訳分析スクリプト
Cost Explorer APIを使用してVPCコストのすべての内訳を取得し、合計を確認する
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
                usage_type = group['Keys'][1] if len(group['Keys']) > 1 else 'N/A'
                
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                if cost > 0:
                    usage_types[usage_type] = cost
                    total_cost += cost
        
        return usage_types, total_cost
    except Exception as e:
        print(f"Error: Cost Explorer APIの呼び出しに失敗: {e}", file=sys.stderr)
        return {}, 0


def get_vpc_cost_by_resource(start_date: str, end_date: str):
    """VPCコストをリソース別に取得"""
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
                {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'},
                {'Type': 'DIMENSION', 'Key': 'RESOURCE_ID'}
            ],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': ['Amazon Virtual Private Cloud']
                }
            }
        )
        
        resources = defaultdict(lambda: defaultdict(float))
        total_cost = 0
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                usage_type = group['Keys'][1] if len(group['Keys']) > 1 else 'N/A'
                resource_id = group['Keys'][2] if len(group['Keys']) > 2 else 'N/A'
                
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                if cost > 0:
                    resources[usage_type][resource_id] += cost
                    total_cost += cost
        
        return dict(resources), total_cost
    except Exception as e:
        print(f"Error: リソース別コストの取得に失敗: {e}", file=sys.stderr)
        return {}, 0


def main():
    print("=" * 80)
    print("VPCコスト詳細内訳分析レポート")
    print("=" * 80)
    print()
    
    # 直近1ヶ月の期間を設定
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"分析期間: {start_date} ～ {end_date}")
    print()
    
    # VPCコストの詳細内訳を取得
    print("【VPCコストの詳細内訳（使用タイプ別）】")
    print("-" * 80)
    
    usage_types, total_cost = get_vpc_cost_detail(start_date, end_date)
    
    if usage_types:
        print(f"  VPC総コスト: ${total_cost:.2f}/月")
        print()
        print("  使用タイプ別の内訳:")
        
        # コスト順にソート
        sorted_usage_types = sorted(usage_types.items(), key=lambda x: x[1], reverse=True)
        
        calculated_total = 0
        for usage_type, cost in sorted_usage_types:
            print(f"    - {usage_type}: ${cost:.2f}")
            calculated_total += cost
        
        print()
        print(f"  内訳の合計: ${calculated_total:.2f}")
        print(f"  総コスト: ${total_cost:.2f}")
        
        if abs(calculated_total - total_cost) > 0.01:
            print(f"  ⚠️ 差額: ${abs(calculated_total - total_cost):.2f}")
            print("  （他のコスト要因がある可能性があります）")
        else:
            print("  ✅ 合計が一致しています")
        print()
    else:
        print("  VPCコストの内訳が取得できませんでした。")
        print()
    
    # リソース別のコストを取得
    print("【VPCコストの詳細内訳（リソース別）】")
    print("-" * 80)
    
    resources, resource_total = get_vpc_cost_by_resource(start_date, end_date)
    
    if resources:
        print(f"  リソース別のコスト合計: ${resource_total:.2f}")
        print()
        
        for usage_type, resource_costs in sorted(resources.items(), key=lambda x: sum(x[1].values()), reverse=True):
            usage_type_total = sum(resource_costs.values())
            print(f"  【{usage_type}】: ${usage_type_total:.2f}")
            
            # リソース別に表示（上位10個まで）
            sorted_resources = sorted(resource_costs.items(), key=lambda x: x[1], reverse=True)
            for resource_id, cost in sorted_resources[:10]:
                print(f"    - {resource_id}: ${cost:.2f}")
            
            if len(sorted_resources) > 10:
                print(f"    ... 他 {len(sorted_resources) - 10} 個のリソース")
            print()
    else:
        print("  リソース別のコストが取得できませんでした。")
        print()
    
    # その他のVPC関連コストを確認
    print("【その他のVPC関連コストの確認】")
    print("-" * 80)
    print("  VPCコストに含まれる可能性のある項目:")
    print("  - Elastic IP（使用中・未使用）")
    print("  - NAT Gateway（時間あたり$0.045）")
    print("  - VPC Endpoint（時間あたり$0.01）")
    print("  - データ転送料")
    print("  - その他のVPC関連サービス")
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
