# BigQuery to Cosmos DB Data Pipeline

Azure Functions를 사용하여 Google BigQuery의 데이터를 Azure Cosmos DB로 이관하는 파이프라인입니다.

## 기능

- Google BigQuery 데이터 조회
- 데이터 변환 및 전처리
- Azure Cosmos DB 데이터 적재
- HTTP 트리거 기반 실행

## 시스템 요구사항

- Python 3.9 이상
- Azure Functions Core Tools v4
- Azure 구독
- Google Cloud Platform 계정
- Azure Cosmos DB 계정
- Google BigQuery 접근 권한

## 설치 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd secondprojectFunction
```

2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

## 환경 설정

1. Google Cloud Platform 설정
   - 서비스 계정 키 파일 (.json) 준비
   - 프로젝트 ID 및 데이터셋 접근 권한 확인

2. Azure Cosmos DB 설정
   - Cosmos DB 연결 문자열 준비
   - 데이터베이스 및 컨테이너 생성

3. 환경 변수 설정
   ```
   GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
   COSMOS_CONNECTION_STRING=your-cosmos-connection-string
   COSMOS_DATABASE_NAME=your-database-name
   COSMOS_CONTAINER_NAME=your-container-name
   ```

## 프로젝트 구조

```
secondprojectFunction/
├── host.json                 # Azure Functions 호스트 설정
├── requirements.txt          # Python 의존성 목록
└── storeToCosmos/           # 함수 앱 디렉토리
    ├── __init__.py          # 함수 진입점
    ├── function.json        # 함수 바인딩 설정
    ├── clients.py           # 클라이언트 구현
    ├── config.py            # 설정 관리
    ├── data_processors.py   # 데이터 처리 로직
    ├── models.py            # 데이터 모델
    ├── queries.py           # BigQuery 쿼리
    ├── time_utils.py        # 시간 관련 유틸리티
    └── utils.py             # 일반 유틸리티
```

## 로컬 실행 방법

1. Azure Functions Core Tools 실행
```bash
func start
```

2. 함수 테스트
```bash
curl http://localhost:7071/api/storeToCosmos
```

## 배포 방법

1. Azure Functions 앱 생성 (Azure Portal 또는 CLI 사용)

2. 배포 실행
```bash
func azure functionapp publish [function-app-name]
```

## 문제 해결

문제 발생 시 `troubleshooting_log.txt` 파일을 참고하세요. 이 파일에는 일반적인 문제와 해결 방법이 기록되어 있습니다.

## 보안 고려사항

- 서비스 계정 키는 절대 버전 관리에 포함하지 마세요
- 환경 변수나 Azure Key Vault를 사용하여 비밀 정보 관리
- 함수 앱의 인증 수준은 "function" 으로 설정되어 있음

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.