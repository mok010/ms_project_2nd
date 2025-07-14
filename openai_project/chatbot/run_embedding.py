from embedding_utils import process_pdf_and_build_index

pdf_files = [
    "C:/Users/EL57/Desktop/논문/논문3_trimmed.pdf",
    "C:/Users/EL57/Desktop/논문/논문4_trimmed.pdf"
]

for pdf_path in pdf_files:
    process_pdf_and_build_index(pdf_path)