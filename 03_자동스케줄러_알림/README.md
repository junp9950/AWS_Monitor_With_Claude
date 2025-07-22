# 📁 03_자동스케줄러_알림

AWS Health 상태를 정기적으로 점검하고 자동으로 알림을 발송하는 스케줄러입니다.

## 📋 포함된 파일

- `health_scheduler.py` - 자동 점검 및 알림 스케줄러
- `health_config.json.template` - 알림 설정 템플릿
- `run_scheduler.bat` - 스케줄러 실행 스크립트

## 🚀 사용 방법

### 1단계: 알림 설정
```bash
copy health_config.json.template health_config.json
```

`health_config.json` 파일을 편집하여 알림 설정:

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "recipients": ["admin@company.com"]
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
```

### 2단계: 스케줄러 실행
```bash
run_scheduler.bat
```

## ⏰ 스케줄링 기능

### 📅 **일일 정기 점검**
- **실행 시간**: 매일 오전 9시 (설정 가능)
- **점검 내용**: 
  - 전체 AWS Health 상태 확인
  - 새로운 이벤트 감지
  - 중요도별 분류 및 집계
- **결과 발송**: 
  - 정상 상태: 일일 요약 이메일
  - 문제 감지: 경고 알림 이메일

### 🚨 **긴급 알림**
- **실행 주기**: 30분마다 (설정 가능)
- **감지 조건**: 
  - 새로운 중요 이슈 (issue 카테고리)
  - 활성 상태인 critical 이벤트
- **알림 방식**: 즉시 이메일 발송

## 📧 이메일 알림 기능

### ✅ **정상 상태 알림**
```
Subject: ✅ AWS Health 일일 점검 결과 - 정상

모든 시스템이 정상 상태입니다.
총 이벤트: 0개
활성 이벤트: 0개
중요 이슈: 0개
```

### ⚠️ **경고 알림**
```
Subject: ⚠️ AWS Health 일일 점검 결과 - 주의 필요

일부 시스템에 주의가 필요합니다.
총 이벤트: 3개
활성 이벤트: 2개
중요 이슈: 0개

상세 내용을 확인하여 조치하세요.
```

### 🚨 **긴급 알림**
```
Subject: 🚨 AWS Health 긴급 알림 - 즉시 확인 필요

새로운 중요 이벤트가 감지되었습니다!

서비스: EC2
리전: us-east-1
이벤트: AWS_EC2_INSTANCE_STORE_DRIVE_PERFORMANCE_DEGRADED
상태: open
시작 시간: 2024-01-15 10:30:00

즉시 AWS 콘솔에서 확인하세요.
```

## ⚙️ 설정 옵션

### 📬 **이메일 설정**
```json
"email": {
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com", 
  "sender_password": "your-app-password",
  "recipients": ["admin1@company.com", "admin2@company.com"]
}
```

### ⏰ **스케줄 설정**
```json
"schedule": {
  "daily_check_time": "09:00",        // 일일 점검 시간 (24시간)
  "urgent_check_interval": 30         // 긴급 점검 간격 (분)
}
```

### 🎯 **알림 임계값**
```json
"thresholds": {
  "max_critical_events": 0,           // 중요 이벤트 허용 개수
  "max_active_events": 5              // 활성 이벤트 허용 개수
}
```

## 📂 생성되는 파일

- `health_check.log` - 스케줄러 실행 로그
- 이메일 발송 기록

## 🔐 Gmail 설정 방법

Gmail 사용 시 앱 비밀번호 생성:
1. Google 계정 설정 → 보안
2. 2단계 인증 활성화
3. 앱 비밀번호 생성
4. 생성된 비밀번호를 설정 파일에 입력

## 🎯 활용 시나리오

- **무인 모니터링**: 24/7 자동 AWS Health 감시
- **조기 경보**: 중요 문제 발생 시 즉시 알림
- **정기 보고**: 매일 Health 상태 요약 제공
- **팀 협업**: 여러 관리자에게 동시 알림 발송