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
    """BigQuery와 Azure SQL Database 클라이언트를 관리하는 클래스
    
    이 클래스는 다음과 같은 역할을 담당합니다:
    1. Google BigQuery 클라이언트 초기화 및 관리
    2. Azure SQL Database 연결 설정 및 관리
    3. SQL Database에 배치 데이터 삽입 처리
    
    모든 클라이언트 연결은 초기화 시 생성되고 재사용되어 성능을 최적화합니다.
    """
    
    def __init__(self):
        """클라이언트 매니저 초기화
        
        BigQuery 클라이언트와 SQL Database 연결을 설정합니다.
        연결 실패 시 예외가 발생합니다.
        """
        self._bq_client = None
        self._sql_conn = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """클라이언트들을 초기화합니다.
        
        1. Google Cloud 서비스 계정 키를 사용하여 BigQuery 클라이언트 초기화
        2. Azure SQL Database 연결 설정 (ODBC Driver 18 사용)
        
        Raises:
            Exception: SQL Database 연결 실패 시 발생
        """
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
        """BigQuery 클라이언트를 반환합니다.
        
        Returns:
            google.cloud.bigquery.Client: 초기화된 BigQuery 클라이언트
        """
        return self._bq_client
    
    @property
    def sql_conn(self):
        """SQL Database 연결을 반환합니다.
        
        Returns:
            pyodbc.Connection: 초기화된 SQL Database 연결
        """
        return self._sql_conn
    
    def execute_batch(self, table_name: str, data: list, columns: list):
        """배치 데이터를 SQL Database에 삽입합니다.
        
        이 메서드는 대량의 데이터를 효율적으로 삽입하기 위해 배치 처리를 사용합니다.
        데이터는 BATCH_SIZE 단위로 나누어 처리되며, 모든 작업은 하나의 트랜잭션으로 처리됩니다.
        오류 발생 시 전체 트랜잭션이 롤백됩니다.
        
        Args:
            table_name (str): 데이터를 삽입할 테이블 이름 (스키마 포함)
            data (list): 삽입할 데이터 행 목록
            columns (list): 삽입할 열 이름 목록
            
        Raises:
            Exception: 배치 삽입 실패 시 발생하며 트랜잭션이 롤백됩니다
        """
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
            # 오류 발생 시 롤백
            self._sql_conn.rollback()
            logging.error(f"배치 삽입 실패 ({table_name}): {str(e)}")
            raise
        finally:
            cursor.close()
    
    def __del__(self):
        """소멸자: 연결을 정리합니다.
        
        객체가 소멸될 때 SQL Database 연결을 안전하게 종료합니다.
        """
        if self._sql_conn:
            try:
                self._sql_conn.close()
            except Exception as e:
                logging.error(f"SQL 연결 종료 중 오류: {str(e)}")

# 전역 클라이언트 매니저 인스턴스
# 애플리케이션 전체에서 하나의 인스턴스를 공유하여 연결을 재사용합니다
client_manager = ClientManager() 