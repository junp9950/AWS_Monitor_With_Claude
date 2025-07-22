# 🔍 AWS Health Dashboard

**매일 반복되는 AWS Health Dashboard 점검 업무를 자동화!**

Azure 스타일의 직관적인 웹 대시보드로 AWS Health 상태를 편리하게 모니터링하고, 일일 점검을 자동화하는 솔루션입니다.

## 📁 프로젝트 구성

### 📂 [00_공통설정](./00_공통설정)
- AWS 계정 설정 파일 및 공통 서비스
- `aws_config.json` - AWS 계정 정보
- `aws_health_service.py` - Health API 연동 서비스
- `requirements.txt` - Python 패키지 의존성

### 📂 [01_단일계정_기본점검](./01_단일계정_기본점검)  
- 단일 AWS 계정 Health 상태 점검
- 웹 대시보드로 실시간 모니터링
- 포트: `http://localhost:8501`

### 📂 [02_멀티계정_통합모니터링](./02_멀티계정_통합모니터링)
- 여러 AWS 계정을 통합 모니터링
- 콘솔 기반 + 웹 대시보드 제공  
- 포트: `http://localhost:8502`

### 📂 [03_자동스케줄러_알림](./03_자동스케줄러_알림)
- 정기적 자동 점검 및 이메일 알림
- 일일 점검 + 긴급 알림 기능
- 24/7 무인 모니터링

## ✨ 주요 기능

### 🎯 핵심 기능
- **일일 자동 점검**: 매일 정해진 시간에 AWS Health 상태 자동 점검
- **실시간 모니터링**: Azure 스타일의 직관적인 웹 대시보드
- **긴급 알림**: 새로운 중요 이벤트 감지 시 즉시 알림
- **이메일 리포트**: 일일 점검 결과를 이메일로 자동 발송
- **필터링 및 검색**: 이벤트 상태, 기간별 필터링 지원

### 📊 대시보드 구성
- **전체 상태 요약**: 총 이벤트, 활성 이벤트, 중요 이슈 수
- **이벤트 목록**: 최근 이벤트의 상세 정보
- **서비스별 차트**: 서비스별 이벤트 발생 현황
- **리전별 분포**: 리전별 이벤트 분포 시각화
- **계정별 알림**: 계정 관련 특별 알림

## 🚀 빠른 시작

### 1. 사전 요구사항

#### AWS 설정
- **AWS Business/Enterprise 지원 플랜**: Health API 사용을 위해 필수
- **AWS CLI 설치 및 설정**:
  ```bash
  aws configure
  ```
- **필요한 IAM 권한**:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "health:DescribeEvents",
          "health:DescribeEventDetails",
          "health:DescribeAffectedEntities"
        ],
        "Resource": "*"
      }
    ]
  }
  ```

#### Python 환경
- Python 3.8 이상
- pip 패키지 관리자

### 2. 설치 및 설정

#### 2.1 패키지 설치
```bash
# 가상환경 생성 (권장)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 필요한 패키지 설치
pip install -r requirements_aws.txt
```

#### 2.2 설정 파일 생성
```bash
# 설정 파일 템플릿 복사
copy health_config.json.template health_config.json
```

#### 2.3 설정 파일 수정
`health_config.json` 파일을 열어 다음 정보를 입력:

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password",
    "recipients": [
      "admin@company.com"
    ]
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

### 3. 실행 방법

#### 3.1 웹 대시보드 실행
```bash
# 배치 파일 실행 (Windows)
run_health_dashboard.bat

# 또는 직접 실행
streamlit run aws_health_dashboard.py
```

브라우저에서 `http://localhost:8501`로 접속

#### 3.2 일일 점검 스케줄러 실행
```bash
# 배치 파일 실행 (Windows)
run_scheduler.bat

# 또는 직접 실행
python health_scheduler.py
```

## 📋 사용법

### 🖥️ 웹 대시보드 기능

#### 메인 화면
- **상태 요약 카드**: 총 이벤트, 활성 이벤트, 중요 이슈 등 핵심 지표
- **전체 상태 알림**: 시스템 상태에 따른 색상별 알림
- **최근 이벤트 목록**: 필터링 가능한 이벤트 테이블

#### 사이드바 옵션
- **자동 새로고침**: 30초마다 자동 데이터 갱신
- **조회 기간**: 1일, 3일, 7일, 14일, 30일 선택
- **필터링**:
  - 해결된 이벤트 포함/제외
  - 예정된 변경사항 포함/제외

#### 차트 분석
- **서비스별 이벤트**: 어떤 AWS 서비스에서 이벤트가 많이 발생하는지 확인
- **리전별 분포**: 지역별 이벤트 발생 현황

### 📧 자동 알림 기능

#### 일일 정기 점검
- **실행 시간**: 설정 파일에서 지정한 시간 (기본: 오전 9시)
- **점검 내용**: 
  - 전체 AWS Health 상태 확인
  - 새로운 이벤트 감지
  - 중요도별 분류
- **결과 발송**: 
  - 정상 상태: 일일 요약 이메일
  - 문제 감지: 경고 알림 이메일

#### 긴급 알림
- **실행 주기**: 30분마다 (설정 변경 가능)
- **감지 조건**: 
  - 새로운 중요 이슈 (issue 카테고리)
  - 활성 상태인 이벤트
- **알림 방식**: 즉시 이메일 발송

### 🔧 상세 설정

#### 알림 임계값 설정
```json
"thresholds": {
  "max_critical_events": 0,    // 중요 이벤트 허용 개수
  "max_active_events": 5       // 활성 이벤트 허용 개수
}
```

#### 스케줄 설정
```json
"schedule": {
  "daily_check_time": "09:00",     // 일일 점검 시간 (24시간 형식)
  "urgent_check_interval": 30      // 긴급 점검 간격 (분)
}
```

## 🔐 보안 및 권한

### AWS IAM 권한
AWS Health API 사용을 위해 다음 권한이 필요합니다:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "health:DescribeEvents",
        "health:DescribeEventDetails", 
        "health:DescribeAffectedEntities"
      ],
      "Resource": "*"
    }
  ]
}
```

### 이메일 보안
Gmail 사용 시 앱 비밀번호 생성 방법:
1. Google 계정 설정 → 보안
2. 2단계 인증 활성화
3. 앱 비밀번호 생성
4. 생성된 비밀번호를 설정 파일에 입력

## 💰 비용 정보

### AWS Health API
- **Business/Enterprise 지원 플랜 필요**: 월 $100+ (Business 플랜 기준)
- **API 호출 비용**: Health API 자체는 무료
- **지원 플랜이 없는 경우**: 제한된 Health 정보만 제공

### 운영 비용
- **컴퓨팅 리소스**: 미미한 수준 (Python 스크립트)
- **네트워크**: AWS API 호출에 따른 데이터 전송료 (매우 적음)

## 🛠️ 문제 해결

### 일반적인 오류

#### 1. AWS 자격 증명 오류
```
NoCredentialsError: Unable to locate credentials
```
**해결방법**:
```bash
aws configure
# 또는
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

#### 2. Health API 접근 권한 오류
```
AccessDenied: User is not authorized to perform: health:DescribeEvents
```
**해결방법**:
- Business/Enterprise 지원 플랜 가입 확인
- IAM 권한 추가
- 리전이 `us-east-1`인지 확인

#### 3. 이메일 발송 실패
```
SMTPAuthenticationError: Username and Password not accepted
```
**해결방법**:
- Gmail 앱 비밀번호 사용
- SMTP 설정 확인
- 방화벽/보안 소프트웨어 확인

#### 4. 패키지 설치 오류
```bash
# 가상환경에서 재설치
pip install --upgrade pip
pip install -r requirements_aws.txt --force-reinstall
```

### 로그 확인
스케줄러 실행 시 `health_check.log` 파일에서 상세 로그 확인:
```bash
tail -f health_check.log
```

## 📊 사용 예시

### 일일 점검 시나리오
1. **오전 9시**: 자동 점검 실행
2. **정상 상태**: "✅ 모든 시스템 정상" 이메일 수신
3. **이상 감지**: "🚨 중요 이슈 감지" 이메일 수신

### 긴급 상황 대응
1. **새로운 중요 이벤트 발생**
2. **30분 이내 긴급 알림 수신**
3. **웹 대시보드에서 상세 정보 확인**
4. **필요한 조치 수행**

## 🔄 업그레이드 및 확장

### 향후 개선 계획
- Slack 알림 연동
- 모바일 앱 알림
- 다중 AWS 계정 지원
- 커스텀 알림 규칙
- 히스토리 데이터 분석

### 커스터마이징
- **알림 템플릿 수정**: `health_scheduler.py`의 보고서 생성 함수
- **대시보드 UI 변경**: `aws_health_dashboard.py`의 CSS 스타일
- **새로운 차트 추가**: Plotly를 이용한 추가 시각화

## 📞 지원 및 문의

문제 발생 시:
1. 로그 파일 확인 (`health_check.log`)
2. AWS 콘솔에서 Health Dashboard 직접 확인
3. IAM 권한 및 지원 플랜 상태 확인

## 📝 라이선스

이 프로젝트는 기존 Azure 모니터링 프로젝트의 확장으로 MIT 라이선스를 따릅니다.

---

**🎯 이제 매일 반복되는 AWS Health Dashboard 점검 업무가 자동화됩니다!**
- 웹 대시보드로 편리한 조회
- 자동 일일 점검 및 알림
- 긴급 상황 즉시 감지
- Azure 스타일의 직관적인 UI