# 5.2.3 CrewAI와 MCP

세 번째 프레임워크는 **CrewAI**입니다. LangGraph가 그래프, AutoGen이 대화에 무게를 둔다면, CrewAI는 **역할 기반 협력**에 중점을 둡니다. 각 에이전트가 분명한 직무·목표·페르소나를 가지고 팀(crew)으로 묶여 작업을 처리합니다. 이 단원에서는 CrewAI의 핵심 추상과 MCP 결합 방식을 정리합니다.

CrewAI의 모델은 세 가지 추상으로 구성됩니다.

```
추상            의미
Agent           역할·목표·배경 이야기를 가진 에이전트
Task            구체적인 작업 지시, 기대 출력
Crew            여러 Agent와 Task의 묶음, 실행 프로세스
```

이 모델이 인상적인 이유는 자연어 단위에서 협력을 설계할 수 있다는 점입니다. 개발자가 그래프 노드나 대화 흐름을 직접 짜기보다, "이 사람은 데이터 분석가이고 이 작업을 합니다" 같은 서술로 시작합니다.

설치와 MCP 어댑터는 다음과 같습니다.

```
pip install crewai crewai-tools
```

`crewai-tools`에는 `MCPServerAdapter`가 포함되어, MCP 서버를 CrewAI 도구로 변환합니다.

```python
from crewai import Agent, Task, Crew, Process
from crewai_tools import MCPServerAdapter
from mcp.client.stdio import StdioServerParameters

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/data"],
)

with MCPServerAdapter(server_params) as mcp_tools:
    researcher = Agent(
        role="Senior Research Analyst",
        goal="Find accurate, relevant information about {topic}.",
        backstory="You are a meticulous analyst with 10 years of experience.",
        tools=mcp_tools,
        verbose=True,
    )

    writer = Agent(
        role="Technical Writer",
        goal="Write clear reports from research notes.",
        backstory="You are a senior writer who clarifies complex ideas.",
    )

    research_task = Task(
        description="Research the topic: {topic}",
        expected_output="A bulleted list of key findings.",
        agent=researcher,
    )

    write_task = Task(
        description="Write a 500-word report based on research findings.",
        expected_output="A polished report in markdown.",
        agent=writer,
        context=[research_task],
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        process=Process.sequential,
    )

    result = crew.kickoff(inputs={"topic": "MCP protocol evolution"})
```

이 코드의 흐름을 따라가 봅니다. researcher는 MCP 도구를 가지고 있고, writer는 도구가 없습니다. 두 Task가 순서대로 실행되며, 두 번째 Task의 `context=[research_task]`가 첫 Task의 결과를 두 번째 Task의 입력으로 흘려보냅니다.

**Role, goal, backstory**의 결정은 단순한 장식이 아닙니다. CrewAI는 이 세 필드를 시스템 프롬프트에 직접 끼워 넣습니다. 따라서 좋은 role·goal·backstory는 좋은 시스템 프롬프트와 같습니다. 다음 팁이 도움이 됩니다.

```
필드           좋은 패턴
role           "Senior Data Scientist", "Technical Writer" (직무 + 시니어리티)
goal           구체적이고 측정 가능 ("X에 대한 5개의 핵심 사실 찾기")
backstory      에이전트의 전문성·접근 방식을 한두 문장으로
```

다음은 **Process 모드**입니다. Crew는 Task들을 어떤 순서로 실행할지를 process로 결정합니다.

```
모드                       의미
Process.sequential         Task 순서대로 실행 (가장 기본)
Process.hierarchical       Manager 에이전트가 Task 분배·검토
Process.consensual         (실험적) 모든 에이전트의 합의
```

`hierarchical` 모드는 5.1.3에서 다룬 supervisor 패턴을 직접 표현합니다. Crew는 별도의 manager LLM이 다음에 어떤 에이전트를 호출할지, 결과를 받아들일지를 결정합니다.

```python
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, write_task, review_task],
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4o"),
)
```

manager는 Task를 직접 정의하지 않고, 그때그때 적절한 에이전트에게 위임합니다. 작업이 비정형이거나 단계가 미리 정해지지 않은 경우에 잘 맞습니다.

다음은 **여러 MCP 서버 결합**입니다. 한 Crew가 여러 MCP 서버의 도구를 함께 사용하려면, 어댑터를 여러 개 만들거나 게이트웨이를 앞에 둡니다.

```python
fs_params = StdioServerParameters(command="npx", args=["...filesystem", "/data"])
wiki_params = StdioServerParameters(command="npx", args=["...wiki"])

with MCPServerAdapter(fs_params) as fs_tools, \
     MCPServerAdapter(wiki_params) as wiki_tools:

    all_tools = list(fs_tools) + list(wiki_tools)
    researcher = Agent(role=..., tools=all_tools)
```

여러 컨텍스트 매니저를 중첩하는 패턴은 자원 정리에 안전하지만 코드가 길어집니다. 서버 수가 많아지면 게이트웨이를 앞에 두고 한 어댑터로 다 다루는 편이 깔끔합니다.

다음은 **Crew 단위 메모리**입니다. CrewAI는 단기·장기 메모리를 내장으로 제공합니다.

```python
from crewai.memory import LongTermMemory, ShortTermMemory

crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,                       # 단기 메모리 활성화
    embedder={"provider": "openai"},   # 임베딩 모델
    long_term_memory=LongTermMemory(),
)
```

단기 메모리는 현재 실행 안에서 에이전트들이 공유하는 컨텍스트이고, 장기 메모리는 여러 실행에 걸쳐 보존되는 지식 베이스입니다. 임베딩 기반 검색으로 관련 항목만 가져옵니다. MCP의 Resources 프리미티브와 결합하면 외부 자원을 메모리로 끌어올 수 있습니다.

다음은 **CrewAI의 강점과 한계**입니다.

```
강점                                          한계
역할 중심의 직관적 설계                         흐름 제어가 LangGraph보다 거침
빠른 프로토타이핑                              세밀한 그래프 제어 어려움
template 기반 협력의 자연스러움                흐름 비결정성
사용자 친화적 문서                              엔터프라이즈 기능은 별도 플랫폼
```

CrewAI는 작은 팀이 빠르게 멀티 에이전트 시스템을 만들 때 매력적입니다. 코드 양이 적고 의도가 분명히 보입니다. 반면 매우 복잡한 흐름 제어가 필요한 시스템에는 LangGraph가 더 어울립니다.

다음은 **MCP와의 결합에서 주의할 점**입니다.

```
주의점                                                완화
verbose=True 로그가 stdout에 섞임                       조용한 모드로 운영
hierarchical 모드의 무한 위임                            max_iter 등 한도
긴 backstory가 컨텍스트를 빠르게 채움                   필요한 만큼만 작성
도구 description 변조 위험                              게이트웨이 사전 검사
LLM 호출 비용이 빠르게 누적                              모델 라우팅 + 캐싱(5.3.2)
```

verbose 로그는 디버깅에 편하지만, 운영 환경에서는 별도 logger로 보내야 stdio MCP 메시지와 섞이지 않습니다. 1.3.3에서 강조한 것과 같은 원칙입니다.

마지막으로, 세 프레임워크의 특징을 한 표로 정리합니다.

```
                  LangGraph              AutoGen                CrewAI
모델 기반          그래프                  대화                   역할
강점              결정적 흐름             자유로운 협력          빠른 프로토타입
적합 시나리오     자동화·파이프라인       연구·브레인스토밍      보고서·콘텐츠
MCP 어댑터         langchain-mcp-adapters McpWorkbench           MCPServerAdapter
체크포인트        강력                    중간                   단순(메모리)
관측 통합         LangSmith·OTel         이벤트 스트림           기본 로그
학습 곡선         중간                    낮음~중간              낮음
```

이 비교는 절대적 우열이 아닙니다. 같은 시스템 안에서 세 프레임워크를 함께 쓰는 패턴도 흔합니다. 예를 들어 supervisor는 LangGraph로 짜고, 한 subgraph는 CrewAI Crew로, 다른 subgraph는 AutoGen GroupChat으로 구성하는 식입니다. MCP가 도구 통합의 표준이라는 점이 이 혼합을 가능하게 합니다. 어떤 프레임워크를 쓰든 같은 MCP 서버를 그대로 노출할 수 있습니다.

정리하면, CrewAI는 role·goal·backstory를 가진 Agent와 Task의 명시적 묶음으로 멀티 에이전트 협력을 표현하며, MCPServerAdapter가 MCP 도구를 그 안에 자연스럽게 합류시킵니다. Crew·Process·Memory가 핵심 부품이고, 빠른 프로토타이핑과 명확한 역할 분리가 가장 큰 강점입니다.

다음 섹션에서는 이 세 프레임워크를 운영 단계로 가져가기 위한 디버깅·비용·평가 패턴을 살펴봅니다.
