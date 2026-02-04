#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPCコスト完全内訳分析スクリプト
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


def get_vpc_total_cost(start_date: str, end_date: str):
    """VPCの総コストを取得"""
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
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': ['Amazon Virtual Private Cloud']
                }
            }
        )
        
        total_cost = 0
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                total_cost += cost
        
        return total_cost
    except Exception as e:
        print(f"Error: VPC総コストの取得に失敗: {e}", file=sys.stderr)
        return 0


def get_vpc_cost_by_usage_type(start_date: str, end_date: str):
    """VPCコストを使用タイプ別に取得（すべての使用タイプを含む）"""
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
                # 使用タイプが存在するか確認
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
        print(f"Error: 使用タイプ別コストの取得に失敗: {e}", file=sys.stderr)
        return {}, 0


def get_vpc_cost_by_operation(start_date: str, end_date: str):
    """VPCコストをオペレーション別に取得"""
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
                {'Type': 'DIMENSION', 'Key': 'OPERATION'}
            ],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': ['Amazon Virtual Private Cloud']
                }
            }
        )
        
        operations = {}
        total_cost = 0
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                operation = group['Keys'][1] if len(group['Keys']) > 1 else 'N/A'
                
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                if cost > 0:
                    operations[operation] = cost
                    total_cost += cost
        
        return operations, total_cost
    except Exception as e:
        print(f"Error: オペレーション別コストの取得に失敗: {e}", file=sys.stderr)
        return {}, 0


def get_vpc_cost_by_region(start_date: str, end_date: str):
    """VPCコストをリージョン別に取得"""
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
                {'Type': 'DIMENSION', 'Key': 'REGION'}
            ],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': ['Amazon Virtual Private Cloud']
                }
            }
        )
        
        regions = {}
        total_cost = 0
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                region = group['Keys'][1] if len(group['Keys']) > 1 else 'N/A'
                
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                
                if cost > 0:
                    regions[region] = cost
                    total_cost += cost
        
        return regions, total_cost
    except Exception as e:
        print(f"Error: リージョン別コストの取得に失敗: {e}", file=sys.stderr)
        return {}, 0


def main():
    print("=" * 80)
    print("VPCコスト完全内訳分析レポート")
    print("=" * 80)
    print()
    
    # 直近1ヶ月の期間を設定
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"分析期間: {start_date} ～ {end_date}")
    print()
    
    # VPC総コストを取得
    print("【VPC総コスト】")
    print("-" * 80)
    total_cost = get_vpc_total_cost(start_date, end_date)
    print(f"  VPC総コスト: ${total_cost:.2f}/月")
    print()
    
    # 使用タイプ別のコスト
    print("【使用タイプ別のコスト内訳】")
    print("-" * 80)
    usage_types, usage_type_total = get_vpc_cost_by_usage_type(start_date, end_date)
    
    if usage_types:
        print(f"  使用タイプ別の合計: ${usage_type_total:.2f}")
        print()
        print("  内訳:")
        calculated_total = 0
        for usage_type, cost in sorted(usage_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {usage_type}: ${cost:.2f}")
            calculated_total += cost
        print()
        print(f"  内訳の合計: ${calculated_total:.2f}")
        print(f"  総コスト: ${total_cost:.2f}")
        
        if abs(calculated_total - total_cost) > 0.01:
            print(f"  ⚠️ 差額: ${abs(calculated_total - total_cost):.2f}")
            print("  （使用タイプがN/Aまたは空のコストが含まれている可能性があります）")
        print()
    else:
        print("  使用タイプ別のコストが取得できませんでした。")
        print()
    
    # オペレーション別のコスト
    print("【オペレーション別のコスト内訳】")
    print("-" * 80)
    operations, operation_total = get_vpc_cost_by_operation(start_date, end_date)
    
    if operations:
        print(f"  オペレーション別の合計: ${operation_total:.2f}")
        print()
        print("  内訳:")
        for operation, cost in sorted(operations.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {operation}: ${cost:.2f}")
        print()
    else:
        print("  オペレーション別のコストが取得できませんでした。")
        print()
    
    # リージョン別のコスト
    print("【リージョン別のコスト内訳】")
    print("-" * 80)
    regions, region_total = get_vpc_cost_by_region(start_date, end_date)
    
    if regions:
        print(f"  リージョン別の合計: ${region_total:.2f}")
        print()
        print("  内訳:")
        for region, cost in sorted(regions.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {region}: ${cost:.2f}")
        print()
    else:
        print("  リージョン別のコストが取得できませんでした。")
        print()
    
    # 総合的な分析
    print("=" * 80)
    print("【総合的な分析】")
    print("=" * 80)
    print()
    print(f"  VPC総コスト: ${total_cost:.2f}/月")
    print(f"  使用タイプ別の合計: ${usage_type_total:.2f}/月")
    
    if abs(usage_type_total - total_cost) > 0.01:
        print(f"  ⚠️ 差額: ${abs(usage_type_total - total_cost):.2f}/月")
        print()
        print("  考えられる原因:")
        print("  1. 使用タイプがN/Aまたは空のコストが含まれている")
        print("  2. データ転送料が別のサービスとして計上されている可能性")
        print("  3. その他のVPC関連サービス（例: VPC Flow Logs、Transit Gatewayなど）")
        print("  4. Cost Explorerのデータ取得のタイミングの問題")
        print()
        print("  推奨される確認方法:")
        print("  - AWS Cost Explorerコンソールで直接確認")
        print("  - より詳細な期間で分析（日次など）")
        print("  - 他のディメンション（リージョン、オペレーションなど）で確認")
    else:
        print("  ✅ 合計が一致しています")
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
