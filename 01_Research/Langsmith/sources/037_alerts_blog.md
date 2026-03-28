---
source_id: 037
title: "Catch Production Failures Early with LangSmith Alerts"
url: "https://blog.langchain.com/langsmith-alerts/"
type: blog
scraped_at: 2026-03-27
keywords: ["alerts", "metric alerts", "threshold configuration", "monitoring dashboards"]
content_length: 1580
---

# Catch Production Failures Early with LangSmith Alerts

## 핵심 기능

LangSmith Alerts는 프로덕션 환경에서 에러율, 실행 지연시간, 피드백 점수에 대한 실시간 알림을 제공합니다. 고객에게 영향을 미치기 전에 문제를 사전에 감지하는 것이 핵심 목표입니다.

## 지원 메트릭 3가지

1. **에러 카운트 및 비율**: 시간 윈도우 내 에러 발생 수와 전체 대비 비율
2. **평균 응답 속도(Latency)**: 실행 시간 평균 측정
3. **평균 피드백 점수(Feedback Score)**: 사용자 피드백 및 온라인 평가 결과

## 설정 옵션

**필터링**: 모델, 도구 호출, 실행 유형 등으로 특정 실행 집합에 집중합니다.

**집계 윈도우**: 5분 또는 15분 단위로 설정합니다.

**임계값(Threshold)**: 알림 민감도를 조정하는 수치를 설정합니다.

## 알림 전달 방식

- **PagerDuty**: 인시던트 관리 워크플로우와 통합하여 온콜 엔지니어에게 에스컬레이션
- **Custom Webhook**: Slack 채널 등 커스텀 서비스에 알림 전송

## 향후 계획 (Roadmap)

공식 블로그에서 다음 기능을 예고하였습니다.

- 실행 카운트 및 LLM 토큰 사용량 기반 알림
- 상대값 기반 변화 알림 (예: 지연시간 25% 증가 시)
- 사용자 정의 시간 윈도우 알림

## 실전 활용 예시

API 레이트 리밋 위반이 발생하면 에러율이 급증합니다. LangSmith Alerts를 통해 5분 집계 윈도우에서 에러율이 5%를 초과하는 순간 PagerDuty 인시던트가 자동 생성되어 온콜 엔지니어에게 즉시 알림이 전달됩니다.
