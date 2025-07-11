# 🚀 BigQuery → CosmosDB 데이터 전송 Azure Function

Google Analytics 데이터를 BigQuery에서 조회하여 Azure CosmosDB에 저장하는 Azure Function입니다.

## 📁 프로젝트 구조

```
storeToCosmos/
├── __init__.py          # 메인 Azure Function
├── config.py            # 설정 관리
├── clients.py           # 클라이언트 초기화
├── queries.py           # BigQuery 쿼리
├── data_processors.py   # 데이터 처리 로직
├── models.py            # 데이터 모델
├── utils.py             # 유틸리티 함수
├── time_utils.py        # 시간 처리 유틸리티
└── function.json        # Azure Function 설정
```

## 🔧 모듈 설명

### `config.py`
- 환경 변수 및 설정 관리
- CosmosDB 컨테이너 이름 정의
- BigQuery 설정

### `clients.py`
- BigQuery 및 CosmosDB 클라이언트 초기화
- `ClientManager` 클래스로 클라이언트 관리

### `queries.py`
- BigQuery 쿼리 정의
- `BigQueryQueries` 클래스로 쿼리 관리

### `data_processors.py`
- BigQuery 데이터를 CosmosDB로 변환
- `DataProcessor` 클래스로 데이터 처리

### `models.py`
- 데이터 모델 정의 (dataclass 사용)
- `DataModels` 팩토리 클래스

### `utils.py`
- 성능 모니터링
- 에러 처리
- 로깅 유틸리티

## 🚀 사용법

### 1. 환경 변수 설정
```bash
COSMOS_CONN_STRING=your_cosmos_connection_string
COSMOS_DB_NAME=your_database_name
```

### 2. 서비스 계정 키 설정
`service_account_key.json` 파일을 프로젝트 루트에 배치

### 3. 함수 실행
```bash
func start
```

## 📊 처리되는 데이터

| 컨테이너 | 설명 |
|---------|------|
| Sessions | 세션 정보 |
| Totals | 총계 데이터 |
| TrafficSource | 트래픽 소스 |
| DeviceAndGeo | 디바이스 및 지리 정보 |
| CustomDimensions | 커스텀 차원 |
| Hits | 페이지 히트 |
| HitsProduct | 제품 히트 |

## 🔍 주요 기능

- ✅ BigQuery에서 Google Analytics 데이터 조회
- ✅ CosmosDB에 구조화된 데이터 저장
- ✅ 시간대 변환 (UTC → LA)
- ✅ 에러 처리 및 로깅
- ✅ 성능 모니터링
- ✅ 모듈화된 구조

## 📈 성능 최적화

- 클라이언트 재사용
- 배치 처리
- 메모리 효율적인 데이터 처리
- 비동기 처리 지원

## 🛠️ 개발 환경

- Python 3.8+
- Azure Functions Core Tools
- Google Cloud BigQuery
- Azure CosmosDB

## 📝 로그 예시

```
🚀 Azure Function Triggered: BigQuery → CosmosDB
⏱️ 데이터 처리 실행 시간: 2.34초
✅ 저장 완료:
  • sessions: 100개
  • totals: 100개
  • traffic: 100개
  • devicegeo: 100개
  • custom: 50개
  • hits: 500개
  • products: 200개
``` 