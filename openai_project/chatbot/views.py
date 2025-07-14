from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os, json, requests
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI 클라이언트
openai_client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_version=os.environ.get("AZURE_API_VERSION")
)

# Azure Cognitive Search 클라이언트
search_client = SearchClient(
    endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
    index_name=os.environ.get("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.environ.get("AZURE_SEARCH_ADMIN_KEY"))
)

class SmartChatbotAPIView(APIView):
    def post(self, request):
        user_question_kr = request.data.get("question", "")

        if not user_question_kr:
            return Response({"error": "질문이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 번역
        try:
            translation_response = openai_client.chat.completions.create(
                model=os.getenv("AZURE_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "Translate the Korean question into English for document search."},
                    {"role": "user", "content": user_question_kr}
                ]
            )
            user_question_en = translation_response.choices[0].message.content
        except Exception as e:
            return Response({"error": f"번역 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 2. Azure Functions (SQL)
        try:
            func_url = "http://localhost:7071/api/sqlquery"
            func_response = requests.post(func_url, json={"question": user_question_kr}, timeout=60)

            # 디버깅용 로그 추가
            print("SQL Function 응답 상태 코드:", func_response.status_code)
            print("SQL Function 응답 내용:", func_response.text)

            func_response.raise_for_status()
            sql_result = func_response.json().get("answer", "")
        except Exception as e:
            return Response({"error": f"Azure Functions 호출 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Azure Cognitive Search
        try:
            search_results = search_client.search(user_question_en, top=3)
            documents = "\n\n".join([doc["content"] for doc in search_results])
        except Exception as e:
            documents = ""
            # 문서가 없더라도 진행

        # 4. 최종 답변 생성
        try:
            prompt = (
                f"[사용자 질문]\n{user_question_kr}\n\n"
                f"[SQL 집계 결과]\n{sql_result}\n\n"
                f"[문서 검색 결과]\n{documents if documents else '관련 문서를 찾을 수 없었습니다.'}\n\n"
                f"위 정보를 바탕으로 사용자의 질문에 친절하고 이해하기 쉬운 한국어 답변을 제공하세요."
                f"이모티콘 등의 요소를 제거하세요."
                f"답변만 하고, 추가 질문은 하지 마세요."
            )
            final_completion = openai_client.chat.completions.create(
                model=os.getenv("AZURE_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "너는 데이터 분석과 마케팅에 정통한 비서야."},
                    {"role": "user", "content": prompt}
                ]
            )
            final_answer = final_completion.choices[0].message.content
        except Exception as e:
            return Response({"error": f"OpenAI 응답 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"answer": final_answer}, status=status.HTTP_200_OK)
