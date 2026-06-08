# 3.3.2 LangSmith 평가·실험 통합

앞 단원에서 LangSmith가 trace·Run·메타데이터·태그라는 어휘로 production의 한 호출 한 호출을 트리 형태로 쌓아 두는 모습을 살펴봤습니다. trace가 잘 쌓이는 것만으로는 회귀를 잡을 수 없습니다. 같은 입력에 대해 어제의 시스템과 오늘의 시스템이 다르게 답하는지를 누군가가 비교해 주어야 하고, 그 비교가 코드 변경 때마다 자동으로 돌아 주어야 합니다. 이번 단원은 LangSmith가 trace 위에 데이터셋·실험·평가라는 세 층을 어떻게 묶어 두는지, 그리고 그 묶음이 production trace와 다시 어떻게 연결되는지를 다룹니다.

가장 아래 층에 놓이는 개념이 **Dataset**입니다. LangSmith의 Dataset은 입력과 기대 출력이 짝지어진 example의 모음입니다. 이름과 설명이 붙고, 그 안에 example이 줄지어 있으며, 각 example은 inputs 딕셔너리와 outputs 딕셔너리, 그리고 자유 메타데이터로 구성됩니다. 골든 데이터셋도 여기에 들어가고, 단계별 trajectory 평가용 데이터셋도 여기에 들어갑니다. UI 화면에서 example을 직접 추가할 수 있고, SDK에서도 한 줄 호출로 만들 수 있습니다.

```python
from langsmith import Client

client = Client()
ds = client.create_dataset(
    dataset_name="refund-qa-golden",
    description="환불 문의 골든 데이터셋 v1",
)
client.create_examples(
    dataset_id=ds.id,
    inputs=[{"question": "주문 취소 후 며칠 안에 환불되나요?"}],
    outputs=[{"answer": "영업일 기준 3~5일 안에 환불됩니다."}],
)
```

Dataset에는 버전이 붙습니다. example을 추가하거나 수정하면 Dataset의 새 버전이 만들어지고, 이후 평가에서는 어느 버전을 사용했는지가 함께 기록됩니다. 골든 데이터셋이 시간에 따라 진화하는 흐름을 LangSmith가 그대로 받아 둔 셈이며, '이 회귀가 데이터셋 변경 때문인지 시스템 변경 때문인지'를 따질 때 이 버전 정보가 결정적인 단서가 됩니다.

Dataset을 두는 이유는 그 위에서 **실험을 실행하고 비교**하기 위해서입니다. LangSmith에서는 한 시스템을 한 Dataset에 흘려 그 결과를 모은 묶음을 experiment라고 부릅니다. evaluate 함수에 평가 대상 함수와 Dataset 이름, 그리고 평가 방법을 넘기면 LangSmith가 Dataset의 모든 example에 그 함수를 한 번씩 흘리고, 결과를 experiment 한 건으로 보관합니다.

```python
from langsmith import evaluate
from langsmith.evaluation import LangChainStringEvaluator

results = evaluate(
    lambda inputs: my_agent(inputs["question"]),
    data="refund-qa-golden",
    evaluators=[LangChainStringEvaluator("qa")],
    experiment_prefix="agent-v0904",
    metadata={"git_sha": "a1b2c3d", "model": "gpt-4o-mini"},
)
```

experiment_prefix와 metadata는 나중에 비교를 위해 붙여 두는 꼬리표입니다. 같은 Dataset 위에서 prefix만 바꾼 experiment를 여러 개 만들면 LangSmith UI가 표 형태로 두 experiment를 나란히 놓고, 각 example마다 어느 쪽이 더 좋은 점수를 받았는지를 색으로 구분해 줍니다. 모델 버전을 바꿨을 때, 프롬프트를 다듬었을 때, 도구 정의를 갈았을 때 일어나는 회귀를 한 화면에서 example 단위로 들여다볼 수 있다는 점이 이 비교의 핵심입니다.

채점은 evaluator가 맡습니다. LangSmith에는 정확도·정답 일치·간단한 LLM-as-judge 등 자주 쓰이는 evaluator가 미리 준비되어 있고, 그 위에 **Custom evaluator**를 등록할 수 있습니다. Custom evaluator는 한 example의 입력과 시스템 출력, 그리고 정답을 받아 점수와 코멘트를 돌려주는 함수입니다.

```python
def grounding_evaluator(run, example):
    answer = run.outputs["answer"]
    docs = run.outputs.get("docs", [])
    grounded = any(token in " ".join(docs) for token in answer.split())
    return {
        "key": "grounded",
        "score": 1.0 if grounded else 0.0,
        "comment": "근거 문서에 답변의 단어가 등장하지 않습니다." if not grounded else "",
    }
```

이 함수를 evaluators 리스트에 넣어 두면 모든 example의 trajectory가 채점에 들어가고, 결과는 experiment의 한 컬럼으로 쌓입니다. trajectory 평가에서 다룬 도구 선택률·인자 전달률·근거-결론 일치도 같은 자체 메트릭은 거의 모두 이 Custom evaluator 자리에 들어갑니다. UI에서는 이렇게 등록한 메트릭별로 분포가 그려지고, 같은 Dataset의 두 experiment를 메트릭별로 따로 비교할 수 있습니다.

여기까지가 offline 평가의 모양이라면, LangSmith가 실제로 강한 지점은 **production trace를 데이터셋으로 흡수**하는 통로입니다. trace 화면에서 한 trace를 골라 'Add to Dataset' 버튼을 누르면 그 trace의 입력과 출력이 한 example로 떨어집니다. 정답을 비워 두면 라벨링 큐로 들어가고, 사람이 정답을 채워 넣으면 그대로 골든 데이터셋의 새 example이 됩니다. 이 흐름은 reactive 평가의 자연스러운 지지대입니다. production에서 누군가가 이상한 응답을 발견하면 그 trace를 곧장 Dataset에 흡수하고, 다음 코드 변경 때 그 example이 회귀 테스트의 일부로 자동 실행됩니다. 'production에서 잡힌 실패가 다시는 같은 이유로 통과하지 못하도록' 막는 사이클이 메뉴 클릭 한두 번으로 닫힙니다.

흡수의 자동화도 가능합니다. SDK에서 client.create_example을 직접 호출해 trace의 inputs·outputs을 example로 떨어뜨리면 새벽 배치로 'thumbs-down이 붙은 trace 모두를 데이터셋에 추가'하는 식의 운영도 짤 수 있습니다. 라벨이 없는 새 example은 평가에서 빠지고, 라벨이 채워진 시점부터 회귀 테스트에 합류합니다.

평가와 실험은 한 사람만 쓰는 도구가 아닙니다. 그래서 LangSmith는 Workspace·Project·Permission이라는 세 층의 **팀 협업과 권한 모델**을 둡니다. Workspace는 한 조직 단위의 가장 바깥 봉투이고, 그 안에 여러 Project가 있으며, Project는 한 시스템 또는 한 환경 단위의 trace·Dataset·experiment를 담는 그릇입니다. 사용자별로 admin·developer·viewer 같은 역할이 부여되고, 역할마다 trace를 볼 수 있는지·Dataset을 수정할 수 있는지·API 키를 발급할 수 있는지가 갈립니다. 다음과 같은 구조가 흔합니다.

```
Workspace: bank-co
  +- Project: refund-agent-prod    (운영팀이 viewer로 trace만 조회)
  +- Project: refund-agent-staging (개발팀이 developer로 실험 실행)
  +- Dataset:  refund-qa-golden    (PM이 라벨러 권한으로 example 추가)
```

이 구조 덕분에 production trace에는 민감 정보가 섞여 있어도 viewer 권한 사용자는 보고 싶은 단면만 보게 묶을 수 있고, 개발자는 staging Project에서 자유롭게 실험을 돌리되 prod Project의 trace를 함부로 수정할 수 없게 분리할 수 있습니다. self-hosted 옵션을 쓰는 환경에서는 이 권한 모델이 사내 SSO와 묶여 들어가 감사 로그까지 남게 됩니다.

여기까지의 흐름을 한 그림으로 묶으면 다음과 같습니다.

```
 [ Production trace ] --(Add to Dataset)--> [ Dataset v_n ]
                                                |
                                                v
       [ Code change ]  ----(evaluate)--->  [ Experiment A ]
                        \\
                         ----(evaluate)--->  [ Experiment B ]
                                                |
                                                v
                                       [ UI 비교 + Custom evaluator 점수 ]
```

production에서 발견한 실패가 Dataset으로 흡수되고, 코드 변경마다 evaluate가 그 Dataset 위에서 새 experiment를 만들며, 두 experiment가 UI에서 example 단위로 비교되고, 비교 결과가 다시 다음 변경의 우선순위를 정합니다. 이 닫힌 사이클이 LangSmith가 단순한 trace 뷰어를 넘어 회귀 테스트 자동화의 골격이 되는 까닭입니다.

정리하면, LangSmith의 평가·실험 통합은 Dataset·experiment·Custom evaluator라는 세 층을 trace 위에 올린 다음, production trace를 다시 Dataset으로 흡수하는 통로와 Workspace·Project·역할 기반 권한 모델로 이 구조를 팀 단위로 운영 가능하게 묶어 두는 흐름을 따릅니다. trace는 무엇이 일어났는지를 보여 주고, Dataset은 무엇이 일어나야 하는지를 못 박으며, experiment와 evaluator는 두 그림이 어긋난 자리를 숫자로 짚어 주고, 권한 모델은 이 모든 것을 여러 사람이 함께 쓰면서도 망가지지 않게 받쳐 줍니다.

다음 단원인 3.4.1에서는 LangSmith와 같은 자리에 자주 비교되는 Langfuse를 살펴보겠습니다. 특히 Langfuse가 강조하는 자체 호스팅과 데이터 주권의 측면에서, 한국이나 EU처럼 데이터 거주성 요구가 강한 환경에서 의사결정이 어떻게 갈리는지를 다루겠습니다.

이 단원을 마치면 LangSmith의 Dataset 관리, 실험 실행과 비교, Custom evaluator 등록, production trace를 Dataset으로 흡수하는 통로, 그리고 Workspace·Project·권한 모델 기반의 팀 협업 구조를 정의하고 이들이 회귀 테스트 자동화에 어떻게 결합되는지를 설명할 수 있습니다.
