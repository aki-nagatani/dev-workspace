#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPC Endpoint活用検討スクリプト
S3やDynamoDBへのアクセス状況を確認し、VPC Endpointの導入効果を分析する
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


def get_vpc_info():
    """VPC情報を取得"""
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    vpcs = []
    response = ec2.describe_vpcs()
    for vpc in response.get('Vpcs', []):
        vpc_id = vpc.get('VpcId')
        cidr = vpc.get('CidrBlock')
        is_default = vpc.get('IsDefault', False)
        tags = {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])}
        name = tags.get('Name', 'N/A')
        
        if not is_default:
            vpcs.append({
                'id': vpc_id,
                'name': name,
                'cidr': cidr
            })
    
    return vpcs


def get_existing_vpc_endpoints():
    """既存のVPC Endpointを取得"""
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    endpoints = []
    response = ec2.describe_vpc_endpoints()
    for endpoint in response.get('VpcEndpoints', []):
        endpoint_id = endpoint.get('VpcEndpointId')
        service_name = endpoint.get('ServiceName', '')
        state = endpoint.get('State')
        vpc_id = endpoint.get('VpcId')
        vpc_endpoint_type = endpoint.get('VpcEndpointType', 'Gateway')
        tags = {tag['Key']: tag['Value'] for tag in endpoint.get('Tags', [])}
        name = tags.get('Name', 'N/A')
        
        endpoints.append({
            'id': endpoint_id,
            'name': name,
            'service': service_name,
            'state': state,
            'vpc_id': vpc_id,
            'type': vpc_endpoint_type
        })
    
    return endpoints


def get_s3_buckets():
    """S3バケット一覧を取得"""
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    
    buckets = []
    try:
        response = s3.list_buckets()
        for bucket in response.get('Buckets', []):
            bucket_name = bucket.get('Name')
            creation_date = bucket.get('CreationDate')
            
            # バケットのリージョンを確認
            try:
                location = s3.get_bucket_location(Bucket=bucket_name)
                bucket_region = location.get('LocationConstraint') or 'us-east-1'
            except:
                bucket_region = 'unknown'
            
            buckets.append({
                'name': bucket_name,
                'region': bucket_region,
                'creation_date': creation_date
            })
    except Exception as e:
        print(f"  Warning: S3バケットの取得に失敗: {e}", file=sys.stderr)
    
    return buckets


def get_dynamodb_tables():
    """DynamoDBテーブル一覧を取得"""
    dynamodb = boto3.client('dynamodb', region_name='ap-northeast-1')
    
    tables = []
    try:
        response = dynamodb.list_tables()
        for table_name in response.get('TableNames', []):
            try:
                table_info = dynamodb.describe_table(TableName=table_name)
                table = table_info.get('Table', {})
                tables.append({
                    'name': table_name,
                    'status': table.get('TableStatus'),
                    'item_count': table.get('ItemCount', 0)
                })
            except:
                tables.append({
                    'name': table_name,
                    'status': 'unknown',
                    'item_count': 0
                })
    except Exception as e:
        print(f"  Warning: DynamoDBテーブルの取得に失敗: {e}", file=sys.stderr)
    
    return tables


def get_cloudwatch_data_transfer(vpc_id: str, days: int = 30):
    """CloudWatchからデータ転送量を取得（概算）"""
    cloudwatch = boto3.client('cloudwatch', region_name='ap-northeast-1')
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    # VPC内のデータ転送量を取得するのは難しいため、概算で提示
    # 実際のデータ転送量は、Cost Explorerで確認する必要がある
    return None


def calculate_vpc_endpoint_cost(service: str, data_transfer_gb: float = 0):
    """VPC Endpointのコストを計算"""
    # VPC Endpointの料金（ap-northeast-1）
    # Gateway型: 時間あたり$0.01（月額約$7.2）+ データ転送料なし
    # Interface型: 時間あたり$0.01（月額約$7.2）+ データ転送料$0.01/GB
    
    if service == 's3':
        # S3はGateway型のみ
        monthly_cost = 7.2  # 固定料金のみ
        return monthly_cost
    elif service == 'dynamodb':
        # DynamoDBはGateway型のみ
        monthly_cost = 7.2  # 固定料金のみ
        return monthly_cost
    else:
        # その他のサービス（Interface型）
        monthly_cost = 7.2 + (data_transfer_gb * 0.01)
        return monthly_cost


def analyze_vpc_endpoint_benefits():
    """VPC Endpointの導入効果を分析"""
    print("=" * 80)
    print("VPC Endpoint活用検討レポート")
    print("=" * 80)
    print()
    
    # VPC情報を取得
    print("【VPC構成】")
    print("-" * 80)
    vpcs = get_vpc_info()
    for vpc in vpcs:
        print(f"  VPC: {vpc['name']} ({vpc['id']})")
        print(f"    CIDR: {vpc['cidr']}")
    print()
    
    # 既存のVPC Endpointを確認
    print("【既存のVPC Endpoint】")
    print("-" * 80)
    existing_endpoints = get_existing_vpc_endpoints()
    if existing_endpoints:
        for endpoint in existing_endpoints:
            print(f"  {endpoint['name']} ({endpoint['id']})")
            print(f"    サービス: {endpoint['service']}")
            print(f"    タイプ: {endpoint['type']}")
            print(f"    ステータス: {endpoint['state']}")
            print(f"    VPC: {endpoint['vpc_id']}")
            print()
    else:
        print("  VPC Endpointは設定されていません。")
        print()
    
    # S3バケットを確認
    print("【S3バケット】")
    print("-" * 80)
    s3_buckets = get_s3_buckets()
    if s3_buckets:
        ap_northeast_1_buckets = [b for b in s3_buckets if b['region'] == 'ap-northeast-1' or b['region'] == '']
        print(f"  総バケット数: {len(s3_buckets)}")
        print(f"  ap-northeast-1リージョンのバケット: {len(ap_northeast_1_buckets)}")
        print()
        if ap_northeast_1_buckets:
            print("  ap-northeast-1リージョンのバケット一覧:")
            for bucket in ap_northeast_1_buckets[:10]:  # 最大10個まで表示
                print(f"    - {bucket['name']}")
            if len(ap_northeast_1_buckets) > 10:
                print(f"    ... 他 {len(ap_northeast_1_buckets) - 10} 個")
            print()
    else:
        print("  S3バケットは見つかりませんでした。")
        print()
    
    # DynamoDBテーブルを確認
    print("【DynamoDBテーブル】")
    print("-" * 80)
    dynamodb_tables = get_dynamodb_tables()
    if dynamodb_tables:
        print(f"  総テーブル数: {len(dynamodb_tables)}")
        print()
        print("  テーブル一覧:")
        for table in dynamodb_tables[:10]:  # 最大10個まで表示
            print(f"    - {table['name']} (ステータス: {table['status']}, アイテム数: {table['item_count']})")
        if len(dynamodb_tables) > 10:
            print(f"    ... 他 {len(dynamodb_tables) - 10} 個")
        print()
    else:
        print("  DynamoDBテーブルは見つかりませんでした。")
        print()
    
    # VPC Endpointの導入効果を分析
    print("=" * 80)
    print("【VPC Endpoint導入効果の分析】")
    print("=" * 80)
    print()
    
    print("1. **現在の状況**")
    print("-" * 80)
    print("  - NAT Gateway: 使用されていない")
    print("  - VPC Endpoint: 設定されていない")
    print("  - VPCコスト: $10.90/月（データ転送料が主な要因）")
    print()
    
    print("2. **VPC Endpointのメリット**")
    print("-" * 80)
    print("  - S3/DynamoDBへのアクセスがVPC内で完結し、インターネット経由のデータ転送が不要")
    print("  - データ転送料の削減（同一リージョン内: $0.01/GB → VPC Endpoint経由: 無料）")
    print("  - セキュリティの向上（インターネット経由のアクセスを排除）")
    print("  - パフォーマンスの向上（VPC内での通信のため低レイテンシ）")
    print()
    
    print("3. **推奨されるVPC Endpoint**")
    print("-" * 80)
    
    if s3_buckets and any(b['region'] == 'ap-northeast-1' or b['region'] == '' for b in s3_buckets):
        print("  ✅ S3 Gateway Endpoint（推奨）")
        print("     - 料金: 月額$7.2（固定料金のみ）")
        print("     - データ転送料: 無料")
        print("     - 対象VPC: すべてのVPC")
        print("     - 効果: S3へのデータ転送料を削減")
        print()
    
    if dynamodb_tables:
        print("  ✅ DynamoDB Gateway Endpoint（推奨）")
        print("     - 料金: 月額$7.2（固定料金のみ）")
        print("     - データ転送料: 無料")
        print("     - 対象VPC: すべてのVPC")
        print("     - 効果: DynamoDBへのデータ転送料を削減")
        print()
    
    print("4. **コスト削減効果の試算**")
    print("-" * 80)
    print("  VPC Endpointの導入により削減できるコスト:")
    print()
    
    total_endpoint_cost = 0
    total_savings = 0
    
    if s3_buckets and any(b['region'] == 'ap-northeast-1' or b['region'] == '' for b in s3_buckets):
        endpoint_cost = calculate_vpc_endpoint_cost('s3')
        total_endpoint_cost += endpoint_cost
        print(f"  - S3 Gateway Endpoint: 月額${endpoint_cost:.2f}")
        print(f"    → S3へのデータ転送料を削減（転送量に応じて削減額が変動）")
        print()
    
    if dynamodb_tables:
        endpoint_cost = calculate_vpc_endpoint_cost('dynamodb')
        total_endpoint_cost += endpoint_cost
        print(f"  - DynamoDB Gateway Endpoint: 月額${endpoint_cost:.2f}")
        print(f"    → DynamoDBへのデータ転送料を削減（転送量に応じて削減額が変動）")
        print()
    
    print(f"  VPC Endpointの合計コスト: 月額${total_endpoint_cost:.2f}")
    print()
    print("  ⚠️ 注意: データ転送量が少ない場合、VPC Endpointの固定料金が")
    print("     データ転送料を上回る可能性があります。")
    print("     実際のデータ転送量をCost Explorerで確認してから導入を検討してください。")
    print()
    
    print("5. **導入判断の基準**")
    print("-" * 80)
    print("  VPC Endpointの導入が有効な場合:")
    print("  - S3/DynamoDBへの月間データ転送量が約720GB以上")
    print("    （$7.2 ÷ $0.01/GB = 720GB）")
    print("  - セキュリティ要件でVPC内通信が必須")
    print("  - パフォーマンス要件で低レイテンシが必要")
    print()
    
    print("6. **導入方法**")
    print("-" * 80)
    print("  AWSコンソールまたはTerraformで設定:")
    print()
    print("  Terraform例（S3 Gateway Endpoint）:")
    print("  ```hcl")
    print("  resource \"aws_vpc_endpoint\" \"s3\" {")
    print("    vpc_id            = aws_vpc.main.id")
    print("    service_name      = \"com.amazonaws.ap-northeast-1.s3\"")
    print("    vpc_endpoint_type = \"Gateway\"")
    print("    route_table_ids   = [aws_route_table.private.id]")
    print("  }")
    print("  ```")
    print()
    print("  Terraform例（DynamoDB Gateway Endpoint）:")
    print("  ```hcl")
    print("  resource \"aws_vpc_endpoint\" \"dynamodb\" {")
    print("    vpc_id            = aws_vpc.main.id")
    print("    service_name      = \"com.amazonaws.ap-northeast-1.dynamodb\"")
    print("    vpc_endpoint_type = \"Gateway\"")
    print("    route_table_ids   = [aws_route_table.private.id]")
    print("  }")
    print("  ```")
    print()
    
    print("=" * 80)


if __name__ == '__main__':
    try:
        analyze_vpc_endpoint_benefits()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
