-- ga_data 스키마가 없으면 생성
-- 모든 Google Analytics 데이터는 이 스키마 아래에 저장됩니다
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'ga_data')
BEGIN
    EXEC('CREATE SCHEMA ga_data');
END
GO

-- 기존 테이블 삭제 (순서 중요: 외래 키 제약이 있다면 자식 테이블부터)
-- 참고: 테이블 간 관계는 코드 로직으로 처리되며, 실제 외래 키 제약조건은 없습니다
DROP TABLE IF EXISTS ga_data.HitsProduct;
DROP TABLE IF EXISTS ga_data.Hits;
DROP TABLE IF EXISTS ga_data.DeviceGeo;
DROP TABLE IF EXISTS ga_data.Traffic;
DROP TABLE IF EXISTS ga_data.Totals;
DROP TABLE IF EXISTS ga_data.Sessions;
GO

-- Sessions 테이블 생성
-- 사용자 세션 기본 정보를 저장하는 테이블
CREATE TABLE ga_data.Sessions (
    session_key VARCHAR(255) PRIMARY KEY,  -- 세션 고유 식별자 (fullVisitorId-visitId 형식)
    primary_key VARCHAR(255),              -- 이전 버전 호환용 키 (날짜-일련번호 형식)
    visitNumber INT,                       -- 방문자의 방문 횟수
    visitId INT,                           -- 방문 ID
    visitStartTime INT,                    -- 방문 시작 시간 (UNIX 타임스탬프)
    date DATE,                             -- 방문 날짜
    fullVisitorId VARCHAR(255),            -- Google Analytics의 방문자 ID
    channelGrouping VARCHAR(255),          -- 채널 그룹 (Organic Search, Direct 등)
    socialEngagementType VARCHAR(255)      -- 소셜 참여 유형
);
GO

-- Totals 테이블 생성
-- 세션별 집계 데이터를 저장하는 테이블
CREATE TABLE ga_data.Totals (
    session_key VARCHAR(255) PRIMARY KEY,  -- 세션 고유 식별자 (Sessions 테이블과 연결)
    primary_key VARCHAR(255),              -- 이전 버전 호환용 키
    visitorId VARCHAR(255),                -- 방문자 ID
    visits INT,                            -- 방문 수
    hits INT,                              -- 히트 수 (페이지뷰, 이벤트 등)
    pageviews INT,                         -- 페이지뷰 수
    timeOnSite INT,                        -- 사이트 체류 시간 (초)
    bounces INT,                           -- 이탈 여부 (1=이탈, 0=비이탈)
    transactions INT,                      -- 트랜잭션 수
    newVisits INT,                         -- 신규 방문 여부 (1=신규, 0=재방문)
    totalTransactionRevenue INTEGER,       -- 총 트랜잭션 수익
    sessionQualityDim INT                  -- 세션 품질 점수 (1-100)
);
GO

-- Traffic 테이블 생성
-- 트래픽 소스 정보를 저장하는 테이블
CREATE TABLE ga_data.Traffic (
    session_key VARCHAR(255) PRIMARY KEY,  -- 세션 고유 식별자 (Sessions 테이블과 연결)
    primary_key VARCHAR(255),              -- 이전 버전 호환용 키
    visitorId VARCHAR(255),                -- 방문자 ID
    referralPath NVARCHAR(MAX),            -- 참조 경로
    campaign NVARCHAR(255),                -- 캠페인 이름
    source NVARCHAR(255),                  -- 트래픽 소스 (google, facebook 등)
    medium NVARCHAR(255),                  -- 트래픽 매체 (organic, cpc 등)
    keyword NVARCHAR(255),                 -- 검색 키워드
    adContent NVARCHAR(MAX),               -- 광고 콘텐츠
    adwordsPage INT,                       -- AdWords 페이지
    adwordsSlot VARCHAR(255),              -- AdWords 슬롯
    gclId VARCHAR(255),                    -- Google Click ID
    adNetworkType VARCHAR(255),            -- 광고 네트워크 유형
    isTrueDirect BIT                       -- 직접 방문 여부
);
GO

-- DeviceGeo 테이블 생성
-- 디바이스 및 지리적 정보를 저장하는 테이블
CREATE TABLE ga_data.DeviceGeo (
    session_key VARCHAR(255) PRIMARY KEY,  -- 세션 고유 식별자 (Sessions 테이블과 연결)
    primary_key VARCHAR(255),              -- 이전 버전 호환용 키
    visitorId VARCHAR(255),                -- 방문자 ID
    browser VARCHAR(255),                  -- 브라우저 (Chrome, Safari 등)
    operatingSystem VARCHAR(255),          -- 운영체제 (Windows, iOS 등)
    deviceCategory VARCHAR(255),           -- 기기 카테고리 (desktop, mobile, tablet)
    continent VARCHAR(255),                -- 대륙
    subContinent VARCHAR(255),             -- 하위 대륙
    country VARCHAR(255),                  -- 국가
    region VARCHAR(255),                   -- 지역
    metro VARCHAR(255),                    -- 대도시권
    city VARCHAR(255)                      -- 도시
);
GO

-- Hits 테이블 생성
-- 페이지 조회, 이벤트 등의 히트 정보를 저장하는 테이블
CREATE TABLE ga_data.Hits (
    hit_key VARCHAR(255) PRIMARY KEY,      -- 히트 고유 식별자 (fullVisitorId-visitId-hitNumber 형식)
    session_key VARCHAR(255),              -- 세션 고유 식별자 (Sessions 테이블과 연결)
    hitId VARCHAR(255),                    -- 이전 버전 호환용 히트 ID (UUID)
    primary_key VARCHAR(255),              -- 이전 버전 호환용 세션 키
    visitorId VARCHAR(255),                -- 방문자 ID
    hitNumber INT,                         -- 히트 번호 (세션 내 순서)
    time INT,                              -- 히트 시간 (세션 시작부터의 밀리초)
    hour INT,                              -- 히트 발생 시간 (0-23)
    minute INT,                            -- 히트 발생 분 (0-59)
    isInteraction BIT,                     -- 상호작용 여부
    isEntrance BIT,                        -- 입구 페이지 여부
    isExit BIT,                            -- 출구 페이지 여부
    pagePath NVARCHAR(MAX),                -- 페이지 경로 (URL)
    hostname NVARCHAR(255),                -- 호스트명
    pageTitle NVARCHAR(MAX),               -- 페이지 제목
    searchKeyword NVARCHAR(255),           -- 검색 키워드
    transactionId VARCHAR(255),            -- 트랜잭션 ID
    screenName VARCHAR(255),               -- 화면 이름 (모바일 앱)
    landingScreenName VARCHAR(255),        -- 랜딩 화면 이름
    exitScreenName VARCHAR(255),           -- 종료 화면 이름
    screenDepth INT,                       -- 화면 깊이
    eventCategory VARCHAR(255),            -- 이벤트 카테고리
    eventAction VARCHAR(255),              -- 이벤트 액션
    eventLabel NVARCHAR(MAX),              -- 이벤트 라벨
    actionType VARCHAR(50),                -- 액션 유형 (클릭, 구매 등)
    hitType VARCHAR(50),                   -- 히트 유형 (PAGE, EVENT 등)
    socialNetwork VARCHAR(255),            -- 소셜 네트워크
    hasSocialSourceReferral BIT,           -- 소셜 소스 참조 여부
    contentGroup1 VARCHAR(255),            -- 콘텐츠 그룹 1
    contentGroup2 VARCHAR(255),            -- 콘텐츠 그룹 2
    contentGroup3 VARCHAR(255),            -- 콘텐츠 그룹 3
    previousContentGroup1 VARCHAR(255),    -- 이전 콘텐츠 그룹 1
    previousContentGroup2 VARCHAR(255),    -- 이전 콘텐츠 그룹 2
    previousContentGroup3 VARCHAR(255),    -- 이전 콘텐츠 그룹 3
    contentGroupUniqueViews1 INT,          -- 콘텐츠 그룹 1 고유 조회수
    contentGroupUniqueViews2 INT,          -- 콘텐츠 그룹 2 고유 조회수
    contentGroupUniqueViews3 INT,          -- 콘텐츠 그룹 3 고유 조회수
    product_productQuantity INT            -- 제품 수량
);
GO

-- HitsProduct 테이블 생성
-- 제품 조회 및 구매 정보를 저장하는 테이블
CREATE TABLE ga_data.HitsProduct (
    product_hit_key VARCHAR(255) PRIMARY KEY,  -- 상품 히트 고유 식별자 (fullVisitorId-visitId-hitNumber-productSKU 형식)
    hit_key VARCHAR(255),                      -- 히트 고유 식별자 (Hits 테이블과 연결)
    productId VARCHAR(255),                    -- 이전 버전 호환용 제품 ID (UUID)
    hitId VARCHAR(255),                        -- 이전 버전 호환용 히트 ID
    visitorId VARCHAR(255),                    -- 방문자 ID
    hitNumber INT,                             -- 히트 번호
    v2ProductName NVARCHAR(255),               -- 제품 이름
    v2ProductCategory NVARCHAR(255),           -- 제품 카테고리
    productBrand NVARCHAR(255),                -- 제품 브랜드
    productPrice INTEGER,                      -- 제품 가격
    productRevenue INTEGER,                    -- 제품 수익
    isImpression BIT,                          -- 제품 노출 여부
    isClick BIT,                               -- 제품 클릭 여부
    productListName NVARCHAR(255),             -- 제품 목록 이름
    productListPosition INT,                   -- 제품 목록 내 위치
    productSKU VARCHAR(255)                    -- 제품 SKU (재고 관리 단위)
);
GO

-- 인덱스 생성
-- 쿼리 성능 향상을 위한 인덱스
CREATE INDEX IX_Sessions_VisitStartTime ON ga_data.Sessions(visitStartTime);
CREATE INDEX IX_Hits_Time ON ga_data.Hits(time);
CREATE INDEX IX_Traffic_Source ON ga_data.Traffic(source);
CREATE INDEX IX_DeviceGeo_Country ON ga_data.DeviceGeo(country);
CREATE INDEX IX_Sessions_SessionKey ON ga_data.Sessions(session_key);
CREATE INDEX IX_Hits_SessionKey ON ga_data.Hits(session_key);
CREATE INDEX IX_Hits_HitKey ON ga_data.Hits(hit_key);
CREATE INDEX IX_HitsProduct_HitKey ON ga_data.HitsProduct(hit_key);
GO 