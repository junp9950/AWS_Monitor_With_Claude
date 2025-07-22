# 📁 00_공통설정

모든 AWS Health 모니터링 도구에서 공통으로 사용하는 설정 파일들과 서비스입니다.

## 📋 포함된 파일

### 🔧 **필수 설정 파일**
- `aws_config.json` - AWS 계정 정보 설정 파일
- `aws_config.json.template` - 설정 파일 템플릿
- `requirements.txt` - Python 패키지 의존성

### 🛠️ **공통 서비스**
- `aws_health_service.py` - AWS Health API 연동 서비스
- `check_aws_setup.py` - AWS 설정 상태 확인 도구

## 🚀 최초 설정 방법

### 1단계: 설정 파일 생성
```bash
copy aws_config.json.template aws_config.json
```

### 2단계: AWS 계정 정보 입력
`aws_config.json` 파일을 편집하여 실제 AWS 계정 정보를 입력:

```json
{
  "aws_accounts": [
    {
      "name": "Production_Account",
      "description": "프로덕션 환경",
      "access_key_id": "AKIA실제액세스키",
      "secret_access_key": "실제시크릿키",
      "region": "us-east-1"
    }
  ],
  "default_account": "Production_Account"
}
```

### 3단계: AWS 설정 확인
```bash
python check_aws_setup.py
```

## ⚠️ 중요 사항

- **보안**: `aws_config.json` 파일은 절대 Git에 커밋하지 마세요
- **지원 플랜**: AWS Business/Enterprise 지원 플랜이 필요합니다
- **리전**: Health API는 `us-east-1` 리전에서만 동작합니다
- **권한**: `health:*` IAM 권한이 필요합니다

## 📞 문제 해결

설정 관련 문제는 `check_aws_setup.py`를 실행하여 진단하세요.