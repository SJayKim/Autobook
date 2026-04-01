# 3.1 REST API와 CRUD

이 섹션에서는 Elasticsearch와 상호작용하는 기본 수단인 REST API를 다룹니다. 문서를 생성·조회·수정·삭제하는 방법과 대량 데이터를 효율적으로 처리하는 Bulk API를 익힙니다.

## 토픽 목록

**3.1.1 REST API 구조**
- Elasticsearch REST API의 URL 패턴과 HTTP 메서드 의미를 설명할 수 있다
- Kibana Dev Tools Console로 API를 실행할 수 있다

URL 구조(/{index}/{endpoint}), HTTP 메서드 의미(GET/POST/PUT/DELETE/HEAD), Content-Type: application/json 헤더, 요청 바디 JSON 구조, 응답 상태 코드 해석, Kibana Dev Tools Console 사용법, curl 기본 사용법, pretty 파라미터를 다룹니다.

**3.1.2 문서 CRUD**
- 문서의 생성, 조회, 수정, 삭제 API를 올바르게 사용할 수 있다
- upsert와 partial update의 차이를 설명할 수 있다

PUT /{index}/_doc/{id} 인덱싱, POST /{index}/_doc 자동 ID 생성, GET /{index}/_doc/{id} 조회, DELETE /{index}/_doc/{id} 삭제, POST /{index}/_update/{id} 부분 업데이트, upsert 패턴(doc_as_upsert), optimistic concurrency control(_if_seq_no, _if_primary_term), DELETE by Query를 다룹니다.

**3.1.3 Bulk API**
- Bulk API의 NDJSON 형식을 이해하고 대량 인덱싱을 수행할 수 있다
- Bulk API 응답에서 오류 항목을 식별할 수 있다

Bulk API NDJSON 형식(action + source 쌍), index/create/update/delete 액션, 배치 크기 최적화(5~15MB 권장), errors 필드와 items 배열 응답 파싱, 재시도 전략, _bulk 엔드포인트, 클라이언트 라이브러리의 bulk helper를 다룹니다.
