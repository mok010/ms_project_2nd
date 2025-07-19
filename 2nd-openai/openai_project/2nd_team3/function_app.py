import azure.functions as func
import os
import json
import logging
import time
import requests
import pyodbc
from datetime import datetime
import traceback # traceback 모듈 임포트

# Application Insights 로깅 설정
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
logger = logging.getLogger(__name__)

# datetime 객체를 JSON 직렬화 가능하도록 변환하는 도우미 함수
# (이전 테스트에서 datetime is not JSON serializable 오류를 해결했습니다)
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat() # ISO 8601 형식의 문자열로 변환 (예: '2023-01-01T12:30:00')
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

# SCHEMA_INFO 정의 (데이터베이스 스키마 정보)
SCHEMA_INFO = """
=== Microsoft SQL Server 데이터베이스 ===

dbo 스키마:
- dbo.News: category, competitor_mentioned, content, created_at, frequent_words, id, keyword_count, market_segment, published_date, sentiment_score, source, title, url
- dbo.StockPrices: change_percent, close_price, created_at, date, id, symbol
- dbo.vw_DailyNewsSummary: avg_sentiment, negative_news, neutral_news, positive_news, summary_date, total_news
- dbo.vw_DailyStockSummary: change_percent, close_price, daily_change_percent, date, prev_close, symbol
- dbo.vw_NewsSentimentTrend: category, news_date, sentiment_score, source, title, url
- dbo.vw_SentimentStockCorrelation: avg_sentiment, change_percent, close_price, summary_date, symbol
- dbo.vw_StockAnalysis: change_percent, close_price, date, ma_30, ma_7, prev_close, symbol

ga_data 스키마:
- ga_data.Analytics: actionType, adContent, browser, campaign, channelGrouping, city, country, date, deviceCategory, eventAction, eventCategory, fullVisitorId, hits, hostname, medium, operatingSystem, pagePath, pageTitle, pageviews, productBrand, productId, productPrice, productRevenue, referralPath, region, source, timeOnSite, totalTransactionRevenue, transactionId, transactions, visits, visitNumber
- ga_data.CustomDimensions: cdId, dimensionIndex, dimensionValue, hitId, visitorId
- ga_data.DateTracking: description, id, setting_key, setting_value, updated_at
- ga_data.ProcessStatus: analytics_count, error_message, execution_time, processed_date, records_processed, run_date, status
"""

@app.function_name(name="SqlQueryFunction")
@app.route(route="sqlquery", methods=["GET", "POST"])
def sql_query_function(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time.time()
    logger.info(f"[{time.time() - start_time:.2f}s] SqlQueryFunction 요청 시작")

    try:
        # 1. 사용자 질문 파싱
        user_question = req.params.get('question')
        if not user_question:
            try:
                req_body = req.get_json()
                user_question = req_body.get('question')
            except ValueError:
                pass # JSON body가 없거나 파싱 오류
            
        if not user_question:
            logger.warning(f"[{time.time() - start_time:.2f}s] 질문이 제공되지 않았습니다.")
            return func.HttpResponse(
                json.dumps({"error": "질문을 입력해주세요.", "execution_time": f"{time.time() - start_time:.2f}s"}, ensure_ascii=False),
                status_code=400,
                mimetype="application/json"
            )
        logger.info(f"[{time.time() - start_time:.2f}s] 사용자 질문: '{user_question}'")

        # 2. OpenAI API 호출 및 SQL 쿼리 생성
        logger.info(f"[{time.time() - start_time:.2f}s] OpenAI API 호출 시작...")
        
        # OpenAI API 관련 환경 변수 확인 (미리 테스트 완료)
        azure_openai_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        azure_openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        azure_deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME")

        if not all([azure_openai_api_key, azure_openai_endpoint, azure_deployment_name]):
            raise ValueError("OpenAI API 환경 변수(API_KEY, ENDPOINT, DEPLOYMENT_NAME)가 설정되지 않았습니다.")

        api_headers = {
            "Content-Type": "application/json",
            "api-key": azure_openai_api_key
        }
        
        prompt = f"""
        당신은 Microsoft SQL Server 전문가입니다. 아래 스키마만 사용하여 SELECT 쿼리를 생성하세요.
        {SCHEMA_INFO}
        STRICT RULES:
        1. ONLY SELECT statements allowed
        2. USE ONLY Microsoft SQL Server syntax
        3. USE TOP instead of LIMIT
        4. ONLY use tables/columns from schema above
        5. NO DROP/DELETE/UPDATE/INSERT commands
        Question: {user_question}
        Return ONLY the SQL query:"""
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 250,
            "temperature": 0,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        api_url = f"{azure_openai_endpoint}/openai/deployments/{azure_deployment_name}/chat/completions?api-version=2024-12-01-preview"
        
        response = requests.post(api_url, headers=api_headers, json=payload, timeout=30) # OpenAI API 호출 타임아웃
        response.raise_for_status() # HTTP 오류 발생 시 예외 발생 (4xx, 5xx)
        
        generated_sql = response.json()['choices'][0]['message']['content'].strip()
        logger.info(f"[{time.time() - start_time:.2f}s] OpenAI로부터 생성된 SQL: '{generated_sql}'")

        # 3. SQL 쿼리 유효성 검사 및 수정 (가장 최근 수정 부분!)
        # OpenAI가 생성한 쿼리에서 마크다운 백틱(```sql, ```)을 제거합니다.
        validated_sql = generated_sql.replace("```sql", "").replace("```", "").strip() 
        logger.info(f"[{time.time() - start_time:.2f}s] 최종 실행할 SQL (유효성 검사 후): '{validated_sql}'")

        # 4. SQL Database 연결 및 쿼리 실행
        sql_server = os.environ.get('SQL_SERVER')
        sql_database = os.environ.get('SQL_DATABASE')
        sql_username = os.environ.get('SQL_USERNAME')
        sql_password = os.environ.get('SQL_PASSWORD') # SQL_PASSWORD 환경 변수 사용

        if not all([sql_server, sql_database, sql_username, sql_password]):
            raise ValueError("SQL 연결을 위한 환경 변수(SERVER, DATABASE, USERNAME, PASSWORD)가 설정되지 않았습니다.")

        # pyodbc 연결 문자열 (드라이버 18 사용)
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={sql_server};"
            f"DATABASE={sql_database};"
            f"UID={sql_username};"
            f"PWD={sql_password}"
        )
        
        logger.info(f"[{time.time() - start_time:.2f}s] DB 연결 시도 중...")
        # pyodbc 연결 타임아웃 (300초 = 5분)
        conn = pyodbc.connect(conn_str, timeout=300) 
        logger.info(f"[{time.time() - start_time:.2f}s] DB 연결 성공!")
        
        cursor = conn.cursor()
        
        logger.info(f"[{time.time() - start_time:.2f}s] 쿼리 실행 시도: '{validated_sql}'")
        cursor.execute(validated_sql) # SQL 쿼리 실행
        logger.info(f"[{time.time() - start_time:.2f}s] 쿼리 실행 완료. 결과 가져오는 중...")

        columns = [column[0] for column in cursor.description]
        rows = []
        for row_tuple in cursor.fetchall(): # 모든 결과 가져오기
            row_dict = dict(zip(columns, row_tuple))
            processed_row = {}
            for k, v in row_dict.items():
                if isinstance(v, datetime):
                    processed_row[k] = v.isoformat() # datetime 객체 ISO 형식 문자열로 변환
                else:
                    processed_row[k] = v
            rows.append(processed_row)
        
        cursor.close()
        conn.close()
        logger.info(f"[{time.time() - start_time:.2f}s] 쿼리 결과 처리 및 DB 연결 종료.")

        # 5. 최종 응답 반환
        execution_time = time.time() - start_time
        response_data = {
            "question": user_question,
            "sql_query": validated_sql,
            "results": rows,
            "execution_time": f"{execution_time:.2f}s"
        }
        
        return func.HttpResponse(
            json.dumps(response_data, ensure_ascii=False),
            mimetype="application/json"
        )

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"[{execution_time:.2f}s] SqlQueryFunction 오류 발생: {str(e)}", exc_info=True)
        
        # 오류 발생 시 디버깅을 위해 더 많은 정보 포함
        error_response_data = {
            "error": str(e),
            "message": "함수 실행 중 오류가 발생했습니다.",
            "execution_time": f"{execution_time:.2f}s",
            "traceback": traceback.format_exc() # traceback 정보 추가 (디버깅용)
        }
        return func.HttpResponse(
            json.dumps(error_response_data, ensure_ascii=False),
            status_code=500,
            mimetype="application/json"
        )