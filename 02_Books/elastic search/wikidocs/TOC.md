# 목차

## Phase 1. 기초 (Foundation)

### 1.1 Elasticsearch 소개
- 1.1.1 Elasticsearch란 무엇인가
- 1.1.2 설치 및 환경 구성
- 1.1.3 첫 번째 문서 인덱싱과 검색

### 1.2 핵심 원리: Lucene과 역색인
- 1.2.1 Lucene과 Elasticsearch의 관계
- 1.2.2 역색인 동작 원리
- 1.2.3 세그먼트 계층 구조
- 1.2.4 NRT 검색과 Translog

### 1.3 데이터 모델: 문서/인덱스/샤드
- 1.3.1 JSON 문서 구조
- 1.3.2 인덱스 개념과 RDBMS 비교
- 1.3.3 샤드와 레플리카

---

## Phase 2. 데이터 모델링 (Data Modeling)

### 2.1 매핑 기초
- 2.1.1 동적 매핑 vs 명시적 매핑
- 2.1.2 매핑 설정과 업데이트 제약
- 2.1.3 매핑 폭발 방지

### 2.2 필드 타입
- 2.2.1 text vs keyword
- 2.2.2 숫자/날짜/불리언 타입
- 2.2.3 특수 타입: dense_vector, geo_point, nested, join
- 2.2.4 멀티필드 패턴

### 2.3 텍스트 분석
- 2.3.1 분석기 파이프라인
- 2.3.2 내장 분석기
- 2.3.3 커스텀 분석기 구성
- 2.3.4 한국어 분석: Nori

### 2.4 고급 데이터 모델링
- 2.4.1 런타임 필드
- 2.4.2 중첩 문서 vs Parent-Child 조인
- 2.4.3 인덱스 템플릿과 Component Template
- 2.4.4 인덱스 별칭

---

## Phase 3. 검색 (Search)

### 3.1 REST API와 CRUD
- 3.1.1 REST API 구조
- 3.1.2 문서 CRUD
- 3.1.3 Bulk API

### 3.2 Query DSL 기초
- 3.2.1 Query context vs Filter context
- 3.2.2 match와 term 쿼리
- 3.2.3 bool 쿼리
- 3.2.4 range, exists, prefix, wildcard 쿼리

### 3.3 고급 검색 기법
- 3.3.1 multi_match와 cross-field 검색
- 3.3.2 자동완성 구현
- 3.3.3 하이라이팅
- 3.3.4 페이지네이션
- 3.3.5 지리 검색

### 3.4 관련성 튜닝
- 3.4.1 BM25 알고리즘
- 3.4.2 k1/b 파라미터 튜닝
- 3.4.3 function_score 쿼리
- 3.4.4 Painless 스크립팅
- 3.4.5 Explain API와 스코어 디버깅

---

## Phase 4. 집계 및 분석 (Aggregations)

### 4.1 집계 기초
- 4.1.1 집계 구문 구조
- 4.1.2 Bucket 집계
- 4.1.3 Metric 집계

### 4.2 고급 집계
- 4.2.1 중첩 집계
- 4.2.2 Pipeline 집계
- 4.2.3 composite 집계
- 4.2.4 집계 성능 최적화

### 4.3 Kibana 시각화
- 4.3.1 Kibana Lens
- 4.3.2 Kibana Dashboard
- 4.3.3 KQL (Kibana Query Language)

---

## Phase 5. 분산 아키텍처 (Distributed Architecture)

### 5.1 클러스터와 노드
- 5.1.1 노드 역할
- 5.1.2 클러스터 아키텍처
- 5.1.3 분산 읽기/쓰기 흐름

### 5.2 샤드 전략
- 5.2.1 샤드 크기와 수 결정
- 5.2.2 Rollover, Shrink, Split, Clone
- 5.2.3 Allocation Awareness

### 5.3 Cross-Cluster Search
- 5.3.1 CCS 설정
- 5.3.2 Sniff 모드 vs Proxy 모드
- 5.3.3 멀티 리전 시나리오

---

## Phase 6. 운영 및 관리 (Operations)

### 6.1 인덱스 수명주기
- 6.1.1 ILM 정책
- 6.1.2 Data Streams
- 6.1.3 Searchable Snapshots

### 6.2 데이터 수집 파이프라인
- 6.2.1 Logstash
- 6.2.2 Beats
- 6.2.3 인제스트 파이프라인

### 6.3 성능 최적화
- 6.3.1 인덱싱 성능 최적화
- 6.3.2 검색 성능 최적화
- 6.3.3 JVM/파일시스템 최적화

### 6.4 보안 및 운영
- 6.4.1 TLS/RBAC/API Key 보안
- 6.4.2 스냅샷과 복구
- 6.4.3 클러스터 모니터링
- 6.4.4 롤링 업그레이드

---

## Phase 7. AI 검색 (Modern AI Search)

### 7.1 벡터 검색
- 7.1.1 dense_vector와 HNSW
- 7.1.2 kNN 검색
- 7.1.3 임베딩 모델 배포

### 7.2 시맨틱 검색
- 7.2.1 ELSER 작동 원리
- 7.2.2 ELSER vs dense 벡터 비교
- 7.2.3 ELSER 배포와 시맨틱 검색 구현

### 7.3 하이브리드 검색
- 7.3.1 RRF 원리
- 7.3.2 BM25+kNN 결합 구현
- 7.3.3 하이브리드 검색 튜닝

### 7.4 RAG 통합
- 7.4.1 RAG 파이프라인 구성
- 7.4.2 ML Inference 파이프라인

### 7.5 ML 이상 감지
- 7.5.1 이상 감지 Job 설정
- 7.5.2 보안 모니터링 활용

---

## Phase 8. 실전 활용 (Use Cases)

### 8.1 전자상거래 검색
- 8.1.1 상품 인덱스 설계
- 8.1.2 자동완성, 오타교정, 동의어 검색

### 8.2 ELK 로그 분석
- 8.2.1 로그 수집 파이프라인
- 8.2.2 Kibana 로그 분석 대시보드

### 8.3 Observability
- 8.3.1 Logs + Metrics + APM 통합
- 8.3.2 Observability 데이터 스트림 설계
