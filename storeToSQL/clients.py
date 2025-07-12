from google.cloud import bigquery
from google.oauth2 import service_account
from azure.identity import DefaultAzureCredential
import pyodbc
import logging
from .config import (
    SERVICE_ACCOUNT_PATH,
    SQL_SERVER,
    SQL_DATABASE,
    SQL_USERNAME,
    SQL_PASSWORD,
    BATCH_SIZE
)

class ClientManager:
    """BigQuery와 Azure SQL Database 클라이언트를 관리하는 클래스"""
    
    def __init__(self):
        self._bq_client = None
        self._sql_conn = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """클라이언트들을 초기화합니다."""
        # BigQuery 클라이언트 초기화
        bq_credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)
        self._bq_client = bigquery.Client(credentials=bq_credentials, project=bq_credentials.project_id)
        
        # Azure SQL Database 클라이언트 초기화
        try:
            # Azure 인증 정보 가져오기 (Managed Identity 지원)
            azure_credential = DefaultAzureCredential()
            
            # SQL Database 연결 문자열 생성 (Microsoft 공식 문서 형식)
            conn_str = f"Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{SQL_SERVER},1433;Database={SQL_DATABASE};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
            
            # SQL Database 연결
            self._sql_conn = pyodbc.connect(conn_str)
            self._sql_conn.autocommit = False  # 트랜잭션 사용
            
            logging.info("Azure SQL Database 연결 성공")
        except Exception as e:
            logging.error(f"Azure SQL Database 연결 실패: {str(e)}")
            raise
    
    @property
    def bq_client(self):
        """BigQuery 클라이언트를 반환합니다."""
        return self._bq_client
    
    @property
    def sql_conn(self):
        """SQL Database 연결을 반환합니다."""
        return self._sql_conn
    
    def execute_batch(self, table_name: str, data: list, columns: list):
        """배치 데이터를 SQL Database에 삽입합니다."""
        cursor = self._sql_conn.cursor()
        
        try:
            # 배치 크기만큼 나누어 처리
            for i in range(0, len(data), BATCH_SIZE):
                batch = data[i:i + BATCH_SIZE]
                
                # INSERT 쿼리 생성
                placeholders = ','.join(['?' for _ in columns])
                column_names = ','.join(columns)
                query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
                
                # 배치 실행
                cursor.executemany(query, batch)
                
            # 커밋
            self._sql_conn.commit()
            logging.info(f"{len(data)}개 레코드가 {table_name}에 성공적으로 삽입됨")
            
        except Exception as e:
            self._sql_conn.rollback()
            logging.error(f"배치 삽입 실패 ({table_name}): {str(e)}")
            raise
        finally:
            cursor.close()
    
    def __del__(self):
        """소멸자: 연결을 정리합니다."""
        if self._sql_conn:
            try:
                self._sql_conn.close()
            except Exception as e:
                logging.error(f"SQL 연결 종료 중 오류: {str(e)}")

# 전역 클라이언트 매니저 인스턴스
client_manager = ClientManager() 