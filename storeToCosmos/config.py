import os
import logging

# ===== 환경 설정 =====
SERVICE_ACCOUNT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'service_account_key.json')
)

# 환경 변수 검증
def validate_environment():
    """환경 변수를 검증합니다."""
    required_vars = ["COSMOS_CONN_STRING", "COSMOS_DB_NAME"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"❌ 누락된 환경 변수: {', '.join(missing_vars)}")
    
    # 서비스 계정 파일 확인
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        raise FileNotFoundError(f"❌ 서비스 계정 파일을 찾을 수 없습니다: {SERVICE_ACCOUNT_PATH}")

# 환경 변수 로드
try:
    validate_environment()
    COSMOS_CONN_STRING = os.environ["COSMOS_CONN_STRING"]
    COSMOS_DB_NAME = os.environ["COSMOS_DB_NAME"]
    logging.info("✅ 환경 변수 검증 완료")
except Exception as e:
    logging.error(f"❌ 환경 변수 검증 실패: {e}")
    raise

# Cosmos DB 컨테이너 이름들
CONTAINER_NAMES = {
    "sessions": "Sessions",
    "totals": "Totals",
    "traffic": "TrafficSource",
    "devicegeo": "DeviceAndGeo",
    "custom": "CustomDimensions",
    "hits": "Hits",
    "products": "HitsProduct"
}

# BigQuery 설정
BQ_PROJECT_ID = "ms-team-project"
BQ_DATASET = "bigquery-public-data.google_analytics_sample"
BQ_TABLE_PREFIX = "ga_sessions_"
BQ_DATE_SUFFIX = "20170801"
BQ_LIMIT = 100 