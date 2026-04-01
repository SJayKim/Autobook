# 8.3 Observability

이 섹션에서는 Elastic Observability를 활용하여 로그(Logs), 메트릭(Metrics), APM 트레이스(Traces)를 통합적으로 모니터링하는 시스템을 구축합니다. 현대 분산 서비스 환경에서 장애를 신속하게 감지하고 원인을 추적하는 방법을 익힙니다.

## 토픽 목록

**8.3.1 Logs + Metrics + APM 통합**
- Elastic Observability에서 Logs, Metrics, APM 데이터를 통합 분석할 수 있다

Elastic Observability 구성요소, APM(Application Performance Monitoring) 에이전트, 분산 추적(trace_id, span_id), 서비스 맵(Service Map), Metricbeat로 인프라 메트릭 수집, Logs 탐색기와 APM 트레이스 연계, SLO(Service Level Objective) 설정, Uptime 모니터링을 다룹니다.

**8.3.2 Observability 데이터 스트림 설계**
- Observability 워크로드를 위한 Data Stream 네이밍 규칙과 ILM 정책을 설계할 수 있다

ECS 기반 데이터 스트림 네이밍({type}-{dataset}-{namespace}), logs-*/metrics-*/traces-* 패턴, Observability 데이터 보존 정책, Hot-Warm-Cold 티어링 설계, 샤드 크기와 롤오버 조건 설정, 대용량 메트릭 다운샘플링(downsampling), Kibana Observability Overview 대시보드를 다룹니다.
