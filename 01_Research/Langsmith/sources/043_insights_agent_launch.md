---
source_id: 043
title: "Improve Agent Quality with Insights Agent and Multi-turn Evals in LangSmith"
url: "https://blog.langchain.com/insights-agent-multiturn-evals-langsmith/"
type: blog
scraped_at: 2026-03-27
keywords: ["Insights Agent", "failure mode discovery", "pattern analysis"]
content_length: 1820
---

# Improve Agent Quality with Insights Agent and Multi-turn Evals in LangSmith

## Insights Agent 개요

Insights Agent는 에이전트 동작 패턴을 자동으로 분류하여 프로덕션 환경에서 수백만 개의 트레이스 데이터에서 패턴을 발견합니다.

## 주요 분석 방식

### 사용 패턴 분석

"사용자가 실제로 에이전트를 어떻게 사용하는지 이해"를 돕습니다. 예상치 못한 사용 패턴이나 급증하는 특정 유형의 요청을 식별합니다.

### 오류 모드 식별

에이전트가 실패하는 일반적인 방식을 이해하여 개선 우선순위를 정합니다. 부정적인 상호작용 신호를 감지하여 실패 케이스를 자동으로 그룹화합니다.

### 사용자 정의 구성

- 분류 카테고리를 원하는 방식으로 정의
- 시간 범위 필터링으로 특정 기간 분석
- 새로운 속성 정의로 분석 범위 확장

## 보고서 구성

보고서 생성에 최대 15분이 소요되며, 완성 후 트레이스 데이터가 카테고리별로 정렬됩니다. 각 카테고리에서 다음 정보를 확인합니다.
- 지연시간(Latency) 통계
- 실행 수(Run Count)
- 평가 메트릭(Evaluation Metrics)

## 계층적 분류 구조

최상위 카테고리가 가장 넓은 패턴을 나타내며, 각 카테고리가 얼마나 자주 발생하는지를 분포 막대로 표시합니다. 카테고리 내에서 더 세부적인 하위 카테고리로 드릴다운할 수 있습니다.

## 높은 구성 가능성

Insights Agent는 다음 항목을 직접 지정할 수 있어 높은 유연성을 제공합니다.
- 그룹화 카테고리 지정
- 기존 속성(시간 범위, 키워드 등)으로 필터링
- 새로운 속성 정의
- 설정을 저장하여 이후 재사용

## 가용성

LangSmith Plus 및 Enterprise 클라우드 고객 대상으로 일반 공개(Generally Available)되었습니다.
