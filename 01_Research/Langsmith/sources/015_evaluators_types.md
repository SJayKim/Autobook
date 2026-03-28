---
source_id: 015
title: "LangSmith Evaluators — Heuristic, LLM, Custom, Pairwise, Code Evaluator 유형"
url: "https://docs.smith.langchain.com/evaluation"
type: docs
scraped_at: 2026-03-27
keywords: ["evaluators", "LLM-as-judge"]
content_length: 3150
---

# LangSmith Evaluators — Heuristic, LLM, Custom, Pairwise, Code Evaluator 유형

## Evaluator 개요

LangSmith의 evaluator는 애플리케이션 출력 품질을 점수화하는 함수다. `evaluate()` 함수에 전달되며, 데이터셋의 각 예제에 대해 실행된다.

## Evaluator 함수 시그니처 (SDK v0.2+)

```python
def my_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> bool | int | float | str:
    # inputs: 데이터셋 예제의 입력
    # outputs: 애플리케이션 출력
    # reference_outputs: 기대 출력 (optional)
    return outputs["answer"] == reference_outputs["answer"]
```

Python evaluator는 `bool`, `int`, `float`, `str`을 직접 반환할 수 있다(딕셔너리 래핑 불필요).

## Heuristic Evaluators (규칙 기반)

결정론적 코드 로직으로 평가한다:
- 응답 길이 확인
- 지연 시간 측정
- 특정 키워드 존재 여부
- 응답 구조 비어 있지 않은지 확인
- 생성된 코드가 컴파일되는지 확인
- 분류 결과가 정확히 일치하는지 확인

## Code Evaluators (UI에서 구성)

UI에서 Python 코드를 직접 작성하는 평가 함수. 허용 라이브러리가 제한된다:
- 표준 라이브러리 함수
- 퍼블릭 패키지: `numpy`, `pandas`, `jsonschema`, `scipy`, `sklearn`

데이터셋에 evaluator를 바인딩하면 이후 생성되는 실험 실행에 자동 적용된다.

## LLM-as-Judge Evaluators

LLM을 활용하여 사람과 유사한 판단을 내리는 평가 방식이다.

### UI 내장 평가 유형
- **Hallucination**: 사실적으로 부정확한 출력 감지
- **Correctness**: 레퍼런스와의 의미적 유사성 확인
- **Conciseness**: 답변이 간결한지 평가

### Reference-free vs Reference-based
- **Reference-free**: 레퍼런스 없이 명확성, 일관성, 유용성, 톤 평가
- **Reference-based**: 정확성, 사실 정확도, exact match, 레퍼런스 기반 LLM 비교

### Human Corrections 통합
평가 점수에 대한 인간 수정(corrections)을 수집하면, 수정 사항이 자동으로 few-shot 예제로 프롬프트에 삽입되어 human preference 정렬이 향상된다.

## Pairwise Evaluators

두 실험 결과를 동시에 비교하는 평가 방식이다.

```python
from langsmith import evaluate

def pairwise_evaluator(inputs, outputs, reference_outputs=None):
    # outputs는 두 실험의 출력 리스트
    # 반환: {key: "pairwise_quality", scores: {run_id_a: 1, run_id_b: 0}}
    return [1, 0]  # 첫 번째 실험이 더 나음

results = evaluate(
    target=[experiment_a_id, experiment_b_id],
    evaluators=[pairwise_evaluator],
    randomize_order=True  # 위치 편향 최소화
)
```

피드백 키 이름 앞에 `pairwise_` 또는 `ranked_` 접두어를 붙이는 것을 권장한다.

## Summary Evaluators

개별 예제가 아닌 실험 전체를 평가하는 함수다. 실험의 모든 run에 대한 aggregate 점수를 산출한다.

## 데이터셋에 Evaluator 바인딩

UI에서 Dataset으로 이동하여 evaluator를 구성하면, 이후에 생성되는 실험 run에 자동 적용된다. 기존 run에는 소급 적용되지 않는다.
