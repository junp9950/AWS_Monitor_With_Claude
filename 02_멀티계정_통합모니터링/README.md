# 📁 02_멀티계정_통합모니터링

여러 AWS 계정의 Health 상태를 통합하여 모니터링하는 도구들입니다.

## 📋 포함된 파일

### 🖥️ **콘솔 기반 도구**
- `aws_multi_account_monitor.py` - 멀티 계정 콘솔 모니터링
- `run_multi_account_check.bat` - 콘솔 점검 실행 스크립트

### 🌐 **웹 대시보드**
- `aws_multi_dashboard.py` - 멀티 계정 웹 대시보드
- `run_multi_dashboard.bat` - 웹 대시보드 실행 스크립트

## 🚀 사용 방법

### 콘솔 기반 점검
```bash
run_multi_account_check.bat
```

**출력 예시:**
```
================================
🔍 AWS 멀티 계정 Health 점검 결과
================================
📊 전체 요약:
   총 계정: 3개
   정상: 2개  
   경고: 1개
   중요: 0개

📋 계정별 상세:
Production_Account   ✅ HEALTHY   0  0  0  0  0
Development_Account  ⚠️ WARNING   0  2  3  1  1  
Test_Account        ✅ HEALTHY   0  0  0  0  0
```

### 웹 대시보드
```bash
run_multi_dashboard.bat
```
브라우저에서 `http://localhost:8502` 접속

## ✨ 주요 기능

### 📊 **통합 모니터링**
- 모든 AWS 계정을 한번에 점검
- 계정별 상태 요약 (정상/경고/중요/오류)
- 전체 Health 상태 종합 판단

### 🔍 **상세 분석**  
- 계정별 필터링 (정상/경고/중요/오류)
- 이벤트 상세 정보 토글
- 계정 상태 분포 차트
- 계정별 이벤트 수 비교

### 📈 **통계 및 차트**
- 계정 상태 분포 파이 차트
- 계정별 이벤트 수 막대 차트  
- 실시간 데이터 업데이트

### 📝 **자동 보고서**
- JSON 형식 상세 보고서 생성
- 타임스탬프 기반 파일명
- 로그 파일 자동 기록

## 🎯 Azure 스타일 기능

Azure 백업 모니터링과 동일한 방식으로:
- 설정 파일 기반 계정 관리
- 순차적 계정 순회 점검
- 통합된 결과 보고서
- 상태별 계정 분류

## 📂 생성되는 파일

- `aws_health_report_YYYYMMDD_HHMMSS.json` - 상세 보고서
- `aws_multi_account_monitor.log` - 점검 로그

## 🔄 자동화 활용

이 도구들은 스케줄러나 CI/CD 파이프라인에서 활용 가능합니다:
- Jenkins, GitHub Actions 등에서 정기 실행
- 결과를 Slack, Teams 등으로 전송
- 임계값 기반 알림 발송