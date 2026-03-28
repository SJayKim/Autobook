---
source_id: 035
title: "LangSmith — Set Up Automation Rules (Filter, Sampling, Actions)"
url: "https://docs.langchain.com/langsmith/rules"
type: docs
scraped_at: 2026-03-27
keywords: ["automation rules", "filter condition", "sampling", "webhook trigger", "dataset addition"]
content_length: 2620
---

# LangSmith — Set Up Automation Rules (Filter, Sampling, Actions)

## 개요

LangSmith의 자동화 규칙(Automation Rules)은 트레이스 데이터에 대해 필터, 샘플링, 액션의 세 가지 요소를 조합하여 자동으로 작업을 수행하는 메커니즘입니다. 대규모 프로덕션 환경에서 수동 개입 없이 데이터를 분류·처리할 수 있습니다.

## 핵심 구성 요소

### 1. 필터 조건 (Filter Condition)

트레이스 프로젝트의 필터와 동일한 방식으로 작동하며, 자동화 규칙이 적용될 대상을 정의합니다.

지원하는 필터 유형:
- **지연시간(Latency)**: 비정상적으로 오래 걸린 실행 대상 지정
- **오류 기반**: breaking error가 발생한 실행 식별
- **사용자 피드백**: 긍정/부정 피드백 데이터 구분
- **메타데이터/태그**: 설정 기반 부분집합 필터링
- **전문 텍스트 검색**: 자연어 기반 쿼리로 실행 필터링
- **Trace attributes**: 부모 추적 기반 필터
- **Tree attributes**: 자식 추적을 포함한 필터
- **AI 쿼리**: 자연어를 필터 조건으로 자동 변환

### 2. 샘플링 레이트 (Sampling Rate)

0과 1 사이의 값으로 설정됩니다. 필터를 통과한 실행 중 실제로 액션을 트리거할 비율을 제어합니다.

예시: 샘플링 레이트 0.5 → 필터를 통과한 트레이스의 50%에만 액션 적용

이를 통해 고비용 작업(예: LLM 평가)을 전체 트레이스가 아닌 일부 샘플에만 적용하여 비용을 절감합니다.

### 3. 액션 (Action)

네 가지 주요 액션을 선택할 수 있습니다.

| 액션 | 설명 |
|------|------|
| **Add to Dataset** | 트레이스의 입출력을 지정된 데이터셋에 자동 추가 |
| **Add to Annotation Queue** | 인간 검토를 위해 주석 큐로 트레이스 전송 |
| **Trigger Webhook** | 트레이스 데이터와 함께 지정된 웹훅 URL에 POST 요청 전송 |
| **Extend Data Retention** | 기본 데이터 보관 기간을 초과하여 특정 트레이스의 보관 기간 연장 |

## 웹훅 트리거 (Webhook Trigger)

자동화 규칙에 웹훅 URL을 등록하면, 규칙이 정의한 조건과 일치하는 새 실행이 발생할 때마다 해당 엔드포인트에 HTTP POST 요청이 전송됩니다.

웹훅 설정 시 커스텀 헤더(Authorization, Content-Type 등)를 추가하여 인증된 엔드포인트에 연결할 수 있으며, 헤더 값은 암호화된 형식으로 저장됩니다.

## 데이터셋 추가 (Dataset Addition)

Add to Dataset 액션을 통해 실제 프로덕션 트레이스를 자동으로 학습/평가 데이터셋에 추가할 수 있습니다. 예를 들어 사용자가 thumbs-down 피드백을 준 트레이스를 자동으로 "실패 케이스 데이터셋"에 추가하는 파이프라인을 구성할 수 있습니다.

## 설정 방법

1. LangSmith UI의 Tracing 섹션에서 대상 프로젝트 선택
2. `+ New` → `New Automation` 클릭
3. 규칙 이름 입력
4. 필터 조건 구성
5. 샘플링 레이트 설정 (기본값 1.0)
6. (선택) `Apply to past runs` 토글 활성화 및 적용 날짜 입력
7. 원하는 액션 선택 및 구성

## 모니터링 및 로그

자동화 탭의 **Logs** 버튼을 통해 규칙 실행 이력을 추적하고, 오류 확인 및 규칙 진행 상황을 모니터링할 수 있습니다.
