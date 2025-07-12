import os
import logging

# Azure Functions는 환경 변수를 자동으로 local.settings.json에서 로드합니다
# 따라서 별도의 dotenv 로드가 필요하지 않습니다

# BigQuery 설정 (하드코딩)
SERVICE_ACCOUNT_PATH = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
BQ_DATASET = "bigquery-public-data.google_analytics_sample"
BQ_TABLE_PREFIX = "ga_sessions_"
BQ_DATE_SUFFIX = "20170801"
BQ_LIMIT = 1000

# Azure SQL Database 설정 (환경 변수에서 로드)
SQL_SERVER = os.environ['SQL_SERVER']  # 예: your-server.database.windows.net
SQL_DATABASE = os.environ['SQL_DATABASE']
SQL_USERNAME = os.environ['SQL_USERNAME']
SQL_PASSWORD = os.environ['SQL_PASSWORD']

# Azure AD 인증 사용 시 필요한 설정 (선택적)
# AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
# AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
# AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')

# 배치 설정 (하드코딩)
BATCH_SIZE = 100 