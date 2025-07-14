from .config import BQ_DATE_SUFFIX, BQ_LIMIT, BQ_OFFSET

class BigQueryQueries:
    """BigQuery 쿼리를 관리하는 클래스
    
    이 클래스는 Google BigQuery에 보낼 SQL 쿼리를 정의합니다.
    주로 Google Analytics 데이터를 조회하는 복잡한 쿼리를 관리합니다.
    """
    
    @staticmethod
    def get_analytics_data_query():
        """Google Analytics 데이터를 조회하는 쿼리를 반환합니다.
        
        이 쿼리는 다음과 같은 주요 섹션으로 구성됩니다:
        1. 기본 정보 (primary_key, 날짜, 시간, 사용자 정보)
        2. 세션 총계 데이터 (방문 횟수, 페이지뷰, 세션 시간 등)
        3. 트래픽 소스 정보 (캠페인, 소스, 미디엄 등)
        4. 디바이스 및 지역 정보 (브라우저, OS, 국가 등)
        5. 커스텀 차원 (사용자 정의 데이터)
        6. 히트 정보 (페이지 조회, 이벤트 등)
        7. 제품 정보 (제품명, 카테고리, 가격 등)
        
        Returns:
            str: BigQuery에 보낼 SQL 쿼리문
        """
        # 참고: 이 쿼리는 bigquery-public-data.google_analytics_sample 데이터셋을 사용합니다.
        # BQ_DATASET과 BQ_TABLE_PREFIX 변수는 현재 이 쿼리에서 사용되지 않습니다.
        return f"""
        SELECT
        -- [Base]
            -- Primary Key : 고유 ID
            CONCAT(date, '-', FORMAT('%07d', ROW_NUMBER() OVER(PARTITION BY date ORDER BY visitStartTime))) AS primary_key,
            -- 세션 키 : 세션 고유 식별자
            CONCAT(t.fullVisitorId, '-', CAST(t.visitId AS STRING)) AS session_key,
            -- 히트 키 : 히트 고유 식별자
            CONCAT(t.fullVisitorId, '-', CAST(t.visitId AS STRING), '-', CAST(h.hitNumber AS STRING)) AS hit_key,
            -- 상품 히트 키 : 상품 히트 고유 식별자
            CONCAT(t.fullVisitorId, '-', CAST(t.visitId AS STRING), '-', CAST(h.hitNumber AS STRING), '-', IFNULL(p.productSKU, 'null')) AS product_hit_key,
            -- 날짜 & 시간
            t.date AS date, 
            t.visitStartTime AS visitStartTime, 
            FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', TIMESTAMP_SECONDS(visitStartTime), 'America/Los_Angeles') AS visitStartTimestamp,
            FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', TIMESTAMP_SECONDS(visitStartTime + CAST(h.time / 1000 AS INT64)), 'America/Los_Angeles') AS hitActualTimestamp,
            -- 사용자 정보
            t.fullVisitorId AS fullVisitorId, 
            t.visitId AS visitId, 
            t.visitNumber AS visitNumber, 
            t.channelGrouping AS channelGrouping, 
            t.socialEngagementType AS socialEngagementType, 

        -- [Totals]
            -- 전체 세션 정보
            CASE
                WHEN totals.newVisits = 1 THEN 'New Visitor'
                ELSE 'Returning Visitor'
            END AS totals_newVisits,
            CASE
                WHEN t.totals.bounces = 1 THEN 'Bounce'
                ELSE 'Non-Bounce'
            END AS totals_bounces,
            ROUND(t.totals.totalTransactionRevenue / 1000000, 2) AS totals_totalTransactionRevenue, 
            -- 특정 세션 내 정보
            t.totals.hits AS totals_hits, 
            t.totals.pageviews AS totals_pageviews, 
            t.totals.timeOnSite AS totals_timeOnSite, 
            t.totals.transactions AS totals_transactions, 
            t.totals.sessionQualityDim AS totals_sessionQualityDim, 

        -- [TrafficSource]
            t.trafficSource.campaign AS trafficSource_campaign, 
            t.trafficSource.source AS trafficSource_source, 
            t.trafficSource.medium AS trafficSource_medium, 
            t.trafficSource.referralPath AS trafficSource_referralPath, 
            t.trafficSource.keyword AS trafficSource_keyword, 
            IFNULL(t.trafficSource.isTrueDirect, FALSE) AS trafficSource_isTrueDirect,
            t.trafficSource.adContent AS trafficSource_adContent, 
            t.trafficSource.adwordsClickInfo.adNetworkType AS trafficSource_adNetworkType, 
            t.trafficSource.adwordsClickInfo.page AS trafficSource_adPage, 
            t.trafficSource.adwordsClickInfo.slot AS trafficSource_adSlot, 
            t.trafficSource.adwordsClickInfo.gclId AS trafficSource_adGclId, 

        -- [Device]
            t.device.deviceCategory AS device_deviceCategory, 
            t.device.browser AS device_browser, 
            t.device.operatingSystem AS device_operatingSystem, 

        -- [GeoNetwork]
            t.geoNetwork.continent AS geoNetwork_continent, 
            t.geoNetwork.subContinent AS geoNetwork_subContinent, 
            t.geoNetwork.country AS geoNetwork_country, 
            t.geoNetwork.region AS geoNetwork_region, 
            t.geoNetwork.metro AS geoNetwork_metro, 
            t.geoNetwork.city AS geoNetwork_city, 

        -- [CustomDimensions] (UNNEST)
            cd.index AS customDimensions_index, 
            cd.value AS customDimensions_value, 

        -- [Hits] (UNNEST)
            h.hitNumber AS hits_hitNumber, 
            h.time AS hits_time, 
            h.hour AS hits_hour, 
            h.minute AS hits_minute, 
            IFNULL(h.isInteraction, FALSE) AS hits_isInteraction,
            IFNULL(h.isEntrance, FALSE) AS hits_isEntrance,
            IFNULL(h.isExit, FALSE) AS hits_isExit,
            h.page.pagePath AS hits_page_pagePath, 
            h.page.pageTitle AS hits_page_pageTitle, 
            h.transaction.transactionId AS hits_transaction_transactionId, 
            h.appInfo.screenName AS hits_appInfo_screenName, 
            h.appInfo.landingScreenName AS hits_appInfo_landingScreenName, 
            h.appInfo.exitScreenName AS hits_appInfo_exitScreenName, 
            h.eventInfo.eventCategory AS hits_eventInfo_eventCategory, 
            h.eventInfo.eventAction AS hits_eventInfo_eventAction, 
            h.eventInfo.eventLabel AS hits_eventInfo_eventLabel, 

            -- 행동 정보 변환 (숫자 → 텍스트)
            CASE h.eCommerceAction.action_type
                WHEN '1' THEN 'Click'
                WHEN '2' THEN 'Product Detail'
                WHEN '3' THEN 'Add to Cart'
                WHEN '4' THEN 'Remove from Cart'
                WHEN '5' THEN 'Checkout'
                WHEN '6' THEN 'Purchase'
                WHEN '7' THEN 'Refund'
                WHEN '8' THEN 'Checkout options'
                ELSE 'Unknown'
            END AS hits_eCommerceAction_action_type,

            h.type AS hits_type, 
            h.social.socialNetwork AS hits_social_socialNetwork, 
            h.social.hasSocialSourceReferral AS hits_social_hasSocialSourceReferral, 
            h.contentGroup.contentGroup1 AS hits_contentGroup_contentGroup1, 
            h.contentGroup.contentGroup2 AS hits_contentGroup_contentGroup2, 
            h.contentGroup.contentGroup3 AS hits_contentGroup_contentGroup3, 
            h.contentGroup.previousContentGroup1 AS hits_contentGroup_previousContentGroup1, 
            h.contentGroup.previousContentGroup2 AS hits_contentGroup_previousContentGroup2, 
            h.contentGroup.previousContentGroup3 AS hits_contentGroup_previousContentGroup3, 
            h.contentGroup.contentGroupUniqueViews1 AS hits_contentGroup_contentGroupUniqueViews1, 
            h.contentGroup.contentGroupUniqueViews2 AS hits_contentGroup_contentGroupUniqueViews2, 
            h.contentGroup.contentGroupUniqueViews3 AS hits_contentGroup_contentGroupUniqueViews3, 

        -- [HitsProduct]
            p.v2ProductName AS hits_product_v2ProductName, 
            p.v2ProductCategory AS hits_product_v2ProductCategory, 
            p.productBrand AS hits_product_productBrand, 
            ROUND(p.productRevenue / 1000000, 2) AS hits_product_productRevenue, 
            ROUND(p.productPrice / 1000000, 2) AS hits_product_productPrice, 
            p.productQuantity AS hits_product_productQuantity, 
            IFNULL(p.isImpression, FALSE) AS hits_product_isImpression,
            IFNULL(p.isClick, FALSE) AS hits_product_isClick,
            p.productListName AS hits_product_productListName, 
            p.productListPosition AS hits_product_productListPosition,
            p.productSKU AS hits_product_productSKU

        FROM
            `bigquery-public-data.google_analytics_sample.ga_sessions_*` AS t
            LEFT JOIN UNNEST(t.customDimensions) AS cd
            LEFT JOIN UNNEST(t.hits) AS h
            LEFT JOIN UNNEST(h.product) AS p
        WHERE _TABLE_SUFFIX = '{BQ_DATE_SUFFIX}'
        OFFSET {BQ_OFFSET}
        LIMIT {BQ_LIMIT}
        """ 