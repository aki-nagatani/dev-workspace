#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
おたよりナビ AWSリソース存在確認スクリプト
S3バケット、EC2、RDS、Secrets Managerの存在を確認する
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


def check_s3_buckets():
    """S3バケットの存在確認"""
    print("【S3バケット確認】")
    print("-" * 80)
    
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    
    # 確認対象のバケット名
    expected_buckets = [
        'otayori-navi-md',      # Markdown用
        'otayori-navi-pdf',     # PDF用
        'otayori-navi-bucket',  # 統合バケット（設定例）
    ]
    
    try:
        # 全バケット一覧を取得
        response = s3.list_buckets()
        existing_buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
        
        # otayori-navi関連のバケットを検索
        otayori_buckets = [b for b in existing_buckets if 'otayori' in b.lower()]
        
        print(f"  確認対象バケット:")
        for bucket_name in expected_buckets:
            exists = bucket_name in existing_buckets
            status = "✅ 存在" if exists else "❌ 不存在"
            print(f"    {bucket_name}: {status}")
        
        if otayori_buckets:
            print(f"\n  その他のotayori-navi関連バケット:")
            for bucket_name in otayori_buckets:
                if bucket_name not in expected_buckets:
                    print(f"    - {bucket_name}")
        
        # バケット詳細情報を取得
        for bucket_name in expected_buckets:
            if bucket_name in existing_buckets:
                try:
                    # バケットの設定を確認
                    versioning = s3.get_bucket_versioning(Bucket=bucket_name)
                    encryption = s3.get_bucket_encryption(Bucket=bucket_name)
                    public_access = s3.get_public_access_block(Bucket=bucket_name)
                    
                    print(f"\n  [{bucket_name} 詳細設定]")
                    print(f"    バージョニング: {versioning.get('Status', '無効')}")
                    print(f"    暗号化: {encryption.get('ServerSideEncryptionConfiguration', {}).get('Rules', [{}])[0].get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm', 'N/A')}")
                    public_block = public_access.get('PublicAccessBlockConfiguration', {})
                    print(f"    パブリックアクセスブロック: {public_block.get('BlockPublicAcls', False)}")
                except Exception as e:
                    print(f"    設定取得エラー: {e}")
        
        print()
        return {
            'expected': expected_buckets,
            'existing': existing_buckets,
            'otayori_buckets': otayori_buckets
        }
        
    except Exception as e:
        print(f"  Error: S3バケットの取得に失敗しました: {e}")
        print()
        return {}


def check_ec2_instances():
    """EC2インスタンスの存在確認（FishTrackと共有）"""
    print("【EC2インスタンス確認】")
    print("-" * 80)
    
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    try:
        response = ec2.describe_instances()
        
        instances_info = []
        running_instances = []
        
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId', 'N/A')
                state = instance.get('State', {}).get('Name', 'N/A')
                instance_type = instance.get('InstanceType', 'N/A')
                
                # タグから名前を取得
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                name = tags.get('Name', 'N/A')
                
                # IAMロールを取得
                iam_profile = instance.get('IamInstanceProfile', {})
                iam_role_arn = iam_profile.get('Arn', 'N/A') if iam_profile else 'N/A'
                
                # セキュリティグループ
                security_groups = [sg['GroupName'] for sg in instance.get('SecurityGroups', [])]
                
                # パブリックIP
                public_ip = instance.get('PublicIpAddress', 'N/A')
                
                instance_info = {
                    'id': instance_id,
                    'name': name,
                    'state': state,
                    'type': instance_type,
                    'iam_role': iam_role_arn,
                    'security_groups': security_groups,
                    'public_ip': public_ip
                }
                
                instances_info.append(instance_info)
                
                # 実行中のインスタンスのみ表示
                if state == 'running':
                    running_instances.append(instance_info)
                    print(f"  インスタンスID: {instance_id}")
                    print(f"    名前: {name}")
                    print(f"    ステータス: {state}")
                    print(f"    インスタンスタイプ: {instance_type}")
                    print(f"    パブリックIP: {public_ip}")
                    print(f"    IAMロール: {iam_role_arn}")
                    print(f"    セキュリティグループ: {', '.join(security_groups)}")
                    print()
        
        if not running_instances:
            print("  実行中のEC2インスタンスが見つかりませんでした。")
            print()
        
        print(f"  実行中: {len(running_instances)} 台")
        print(f"  停止中: {len(instances_info) - len(running_instances)} 台")
        print()
        
        return {
            'all': instances_info,
            'running': running_instances
        }
        
    except Exception as e:
        print(f"  Error: EC2インスタンスの取得に失敗しました: {e}")
        print()
        return {}


def check_rds_instances():
    """RDSインスタンスの存在確認（FishTrackと共有）"""
    print("【RDSインスタンス確認】")
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
            endpoint = instance.get('Endpoint', {})
            endpoint_address = endpoint.get('Address', 'N/A')
            endpoint_port = endpoint.get('Port', 'N/A')
            db_name = instance.get('DBName', 'N/A')
            
            # タグから環境情報を取得
            tags_response = rds.list_tags_for_resource(ResourceName=instance['DBInstanceArn'])
            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
            
            instance_info = {
                'id': db_id,
                'status': status,
                'class': instance_class,
                'engine': engine,
                'version': engine_version,
                'endpoint': endpoint_address,
                'port': endpoint_port,
                'db_name': db_name,
                'tags': tags
            }
            
            rds_info.append(instance_info)
            
            print(f"  DB識別子: {db_id}")
            print(f"    ステータス: {status}")
            print(f"    インスタンスクラス: {instance_class}")
            print(f"    エンジン: {engine} {engine_version}")
            print(f"    エンドポイント: {endpoint_address}:{endpoint_port}")
            print(f"    データベース名: {db_name}")
            print()
        
        return rds_info
        
    except Exception as e:
        print(f"  Error: RDSインスタンスの取得に失敗しました: {e}")
        print()
        return []


def check_secrets_manager():
    """Secrets Managerの存在確認"""
    print("【Secrets Manager確認】")
    print("-" * 80)
    
    secrets_client = boto3.client('secretsmanager', region_name='ap-northeast-1')
    
    # 確認対象のシークレット名
    expected_secrets = [
        'otayori/web-secret',           # セッション秘密鍵
        'otayori/db-url',              # RDS接続情報
        'ai/api-key',                  # AI APIキー
        'onedrive/client-id',          # OneDrive Client ID
        'onedrive/client-secret',      # OneDrive Client Secret
        'onedrive/refresh-token',      # OneDrive Refresh Token
    ]
    
    try:
        # 全シークレット一覧を取得
        response = secrets_client.list_secrets()
        existing_secrets = [secret['Name'] for secret in response.get('SecretList', [])]
        
        # otayori-navi関連のシークレットを検索
        otayori_secrets = [s for s in existing_secrets if 'otayori' in s.lower() or 'ai/api-key' in s.lower() or 'onedrive' in s.lower()]
        
        print(f"  確認対象シークレット:")
        for secret_name in expected_secrets:
            exists = secret_name in existing_secrets
            status = "✅ 存在" if exists else "❌ 不存在"
            print(f"    {secret_name}: {status}")
        
        if otayori_secrets:
            print(f"\n  その他のotayori-navi関連シークレット:")
            for secret_name in otayori_secrets:
                if secret_name not in expected_secrets:
                    print(f"    - {secret_name}")
        
        # シークレットの詳細情報を取得（存在する場合）
        for secret_name in expected_secrets:
            if secret_name in existing_secrets:
                try:
                    secret_info = secrets_client.describe_secret(SecretId=secret_name)
                    description = secret_info.get('Description', 'N/A')
                    last_changed = secret_info.get('LastChangedDate', 'N/A')
                    print(f"\n  [{secret_name} 詳細]")
                    print(f"    説明: {description}")
                    print(f"    最終更新: {last_changed}")
                except Exception as e:
                    print(f"    詳細取得エラー: {e}")
        
        print()
        return {
            'expected': expected_secrets,
            'existing': existing_secrets,
            'otayori_secrets': otayori_secrets
        }
        
    except Exception as e:
        print(f"  Error: Secrets Managerの取得に失敗しました: {e}")
        print()
        return {}


def check_iam_roles():
    """IAMロールの権限確認（EC2用）"""
    print("【IAMロール権限確認】")
    print("-" * 80)
    
    iam = boto3.client('iam', region_name='ap-northeast-1')
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    # 必要な権限
    required_permissions = [
        'textract:DetectDocumentText',
        's3:GetObject',
        's3:PutObject',
        's3:ListBucket',
        'secretsmanager:GetSecretValue',
    ]
    
    try:
        # 実行中のEC2インスタンスのIAMロールを取得
        response = ec2.describe_instances()
        instance_profiles = set()
        
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                if instance.get('State', {}).get('Name') == 'running':
                    iam_profile = instance.get('IamInstanceProfile', {})
                    if iam_profile:
                        profile_arn = iam_profile.get('Arn', '')
                        instance_profiles.add(profile_arn)
        
        if not instance_profiles:
            print("  実行中のEC2インスタンスのIAMロールが見つかりませんでした。")
            print()
            return {}
        
        print(f"  確認対象IAMロール: {len(instance_profiles)} 個")
        
        for profile_arn in instance_profiles:
            print(f"\n  [{profile_arn}]")
            
            # プロファイル名を抽出
            profile_name = profile_arn.split('/')[-1]
            
            try:
                # インスタンスプロファイルのロールを取得
                profile_response = iam.get_instance_profile(InstanceProfileName=profile_name)
                roles = profile_response.get('InstanceProfile', {}).get('Roles', [])
                
                for role in roles:
                    role_name = role.get('RoleName', 'N/A')
                    print(f"    ロール名: {role_name}")
                    
                    # ロールのポリシーを取得
                    attached_policies = iam.list_attached_role_policies(RoleName=role_name)
                    inline_policies = iam.list_role_policies(RoleName=role_name)
                    
                    # インラインポリシーを取得
                    all_permissions = set()
                    
                    # アタッチされたポリシー
                    for policy in attached_policies.get('AttachedPolicies', []):
                        policy_arn = policy['PolicyArn']
                        policy_version = iam.get_policy(PolicyArn=policy_arn)
                        default_version = policy_version['Policy']['DefaultVersionId']
                        policy_doc = iam.get_policy_version(PolicyArn=policy_arn, VersionId=default_version)
                        
                        statements = policy_doc['PolicyVersion']['Document'].get('Statement', [])
                        for stmt in statements:
                            actions = stmt.get('Action', [])
                            if isinstance(actions, str):
                                actions = [actions]
                            all_permissions.update(actions)
                    
                    # インラインポリシー
                    for policy_name in inline_policies.get('PolicyNames', []):
                        policy_doc = iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                        statements = policy_doc['PolicyDocument'].get('Statement', [])
                        for stmt in statements:
                            actions = stmt.get('Action', [])
                            if isinstance(actions, str):
                                actions = [actions]
                            all_permissions.update(actions)
                    
                    # 必要な権限の確認
                    print(f"    必要な権限:")
                    for perm in required_permissions:
                        # ワイルドカード対応（例: s3:* は s3:GetObject を含む）
                        has_permission = False
                        for existing_perm in all_permissions:
                            if perm == existing_perm:
                                has_permission = True
                                break
                            elif '*' in existing_perm:
                                # ワイルドカードマッチング
                                prefix = existing_perm.split(':')[0]
                                if perm.startswith(prefix + ':'):
                                    has_permission = True
                                    break
                        
                        status = "✅" if has_permission else "❌"
                        print(f"      {status} {perm}")
                    
            except Exception as e:
                print(f"    権限取得エラー: {e}")
        
        print()
        return {}
        
    except Exception as e:
        print(f"  Error: IAMロールの取得に失敗しました: {e}")
        print()
        return {}


def generate_summary(s3_result, ec2_result, rds_result, secrets_result):
    """確認結果のサマリーを生成"""
    print("=" * 80)
    print("【確認結果サマリー】")
    print("=" * 80)
    print()
    
    # S3バケット
    if s3_result:
        expected_buckets = s3_result.get('expected', [])
        existing_buckets = s3_result.get('existing', [])
        missing_buckets = [b for b in expected_buckets if b not in existing_buckets]
        
        print("S3バケット:")
        if missing_buckets:
            print(f"  ❌ 不足しているバケット: {', '.join(missing_buckets)}")
        else:
            print(f"  ✅ 必要なバケットはすべて存在します")
        print()
    
    # EC2インスタンス
    if ec2_result:
        running = ec2_result.get('running', [])
        if running:
            print(f"EC2インスタンス:")
            print(f"  ✅ 実行中: {len(running)} 台")
            for inst in running:
                print(f"    - {inst['id']} ({inst['name']})")
        else:
            print(f"EC2インスタンス:")
            print(f"  ❌ 実行中のインスタンスが見つかりません")
        print()
    
    # RDSインスタンス
    if rds_result:
        if rds_result:
            print(f"RDSインスタンス:")
            print(f"  ✅ {len(rds_result)} 台のインスタンスが見つかりました")
            for rds in rds_result:
                print(f"    - {rds['id']} ({rds['engine']} {rds['version']})")
                print(f"      エンドポイント: {rds['endpoint']}:{rds['port']}")
        else:
            print(f"RDSインスタンス:")
            print(f"  ❌ RDSインスタンスが見つかりません")
        print()
    
    # Secrets Manager
    if secrets_result:
        expected_secrets = secrets_result.get('expected', [])
        existing_secrets = secrets_result.get('existing', [])
        missing_secrets = [s for s in expected_secrets if s not in existing_secrets]
        
        print("Secrets Manager:")
        if missing_secrets:
            print(f"  ❌ 不足しているシークレット: {', '.join(missing_secrets)}")
        else:
            print(f"  ✅ 必要なシークレットはすべて存在します")
        print()
    
    print("=" * 80)


def main():
    print("=" * 80)
    print("おたよりナビ AWSリソース存在確認")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    s3_result = check_s3_buckets()
    ec2_result = check_ec2_instances()
    rds_result = check_rds_instances()
    secrets_result = check_secrets_manager()
    iam_result = check_iam_roles()
    
    generate_summary(s3_result, ec2_result, rds_result, secrets_result)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
