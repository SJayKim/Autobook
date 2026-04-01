# Phase 3. 검색 (Search)

이 Phase를 마치면 Query DSL로 복합 검색을 작성하고, 자동완성·하이라이팅·페이지네이션을 구현하며, 관련성 스코어를 튜닝할 수 있게 됩니다.

Elasticsearch를 사용하는 가장 핵심적인 목적은 빠르고 정확한 검색입니다. Phase 3에서는 REST API를 통한 문서 CRUD부터 시작해, Query DSL의 기본 구조, 다양한 고급 검색 기법, 그리고 검색 결과의 관련성을 높이는 스코어 튜닝까지 체계적으로 다룹니다.

첫 번째 섹션에서는 REST API의 구조와 문서 CRUD, Bulk API를 다룹니다. 두 번째 섹션에서는 Query DSL의 핵심인 query/filter context, match/term 쿼리, bool 쿼리, range/exists/prefix/wildcard 쿼리를 다룹니다. 세 번째 섹션에서는 multi_match, 자동완성, 하이라이팅, 페이지네이션, 지리 검색 등 고급 검색 기법을 다룹니다. 네 번째 섹션에서는 BM25 알고리즘, 파라미터 튜닝, function_score, Painless 스크립팅, Explain API를 통한 스코어 디버깅을 다룹니다.

## 이 Phase의 섹션 구성

**3.1 REST API와 CRUD**
REST API 구조, 문서 CRUD(생성/조회/수정/삭제), Bulk API 대량 인덱싱을 다룹니다.
- 3.1.1 REST API 구조
- 3.1.2 문서 CRUD
- 3.1.3 Bulk API

**3.2 Query DSL 기초**
query/filter context, match/term/bool/range/exists/prefix/wildcard 쿼리를 다룹니다.
- 3.2.1 Query context vs Filter context
- 3.2.2 match와 term 쿼리
- 3.2.3 bool 쿼리
- 3.2.4 range, exists, prefix, wildcard 쿼리

**3.3 고급 검색 기법**
multi_match, 자동완성, 하이라이팅, 페이지네이션(search_after/PIT), 지리 검색을 다룹니다.
- 3.3.1 multi_match와 cross-field 검색
- 3.3.2 자동완성 구현
- 3.3.3 하이라이팅
- 3.3.4 페이지네이션
- 3.3.5 지리 검색

**3.4 관련성 튜닝**
BM25 알고리즘, k1/b 파라미터 튜닝, function_score, Painless 스크립팅, Explain API와 스코어 디버깅을 다룹니다.
- 3.4.1 BM25 알고리즘
- 3.4.2 k1/b 파라미터 튜닝
- 3.4.3 function_score 쿼리
- 3.4.4 Painless 스크립팅
- 3.4.5 Explain API와 스코어 디버깅
