# 5.2.2 AutoGen과 MCP

LangGraph가 그래프 기반의 명시적 흐름을 강조한다면, **AutoGen**은 대화 기반의 협력에 무게를 두는 프레임워크입니다. 에이전트들이 메시지를 주고받으며 합의에 도달하는 모델을 자연스럽게 표현합니다. 이 단원에서는 Microsoft Research가 만든 AutoGen v0.4 아키텍처와 MCP의 결합을 살펴봅니다.

AutoGen은 두 메이저 버전이 있습니다. **v0.2**는 단일 패키지 안에서 모든 기능을 제공했고, 빠른 프로토타이핑에 강점이 있었습니다. **v0.4**는 모듈화·관측·이벤트 기반 아키텍처로 다시 설계되었으며, autogen-core·autogen-agentchat·autogen-ext 세 패키지로 분리되었습니다. MCP 통합은 주로 v0.4 이후의 흐름을 따릅니다.

```
패키지 분리

autogen-core         - 메시지 라우팅, runtime, 이벤트
autogen-agentchat    - 에이전트 추상화, 그룹 채팅 패턴
autogen-ext          - 모델·도구·메모리 확장(MCP 포함)
```

설치는 다음과 같습니다.

```
pip install "autogen-agentchat" "autogen-ext[openai,mcp]"
```

다음은 **단일 MCP 서버 연결**입니다. autogen-ext의 `McpWorkbench`가 MCP 도구를 AutoGen의 도구로 변환해 줍니다.

```python
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

server_params = StdioServerParams(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/data"],
)

async with McpWorkbench(server_params) as workbench:
    tools = await workbench.list_tools()
    agent = AssistantAgent(
        name="assistant",
        model_client=OpenAIChatCompletionClient(model="gpt-4o"),
        tools=tools,
    )
    response = await agent.run(task="List markdown files in /data and summarize.")
```

McpWorkbench는 LangGraph의 MultiServerMCPClient와 비슷한 역할이지만, 한 번에 하나의 서버를 다루는 것이 기본입니다. 여러 서버를 결합하려면 여러 workbench를 만들고 도구 목록을 합치거나, gateway를 앞에 두는 모델을 채택합니다(4.1.2 참조).

다음은 **GroupChat 패턴**입니다. AutoGen의 가장 특징적인 기능은 여러 에이전트가 한 대화방에서 서로 메시지를 주고받는 모델입니다.

```python
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination

researcher = AssistantAgent(name="researcher", model_client=client, tools=research_tools,
    system_message="You research and provide facts.")

analyst = AssistantAgent(name="analyst", model_client=client, tools=analysis_tools,
    system_message="You analyze facts and produce insights.")

writer = AssistantAgent(name="writer", model_client=client, system_message=
    "You write final reports from insights.")

team = RoundRobinGroupChat(
    [researcher, analyst, writer],
    termination_condition=MaxMessageTermination(20),
)

result = await team.run(task="Q3 매출 분석 보고서를 작성해.")
```

이 모델에서 각 에이전트는 자기 차례가 되면 응답하고, 메시지는 그룹의 모든 멤버가 볼 수 있습니다. RoundRobin 외에 SelectorGroupChat(LLM이 다음 발화자를 선택)이나 SwarmGroupChat(목표 지향 협력) 같은 패턴이 있습니다.

이 대화 모델의 가치는 자연스러운 협력 표현에 있습니다. 사람의 회의처럼 한 사람이 의견을 내면 다른 사람이 받아 의견을 추가하는 흐름이 직관적으로 표현됩니다. 단점은 흐름이 결정적이지 않다는 점입니다. 같은 입력에 다른 대화가 펼쳐질 수 있고, 길이가 예측 어려워집니다.

다음은 **종료 조건**입니다. 대화가 무한히 이어지지 않도록 명시적 종료가 필요합니다. AutoGen은 여러 종료 조건을 제공합니다.

```
종료 조건                                  의미
MaxMessageTermination(n)                  메시지 수 한도
TextMentionTermination("TERMINATE")        특정 텍스트 등장
TimeoutTermination(seconds)                시간 한도
ExternalTermination()                      외부 신호로 종료
AndTerminationCondition(...)               조합
```

권장 패턴은 메시지 수와 시간 한도를 함께 두는 것입니다. 한 가지가 빠지면 비정상 상황에서 시스템이 멈추지 않을 수 있습니다.

다음은 **MCP 도구 격리**입니다. GroupChat에서 모든 에이전트가 같은 도구를 가져야 하는 것은 아닙니다. 5.1.3에서 다룬 책임 분리에 맞춰, 에이전트별로 다른 도구 묶음을 부여하는 것이 자연스럽습니다.

```python
researcher = AssistantAgent(name="researcher", tools=[wiki_search, web_search])
analyst    = AssistantAgent(name="analyst",    tools=[stats_tool, viz_tool])
writer     = AssistantAgent(name="writer",     tools=[]) # 도구 없음, 글만
```

이 분리가 MCP 게이트웨이의 정책 엔진과 결합되면 더 강력합니다. 각 에이전트가 다른 토큰·다른 scope로 게이트웨이를 호출하도록 만들면, "writer가 갑자기 데이터베이스를 직접 호출"하는 식의 사고가 일어나지 않습니다.

다음은 **Conversation logger**입니다. AutoGen v0.4는 모든 메시지를 이벤트 스트림으로 노출합니다. 외부 관측 도구(LangSmith, LangFuse, OpenTelemetry)에 연결해 둘 수 있습니다.

```python
async for event in team.run_stream(task="..."):
    # 각 이벤트는 누가 누구에게 무엇을 말했는지의 정보
    print(event)
```

이 스트림이 디버깅과 회고에 큰 도움이 됩니다. 시스템이 잘못된 결론에 도달했을 때, 어느 에이전트의 어떤 발화에서 어긋났는지를 메시지 단위로 확인할 수 있습니다.

다음은 **사람 참여(human-in-the-loop)** 패턴입니다. AutoGen은 UserProxyAgent를 통해 사람을 대화의 한 참여자로 포함시킬 수 있습니다.

```python
user_proxy = UserProxyAgent(name="user", input_func=ask_user)
team = RoundRobinGroupChat([user_proxy, researcher, analyst, writer])
```

이 패턴은 중요한 결정 지점에 사람의 확인을 받는 시나리오에 어울립니다. 예를 들어 결제·외부 메일·코드 푸시 같은 결정적 호출 전에 사람이 마지막 검토를 한 번 합니다.

다음은 **AutoGen의 강점과 한계**입니다.

```
강점                                       한계
대화 기반의 자연스러운 협력 표현              흐름의 비결정성
GroupChat 패턴의 다양성                       메시지 폭주 위험
이벤트 스트림과 관측의 깔끔함                 그래프 기반 시각화는 LangGraph가 더 강함
UserProxyAgent의 매끄러운 통합                결정적 워크플로에는 과함
```

AutoGen은 자유로운 협력이 필요한 시나리오(연구, 브레인스토밍, 협상)에 잘 어울리고, 결정적 단계가 명확한 시나리오(데이터 파이프라인, 자동화)에는 LangGraph가 더 잘 맞을 수 있습니다.

다음은 **MCP와의 결합에서 주의할 점**입니다.

```
주의점                                                완화
McpWorkbench 컨텍스트 매니저 누락                       async with로 묶어 자원 정리
여러 에이전트가 같은 stdio 서버를 동시 호출              SSE/HTTP로 바꾸거나 워크벤치 분리
도구 결과의 isError가 모델에게 전달되지 않음             AutoGen v0.4의 tool_call 이벤트로 확인
도구 description의 prompt injection                     게이트웨이에서 사전 검사(4.2)
대화 컨텍스트 폭주                                       요약 메시지로 압축
```

특히 stdio 서버는 자식 프로세스이므로 여러 에이전트가 동시에 호출하면 직렬화되거나 자원이 부족해질 수 있습니다. 다중 에이전트 시나리오에서는 Streamable HTTP로 운영되는 MCP 서버나 게이트웨이가 더 자연스럽습니다.

마지막으로, **AutoGen v0.2에서 v0.4로의 이주**도 짧게 언급합니다. v0.2 코드는 단일 패키지에 모두 들어 있어 사용이 쉽지만, MCP 통합은 v0.4가 표준입니다. 새 프로젝트는 v0.4를 기본으로, 기존 v0.2 코드는 시간 여유에 맞춰 점진적으로 이주하는 것이 일반적입니다.

정리하면, AutoGen은 대화 기반 멀티 에이전트 협력의 표준 프레임워크이며, v0.4의 McpWorkbench가 MCP 도구를 자연스럽게 합류시킵니다. GroupChat 패턴, 종료 조건, 에이전트별 도구 격리, 이벤트 스트림 관측, human-in-the-loop이 핵심 부품입니다.

다음 단원인 5.2.3에서는 역할 기반 협력을 강조하는 CrewAI와 MCP의 결합을 살펴봅니다.
