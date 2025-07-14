import uuid
import logging
from typing import Dict, Any, List
from .clients import client_manager
from .time_utils import enrich_with_time_info

class DataProcessor:
    """BigQuery 데이터를 SQL Database에 저장하는 프로세서
    
    이 클래스는 Google Analytics 데이터를 가공하여 여러 테이블로 분류하고 저장하는 역할을 합니다.
    주요 기능:
    1. 원시 데이터를 6개의 정규화된 테이블로 변환
    2. 데이터 타입 변환 (예: 'Yes'/'No' 텍스트를 불리언으로)
    3. 중복 데이터 처리 방지
    4. 각 테이블별 데이터 삽입 처리
    """
    
    def __init__(self):
        """DataProcessor 초기화
        
        테이블 이름 정의, 성공 카운터 초기화, 중복 처리 방지를 위한 세션 키 세트 생성
        """
        # 테이블 이름 정의 (스키마 포함)
        self.tables = {
            "sessions": "ga_data.Sessions",
            "totals": "ga_data.Totals",
            "traffic": "ga_data.Traffic",
            "devicegeo": "ga_data.DeviceGeo",
            "hits": "ga_data.Hits",
            "products": "ga_data.HitsProduct"
        }
        self.success_count = {k: 0 for k in self.tables.keys()}
        # 세션 중복 처리를 방지하기 위한 세트
        self.processed_session_keys = set()
    
    def _convert_yes_no_to_boolean(self, value):
        """BigQuery의 'Yes'/'No' 텍스트 값을 불리언으로 변환합니다.
        
        Args:
            value: 변환할 값 ('Yes', 'No', True, False 또는 기타 값)
            
        Returns:
            bool 또는 None: 'Yes'/True는 True로, 'No'/False는 False로 변환, 그 외는 None
        """
        if value == 'Yes' or value == True:
            return True
        elif value == 'No' or value == False:
            return False
        else:
            return None  # NULL로 저장
    
    def process_row(self, row) -> None:
        """단일 행을 처리하여 SQL Database에 저장합니다.
        
        이 메서드는 BigQuery에서 가져온 한 행의 데이터를 여러 테이블로 분류하여 저장합니다.
        세션 레벨 데이터는 중복 처리를 방지하고, 히트 레벨 데이터는 모두 처리합니다.
        
        Args:
            row: BigQuery에서 가져온 데이터 행
            
        Raises:
            Exception: 데이터 처리 중 오류 발생 시
        """
        vid = str(row.fullVisitorId) if row.fullVisitorId else str(uuid.uuid4())
        primary_key = getattr(row, 'primary_key', None)

        try:
            # --- 세션 레벨 데이터 처리 (중복 방지) ---
            # primary_key가 있고, 아직 처리되지 않은 세션인 경우에만 세션 관련 데이터 삽입
            if primary_key and primary_key not in self.processed_session_keys:
                self._process_sessions_data(row, vid, primary_key)
                self._process_totals_data(row, vid, primary_key)
                self._process_traffic_data(row, vid, primary_key)
                self._process_devicegeo_data(row, vid, primary_key)
                # 처리된 세션으로 등록
                self.processed_session_keys.add(primary_key)
            
            # --- 히트 레벨 데이터 처리 ---
            # 히트 데이터가 없는 행(세션 정보만 있는 행)은 여기서 처리를 중단
            if getattr(row, 'hits_hitNumber', None) is None:
                return

            # 고유한 hitId 생성하여 하위 데이터(product)와 관계 형성
            hit_id = str(uuid.uuid4())
            
            self._process_hits_data(row, vid, primary_key, hit_id)
            # CustomDimensions 테이블이 삭제되었으므로 처리하지 않음
            self._process_products_data(row, vid, hit_id)
            
        except Exception as e:
            logging.error(f"행 처리 중 오류 발생 (fullVisitorId: {vid}, primary_key: {primary_key}): {e}")
            raise
    
    def _process_sessions_data(self, row, vid: str, primary_key: str) -> None:
        """Sessions 데이터를 처리합니다.
        
        세션 기본 정보(방문자 ID, 방문 번호, 날짜 등)를 Sessions 테이블에 저장합니다.
        
        Args:
            row: 원본 데이터 행
            vid (str): 방문자 ID
            primary_key (str): 세션 기본 키
        """
        sessions_data = [
            primary_key,
            vid,
            getattr(row, 'visitNumber', None),
            getattr(row, 'visitId', None),
            getattr(row, 'visitStartTime', None),
            getattr(row, 'date', None),
            getattr(row, 'fullVisitorId', None),
            getattr(row, 'channelGrouping', None),
            getattr(row, 'socialEngagementType', None)
        ]
        columns = [
            "primary_key", "visitorId", "visitNumber", "visitId", 
            "visitStartTime", "date", "fullVisitorId",
            "channelGrouping", "socialEngagementType"
        ]
        client_manager.execute_batch(self.tables["sessions"], [sessions_data], columns)
        self.success_count["sessions"] += 1
    
    def _process_totals_data(self, row, vid: str, primary_key: str) -> None:
        """Totals 데이터를 처리합니다.
        
        세션 집계 데이터(히트 수, 페이지뷰, 세션 시간 등)를 Totals 테이블에 저장합니다.
        
        Args:
            row: 원본 데이터 행
            vid (str): 방문자 ID
            primary_key (str): 세션 기본 키
        """
        new_visits = 1 if getattr(row, 'totals_newVisits', None) == 'New Visitor' else 0
        bounces = 1 if getattr(row, 'totals_bounces', None) == 'Bounce' else 0
        totals_data = [
            primary_key, vid, None, getattr(row, 'totals_hits', None),
            getattr(row, 'totals_pageviews', None), getattr(row, 'totals_timeOnSite', None),
            bounces, getattr(row, 'totals_transactions', None), None,
            getattr(row, 'totals_totalTransactionRevenue', None),
            getattr(row, 'totals_sessionQualityDim', None),
            new_visits # 이전 코드에서 누락되었던 부분 추가
        ]
        columns = [
            "primary_key", "visitorId", "visits", "hits", "pageviews", 
            "timeOnSite", "bounces", "transactions", "transactionRevenue", 
            "totalTransactionRevenue", "sessionQualityDim", "newVisits"
        ]
        client_manager.execute_batch(self.tables["totals"], [totals_data], columns)
        self.success_count["totals"] += 1
    
    def _process_traffic_data(self, row, vid: str, primary_key: str) -> None:
        """TrafficSource 데이터를 처리합니다.
        
        트래픽 소스 정보(캠페인, 소스, 미디엄 등)를 Traffic 테이블에 저장합니다.
        
        Args:
            row: 원본 데이터 행
            vid (str): 방문자 ID
            primary_key (str): 세션 기본 키
        """
        is_true_direct = self._convert_yes_no_to_boolean(getattr(row, 'trafficSource_isTrueDirect', None))
        traffic_data = [
            primary_key, vid, getattr(row, 'trafficSource_referralPath', None),
            getattr(row, 'trafficSource_campaign', None), getattr(row, 'trafficSource_source', None),
            getattr(row, 'trafficSource_medium', None), getattr(row, 'trafficSource_keyword', None),
            getattr(row, 'trafficSource_adContent', None), getattr(row, 'trafficSource_adPage', None),
            getattr(row, 'trafficSource_adSlot', None), getattr(row, 'trafficSource_adGclId', None),
            getattr(row, 'trafficSource_adNetworkType', None), None, is_true_direct
        ]
        columns = [
            "primary_key", "visitorId", "referralPath", "campaign", "source", 
            "medium", "keyword", "adContent", "adwordsPage", "adwordsSlot", 
            "gclId", "adNetworkType", "isVideoAd", "isTrueDirect"
        ]
        client_manager.execute_batch(self.tables["traffic"], [traffic_data], columns)
        self.success_count["traffic"] += 1
    
    def _process_devicegeo_data(self, row, vid: str, primary_key: str) -> None:
        """DeviceAndGeo 데이터를 처리합니다.
        
        디바이스 및 지역 정보(브라우저, OS, 국가, 도시 등)를 DeviceGeo 테이블에 저장합니다.
        
        Args:
            row: 원본 데이터 행
            vid (str): 방문자 ID
            primary_key (str): 세션 기본 키
        """
        devicegeo_data = [
            primary_key, vid, getattr(row, 'device_browser', None),
            getattr(row, 'device_operatingSystem', None), None, None,
            getattr(row, 'device_deviceCategory', None), getattr(row, 'geoNetwork_continent', None),
            getattr(row, 'geoNetwork_subContinent', None), getattr(row, 'geoNetwork_country', None),
            getattr(row, 'geoNetwork_region', None), getattr(row, 'geoNetwork_metro', None),
            getattr(row, 'geoNetwork_city', None), None
        ]
        columns = [
            "primary_key", "visitorId", "browser", "operatingSystem", "isMobile", 
            "javaEnabled", "deviceCategory", "continent", "subContinent", 
            "country", "region", "metro", "city", "networkDomain"
        ]
        client_manager.execute_batch(self.tables["devicegeo"], [devicegeo_data], columns)
        self.success_count["devicegeo"] += 1
    
    def _process_custom_data(self, row, vid: str, hit_id: str) -> None:
        """CustomDimensions 데이터를 처리합니다.
        
        참고: CustomDimensions 테이블이 삭제되었으므로 아무 작업도 하지 않습니다.
        
        Args:
            row: 원본 데이터 행
            vid (str): 방문자 ID
            hit_id (str): 히트 ID
        """
        # CustomDimensions 테이블이 삭제되었으므로 아무 작업도 하지 않음
        return
    
    def _process_hits_data(self, row, vid: str, primary_key: str, hit_id: str) -> None:
        """Hits 데이터를 처리합니다.
        
        페이지 조회 및 이벤트 정보(히트 번호, 시간, 페이지 경로 등)를 Hits 테이블에 저장합니다.
        
        Args:
            row: 원본 데이터 행
            vid (str): 방문자 ID
            primary_key (str): 세션 기본 키
            hit_id (str): 히트 ID
        """
        # 행동 타입 코드를 텍스트로 변환 (예: '1' -> 'Click')
        action_type_text = getattr(row, 'hits_eCommerceAction_action_type', None)
        action_type_map = {'Click': '1', 'Product Detail': '2', 'Add to Cart': '3', 'Remove from Cart': '4', 'Checkout': '5', 'Purchase': '6', 'Refund': '7'}
        action_type = action_type_map.get(action_type_text, None)
        
        # BigQuery의 'Yes'/'No' 텍스트를 불리언으로 변환
        is_interaction = self._convert_yes_no_to_boolean(getattr(row, 'hits_isInteraction', None))
        is_entrance = self._convert_yes_no_to_boolean(getattr(row, 'hits_isEntrance', None))
        is_exit = self._convert_yes_no_to_boolean(getattr(row, 'hits_isExit', None))
        has_social_source_referral = self._convert_yes_no_to_boolean(getattr(row, 'hits_social_hasSocialSourceReferral', None))
        
        hits_data = [
            hit_id, primary_key, vid, getattr(row, 'hits_hitNumber', None),
            getattr(row, 'hits_time', None), getattr(row, 'hits_hour', None),
            getattr(row, 'hits_minute', None), is_interaction,
            is_entrance, is_exit,
            getattr(row, 'hits_page_pagePath', None), None,
            getattr(row, 'hits_page_pageTitle', None), None,
            getattr(row, 'hits_transaction_transactionId', None), getattr(row, 'hits_appInfo_screenName', None),
            getattr(row, 'hits_appInfo_landingScreenName', None), getattr(row, 'hits_appInfo_exitScreenName', None),
            None, getattr(row, 'hits_eventInfo_eventCategory', None),
            getattr(row, 'hits_eventInfo_eventAction', None), getattr(row, 'hits_eventInfo_eventLabel', None),
            action_type, getattr(row, 'hits_type', None),
            getattr(row, 'hits_social_socialNetwork', None), has_social_source_referral,
            getattr(row, 'hits_contentGroup_contentGroup1', None), getattr(row, 'hits_contentGroup_contentGroup2', None),
            getattr(row, 'hits_contentGroup_contentGroup3', None), getattr(row, 'hits_contentGroup_previousContentGroup1', None),
            getattr(row, 'hits_contentGroup_previousContentGroup2', None), getattr(row, 'hits_contentGroup_previousContentGroup3', None),
            getattr(row, 'hits_contentGroup_contentGroupUniqueViews1', None), getattr(row, 'hits_contentGroup_contentGroupUniqueViews2', None),
            getattr(row, 'hits_contentGroup_contentGroupUniqueViews3', None), getattr(row, 'hits_product_productQuantity', None), None
        ]
        columns = [
            "hitId", "primary_key", "visitorId", "hitNumber", "time", "hour", "minute", 
            "isInteraction", "isEntrance", "isExit", "pagePath", "hostname", 
            "pageTitle", "searchKeyword", "transactionId", "screenName", 
            "landingScreenName", "exitScreenName", "screenDepth", "eventCategory", 
            "eventAction", "eventLabel", "actionType", "hitType", "socialNetwork", 
            "hasSocialSourceReferral", "contentGroup1", "contentGroup2", 
            "contentGroup3", "previousContentGroup1", "previousContentGroup2", 
            "previousContentGroup3", "contentGroupUniqueViews1", 
            "contentGroupUniqueViews2", "contentGroupUniqueViews3", "product_productQuantity", "dataSource"
        ]
        client_manager.execute_batch(self.tables["hits"], [hits_data], columns)
        self.success_count["hits"] += 1
    
    def _process_products_data(self, row, vid: str, hit_id: str) -> None:
        """HitsProduct 데이터를 처리합니다.
        
        제품 정보(제품명, 카테고리, 가격 등)를 HitsProduct 테이블에 저장합니다.
        모든 제품 데이터는 hits_product_v2ProductName이 없어도 처리됩니다.
        
        Args:
            row: 원본 데이터 행
            vid (str): 방문자 ID
            hit_id (str): 히트 ID
        """
        # hits_product_v2ProductName이 없어도 데이터 처리 (조건 제거)
        
        # BigQuery의 'Yes'/'No' 텍스트를 불리언으로 변환
        is_impression = self._convert_yes_no_to_boolean(getattr(row, 'hits_product_isImpression', None))
        is_click = self._convert_yes_no_to_boolean(getattr(row, 'hits_product_isClick', None))
        
        products_data = [
            str(uuid.uuid4()), # productId (PK)
            hit_id,            # hitId (FK)
            vid,
            getattr(row, 'hits_hitNumber', None),
            getattr(row, 'hits_product_v2ProductName', None),
            getattr(row, 'hits_product_v2ProductCategory', None),
            getattr(row, 'hits_product_productBrand', None),
            getattr(row, 'hits_product_productPrice', None),
            None,
            is_impression,
            is_click,
            getattr(row, 'hits_product_productListName', None),
            getattr(row, 'hits_product_productListPosition', None)
        ]
        columns = [
            "productId", "hitId", "visitorId", "hitNumber", "v2ProductName", "v2ProductCategory", 
            "productBrand", "productPrice", "localProductPrice", "isImpression", 
            "isClick", "productListName", "productListPosition"
        ]
        client_manager.execute_batch(self.tables["products"], [products_data], columns)
        self.success_count["products"] += 1

    def get_success_summary(self) -> Dict[str, int]:
        """성공 카운트를 반환합니다.
        
        각 테이블별로 처리된 데이터 수를 딕셔너리 형태로 반환합니다.
        
        Returns:
            Dict[str, int]: 테이블별 성공 카운트
        """
        return self.success_count
    
    def reset_counters(self) -> None:
        """카운터를 초기화합니다.
        
        모든 테이블의 성공 카운트와 처리된 세션 키를 초기화합니다.
        """
        self.success_count = {k: 0 for k in self.tables.keys()}
        self.processed_session_keys = set() 