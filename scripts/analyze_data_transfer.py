#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ転送量分析スクリプト
Cost Explorer APIを使用してS3/DynamoDBへのデータ転送量を確認し、
VPC Endpoint導入の効果を分析する
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


def get_cost_by_service_and_usage_type(start_date: str, end_date: str):
    """サービス別・使用タイプ別のコストを取得"""
    client = boto3.client('ce', region_name='us-east-1')
    
    try:
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost', 'UsageQuantity'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
            ]
        )
        
        results = defaultdict(lambda: {'cost': 0, 'usage': 0, 'usage_type_details': {}})
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                usage_type = group['Keys'][1] if len(group['Keys']) > 1 else 'N/A'
                
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                usage = float(group['Metrics'].get('UsageQuantity', {}).get('Amount', 0))
                
                if cost > 0:
                    results[service]['cost'] += cost
                    results[service]['usage'] += usage
                    if usage_type != 'N/A':
                        results[service]['usage_type_details'][usage_type] = {
                            'cost': cost,
                            'usage': usage
                        }
        
        return dict(results)
    except Exception as e:
        print(f"Error: Cost Explorer APIの呼び出しに失敗: {e}", file=sys.stderr)
        return {}


def get_data_transfer_costs(start_date: str, end_date: str):
    """データ転送関連のコストを取得"""
    client = boto3.client('ce', region_name='us-east-1')
    
    # データ転送関連の使用タイプを検索
    data_transfer_keywords = [
        'DataTransfer',
        'Data-Transfer',
        'Bytes',
        'GB-',
        'Data'
    ]
    
    try:
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost', 'UsageQuantity'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
            ]
        )
        
        data_transfer_results = defaultdict(lambda: {'cost': 0, 'usage_gb': 0, 'details': []})
        
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                usage_type = group['Keys'][1] if len(group['Keys']) > 1 else 'N/A'
                
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                usage = float(group['Metrics'].get('UsageQuantity', {}).get('Amount', 0))
                
                # データ転送関連の使用タイプをフィルタ
                if any(keyword.lower() in usage_type.lower() for keyword in data_transfer_keywords):
                    if cost > 0:
                        # 使用量をGBに変換（使用タイプによって単位が異なる可能性がある）
                        usage_gb = usage
                        if 'Bytes' in usage_type or 'bytes' in usage_type.lower():
                            usage_gb = usage / (1024**3)  # Bytes to GB
                        
                        data_transfer_results[service]['cost'] += cost
                        data_transfer_results[service]['usage_gb'] += usage_gb
                        data_transfer_results[service]['details'].append({
                            'usage_type': usage_type,
                            'cost': cost,
                            'usage': usage,
                            'usage_gb': usage_gb
                        })
        
        return dict(data_transfer_results)
    except Exception as e:
        print(f"Error: データ転送コストの取得に失敗: {e}", file=sys.stderr)
        return {}


def analyze_s3_data_transfer(start_date: str, end_date: str):
    """S3へのデータ転送量を分析"""
    print("【S3データ転送分析】")
    print("-" * 80)
    
    # S3のコストを取得
    service_costs = get_cost_by_service_and_usage_type(start_date, end_date)
    s3_data = service_costs.get('Amazon Simple Storage Service', {})
    
    if not s3_data or s3_data['cost'] == 0:
        print("  S3へのデータ転送コストは検出されませんでした。")
        print("  （データ転送量が少ないか、無料枠内の可能性があります）")
        print()
        return 0, 0
    
    # データ転送関連のコストを詳細に取得
    data_transfer_costs = get_data_transfer_costs(start_date, end_date)
    s3_transfer = data_transfer_costs.get('Amazon Simple Storage Service', {})
    
    print(f"  S3総コスト: ${s3_data['cost']:.2f}")
    print()
    
    if s3_transfer and s3_transfer['cost'] > 0:
        print("  データ転送関連のコスト:")
        print(f"    - データ転送コスト: ${s3_transfer['cost']:.2f}")
        print(f"    - 推定データ転送量: {s3_transfer['usage_gb']:.2f} GB")
        print()
        
        if s3_transfer['details']:
            print("    詳細内訳:")
            for detail in s3_transfer['details']:
                print(f"      - {detail['usage_type']}: ${detail['cost']:.2f} ({detail['usage_gb']:.2f} GB)")
            print()
        
        return s3_transfer['cost'], s3_transfer['usage_gb']
    else:
        print("  データ転送関連のコストは検出されませんでした。")
        print("  （ストレージコストのみの可能性があります）")
        print()
        return 0, 0


def analyze_dynamodb_data_transfer(start_date: str, end_date: str):
    """DynamoDBへのデータ転送量を分析"""
    print("【DynamoDBデータ転送分析】")
    print("-" * 80)
    
    # DynamoDBのコストを取得
    service_costs = get_cost_by_service_and_usage_type(start_date, end_date)
    dynamodb_data = service_costs.get('Amazon DynamoDB', {})
    
    if not dynamodb_data or dynamodb_data['cost'] == 0:
        print("  DynamoDBへのデータ転送コストは検出されませんでした。")
        print("  （データ転送量が少ないか、無料枠内の可能性があります）")
        print()
        return 0, 0
    
    # データ転送関連のコストを詳細に取得
    data_transfer_costs = get_data_transfer_costs(start_date, end_date)
    dynamodb_transfer = data_transfer_costs.get('Amazon DynamoDB', {})
    
    print(f"  DynamoDB総コスト: ${dynamodb_data['cost']:.2f}")
    print()
    
    if dynamodb_transfer and dynamodb_transfer['cost'] > 0:
        print("  データ転送関連のコスト:")
        print(f"    - データ転送コスト: ${dynamodb_transfer['cost']:.2f}")
        print(f"    - 推定データ転送量: {dynamodb_transfer['usage_gb']:.2f} GB")
        print()
        
        if dynamodb_transfer['details']:
            print("    詳細内訳:")
            for detail in dynamodb_transfer['details']:
                print(f"      - {detail['usage_type']}: ${detail['cost']:.2f} ({detail['usage_gb']:.2f} GB)")
            print()
        
        return dynamodb_transfer['cost'], dynamodb_transfer['usage_gb']
    else:
        print("  データ転送関連のコストは検出されませんでした。")
        print("  （読み書きユニットのコストのみの可能性があります）")
        print()
        return 0, 0


def analyze_vpc_data_transfer(start_date: str, end_date: str):
    """VPC関連のデータ転送コストを分析"""
    print("【VPCデータ転送分析】")
    print("-" * 80)
    
    # VPCのコストを取得
    service_costs = get_cost_by_service_and_usage_type(start_date, end_date)
    vpc_data = service_costs.get('Amazon Virtual Private Cloud', {})
    
    if not vpc_data or vpc_data['cost'] == 0:
        print("  VPC関連のコストは検出されませんでした。")
        print()
        return 0
    
    print(f"  VPC総コスト: ${vpc_data['cost']:.2f}")
    print()
    
    if vpc_data['usage_type_details']:
        print("  使用タイプ別の内訳:")
        for usage_type, details in sorted(vpc_data['usage_type_details'].items(), 
                                          key=lambda x: x[1]['cost'], reverse=True):
            print(f"    - {usage_type}: ${details['cost']:.2f}")
        print()
    
    return vpc_data['cost']


def calculate_vpc_endpoint_benefit(s3_transfer_cost: float, s3_transfer_gb: float,
                                   dynamodb_transfer_cost: float, dynamodb_transfer_gb: float):
    """VPC Endpoint導入による効果を計算"""
    print("=" * 80)
    print("【VPC Endpoint導入効果の試算】")
    print("=" * 80)
    print()
    
    # VPC Endpointの料金
    s3_endpoint_cost = 7.2  # 月額
    dynamodb_endpoint_cost = 7.2  # 月額
    
    # データ転送料（同一リージョン内: $0.01/GB）
    data_transfer_rate = 0.01  # per GB
    
    print("1. **S3 Gateway Endpoint**")
    print("-" * 80)
    print(f"   VPC Endpoint料金: ${s3_endpoint_cost:.2f}/月")
    print(f"   現在のデータ転送コスト: ${s3_transfer_cost:.2f}/月")
    print(f"   推定データ転送量: {s3_transfer_gb:.2f} GB/月")
    print()
    
    if s3_transfer_gb > 0:
        current_transfer_cost = s3_transfer_gb * data_transfer_rate
        savings = current_transfer_cost - s3_endpoint_cost
        break_even_gb = s3_endpoint_cost / data_transfer_rate
        
        print(f"   データ転送料（$0.01/GB）: ${current_transfer_cost:.2f}/月")
        print(f"   導入後のコスト: ${s3_endpoint_cost:.2f}/月")
        print(f"   削減額: ${savings:.2f}/月")
        print(f"   損益分岐点: {break_even_gb:.2f} GB/月")
        print()
        
        if s3_transfer_gb >= break_even_gb:
            print(f"   ✅ 推奨: データ転送量が{break_even_gb:.2f}GB以上のため、導入が有効です")
        else:
            print(f"   ⚠️ 注意: データ転送量が{break_even_gb:.2f}GB未満のため、")
            print(f"      固定料金がデータ転送料を上回る可能性があります")
        print()
    else:
        print("   ⚠️ データ転送量が検出されませんでした。")
        print("      セキュリティやパフォーマンス要件で導入を検討してください。")
        print()
    
    print("2. **DynamoDB Gateway Endpoint**")
    print("-" * 80)
    print(f"   VPC Endpoint料金: ${dynamodb_endpoint_cost:.2f}/月")
    print(f"   現在のデータ転送コスト: ${dynamodb_transfer_cost:.2f}/月")
    print(f"   推定データ転送量: {dynamodb_transfer_gb:.2f} GB/月")
    print()
    
    if dynamodb_transfer_gb > 0:
        current_transfer_cost = dynamodb_transfer_gb * data_transfer_rate
        savings = current_transfer_cost - dynamodb_endpoint_cost
        break_even_gb = dynamodb_endpoint_cost / data_transfer_rate
        
        print(f"   データ転送料（$0.01/GB）: ${current_transfer_cost:.2f}/月")
        print(f"   導入後のコスト: ${dynamodb_endpoint_cost:.2f}/月")
        print(f"   削減額: ${savings:.2f}/月")
        print(f"   損益分岐点: {break_even_gb:.2f} GB/月")
        print()
        
        if dynamodb_transfer_gb >= break_even_gb:
            print(f"   ✅ 推奨: データ転送量が{break_even_gb:.2f}GB以上のため、導入が有効です")
        else:
            print(f"   ⚠️ 注意: データ転送量が{break_even_gb:.2f}GB未満のため、")
            print(f"      固定料金がデータ転送料を上回る可能性があります")
        print()
    else:
        print("   ⚠️ データ転送量が検出されませんでした。")
        print("      セキュリティやパフォーマンス要件で導入を検討してください。")
        print()
    
    # 総合的な推奨
    print("3. **総合的な推奨**")
    print("-" * 80)
    total_endpoint_cost = s3_endpoint_cost + dynamodb_endpoint_cost
    total_transfer_cost = s3_transfer_cost + dynamodb_transfer_cost
    total_savings = total_transfer_cost - total_endpoint_cost
    
    print(f"   VPC Endpoint合計コスト: ${total_endpoint_cost:.2f}/月")
    print(f"   現在のデータ転送コスト合計: ${total_transfer_cost:.2f}/月")
    print(f"   推定削減額: ${total_savings:.2f}/月")
    print()
    
    if total_savings > 0:
        print(f"   ✅ VPC Endpointの導入により、月額${total_savings:.2f}の削減が可能です")
    else:
        print(f"   ⚠️ データ転送量が少ないため、VPC Endpointの固定料金が")
        print(f"      データ転送料を上回る可能性があります")
        print(f"      セキュリティやパフォーマンス要件で導入を検討してください")
    print()


def main():
    print("=" * 80)
    print("データ転送量分析レポート")
    print("=" * 80)
    print()
    
    # 直近1ヶ月の期間を設定
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"分析期間: {start_date} ～ {end_date}")
    print()
    
    # S3のデータ転送量を分析
    s3_transfer_cost, s3_transfer_gb = analyze_s3_data_transfer(start_date, end_date)
    
    # DynamoDBのデータ転送量を分析
    dynamodb_transfer_cost, dynamodb_transfer_gb = analyze_dynamodb_data_transfer(start_date, end_date)
    
    # VPCのデータ転送コストを分析
    vpc_cost = analyze_vpc_data_transfer(start_date, end_date)
    
    # VPC Endpoint導入効果を計算
    calculate_vpc_endpoint_benefit(s3_transfer_cost, s3_transfer_gb,
                                   dynamodb_transfer_cost, dynamodb_transfer_gb)
    
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
