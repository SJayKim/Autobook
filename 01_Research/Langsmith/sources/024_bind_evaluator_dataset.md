---
source_id: 024
title: "LangSmith — 데이터셋에 Evaluator 바인딩 (UI 구성, Code Evaluator, 자동 실험 채점)"
url: "https://docs.langchain.com/langsmith/bind-evaluator-to-dataset"
type: docs
scraped_at: 2026-03-27
keywords: ["evaluators", "datasets", "experiments"]
content_length: 2210
---

# LangSmith — 데이터셋에 Evaluator 바인딩 (UI 구성, Code Evaluator, 자동 실험 채점)

## 개요

LangSmith는 데이터셋에 evaluator를 바인딩하여 새로운 실험에 자동으로 채점을 적용하는 기능을 제공한다. SDK 기반 evaluator와 함께 동작한다.

> "데이터셋에 바인딩된 evaluator는 이후에 생성되는 모든 새 실험에 자동으로 실행된다."

**중요한 타이밍**: 바인딩 구성 이후에 생성된 실험에만 적용되며, 기존 실험에는 소급 적용되지 않는다.

## 구성 단계

1. **Datasets and Experiments** 탭으로 이동
2. 대상 데이터셋 선택
3. **+ Evaluator** 버튼 클릭하여 구성 패널 열기

## Evaluator 유형

### LLM-as-a-Judge Evaluator
Playground 기반 LLM judge와 동일한 구성 패턴을 따른다:
- 프롬프트 선택 또는 작성
- 모델 선택
- 피드백 타입 설정 (Boolean / Categorical / Continuous)

### Custom Code Evaluator
Python 코드로 직접 평가 로직을 작성한다. Online evaluation의 code evaluator와 유사하나, **데이터셋 Example 데이터에 접근**할 수 있다는 점이 다르다.

```python
def exact_match(run, example):
    """
    run: 실험 출력이 담긴 Run 객체
    example: 데이터셋의 Reference 데이터가 담긴 Example 객체
    """
    return {
        "key": "exact_match",
        "score": int(run.outputs["answer"] == example.outputs["answer"])
    }
```

함수 파라미터:
- **`run`**: 평가 중인 실험 출력 (Run 객체)
- **`example`**: 데이터셋의 레퍼런스 데이터 (Example 객체)

허용 라이브러리: 표준 라이브러리 + `numpy`, `pandas`, `jsonschema`, `scipy`, `sklearn`

## 자동 채점 워크플로

1. 데이터셋에 evaluator 바인딩
2. 팀이 `evaluate(my_app, data="dataset-name")` 실행
3. LangSmith가 SDK evaluator + 바인딩된 evaluator 모두 자동 실행
4. 실험 결과 페이지에서 모든 점수 확인

## 활용 시나리오

- CI/CD 파이프라인에서 자동 품질 게이트
- 팀 전체가 동일한 평가 기준으로 실험 비교
- 데이터셋에 새 예제 추가 시 자동 품질 검증
