from .config import BQ_DATASET, BQ_TABLE_PREFIX, BQ_DATE_SUFFIX, BQ_LIMIT

class BigQueryQueries:
    """BigQuery 쿼리를 관리하는 클래스"""
    
    @staticmethod
    def get_analytics_data_query():
        """Google Analytics 데이터를 조회하는 쿼리를 반환합니다."""
        return f"""
        SELECT
            t.visitorId, t.visitNumber, t.visitId, t.visitStartTime, t.date, t.fullVisitorId,
            t.clientId, t.channelGrouping, t.socialEngagementType,

            t.totals.visits, t.totals.hits, t.totals.pageviews, t.totals.timeOnSite,
            t.totals.bounces, t.totals.transactions, t.totals.transactionRevenue,
            t.totals.newVisits, t.totals.totalTransactionRevenue, t.totals.sessionQualityDim,

            t.trafficSource.referralPath, t.trafficSource.campaign, t.trafficSource.source,
            t.trafficSource.medium, t.trafficSource.keyword, t.trafficSource.adContent,
            t.trafficSource.adwordsClickInfo.page, t.trafficSource.adwordsClickInfo.slot,
            t.trafficSource.adwordsClickInfo.gclId, t.trafficSource.adwordsClickInfo.adNetworkType,
            t.trafficSource.adwordsClickInfo.isVideoAd, t.trafficSource.isTrueDirect,

            t.device.browser, t.device.operatingSystem, t.device.isMobile, t.device.javaEnabled,
            t.device.deviceCategory,

            t.geoNetwork.continent, t.geoNetwork.subContinent, t.geoNetwork.country,
            t.geoNetwork.region, t.geoNetwork.metro, t.geoNetwork.city, t.geoNetwork.networkDomain,

            cd.index, cd.value,

            h.hitNumber, h.time, h.hour, h.minute, h.isInteraction, h.isEntrance, h.isExit,
            h.page.pagePath, h.page.hostname, h.page.pageTitle, h.page.searchKeyword,
            h.transaction.transactionId, h.appInfo.screenName, h.appInfo.landingScreenName,
            h.appInfo.exitScreenName, h.appInfo.screenDepth, h.eventInfo.eventCategory,
            h.eventInfo.eventAction, h.eventInfo.eventLabel,
            h.eCommerceAction.action_type, h.type,
            h.social.socialNetwork, h.social.hasSocialSourceReferral,
            h.contentGroup.contentGroup1, h.contentGroup.contentGroup2, h.contentGroup.contentGroup3,
            h.contentGroup.previousContentGroup1, h.contentGroup.previousContentGroup2, h.contentGroup.previousContentGroup3,
            h.contentGroup.contentGroupUniqueViews1, h.contentGroup.contentGroupUniqueViews2, h.contentGroup.contentGroupUniqueViews3,
            h.dataSource,

            p.v2ProductName, p.v2ProductCategory, p.productBrand, p.productPrice,
            p.localProductPrice, p.isImpression, p.isClick,
            p.productListName, p.productListPosition

        FROM `{BQ_DATASET}.{BQ_TABLE_PREFIX}*` AS t
        LEFT JOIN UNNEST(t.customDimensions) AS cd
        LEFT JOIN UNNEST(t.hits) AS h
        LEFT JOIN UNNEST(h.product) AS p
        WHERE _TABLE_SUFFIX = '{BQ_DATE_SUFFIX}'
        LIMIT {BQ_LIMIT}
        """
    
    @staticmethod
    def get_custom_query(date_suffix=None, limit=None):
        """사용자 정의 쿼리를 생성합니다."""
        date_suffix = date_suffix or BQ_DATE_SUFFIX
        limit = limit or BQ_LIMIT
        
        return f"""
        SELECT
            t.visitorId, t.visitNumber, t.visitId, t.visitStartTime, t.date, t.fullVisitorId,
            t.clientId, t.channelGrouping, t.socialEngagementType,

            t.totals.visits, t.totals.hits, t.totals.pageviews, t.totals.timeOnSite,
            t.totals.bounces, t.totals.transactions, t.totals.transactionRevenue,
            t.totals.newVisits, t.totals.totalTransactionRevenue, t.totals.sessionQualityDim,

            t.trafficSource.referralPath, t.trafficSource.campaign, t.trafficSource.source,
            t.trafficSource.medium, t.trafficSource.keyword, t.trafficSource.adContent,
            t.trafficSource.adwordsClickInfo.page, t.trafficSource.adwordsClickInfo.slot,
            t.trafficSource.adwordsClickInfo.gclId, t.trafficSource.adwordsClickInfo.adNetworkType,
            t.trafficSource.adwordsClickInfo.isVideoAd, t.trafficSource.isTrueDirect,

            t.device.browser, t.device.operatingSystem, t.device.isMobile, t.device.javaEnabled,
            t.device.deviceCategory,

            t.geoNetwork.continent, t.geoNetwork.subContinent, t.geoNetwork.country,
            t.geoNetwork.region, t.geoNetwork.metro, t.geoNetwork.city, t.geoNetwork.networkDomain,

            cd.index, cd.value,

            h.hitNumber, h.time, h.hour, h.minute, h.isInteraction, h.isEntrance, h.isExit,
            h.page.pagePath, h.page.hostname, h.page.pageTitle, h.page.searchKeyword,
            h.transaction.transactionId, h.appInfo.screenName, h.appInfo.landingScreenName,
            h.appInfo.exitScreenName, h.appInfo.screenDepth, h.eventInfo.eventCategory,
            h.eventInfo.eventAction, h.eventInfo.eventLabel,
            h.eCommerceAction.action_type, h.type,
            h.social.socialNetwork, h.social.hasSocialSourceReferral,
            h.contentGroup.contentGroup1, h.contentGroup.contentGroup2, h.contentGroup.contentGroup3,
            h.contentGroup.previousContentGroup1, h.contentGroup.previousContentGroup2, h.contentGroup.previousContentGroup3,
            h.contentGroup.contentGroupUniqueViews1, h.contentGroup.contentGroupUniqueViews2, h.contentGroup.contentGroupUniqueViews3,
            h.dataSource,

            p.v2ProductName, p.v2ProductCategory, p.productBrand, p.productPrice,
            p.localProductPrice, p.isImpression, p.isClick,
            p.productListName, p.productListPosition

        FROM `{BQ_DATASET}.{BQ_TABLE_PREFIX}*` AS t
        LEFT JOIN UNNEST(t.customDimensions) AS cd
        LEFT JOIN UNNEST(t.hits) AS h
        LEFT JOIN UNNEST(h.product) AS p
        WHERE _TABLE_SUFFIX = '{date_suffix}'
        LIMIT {limit}
        """ 