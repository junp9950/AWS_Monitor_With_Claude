import boto3
import json
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import pandas as pd

class AWSHealthService:
    def __init__(self, config_file: str = None, account_name: str = None):
        """
        AWS Health 서비스 클라이언트 초기화
        
        Args:
            config_file: AWS 계정 설정 파일 경로
            account_name: 사용할 계정 이름 (None이면 기본 계정 사용)
        """
        # 설정 파일 경로 자동 결정
        if config_file is None:
            # 현재 파일의 디렉토리에서 aws_config.json 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(current_dir, 'aws_config.json')
        
        self.config = self.load_aws_config(config_file)
        self.current_account = self.get_account_config(account_name)
        
        try:
            if self.current_account:
                # 설정 파일의 자격 증명 사용
                self.health_client = boto3.client(
                    'health',
                    region_name=self.current_account['region'],
                    aws_access_key_id=self.current_account['access_key_id'],
                    aws_secret_access_key=self.current_account['secret_access_key']
                )
                self.organizations_client = boto3.client(
                    'organizations',
                    region_name=self.current_account['region'],
                    aws_access_key_id=self.current_account['access_key_id'],
                    aws_secret_access_key=self.current_account['secret_access_key']
                )
                print(f"✅ AWS 계정 연결됨: {self.current_account['name']} ({self.current_account['description']})")
            else:
                # 기본 자격 증명 사용 (aws configure 또는 환경변수)
                self.health_client = boto3.client('health', region_name='us-east-1')
                self.organizations_client = boto3.client('organizations', region_name='us-east-1')
                print("⚠️ 기본 AWS 자격 증명 사용 중")
                
        except Exception as e:
            print(f"❌ AWS 클라이언트 초기화 실패: {e}")
            self.health_client = None
            self.organizations_client = None
    
    def load_aws_config(self, config_file: str) -> Dict:
        """
        AWS 설정 파일 로드
        
        Args:
            config_file: 설정 파일 경로
            
        Returns:
            설정 딕셔너리
        """
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 설정 파일 로드 실패: {e}")
                return {}
        else:
            print(f"⚠️ 설정 파일 없음: {config_file}")
            print("   aws_config.json.template을 복사하여 aws_config.json을 만들고 계정 정보를 입력하세요.")
            return {}
    
    def get_account_config(self, account_name: str = None) -> Dict:
        """
        특정 계정의 설정 정보 반환
        
        Args:
            account_name: 계정 이름 (None이면 기본 계정)
            
        Returns:
            계정 설정 딕셔너리
        """
        if not self.config or 'aws_accounts' not in self.config:
            return None
        
        # 계정 이름이 지정되지 않으면 기본 계정 사용
        if not account_name:
            account_name = self.config.get('default_account')
        
        # 해당 이름의 계정 찾기
        for account in self.config['aws_accounts']:
            if account['name'] == account_name:
                return account
        
        # 찾지 못하면 첫 번째 계정 반환
        if self.config['aws_accounts']:
            return self.config['aws_accounts'][0]
        
        return None
    
    def get_available_accounts(self) -> List[str]:
        """
        사용 가능한 AWS 계정 목록 반환
        
        Returns:
            계정 이름 리스트
        """
        if not self.config or 'aws_accounts' not in self.config:
            return []
        
        return [account['name'] for account in self.config['aws_accounts']]
    
    def get_service_health_events(self, days_back: int = 7) -> tuple[List[Dict], str]:
        """
        AWS 서비스 상태 이벤트 조회
        
        Args:
            days_back: 조회할 이전 일수
            
        Returns:
            (이벤트 리스트, 상태 메시지) 튜플
        """
        if not self.health_client:
            return [], "ERROR - AWS 클라이언트 초기화 실패"
        
        try:
            # 시간 범위 설정
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=days_back)
            
            # Health 이벤트 조회
            response = self.health_client.describe_events(
                filter={
                    'startTimes': [
                        {
                            'from': start_time,
                            'to': end_time
                        }
                    ],
                    'eventTypeCategories': ['issue', 'accountNotification', 'scheduledChange']
                }
            )
            
            events = []
            for event in response.get('events', []):
                event_detail = self._get_event_details(event['arn'])
                
                events.append({
                    'arn': event['arn'],
                    'service': event.get('service', 'Unknown'),
                    'event_type_category': event.get('eventTypeCategory', 'Unknown'),
                    'event_type_code': event.get('eventTypeCode', 'Unknown'),
                    'region': event.get('region', 'Global'),
                    'status': event.get('statusCode', 'Unknown'),
                    'start_time': event.get('startTime', ''),
                    'end_time': event.get('endTime', ''),
                    'last_updated_time': event.get('lastUpdatedTime', ''),
                    'description': event_detail.get('description', ''),
                    'affected_entities_count': self._count_affected_entities(event['arn'])
                })
            
            return events, "SUCCESS"
            
        except Exception as e:
            error_msg = str(e)
            print(f"Health 이벤트 조회 실패: {e}")
            
            # 구체적인 오류 분류
            if "Unable to locate credentials" in error_msg:
                return [], "ERROR - AWS 자격 증명 없음"
            elif "SubscriptionRequiredException" in error_msg:
                return [], "ERROR - Business/Enterprise 지원 플랜 필요"
            elif "AccessDenied" in error_msg:
                return [], "ERROR - Health API 접근 권한 없음"
            elif "InvalidUserID.NotFound" in error_msg:
                return [], "ERROR - 존재하지 않는 계정"
            else:
                return [], f"ERROR - API 호출 실패: {error_msg}"
    
    def _get_event_details(self, event_arn: str) -> Dict:
        """
        특정 이벤트의 상세 정보 조회
        
        Args:
            event_arn: 이벤트 ARN
            
        Returns:
            이벤트 상세 정보
        """
        try:
            response = self.health_client.describe_event_details(
                eventArns=[event_arn]
            )
            
            if response.get('successfulSet'):
                return response['successfulSet'][0].get('eventDescription', {})
            else:
                return {}
                
        except Exception as e:
            print(f"이벤트 상세 정보 조회 실패: {e}")
            return {}
    
    def _count_affected_entities(self, event_arn: str) -> int:
        """
        영향받은 엔티티 수 조회
        
        Args:
            event_arn: 이벤트 ARN
            
        Returns:
            영향받은 엔티티 수
        """
        try:
            response = self.health_client.describe_affected_entities(
                filter={
                    'eventArns': [event_arn]
                }
            )
            
            return len(response.get('entities', []))
            
        except Exception as e:
            print(f"영향받은 엔티티 수 조회 실패: {e}")
            return 0
    
    def get_health_summary(self) -> Dict:
        """
        AWS Health 전체 요약 정보 조회
        
        Returns:
            Health 요약 정보
        """
        events, status = self.get_service_health_events()
        
        # API 호출이 실패한 경우
        if status != "SUCCESS":
            return {
                'total_events': 0,
                'active_events': 0,
                'resolved_events': 0,
                'services_affected': 0,
                'regions_affected': 0,
                'critical_events': 0,
                'error_status': status,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
        
        # 성공했지만 이벤트가 없는 경우 (실제 정상 상태)
        if not events:
            return {
                'total_events': 0,
                'active_events': 0,
                'resolved_events': 0,
                'services_affected': 0,
                'regions_affected': 0,
                'critical_events': 0,
                'error_status': None,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
        
        df = pd.DataFrame(events)
        
        # 활성 이벤트 (종료 시간이 없는 이벤트)
        active_events = df[df['end_time'].isnull() | (df['end_time'] == '')].shape[0]
        resolved_events = df[~(df['end_time'].isnull() | (df['end_time'] == ''))].shape[0]
        
        # 영향받은 서비스 및 리전 수
        services_affected = df['service'].nunique()
        regions_affected = df[df['region'] != 'Global']['region'].nunique()
        
        # 중요 이벤트 (issue 카테고리)
        critical_events = df[df['event_type_category'] == 'issue'].shape[0]
        
        return {
            'total_events': len(events),
            'active_events': active_events,
            'resolved_events': resolved_events,
            'services_affected': services_affected,
            'regions_affected': regions_affected,
            'critical_events': critical_events,
            'error_status': None,
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    def get_events_by_service(self) -> Dict:
        """
        서비스별 이벤트 집계
        
        Returns:
            서비스별 이벤트 집계 정보
        """
        events, status = self.get_service_health_events()
        
        if status != "SUCCESS" or not events:
            return {}
        
        df = pd.DataFrame(events)
        service_counts = df.groupby('service').agg({
            'arn': 'count',
            'event_type_category': lambda x: (x == 'issue').sum()
        }).rename(columns={'arn': 'total_events', 'event_type_category': 'critical_events'})
        
        return service_counts.to_dict('index')
    
    def get_events_by_region(self) -> Dict:
        """
        리전별 이벤트 집계
        
        Returns:
            리전별 이벤트 집계 정보
        """
        events, status = self.get_service_health_events()
        
        if status != "SUCCESS" or not events:
            return {}
        
        df = pd.DataFrame(events)
        region_counts = df.groupby('region').agg({
            'arn': 'count',
            'event_type_category': lambda x: (x == 'issue').sum()
        }).rename(columns={'arn': 'total_events', 'event_type_category': 'critical_events'})
        
        return region_counts.to_dict('index')
    
    def check_account_specific_events(self) -> List[Dict]:
        """
        계정별 특정 이벤트 조회
        
        Returns:
            계정별 이벤트 리스트
        """
        if not self.health_client:
            return []
            
        try:
            response = self.health_client.describe_events(
                filter={
                    'eventTypeCategories': ['accountNotification']
                }
            )
            
            account_events = []
            for event in response.get('events', []):
                event_detail = self._get_event_details(event['arn'])
                
                account_events.append({
                    'arn': event['arn'],
                    'service': event.get('service', 'Account'),
                    'event_type_code': event.get('eventTypeCode', 'Unknown'),
                    'status': event.get('statusCode', 'Unknown'),
                    'start_time': event.get('startTime', ''),
                    'description': event_detail.get('description', ''),
                    'region': event.get('region', 'Global')
                })
            
            return account_events
            
        except Exception as e:
            print(f"계정별 이벤트 조회 실패: {e}")
            return []