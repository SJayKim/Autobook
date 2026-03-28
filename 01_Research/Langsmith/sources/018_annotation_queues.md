---
source_id: 018
title: "LangSmith — Annotation Queues (인간 리뷰 큐, Rubric, Pairwise Annotation)"
url: "https://docs.langchain.com/langsmith/annotation-queues"
type: docs
scraped_at: 2026-03-27
keywords: ["annotation queues"]
content_length: 3280
---

# LangSmith — Annotation Queues (인간 리뷰 큐, Rubric, Pairwise Annotation)

## Annotation Queues 개요

Annotation Queues는 인간 어노테이터가 특정 run에 피드백을 첨부하는 **스트림라인된 뷰**를 제공한다. Run들을 그룹으로 묶어 검토하고 피드백을 제공하는 워크플로를 구성한다.

두 가지 큐 유형:
1. **Single-run queues**: 한 번에 하나의 run을 보여줌
2. **Pairwise Annotation Queues (PAQs)**: 두 run을 나란히 표시하여 A/B 비교 평가

## Single-Run Queue 생성

### 기본 설정
- 큐 이름과 설명 입력
- 검토된 run을 내보낼 기본 데이터셋 지정 (optional)

### Rubric 구성
검토자 가이드라인 설정:
- 사이드바에 표시되는 고수준 지침 작성
- 피드백 키(feedback keys)와 설명 추가
- Categorical 피드백: 카테고리 설명 지정 (어노테이터가 참조)

### 협업자 설정
- **Reviewer count**: run이 "완료" 처리되기 위해 필요한 어노테이터 수
- **Reservations**: 활성화 시 여러 사람이 동시에 같은 run을 검토하지 못하도록 차단 (만료 기간 설정 가능)

## 큐에 Run 추가하는 방법

- 트레이스 뷰에서 "Add to Annotation Queue" 버튼 클릭
- Run 테이블에서 대량 선택
- 자동화 규칙(Automation Rules)으로 특정 조건 트리거
- 데이터셋 실험에서 어노테이션 선택

## 검토 워크플로

어노테이터는 큐에 접근하여:
- run에 코멘트 첨부
- 피드백 기준에 점수 제출
- run을 데이터셋에 추가
- run을 "검토 완료" 처리
- 키보드 단축키로 작업 속도 향상

## Pairwise Annotation Queues (PAQs)

### 목적
두 실험 결과를 나란히 비교하여 어느 출력이 더 나은지 빠르게 결정하는 A/B 비교 평가 방식이다.

### 생성 절차
1. Datasets & Experiments에서 정확히 **두 개**의 실험 선택
2. "Add to Pairwise Annotation Queue" 선택
3. 큐 이름, 지침, 협업자 설정 지정
4. LangSmith가 두 실험의 run을 시간 순으로 자동 페어링

### Rubric 구성 차이
- Rubric 항목은 피드백 키만 필요 (설명 optional)
- 어노테이터는 Run A, Run B, 또는 둘 다 더 낫다고 선택

### 검토 액션
- 단축키: **A** (Run A가 더 나음), **B** (Run B가 더 나음), **E** (동등)
- 코멘트 추가, 재큐, 전체 트레이스 조회 옵션

## SDK 프로그래매틱 관리

```python
# Annotation queue 생성
queue = client.create_annotation_queue(
    name="my-review-queue",
    description="Review flagged responses",
    default_dataset="my-dataset"
)

# Run을 큐에 추가
client.add_runs_to_annotation_queue(
    queue_id=queue.id,
    run_ids=[run_id_1, run_id_2]
)
```

SDK를 통해 annotation queue와 feedback config를 프로그래매틱하게 관리할 수 있다.
