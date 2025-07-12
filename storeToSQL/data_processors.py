import uuid
import logging
from typing import Dict, Any, List
from .clients import client_manager
from .time_utils import enrich_with_time_info

class DataProcessor:
    """BigQuery 데이터를 SQL Database에 저장하는 프로세서"""
    
    def __init__(self):
        # 테이블 이름 정의 (스키마 포함)
        self.tables = {
            "sessions": "ga_data.Sessions",
            "totals": "ga_data.Totals",
            "traffic": "ga_data.Traffic",
            "devicegeo": "ga_data.DeviceGeo",
            "custom": "ga_data.CustomDimensions",
            "hits": "ga_data.Hits",
            "products": "ga_data.HitsProduct"
        }
        self.success_count = {k: 0 for k in self.tables.keys()}
    
    def process_row(self, row) -> None:
        """단일 행을 처리하여 SQL Database에 저장합니다."""
        vid = str(row.visitorId) if row.visitorId else str(uuid.uuid4())
        
        try:
            # Sessions 데이터 처리
            self._process_sessions_data(row, vid)
            
            # Totals 데이터 처리
            self._process_totals_data(row, vid)
            
            # TrafficSource 데이터 처리
            self._process_traffic_data(row, vid)
            
            # DeviceAndGeo 데이터 처리
            self._process_devicegeo_data(row, vid)
            
            # CustomDimensions 데이터 처리
            self._process_custom_data(row, vid)
            
            # Hits 데이터 처리
            self._process_hits_data(row, vid)
            
            # HitsProduct 데이터 처리
            self._process_products_data(row, vid)
            
        except Exception as e:
            logging.error(f"행 처리 중 오류 발생 (visitorId: {vid}): {e}")
            raise
    
    def _process_sessions_data(self, row, vid: str) -> None:
        """Sessions 데이터를 처리합니다."""
        visit_start_time = getattr(row, 'visitStartTime', None)
        
        # 날짜 형식 변환 (필요한 경우)
        if visit_start_time:
            # 여기에 날짜 변환 로직 추가
            pass
            
        sessions_data = [
            vid,
            getattr(row, 'visitNumber', None),
            getattr(row, 'visitId', None),
            visit_start_time,
            getattr(row, 'date', None),
            getattr(row, 'fullVisitorId', None),
            getattr(row, 'channelGrouping', None),
            getattr(row, 'socialEngagementType', None)
        ]
        
        columns = [
            "visitorId", "visitNumber", "visitId", 
            "visitStartTime", "date", "fullVisitorId",
            "channelGrouping", "socialEngagementType"
        ]
        
        client_manager.execute_batch("ga_data.Sessions", [sessions_data], columns)
        self.success_count["sessions"] += 1
    
    def _process_totals_data(self, row, vid: str) -> None:
        """Totals 데이터를 처리합니다."""
        totals_data = [
            vid,
            getattr(row, 'visits', None),
            getattr(row, 'hits', None),
            getattr(row, 'pageviews', None),
            getattr(row, 'timeOnSite', None),
            getattr(row, 'bounces', None),
            getattr(row, 'transactions', None),
            getattr(row, 'transactionRevenue', None),
            getattr(row, 'newVisits', None),
            getattr(row, 'totalTransactionRevenue', None),
            getattr(row, 'sessionQualityDim', None)
        ]
        
        columns = [
            "visitorId", "visits", "hits", "pageviews", 
            "timeOnSite", "bounces", "transactions", "transactionRevenue", 
            "newVisits", "totalTransactionRevenue", "sessionQualityDim"
        ]
        
        client_manager.execute_batch("ga_data.Totals", [totals_data], columns)
        self.success_count["totals"] += 1
    
    def _process_traffic_data(self, row, vid: str) -> None:
        """TrafficSource 데이터를 처리합니다."""
        traffic_data = [
            vid,
            getattr(row, 'referralPath', None),
            getattr(row, 'campaign', None),
            getattr(row, 'source', None),
            getattr(row, 'medium', None),
            getattr(row, 'keyword', None),
            getattr(row, 'adContent', None),
            getattr(row, 'page', None),
            getattr(row, 'slot', None),
            getattr(row, 'gclId', None),
            getattr(row, 'adNetworkType', None),
            getattr(row, 'isVideoAd', None),
            getattr(row, 'isTrueDirect', None)
        ]
        
        columns = [
            "visitorId", "referralPath", "campaign", "source", 
            "medium", "keyword", "adContent", "adwordsPage", "adwordsSlot", 
            "gclId", "adNetworkType", "isVideoAd", "isTrueDirect"
        ]
        
        client_manager.execute_batch("ga_data.Traffic", [traffic_data], columns)
        self.success_count["traffic"] += 1
    
    def _process_devicegeo_data(self, row, vid: str) -> None:
        """DeviceAndGeo 데이터를 처리합니다."""
        devicegeo_data = [
            vid,
            getattr(row, 'browser', None),
            getattr(row, 'operatingSystem', None),
            getattr(row, 'isMobile', None),
            getattr(row, 'javaEnabled', None),
            getattr(row, 'deviceCategory', None),
            getattr(row, 'continent', None),
            getattr(row, 'subContinent', None),
            getattr(row, 'country', None),
            getattr(row, 'region', None),
            getattr(row, 'metro', None),
            getattr(row, 'city', None),
            getattr(row, 'networkDomain', None)
        ]
        
        columns = [
            "visitorId", "browser", "operatingSystem", "isMobile", 
            "javaEnabled", "deviceCategory", "continent", "subContinent", 
            "country", "region", "metro", "city", "networkDomain"
        ]
        
        client_manager.execute_batch("ga_data.DeviceGeo", [devicegeo_data], columns)
        self.success_count["devicegeo"] += 1
    
    def _process_custom_data(self, row, vid: str) -> None:
        """CustomDimensions 데이터를 처리합니다."""
        index = getattr(row, 'index', 0)
        
        custom_data = [
            vid,
            index,
            getattr(row, 'value', None)
        ]
        
        columns = ["visitorId", "dimensionIndex", "dimensionValue"]
        
        client_manager.execute_batch("ga_data.CustomDimensions", [custom_data], columns)
        self.success_count["custom"] += 1
    
    def _process_hits_data(self, row, vid: str) -> None:
        """Hits 데이터를 처리합니다."""
        hit_number = getattr(row, 'hitNumber', 0)
        
        hits_data = [
            vid,
            hit_number,
            getattr(row, 'time', None),
            getattr(row, 'hour', None),
            getattr(row, 'minute', None),
            getattr(row, 'isInteraction', None),
            getattr(row, 'isEntrance', None),
            getattr(row, 'isExit', None),
            getattr(row, 'pagePath', None),
            getattr(row, 'hostname', None),
            getattr(row, 'pageTitle', None),
            getattr(row, 'searchKeyword', None),
            getattr(row, 'transactionId', None),
            getattr(row, 'screenName', None),
            getattr(row, 'landingScreenName', None),
            getattr(row, 'exitScreenName', None),
            getattr(row, 'screenDepth', None),
            getattr(row, 'eventCategory', None),
            getattr(row, 'eventAction', None),
            getattr(row, 'eventLabel', None),
            getattr(row, 'action_type', None),
            getattr(row, 'type', None),
            getattr(row, 'socialNetwork', None),
            getattr(row, 'hasSocialSourceReferral', None),
            getattr(row, 'contentGroup1', None),
            getattr(row, 'contentGroup2', None),
            getattr(row, 'contentGroup3', None),
            getattr(row, 'previousContentGroup1', None),
            getattr(row, 'previousContentGroup2', None),
            getattr(row, 'previousContentGroup3', None),
            getattr(row, 'contentGroupUniqueViews1', None),
            getattr(row, 'contentGroupUniqueViews2', None),
            getattr(row, 'contentGroupUniqueViews3', None),
            getattr(row, 'dataSource', None)
        ]
        
        columns = [
            "visitorId", "hitNumber", "time", "hour", "minute", 
            "isInteraction", "isEntrance", "isExit", "pagePath", "hostname", 
            "pageTitle", "searchKeyword", "transactionId", "screenName", 
            "landingScreenName", "exitScreenName", "screenDepth", "eventCategory", 
            "eventAction", "eventLabel", "actionType", "hitType", "socialNetwork", 
            "hasSocialSourceReferral", "contentGroup1", "contentGroup2", 
            "contentGroup3", "previousContentGroup1", "previousContentGroup2", 
            "previousContentGroup3", "contentGroupUniqueViews1", 
            "contentGroupUniqueViews2", "contentGroupUniqueViews3", "dataSource"
        ]
        
        client_manager.execute_batch("ga_data.Hits", [hits_data], columns)
        self.success_count["hits"] += 1
    
    def _process_products_data(self, row, vid: str) -> None:
        """HitsProduct 데이터를 처리합니다."""
        hit_number = getattr(row, 'hitNumber', 0)
        
        products_data = [
            vid,
            hit_number,
            getattr(row, 'v2ProductName', None),
            getattr(row, 'v2ProductCategory', None),
            getattr(row, 'productBrand', None),
            getattr(row, 'productPrice', None),
            getattr(row, 'localProductPrice', None),
            getattr(row, 'isImpression', None),
            getattr(row, 'isClick', None),
            getattr(row, 'productListName', None),
            getattr(row, 'productListPosition', None)
        ]
        
        columns = [
            "visitorId", "hitNumber", "v2ProductName", "v2ProductCategory", 
            "productBrand", "productPrice", "localProductPrice", "isImpression", 
            "isClick", "productListName", "productListPosition"
        ]
        
        client_manager.execute_batch("ga_data.HitsProduct", [products_data], columns)
        self.success_count["products"] += 1
    
    def get_success_summary(self) -> Dict[str, int]:
        """성공적으로 처리된 데이터 개수를 반환합니다."""
        return self.success_count.copy()
    
    def reset_counters(self) -> None:
        """카운터를 초기화합니다."""
        self.success_count = {k: 0 for k in self.tables.keys()} 