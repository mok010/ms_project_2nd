import azure.functions as func
import os
import json
import traceback
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text
from langchain_community.chat_models import AzureChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain.prompts import PromptTemplate

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="SqlQueryFunction")
@app.route(route="sqlquery")
def sql_query_function(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        user_question = req_body.get('question')
        if not user_question:
            raise ValueError("질문이 없습니다.")
    except Exception as e:
        print("요청 파싱 실패:", str(e))
        return func.HttpResponse(f"Invalid request body: {e}", status_code=400)

    try:
        # DB 연결
        connection_url = URL.create(
            drivername="mssql+pyodbc",
            username=os.environ["SQL_USERNAME"],
            password=os.environ["SQL_PASSWORD"],
            host=os.environ["SQL_SERVER"],
            port=1433,
            database=os.environ["SQL_DATABASE"],
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "Encrypt": "yes",
                "TrustServerCertificate": "no",
                "Connection Timeout": "30"
            }
        )
        engine = create_engine(connection_url)

        db = SQLDatabase(
            engine,
            schema="ga_data",
            include_tables=[
                "CustomDimensions",
                "DeviceGeo",
                "Hits",
                "HitsProduct",
                "Sessions",
                "Totals",
                "Traffic"
            ],
            sample_rows_in_table_info=3,
            view_support=True
        )

        table_info = db.get_table_info()
        print("DB 연결 및 구조 분석 성공")

    except Exception as e:
        print("DB 연결 실패:", str(e))
        traceback.print_exc()
        return func.HttpResponse(f"DB 연결 실패: {e}", status_code=500)

    try:
        llm = AzureChatOpenAI(
            deployment_name=os.environ["AZURE_DEPLOYMENT_NAME"],
            openai_api_version="2024-12-01-preview",
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            openai_api_key=os.environ["AZURE_OPENAI_API_KEY"]
        )
        print("LLM 연결 성공")

        prompt_template = PromptTemplate.from_template("""
        You are an expert SQL developer working with Microsoft SQL Server.
        Your job is to convert natural language questions into a syntactically correct SQL query.

        Use only the schema below:

        {table_info}

        Do not invent any table or column that does not exist above.
        Only use tables under schema [ga_data].

        If the question cannot be answered using only the schema above, return:
        SELECT 'Invalid question: missing required table or column.' AS Error;

        ### Rules:
        - Return a single SQL query only.
        - No markdown (no ```sql or ```).
        - No explanation or comments.
        - No extra newlines or whitespace.
        - Must start with SELECT/INSERT/UPDATE/DELETE.

        Question: {input}
        SQL:
        """)

        db_chain = SQLDatabaseChain.from_llm(
            llm,
            db,
            prompt=prompt_template,
            return_intermediate_steps=True,
            verbose=True
        )

        response = db_chain(user_question)
        print("Raw LLM 응답:", response)

        # SQL 추출
        generated_sql = ""
        if isinstance(response, dict) and "intermediate_steps" in response:
            for step in response["intermediate_steps"]:
                if isinstance(step, str) and step.strip().upper().startswith("SELECT"):
                    generated_sql = step.strip()
                    break
        elif isinstance(response, str):
            generated_sql = response.strip()
        else:
            generated_sql = str(response).strip()

        print("최종 SQL:", generated_sql)

        with engine.connect() as conn:
            result = conn.execute(text(generated_sql))
            rows = [dict(row._mapping) for row in result]

        return func.HttpResponse(
            json.dumps({"answer": rows}, ensure_ascii=False),
            mimetype="application/json"
        )

    except Exception as e:
        print("LLM 실행 중 오류:", str(e))
        traceback.print_exc()
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
