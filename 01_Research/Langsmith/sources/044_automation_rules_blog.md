---
source_id: 044
title: "LangSmith: Production Monitoring and Automations"
url: "https://blog.langchain.com/langsmith-production-logging-automations/"
type: blog
scraped_at: 2026-03-27
keywords: ["automation rules", "filter condition", "sampling", "dataset addition"]
content_length: 1720
---

# LangSmith: Production Monitoring and Automations

## 자동화 규칙의 목적

LangSmith의 자동화 기능은 수동 개입 없이 프로덕션 트레이스 데이터를 자동으로 처리합니다. 필터링, 샘플링 속도, 실행 액션의 세 요소를 조합하여 규칙을 구성합니다.

## 필터링 옵션

자동화 규칙에서 지원하는 다양한 필터 방식:

**기본 필터**:
- 지연시간(Latency)으로 비정상적으로 오래 걸린 실행 대상 지정
- 오류 기반 필터링으로 breaking error 식별
- 사용자 피드백으로 긍정/부정 데이터 구분
- 메타데이터/태그로 설정 기반 부분집합 필터링
- 전문 텍스트 검색

**고급 필터**:
- Trace attributes (부모 추적 기반)
- Tree attributes (자식 추적 포함)
- AI 쿼리 (자연어를 필터 조건으로 자동 변환)

## 샘플링 속도

0과 1 사이의 비율로, 필터를 만족하는 데이터포인트 중 실제로 액션을 적용할 비율을 설정합니다. 비용이 높은 액션(예: LLM-as-judge 온라인 평가)을 전체 트레이스가 아닌 일부 샘플에만 적용하여 비용을 절감합니다.

## 실행 가능한 액션

| 액션 | 설명 |
|------|------|
| **데이터셋 추가** | 선택된 실행을 자동으로 데이터셋에 추가 |
| **주석 큐 추가** | 데이터포인트를 인간 검토 대기열로 이동 |
| **온라인 평가** | LLM이 설정된 기준에 따라 각 실행을 자동 평가 |

## 실전 활용 사례

**데이터셋 자동 구축**: 사용자가 thumbs-down을 준 트레이스의 10%를 자동으로 "실패 케이스 데이터셋"에 추가합니다. 이를 통해 프로덕션 환경의 실제 실패 사례를 체계적으로 수집할 수 있습니다.

**품질 드리프트 감지**: 지연시간이 10초를 초과하거나 오류가 발생한 트레이스를 자동으로 주석 큐에 추가하여 인간 검토자가 확인하도록 합니다.
