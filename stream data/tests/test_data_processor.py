import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from collections import namedtuple

# 상위 디렉토리를 import 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storeToSQL.data_processors import DataProcessor

class TestDataProcessor(unittest.TestCase):
    """DataProcessor 클래스에 대한 단위 테스트"""
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        # client_manager를 모킹
        self.patcher = patch('storeToSQL.data_processors.client_manager')
        self.mock_client_manager = self.patcher.start()
        self.mock_client_manager.execute_batch = MagicMock()
        
        # DataProcessor 인스턴스 생성
        self.processor = DataProcessor()
    
    def tearDown(self):
        """각 테스트 후에 실행되는 정리"""
        self.patcher.stop()
    
    def test_init(self):
        """초기화 테스트: processed_hit_keys 세트가 올바르게 초기화되는지 확인"""
        self.assertIsInstance(self.processor.processed_hit_keys, set)
        self.assertEqual(len(self.processor.processed_hit_keys), 0)
    
    def test_duplicate_hit_key_handling(self):
        """중복 hit_key 처리 테스트: 중복된 hit_key를 가진 데이터가 올바르게 건너뛰어지는지 확인"""
        # 테스트용 행 데이터 생성 (namedtuple 사용)
        Row = namedtuple('Row', ['fullVisitorId', 'primary_key', 'session_key', 'hit_key', 'hits_hitNumber'])
        
        # 첫 번째 행: 새로운 hit_key
        row1 = Row(
            fullVisitorId='123456',
            primary_key='pk-1',
            session_key='session-1',
            hit_key='hit-1',
            hits_hitNumber=1
        )
        
        # 두 번째 행: 중복된 hit_key
        row2 = Row(
            fullVisitorId='123456',
            primary_key='pk-1',
            session_key='session-1',
            hit_key='hit-1',
            hits_hitNumber=1
        )
        
        # _process_hits_data 메서드를 모킹하여 호출 여부 추적
        original_method = self.processor._process_hits_data
        self.processor._process_hits_data = MagicMock(wraps=original_method)
        
        # 첫 번째 행 처리
        self.processor._process_hits_data(row1, '123456', 'pk-1', 'session-1', 'hit-1')
        
        # processed_hit_keys에 hit_key가 추가되었는지 확인
        self.assertIn('hit-1', self.processor.processed_hit_keys)
        self.assertEqual(len(self.processor.processed_hit_keys), 1)
        
        # 두 번째 행 처리
        self.processor._process_hits_data(row2, '123456', 'pk-1', 'session-1', 'hit-1')
        
        # 중복된 hit_key는 처리되지 않았는지 확인
        self.assertEqual(self.processor._process_hits_data.call_count, 2)  # 메서드는 두 번 호출됨
        self.assertEqual(self.mock_client_manager.execute_batch.call_count, 1)  # SQL 삽입은 한 번만 실행됨
    
    def test_reset_counters(self):
        """reset_counters 테스트: processed_hit_keys 세트가 초기화되는지 확인"""
        # 세트에 데이터 추가
        self.processor.processed_hit_keys.add('hit-1')
        self.processor.processed_hit_keys.add('hit-2')
        self.assertEqual(len(self.processor.processed_hit_keys), 2)
        
        # reset_counters 호출
        self.processor.reset_counters()
        
        # 세트가 비어있는지 확인
        self.assertEqual(len(self.processor.processed_hit_keys), 0)
    
    def test_process_products_data_with_duplicate_hit_key(self):
        """제품 데이터 처리 테스트: 중복된 hit_key를 가진 제품 데이터가 올바르게 처리되는지 확인"""
        # 테스트용 행 데이터 생성
        Row = namedtuple('Row', [
            'fullVisitorId', 'hit_key', 'product_hit_key', 'hits_hitNumber',
            'hits_product_v2ProductName', 'hits_product_productSKU'
        ])
        
        # 히트 키 추가
        self.processor.processed_hit_keys.add('hit-1')
        
        # 중복된 hit_key를 가진 제품 데이터
        row = Row(
            fullVisitorId='123456',
            hit_key='hit-1',
            product_hit_key='hit-1-prod1',
            hits_hitNumber=1,
            hits_product_v2ProductName='Product A',
            hits_product_productSKU='prod1'
        )
        
        # 제품 데이터 처리
        self.processor._process_products_data(row, '123456', 'hit-1', 'hit-1-prod1')
        
        # 제품 데이터가 처리되었는지 확인
        self.assertEqual(self.mock_client_manager.execute_batch.call_count, 1)
        self.assertEqual(self.processor.success_count['products'], 1)

if __name__ == '__main__':
    unittest.main() 