---
source_id: 042
title: "LangSmith — Unified Cost Tracking for LLMs, Tools, and Retrieval"
url: "https://changelog.langchain.com/announcements/unified-cost-tracking-for-llms-tools-retrieval"
type: web
scraped_at: 2026-03-27
keywords: ["cost and token tracking", "LLM 비용", "provider cost breakdown", "monitoring dashboards"]
content_length: 1460
---

# LangSmith — Unified Cost Tracking for LLMs, Tools, and Retrieval

## 발표 개요

LangSmith는 복잡한 에이전트 애플리케이션 전반의 지출을 모니터링하는 "full-stack cost tracking" 기능을 추가하였습니다.

## 핵심 기능

### 자동 비용 계산

주요 모델 제공자(OpenAI, Anthropic 등)의 토큰 사용량을 기반으로 자동 기록합니다. 멀티모달 토큰 유형과 캐시 읽기를 포함한 공급자 인식(provider-aware) 가격 설정을 지원합니다.

### 수동 비용 제출

모든 실행 유형(LLM, tools, retrieval, 커스텀 작업)에 대해 커스텀 비용 데이터를 제출할 수 있습니다. 단순 LLM 비용만이 아닌 에이전트 전체 파이프라인의 비용을 통합적으로 추적합니다.

## 비용 가시화

추적된 비용은 다음 위치에서 확인합니다.
- 트레이스 트리 구조에서 실행별 상세 비용
- 프로젝트 통계에서 집계 비용
- 대시보드에서 시간별 비용 추이

## 커스텀 가격 설정

모델 가격 맵 편집기를 통해 커스텀 모델을 추가하거나 기본 가격을 재설정할 수 있습니다. 기업 협상 요금이나 커스텀 모델에 대해서도 정확한 비용 보고가 가능합니다.

## 지원 제공자

LangSmith는 주요 OpenAI, Anthropic, Gemini 모델의 가격 데이터를 기본 내장합니다. 다른 공급자나 비표준 가격 체계에는 사용자 정의 토큰 수와 가격 매핑을 제공합니다.
