import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# 환경변수에서 설정값 로딩
SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT") 
SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")      
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")

def upload_documents_to_ai_search(documents):
    """
    AI Search에 문서 리스트 업로드
    :param documents: JSON 형식의 문서 리스트 (각 문서는 'id', 'chunk', 'embedding', 'metadata' 포함)
    """
    headers = {
        "Content-Type": "application/json",
        "api-key": SEARCH_API_KEY
    }

    upload_body = {
        "value": [
            {
                "@search.action": "upload",
                "id": doc["id"],
                "chunk": doc["chunk"],
                "embedding": doc["embedding"],
                "metadata_source": doc["metadata_source"],
                "metadata_chunk_index": doc["metadata_chunk_index"]
            }
            for doc in documents
        ]
    }

    endpoint = f"{SEARCH_SERVICE_ENDPOINT}/indexes/{SEARCH_INDEX_NAME}/docs/index?api-version=2023-11-01"
    response = requests.post(endpoint, headers=headers, data=json.dumps(upload_body))

    if response.status_code == 200:
        print(f"AI Search 업로드 성공! 업로드된 문서 수: {len(documents)}")
    else:
        print(f"업로드 실패: {response.status_code} - {response.text}")
