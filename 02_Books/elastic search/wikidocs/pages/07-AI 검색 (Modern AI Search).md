# Phase 7. AI 검색 (Modern AI Search)

이 Phase를 마치면 벡터 검색, ELSER 시맨틱 검색, BM25+kNN 하이브리드 검색을 구현하고 RAG 파이프라인을 통합할 수 있게 됩니다.

현대 검색 시스템은 키워드 매칭을 넘어 의미 기반의 시맨틱 검색으로 진화하고 있습니다. Elasticsearch는 8.x 버전부터 dense_vector, HNSW 인덱스, ELSER, retriever API 등 AI 검색에 필요한 기능을 대폭 강화했습니다. Phase 7에서는 벡터 임베딩 저장과 kNN 검색, ELSER 시맨틱 검색, BM25와 kNN을 결합한 하이브리드 검색, RAG 파이프라인 통합, 그리고 ML 기반 이상 감지까지 최신 AI 검색 기술을 다룹니다.

## 이 Phase의 섹션 구성

**7.1 벡터 검색**
dense_vector 타입과 HNSW 인덱스, kNN 검색 실행, 임베딩 모델 배포와 인제스트 파이프라인 연결을 다룹니다.
- 7.1.1 dense_vector와 HNSW
- 7.1.2 kNN 검색
- 7.1.3 임베딩 모델 배포

**7.2 시맨틱 검색**
ELSER의 희소 벡터 방식, ELSER vs dense 벡터 비교, ELSER 배포와 시맨틱 검색 구현을 다룹니다.
- 7.2.1 ELSER 작동 원리
- 7.2.2 ELSER vs dense 벡터 비교
- 7.2.3 ELSER 배포와 시맨틱 검색 구현

**7.3 하이브리드 검색**
RRF(Reciprocal Rank Fusion) 원리, BM25+kNN 결합 구현(retriever API), 하이브리드 검색 튜닝을 다룹니다.
- 7.3.1 RRF 원리
- 7.3.2 BM25+kNN 결합 구현
- 7.3.3 하이브리드 검색 튜닝

**7.4 RAG 통합**
Elasticsearch를 벡터 저장소로 사용하는 RAG 파이프라인 설계, ML Inference 파이프라인을 이용한 자동 임베딩 생성을 다룹니다.
- 7.4.1 RAG 파이프라인 구성
- 7.4.2 ML Inference 파이프라인

**7.5 ML 이상 감지**
Kibana에서 이상 감지 Job 설정 및 결과 해석, Elastic Security와의 SIEM 통합을 다룹니다.
- 7.5.1 이상 감지 Job 설정
- 7.5.2 보안 모니터링 활용
