#!/usr/bin/env python3
import boto3
import json
from botocore.exceptions import NoCredentialsError, ClientError

def check_aws_credentials():
    """AWS 자격 증명 확인"""
    print("🔍 AWS 자격 증명 확인 중...")
    
    try:
        # STS 클라이언트로 현재 자격 증명 확인
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print("✅ AWS 자격 증명 정상!")
        print(f"   계정 ID: {identity['Account']}")
        print(f"   사용자 ARN: {identity['Arn']}")
        print(f"   사용자 ID: {identity['UserId']}")
        return True
        
    except NoCredentialsError:
        print("❌ AWS 자격 증명이 설정되지 않았습니다!")
        print("   다음 방법 중 하나로 설정하세요:")
        print("   1. aws configure 명령어 사용")
        print("   2. 환경변수 설정 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print("   3. IAM 역할 사용")
        return False
        
    except Exception as e:
        print(f"❌ AWS 자격 증명 확인 실패: {e}")
        return False

def check_health_api_access():
    """Health API 접근 권한 확인"""
    print("\n🏥 AWS Health API 접근 권한 확인 중...")
    
    try:
        health = boto3.client('health', region_name='us-east-1')
        
        # Health 이벤트 조회 테스트
        response = health.describe_events(maxResults=1)
        
        print("✅ Health API 접근 성공!")
        print(f"   조회된 이벤트 수: {len(response.get('events', []))}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'SubscriptionRequiredException':
            print("❌ AWS Business/Enterprise 지원 플랜이 필요합니다!")
            print("   Health API는 Business 또는 Enterprise 지원 플랜에서만 사용 가능합니다.")
            print("   현재 Basic 지원 플랜을 사용 중인 것 같습니다.")
            
        elif error_code == 'AccessDenied':
            print("❌ Health API 접근 권한이 없습니다!")
            print("   필요한 IAM 권한:")
            print("   - health:DescribeEvents")
            print("   - health:DescribeEventDetails")
            print("   - health:DescribeAffectedEntities")
            
        else:
            print(f"❌ Health API 접근 실패: {error_code}")
            print(f"   오류 메시지: {e.response['Error']['Message']}")
            
        return False
        
    except Exception as e:
        print(f"❌ Health API 확인 중 오류: {e}")
        return False

def check_regions():
    """사용 가능한 AWS 리전 확인"""
    print("\n🌍 AWS 리전 확인 중...")
    
    try:
        ec2 = boto3.client('ec2', region_name='us-east-1')
        regions = ec2.describe_regions()['Regions']
        
        print(f"✅ 접근 가능한 리전 수: {len(regions)}")
        print("   주요 리전:")
        for region in regions[:5]:
            print(f"   - {region['RegionName']}")
        
        print("\n⚠️  주의: Health API는 us-east-1 리전에서만 사용 가능합니다!")
        return True
        
    except Exception as e:
        print(f"❌ 리전 확인 실패: {e}")
        return False

def main():
    print("🔧 AWS Health Dashboard 설정 확인")
    print("=" * 50)
    
    # 1. 자격 증명 확인
    creds_ok = check_aws_credentials()
    
    if creds_ok:
        # 2. Health API 접근 확인
        health_ok = check_health_api_access()
        
        # 3. 리전 확인
        regions_ok = check_regions()
        
        print("\n📋 확인 결과 요약:")
        print(f"   AWS 자격 증명: {'✅' if creds_ok else '❌'}")
        print(f"   Health API 접근: {'✅' if health_ok else '❌'}")
        print(f"   리전 접근: {'✅' if regions_ok else '❌'}")
        
        if creds_ok and health_ok and regions_ok:
            print("\n🎉 모든 설정이 완료되었습니다! 대시보드를 사용할 수 있습니다.")
        else:
            print("\n⚠️  일부 설정이 필요합니다. 위의 오류 메시지를 확인하세요.")
    
    else:
        print("\n🛠️  AWS 자격 증명을 먼저 설정하세요:")
        print("\n   방법 1: AWS CLI 사용")
        print("   aws configure")
        print("   AWS Access Key ID: [YOUR_ACCESS_KEY]")
        print("   AWS Secret Access Key: [YOUR_SECRET_KEY]")
        print("   Default region name: us-east-1")
        print("   Default output format: json")
        
        print("\n   방법 2: 환경변수 설정")
        print("   set AWS_ACCESS_KEY_ID=your_access_key")
        print("   set AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   set AWS_DEFAULT_REGION=us-east-1")

if __name__ == "__main__":
    main()