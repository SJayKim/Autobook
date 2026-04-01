# 3.2 Query DSL 기초

이 섹션에서는 Elasticsearch의 검색 언어인 Query DSL의 핵심 구성요소를 다룹니다. query/filter context의 차이를 이해하고, match·term·bool 쿼리를 조합하여 복잡한 검색 조건을 표현하는 방법을 익힙니다.

## 토픽 목록

**3.2.1 Query context vs Filter context**
- query context와 filter context의 차이를 설명하고 적절히 선택할 수 있다
- filter context의 캐싱 이점을 설명할 수 있다

query context(관련성 스코어 계산), filter context(이진 매칭, 스코어 없음), filter 캐싱(bitset cache) 메커니즘, bool 쿼리의 must/filter/should/must_not, filter에 적합한 조건(날짜, 카테고리, 상태), query에 적합한 조건(텍스트 유사도), 성능 최적화 관점에서의 선택 기준을 다룹니다.

**3.2.2 match와 term 쿼리**
- match 쿼리와 term 쿼리의 분석기 적용 여부 차이를 설명할 수 있다
- match_phrase로 구문 검색을 수행할 수 있다

match 쿼리(분석기 적용 후 검색), term 쿼리(분석 없는 exact 매칭), terms 쿼리(복수 값 매칭), match_phrase 쿼리(어순 보장), match_phrase_prefix 쿼리, operator: and/or 설정, minimum_should_match 설정, fuzziness 파라미터를 다룹니다.

**3.2.3 bool 쿼리**
- bool 쿼리의 must/filter/should/must_not 절을 조합하여 복합 조건 검색을 작성할 수 있다

must 절(필수 조건 + 스코어 기여), filter 절(필수 조건, 스코어 기여 없음), should 절(선택적 조건 + 스코어 부스트), must_not 절(제외 조건), minimum_should_match와 should 절, 중첩 bool 쿼리, boost 파라미터로 가중치 조정을 다룹니다.

**3.2.4 range, exists, prefix, wildcard 쿼리**
- range 쿼리로 날짜/숫자 범위 검색을 수행할 수 있다
- prefix, wildcard, regexp 쿼리의 성능 위험을 인식하고 적절히 사용할 수 있다

range 쿼리(gte, lte, gt, lt), 날짜 범위 math(now-7d/d), exists 쿼리(null/누락 필드 처리), prefix 쿼리, wildcard 쿼리(* 와 ? 패턴), regexp 쿼리, wildcard/regexp 성능 위험(leading wildcard), ids 쿼리를 다룹니다.
