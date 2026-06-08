# 3.3.1 LangSmith의 trace 모델

앞 단원에서는 trace·span·metric이라는 일반적인 데이터 모델을 살펴봤습니다. trace는 한 번의 요청을 처음부터 끝까지 묶는 큰 봉투이고, span은 그 안에서 일어난 개별 작업의 시간 구간이며, metric은 token·latency·cost처럼 trace와 span에 부착되는 숫자 신호였습니다. 이 단원은 이 일반 모델 위에 LangSmith라는 도구가 자체적으로 어떤 표현을 쌓아 올리는지를 다룹니다. 같은 trace라는 단어를 쓰지만, LangSmith는 그 단어를 자기 화면과 자기 데이터 구조에 맞게 다듬어 두고 있어서, 일반 모델을 알아도 LangSmith를 처음 열면 낯선 용어가 한꺼번에 쏟아집니다.

가장 먼저 짚을 용어는 **Run**입니다. LangSmith에서는 trace라는 말 옆에 Run이라는 말이 붙어 다닙니다. 한 번의 요청 전체를 묶는 가장 바깥 단위가 trace이고, 그 trace 안에서 개별로 실행된 한 조각 한 조각이 Run입니다. 일반 분산 추적의 span 자리에 들어가는 개념이 LangSmith에서는 Run이라고 보면 거의 맞습니다. 단, LangSmith의 Run은 단순히 시간 구간만 담지 않고 입력 메시지·출력 메시지·사용한 모델·token 수·비용까지 함께 담는다는 차이가 있습니다. trace 한 건을 열면 트리 형태로 Run이 줄지어 나오고, 각 Run을 클릭하면 그 단계에서 LLM에게 무엇을 주고 무엇을 받았는지가 그대로 보입니다.

Run에는 종류가 있습니다. LLM 호출은 LLM Run, 도구 호출은 Tool Run, 여러 단계를 묶은 체인은 Chain Run, 검색은 Retriever Run으로 분류됩니다. 이 분류 자체가 실패 모드별 필터링을 가능하게 합니다. 예를 들어 도구 선택 오류를 들여다보고 싶을 때 Tool Run만 추려 보면, 어떤 도구가 어떤 입력으로 불렸는지가 한 화면에 모입니다. 일반 OpenTelemetry trace에서는 span의 종류를 직접 attribute로 다 다뤄야 했지만, LangSmith는 LLM·Tool·Chain·Retriever라는 자주 쓰이는 분류를 미리 굳혀 둔 셈입니다.

이 Run 트리를 사람이 손으로 채울 수도 있지만, LangSmith가 본격적으로 빛을 보는 지점은 **자동 인스트루먼트**입니다. 인스트루먼트라는 말은 측정용 부품을 코드 곳곳에 박아 둔다는 뜻인데, LangSmith는 LangChain과 LangGraph로 짠 코드라면 이 부품을 거의 자동으로 박아 줍니다. LangChain의 체인을 호출하기만 해도 그 호출이 어느 모델을 어떤 프롬프트로 부르고 어떤 도구를 어느 인자로 부르는지가 Run 트리에 자동으로 쌓입니다. LangGraph로 만든 그래프 기반 에이전트에서도 노드 하나가 실행될 때마다 자식 Run이 생기고, 그래프의 분기와 합류가 트리 구조에 그대로 반영됩니다. 환경변수에 LangSmith API 키와 프로젝트 이름을 한 번 적어 두면 별도의 코드 수정 없이 추적이 시작된다는 점이 이 자동화의 가장 직관적인 모습입니다.

LangChain·LangGraph 바깥의 코드, 예컨대 직접 SDK로 모델을 부르거나 자체 도구를 짜는 경우에는 데코레이터 방식의 명시 인스트루먼트를 씁니다. 다음과 같은 형태입니다.

```python
import os
from langsmith import traceable

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "ls_..."
os.environ["LANGSMITH_PROJECT"] = "agent-eval-prod"

@traceable(run_type="tool", name="search_docs")
def search_docs(query: str) -> list[str]:
    return retriever.invoke(query)

@traceable(run_type="chain", name="answer_query")
def answer_query(question: str) -> str:
    docs = search_docs(question)
    return llm.invoke(format_prompt(question, docs))
```

@traceable이 붙은 함수가 호출되면 LangSmith가 그 함수의 진입과 종료를 Run 한 건으로 기록하고, 그 안에서 다시 @traceable이 붙은 함수가 불리면 자식 Run으로 트리에 매답니다. run_type 인자로 LLM·Tool·Chain·Retriever 중 어디에 속하는 Run인지를 LangSmith에 알려 줍니다.

기록된 Run에는 **메타데이터와 태그**가 붙습니다. 메타데이터는 키·값 쌍의 딕셔너리이고 태그는 문자열의 리스트입니다. 사용자 ID, 세션 ID, A/B 테스트의 분기 이름, 모델 버전, 실험 이름 같이 검색·필터에 쓰고 싶은 정보를 여기에 담아 둡니다. 메타데이터는 trace 안에서 특정 사용자만 추리는 식의 정밀 검색에, 태그는 'experiment-v3' 같이 굵직한 그룹 분류에 쓰입니다. 두 장치가 있어야 production trace 수십만 건 가운데 원하는 것을 빠르게 좁힐 수 있습니다.

여기까지가 trace를 쌓는 쪽 이야기라면, 들여다보는 쪽에는 **Replay**와 **fork**라는 도구가 놓여 있습니다. Replay는 이미 기록된 trace의 입력을 그대로 다시 모델에 흘려 결과를 새로 받아 보는 기능입니다. 같은 입력을 다른 모델이나 다른 프롬프트 버전에 흘렸을 때 결과가 어떻게 달라지는지를 같은 화면에서 비교할 수 있습니다. fork는 trace 트리의 어느 Run에서 갈래를 떼어 그 지점부터 새 경로로 다시 실행하는 방식입니다. 예를 들어 실패한 trace의 5번째 Run이 잘못된 도구 선택이라고 판단했다면, 4번째 Run까지의 상태를 그대로 두고 5번째에서 다른 도구를 호출하도록 갈래를 만들 수 있습니다. 이 두 기능 덕에 디버깅이 '로그 보고 추측해서 다시 실행'이 아니라 '문제 지점에서 곧장 갈래 치고 비교'로 바뀝니다.

Replay와 fork는 비결정성과 직접 맞물립니다. 같은 입력을 흘려도 결과가 매번 달라지는 환경에서는 한 번의 실패가 진짜 회귀인지 운인지 가리기 어려운데, Replay는 그 입력을 여러 번 다시 흘려 평균을 보게 해 주고, fork는 그 가운데 의심되는 단계만 분리해 비교 실험을 할 수 있게 해 줍니다.

마지막 축은 **Hosted vs self-hosted 옵션**입니다. LangSmith는 기본적으로 LangChain의 클라우드에서 호스팅되는 서비스이고, 가입 후 API 키만 받으면 인프라 부담 없이 trace를 저장하고 들여다볼 수 있습니다. Hosted 옵션은 도입이 빠르고 운영이 거의 필요 없다는 장점이 있는 반면, trace에 담기는 프롬프트와 응답이 외부 서버를 거친다는 점이 있습니다. 이 점이 한국의 금융권·공공기관처럼 데이터 거주성과 보안 정책이 까다로운 환경에서는 곧바로 의사결정 변수가 됩니다. 이런 환경을 위한 self-hosted 옵션은 사내 인프라에 LangSmith 인스턴스를 설치하고 trace 데이터를 자체 DB에 두는 방식입니다. 운영 부담은 늘지만 trace 한 건도 외부로 나가지 않게 묶어 둘 수 있습니다. 한국 기업이 LangSmith를 검토할 때 가장 먼저 가르는 질문이 결국 이 Hosted·self-hosted 선택이며, 이 결정이 비용·운영 인력·규제 대응 전략을 동시에 흔듭니다.

화면에서 보이는 모습을 한 번 그려 두면 다음과 같습니다.

```
[Trace] answer_query  | 12.4s | $0.018 | tokens 3,210
  +- [Chain Run] retrieve_and_answer  | 11.2s
  |    +- [Retriever Run] search_docs(query="환불 정책")  | 0.6s
  |    +- [LLM Run] gpt-4o-mini (system+context+user)     | 9.8s
  |          tags: [experiment-v3, prod]
  |          metadata: {user_id: 12931, session: a91, model_ver: 0903}
  +- [Tool Run] format_response                            | 0.4s
```

이 트리가 LangSmith 화면의 골격이고, 각 Run을 클릭하면 입력·출력·메타데이터·token·비용이 펼쳐집니다. 상위 trace 행에는 전체 latency와 누적 비용이 한 눈에 들어오고, 메타데이터와 태그를 이용한 필터로 production trace 가운데 원하는 단면을 잘라 볼 수 있습니다.

정리하면, LangSmith의 trace 모델은 일반 trace·span·metric 위에 Run·LangChain·LangGraph 자동 인스트루먼트·메타데이터·태그·Replay·fork·Hosted·self-hosted라는 자체 어휘를 얹은 구조입니다. trace가 한 번의 요청을 묶는 봉투라면, Run은 그 안에서 LLM·Tool·Chain·Retriever 중 무엇이었는지를 분류해 트리로 펼쳐 주는 단위이고, 자동 인스트루먼트는 LangChain·LangGraph 코드라면 별다른 수정 없이 이 트리를 채워 주며, Replay와 fork는 채워진 트리 위에서 비결정성을 다루는 디버깅 손잡이가 됩니다. Hosted·self-hosted 선택은 이 모든 구조의 데이터가 어디에 사는지를 결정하는 도입 의사결정의 첫 갈림길입니다.

다음 단원인 3.3.2에서는 이렇게 쌓인 trace 위에서 LangSmith가 데이터셋·실험·평가 워크플로를 어떻게 묶어 두는지, 그리고 production trace를 다시 데이터셋으로 흡수해 회귀 테스트를 자동화하는 흐름을 살펴보겠습니다.

이 단원을 마치면 LangSmith의 trace·Run 구조와 LangChain·LangGraph 자동 인스트루먼트, 메타데이터와 태그 활용, Replay·fork 기능, 그리고 Hosted·self-hosted 옵션의 차이를 정의하고 각각이 도입 의사결정에 어떻게 영향을 주는지를 설명할 수 있습니다.
