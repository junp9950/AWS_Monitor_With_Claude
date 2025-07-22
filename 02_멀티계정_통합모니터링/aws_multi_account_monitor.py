#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '00_공통설정'))

import json
import pandas as pd
from datetime import datetime, timezone
from aws_health_service import AWSHealthService
import time
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aws_multi_account_monitor.log'),
        logging.StreamHandler()
    ]
)

class AWSMultiAccountMonitor:
    def __init__(self, config_file=None):
        """
        AWS 멀티 계정 모니터링 클라이언트 초기화
        
        Args:
            config_file: AWS 설정 파일 경로 (None이면 자동 탐색)
        """
        # 설정 파일 경로 자동 결정
        if config_file is None:
            # 00_공통설정 폴더의 aws_config.json 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            config_file = os.path.join(parent_dir, '00_공통설정', 'aws_config.json')
        
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """설정 파일 로드"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            logging.info(f"설정 파일 로드 완료: {len(self.config.get('aws_accounts', []))}개 계정")
        except Exception as e:
            logging.error(f"설정 파일 로드 실패: {e}")
            self.config = {}
    
    def get_all_accounts_health(self, days_back=7):
        """
        모든 AWS 계정의 Health 상태 조회
        
        Args:
            days_back: 조회할 이전 일수
            
        Returns:
            계정별 Health 데이터 딕셔너리
        """
        all_accounts_data = {}
        accounts = self.config.get('aws_accounts', [])
        
        if not accounts:
            logging.warning("설정된 AWS 계정이 없습니다.")
            return {}
        
        logging.info(f"=== {len(accounts)}개 AWS 계정 Health 점검 시작 ===")
        
        for account in accounts:
            account_name = account['name']
            logging.info(f"📋 {account_name} 계정 점검 중...")
            
            try:
                # 계정별 Health 서비스 초기화
                health_service = AWSHealthService(account_name=account_name)
                
                # Health 데이터 수집
                summary = health_service.get_health_summary()
                events, event_status = health_service.get_service_health_events(days_back)
                
                # 오류 상태 확인
                if summary.get('error_status'):
                    # API 호출 실패
                    account_data = {
                        'account_info': account,
                        'summary': summary,
                        'events': [],
                        'services': {},
                        'regions': {},
                        'account_events': [],
                        'check_time': datetime.now().isoformat(),
                        'status': 'error',
                        'error': summary['error_status']
                    }
                    logging.error(f"❌ {account_name}: {summary['error_status']}")
                    
                else:
                    # 정상 처리
                    account_data = {
                        'account_info': account,
                        'summary': summary,
                        'events': events,
                        'services': health_service.get_events_by_service(),
                        'regions': health_service.get_events_by_region(),
                        'account_events': health_service.check_account_specific_events(),
                        'check_time': datetime.now().isoformat(),
                        'status': 'success'
                    }
                    
                    # 요약 정보 로깅
                    if summary['critical_events'] > 0:
                        logging.warning(f"🚨 {account_name}: 중요 이슈 {summary['critical_events']}개 감지!")
                    elif summary['active_events'] > 0:
                        logging.info(f"⚠️ {account_name}: 활성 이벤트 {summary['active_events']}개")
                    else:
                        logging.info(f"✅ {account_name}: 정상 상태")
                
                all_accounts_data[account_name] = account_data
                
            except Exception as e:
                logging.error(f"❌ {account_name} 점검 실패: {e}")
                all_accounts_data[account_name] = {
                    'account_info': account,
                    'status': 'error',
                    'error': str(e),
                    'check_time': datetime.now().isoformat()
                }
            
            # 계정 간 간격 (API 제한 방지)
            time.sleep(1)
        
        logging.info("=== 모든 계정 점검 완료 ===")
        return all_accounts_data
    
    def generate_consolidated_report(self, all_accounts_data):
        """
        통합 보고서 생성
        
        Args:
            all_accounts_data: 모든 계정의 Health 데이터
            
        Returns:
            통합 보고서 딕셔너리
        """
        total_accounts = len(all_accounts_data)
        healthy_accounts = 0
        warning_accounts = 0
        critical_accounts = 0
        error_accounts = 0
        
        total_events = 0
        total_critical_events = 0
        total_active_events = 0
        
        account_summary = []
        
        for account_name, data in all_accounts_data.items():
            if data['status'] == 'error':
                error_accounts += 1
                account_summary.append({
                    'account': account_name,
                    'status': 'ERROR',
                    'critical_events': 0,
                    'active_events': 0,
                    'total_events': 0,
                    'error': data.get('error', 'Unknown error')
                })
                continue
            
            summary = data['summary']
            total_events += summary['total_events']
            total_critical_events += summary['critical_events']
            total_active_events += summary['active_events']
            
            # 계정 상태 분류
            if summary['critical_events'] > 0:
                critical_accounts += 1
                status = 'CRITICAL'
            elif summary['active_events'] > 0:
                warning_accounts += 1
                status = 'WARNING'
            else:
                healthy_accounts += 1
                status = 'HEALTHY'
            
            account_summary.append({
                'account': account_name,
                'status': status,
                'critical_events': summary['critical_events'],
                'active_events': summary['active_events'],
                'total_events': summary['total_events'],
                'services_affected': summary['services_affected'],
                'regions_affected': summary['regions_affected']
            })
        
        return {
            'check_time': datetime.now().isoformat(),
            'total_accounts': total_accounts,
            'healthy_accounts': healthy_accounts,
            'warning_accounts': warning_accounts,
            'critical_accounts': critical_accounts,
            'error_accounts': error_accounts,
            'total_events': total_events,
            'total_critical_events': total_critical_events,
            'total_active_events': total_active_events,
            'account_summary': account_summary,
            'overall_status': self.get_overall_status(critical_accounts, warning_accounts, error_accounts)
        }
    
    def get_overall_status(self, critical_accounts, warning_accounts, error_accounts):
        """
        전체 상태 판단
        
        Args:
            critical_accounts: 중요 이슈가 있는 계정 수
            warning_accounts: 경고가 있는 계정 수
            error_accounts: 오류가 있는 계정 수
            
        Returns:
            전체 상태 문자열
        """
        if critical_accounts > 0 or error_accounts > 0:
            return 'CRITICAL'
        elif warning_accounts > 0:
            return 'WARNING'
        else:
            return 'HEALTHY'
    
    def print_console_report(self, consolidated_report):
        """
        콘솔용 보고서 출력
        
        Args:
            consolidated_report: 통합 보고서
        """
        print("\n" + "="*80)
        print("🔍 AWS 멀티 계정 Health 점검 결과")
        print("="*80)
        
        # 전체 요약
        print(f"📊 전체 요약:")
        print(f"   총 계정: {consolidated_report['total_accounts']}개")
        print(f"   정상: {consolidated_report['healthy_accounts']}개")
        print(f"   경고: {consolidated_report['warning_accounts']}개")
        print(f"   중요: {consolidated_report['critical_accounts']}개")
        print(f"   오류: {consolidated_report['error_accounts']}개")
        print()
        
        # 전체 상태
        status = consolidated_report['overall_status']
        status_emoji = {"HEALTHY": "✅", "WARNING": "⚠️", "CRITICAL": "🚨"}
        print(f"🎯 전체 상태: {status_emoji.get(status, '❓')} {status}")
        print()
        
        # 계정별 상세
        print("📋 계정별 상세:")
        print("-"*80)
        print(f"{'계정명':<20} {'상태':<10} {'중요':<6} {'활성':<6} {'총계':<6} {'서비스':<8} {'리전':<6}")
        print("-"*80)
        
        for account in consolidated_report['account_summary']:
            status_emoji = {
                'HEALTHY': '✅',
                'WARNING': '⚠️', 
                'CRITICAL': '🚨',
                'ERROR': '❌'
            }
            
            emoji = status_emoji.get(account['status'], '❓')
            
            if account['status'] == 'ERROR':
                print(f"{account['account']:<20} {emoji} ERROR    -     -     -     -       -")
                print(f"    오류: {account['error']}")
            else:
                print(f"{account['account']:<20} {emoji} {account['status']:<8} "
                      f"{account['critical_events']:<6} {account['active_events']:<6} "
                      f"{account['total_events']:<6} {account['services_affected']:<8} "
                      f"{account['regions_affected']:<6}")
        
        print("-"*80)
        print(f"점검 시간: {consolidated_report['check_time']}")
        print("="*80)
    
    def save_report_to_file(self, consolidated_report, filename=None):
        """
        보고서를 파일로 저장
        
        Args:
            consolidated_report: 통합 보고서
            filename: 저장할 파일명 (None이면 자동 생성)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"aws_health_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(consolidated_report, f, indent=2, ensure_ascii=False)
            logging.info(f"보고서 저장 완료: {filename}")
        except Exception as e:
            logging.error(f"보고서 저장 실패: {e}")
    
    def run_full_check(self, days_back=7, save_report=True):
        """
        전체 점검 실행
        
        Args:
            days_back: 조회할 이전 일수
            save_report: 보고서 파일 저장 여부
        """
        logging.info("AWS 멀티 계정 Health 점검 시작")
        
        # 모든 계정 점검
        all_accounts_data = self.get_all_accounts_health(days_back)
        
        # 통합 보고서 생성
        consolidated_report = self.generate_consolidated_report(all_accounts_data)
        
        # 콘솔 출력
        self.print_console_report(consolidated_report)
        
        # 파일 저장
        if save_report:
            self.save_report_to_file(consolidated_report)
        
        return consolidated_report

def main():
    """메인 실행 함수"""
    monitor = AWSMultiAccountMonitor()
    
    # 전체 점검 실행
    report = monitor.run_full_check(days_back=7, save_report=True)
    
    # 중요 이슈가 있으면 별도 알림
    if report['overall_status'] == 'CRITICAL':
        logging.warning("🚨 중요한 이슈가 감지되었습니다. 즉시 확인이 필요합니다!")
    elif report['overall_status'] == 'WARNING':
        logging.info("⚠️ 일부 계정에 주의가 필요한 이벤트가 있습니다.")
    else:
        logging.info("✅ 모든 계정이 정상 상태입니다.")

if __name__ == "__main__":
    main()