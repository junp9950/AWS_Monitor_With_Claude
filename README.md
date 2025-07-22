# 🔍 AWS Health Dashboard

**매일 반복되는 AWS Health Dashboard 점검 업무를 완전 자동화!**

Azure 스타일의 직관적인 웹 대시보드로 AWS Health 상태를 편리하게 모니터링하고, 일일 점검을 자동화하는 통합 솔루션입니다.

## 📁 프로젝트 구성

### 📂 [00_공통설정](./00_공통설정)
- **AWS 계정 설정 및 공통 서비스**
- `aws_config.json` - AWS 계정 정보 설정
- `aws_health_service.py` - Health API 연동 서비스
- `requirements.txt` - Python 패키지 의존성

### 📂 [01_단일계정_기본점검](./01_단일계정_기본점검)  
- **단일 AWS 계정 Health 상태 점검**
- 웹 대시보드로 실시간 모니터링
- **접속**: `http://localhost:8501`

### 📂 [02_멀티계정_통합모니터링](./02_멀티계정_통합모니터링)
- **여러 AWS 계정을 통합 모니터링**
- 콘솔 기반 + 웹 대시보드 제공  
- **접속**: `http://localhost:8502`

### 📂 [03_자동스케줄러_알림](./03_자동스케줄러_알림)
- **정기적 자동 점검 및 이메일 알림**
- 일일 점검 + 긴급 알림 기능
- 24/7 무인 모니터링

## ✨ 주요 기능

### 🎯 **핵심 기능**
- **일일 자동 점검**: 매일 정해진 시간에 AWS Health 상태 자동 점검
- **실시간 모니터링**: Azure 스타일의 직관적인 웹 대시보드
- **긴급 알림**: 새로운 중요 이벤트 감지 시 즉시 알림
- **이메일 리포트**: 일일 점검 결과를 이메일로 자동 발송
- **필터링 및 검색**: 이벤트 상태, 기간별 필터링 지원

### 📊 **대시보드 구성**
- **전체 상태 요약**: 총 이벤트, 활성 이벤트, 중요 이슈 수
- **이벤트 목록**: 최근 이벤트의 상세 정보
- **서비스별 차트**: 서비스별 이벤트 발생 현황
- **리전별 분포**: 리전별 이벤트 분포 시각화
- **계정별 알림**: 계정 관련 특별 알림

### 🔄 **Azure 스타일 멀티 계정 지원**
- **설정 파일 기반**: `aws_config.json`으로 여러 계정 관리
- **순차적 점검**: 모든 계정을 자동으로 순회하며 점검
- **통합 보고서**: 전체 계정의 상태를 한눈에 확인
- **오류 감지**: 인증 실패, 권한 부족, 지원 플랜 문제 등 정확한 진단

## 🚀 빠른 시작

### 1️⃣ **사전 요구사항**
- **Python 3.8+**
- **AWS Business/Enterprise 지원 플랜** (Health API 사용 필수)
- **AWS 액세스 키** (IAM 권한: `health:*`)

### 2️⃣ **설치**
```bash
# 저장소 클론
git clone https://github.com/junp9950/AWS_Monitor_With_Claude.git
cd AWS_Monitor_With_Claude

# AWS 계정 설정
cd 00_공통설정
copy aws_config.json.template aws_config.json
# aws_config.json 파일을 열어 실제 AWS 계정 정보 입력
```

### 3️⃣ **실행**

#### **단일 계정 모니터링**
```bash
cd 01_단일계정_기본점검
run_health_dashboard.bat
```
브라우저에서 `http://localhost:8501` 접속

#### **멀티 계정 모니터링** ⭐
```bash
cd 02_멀티계정_통합모니터링
run_multi_dashboard.bat
```
브라우저에서 `http://localhost:8502` 접속

#### **자동 스케줄러**
```bash
cd 03_자동스케줄러_알림
run_scheduler.bat
```

## ⚙️ 설정 파일 예시

### **AWS 계정 설정** (`00_공통설정/aws_config.json`)
```json
{
  "aws_accounts": [
    {
      "name": "Production_Account",
      "description": "프로덕션 환경",
      "access_key_id": "AKIA실제액세스키",
      "secret_access_key": "실제시크릿키",
      "region": "us-east-1"
    },
    {
      "name": "Development_Account", 
      "description": "개발 환경",
      "access_key_id": "AKIA개발계정키",
      "secret_access_key": "개발계정시크릿키",
      "region": "us-east-1"
    }
  ],
  "default_account": "Production_Account"
}
```

### **알림 설정** (`03_자동스케줄러_알림/health_config.json`)
```json
{
  "email": {
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

## 💰 비용 정보

### **AWS Health API 요구사항**
- **Basic 지원 플랜**: ❌ Health API 사용 불가
- **Business 플랜**: ✅ 월 $100+ (완전한 Health API 접근)
- **Enterprise 플랜**: ✅ 월 $15,000+ (완전한 Health API 접근)

### **운영 비용**
- Health API 자체: 무료
- 컴퓨팅 리소스: 미미한 수준
- 네트워크: AWS API 호출 데이터 전송료 (매우 적음)

## 🛠️ 주요 특징

### ✅ **정확한 오류 감지**
- `❌ ERROR - AWS 자격 증명 없음`
- `❌ ERROR - Business/Enterprise 지원 플랜 필요`
- `❌ ERROR - Health API 접근 권한 없음`
- `❌ ERROR - 존재하지 않는 계정`

### ✅ **자동 임시 파일 정리**
- 패키지 설치 시 생성되는 임시 폴더 자동 삭제
- Python 캐시 파일 자동 정리
- 로그 파일 관리

### ✅ **보안 강화**
- `.gitignore`로 민감한 정보 자동 제외
- AWS 액세스 키 안전 관리
- 템플릿 파일 제공으로 설정 가이드

## 🔧 문제 해결

### **일반적인 오류**

#### 1. **"Unable to locate credentials"**
```bash
# 해결방법: AWS 계정 설정 확인
cd 00_공통설정
notepad aws_config.json
```

#### 2. **"Business/Enterprise 지원 플랜 필요"**
- AWS 지원 플랜 업그레이드 필요
- Basic 플랜에서는 Health API 사용 불가

#### 3. **"ModuleNotFoundError: boto3"**
```bash
# 해결방법: 패키지 설치
pip install -r requirements.txt
```

#### 4. **한글 인코딩 오류 (Windows)**
- 배치 파일에 `chcp 65001` 추가됨
- UTF-8 인코딩으로 자동 설정

## 📈 사용 시나리오

### **일일 운영 시나리오**
1. **오전 9시**: 자동 스케줄러가 모든 계정 점검
2. **정상 상태**: "✅ 모든 시스템 정상" 이메일 수신
3. **이상 감지**: "🚨 중요 이슈 감지" 이메일 즉시 수신
4. **웹 대시보드**: 실시간으로 상세 정보 확인

### **긴급 상황 대응**
1. **새로운 중요 이벤트 발생**
2. **30분 이내 긴급 알림 수신**
3. **멀티 계정 대시보드에서 영향 범위 확인**
4. **계정별 상세 분석 및 조치**

## 🎯 Azure 백업 모니터링과의 차이점

| 구분 | Azure 백업 모니터링 | AWS Health 모니터링 |
|------|-------------------|-------------------|
| **대상** | Azure 백업 작업 상태 | AWS 서비스 전반 Health 상태 |
| **API** | Azure Management API | AWS Health API |
| **지원 플랜** | 기본 제공 | Business/Enterprise 필요 |
| **모니터링** | 백업 성공/실패 | 서비스 장애, 유지보수, 보안 |
| **알림** | 백업 실패 시 | Health 이벤트 발생 시 |

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다.

## 🤝 기여 및 지원

- **버그 리포트**: GitHub Issues
- **기능 요청**: Pull Request 환영
- **문의사항**: GitHub Discussions

## 📞 개발자

🔍 **Generated with [Claude Code](https://claude.ai/code)**

**Co-Authored-By**: Claude <noreply@anthropic.com>

---

**🎉 이제 매일 반복되는 AWS Health Dashboard 점검 업무가 완전히 자동화됩니다!**

- ✅ **Azure 스타일** 직관적 대시보드
- ✅ **멀티 계정** 통합 모니터링  
- ✅ **자동 스케줄러** 일일 점검
- ✅ **실시간 알림** 긴급 상황 대응
- ✅ **정확한 진단** 오류 상태 감지