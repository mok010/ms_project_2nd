# 🛍 Commercy: 마케터를 위한 실시간 이커머스 분석 솔루션

Commercy는 이커머스 마케터를 위해 설계된 **실시간 통합 마케팅 분석 플랫폼**입니다.  
실시간 KPI 모니터링, 자동 전략 제안, 경고 메시지 전송 기능을 통해 **데이터 기반 의사결정**을 지원합니다.

---

##  프로젝트 개요

- **목적**: 실시간 고객 행동 데이터를 기반으로 마케팅 전략을 수립하고, 이상 징후에 신속하게 대응할 수 있는 도구 제공
- **데이터 출처**: Google Merchandise Store (2016.08 ~ 2017.07 / 약 65GB)
- **구성요소**: Power BI 대시보드, AI 기반 챗봇, Teams 실시간 메시지 시스템

---

##  팀 구성 및 역할

| 이름 | 담당 역할 |
|------|-----------|
| [mok010](https://github.com/mok010) | 챗봇 SQL 연동, 문서 벡터화, Teams 메시지 파이프라인 |
| [LeeHooyo](https://github.com/LeeHooyo) | 챗봇 백엔드/프론트엔드 구축, UI 설계 및 구현 |
| [nina-gitty](https://github.com/nina-gitty) | 데이터 수집, 전처리, Power BI 대시보드 설계 |
| [JaeHoonKOR](https://github.com/JaeHoonKOR) | ADF 기반 데이터 적재/전처리 파이프라인 구축 |
| [JeongJYs](https://github.com/JeongJYs) | KPI 시각화 및 Semantic Model 구성 |
| [mynx6y](https://github.com/mynx6y) | 통합 플랫폼 설계, 전체 프로젝트 관리 및 팀 협업 조율 |

---

##  주요 기능

###  실시간 대시보드 (Power BI)
- KPI 추적: 매출, 이탈률, 전환율 등
- 뉴스 크롤링 및 감성 분석 시각화
- 다양한 필터 제공: 날짜, 국가, 고객군, 접속기기 등
- 탭 구성: 요약 / 매출 / 유입·이탈 / 뉴스

###  AI 챗봇 (Django + React)
- 자연어 입력 기반 질의 처리
- SQL 자동 생성 및 DB 조회 (LangChain 기반)
- PDF 문서 임베딩 및 RAG 검색
- 반응형 UI: 타이핑 애니메이션, 입력창 자동 조절

###  Teams 메시지 시스템
- 5분 단위 실시간 위험 경고 알림
- 1일 단위 KPI 요약 메시지 자동 전송
- Azure Stream Analytics + Function + Webhook 기반

---

##  기술 스택

| 영역 | 기술 |
|------|------|
| 클라우드 | Azure SQL, Blob, Function App, Cosmos DB, AI Search |
| 실시간 처리 | Azure Data Factory, Stream Analytics, Timer Trigger |
| 시각화 | Microsoft Fabric (Lakehouse, Dataflow Gen2, Semantic Model), Power BI |
| 백엔드 | Django, Azure Function, Swagger |
| 프론트엔드 | React, TailwindCSS |
| AI | Azure OpenAI API (Chat, Embedding), LangChain, RAG |
| 문서 임베딩 | PyMuPDF, SAS URL 기반 PDF 처리 |
| 배포 | Azure Container Registry, Azure CLI |

---

##  챗봇 처리 흐름

1. 질문 유형 분류: `SQL`, `RAG`, `Reasoning`
2. SQL: LangChain으로 쿼리 생성 → DB 조회
3. RAG: PDF → 텍스트 추출 → 임베딩 → Azure AI Search 검색
4. Reasoning: GPT 기반 응답 생성

<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/chatbot.gif">


## 챗봇 RAG 학습 자동화 파이프라인 
1. RAG 자료 업로드 
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/pdf_fileupload.gif">
2. 블록 트리거 발동 및 함수 앱 실행
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/pdf_function.gif">
3. 아웃풋 컨테이너에 JSON 파일 생성
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/pdf_output.gif">
4. AI SEARCH에 자료 학습
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/pdf_aisearch.gif">

---

##  대시보드 구성

### 기본 인터페이스
- 좌측 탭 전환 버튼을 통해 요약/매출/유입·이탈/뉴스 탭 전환
- 상단 필터: 날짜, 고객군, 국가, 접속기기 등
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/dash_1.png">


### 탭 구성
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/dash_tab.gif">

#### 1) 요약 탭
- KPI 핵심 지표를 한눈에 요약
- 자주 사용하는 지표를 빠르게 확인 가능
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/dash_2.png">
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/dash_fil.gif">

#### 2) 매출 탭
- Revenue, CVR, AOV 등 시계열 매출 분석
- 상품 전환율, 주문 금액을 바탕으로 판매 전략 수립 지원
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/dash_3.png">

#### 3) 유입/이탈 탭
- Session 수, 이탈률 분석
- 병목 지점 파악 및 고객 리텐션 개선 전략 도출
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/dash_4.png">

#### 4) 뉴스 탭
- 관련 뉴스 수집 및 감성 분석 (범위: -1.0 ~ 1.0)
- 주제별 필터 제공 (모기업, 이커머스, 패션 등)
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/dash_5.png">

---

##  Teams 메시지 시스템 구성
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/teams_img.png">
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/teams_message.gif">

### 파이프라인 흐름
```
SQL DB → ADF 전처리 → Blob 저장 → Stream Analytics 수신
→ 조건별 집계 → Function App 호출 → Teams 알림 전송
```

### 1) 실시간 위험 경고 (5분 단위)
- 이탈 지점에서 평균보다 오래 머문 사용자 수 감지
- 임계치 초과 시 Function App 호출 → Teams Webhook 전송

### 2) KPI 요약 리포트 (1일 단위)
- 하루 동안의 KPI를 집계하여 Function App이 메시지 전송
- 출근 시점에 요약된 지표를 바로 확인 가능

### 이벤트 버퍼링 전략
- 실시간 전송 대신 1분 단위로 로그를 묶어 저장 (네트워크 부하 최소화)

---

## 통합 서비스 웹 사이트
<img src="https://github.com/mok010/ms_project_2nd/blob/main/readme_gif/website.gif">

---

##  Responsible AI 원칙 적용

| 항목 | 적용 내용 |
|------|-----------|
| 투명성 | 처리 로그, 응답 근거 추적 가능 |
| 책임성 | 예외 처리 로깅, 저작권 자료만 학습 |
| 공정성 | 전체 고객군 대상 데이터 사용, 무결성 보장 |
| 신뢰성 | Try-Catch 처리, 재시도 메커니즘 적용 |
| 개인정보 보호 | 민감 정보는 환경변수로 관리, 개인 로그 미수집 |
| 포용성 | 다국어 확장 가능성 고려, 다양한 기기·지역 지원 |

---

##  프로젝트 성과

- 실시간 KPI 분석 및 이상 탐지 시스템 완성
- Power BI 대시보드 성능 최적화 (최대 166초 단축)
- 자연어 → SQL 자동 생성 + 문서 기반 전략 제안 챗봇 구축
- RAG 기반 문서 임베딩 파이프라인 자동화

---

## 더 자세한 구현 과정
https://star-ccomputer-go.tistory.com/category/Data/Commercy%3A%20%EB%A7%88%EC%BC%80%ED%84%B0%EB%A5%BC%20%EC%9C%84%ED%95%9C%20%EC%8B%A4%EC%8B%9C%EA%B0%84%20%EC%9D%B4%EC%BB%A4%EB%A8%B8%EC%8A%A4%20%EB%B6%84%EC%84%9D%20%EC%86%94%EB%A3%A8%EC%85%98%20%EA%B5%AC%EC%B6%95%EA%B8%B0

> “Commercy는 단순한 분석 도구가 아닌, 마케터의 실시간 의사결정을 위한 전략 파트너입니다.”
```


