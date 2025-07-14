import logging
import azure.functions as func
from .clients import client_manager
from .queries import BigQueryQueries
from .data_processors import DataProcessor
from .utils import format_success_message, create_error_response

def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Function 메인 함수: BigQuery → SQL Database 데이터 전송
    
    이 함수는 HTTP 트리거로 실행되며, 다음과 같은 작업을 수행합니다:
    1. BigQuery에서 데이터 조회
    2. 조회된 데이터를 가공하여 SQL Database에 저장
    3. 처리 결과를 HTTP 응답으로 반환
    
    Returns:
        func.HttpResponse: 성공 시 처리된 데이터 요약, 실패 시 오류 메시지
    """
    logging.info("🚀 Azure Function Triggered: BigQuery → SQL Database")

    try:
        # 1. BigQuery에서 데이터 조회
        # BigQueryQueries 클래스에서 정의된 쿼리를 사용하여 Google Analytics 데이터를 가져옵니다
        logging.info("📊 BigQuery에서 데이터 조회 시작")
        query = BigQueryQueries.get_analytics_data_query()
        rows = client_manager.bq_client.query(query).result()
        
        # 2. 데이터 프로세서 초기화
        # DataProcessor 클래스는 데이터를 가공하고 SQL Database에 저장하는 역할을 합니다
        processor = DataProcessor()
        logging.info("🔧 데이터 프로세서 초기화 완료")
        
        # 3. 각 행 처리
        # 조회된 모든 행을 순회하며 처리합니다
        # 개별 행 처리 중 오류가 발생해도 전체 프로세스는 계속 진행됩니다
        processed_count = 0
        skipped_hit_keys = set()  # 중복으로 건너뛴 hit_key 추적
        
        for row in rows:
            try:
                # 행 처리 전 현재 processed_hit_keys 크기 저장
                hit_keys_before = len(processor.processed_hit_keys) if hasattr(processor, 'processed_hit_keys') else 0
                
                processor.process_row(row)
                processed_count += 1
                
                # 행 처리 후 새로 추가된 hit_key가 있는지 확인
                hit_keys_after = len(processor.processed_hit_keys) if hasattr(processor, 'processed_hit_keys') else 0
                if hit_keys_after == hit_keys_before and hasattr(row, 'hit_key'):
                    # hit_key가 추가되지 않았다면 중복으로 건너뛴 것으로 간주
                    skipped_hit_keys.add(getattr(row, 'hit_key', None))
                
            except Exception as row_error:
                logging.error(f"❌ 행 처리 중 오류 (행 {processed_count}): {row_error}")
                continue  # 개별 행 오류는 건너뛰고 계속 진행
        
        # 4. 성공 요약 생성
        # 각 테이블별로 처리된 데이터 수와 중복 처리된 데이터 수를 요약하여 반환합니다
        success_summary = processor.get_success_summary()
        
        # 중복 처리 정보 수집
        duplicate_counts = {"hits": len(skipped_hit_keys)} if skipped_hit_keys else None
        
        summary_text = format_success_message(success_summary, duplicate_counts)
        
        # 중복 키 처리 정보 로깅
        if skipped_hit_keys:
            logging.info(f"🔄 중복으로 건너뛴 hit_key 수: {len(skipped_hit_keys)}")
        
        logging.info(f"✅ 처리 완료: {processed_count}개 행 처리됨")
        return func.HttpResponse(
            f"✅ 저장 완료:\n{summary_text}",
            status_code=200
        )

    except Exception as e:
        # 5. 오류 처리
        # 전체 프로세스 실행 중 발생한 오류를 로깅하고 클라이언트에게 반환합니다
        error_msg = create_error_response(e, "메인 함수")
        logging.error(error_msg)
        return func.HttpResponse(error_msg, status_code=500)
