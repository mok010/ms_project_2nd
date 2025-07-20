import os
import fitz  # PyMuPDF
import numpy as np
import faiss
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

# 환경변수 로드
load_dotenv()

# Azure OpenAI 클라이언트
embedding_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
)

# 임베딩 차원
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION"))

# Blob Storage 연결
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_name = os.getenv("BLOB_CONTAINER_NAME")
container_client = blob_service_client.get_container_client(container_name)

# 텍스트 정제
def clean_text(text):
    text = text.replace('\n', ' ').replace('\xa0', ' ')
    text = ' '.join(text.split())
    return text

# PDF에서 텍스트 추출
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return clean_text(full_text)

# 유효한 chunk 판별
def is_valid_chunk(chunk):
    chunk_lower = chunk.lower()
    if len(chunk.strip()) < 20:
        return False
    if chunk_lower.startswith(("figure", "table", "references", "doi", "copyright")):
        return False
    return True

# 텍스트 분할
def split_text(text, chunk_size=500):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return [chunk for chunk in chunks if is_valid_chunk(chunk)]

# 임베딩 생성
def get_embeddings(text_list):
    response = embedding_client.embeddings.create(
        input=text_list,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )
    return [np.array(e.embedding, dtype=np.float32) for e in response.data]

# FAISS 인덱스 구축
def build_faiss_index(embeddings):
    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(np.array(embeddings))
    return index

# Chunk를 Blob에 업로드
def upload_chunks_to_blob(chunks, prefix="paper-processed"):
    for i, chunk in enumerate(chunks):
        blob_name = f"{prefix}-{i+1:03}.txt"
        container_client.upload_blob(name=blob_name, data=chunk.encode("utf-8"), overwrite=True)

# 전체 파이프라인
def process_pdf_and_build_index(pdf_path):
    print(f"Processing: {os.path.basename(pdf_path)}")
    text = extract_text_from_pdf(pdf_path)
    chunks = split_text(text)
    if not chunks:
        raise ValueError("No valid chunks to process.")
    embeddings = get_embeddings(chunks)
    index = build_faiss_index(embeddings)
    upload_chunks_to_blob(chunks)
    return index, chunks
