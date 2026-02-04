#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWSコスト分析スクリプト
1月のAWSコストを詳細に分析し、改善案を提案する
"""

import boto3
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any
import sys
import io

# 標準出力のエンコーディングをUTF-8に設定
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def get_cost_by_service(start_date: str, end_date: str) -> Dict[str, float]:
    """サービス別のコストを取得"""
    client = boto3.client('ce', region_name='us-east-1')
    
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'}
        ]
    )
    
    costs = {}
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            service = group['Keys'][0]
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            if amount > 0:
                costs[service] = amount
    
    return costs


def get_cost_by_region(start_date: str, end_date: str) -> Dict[str, float]:
    """リージョン別のコストを取得"""
    client = boto3.client('ce', region_name='us-east-1')
    
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'REGION'}
        ]
    )
    
    costs = {}
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            region = group['Keys'][0] if group['Keys'][0] else 'No Region'
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            if amount > 0:
                costs[region] = amount
    
    return costs


def get_daily_costs(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """日次コストの推移を取得"""
    client = boto3.client('ce', region_name='us-east-1')
    
    # 日付範囲を計算
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    daily_costs = []
    current = start
    
    while current < end:
        day_start = current.strftime('%Y-%m-%d')
        day_end = (current + timedelta(days=1)).strftime('%Y-%m-%d')
        
        try:
            response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': day_start,
                    'End': day_end
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            
            for result in response['ResultsByTime']:
                amount = float(result['Total']['UnblendedCost']['Amount'])
                daily_costs.append({
                    'date': day_start,
                    'cost': amount
                })
        except Exception as e:
            print(f"Warning: Failed to get cost for {day_start}: {e}", file=sys.stderr)
        
        current += timedelta(days=1)
    
    return daily_costs


def get_cost_optimization_recommendations() -> List[Dict[str, Any]]:
    """コスト最適化の推奨事項を取得"""
    recommendations = []
    
    try:
        # Compute Optimizerの推奨事項
        compute_optimizer = boto3.client('compute-optimizer', region_name='us-east-1')
        
        # EC2インスタンスの推奨事項
        try:
            ec2_response = compute_optimizer.get_ec2_instance_recommendations()
            for rec in ec2_response.get('instanceRecommendations', [])[:10]:
                recommendations.append({
                    'type': 'EC2',
                    'resource_id': rec.get('instanceArn', 'N/A'),
                    'current_instance_type': rec.get('currentInstanceType', 'N/A'),
                    'recommended_instance_type': rec.get('recommendationOptions', [{}])[0].get('instanceType', 'N/A'),
                    'estimated_monthly_savings': rec.get('recommendationOptions', [{}])[0].get('estimatedMonthlySavings', {}).get('value', 0)
                })
        except Exception as e:
            print(f"Warning: Could not get EC2 recommendations: {e}", file=sys.stderr)
        
        # Lambda関数の推奨事項
        try:
            lambda_response = compute_optimizer.get_lambda_function_recommendations()
            for rec in lambda_response.get('lambdaFunctionRecommendations', [])[:10]:
                recommendations.append({
                    'type': 'Lambda',
                    'resource_id': rec.get('functionArn', 'N/A'),
                    'current_memory': rec.get('currentMemorySize', 'N/A'),
                    'recommended_memory': rec.get('recommendationOptions', [{}])[0].get('memorySize', 'N/A'),
                    'estimated_monthly_savings': rec.get('recommendationOptions', [{}])[0].get('estimatedMonthlySavings', {}).get('value', 0)
                })
        except Exception as e:
            print(f"Warning: Could not get Lambda recommendations: {e}", file=sys.stderr)
            
    except Exception as e:
        print(f"Warning: Could not get optimization recommendations: {e}", file=sys.stderr)
    
    return recommendations


def analyze_and_report(start_date: str, end_date: str):
    """コストを分析してレポートを生成"""
    print("=" * 80)
    print(f"AWSコスト分析レポート ({start_date} ～ {end_date})")
    print("=" * 80)
    print()
    
    # サービス別コスト
    print("【サービス別コスト】")
    print("-" * 80)
    service_costs = get_cost_by_service(start_date, end_date)
    total_cost = sum(service_costs.values())
    
    # コスト順にソート
    sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
    
    for service, cost in sorted_services:
        percentage = (cost / total_cost * 100) if total_cost > 0 else 0
        print(f"  {service:40s} ${cost:>10.2f} ({percentage:>5.1f}%)")
    
    print(f"\n  合計: ${total_cost:.2f}")
    print()
    
    # リージョン別コスト
    print("【リージョン別コスト】")
    print("-" * 80)
    region_costs = get_cost_by_region(start_date, end_date)
    sorted_regions = sorted(region_costs.items(), key=lambda x: x[1], reverse=True)
    
    for region, cost in sorted_regions:
        percentage = (cost / total_cost * 100) if total_cost > 0 else 0
        print(f"  {region:40s} ${cost:>10.2f} ({percentage:>5.1f}%)")
    print()
    
    # 日次コスト推移
    print("【日次コスト推移（上位10日）】")
    print("-" * 80)
    daily_costs = get_daily_costs(start_date, end_date)
    sorted_daily = sorted(daily_costs, key=lambda x: x['cost'], reverse=True)[:10]
    
    for day in sorted_daily:
        print(f"  {day['date']}: ${day['cost']:.2f}")
    print()
    
    # コスト最適化の推奨事項
    print("【コスト最適化の推奨事項】")
    print("-" * 80)
    recommendations = get_cost_optimization_recommendations()
    
    if recommendations:
        total_savings = 0
        for rec in recommendations:
            savings = rec.get('estimated_monthly_savings', 0)
            total_savings += savings
            
            if rec['type'] == 'EC2':
                print(f"  EC2インスタンス:")
                print(f"    - リソースID: {rec['resource_id']}")
                print(f"    - 現在のインスタンスタイプ: {rec['current_instance_type']}")
                print(f"    - 推奨インスタンスタイプ: {rec['recommended_instance_type']}")
                print(f"    - 推定月間節約額: ${savings:.2f}")
                print()
            elif rec['type'] == 'Lambda':
                print(f"  Lambda関数:")
                print(f"    - リソースID: {rec['resource_id']}")
                print(f"    - 現在のメモリ: {rec['current_memory']} MB")
                print(f"    - 推奨メモリ: {rec['recommended_memory']} MB")
                print(f"    - 推定月間節約額: ${savings:.2f}")
                print()
        
        if total_savings > 0:
            print(f"  推定月間節約額合計: ${total_savings:.2f}")
    else:
        print("  推奨事項が見つかりませんでした。")
    print()
    
    # 改善案の提案
    print("【改善案の提案】")
    print("-" * 80)
    
    improvement_suggestions = []
    
    # 高コストサービスの分析
    top_services = sorted_services[:5]
    for service, cost in top_services:
        if cost > total_cost * 0.1:  # 総コストの10%以上
            percentage = (cost / total_cost * 100)
            print(f"  [1] {service}:")
            print(f"      - 月間コスト: ${cost:.2f} ({percentage:.1f}%)")
            
            if service == "Amazon Relational Database Service":
                print(f"      - RDSのコスト最適化案:")
                print(f"        * Reserved Instancesの検討（最大72%の割引）")
                print(f"        * 使用していないDBインスタンスの停止")
                print(f"        * インスタンスタイプの見直し（必要以上のスペックを削減）")
                print(f"        * 自動バックアップの保持期間の見直し")
                print(f"        * ストレージタイプの最適化（gp3への移行検討）")
            elif service == "Amazon Elastic Compute Cloud - Compute":
                print(f"      - EC2のコスト最適化案:")
                print(f"        * Reserved InstancesまたはSavings Plansの検討（最大72%の割引）")
                print(f"        * 使用していないインスタンスの停止・削除")
                print(f"        * インスタンスタイプの見直し（Right Sizing）")
                print(f"        * Spot Instancesの活用（開発・テスト環境）")
                print(f"        * Auto Scalingの適切な設定")
            elif service == "Amazon Virtual Private Cloud":
                print(f"      - VPCのコスト最適化案:")
                print(f"        * NAT Gatewayの使用状況確認（不要な場合は削除）")
                print(f"        * VPC Endpointの活用（NAT Gatewayの代替）")
                print(f"        * 未使用のElastic IPの解放")
                print(f"        * データ転送量の見直し")
            print()
    
    # リージョン分散の確認
    if len(sorted_regions) > 1:
        top_region_cost = sorted_regions[0][1]
        top_region_name = sorted_regions[0][0]
        if top_region_cost > total_cost * 0.8:  # 1つのリージョンが80%以上
            print(f"  [2] リージョン集中:")
            print(f"      - {top_region_name}が総コストの{(top_region_cost/total_cost*100):.1f}%を占めています")
            print(f"      - 現状は問題ありませんが、将来的なマルチリージョン戦略の検討を推奨します")
            print()
    
    # 日次コストの変動分析
    if daily_costs:
        avg_daily = sum(d['cost'] for d in daily_costs) / len(daily_costs)
        max_daily = max(d['cost'] for d in daily_costs)
        min_daily = min(d['cost'] for d in daily_costs)
        max_date = next(d['date'] for d in daily_costs if d['cost'] == max_daily)
        
        print(f"  [3] 日次コストの変動:")
        print(f"      - 平均日次コスト: ${avg_daily:.2f}")
        print(f"      - 最大日次コスト: ${max_daily:.2f} ({max_date})")
        print(f"      - 最小日次コスト: ${min_daily:.2f}")
        
        if max_daily > avg_daily * 1.5:  # 平均の1.5倍以上
            print(f"      - 警告: {max_date}にコストスパイクが発生しています")
            print(f"      - 原因調査を推奨します（新規リソースの起動、データ転送量の増加など）")
        print()
    
    # 総合的な推奨事項
    print("  [4] 総合的な推奨事項:")
    print(f"      - 総コスト: ${total_cost:.2f}/月")
    
    # RDSとEC2の合計が70%以上の場合
    rds_cost = service_costs.get("Amazon Relational Database Service", 0)
    ec2_cost = service_costs.get("Amazon Elastic Compute Cloud - Compute", 0)
    compute_total = rds_cost + ec2_cost
    
    if compute_total > total_cost * 0.7:
        print(f"      - コンピューティングリソース（RDS + EC2）が総コストの{(compute_total/total_cost*100):.1f}%を占めています")
        print(f"      - Reserved InstancesまたはSavings Plansの導入を強く推奨します")
        print(f"      - 推定節約額: ${compute_total * 0.3:.2f}/月（30%割引を想定）")
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    # 1月の日付範囲
    start_date = '2026-01-01'
    end_date = '2026-01-31'
    
    try:
        analyze_and_report(start_date, end_date)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
