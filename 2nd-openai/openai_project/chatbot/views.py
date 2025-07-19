from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os, json, requests, re
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_API_VERSION")
)

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_ADMIN_KEY"))
)

class SmartChatbotAPIView(APIView):
    def post(self, request):
        user_question_kr = request.data.get("question", "")
        if not user_question_kr:
            return Response({"error": "질문이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Step 0: 질문 분해
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
                        "  \"db_query\": \"...\",\n"
                        "  \"rag_query\": \"...\",\n"
                        "  \"reasoning\": \"...\"\n"
                        "}"
                    )
                    }

                    ,
                    {"role": "user", "content": user_question_kr}
                ]
            )

            raw_content = decompose_response.choices[0].message.content.strip()
            print("질문 분해 응답:\n", raw_content)

            try:
                decomposed = json.loads(raw_content)
            except json.JSONDecodeError:
                # YAML 스타일 fallback 파싱
                decomposed = {}
                for key in ["db_query", "rag_query", "reasoning"]:
                    match = re.search(rf"{key}\s*:\s*(.*)", raw_content)
                    decomposed[key] = match.group(1).strip() if match else ""

            db_query = decomposed.get("db_query", "").strip()
            rag_query = decomposed.get("rag_query", "").strip()
            reasoning = decomposed.get("reasoning", "").strip()

            sql_result_str = "DB 결과 없음"
            documents_str = "문서 없음"

            # Step 1: SQL 처리
            if db_query:
                try:
                    func_response = requests.post(
                        "http://localhost:7071/api/sqlquery",
                        json={"question": db_query},
                        timeout=360
                    )
                    func_response.raise_for_status()
                    sql_json = func_response.json()
                    sql_rows = sql_json.get("answer", [])
                    if isinstance(sql_rows, list) and sql_rows:
                        sql_result_str = "\n".join(
                            [json.dumps(row, ensure_ascii=False) for row in sql_rows]
                        )
                    else:
                        sql_result_str = "DB 결과 없음"
                except Exception as e:
                    print("SQL 호출 실패:", str(e))
                    sql_result_str = "데이터베이스 집계 결과를 불러오지 못했습니다."

            # Step 2: RAG 처리
            if rag_query:
                try:
                    translate_response = openai_client.chat.completions.create(
                        model=os.getenv("AZURE_DEPLOYMENT_NAME"),
                        messages=[
                            {"role": "system", "content": "Translate the Korean question into English."},
                            {"role": "user", "content": rag_query}
                        ]
                    )
                    rag_query_en = translate_response.choices[0].message.content.strip()

                    search_results = search_client.search(
                        rag_query_en,
                        query_type="semantic",
                        semantic_configuration_name="default",
                        top=3
                    )
                    docs = [doc.get("content", "") for doc in search_results if doc.get("content")]
                    if docs:
                        documents_str = "\n\n".join(docs)
                    else:
                        documents_str = "관련 문서를 찾을 수 없었습니다."
                except Exception as e:
                    print("문서 검색 실패:", str(e))
                    documents_str = "문서 검색에 실패했습니다."

            # Step 3: 프롬프트 구성
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

            final_completion = openai_client.chat.completions.create(
                model=os.getenv("AZURE_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "너는 데이터 분석과 마케팅 전략에 정통한 한국어 전문가야."},
                    {"role": "user", "content": final_prompt}
                ]
            )
            final_answer = final_completion.choices[0].message.content

            return Response({
                "answer": final_answer,
                "question_type": {
                    "db_query": bool(db_query),
                    "rag_query": bool(rag_query),
                    "reasoning": bool(reasoning)
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"처리 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
