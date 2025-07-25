import os
import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv
from embedding_utils import process_pdf_and_build_index
import re

load_dotenv()

AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
TRIGGER_CONTAINER_NAME = os.getenv("TRIGGER_CONTAINER_NAME", "test-input-pdf")

process_pdf_trigger = func.Blueprint()

def generate_slug_from_filename(filename: str):
    base = os.path.basename(filename).replace(".pdf", "")
    slug = re.sub(r'[^a-zA-Z0-9]', '-', base.lower())
    return f"paper-processed-{slug}"

def generate_sas_url(container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    account_name = blob_service_client.account_name
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=AZURE_STORAGE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(minutes=30)
    )
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

@process_pdf_trigger.function_name(name="process_pdf_trigger_fn")
@process_pdf_trigger.blob_trigger(arg_name="blob", path="test-input-pdf/{name}", connection="AzureWebJobsStorage")
def main(blob: func.InputStream):
    logging.info(f"[TRIGGER] {blob.name} ({blob.length} bytes) 업로드 감지")

    try:
        filename = blob.name.split("/")[-1]
        sas_url = generate_sas_url(TRIGGER_CONTAINER_NAME, filename)
        paper_prefix = generate_slug_from_filename(filename)
        process_pdf_and_build_index(sas_url, paper_prefix)
    except Exception as e:
        logging.error(f"[ERROR] {blob.name} 처리 실패 → {str(e)}")
