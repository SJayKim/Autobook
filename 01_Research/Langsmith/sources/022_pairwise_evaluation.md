---
source_id: 022
title: "LangSmith — Pairwise Evaluation (evaluate_comparative, 비교 평가, 위치 편향)"
url: "https://docs.langchain.com/langsmith/evaluate-pairwise"
type: docs
scraped_at: 2026-03-27
keywords: ["evaluators", "experiments", "annotation queues"]
content_length: 2560
---

# LangSmith — Pairwise Evaluation (evaluate_comparative, 비교 평가, 위치 편향)

## Pairwise Evaluation 개요

Pairwise evaluation은 두 실험 결과를 동시에 비교하여 어느 쪽이 더 나은지 판단하는 평가 방식이다. 단일 출력의 절대적 점수보다 더 신뢰할 수 있는 피드백을 생성한다.

## evaluate() 함수 사용법 (Python ≥ 0.2.0, JS ≥ 0.2.9)

```python
from langsmith import evaluate

def pairwise_evaluator(inputs, outputs, reference_outputs=None):
    """
    inputs: dict — 데이터셋 예제 입력
    outputs: list[dict] — 두 실험의 출력 (길이 2)
    reference_outputs: dict — 정답 (있는 경우)
    """
    quality_a = score_response(outputs[0]["answer"])
    quality_b = score_response(outputs[1]["answer"])

    return {
        "key": "pairwise_quality",
        "scores": {run_a_id: quality_a, run_b_id: quality_b},
        "comment": "A was more concise"
    }

results = evaluate(
    target=[experiment_a_id, experiment_b_id],
    evaluators=[pairwise_evaluator],
    randomize_order=True,         # 위치 편향 최소화
    experiment_prefix="pairwise",
    max_concurrency=5
)
```

## evaluate_comparative() 함수

두 개 이상의 실험을 비교하려면 `evaluate_comparative()`를 사용한다:

```python
from langsmith.evaluation import evaluate_comparative

results = evaluate_comparative(
    experiments=[exp_a, exp_b, exp_c],
    evaluators=[my_pairwise_evaluator]
)
```

## 핵심 파라미터

| 파라미터 | 설명 |
|---------|------|
| `target` | 두 기존 실험의 UUID 또는 이름 |
| `evaluators` | pairwise evaluator 함수 목록 |
| `randomize_order` | 위치 편향 최소화 (기본값: False) |
| `experiment_prefix` | pairwise 실험의 이름 접두어 |
| `max_concurrency` | 동시 평가 수 (기본값: 5) |

## Evaluator 반환 형식

**딕셔너리 형식:**
```python
{
    "key": "pairwise_quality",
    "scores": {run_id_a: 1, run_id_b: 0},
    "comment": "A was more helpful"
}
```

**리스트 형식 (순서 기반):**
```python
return [1, 0]  # 첫 번째 실험: 1점, 두 번째: 0점
```

## 피드백 키 네이밍 관행

Pairwise evaluator의 피드백 키에는 `pairwise_` 또는 `ranked_` 접두어를 붙이는 것을 권장한다. 일반 피드백과 구분하기 위해서다:
- `pairwise_quality`
- `ranked_helpfulness`

## 언제 Pairwise를 사용하는가

- 두 모델 버전의 상대적 품질 비교
- A/B 테스팅
- 절대 점수를 정의하기 어려운 주관적 품질 평가
- 더 신뢰할 수 있는 human preference 수집

## UI Pairwise Annotation Queue와의 관계

SDK의 pairwise evaluation은 자동화된 LLM 기반 비교 평가이고, Pairwise Annotation Queues는 인간 어노테이터가 직접 비교하는 수동 방식이다. 두 방식 모두 동일한 피드백 키 구조를 사용한다.
