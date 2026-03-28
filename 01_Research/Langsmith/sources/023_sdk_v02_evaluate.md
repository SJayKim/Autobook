---
source_id: 023
title: "LangSmith SDK v0.2 — evaluate() 통합 API, num_repetitions, Custom Evaluators"
url: "https://blog.langchain.com/easier-evaluations-with-langsmith-sdk-v0-2/"
type: blog
scraped_at: 2026-03-27
keywords: ["evaluators", "experiments"]
content_length: 2720
---

# LangSmith SDK v0.2 — evaluate() 통합 API, num_repetitions, Custom Evaluators

## SDK v0.2의 주요 변화

SDK v0.2는 기존의 세 가지 평가 메서드를 단일 `evaluate()` / `aevaluate()` 함수로 통합했다.

### 이전 방식 (v0.1)
- `evaluate()` — 애플리케이션을 데이터셋에 실행하고 점수화
- `evaluate_existing()` — 기존 실험 결과에 evaluator 실행
- `evaluate_comparative()` — 두 실험을 pairwise 비교

### 새 방식 (v0.2)
```python
from langsmith import evaluate

# 1. 새 실험 실행 + 평가
results = evaluate(my_app, data="dataset-name", evaluators=[correct])

# 2. 기존 실험에 추가 평가
results = evaluate(existing_experiment_id, evaluators=[new_evaluator])

# 3. Pairwise 비교 평가
results = evaluate([exp_a_id, exp_b_id], evaluators=[pairwise_eval])
```

## 단순화된 Evaluator 시그니처

v0.2 이전에는 `Run`과 `Example` 객체를 직접 받아야 했다. v0.2부터 세 가지 파라미터로 단순화됐다:

```python
def correct(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    return outputs["answer"] == reference_outputs["answer"]
```

반환 타입도 단순화됐다. 딕셔너리 래핑 없이 **기본 타입**을 직접 반환할 수 있다:
- `bool` → 참/거짓 평가
- `int` / `float` → 수치 점수
- `str` → 카테고리 레이블

## num_repetitions (반복 실행)

비결정론적 출력의 분산을 측정하기 위해 각 예제를 여러 번 실행한다:

```python
results = evaluate(
    my_app,
    data="dataset-name",
    evaluators=[correct],
    num_repetitions=5   # 각 예제를 5번 실행
)
```

## 지원하는 평가 유형

| 유형 | 설명 | 사용 방법 |
|------|------|----------|
| Standard evaluators | 각 예제별 점수화 | `evaluators=[fn]` |
| Summary evaluators | 실험 전체 집계 | `summary_evaluators=[fn]` |
| Pairwise evaluators | 두 실험 비교 | `target=[exp_a, exp_b]` |
| Intermediate step | 중간 추론 단계 평가 | runs 파라미터 접근 |

## LangGraph / LangChain 직접 전달

프레임워크 객체를 직접 `evaluate()`에 전달할 수 있다:

```python
from langgraph.graph import StateGraph

graph = StateGraph(...)  # LangGraph 그래프 정의
results = evaluate(graph, data="my-dataset", evaluators=[my_evaluator])
```

## 성능 개선

- 비동기 평가 **30% 속도 향상** (4MB 이하 예제 기준)
- 기본 동시성: `max_concurrency=0` (이전: 무제한)

## Local Evaluation Mode (beta, Python only)

결과를 LangSmith에 업로드하지 않고 로컬에서만 평가:

```python
results = evaluate(
    my_app,
    data="dataset-name",
    evaluators=[correct],
    upload_results=False
)
# 결과를 로컬에서 직접 분석
df = results.to_pandas()
```
