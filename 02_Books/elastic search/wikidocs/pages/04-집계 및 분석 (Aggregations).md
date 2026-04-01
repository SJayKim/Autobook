# Phase 4. 집계 및 분석 (Aggregations)

이 Phase를 마치면 Bucket/Metric/Pipeline 집계를 중첩하여 복합 분석 쿼리를 작성하고, Kibana Dashboard로 시각화할 수 있게 됩니다.

Elasticsearch는 단순한 검색 엔진을 넘어 강력한 분석 플랫폼입니다. 집계(Aggregations) 기능을 사용하면 수억 건의 문서에서 통계량을 계산하고, 시계열 트렌드를 분석하며, 다차원 그룹별 지표를 집계할 수 있습니다. Phase 4에서는 집계의 기본 구조부터 중첩 집계, Pipeline 집계, Kibana 시각화까지 다룹니다.

첫 번째 섹션에서는 집계의 기본 문법 구조와 Bucket/Metric 집계를 다룹니다. 두 번째 섹션에서는 중첩 집계, Pipeline 집계, composite 집계, 집계 성능 최적화를 다룹니다. 세 번째 섹션에서는 Kibana Lens, Dashboard, KQL을 통한 시각화를 다룹니다.

## 이 Phase의 섹션 구성

**4.1 집계 기초**
집계 구문 구조, Bucket 집계(terms, date_histogram, range 등), Metric 집계(avg, sum, cardinality 등)를 다룹니다.
- 4.1.1 집계 구문 구조
- 4.1.2 Bucket 집계
- 4.1.3 Metric 집계

**4.2 고급 집계**
중첩 집계, Pipeline 집계(derivative, cumulative_sum 등), composite 집계, 집계 성능 최적화를 다룹니다.
- 4.2.1 중첩 집계
- 4.2.2 Pipeline 집계
- 4.2.3 composite 집계
- 4.2.4 집계 성능 최적화

**4.3 Kibana 시각화**
Kibana Lens로 시각화 생성, Dashboard 구성 및 공유, KQL(Kibana Query Language) 사용법을 다룹니다.
- 4.3.1 Kibana Lens
- 4.3.2 Kibana Dashboard
- 4.3.3 KQL (Kibana Query Language)
