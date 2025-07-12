import logging
import azure.functions as func
from .clients import client_manager
from .queries import BigQueryQueries
from .data_processors import DataProcessor
from .utils import format_success_message, create_error_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function 메인 함수: BigQuery → SQL Database 데이터 전송"""
    logging.info("🚀 Azure Function Triggered: BigQuery → SQL Database")

    try:
        # BigQuery에서 데이터 조회
        logging.info("📊 BigQuery에서 데이터 조회 시작")
        query = BigQueryQueries.get_analytics_data_query()
        rows = client_manager.bq_client.query(query).result()
        
        # 데이터 프로세서 초기화
        processor = DataProcessor()
        logging.info("🔧 데이터 프로세서 초기화 완료")
        
        # 각 행 처리
        processed_count = 0
        for row in rows:
            try:
                processor.process_row(row)
                processed_count += 1
            except Exception as row_error:
                logging.error(f"❌ 행 처리 중 오류 (행 {processed_count}): {row_error}")
                continue  # 개별 행 오류는 건너뛰고 계속 진행
        
        # 성공 요약 생성
        success_summary = processor.get_success_summary()
        summary_text = format_success_message(success_summary)
        
        logging.info(f"✅ 처리 완료: {processed_count}개 행 처리됨")
        return func.HttpResponse(
            f"✅ 저장 완료:\n{summary_text}",
            status_code=200
        )

    except Exception as e:
        error_msg = create_error_response(e, "메인 함수")
        logging.error(error_msg)
        return func.HttpResponse(error_msg, status_code=500)
