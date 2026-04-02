# Elasticsearch 완벽 가이드 — 목차

[들어가며](pages/00-들어가며.md)

---

## [Phase 1. 기초 (Foundation)](pages/01-기초 (Foundation).md)

### [1.1 Elasticsearch 소개](pages/01-01-Elasticsearch 소개.md)

- [1.1.1 Elasticsearch란 무엇인가](pages/01-01-01-Elasticsearch란 무엇인가.md)
- [1.1.2 설치 및 환경 구성](pages/01-01-02-설치 및 환경 구성.md)
- [1.1.3 첫 번째 문서 인덱싱과 검색](pages/01-01-03-첫 번째 문서 인덱싱과 검색.md)

### [1.2 핵심 원리: Lucene과 역색인](pages/01-02-핵심 원리 Lucene과 역색인.md)

- [1.2.1 Lucene과 Elasticsearch의 관계](pages/01-02-01-Lucene과 Elasticsearch의 관계.md)
- [1.2.2 역색인 동작 원리](pages/01-02-02-역색인 동작 원리.md)
- [1.2.3 세그먼트 계층 구조](pages/01-02-03-세그먼트 계층 구조.md)
- [1.2.4 NRT 검색과 Translog](pages/01-02-04-NRT 검색과 Translog.md)

### [1.3 데이터 모델: 문서/인덱스/샤드](pages/01-03-데이터 모델 문서 인덱스 샤드.md)

- [1.3.1 JSON 문서 구조](pages/01-03-01-JSON 문서 구조.md)
- [1.3.2 인덱스 개념과 RDBMS 비교](pages/01-03-02-인덱스 개념과 RDBMS 비교.md)
- [1.3.3 샤드와 레플리카](pages/01-03-03-샤드와 레플리카.md)

---

## [Phase 2. 데이터 모델링 (Data Modeling)](pages/02-데이터 모델링 (Data Modeling).md)

### [2.1 매핑 기초](pages/02-01-매핑 기초.md)

- [2.1.1 동적 매핑 vs 명시적 매핑](pages/02-01-01-동적 매핑 vs 명시적 매핑.md)
- [2.1.2 매핑 설정과 업데이트 제약](pages/02-01-02-매핑 설정과 업데이트 제약.md)
- [2.1.3 매핑 폭발 방지](pages/02-01-03-매핑 폭발 방지.md)

### [2.2 필드 타입](pages/02-02-필드 타입.md)

- [2.2.1 text vs keyword](pages/02-02-01-text vs keyword.md)
- [2.2.2 숫자/날짜/불리언 타입](pages/02-02-02-숫자 날짜 불리언 타입.md)
- [2.2.3 특수 타입: dense_vector, geo_point, nested, join](pages/02-02-03-특수 타입.md)
- [2.2.4 멀티필드 패턴](pages/02-02-04-멀티필드 패턴.md)

### [2.3 텍스트 분석](pages/02-03-텍스트 분석.md)

- [2.3.1 분석기 파이프라인](pages/02-03-01-분석기 파이프라인.md)
- [2.3.2 내장 분석기](pages/02-03-02-내장 분석기.md)
- [2.3.3 커스텀 분석기 구성](pages/02-03-03-커스텀 분석기 구성.md)
- [2.3.4 한국어 분석: Nori](pages/02-03-04-한국어 분석 Nori.md)

### [2.4 고급 데이터 모델링](pages/02-04-고급 데이터 모델링.md)

- 2.4.1 런타임 필드
- 2.4.2 중첩 문서 vs Parent-Child 조인
- 2.4.3 인덱스 템플릿과 Component Template
- 2.4.4 인덱스 별칭

---

## [Phase 3. 검색 (Search)](pages/03-검색 (Search).md)

### [3.1 REST API와 CRUD](pages/03-01-REST API와 CRUD.md)

- 3.1.1 REST API 구조
- 3.1.2 문서 CRUD
- 3.1.3 Bulk API

### [3.2 Query DSL 기초](pages/03-02-Query DSL 기초.md)

- 3.2.1 Query context vs Filter context
- 3.2.2 match와 term 쿼리
- 3.2.3 bool 쿼리
- 3.2.4 range, exists, prefix, wildcard 쿼리

### [3.3 고급 검색 기법](pages/03-03-고급 검색 기법.md)

- 3.3.1 multi_match와 cross-field 검색
- 3.3.2 자동완성 구현
- 3.3.3 하이라이팅
- 3.3.4 페이지네이션
- 3.3.5 지리 검색

### [3.4 관련성 튜닝](pages/03-04-관련성 튜닝.md)

- 3.4.1 BM25 알고리즘
- 3.4.2 k1/b 파라미터 튜닝
- 3.4.3 function_score 쿼리
- 3.4.4 Painless 스크립팅
- 3.4.5 Explain API와 스코어 디버깅

---

## [Phase 4. 집계 및 분석 (Aggregations)](pages/04-집계 및 분석 (Aggregations).md)

### [4.1 집계 기초](pages/04-01-집계 기초.md)

- 4.1.1 집계 구문 구조
- 4.1.2 Bucket 집계
- 4.1.3 Metric 집계

### [4.2 고급 집계](pages/04-02-고급 집계.md)

- 4.2.1 중첩 집계
- 4.2.2 Pipeline 집계
- 4.2.3 composite 집계
- 4.2.4 집계 성능 최적화

### [4.3 Kibana 시각화](pages/04-03-Kibana 시각화.md)

- 4.3.1 Kibana Lens
- 4.3.2 Kibana Dashboard
- 4.3.3 KQL (Kibana Query Language)

---

## [Phase 5. 분산 아키텍처 (Distributed Architecture)](pages/05-분산 아키텍처 (Distributed Architecture).md)

### [5.1 클러스터와 노드](pages/05-01-클러스터와 노드.md)

- 5.1.1 노드 역할
- 5.1.2 클러스터 아키텍처
- 5.1.3 분산 읽기/쓰기 흐름

### [5.2 샤드 전략](pages/05-02-샤드 전략.md)

- 5.2.1 샤드 크기와 수 결정
- 5.2.2 Rollover, Shrink, Split, Clone
- 5.2.3 Allocation Awareness

### [5.3 Cross-Cluster Search](pages/05-03-Cross-Cluster Search.md)

- 5.3.1 CCS 설정
- 5.3.2 Sniff 모드 vs Proxy 모드
- 5.3.3 멀티 리전 시나리오

---

## [Phase 6. 운영 및 관리 (Operations)](pages/06-운영 및 관리 (Operations).md)

### [6.1 인덱스 수명주기](pages/06-01-인덱스 수명주기.md)

- 6.1.1 ILM 정책
- 6.1.2 Data Streams
- 6.1.3 Searchable Snapshots

### [6.2 데이터 수집 파이프라인](pages/06-02-데이터 수집 파이프라인.md)

- 6.2.1 Logstash
- 6.2.2 Beats
- 6.2.3 인제스트 파이프라인

### [6.3 성능 최적화](pages/06-03-성능 최적화.md)

- 6.3.1 인덱싱 성능 최적화
- 6.3.2 검색 성능 최적화
- 6.3.3 JVM/파일시스템 최적화

### [6.4 보안 및 운영](pages/06-04-보안 및 운영.md)

- 6.4.1 TLS/RBAC/API Key 보안
- 6.4.2 스냅샷과 복구
- 6.4.3 클러스터 모니터링
- 6.4.4 롤링 업그레이드

---

## [Phase 7. AI 검색 (Modern AI Search)](pages/07-AI 검색 (Modern AI Search).md)

### [7.1 벡터 검색](pages/07-01-벡터 검색.md)

- 7.1.1 dense_vector와 HNSW
- 7.1.2 kNN 검색
- 7.1.3 임베딩 모델 배포

### [7.2 시맨틱 검색](pages/07-02-시맨틱 검색.md)

- 7.2.1 ELSER 작동 원리
- 7.2.2 ELSER vs dense 벡터 비교
- 7.2.3 ELSER 배포와 시맨틱 검색 구현

### [7.3 하이브리드 검색](pages/07-03-하이브리드 검색.md)

- 7.3.1 RRF 원리
- 7.3.2 BM25+kNN 결합 구현
- 7.3.3 하이브리드 검색 튜닝

### [7.4 RAG 통합](pages/07-04-RAG 통합.md)

- 7.4.1 RAG 파이프라인 구성
- 7.4.2 ML Inference 파이프라인

### [7.5 ML 이상 감지](pages/07-05-ML 이상 감지.md)

- 7.5.1 이상 감지 Job 설정
- 7.5.2 보안 모니터링 활용

---

## [Phase 8. 실전 활용 (Use Cases)](pages/08-실전 활용 (Use Cases).md)

### [8.1 전자상거래 검색](pages/08-01-전자상거래 검색.md)

- 8.1.1 상품 인덱스 설계
- 8.1.2 자동완성, 오타교정, 동의어 검색

### [8.2 ELK 로그 분석](pages/08-02-ELK 로그 분석.md)

- 8.2.1 로그 수집 파이프라인
- 8.2.2 Kibana 로그 분석 대시보드

### [8.3 Observability](pages/08-03-Observability.md)

- 8.3.1 Logs + Metrics + APM 통합
- 8.3.2 Observability 데이터 스트림 설계
