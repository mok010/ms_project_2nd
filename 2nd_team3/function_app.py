import azure.functions as func
import pyodbc
import os
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)  # 필요시 ANONYMOUS 로 변경

@app.function_name(name="SqlQueryFunction")
@app.route(route="sqlquery")  # 호출 경로: /api/sqlquery
def sql_query_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        user_question = req_body.get('question')
    except Exception as e:
        return func.HttpResponse(f"Invalid request body: {e}", status_code=400)

    # 간단한 질문 → 쿼리 매핑
        # 질문 → 쿼리 매핑
    if "상품별 평균 가격" in user_question:
        query = """
        SELECT v2ProductName, AVG(productPrice) AS avgPrice
        FROM [ga_data].[HitsProduct]
        GROUP BY v2ProductName
        """
    elif "새 방문자 수" in user_question:
        query = """
        SELECT COUNT(*) as new_user_count
        FROM [ga_data].[Totals]
        WHERE newVisits = 1
        """
    elif "채널별 사용자 수" in user_question or "방문 채널" in user_question:
        query = """
        SELECT 'browser' as channel_type, browser as channel_name, count(visitorId) as user_count
        FROM [ga_data].[DeviceGeo]
        GROUP BY browser

        UNION ALL

        SELECT 'deviceCategory' as channel_type, deviceCategory as channel_name, count(visitorId) as user_count
        FROM [ga_data].[DeviceGeo]
        GROUP BY deviceCategory

        UNION ALL
        
        SELECT 'operatingSystem' as channel_type, operatingSystem as channel_name, count(visitorId) as user_count
        FROM [ga_data].[DeviceGeo]
        GROUP BY operatingSystem
        """
    else:
        return func.HttpResponse(
            json.dumps({"error": "지원하지 않는 질문입니다."}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json"
        )


    # SQL 연결 정보
    server = os.environ["SQL_SERVER"]
    database = os.environ["SQL_DATABASE"]
    username = os.environ["SQL_USERNAME"]
    password = os.environ["SQL_PASSWORD"]
    driver = "ODBC Driver 18 for SQL Server"

    try:
        with pyodbc.connect(
            f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}",
            timeout=5
        ) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]

            return func.HttpResponse(
                json.dumps(result, ensure_ascii=False),
                status_code=200,
                mimetype="application/json"
            )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json"
        )
