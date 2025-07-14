import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField
)

# 환경변수 로드
load_dotenv()

# 설정값 로드
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
BLOB_PREFIX = "paper-processed"

# 클라이언트 세팅
search_credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
search_index_client = SearchIndexClient(endpoint=AZURE_SEARCH_ENDPOINT, credential=search_credential)
search_client = SearchClient(endpoint=AZURE_SEARCH_ENDPOINT,
                             index_name=AZURE_SEARCH_INDEX_NAME,
                             credential=search_credential)

# 인덱스 생성 함수
def create_index():
    print("Creating index if not exists...")

    fields = [
        SimpleField(name="id", type="Edm.String", key=True),
        SearchableField(name="content", type="Edm.String", analyzer_name="en.lucene"),
        SimpleField(name="chunk_id", type="Edm.Int32"),
    ]

    index = SearchIndex(name=AZURE_SEARCH_INDEX_NAME, fields=fields)

    try:
        search_index_client.get_index(AZURE_SEARCH_INDEX_NAME)
        print("Index already exists.")
    except:
        search_index_client.create_index(index)
        print("Index created.")

# Blob에서 chunk 읽기
def load_chunks_from_blob():
    print("Loading chunks from blob storage...")
    documents = []
    blobs = container_client.list_blobs(name_starts_with=BLOB_PREFIX)
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        content = blob_client.download_blob().readall().decode("utf-8")
        chunk_id = int(blob.name.split("-")[-1].replace(".txt", ""))
        documents.append({
            "id": blob.name.replace(".txt", ""),
            "content": content,
            "chunk_id": chunk_id
        })
    print(f"Loaded {len(documents)} documents.")
    return documents

# 인덱스에 업로드
def upload_to_search(documents):
    print("Uploading to Azure AI Search...")
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        result = search_client.upload_documents(documents=batch)
        
        # 결과 출력 추가
        for r in result:
            if not r.succeeded:
                print(f"Failed to upload: {r.key}, Error: {r.error_message}")
            else:
                print(f"Uploaded: {r.key}")

# 실행 흐름
if __name__ == "__main__":
    create_index()
    docs = load_chunks_from_blob()
    upload_to_search(docs)
    print("All documents uploaded to Azure AI Search")
