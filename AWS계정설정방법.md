# 🔧 AWS 계정 설정 방법

## 1️⃣ 설정 파일 생성

```bash
# 템플릿 파일을 복사하여 실제 설정 파일 생성
copy aws_config.json.template aws_config.json
```

## 2️⃣ AWS 액세스 키 생성

### AWS Management Console에서:

1. **IAM 콘솔 접속**: https://console.aws.amazon.com/iam/
2. **사용자 메뉴** → **보안 자격 증명**
3. **액세스 키** → **액세스 키 만들기**
4. **사용 사례 선택**: "Command Line Interface (CLI)"
5. **액세스 키 생성** 완료
6. **액세스 키 ID**와 **비밀 액세스 키** 복사 📋

### ⚠️ 보안 주의사항:
- 액세스 키는 안전한 곳에 보관
- 절대 Git에 커밋하지 말 것
- 정기적으로 키 교체 권장

## 3️⃣ 설정 파일 수정

`aws_config.json` 파일을 열어서 다음 정보를 입력:

```json
{
  "aws_accounts": [
    {
      "name": "Production_Account",
      "description": "메인 프로덕션 계정",
      "access_key_id": "AKIA여기에실제액세스키입력",
      "secret_access_key": "여기에실제시크릿키입력",
      "region": "us-east-1"
    }
  ],
  "default_account": "Production_Account",
  "health_settings": {
    "check_interval_minutes": 30,
    "days_back": 7,
    "include_resolved": false,
    "include_scheduled": true
  }
}
```

### 📝 필드 설명:
- **name**: 계정을 구분하는 이름 (자유롭게 설정)
- **description**: 계정 설명 (자유롭게 설정)
- **access_key_id**: AWS 액세스 키 ID (AKIA로 시작)
- **secret_access_key**: AWS 비밀 액세스 키
- **region**: 반드시 `us-east-1` (Health API 전용 리전)

## 4️⃣ 권한 설정

### 필요한 IAM 권한:
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

### IAM 정책 생성 방법:
1. **IAM 콘솔** → **정책** → **정책 생성**
2. **JSON** 탭 선택
3. 위의 JSON 내용 붙여넣기
4. **정책 검토** → 이름: `AWSHealthReadOnly`
5. **사용자**에 정책 연결

## 5️⃣ 지원 플랜 확인

### ⚠️ 중요: AWS Business/Enterprise 지원 플랜 필요!

**현재 플랜 확인 방법:**
1. AWS Console → **Support** → **Support Center**
2. 우측 상단에 현재 플랜 표시

**플랜별 Health API 접근:**
- ❌ **Basic**: Health API 사용 불가
- ✅ **Developer**: 제한적 접근  
- ✅ **Business**: 완전 접근 (월 $100+)
- ✅ **Enterprise**: 완전 접근 (월 $15,000+)

## 6️⃣ 테스트

```bash
# 설정 완료 후 테스트
python check_aws_setup.py

# 대시보드 실행
run_health_dashboard.bat
```

### 성공 시 출력:
```
✅ AWS 계정 연결됨: Production_Account (메인 프로덕션 계정)
✅ Health API 접근 성공!
```

## 7️⃣ 여러 계정 사용하기

```json
{
  "aws_accounts": [
    {
      "name": "Production",
      "description": "프로덕션 환경",
      "access_key_id": "AKIA프로덕션키",
      "secret_access_key": "프로덕션시크릿키",
      "region": "us-east-1"
    },
    {
      "name": "Development", 
      "description": "개발 환경",
      "access_key_id": "AKIA개발키",
      "secret_access_key": "개발시크릿키",
      "region": "us-east-1"
    }
  ],
  "default_account": "Production"
}
```

대시보드 사이드바에서 계정을 선택하여 전환 가능합니다.

## 🛠️ 문제 해결

### "Unable to locate credentials" 오류:
- aws_config.json 파일이 존재하는지 확인
- 액세스 키가 올바른지 확인
- 파일 경로가 올바른지 확인

### "SubscriptionRequiredException" 오류:
- AWS Business/Enterprise 지원 플랜 필요
- 현재 Basic 플랜 사용 중

### "AccessDenied" 오류:
- IAM 권한 확인
- health:* 권한 추가 필요

---

**🎯 설정 완료 후 매일 AWS Health 점검이 자동화됩니다!**