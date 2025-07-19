import os
import json
import requests
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import traceback

# 수정된 import: SearchOptions 제거, VectorizableTextQuery 사용
from azure.search.documents.models import VectorizableTextQuery

load_dotenv()

# 환경 변수 로드
AZURE_FUNCTION_SQL_API_URL = os.getenv("AZURE_FUNCTION_SQL_API_URL")
if not AZURE_FUNCTION_SQL_API_URL:
    print("CRITICAL ERROR: AZURE_FUNCTION_SQL_API_URL 환경 변수가 설정되지 않았습니다.")
    raise ValueError("AZURE_FUNCTION_SQL_API_URL 환경 변수가 설정되지 않았습니다. .env 파일을 확인하거나 배포 환경 설정을 확인하세요.")

# Azure OpenAI 클라이언트 초기화
try:
    openai_client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_API_VERSION") # 일반적인 GPT 모델용 API 버전
    )
    print("DEBUG: Azure OpenAI client initialized successfully at global scope.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize Azure OpenAI client at global scope: {e}")
    traceback.print_exc()
    raise # 초기화 실패 시 애플리케이션 시작을 중단

# Azure Search 클라이언트 초기화
try:
    search_client = SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"), # paper-index
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY"))
    )
    print("DEBUG: Azure Search client initialized successfully at global scope.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize Azure AI Search client at global scope: {e}")
    traceback.print_exc()
    raise # 초기화 실패 시 애플리케이션 시작을 중단

class SmartChatbotAPIView(APIView):
    def post(self, request):
        print("DEBUG: SmartChatbotAPIView.post method started.")
        user_question_kr = request.data.get("question", "")
        print(f"DEBUG: Received user_question_kr: '{user_question_kr}'")

        if not user_question_kr:
            print("DEBUG: User question is empty. Returning 400.")
            return Response({"error": "질문이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Step 0: 질문 분해
            print("DEBUG: Starting Step 0: Question decomposition.")
            decompose_response = openai_client.chat.completions.create(
                model=os.getenv("AZURE_DEPLOYMENT_NAME"),
                messages=[
                    {
                    "role": "system",
                    "content": (
                        "사용자의 자연어 질문을 다음 세 가지 항목으로 나누세요:\n\n"
                        "1. db_query: 숫자, 통계, 수치, 비교, 집계 등을 묻는 질문\n"
                        "2. rag_query: 특정 정보를 문서에서 검색해야 답할 수 있는 질문\n"
                        "3. reasoning: 전략, 창의적인 아이디어, 판단, 분석, 제안 등을 요하는 질문\n\n"
                        "각 항목은 질문 속 해당 내용을 문장 단위로 발췌해서 넣고, 없으면 빈 문자열로 두세요.\n"
                        "다음 JSON 형식으로만 응답하세요:\n"
                        "{\n"
                        " \"db_query\": \"...\",\n"
                        " \"rag_query\": \"...\",\n"
                        " \"reasoning\": \"...\"\n"
                        "}"
                    )
                    }
                    ,
                    {"role": "user", "content": user_question_kr}
                ]
            )

            raw_content = decompose_response.choices[0].message.content.strip()
            print(f"DEBUG: Decomposed raw_content: {raw_content}")

            try:
                decomposed = json.loads(raw_content)
            except json.JSONDecodeError:
                print("DEBUG: JSONDecodeError. Attempting YAML-style fallback parsing.")
                decomposed = {}
                for key in ["db_query", "rag_query", "reasoning"]:
                    match = re.search(rf"{key}\s*:\s*(.*)", raw_content)
                    decomposed[key] = match.group(1).strip() if match else ""
                print(f"DEBUG: Decomposed (fallback): {decomposed}")

            db_query = decomposed.get("db_query", "").strip()
            rag_query = decomposed.get("rag_query", "").strip()
            reasoning = decomposed.get("reasoning", "").strip()
            print(f"DEBUG: Extracted: db_query='{db_query}', rag_query='{rag_query}', reasoning='{reasoning}'")

            sql_result_str = "DB 결과 없음"
            documents_str = "문서 없음"

            # Step 1: SQL 처리
            if db_query:
                print(f"DEBUG: Starting Step 1: SQL processing for db_query: '{db_query}'")
                try:
                    print(f"DEBUG: Calling Azure Function SQL API URL: {AZURE_FUNCTION_SQL_API_URL}")
                    func_response = requests.post(
                        AZURE_FUNCTION_SQL_API_URL,
                        json={"question": db_query},
                        timeout=360
                    )
                    func_response.raise_for_status()
                    sql_json = func_response.json()
                    sql_rows = sql_json.get("results", [])
                    if isinstance(sql_rows, list) and sql_rows:
                        sql_result_str = "\n".join(
                            [json.dumps(row, ensure_ascii=False) for row in sql_rows]
                        )
                        print(f"DEBUG: SQL result received: {sql_result_str}")
                    else:
                        sql_result_str = "DB 결과 없음"
                        print("DEBUG: No SQL results found from Azure Function.")
                except Exception as e:
                    print(f"ERROR: SQL API call failed: {e}")
                    traceback.print_exc()
                    sql_result_str = "데이터베이스 집계 결과를 불러오지 못했습니다."

            # Step 2: RAG 처리 (벡터 검색 우선)
            if rag_query:
                print(f"DEBUG: Starting Step 2: RAG processing for rag_query: '{rag_query}'")
                try:
                    # 1. 사용자 질문(rag_query_en)을 번역
                    print("DEBUG: Translating RAG query from Korean to English.")
                    translate_response = openai_client.chat.completions.create(
                        model=os.getenv("AZURE_DEPLOYMENT_NAME"),
                        messages=[
                            {"role": "system", "content": "Translate the Korean question into English."},
                            {"role": "user", "content": rag_query}
                        ]
                    )
                    rag_query_en = translate_response.choices[0].message.content.strip()
                    print(f"DEBUG: Translated RAG query (English): '{rag_query_en}'")

                    # 2. 벡터 검색 먼저 시도
                    print("DEBUG: Trying vector search first for testing")
                    search_success = False

                    try:
                        print("DEBUG: Trying vector field: embedding")
                        
                        # 임베딩 생성
                        embedding_response = openai_client.embeddings.create(
                            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
                            input=rag_query_en,
                        )
                        query_vector = embedding_response.data[0].embedding
                        print(f"DEBUG: Embedding created. Vector length: {len(query_vector)}")
                        
                        # VectorizableTextQuery 사용
                        vector_query = VectorizableTextQuery(
                            text=rag_query_en,
                            k_nearest_neighbors=3,
                            fields="embedding"
                        )
                        
                        # 벡터 검색 실행
                        search_results = search_client.search(
                            search_text=rag_query_en,
                            vector_queries=[vector_query],
                            top=3
                        )
                        
                        docs = []
                        for doc in search_results:
                            print(f"DEBUG: Found document fields: {list(doc.keys())}")
                            # chunk 필드에서 텍스트 가져오기
                            if "chunk" in doc and doc["chunk"]:
                                docs.append(doc["chunk"])
                                print(f"DEBUG: Using text field: chunk")
                        
                        if docs:
                            documents_str = "\n\n".join(docs)
                            print(f"DEBUG: Vector search successful, found {len(docs)} documents")
                            print(f"DEBUG: Documents (first 200 chars): {documents_str[:200]}...")
                            search_success = True
                        else:
                            print("DEBUG: Vector search returned results but no text content found")
                            
                    except Exception as vector_error:
                        print(f"DEBUG: Vector search failed: {vector_error}")

                    # 3. 벡터 검색이 실패했으면 기본 텍스트 검색 시도
                    if not search_success:
                        print("DEBUG: Vector search failed, trying basic text search")
                        try:
                            # 가장 기본적인 검색 (select 없이)
                            search_results = search_client.search(
                                search_text=rag_query_en,
                                top=3
                            )
                            
                            docs = []
                            for doc in search_results:
                                print(f"DEBUG: Found document fields: {list(doc.keys())}")
                                # 여러 가능한 텍스트 필드명 시도
                                text_content = None
                                for field_name in ["chunk", "content", "text", "body", "description"]:
                                    if field_name in doc and doc[field_name]:
                                        text_content = doc[field_name]
                                        print(f"DEBUG: Using text field: {field_name}")
                                        break
                                
                                if text_content:
                                    docs.append(text_content)
                            
                            if docs:
                                documents_str = "\n\n".join(docs)
                                print(f"DEBUG: Basic search successful, found {len(docs)} documents")
                                print(f"DEBUG: Documents (first 200 chars): {documents_str[:200]}...")
                                search_success = True
                            else:
                                print("DEBUG: Basic search returned results but no text content found")
                                
                        except Exception as basic_search_error:
                            print(f"DEBUG: Basic search failed: {basic_search_error}")

                    # 4. 모든 검색이 실패했을 때
                    if not search_success:
                        print("DEBUG: All search methods failed")
                        documents_str = "관련 문서를 찾을 수 없었습니다."

                except Exception as e:
                    print(f"ERROR: Document search failed: {e}")
                    traceback.print_exc()
                    documents_str = "문서 검색에 실패했습니다. 오류: " + str(e)

            # Step 3: 프롬프트 구성
            print("DEBUG: Constructing final prompt for LLM.")
            prompt_parts = [f"[사용자 질문]\n{user_question_kr}"]
            prompt_parts.append(f"[SQL 결과]\n{sql_result_str}")
            prompt_parts.append(f"[문서 검색 결과]\n{documents_str}")
            if reasoning:
                prompt_parts.append(f"[추론해야 할 내용]\n{reasoning}")
            prompt_parts.append(
                "위 내용을 바탕으로 사용자의 질문에 대해 창의적이고 구체적인 한국어 답변을 작성하세요. "
                "이모티콘은 금지. 질문 유도는 금지."
            )

            final_prompt = "\n\n".join(prompt_parts)
            print(f"DEBUG: Final prompt for LLM (first 500 chars):\n{final_prompt[:500]}...")

            print(f"DEBUG: Calling final OpenAI completion with model: '{os.getenv('AZURE_DEPLOYMENT_NAME')}'")
            final_completion = openai_client.chat.completions.create(
                model=os.getenv("AZURE_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "너는 데이터 분석과 마케팅 전략에 정통한 한국어 전문가야."},
                    {"role": "user", "content": final_prompt}
                ]
            )
            final_answer = final_completion.choices[0].message.content
            print(f"DEBUG: Final answer received (first 200 chars): {final_answer[:200]}...")

            print("DEBUG: Returning final API response (200 OK).")
            return Response({
                "answer": final_answer,
                "question_type": {
                    "db_query": bool(db_query),
                    "rag_query": bool(rag_query),
                    "reasoning": bool(reasoning)
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"CRITICAL ERROR: An unexpected error occurred in post method: {e}")
            traceback.print_exc()
            return Response({"error": f"처리 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
