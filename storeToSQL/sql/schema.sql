-- 스키마 생성
CREATE SCHEMA ga_data;
GO

-- Sessions 테이블 (방문 세션)
CREATE TABLE ga_data.Sessions (
    visitorId NVARCHAR(255) PRIMARY KEY,
    visitNumber INT NULL,
    visitId NVARCHAR(255) NULL,
    visitStartTime BIGINT NULL,
    date NVARCHAR(50) NULL,
    fullVisitorId NVARCHAR(255) NULL,
    channelGrouping NVARCHAR(255) NULL,
    socialEngagementType NVARCHAR(255) NULL,
    createdAt DATETIME2 DEFAULT GETDATE() NULL
);

-- Totals 테이블 (방문 통계)
CREATE TABLE ga_data.Totals (
    visitorId NVARCHAR(255) PRIMARY KEY,
    visits INT NULL,
    hits INT NULL,
    pageviews INT NULL,
    timeOnSite INT NULL,
    bounces INT NULL,
    transactions INT NULL,
    transactionRevenue FLOAT NULL,
    newVisits INT NULL,
    totalTransactionRevenue FLOAT NULL,
    sessionQualityDim INT NULL,
    createdAt DATETIME2 DEFAULT GETDATE() NULL
);

-- Traffic 테이블 (트래픽 소스)
CREATE TABLE ga_data.Traffic (
    visitorId NVARCHAR(255) PRIMARY KEY,
    referralPath NVARCHAR(MAX) NULL,
    campaign NVARCHAR(255) NULL,
    source NVARCHAR(255) NULL,
    medium NVARCHAR(255) NULL,
    keyword NVARCHAR(255) NULL,
    adContent NVARCHAR(MAX) NULL,
    adwordsPage NVARCHAR(255) NULL,
    adwordsSlot NVARCHAR(255) NULL,
    gclId NVARCHAR(255) NULL,
    adNetworkType NVARCHAR(50) NULL,
    isVideoAd NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    isTrueDirect NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    createdAt DATETIME2 DEFAULT GETDATE() NULL
);

-- DeviceGeo 테이블 (기기 및 지역 정보)
CREATE TABLE ga_data.DeviceGeo (
    visitorId NVARCHAR(255) PRIMARY KEY,
    browser NVARCHAR(255) NULL,
    operatingSystem NVARCHAR(255) NULL,
    isMobile NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    javaEnabled NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    deviceCategory NVARCHAR(50) NULL,
    continent NVARCHAR(50) NULL,
    subContinent NVARCHAR(100) NULL,
    country NVARCHAR(50) NULL,
    region NVARCHAR(100) NULL,
    metro NVARCHAR(100) NULL,
    city NVARCHAR(100) NULL,
    networkDomain NVARCHAR(255) NULL,
    createdAt DATETIME2 DEFAULT GETDATE() NULL
);

-- CustomDimensions 테이블
CREATE TABLE ga_data.CustomDimensions (
    visitorId NVARCHAR(255) NULL,
    dimensionIndex INT NULL,
    dimensionValue NVARCHAR(MAX) NULL,
    createdAt DATETIME2 DEFAULT GETDATE() NULL,
    PRIMARY KEY (visitorId, dimensionIndex)
);

-- Hits 테이블 (페이지뷰, 이벤트 등)
CREATE TABLE ga_data.Hits (
    visitorId NVARCHAR(255) NULL,
    hitNumber INT NULL,
    time INT NULL,
    hour INT NULL,
    minute INT NULL,
    isInteraction NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    isEntrance NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    isExit NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    pagePath NVARCHAR(MAX) NULL,
    hostname NVARCHAR(255) NULL,
    pageTitle NVARCHAR(MAX) NULL,
    searchKeyword NVARCHAR(255) NULL,
    transactionId NVARCHAR(255) NULL,
    screenName NVARCHAR(255) NULL,
    landingScreenName NVARCHAR(255) NULL,
    exitScreenName NVARCHAR(255) NULL,
    screenDepth INT NULL,
    eventCategory NVARCHAR(255) NULL,
    eventAction NVARCHAR(255) NULL,
    eventLabel NVARCHAR(MAX) NULL,
    actionType NVARCHAR(50) NULL,
    hitType NVARCHAR(50) NULL,
    socialNetwork NVARCHAR(50) NULL,
    hasSocialSourceReferral NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    contentGroup1 NVARCHAR(255) NULL,
    contentGroup2 NVARCHAR(255) NULL,
    contentGroup3 NVARCHAR(255) NULL,
    previousContentGroup1 NVARCHAR(255) NULL,
    previousContentGroup2 NVARCHAR(255) NULL,
    previousContentGroup3 NVARCHAR(255) NULL,
    contentGroupUniqueViews1 INT NULL,
    contentGroupUniqueViews2 INT NULL,
    contentGroupUniqueViews3 INT NULL,
    dataSource NVARCHAR(50) NULL,
    createdAt DATETIME2 DEFAULT GETDATE() NULL,
    PRIMARY KEY (visitorId, hitNumber)
);

-- HitsProduct 테이블
CREATE TABLE ga_data.HitsProduct (
    visitorId NVARCHAR(255) NULL,
    hitNumber INT NULL,
    v2ProductName NVARCHAR(255) NULL,
    v2ProductCategory NVARCHAR(255) NULL,
    productBrand NVARCHAR(255) NULL,
    productPrice FLOAT NULL,
    localProductPrice FLOAT NULL,
    isImpression NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    isClick NVARCHAR(10) NULL,  -- 'Yes'/'No' 문자열 값을 허용하기 위해 BIT에서 NVARCHAR로 변경
    productListName NVARCHAR(255) NULL,
    productListPosition INT NULL,
    createdAt DATETIME2 DEFAULT GETDATE() NULL,
    PRIMARY KEY (visitorId, hitNumber)
);

-- 인덱스 생성
CREATE INDEX IX_Sessions_VisitStartTime ON ga_data.Sessions(visitStartTime);
CREATE INDEX IX_Hits_Time ON ga_data.Hits(time);
CREATE INDEX IX_Traffic_Source ON ga_data.Traffic(source);
CREATE INDEX IX_DeviceGeo_Country ON ga_data.DeviceGeo(country); 