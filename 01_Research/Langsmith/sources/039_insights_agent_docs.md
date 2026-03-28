---
source_id: 039
title: "LangSmith — Discover Errors and Usage Patterns with the Insights Agent"
url: "https://docs.langchain.com/langsmith/insights"
type: docs
scraped_at: 2026-03-27
keywords: ["Insights Agent", "failure mode discovery", "pattern analysis"]
content_length: 2760
---

# LangSmith — Discover Errors and Usage Patterns with the Insights Agent

## 기본 개념

Insights Agent는 자동으로 트레이스를 분석하여 사용 패턴, 에이전트 동작, 실패 모드를 감지합니다. 계층적 분류를 활용하여 대규모 데이터에서 실행 가능한 추세를 도출합니다.

## 작동 방식

### 핵심 4단계 프로세스

1. **Trace 요약**: 각 트레이스에 대해 간단한 요약을 생성합니다. 요약 단계에서 추출할 정보와 트레이스 콘텐츠를 지정하는 프롬프트를 사용합니다.
2. **클러스터링**: 사고 모델(thinking model)이 요약된 트레이스들을 그룹화합니다.
3. **범주화**: 자동 생성 또는 사용자 정의 상위 범주로 조직합니다.
4. **세부 분류**: 각 범주 내에서 하위 범주가 추가로 생성됩니다.

### 사용 모델

- **사고 모델(Thinking Model)**: 클러스터링 단계 수행. 높은 성능, 상대적으로 높은 비용
- **요약 모델(Summary Model)**: 트레이스별 요약 생성. 빠른 속도, 낮은 비용

## 주요 분석 기능

### Executive Summary

각 보고서 상단에 발견된 가장 중요한 패턴과 백분율을 포함한 주요 결과가 표시됩니다.

### 사용 패턴 분석 (Usage Pattern Analysis)

에이전트가 실제로 어떻게 사용되는지 파악합니다. 예를 들어 "코드 디버깅"이 전체 대화의 35%, "데이터 분석"이 28%를 차지한다는 식의 분포를 확인할 수 있습니다.

### 실패 모드 발견 (Failure Mode Discovery)

부정적인 상호작용 신호(사용자가 불만족하거나 좌절하는 패턴 등)를 기반으로 클러스터링하여 에이전트가 실패하는 공통 방식을 그룹화합니다. 이를 통해 개선 우선순위를 정할 수 있습니다.

### 사용자 정의 속성 (Attributes)

문자열, 수치, 부울(Boolean) 속성을 추가로 정의하여 트레이스에서 추출할 수 있습니다. 이 속성들은 범주화 과정에 영향을 미칩니다.

### 필터 속성 (Filter Attributes)

부울 속성에 `filter_by` 매개변수를 추가하여 특정 트레이스 부분집합만 분석하도록 사전 필터링할 수 있습니다.

## 설정 방법

### 자동 생성 방식

자연어 질문을 입력하면 Insights Agent가 자동으로 다음 항목을 생성합니다.
- 작업(Job) 이름
- 요약 프롬프트
- 분석 속성
- 샘플링 기본값

### 수동 설정 방식

- **Trace 선택**: 최대 1,000개 트레이스 샘플 분석
- **범주 정의**: 사전 정의된 범주 또는 자동 생성 선택
- **요약 프롬프트**: 추출할 정보와 트레이스 콘텐츠 직접 지정

## 스케줄링

정기적 실행을 위해 다음 옵션을 제공합니다.
- 일일(Daily)
- 주간 — 매주 월요일(Weekly on Monday)
- 커스텀 cron 표현식

## 가용성

LangSmith Plus 및 Enterprise 클라우드 고객을 대상으로 일반 공개(GA) 상태입니다.
