import os
import fitz  # PyMuPDF
import numpy as np
import json
import requests
import re
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from upload_to_ai_search import upload_documents_to_ai_search  # AI Search 업로드 함수

load_dotenv()

# Azure OpenAI Embedding 클라이언트 설정
embedding_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
)

# 설정값 로딩
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION"))
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_client = blob_service_client.get_container_client(os.getenv("BLOB_CONTAINER_NAME"))

# 텍스트 전처리
def clean_text(text):
    text = text.replace('\n', ' ').replace('\xa0', ' ')
    text = ' '.join(text.split())

    # 유니코드 특수문자 제거 또는 대체
    ligature_map = {
        '\ufb01': 'fi',
        '\ufb02': 'fl',
        '©': '', '®': '', '™': '', '–': '-', '—': '-', '…': '...',
        '“': '"', '”': '"', '‘': "'", '’': "'",
    }
    for bad_char, replacement in ligature_map.items():
        text = text.replace(bad_char, replacement)

    # 제어 문자 제거
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)

    return text

# 유효한 청크인지 판단
def is_valid_chunk(chunk):
    chunk = chunk.strip().lower()
    return len(chunk) >= 20 and not chunk.startswith(("figure", "table", "references", "doi", "copyright"))

# 텍스트 청크 분할
def split_text(text, chunk_size=500):
    return [c for c in [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)] if is_valid_chunk(c)]

# Azure OpenAI로 임베딩 생성
def get_embeddings(texts):
    response = embedding_client.embeddings.create(
        input=texts,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )
    return [np.array(e.embedding, dtype=np.float32) for e in response.data]

# PDF → 텍스트 청크화 + 임베딩 → Blob 저장 + AI Search 업로드
def process_pdf_and_build_index(pdf_url: str, paper_prefix: str):
    from tempfile import NamedTemporaryFile

    # PDF 다운로드
    r = requests.get(pdf_url)
    with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(r.content)
        tmp_path = tmp_file.name

    doc = fitz.open(tmp_path)
    pages = [page.get_text() for page in doc]

    # Introduction ~ References 구간 추출
    intro_idx = 0
    for i, text in enumerate(pages):
        if "introduction" in text.lower():
            intro_idx = i
            break

    ref_idx = len(pages)
    for i in reversed(range(len(pages))):
        if "references" in pages[i].lower():
            ref_idx = i
            break

    excluded_before = list(range(0, intro_idx))
    excluded_after = list(range(ref_idx, len(pages)))
    print(f"제외된 페이지 (Introduction 이전): {excluded_before}")
    print(f"제외된 페이지 (References 이후): {excluded_after}")

    # 텍스트 청크화
    trimmed_pages = pages[intro_idx:ref_idx]
    full_text = "".join(trimmed_pages)
    chunks = split_text(clean_text(full_text))
    if not chunks:
        raise ValueError("유효한 청크 없음")

    # 임베딩 생성
    embeddings = get_embeddings(chunks)

    # 저장 및 업로드
    json_docs_for_search = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        doc_id = f"{paper_prefix}-{i+1:03}"
        json_doc = {
            "id": doc_id,
            "chunk": chunk,
            "embedding": embedding.tolist(),
            "metadata": {
                "source": f"{paper_prefix}.pdf",
                "chunk_index": i + 1
            }
        }

        # 1) Blob 저장
        blob_name = f"{doc_id}.json"
        container_client.upload_blob(
            name=blob_name,
            data=json.dumps(json_doc, ensure_ascii=False).encode("utf-8"),
            overwrite=True
        )

        # 2) AI Search 업로드용 리스트 구성
        json_docs_for_search.append({
            "id": doc_id,
            "chunk": chunk,
            "embedding": embedding.tolist(),
            "metadata_source": f"{paper_prefix}.pdf",
            "metadata_chunk_index": i + 1
        })

    # AI Search 업로드
    upload_documents_to_ai_search(json_docs_for_search)
