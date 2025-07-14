import logging
import time
from typing import Dict, Any, List
from functools import wraps

def timing_decorator(func):
    """함수 실행 시간을 측정하는 데코레이터
    
    이 데코레이터는 함수의 실행 시간을 측정하여 로깅합니다.
    성능 최적화와 병목 현상 파악에 유용합니다.
    
    Args:
        func: 실행 시간을 측정할 함수
        
    Returns:
        function: 실행 시간 측정 기능이 추가된 래퍼 함수
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"⏱️ {func.__name__} 실행 시간: {execution_time:.2f}초")
        return result
    return wrapper

def safe_get_attr(obj, attr_name: str, default=None):
    """안전하게 객체의 속성을 가져오는 함수
    
    AttributeError 예외를 방지하고 객체에서 안전하게 속성을 가져옵니다.
    속성이 없는 경우 기본값을 반환합니다.
    
    Args:
        obj: 속성을 가져올 객체
        attr_name (str): 가져올 속성 이름
        default: 속성이 없을 경우 반환할 기본값
        
    Returns:
        Any: 속성 값 또는 기본값
    """
    try:
        return getattr(obj, attr_name, default)
    except Exception:
        return default

def format_success_message(success_counts: Dict[str, int], duplicate_counts: Dict[str, int] = None) -> str:
    """성공 메시지를 포맷팅하는 함수
    
    각 테이블별 처리된 데이터 수와 중복 처리된 데이터 수를 요약하여 사용자 친화적인 메시지로 변환합니다.
    
    Args:
        success_counts (Dict[str, int]): 테이블별 성공 카운트
        duplicate_counts (Dict[str, int], optional): 테이블별 중복 처리 카운트
        
    Returns:
        str: 포맷팅된 성공 메시지
    """
    if not success_counts:
        return "❌ 처리된 데이터가 없습니다."
    
    total = sum(success_counts.values())
    summary_lines = [f"📊 총 처리된 데이터: {total}개"]
    
    for table_name, count in success_counts.items():
        if count > 0:
            summary_lines.append(f"  • {table_name}: {count}개")
    
    # 중복 처리 정보가 있으면 추가
    if duplicate_counts and sum(duplicate_counts.values()) > 0:
        summary_lines.append(f"\n🔄 중복 처리된 데이터:")
        for table_name, count in duplicate_counts.items():
            if count > 0:
                summary_lines.append(f"  • {table_name}: {count}개")
    
    return "\n".join(summary_lines)

def validate_environment_variables() -> bool:
    """환경 변수 검증
    
    필수 환경 변수가 설정되어 있는지 확인합니다.
    누락된 환경 변수가 있으면 로그에 기록하고 False를 반환합니다.
    
    Returns:
        bool: 모든 필수 환경 변수가 설정되어 있으면 True, 아니면 False
    """
    required_vars = ["SQL_SERVER", "SQL_DATABASE", "SQL_USERNAME", "SQL_PASSWORD"]
    missing_vars = []
    
    import os
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logging.error(f"❌ 누락된 환경 변수: {', '.join(missing_vars)}")
        return False
    
    return True

def log_function_start(func_name: str, **kwargs):
    """함수 시작 로그
    
    함수 실행 시작을 로깅합니다. 선택적으로 함수 파라미터도 로깅할 수 있습니다.
    
    Args:
        func_name (str): 함수 이름
        **kwargs: 로깅할 추가 파라미터
    """
    logging.info(f"🚀 {func_name} 시작")
    if kwargs:
        logging.info(f"📋 파라미터: {kwargs}")

def log_function_end(func_name: str, success: bool, **kwargs):
    """함수 종료 로그
    
    함수 실행 종료를 로깅합니다. 성공 여부와 선택적으로 결과도 로깅할 수 있습니다.
    
    Args:
        func_name (str): 함수 이름
        success (bool): 함수 실행 성공 여부
        **kwargs: 로깅할 추가 결과 정보
    """
    status = "✅ 성공" if success else "❌ 실패"
    logging.info(f"{status} {func_name} 완료")
    if kwargs:
        logging.info(f"📊 결과: {kwargs}")

class PerformanceMonitor:
    """성능 모니터링 클래스
    
    함수나 코드 블록의 실행 시간과 성능 메트릭을 측정하고 기록합니다.
    디버깅과 성능 최적화에 유용합니다.
    """
    
    def __init__(self):
        """PerformanceMonitor 초기화"""
        self.start_time = None
        self.end_time = None
        self.metrics = {}
    
    def start(self):
        """모니터링 시작
        
        현재 시간을 기록하고 메트릭 딕셔너리를 초기화합니다.
        """
        self.start_time = time.time()
        self.metrics = {}
    
    def end(self):
        """모니터링 종료
        
        현재 시간을 기록하고 총 실행 시간을 계산합니다.
        """
        self.end_time = time.time()
        if self.start_time:
            self.metrics['total_time'] = self.end_time - self.start_time
    
    def add_metric(self, name: str, value: Any):
        """메트릭 추가
        
        사용자 정의 메트릭을 추가합니다.
        
        Args:
            name (str): 메트릭 이름
            value (Any): 메트릭 값
        """
        self.metrics[name] = value
    
    def get_summary(self) -> Dict[str, Any]:
        """성능 요약 반환
        
        수집된 모든 메트릭의 복사본을 반환합니다.
        
        Returns:
            Dict[str, Any]: 메트릭 이름과 값의 딕셔너리
        """
        return self.metrics.copy()
    
    def log_summary(self):
        """성능 요약 로그 출력
        
        수집된 모든 메트릭을 로그에 기록합니다.
        """
        if self.metrics:
            logging.info(f"📈 성능 요약: {self.metrics}")

def create_error_response(error: Exception, context: str = "") -> str:
    """에러 응답 생성
    
    사용자 친화적인 에러 메시지를 생성합니다.
    PRIMARY KEY 제약 조건 위반 오류의 경우 특별한 메시지를 제공합니다.
    
    Args:
        error (Exception): 발생한 예외 객체
        context (str, optional): 에러가 발생한 컨텍스트 설명
        
    Returns:
        str: 포맷팅된 에러 메시지
    """
    error_msg = f"❌ 오류 발생"
    if context:
        error_msg += f" ({context})"
    
    # PRIMARY KEY 제약 조건 위반 오류인 경우 특별 처리
    error_str = str(error)
    if "Violation of PRIMARY KEY constraint" in error_str and "Cannot insert duplicate key" in error_str:
        # 중복 키 값 추출 시도
        import re
        key_match = re.search(r"The duplicate key value is \((.*?)\)", error_str)
        duplicate_key = key_match.group(1) if key_match else "알 수 없음"
        
        error_msg += f": PRIMARY KEY 제약 조건 위반 - 중복 키 값: {duplicate_key}"
        error_msg += "\n💡 해결 방안: DataProcessor 클래스에 히트 키 중복 처리 로직이 추가되었습니다. 이 오류는 더 이상 발생하지 않을 것입니다."
    else:
        error_msg += f": {error_str}"
    
    return error_msg 