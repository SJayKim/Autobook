---
source_id: 036
title: "LangSmith — Configure Alerts with Webhook and Metric Thresholds"
url: "https://docs.langchain.com/langsmith/alerts-webhook"
type: docs
scraped_at: 2026-03-27
keywords: ["alerts", "metric alerts", "webhook alert", "threshold configuration"]
content_length: 2890
---

# LangSmith — Configure Alerts with Webhook and Metric Thresholds

## 개요

LangSmith Alerts는 API 레이트 리밋 위반, 지연시간 증가, 피드백 점수 저하 등 프로덕션 환경의 중요 이슈를 사전에 감지하여 실시간으로 알림을 전달합니다. 각 프로젝트마다 별도로 알림을 설정합니다.

## 지원 메트릭 유형

| 메트릭 | 설명 | 주요 용도 |
|--------|------|-----------|
| **Run Count** | 시간 윈도우 내 전체 실행 수 | 파이프라인 예상 볼륨 이상 감지 |
| **Errors** | 에러 상태 실행 수 또는 에러율 | 애플리케이션 실패 감시 |
| **Feedback Score** | 평균 피드백 점수 | 사용자 피드백/온라인 평가 결과 기반 회귀 감지 |
| **Latency** | 평균 실행 시간 | 성능 저하 및 병목 추적 |

## 임계값 설정 (Threshold Configuration)

임계값 설정에는 다음 구성 요소가 필요합니다.

- **집계 방법**: 평균(Average), 백분율(Percentage), 카운트(Count)
- **비교 연산자**: `>=`, `<=` 또는 임계값 초과
- **임계값(Threshold)**: 알림을 트리거할 수치
- **집계 윈도우(Aggregation Window)**: 5분 또는 15분
- **피드백 키**: Feedback Score 알림에만 해당

설정 예시: "5분 내 5% 이상의 실행에서 에러 발생 시 알림"

## 필터 적용

모델, 도구 호출, 실행 유형 등으로 특정 실행 집합에만 집중하는 필터를 적용할 수 있습니다. 이를 통해 특정 LLM 모델이나 특정 엔드포인트에 대해서만 알림을 받을 수 있습니다.

## Webhook 알림 설정

### 필수 설정

- **URL**: 수신 엔드포인트의 전체 주소 (HTTPS 권장)

### 선택 설정

- **Headers**: Authorization, Content-Type 등 JSON 형식으로 지정
- **Request Body**: 커스텀 JSON 페이로드 추가 가능

### 자동 추가 필드 (Webhook Payload)

LangSmith가 자동으로 다음 필드를 페이로드에 추가합니다.

```json
{
  "project_name": "my-project",
  "alert_rule_id": "uuid-...",
  "alert_rule_name": "High Error Rate",
  "alert_rule_type": "threshold",
  "alert_rule_attribute": "error_count",
  "triggered_metric_value": 0.08,
  "triggered_threshold": 0.05,
  "timestamp": "2026-03-27T10:00:00Z"
}
```

`alert_rule_attribute` 값: `error_count`, `feedback_score`, `latency` 중 하나

## Slack 연동 예시

Webhook을 Slack에 연결하는 설정:

- **엔드포인트**: `https://slack.com/api/chat.postMessage`
- **헤더**: Authorization Bearer 토큰 + Content-Type: application/json
- **바디**: channel(채널 ID), text(메시지), blocks(Slack Block Kit 포맷)

## 모범 사례

- 애플리케이션의 중요도에 따라 임계값 민감도를 조정합니다.
- 처음에는 광범위한 임계값에서 시작하여 패턴을 관찰한 후 점진적으로 세분화합니다.
- 알림이 적절한 온콜 담당자에게 라우팅되도록 설정을 검토합니다.
