import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '00_공통설정'))

import schedule
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from aws_health_service import AWSHealthService
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_check.log'),
        logging.StreamHandler()
    ]
)

class HealthScheduler:
    def __init__(self, config_file='health_config.json'):
        """
        Health 스케줄러 초기화
        
        Args:
            config_file: 설정 파일 경로
        """
        self.config = self.load_config(config_file)
        self.health_service = AWSHealthService()
        self.last_events = []
    
    def load_config(self, config_file):
        """
        설정 파일 로드
        
        Args:
            config_file: 설정 파일 경로
            
        Returns:
            설정 딕셔너리
        """
        default_config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",
                "sender_password": "",
                "recipients": []
            },
            "slack": {
                "webhook_url": "",
                "channel": "#aws-health"
            },
            "schedule": {
                "daily_check_time": "09:00",
                "urgent_check_interval": 30
            },
            "thresholds": {
                "max_critical_events": 0,
                "max_active_events": 5
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 기본값과 병합
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
            except Exception as e:
                logging.error(f"설정 파일 로드 실패: {e}")
                return default_config
        else:
            # 기본 설정 파일 생성
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            logging.info(f"기본 설정 파일 생성됨: {config_file}")
            return default_config
    
    def daily_health_check(self):
        """
        일일 정기 점검 수행
        """
        logging.info("일일 Health 점검 시작")
        
        try:
            # Health 데이터 수집
            summary = self.health_service.get_health_summary()
            events = self.health_service.get_service_health_events(days_back=1)
            
            # 점검 결과 생성
            report = self.generate_daily_report(summary, events)
            
            # 알림 발송 여부 결정
            if self.should_send_alert(summary):
                self.send_alert(report, "일일 Health 점검 결과 - 주의 필요")
            else:
                self.send_daily_summary(report)
            
            # 마지막 이벤트 업데이트
            self.last_events = events
            
            logging.info("일일 Health 점검 완료")
            
        except Exception as e:
            logging.error(f"일일 점검 중 오류 발생: {e}")
            self.send_error_alert(str(e))
    
    def urgent_health_check(self):
        """
        긴급 점검 수행 (새로운 중요 이벤트 감지)
        """
        try:
            current_events = self.health_service.get_service_health_events(days_back=1)
            
            # 새로운 중요 이벤트 감지
            new_critical_events = self.detect_new_critical_events(current_events)
            
            if new_critical_events:
                logging.warning(f"새로운 중요 이벤트 {len(new_critical_events)}개 감지")
                
                report = self.generate_urgent_report(new_critical_events)
                self.send_alert(report, "🚨 AWS Health 긴급 알림 - 즉시 확인 필요")
                
                # 마지막 이벤트 업데이트
                self.last_events = current_events
            
        except Exception as e:
            logging.error(f"긴급 점검 중 오류 발생: {e}")
    
    def detect_new_critical_events(self, current_events):
        """
        새로운 중요 이벤트 감지
        
        Args:
            current_events: 현재 이벤트 목록
            
        Returns:
            새로운 중요 이벤트 목록
        """
        if not self.last_events:
            return []
        
        # 기존 이벤트 ARN 목록
        last_event_arns = {event['arn'] for event in self.last_events}
        
        # 새로운 중요 이벤트 필터링
        new_critical_events = []
        for event in current_events:
            if (event['arn'] not in last_event_arns and 
                event['event_type_category'] == 'issue' and
                event['status'] == 'open'):
                new_critical_events.append(event)
        
        return new_critical_events
    
    def should_send_alert(self, summary):
        """
        알림 발송 여부 결정
        
        Args:
            summary: Health 요약 정보
            
        Returns:
            알림 발송 여부
        """
        thresholds = self.config['thresholds']
        
        return (summary['critical_events'] > thresholds['max_critical_events'] or
                summary['active_events'] > thresholds['max_active_events'])
    
    def generate_daily_report(self, summary, events):
        """
        일일 점검 보고서 생성
        
        Args:
            summary: Health 요약 정보
            events: 이벤트 목록
            
        Returns:
            HTML 형식의 보고서
        """
        status_emoji = "✅" if summary['critical_events'] == 0 else "🚨"
        
        html_report = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; 
                         background-color: #e9ecef; border-radius: 8px; }}
                .critical {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
                .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; }}
                .success {{ background-color: #d1edff; border-left: 4px solid #0084ff; }}
                .event {{ margin: 10px 0; padding: 10px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{status_emoji} AWS Health 일일 점검 결과</h1>
                <p><strong>점검 시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h2>📊 전체 요약</h2>
            <div>
                <div class="metric">
                    <strong>총 이벤트:</strong> {summary['total_events']}
                </div>
                <div class="metric">
                    <strong>활성 이벤트:</strong> {summary['active_events']}
                </div>
                <div class="metric">
                    <strong>중요 이슈:</strong> {summary['critical_events']}
                </div>
                <div class="metric">
                    <strong>영향받은 서비스:</strong> {summary['services_affected']}
                </div>
            </div>
        """
        
        if summary['critical_events'] > 0:
            html_report += """
            <div class="critical">
                <h3>🚨 중요 이슈</h3>
                <p>즉시 확인이 필요한 중요한 이슈가 있습니다.</p>
            </div>
            """
        
        if events:
            html_report += "<h2>📋 최근 이벤트</h2>"
            for event in events[:10]:  # 최대 10개 이벤트만 표시
                event_class = "critical" if event['event_type_category'] == 'issue' else "warning"
                html_report += f"""
                <div class="event {event_class}">
                    <strong>{event['service']}</strong> - {event['region']}<br>
                    <em>{event['event_type_code']}</em><br>
                    <small>{event['start_time']}</small>
                </div>
                """
        
        html_report += """
            <hr>
            <p><small>이 보고서는 자동으로 생성되었습니다. 문제가 있을 경우 AWS 콘솔에서 직접 확인해주세요.</small></p>
        </body>
        </html>
        """
        
        return html_report
    
    def generate_urgent_report(self, critical_events):
        """
        긴급 알림 보고서 생성
        
        Args:
            critical_events: 새로운 중요 이벤트 목록
            
        Returns:
            HTML 형식의 긴급 보고서
        """
        html_report = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .urgent {{ background-color: #f8d7da; padding: 20px; border-radius: 8px; 
                          border-left: 4px solid #dc3545; }}
                .event {{ margin: 15px 0; padding: 15px; background-color: #fff; 
                         border-radius: 4px; border-left: 3px solid #dc3545; }}
            </style>
        </head>
        <body>
            <div class="urgent">
                <h1>🚨 AWS Health 긴급 알림</h1>
                <p><strong>감지 시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>새로운 중요 이벤트:</strong> {len(critical_events)}개</p>
            </div>
            
            <h2>⚠️ 즉시 확인이 필요한 이벤트</h2>
        """
        
        for event in critical_events:
            html_report += f"""
            <div class="event">
                <h3>{event['service']} - {event['region']}</h3>
                <p><strong>이벤트 유형:</strong> {event['event_type_code']}</p>
                <p><strong>상태:</strong> {event['status']}</p>
                <p><strong>시작 시간:</strong> {event['start_time']}</p>
                <p><strong>설명:</strong> {event['description'][:200]}...</p>
            </div>
            """
        
        html_report += """
            <hr>
            <p><strong>권장 조치:</strong></p>
            <ul>
                <li>AWS 콘솔에서 상세 정보 확인</li>
                <li>영향받은 리소스 점검</li>
                <li>필요시 관련 팀에 알림</li>
                <li>복구 계획 실행</li>
            </ul>
        </body>
        </html>
        """
        
        return html_report
    
    def send_alert(self, message, subject):
        """
        알림 이메일 발송
        
        Args:
            message: 메시지 내용
            subject: 이메일 제목
        """
        email_config = self.config['email']
        
        if not email_config['sender_email'] or not email_config['recipients']:
            logging.warning("이메일 설정이 없어 알림을 보낼 수 없습니다.")
            return
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = email_config['sender_email']
            msg['To'] = ', '.join(email_config['recipients'])
            
            html_part = MIMEText(message, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender_email'], email_config['sender_password'])
                server.send_message(msg)
            
            logging.info("알림 이메일 발송 완료")
            
        except Exception as e:
            logging.error(f"이메일 발송 실패: {e}")
    
    def send_daily_summary(self, report):
        """
        일일 요약 발송 (정상 상태일 때)
        """
        self.send_alert(report, "✅ AWS Health 일일 점검 결과 - 정상")
    
    def send_error_alert(self, error_message):
        """
        오류 알림 발송
        """
        error_report = f"""
        <html>
        <body>
            <h1>🔥 AWS Health 점검 오류</h1>
            <p><strong>오류 시간:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>오류 내용:</strong> {error_message}</p>
            <p>점검 시스템에 문제가 발생했습니다. 수동으로 AWS Health를 확인해주세요.</p>
        </body>
        </html>
        """
        self.send_alert(error_report, "🔥 AWS Health 점검 시스템 오류")
    
    def start_scheduler(self):
        """
        스케줄러 시작
        """
        # 일일 정기 점검 스케줄
        daily_time = self.config['schedule']['daily_check_time']
        schedule.every().day.at(daily_time).do(self.daily_health_check)
        
        # 긴급 점검 스케줄 (30분마다)
        urgent_interval = self.config['schedule']['urgent_check_interval']
        schedule.every(urgent_interval).minutes.do(self.urgent_health_check)
        
        logging.info(f"스케줄러 시작됨 - 일일 점검: {daily_time}, 긴급 점검: {urgent_interval}분마다")
        
        # 초기 점검 실행
        self.daily_health_check()
        
        # 스케줄 실행
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    scheduler = HealthScheduler()
    scheduler.start_scheduler()