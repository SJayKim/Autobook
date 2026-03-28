---
source_id: 016
title: "LangSmith — LLM-as-Judge 평가 정의 방법 (Criteria Scoring, Reference-free/based)"
url: "https://docs.langchain.com/langsmith/llm-as-judge"
type: docs
scraped_at: 2026-03-27
keywords: ["LLM-as-judge", "evaluators"]
content_length: 2980
---

# LangSmith — LLM-as-Judge 평가 정의 방법 (Criteria Scoring, Reference-free/based)

## LLM-as-Judge란

LLM-as-judge 평가 방법론은 LLM을 사용하여 다른 LLM 애플리케이션의 출력 품질을 평가하는 방식이다. "judge" 역할을 하는 모델에게 입력, 출력, 점수 루브릭(rubric)을 제공하고, judge 모델은 추론과 함께 점수를 산출한다.

핵심 문제를 해결한다: "LLM 애플리케이션은 대화형 텍스트를 생성하는 경우가 많아 단일한 정답이 없어 평가가 어렵다."

## 평가 구성 단계

### 1. 프롬프트 설정
- 커스텀 프롬프트를 작성하거나 프롬프트 허브에서 선택
- 변수 매핑(variable mapping): 실행 또는 예제에서 평가 프롬프트로 전달되는 변수를 지정
- 포맷: `{{variable}}` (mustache) 또는 `{variable}` (f-string)

### 2. 모델 선택
평가에 사용할 LLM 모델을 선택한다.

### 3. 점수 루브릭 정의 (Feedback Configuration)
세 가지 타입:
- **Boolean**: 참/거짓 (예: 정답 여부)
- **Categorical**: 사전 정의된 옵션 중 선택 (예: "좋음/보통/나쁨")
- **Continuous**: 수치 범위 (예: 1~5점)

## Reference-free 평가

레퍼런스 출력 없이 단독으로 평가한다. 평가 가능한 기준:
- 명확성 (clarity)
- 일관성 (coherence)
- 도움 정도 (helpfulness)
- 톤 (tone)
- 간결성 (conciseness)

## Reference-based 평가

레퍼런스(기대 출력)와 비교하여 평가한다:
- 정확성 (correctness) — 의미적 유사성 확인
- 사실 정확도 (factual accuracy)
- 정확 일치 (exact match)
- Hallucination 감지 — 레퍼런스에 없는 내용 추가 여부

## UI 내장 Evaluator 유형

| 유형 | 설명 |
|------|------|
| Hallucination | 사실적으로 부정확한 출력 감지 |
| Correctness | 레퍼런스와의 의미적 유사성 |
| Conciseness | 질문에 대한 간결한 답변 여부 |

## Human Corrections으로 품질 향상

평가 점수에 대한 인간 수정(corrections)을 수집하면:
1. 수정 사항이 few-shot 예제로 자동 삽입된다
2. 평가 프롬프트의 human preference 정렬이 점진적으로 향상된다

## Python SDK 예시

```python
from langsmith import evaluate
from langsmith.evaluation import LangChainStringEvaluator

# LangChain 내장 evaluator 사용
evaluator = LangChainStringEvaluator("criteria", config={
    "criteria": {
        "helpfulness": "Is this response helpful to the user?",
        "conciseness": "Is the response concise and to the point?"
    }
})

results = evaluate(
    my_app,
    data="my-dataset",
    evaluators=[evaluator]
)
```

## 데이터셋 바인딩

UI에서 데이터셋에 LLM-as-judge evaluator를 바인딩하면 이후 실험에 자동 적용된다.
