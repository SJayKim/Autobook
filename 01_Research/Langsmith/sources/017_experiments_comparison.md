---
source_id: 017
title: "LangSmith — Experiments 실행, 비교 뷰, Regression Testing, Repetitions"
url: "https://docs.smith.langchain.com/evaluation/how_to_guides/compare_experiment_results"
type: docs
scraped_at: 2026-03-27
keywords: ["experiments"]
content_length: 3020
---

# LangSmith — Experiments 실행, 비교 뷰, Regression Testing, Repetitions

## Experiments 개요

LangSmith에서 **Experiment**는 특정 데이터셋 위에서 특정 애플리케이션 버전을 평가한 결과물이다. 실험을 통해 다음을 달성한다:
- 버전 간 성능 비교 (benchmarking)
- 회귀 탐지 (regression testing)
- 유닛 테스트 (unit tests)
- 백테스팅 (backtesting)

## evaluate() 함수 기본 사용

```python
from langsmith import evaluate

def my_app(inputs: dict) -> dict:
    # 평가할 애플리케이션
    return {"answer": llm.invoke(inputs["question"])}

def correct(inputs, outputs, reference_outputs):
    return outputs["answer"] == reference_outputs["answer"]

results = evaluate(
    my_app,
    data="my-dataset",
    evaluators=[correct],
    experiment_prefix="v2-experiment",
    num_repetitions=3,      # 각 예제를 3번 반복 실행
    max_concurrency=4       # 동시 실행 수
)
```

## num_repetitions (반복 실행)

`num_repetitions` 파라미터는 각 데이터셋 예제를 몇 번 실행할지 지정한다. 기본값은 1이다. 비결정론적 LLM 출력의 분산을 측정할 때 유용하다.

## Comparison View (비교 뷰)

UI에서 여러 실험을 동시에 선택하면 **비교 뷰**가 활성화된다:
- 모든 실험 결과가 나란히 배치됨
- 특정 기준 실험(baseline) 대비 회귀를 컬러 코딩으로 표시
- 실험 간 점수 차이를 즉시 파악 가능

## Pairwise Evaluation (쌍 비교 평가)

두 실험을 동시에 비교하는 평가 방식. 단일 출력 절대 평가보다 더 신뢰할 수 있는 피드백을 생성한다.

```python
from langsmith import evaluate

def pairwise_quality(inputs, outputs, reference_outputs=None):
    # outputs: 두 실험 출력의 리스트
    score_a = evaluate_quality(outputs[0])
    score_b = evaluate_quality(outputs[1])
    return [score_a, score_b]

results = evaluate(
    target=[experiment_a_id, experiment_b_id],  # 두 기존 실험 ID
    evaluators=[pairwise_quality],
    randomize_order=True,    # 위치 편향 최소화
    experiment_prefix="pairwise-eval"
)
```

`evaluate_comparative()` 함수는 두 개 이상의 실험 비교도 지원한다.

## Summary Evaluators

개별 예제가 아닌 실험 전체를 평가하는 함수다. 예를 들어 전체 정확도 비율을 계산할 때 사용한다.

```python
def aggregate_accuracy(runs, examples):
    correct_count = sum(
        1 for r, e in zip(runs, examples)
        if r.outputs["answer"] == e.outputs["answer"]
    )
    return {"accuracy": correct_count / len(runs)}

results = evaluate(
    my_app,
    data="my-dataset",
    evaluators=[correct],
    summary_evaluators=[aggregate_accuracy]
)
```

## 기존 실험 재평가

이미 실행된 실험에 새로운 evaluator를 적용할 수 있다:

```python
# 기존 실험에 추가 평가 실행
results = evaluate(
    target=existing_experiment_id,  # 기존 실험 ID
    evaluators=[new_evaluator]
)
```

## Local Evaluation Mode (beta)

결과를 LangSmith에 업로드하지 않고 로컬에서만 평가:

```python
results = evaluate(my_app, data="dataset", evaluators=[correct], upload_results=False)
```
