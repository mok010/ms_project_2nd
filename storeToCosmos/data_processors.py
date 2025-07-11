import uuid
import logging
from typing import Dict, Any, List
from .clients import client_manager
from .time_utils import enrich_with_time_info

class DataProcessor:
    """BigQuery 데이터를 CosmosDB에 저장하는 프로세서"""
    
    def __init__(self):
        self.containers = client_manager.containers
        self.success_count = {k: 0 for k in self.containers.keys()}
    
    def process_row(self, row) -> None:
        """단일 행을 처리하여 CosmosDB에 저장합니다."""
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
        sessions_data = {
            "id": f"{vid}_session",
            "visitorId": vid,
            "visitNumber": getattr(row, 'visitNumber', None),
            "visitId": getattr(row, 'visitId', None),
            "visitStartTime": getattr(row, 'visitStartTime', None),
            "date": getattr(row, 'date', None),
            "fullVisitorId": getattr(row, 'fullVisitorId', None),
            "clientId": getattr(row, 'clientId', None),
            "channelGrouping": getattr(row, 'channelGrouping', None),
            "socialEngagementType": getattr(row, 'socialEngagementType', None)
        }
        
        # 시간 정보 추가
        sessions_data = enrich_with_time_info(sessions_data, "visitStartTime")
        
        self.containers["sessions"].upsert_item(sessions_data)
        self.success_count["sessions"] += 1
    
    def _process_totals_data(self, row, vid: str) -> None:
        """Totals 데이터를 처리합니다."""
        totals_data = {
            "id": f"{vid}_totals",
            "visitorId": vid,
            "visits": getattr(row, 'visits', None),
            "hits": getattr(row, 'hits', None),
            "pageviews": getattr(row, 'pageviews', None),
            "timeOnSite": getattr(row, 'timeOnSite', None),
            "bounces": getattr(row, 'bounces', None),
            "transactions": getattr(row, 'transactions', None),
            "transactionRevenue": getattr(row, 'transactionRevenue', None),
            "newVisits": getattr(row, 'newVisits', None),
            "totalTransactionRevenue": getattr(row, 'totalTransactionRevenue', None),
            "sessionQualityDim": getattr(row, 'sessionQualityDim', None)
        }
        
        self.containers["totals"].upsert_item(totals_data)
        self.success_count["totals"] += 1
    
    def _process_traffic_data(self, row, vid: str) -> None:
        """TrafficSource 데이터를 처리합니다."""
        traffic_data = {
            "id": f"{vid}_traffic",
            "visitorId": vid,
            "referralPath": getattr(row, 'referralPath', None),
            "campaign": getattr(row, 'campaign', None),
            "source": getattr(row, 'source', None),
            "medium": getattr(row, 'medium', None),
            "keyword": getattr(row, 'keyword', None),
            "adContent": getattr(row, 'adContent', None),
            "adwordsPage": getattr(row, 'page', None),
            "adwordsSlot": getattr(row, 'slot', None),
            "gclId": getattr(row, 'gclId', None),
            "adNetworkType": getattr(row, 'adNetworkType', None),
            "isVideoAd": getattr(row, 'isVideoAd', None),
            "isTrueDirect": getattr(row, 'isTrueDirect', None)
        }
        
        self.containers["traffic"].upsert_item(traffic_data)
        self.success_count["traffic"] += 1
    
    def _process_devicegeo_data(self, row, vid: str) -> None:
        """DeviceAndGeo 데이터를 처리합니다."""
        devicegeo_data = {
            "id": f"{vid}_devicegeo",
            "visitorId": vid,
            "browser": getattr(row, 'browser', None),
            "operatingSystem": getattr(row, 'operatingSystem', None),
            "isMobile": getattr(row, 'isMobile', None),
            "javaEnabled": getattr(row, 'javaEnabled', None),
            "deviceCategory": getattr(row, 'deviceCategory', None),
            "continent": getattr(row, 'continent', None),
            "subContinent": getattr(row, 'subContinent', None),
            "country": getattr(row, 'country', None),
            "region": getattr(row, 'region', None),
            "metro": getattr(row, 'metro', None),
            "city": getattr(row, 'city', None),
            "networkDomain": getattr(row, 'networkDomain', None)
        }
        
        self.containers["devicegeo"].upsert_item(devicegeo_data)
        self.success_count["devicegeo"] += 1
    
    def _process_custom_data(self, row, vid: str) -> None:
        """CustomDimensions 데이터를 처리합니다."""
        custom_data = {
            "id": f"{vid}_custom_{getattr(row, 'index', 0)}",
            "visitorId": vid,
            "index": getattr(row, 'index', None),
            "value": getattr(row, 'value', None)
        }
        
        self.containers["custom"].upsert_item(custom_data)
        self.success_count["custom"] += 1
    
    def _process_hits_data(self, row, vid: str) -> None:
        """Hits 데이터를 처리합니다."""
        hits_data = {
            "id": f"{vid}_hit_{getattr(row, 'hitNumber', 0)}",
            "visitorId": vid,
            "hitNumber": getattr(row, 'hitNumber', None),
            "time": getattr(row, 'time', None),
            "hour": getattr(row, 'hour', None),
            "minute": getattr(row, 'minute', None),
            "isInteraction": getattr(row, 'isInteraction', None),
            "isEntrance": getattr(row, 'isEntrance', None),
            "isExit": getattr(row, 'isExit', None),
            "pagePath": getattr(row, 'pagePath', None),
            "hostname": getattr(row, 'hostname', None),
            "pageTitle": getattr(row, 'pageTitle', None),
            "searchKeyword": getattr(row, 'searchKeyword', None),
            "transactionId": getattr(row, 'transactionId', None),
            "screenName": getattr(row, 'screenName', None),
            "landingScreenName": getattr(row, 'landingScreenName', None),
            "exitScreenName": getattr(row, 'exitScreenName', None),
            "screenDepth": getattr(row, 'screenDepth', None),
            "eventCategory": getattr(row, 'eventCategory', None),
            "eventAction": getattr(row, 'eventAction', None),
            "eventLabel": getattr(row, 'eventLabel', None),
            "actionType": getattr(row, 'action_type', None),
            "hitType": getattr(row, 'type', None),
            "socialNetwork": getattr(row, 'socialNetwork', None),
            "hasSocialSourceReferral": getattr(row, 'hasSocialSourceReferral', None),
            "contentGroup1": getattr(row, 'contentGroup1', None),
            "contentGroup2": getattr(row, 'contentGroup2', None),
            "contentGroup3": getattr(row, 'contentGroup3', None),
            "previousContentGroup1": getattr(row, 'previousContentGroup1', None),
            "previousContentGroup2": getattr(row, 'previousContentGroup2', None),
            "previousContentGroup3": getattr(row, 'previousContentGroup3', None),
            "contentGroupUniqueViews1": getattr(row, 'contentGroupUniqueViews1', None),
            "contentGroupUniqueViews2": getattr(row, 'contentGroupUniqueViews2', None),
            "contentGroupUniqueViews3": getattr(row, 'contentGroupUniqueViews3', None),
            "dataSource": getattr(row, 'dataSource', None)
        }
        
        self.containers["hits"].upsert_item(hits_data)
        self.success_count["hits"] += 1
    
    def _process_products_data(self, row, vid: str) -> None:
        """HitsProduct 데이터를 처리합니다."""
        products_data = {
            "id": f"{vid}_product_{getattr(row, 'hitNumber', 0)}",
            "visitorId": vid,
            "v2ProductName": getattr(row, 'v2ProductName', None),
            "v2ProductCategory": getattr(row, 'v2ProductCategory', None),
            "productBrand": getattr(row, 'productBrand', None),
            "productPrice": getattr(row, 'productPrice', None),
            "localProductPrice": getattr(row, 'localProductPrice', None),
            "isImpression": getattr(row, 'isImpression', None),
            "isClick": getattr(row, 'isClick', None),
            "productListName": getattr(row, 'productListName', None),
            "productListPosition": getattr(row, 'productListPosition', None)
        }
        
        self.containers["products"].upsert_item(products_data)
        self.success_count["products"] += 1
    
    def get_success_summary(self) -> Dict[str, int]:
        """성공적으로 처리된 데이터 개수를 반환합니다."""
        return self.success_count.copy()
    
    def reset_counters(self) -> None:
        """카운터를 초기화합니다."""
        self.success_count = {k: 0 for k in self.containers.keys()} 