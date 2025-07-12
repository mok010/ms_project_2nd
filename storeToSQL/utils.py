import logging
import time
from typing import Dict, Any, List
from functools import wraps

def timing_decorator(func):
    """함수 실행 시간을 측정하는 데코레이터"""
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
    """안전하게 객체의 속성을 가져오는 함수"""
    try:
        return getattr(obj, attr_name, default)
    except Exception:
        return default

def format_success_message(success_counts: Dict[str, int]) -> str:
    """성공 메시지를 포맷팅하는 함수"""
    if not success_counts:
        return "❌ 처리된 데이터가 없습니다."
    
    total = sum(success_counts.values())
    summary_lines = [f"📊 총 처리된 데이터: {total}개"]
    
    for table_name, count in success_counts.items():
        if count > 0:
            summary_lines.append(f"  • {table_name}: {count}개")
    
    return "\n".join(summary_lines)

def validate_environment_variables() -> bool:
    """환경 변수 검증"""
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
    """함수 시작 로그"""
    logging.info(f"🚀 {func_name} 시작")
    if kwargs:
        logging.info(f"📋 파라미터: {kwargs}")

def log_function_end(func_name: str, success: bool, **kwargs):
    """함수 종료 로그"""
    status = "✅ 성공" if success else "❌ 실패"
    logging.info(f"{status} {func_name} 완료")
    if kwargs:
        logging.info(f"📊 결과: {kwargs}")

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.metrics = {}
    
    def start(self):
        """모니터링 시작"""
        self.start_time = time.time()
        self.metrics = {}
    
    def end(self):
        """모니터링 종료"""
        self.end_time = time.time()
        if self.start_time:
            self.metrics['total_time'] = self.end_time - self.start_time
    
    def add_metric(self, name: str, value: Any):
        """메트릭 추가"""
        self.metrics[name] = value
    
    def get_summary(self) -> Dict[str, Any]:
        """성능 요약 반환"""
        return self.metrics.copy()
    
    def log_summary(self):
        """성능 요약 로그 출력"""
        if self.metrics:
            logging.info(f"📈 성능 요약: {self.metrics}")

def create_error_response(error: Exception, context: str = "") -> str:
    """에러 응답 생성"""
    error_msg = f"❌ 오류 발생"
    if context:
        error_msg += f" ({context})"
    error_msg += f": {str(error)}"
    return error_msg 