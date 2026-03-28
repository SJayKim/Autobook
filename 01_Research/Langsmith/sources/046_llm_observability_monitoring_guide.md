---
source_id: 046
title: "LLM Observability: A Guide to Monitoring with LangSmith — Latency, Token Usage, Error Rate"
url: "https://activewizards.com/blog/llm-observability-a-guide-to-monitoring-with-langsmith"
type: web
scraped_at: 2026-03-27
keywords: ["monitoring dashboards", "latency metrics", "token usage", "error rate", "P50/P99"]
content_length: 1640
---

# LLM Observability: A Guide to Monitoring with LangSmith — Latency, Token Usage, Error Rate

## 모니터링 핵심 지표

LangSmith와 Prometheus, Grafana를 통합한 LLM 시스템 관찰성(Observability) 구축 접근법입니다.

## 대시보드 구성 요소

### Cost Monitoring 패널

모델별 토큰 사용량을 시각화하며 실시간 비용 추적이 가능합니다. 시간 경과에 따른 비용 추이를 파악하여 예상치 못한 비용 급증에 대응합니다.

### Performance & Latency 패널

P50, P90, P99 지연시간을 히스토그램 또는 히트맵으로 표시합니다.

- **P50**: 중앙값 지연시간 — 전형적인 응답 속도
- **P90**: 90번째 백분위 — 대부분의 사용자 경험
- **P99**: 99번째 백분위 — 최악의 경우 응답 시간

## 모니터링 메트릭 상세

### 토큰 사용량

`llm_agent_tokens_total` 카운터로 측정하며, 프롬프트 토큰과 응답 토큰을 구분하여 추적합니다.

### 요청 지연시간

`llm_agent_request_latency_seconds` 히스토그램으로 수집합니다. 분위수별 집계로 P50/P99를 계산합니다.

### 오류율

Failed requests와 tool execution errors를 통해 오류율을 모니터링합니다.

## 통합 아키텍처 — "관찰성의 황금 삼각형"

| 도구 | 역할 |
|------|------|
| LangSmith | 정성적 추적 데이터 (트레이스, 입출력) |
| Prometheus | 시계열 메트릭 수집 및 저장 |
| Grafana | 대시보드 시각화 |

세 도구의 역할 분담을 통해 성능 이상 발생 시 근본 원인 파악이 효과적입니다. LangSmith의 정성적 트레이스 데이터와 Prometheus의 정량적 메트릭을 함께 활용하면 "무엇이 문제인가"와 "왜 문제인가"를 모두 파악할 수 있습니다.
