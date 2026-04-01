# Phase 8. 실전 활용 (Use Cases)

이 Phase를 마치면 전자상거래 검색, ELK 로그 분석, Observability 시스템을 Elasticsearch로 구축할 수 있게 됩니다.

Phase 8은 이 책의 대미를 장식하는 실전 활용 단계입니다. 앞서 7개의 Phase에서 쌓은 지식을 실제 비즈니스 시나리오에 통합적으로 적용합니다. 전자상거래 상품 검색 서비스를 설계하고, ELK 스택으로 서버 로그를 수집·분석하며, Elastic Observability로 애플리케이션의 전체 상태를 모니터링하는 방법을 다룹니다.

각 섹션은 단순한 기능 설명이 아니라, 실제로 시스템을 설계하고 구현하는 관점에서 서술됩니다. 어떤 매핑을 선택할지, 어떤 쿼리를 조합할지, 어떤 파이프라인을 구성할지 실무적인 의사결정 과정을 함께 다룹니다.

## 이 Phase의 섹션 구성

**8.1 전자상거래 검색**
상품 인덱스 설계(멀티필드, 한국어 분석기, 벡터 임베딩), 자동완성·오타교정·동의어 검색·function_score 부스팅을 통합한 검색 서비스 구현을 다룹니다.
- 8.1.1 상품 인덱스 설계
- 8.1.2 자동완성, 오타교정, 동의어 검색

**8.2 ELK 로그 분석**
Filebeat → Logstash → Elasticsearch 수집 파이프라인 구성, Kibana 에러율·응답시간·트래픽 분석 대시보드 구성을 다룹니다.
- 8.2.1 로그 수집 파이프라인
- 8.2.2 Kibana 로그 분석 대시보드

**8.3 Observability**
Elastic Observability에서 Logs/Metrics/APM 통합 분석, Observability 워크로드를 위한 Data Stream 네이밍 규칙과 ILM 정책 설계를 다룹니다.
- 8.3.1 Logs + Metrics + APM 통합
- 8.3.2 Observability 데이터 스트림 설계
