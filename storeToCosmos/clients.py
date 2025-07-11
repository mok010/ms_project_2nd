from google.cloud import bigquery
from google.oauth2 import service_account
from azure.cosmos import CosmosClient, PartitionKey
from .config import SERVICE_ACCOUNT_PATH, COSMOS_CONN_STRING, COSMOS_DB_NAME, CONTAINER_NAMES

class ClientManager:
    """BigQuery와 CosmosDB 클라이언트를 관리하는 클래스"""
    
    def __init__(self):
        self._bq_client = None
        self._cosmos_client = None
        self._db = None
        self._containers = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """클라이언트들을 초기화합니다."""
        # BigQuery 클라이언트 초기화
        bq_credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)
        self._bq_client = bigquery.Client(credentials=bq_credentials, project=bq_credentials.project_id)
        
        # CosmosDB 클라이언트 초기화
        self._cosmos_client = CosmosClient.from_connection_string(COSMOS_CONN_STRING)
        self._db = self._cosmos_client.create_database_if_not_exists(COSMOS_DB_NAME)
        
        # 컨테이너들 초기화
        self._containers = {
            name: self._db.create_container_if_not_exists(
                id=container_id,
                partition_key=PartitionKey(path="/visitorId"),
                offer_throughput=400
            )
            for name, container_id in CONTAINER_NAMES.items()
        }
    
    @property
    def bq_client(self):
        """BigQuery 클라이언트를 반환합니다."""
        return self._bq_client
    
    @property
    def containers(self):
        """CosmosDB 컨테이너들을 반환합니다."""
        return self._containers
    
    def get_container(self, name):
        """특정 컨테이너를 반환합니다."""
        return self._containers.get(name)

# 전역 클라이언트 매니저 인스턴스
client_manager = ClientManager() 