# 8.1.3 DeepEval을 이용한 자동 평가

8.1.2에서 RAGAS를 활용하여 RAG 파이프라인의 품질을 정량적으로 측정하는 방법을 살펴보았습니다. RAGAS는 RAG에 특화된 지표를 제공하지만, LLM 애플리케이션이 반드시 RAG 형태만 취하는 것은 아닙니다. 챗봇, 요약, 분류, 코드 생성 등 다양한 형태의 LLM 기반 기능이 프로덕션에 투입되고 있으며, 이들 각각에 대해 환각(hallucination), 유해성(toxicity), 답변 관련성 같은 품질 속성을 측정해야 합니다. RAGAS의 지표 체계를 RAG가 아닌 일반 LLM 애플리케이션에 곧바로 적용하기는 어렵습니다. 이 단원에서는 범용 LLM 평가 프레임워크인 DeepEval을 소개하고, 자동 평가 파이프라인을 구축하는 과정을 다룹니다.

**DeepEval**은 LLM 애플리케이션의 출력 품질을 자동으로 평가하기 위한 오픈소스 Python 프레임워크입니다. "LLM 애플리케이션을 위한 pytest"라고 부르기도 하는데, 그 이유는 기존 Python 테스트 프레임워크인 pytest와 통합되어 동작하도록 설계되었기 때문입니다. pytest는 Python 코드의 함수나 클래스가 기대대로 동작하는지 자동으로 검증하는 도구입니다. DeepEval은 이 구조를 빌려, LLM의 출력에 대해서도 "이 응답이 기준을 충족하는가"를 자동으로 판정하는 테스트를 작성할 수 있게 합니다. 테스트를 코드로 작성하므로, 수동으로 응답을 읽고 판단하는 과정을 자동화할 수 있습니다.

DeepEval이 해결하려는 문제를 좀 더 구체적으로 살펴보겠습니다. LLM의 출력은 자연어 텍스트이므로, 전통적인 소프트웨어 테스트처럼 "기대값과 일치하는가"를 단순 비교할 수 없습니다. 같은 질문에 대해 표현은 다르지만 의미는 동일한 답변이 나올 수 있고, 반대로 겉보기에는 그럴듯하지만 사실과 다른 내용을 포함할 수도 있습니다. DeepEval은 이 문제를 "메트릭(metric)"이라는 단위로 접근합니다. 메트릭은 LLM 출력의 특정 품질 속성을 0에서 1 사이의 점수로 환산하는 측정 기준입니다. 개발자는 평가하고 싶은 품질 속성에 맞는 메트릭을 선택하고, 통과 기준 점수(threshold)를 설정한 뒤, 테스트를 실행합니다. 점수가 기준 이상이면 통과, 미만이면 실패로 판정됩니다.

DeepEval은 다양한 **내장 메트릭**을 제공합니다. 대표적인 것들을 하나씩 살펴보겠습니다.

첫째, **GEval**입니다. GEval은 "LLM이 LLM을 평가한다"는 개념에 기반한 메트릭입니다. 8.1.1에서 다룬 LLM-as-Judge 방식을 체계화한 것으로, 평가 기준을 자연어로 정의하면 평가용 LLM이 해당 기준에 따라 출력을 채점합니다. 예를 들어 "답변이 질문의 의도를 정확히 반영하는가"라는 기준을 텍스트로 작성하면, GEval은 이 기준을 평가 단계로 분해하고 각 단계에 점수를 매겨 종합 점수를 산출합니다. GEval의 장점은 평가 기준을 코드가 아닌 자연어로 정의할 수 있어, 새로운 품질 속성에 대한 평가를 빠르게 설정할 수 있다는 점입니다.

둘째, **Hallucination** 메트릭입니다. 이 메트릭은 LLM의 출력이 주어진 컨텍스트(참조 문서)에 없는 내용을 만들어 냈는지를 측정합니다. 컨텍스트와 출력을 비교하여, 출력에 포함된 주장 중 컨텍스트로 뒷받침되지 않는 비율을 계산합니다. 환각 비율이 높을수록 점수가 낮아집니다. RAG 파이프라인에서 검색된 문서를 기반으로 답변을 생성할 때, 모델이 문서에 없는 내용을 지어내는지 확인하는 데 유용합니다.

셋째, **Toxicity** 메트릭입니다. 이 메트릭은 LLM의 출력에 욕설, 혐오 표현, 차별적 언어, 폭력적 내용 등 유해한 요소가 포함되어 있는지를 측정합니다. 서비스에 배포되는 LLM 애플리케이션은 사용자에게 유해한 내용을 전달해서는 안 되므로, 이 메트릭은 안전성 점검에 필수적입니다.

이 외에도 DeepEval은 **Answer Relevancy**(답변 관련성), **Faithfulness**(충실도), **Contextual Precision**(컨텍스트 정밀도), **Contextual Recall**(컨텍스트 재현율), **Bias**(편향), **Summarization**(요약 품질) 등 다양한 내장 메트릭을 제공합니다. 각 메트릭은 평가 대상과 기준이 다르므로, 애플리케이션의 성격에 맞는 메트릭을 조합하여 사용합니다.

내장 메트릭만으로 측정할 수 없는 품질 속성이 있을 수 있습니다. 예를 들어, 특정 도메인에서 사용하는 용어가 정확한지, 응답이 회사의 톤앤매너 가이드라인을 준수하는지 같은 기준은 범용 메트릭으로 포착하기 어렵습니다. 이런 경우를 위해 DeepEval은 **커스텀 메트릭**을 정의하는 기능을 제공합니다. 개발자가 평가 로직을 직접 작성하여 DeepEval의 메트릭 인터페이스에 맞추면, 내장 메트릭과 동일한 방식으로 테스트에 사용할 수 있습니다. 커스텀 메트릭을 만드는 기본 구조는 다음과 같습니다.

```python
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

class DomainTermAccuracyMetric(BaseMetric):
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        # test_case.actual_output에서 도메인 용어 정확도를 계산하는 로직
        score = self._calculate_term_accuracy(
            test_case.actual_output,
            test_case.expected_output
        )
        self.score = score
        self.success = score >= self.threshold
        return score

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self):
        return "Domain Term Accuracy"
```

이 코드에서 `BaseMetric`은 DeepEval이 제공하는 메트릭의 기본 클래스입니다. 이 클래스를 상속받아 `measure` 메서드에 평가 로직을 구현합니다. `measure` 메서드는 `LLMTestCase` 객체를 받아, 그 안에 담긴 `actual_output`(모델의 실제 출력)과 필요에 따라 `expected_output`(기대 출력), `context`(참조 문서) 등을 이용하여 점수를 계산합니다. `threshold`는 통과 기준 점수입니다. 이렇게 정의한 커스텀 메트릭은 내장 메트릭과 동일하게 테스트에 투입할 수 있습니다.

DeepEval에서 평가를 실행하려면 **테스트 케이스**와 **데이터셋**을 구성해야 합니다. 테스트 케이스는 한 건의 평가 단위입니다. 하나의 테스트 케이스에는 모델에 전달한 입력(input), 모델이 생성한 출력(actual_output), 그리고 평가에 필요한 부가 정보가 포함됩니다. 부가 정보에는 기대 출력(expected_output), 참조 컨텍스트(context), 검색된 문서(retrieval_context) 등이 있으며, 어떤 메트릭을 사용하느냐에 따라 필요한 필드가 달라집니다. 예를 들어 Hallucination 메트릭은 context가 필요하고, GEval은 평가 기준에 따라 expected_output이 필요할 수 있습니다.

테스트 케이스를 코드로 작성하면 다음과 같습니다.

```python
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input="대한민국의 수도는 어디인가요?",
    actual_output="대한민국의 수도는 서울입니다.",
    expected_output="서울",
    context=["대한민국의 수도는 서울특별시이다."]
)
```

`input`은 모델에 전달한 질문이고, `actual_output`은 모델이 실제로 생성한 답변입니다. `expected_output`은 정답 또는 기대하는 답변의 핵심 내용이며, `context`는 모델이 참조할 수 있도록 제공된 문서 목록입니다. 이 테스트 케이스 한 건에 여러 메트릭을 동시에 적용할 수 있습니다.

여러 테스트 케이스를 묶으면 **데이터셋**이 됩니다. 데이터셋은 평가의 규모를 키우기 위한 단위입니다. 실무에서는 수십에서 수백 건의 테스트 케이스를 데이터셋으로 구성하여, 모델의 품질을 통계적으로 파악합니다. 하나의 질문에 대해 잘 답한다고 해서 전체 품질이 좋다고 판단할 수 없으므로, 다양한 시나리오를 포함하는 데이터셋을 구축하는 것이 중요합니다.

```python
from deepeval.dataset import EvaluationDataset

dataset = EvaluationDataset(test_cases=[
    LLMTestCase(
        input="Python에서 리스트와 튜플의 차이는?",
        actual_output="리스트는 가변이고 튜플은 불변입니다.",
        expected_output="리스트는 수정 가능하고, 튜플은 수정 불가능하다."
    ),
    LLMTestCase(
        input="HTTP 상태 코드 404는 무엇을 의미하나요?",
        actual_output="404는 요청한 리소스를 찾을 수 없다는 뜻입니다.",
        expected_output="Not Found"
    ),
])
```

이 데이터셋을 평가에 투입하면, 모든 테스트 케이스에 대해 지정한 메트릭이 일괄 실행되고, 각 케이스별 점수와 전체 평균 점수가 산출됩니다.

테스트 케이스와 메트릭을 조합하여 실제 평가를 실행하는 방법은 두 가지입니다. 첫 번째는 pytest 기반의 방법입니다.

```python
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import HallucinationMetric

def test_hallucination():
    test_case = LLMTestCase(
        input="양자 컴퓨팅이란 무엇인가요?",
        actual_output="양자 컴퓨팅은 큐비트를 사용하여 연산을 수행하는 방식입니다.",
        context=["양자 컴퓨팅은 양자역학 원리를 이용한 연산 방식으로, 큐비트를 기본 단위로 사용한다."]
    )
    metric = HallucinationMetric(threshold=0.7)
    assert_test(test_case, [metric])
```

이 코드에서 `assert_test`는 DeepEval이 제공하는 함수로, 테스트 케이스에 메트릭을 적용하여 통과 여부를 판정합니다. 이 파일을 `pytest`로 실행하면 일반적인 Python 테스트처럼 결과가 출력됩니다. 메트릭 점수가 threshold 이상이면 테스트가 통과하고, 미만이면 실패합니다.

두 번째는 `evaluate` 함수를 사용하는 방법입니다. 데이터셋 전체를 한 번에 평가할 때 유용합니다.

```python
from deepeval import evaluate

results = evaluate(dataset, [HallucinationMetric(threshold=0.7)])
```

이 방식은 데이터셋에 포함된 모든 테스트 케이스에 대해 지정한 메트릭을 실행하고, 결과를 종합하여 반환합니다.

DeepEval의 큰 장점 중 하나는 **CI/CD 파이프라인에 통합**할 수 있다는 점입니다. CI/CD(Continuous Integration / Continuous Deployment)란 코드 변경을 자동으로 빌드, 테스트, 배포하는 자동화 파이프라인을 뜻합니다. 소프트웨어 개발에서는 코드를 변경할 때마다 자동 테스트를 실행하여, 변경이 기존 기능을 깨뜨리지 않았는지 확인합니다. DeepEval은 pytest와 통합되므로, 기존 CI/CD 파이프라인에 LLM 평가 테스트를 추가할 수 있습니다.

구체적인 흐름은 다음과 같습니다.

```
CI/CD 파이프라인에서의 DeepEval 평가 흐름

개발자가 프롬프트 또는 코드를 변경
        |
        v
Git에 커밋 / Pull Request 생성
        |
        v
CI 서버가 자동으로 테스트 실행
        |
        v
pytest가 DeepEval 테스트를 포함하여 전체 테스트 실행
        |
        v
+-------------------+     +--------------------+
| 일반 단위 테스트  |     | DeepEval 평가 테스트|
| (함수, API 검증)  |     | (LLM 출력 품질)    |
+-------------------+     +--------------------+
        |                          |
        v                          v
모든 테스트 통과 ----------> 배포 승인
        |
일부 테스트 실패 ----------> 배포 차단, 개발자에게 알림
```

이 흐름을 따르면, 프롬프트를 수정하거나 모델을 교체할 때 LLM 출력 품질이 기준 이하로 떨어지는 것을 자동으로 감지할 수 있습니다. 수동으로 응답을 확인하지 않아도, 품질 저하가 프로덕션에 반영되기 전에 차단됩니다.

GitHub Actions에서 DeepEval 테스트를 실행하는 워크플로우 파일 예시는 다음과 같습니다.

```yaml
name: LLM Evaluation
on: [push, pull_request]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install deepeval pytest
      - run: pytest tests/test_llm_eval.py --tb=short
```

`tests/test_llm_eval.py` 파일에 앞서 작성한 DeepEval 테스트 코드를 넣어 두면, 코드를 Push하거나 Pull Request를 생성할 때마다 자동으로 LLM 평가가 실행됩니다.

마지막으로 8.1.2에서 다룬 RAGAS와 DeepEval을 비교해 보겠습니다. 두 프레임워크는 모두 LLM 애플리케이션의 품질을 자동으로 평가한다는 공통점이 있지만, 설계 철학과 적용 범위에 차이가 있습니다.

RAGAS는 RAG 파이프라인 평가에 특화되어 있습니다. Faithfulness, Answer Relevance, Context Precision, Context Recall 등 RAG의 검색 단계와 생성 단계를 분리하여 각각의 품질을 측정하는 지표를 중심으로 설계되었습니다. RAG 파이프라인에서 "검색이 문제인지, 생성이 문제인지"를 진단하는 데 강점이 있습니다.

DeepEval은 범용 LLM 평가 프레임워크입니다. RAG뿐 아니라 챗봇, 요약, 분류, 코드 생성 등 LLM이 활용되는 모든 형태의 애플리케이션을 평가할 수 있습니다. GEval처럼 평가 기준을 자연어로 정의하는 유연한 메트릭, Toxicity나 Bias 같은 안전성 메트릭, 그리고 커스텀 메트릭 기능을 통해 다양한 품질 속성을 측정합니다. pytest 통합을 통한 CI/CD 연동도 DeepEval의 차별점입니다.

두 프레임워크의 주요 차이를 정리하면 다음과 같습니다.

```
RAGAS vs DeepEval 비교

항목              | RAGAS                    | DeepEval
------------------+--------------------------+--------------------------
주요 대상         | RAG 파이프라인           | 범용 LLM 애플리케이션
핵심 메트릭       | Faithfulness,            | GEval, Hallucination,
                  | Answer Relevance,        | Toxicity, Bias,
                  | Context Precision/Recall | Answer Relevancy 등
커스텀 메트릭     | 제한적                   | BaseMetric 상속으로 자유롭게 정의
테스트 프레임워크 | 자체 evaluate 함수       | pytest 통합
CI/CD 연동        | 별도 스크립트 필요       | pytest 기반으로 자연스러운 통합
평가 방식         | LLM-as-Judge 중심        | LLM-as-Judge + 규칙 기반 혼합
```

두 프레임워크는 배타적인 관계가 아닙니다. RAG 파이프라인을 운영한다면 RAGAS로 검색-생성 각 단계의 품질을 세밀하게 진단하고, DeepEval로 환각, 유해성, 도메인 특화 기준 등 보다 넓은 범위의 품질을 측정하는 방식으로 병행할 수 있습니다.

정리하면, DeepEval은 LLM 애플리케이션의 출력 품질을 pytest 기반으로 자동 검증하는 프레임워크입니다. GEval, Hallucination, Toxicity 등 다양한 내장 메트릭을 제공하고, BaseMetric을 상속하여 커스텀 메트릭을 정의할 수 있습니다. 테스트 케이스와 데이터셋으로 평가 단위를 구성하며, pytest 통합을 통해 CI/CD 파이프라인에 LLM 평가를 자연스럽게 포함시킬 수 있습니다. RAGAS가 RAG에 특화된 프레임워크라면, DeepEval은 LLM 애플리케이션 전반을 아우르는 범용 평가 도구입니다.

다음 단원인 8.2.1에서는 할루시네이션 탐지와 완화 전략을 다룹니다.

이 단원을 마치면 DeepEval을 활용하여 LLM 애플리케이션의 자동 평가 파이프라인을 구축할 수 있습니다.

<!-- INCOMPLETE: DeepEval 프레임워크 개요, 내장 메트릭 (GEval, Hallucination, Toxicity 등), 커스텀 메트릭 정의, 테스트 케이스와 데이터셋 구성, CI/CD 통합, RAGAS vs DeepEval 비교 -->
