from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class AnalyticsSession:
    """Google Analytics 세션 데이터 모델"""
    visitorId: str
    visitNumber: Optional[int]
    visitId: Optional[str]
    visitStartTime: Optional[int]
    date: Optional[str]
    fullVisitorId: Optional[str]
    clientId: Optional[str]
    channelGrouping: Optional[str]
    socialEngagementType: Optional[str]

@dataclass
class AnalyticsTotals:
    """Google Analytics 총계 데이터 모델"""
    visitorId: str
    visits: Optional[int]
    hits: Optional[int]
    pageviews: Optional[int]
    timeOnSite: Optional[int]
    bounces: Optional[int]
    transactions: Optional[int]
    transactionRevenue: Optional[float]
    newVisits: Optional[int]
    totalTransactionRevenue: Optional[float]
    sessionQualityDim: Optional[int]

@dataclass
class AnalyticsTrafficSource:
    """Google Analytics 트래픽 소스 데이터 모델"""
    visitorId: str
    referralPath: Optional[str]
    campaign: Optional[str]
    source: Optional[str]
    medium: Optional[str]
    keyword: Optional[str]
    adContent: Optional[str]
    adwordsPage: Optional[str]
    adwordsSlot: Optional[str]
    gclId: Optional[str]
    adNetworkType: Optional[str]
    isVideoAd: Optional[bool]
    isTrueDirect: Optional[bool]

@dataclass
class AnalyticsDeviceGeo:
    """Google Analytics 디바이스 및 지리 데이터 모델"""
    visitorId: str
    browser: Optional[str]
    operatingSystem: Optional[str]
    isMobile: Optional[bool]
    javaEnabled: Optional[bool]
    deviceCategory: Optional[str]
    continent: Optional[str]
    subContinent: Optional[str]
    country: Optional[str]
    region: Optional[str]
    metro: Optional[str]
    city: Optional[str]
    networkDomain: Optional[str]

@dataclass
class AnalyticsCustomDimension:
    """Google Analytics 커스텀 차원 데이터 모델"""
    visitorId: str
    index: Optional[int]
    value: Optional[str]

@dataclass
class AnalyticsHit:
    """Google Analytics 히트 데이터 모델"""
    visitorId: str
    hitNumber: Optional[int]
    time: Optional[int]
    hour: Optional[int]
    minute: Optional[int]
    isInteraction: Optional[bool]
    isEntrance: Optional[bool]
    isExit: Optional[bool]
    pagePath: Optional[str]
    hostname: Optional[str]
    pageTitle: Optional[str]
    searchKeyword: Optional[str]
    transactionId: Optional[str]
    screenName: Optional[str]
    landingScreenName: Optional[str]
    exitScreenName: Optional[str]
    screenDepth: Optional[int]
    eventCategory: Optional[str]
    eventAction: Optional[str]
    eventLabel: Optional[str]
    actionType: Optional[str]
    hitType: Optional[str]
    socialNetwork: Optional[str]
    hasSocialSourceReferral: Optional[bool]
    contentGroup1: Optional[str]
    contentGroup2: Optional[str]
    contentGroup3: Optional[str]
    previousContentGroup1: Optional[str]
    previousContentGroup2: Optional[str]
    previousContentGroup3: Optional[str]
    contentGroupUniqueViews1: Optional[int]
    contentGroupUniqueViews2: Optional[int]
    contentGroupUniqueViews3: Optional[int]
    dataSource: Optional[str]

@dataclass
class AnalyticsProduct:
    """Google Analytics 제품 데이터 모델"""
    visitorId: str
    v2ProductName: Optional[str]
    v2ProductCategory: Optional[str]
    productBrand: Optional[str]
    productPrice: Optional[float]
    localProductPrice: Optional[float]
    isImpression: Optional[bool]
    isClick: Optional[bool]
    productListName: Optional[str]
    productListPosition: Optional[int]

class DataModels:
    """데이터 모델 팩토리 클래스"""
    
    @staticmethod
    def create_session_from_row(row, visitor_id: str) -> AnalyticsSession:
        """BigQuery 행에서 세션 모델을 생성합니다."""
        return AnalyticsSession(
            visitorId=visitor_id,
            visitNumber=getattr(row, 'visitNumber', None),
            visitId=getattr(row, 'visitId', None),
            visitStartTime=getattr(row, 'visitStartTime', None),
            date=getattr(row, 'date', None),
            fullVisitorId=getattr(row, 'fullVisitorId', None),
            clientId=getattr(row, 'clientId', None),
            channelGrouping=getattr(row, 'channelGrouping', None),
            socialEngagementType=getattr(row, 'socialEngagementType', None)
        )
    
    @staticmethod
    def create_totals_from_row(row, visitor_id: str) -> AnalyticsTotals:
        """BigQuery 행에서 총계 모델을 생성합니다."""
        return AnalyticsTotals(
            visitorId=visitor_id,
            visits=getattr(row, 'visits', None),
            hits=getattr(row, 'hits', None),
            pageviews=getattr(row, 'pageviews', None),
            timeOnSite=getattr(row, 'timeOnSite', None),
            bounces=getattr(row, 'bounces', None),
            transactions=getattr(row, 'transactions', None),
            transactionRevenue=getattr(row, 'transactionRevenue', None),
            newVisits=getattr(row, 'newVisits', None),
            totalTransactionRevenue=getattr(row, 'totalTransactionRevenue', None),
            sessionQualityDim=getattr(row, 'sessionQualityDim', None)
        )
    
    @staticmethod
    def create_traffic_from_row(row, visitor_id: str) -> AnalyticsTrafficSource:
        """BigQuery 행에서 트래픽 소스 모델을 생성합니다."""
        return AnalyticsTrafficSource(
            visitorId=visitor_id,
            referralPath=getattr(row, 'referralPath', None),
            campaign=getattr(row, 'campaign', None),
            source=getattr(row, 'source', None),
            medium=getattr(row, 'medium', None),
            keyword=getattr(row, 'keyword', None),
            adContent=getattr(row, 'adContent', None),
            adwordsPage=getattr(row, 'page', None),
            adwordsSlot=getattr(row, 'slot', None),
            gclId=getattr(row, 'gclId', None),
            adNetworkType=getattr(row, 'adNetworkType', None),
            isVideoAd=getattr(row, 'isVideoAd', None),
            isTrueDirect=getattr(row, 'isTrueDirect', None)
        )
    
    @staticmethod
    def create_devicegeo_from_row(row, visitor_id: str) -> AnalyticsDeviceGeo:
        """BigQuery 행에서 디바이스/지리 모델을 생성합니다."""
        return AnalyticsDeviceGeo(
            visitorId=visitor_id,
            browser=getattr(row, 'browser', None),
            operatingSystem=getattr(row, 'operatingSystem', None),
            isMobile=getattr(row, 'isMobile', None),
            javaEnabled=getattr(row, 'javaEnabled', None),
            deviceCategory=getattr(row, 'deviceCategory', None),
            continent=getattr(row, 'continent', None),
            subContinent=getattr(row, 'subContinent', None),
            country=getattr(row, 'country', None),
            region=getattr(row, 'region', None),
            metro=getattr(row, 'metro', None),
            city=getattr(row, 'city', None),
            networkDomain=getattr(row, 'networkDomain', None)
        )
    
    @staticmethod
    def create_custom_from_row(row, visitor_id: str) -> AnalyticsCustomDimension:
        """BigQuery 행에서 커스텀 차원 모델을 생성합니다."""
        return AnalyticsCustomDimension(
            visitorId=visitor_id,
            index=getattr(row, 'index', None),
            value=getattr(row, 'value', None)
        )
    
    @staticmethod
    def create_hit_from_row(row, visitor_id: str) -> AnalyticsHit:
        """BigQuery 행에서 히트 모델을 생성합니다."""
        return AnalyticsHit(
            visitorId=visitor_id,
            hitNumber=getattr(row, 'hitNumber', None),
            time=getattr(row, 'time', None),
            hour=getattr(row, 'hour', None),
            minute=getattr(row, 'minute', None),
            isInteraction=getattr(row, 'isInteraction', None),
            isEntrance=getattr(row, 'isEntrance', None),
            isExit=getattr(row, 'isExit', None),
            pagePath=getattr(row, 'pagePath', None),
            hostname=getattr(row, 'hostname', None),
            pageTitle=getattr(row, 'pageTitle', None),
            searchKeyword=getattr(row, 'searchKeyword', None),
            transactionId=getattr(row, 'transactionId', None),
            screenName=getattr(row, 'screenName', None),
            landingScreenName=getattr(row, 'landingScreenName', None),
            exitScreenName=getattr(row, 'exitScreenName', None),
            screenDepth=getattr(row, 'screenDepth', None),
            eventCategory=getattr(row, 'eventCategory', None),
            eventAction=getattr(row, 'eventAction', None),
            eventLabel=getattr(row, 'eventLabel', None),
            actionType=getattr(row, 'action_type', None),
            hitType=getattr(row, 'type', None),
            socialNetwork=getattr(row, 'socialNetwork', None),
            hasSocialSourceReferral=getattr(row, 'hasSocialSourceReferral', None),
            contentGroup1=getattr(row, 'contentGroup1', None),
            contentGroup2=getattr(row, 'contentGroup2', None),
            contentGroup3=getattr(row, 'contentGroup3', None),
            previousContentGroup1=getattr(row, 'previousContentGroup1', None),
            previousContentGroup2=getattr(row, 'previousContentGroup2', None),
            previousContentGroup3=getattr(row, 'previousContentGroup3', None),
            contentGroupUniqueViews1=getattr(row, 'contentGroupUniqueViews1', None),
            contentGroupUniqueViews2=getattr(row, 'contentGroupUniqueViews2', None),
            contentGroupUniqueViews3=getattr(row, 'contentGroupUniqueViews3', None),
            dataSource=getattr(row, 'dataSource', None)
        )
    
    @staticmethod
    def create_product_from_row(row, visitor_id: str) -> AnalyticsProduct:
        """BigQuery 행에서 제품 모델을 생성합니다."""
        return AnalyticsProduct(
            visitorId=visitor_id,
            v2ProductName=getattr(row, 'v2ProductName', None),
            v2ProductCategory=getattr(row, 'v2ProductCategory', None),
            productBrand=getattr(row, 'productBrand', None),
            productPrice=getattr(row, 'productPrice', None),
            localProductPrice=getattr(row, 'localProductPrice', None),
            isImpression=getattr(row, 'isImpression', None),
            isClick=getattr(row, 'isClick', None),
            productListName=getattr(row, 'productListName', None),
            productListPosition=getattr(row, 'productListPosition', None)
        ) 