import os
import json
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# ─────────────── 🔹 local.settings.json 로드 ───────────────
def load_local_settings(path="local.settings.json"):
    with open(path, "r", encoding="utf-8") as f:
        settings = json.load(f)
    for key, value in settings.get("Values", {}).items():
        os.environ.setdefault(key, value)

load_local_settings()

# ─────────────── 🔹 환경 변수 로딩 ───────────────
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

# ─────────────── 🔹 SearchClient 초기화 ───────────────
search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
)

# ─────────────── 🔹 검색 함수 ───────────────
def search(query: str, top_k: int = 5):
    print(f"\n🔍 Query: {query}\n")
    results = search_client.search(search_text=query, top=top_k)

    for i, result in enumerate(results):
        print(f"[{i+1}] ID: {result['id']}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Content:\n{result['content'][:300]}...")
        print("-" * 50)

# ─────────────── 🔹 테스트 실행 ───────────────
if __name__ == "__main__":
    user_query = input("검색할 내용을 입력하세요: ")
    search(user_query)
