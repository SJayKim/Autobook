# 1.1 Elasticsearch 소개

이 섹션에서는 Elasticsearch가 무엇인지, 왜 사용하는지, 그리고 어떻게 처음 시작하는지를 다룹니다. 개념 이해에서 출발해 실제 클러스터를 기동하고 첫 문서를 저장·검색하는 데까지 나아갑니다.

## 토픽 목록

**1.1.1 Elasticsearch란 무엇인가**
- Elasticsearch의 정의와 핵심 특징을 설명할 수 있다
- 검색 엔진과 분석 엔진으로서의 역할을 구분할 수 있다
- ELK Stack 구성요소를 나열하고 각 역할을 설명할 수 있다

Elasticsearch가 어떤 도구인지, RESTful API 기반의 JSON 문서 저장 방식, 수평 확장성과 고가용성, 실시간 검색(Near Real-Time)의 의미, 그리고 ELK Stack(Elasticsearch + Logstash + Kibana) 및 OpenSearch와의 관계를 다룹니다.

**1.1.2 설치 및 환경 구성**
- Elasticsearch를 로컬 환경에 설치하고 정상 기동을 확인할 수 있다
- Docker Compose로 단일 노드 클러스터를 구성할 수 있다
- elasticsearch.yml 핵심 설정 항목을 조작할 수 있다

Docker 및 Docker Compose를 이용한 설치 방법, elasticsearch.yml의 핵심 파라미터(cluster.name, node.name, network.host), JVM heap 설정, Kibana 연결, 클러스터 상태 확인(_cluster/health)을 다룹니다.

**1.1.3 첫 번째 문서 인덱싱과 검색**
- PUT/GET API로 문서를 인덱싱하고 조회할 수 있다
- _search API로 기본 전문 검색을 실행할 수 있다
- 응답 JSON의 hits, _score 필드를 해석할 수 있다

PUT /{index}/_doc/{id} 인덱싱, GET으로 문서 조회, POST /{index}/_search 검색 실행, match 쿼리 기본 사용법, 응답 구조(took, hits.total, hits.hits, _score) 해석을 다룹니다.
