# 5.2.1 LangGraph와 MCP

지금까지 살펴본 멀티 에이전트 패턴을 실제로 코드로 옮기려면 프레임워크의 도움이 필요합니다. 이 섹션에서는 세 가지 대표 프레임워크와 MCP의 결합을 살펴봅니다. 첫 번째 단원에서는 **LangGraph**를 다룹니다.

**LangGraph**는 LangChain 생태계가 만든 그래프 기반 에이전트 프레임워크입니다. 노드(node)와 엣지(edge)로 에이전트의 흐름을 표현하고, 상태(state)를 노드 사이에서 명시적으로 흘려보냅니다. 이 그래프 구조는 5.1.3에서 다룬 subgraph·supervisor 패턴을 매우 자연스럽게 표현합니다.

LangGraph가 MCP와 결합하는 방식은 단순합니다. **langchain-mcp-adapters** 패키지가 MCP 도구를 LangChain Tool로 변환해 줍니다. 한 번 변환된 도구는 LangGraph의 ToolNode 안에서 다른 LangChain 도구와 동일하게 사용됩니다.

```
pip install langgraph langchain-mcp-adapters
```

가장 단순한 형태는 단일 MCP 서버 연결입니다.

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

client = MultiServerMCPClient(
    {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"],
            "transport": "stdio",
        }
    }
)

async with client:
    tools = client.get_tools()
    agent = create_react_agent("anthropic:claude-sonnet-4-6", tools)
    result = await agent.ainvoke({
        "messages": [("user", "Summarize all .md files in /data")]
    })
```

여기서 핵심은 `MultiServerMCPClient`입니다. 이름이 시사하듯 **여러 MCP 서버**를 한 번에 등록할 수 있고, 각 서버의 도구를 모두 모아 단일 도구 목록으로 노출합니다. 4.1.2에서 다룬 Aggregator 패턴이 그대로 적용됩니다.

여러 서버를 결합한 예시는 다음과 같습니다.

```python
client = MultiServerMCPClient({
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"],
        "transport": "stdio",
    },
    "wiki": {
        "url": "https://mcp.example.com/wiki",
        "transport": "streamable_http",
        "headers": {"Authorization": "Bearer <token>"},
    },
    "github": {
        "url": "https://mcp.example.com/github",
        "transport": "streamable_http",
    },
})

async with client:
    tools = client.get_tools()  # 세 서버의 도구 모두 합쳐짐
```

이 한 객체가 stdio 서버와 두 개의 원격 Streamable HTTP 서버를 동시에 관리합니다. 도구 이름이 충돌하면 LangChain이 자동으로 prefix를 붙여 줍니다(예: `filesystem__read_file`).

다음은 **ToolNode와 그래프 통합**입니다. LangGraph의 그래프에서 도구 호출은 `ToolNode`라는 표준 노드가 처리합니다. MCP 도구도 이 노드 안에서 다른 도구와 같은 방식으로 사용됩니다.

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage

graph = StateGraph(state_schema=MyState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.add_edge("__start__", "agent")
graph.add_conditional_edges("agent", route_after_agent, {"tools": "tools", "end": END})
graph.add_edge("tools", "agent")
app = graph.compile()
```

이 그래프는 ReAct 패턴의 표준 골격입니다. 모델 노드가 응답을 만들고, 그 응답에 도구 호출 의도가 있으면 ToolNode로 가서 실행하고, 결과를 모델 노드로 돌려 보내는 순환입니다. 종료 조건은 모델이 더 이상 도구를 부르지 않을 때입니다.

다음은 **Subgraph 표현**입니다. LangGraph는 5.1.3에서 다룬 subgraph를 1급 객체로 제공합니다. 한 그래프를 다른 그래프의 노드로 끼워 넣을 수 있습니다.

```python
research_graph = build_research_graph()       # 조사 묶음
analysis_graph = build_analysis_graph()       # 분석 묶음
writing_graph = build_writing_graph()         # 작성 묶음

supervisor = StateGraph(ReportState)
supervisor.add_node("research", research_graph)
supervisor.add_node("analyze", analysis_graph)
supervisor.add_node("write", writing_graph)
supervisor.add_edge("__start__", "research")
supervisor.add_edge("research", "analyze")
supervisor.add_edge("analyze", "write")
supervisor.add_edge("write", END)
```

각 subgraph는 자기 안에서 MCP 도구를 가질 수 있고, supervisor는 그 도구를 직접 다루지 않습니다. 4.2.1의 정책 엔진과 결합하면 각 subgraph가 다른 토큰·다른 scope로 게이트웨이를 호출하도록 만들 수 있습니다.

다음은 **Streaming 결과 처리**입니다. LangGraph는 그래프 실행을 토큰 단위 또는 노드 단위로 스트리밍할 수 있습니다. MCP 도구가 Streamable HTTP로 progress 알림을 흘려보내면, 그것도 그래프의 스트리밍 이벤트로 흘러나옵니다.

```python
async for event in app.astream({"messages": [...]}, stream_mode="updates"):
    # event는 각 노드의 출력 변화
    print(event)
```

이 흐름은 사용자 UI에 진행률을 보여 줄 때 유용합니다. fan-out 노드들이 병렬로 실행되면 각 분기의 진행이 별도 이벤트로 들어옵니다.

다음은 **Checkpointing과 세션 복원**입니다. LangGraph의 가장 큰 강점 중 하나는 그래프 실행 상태를 체크포인트로 저장하고 재개할 수 있다는 점입니다.

```python
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string(":memory:")
app = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "user-42"}}
# 첫 호출
await app.ainvoke({"messages": [...]}, config=config)
# 나중에 같은 thread_id로 이어서
await app.ainvoke({"messages": [추가 메시지]}, config=config)
```

체크포인트는 LangGraph의 상태를 디스크에 저장하므로, 같은 대화를 며칠 뒤에 이어 갈 수 있습니다. MCP 세션의 Mcp-Session-Id(2.2.3)와 다른 계층이지만 비슷한 역할을 합니다. MCP 세션이 transport 단의 세션이라면, LangGraph 체크포인트는 그래프 상태 단의 세션입니다.

다음은 **실전 패턴 한 가지**입니다. fan-out + supervisor의 결합 예시입니다.

```python
# fan-out 단계
async def fan_out(state):
    user_q = state["messages"][-1].content
    tasks = [
        research_graph.ainvoke({"q": user_q, "source": "wiki"}),
        research_graph.ainvoke({"q": user_q, "source": "github"}),
        research_graph.ainvoke({"q": user_q, "source": "web"}),
    ]
    results = await asyncio.gather(*tasks)
    return {"branch_results": results}

# fan-in 단계
async def fan_in(state):
    summary = await combine_chain.ainvoke({"branches": state["branch_results"]})
    return {"messages": [...state["messages"], summary]}
```

이 예시는 5.1.2에서 다룬 fan-out·fan-in 패턴을 LangGraph 코드로 옮긴 형태입니다. 각 분기는 자기 MCP 서버를 호출합니다.

다음은 **주의점과 함정**입니다.

```
함정                                          완화
async와 sync 혼용                              모든 그래프 호출을 await으로
같은 client를 재사용하지 못함                  MultiServerMCPClient는 컨텍스트 매니저
stdio 자식 프로세스 누수                        async with 블록 안에서 사용
도구 description의 한국어 변환                  필요 시 데코레이터로 후처리
recursion limit 도달                            recursion_limit 명시
```

특히 stdio 자식 프로세스 누수가 자주 발생합니다. `async with client:` 블록을 빠져나갈 때 자식 프로세스가 자동으로 종료되므로, 블록 밖에서 클라이언트를 들고 다니지 않아야 합니다.

마지막으로, LangGraph + MCP의 가장 큰 가치는 **표준 위에 또 다른 표준이 얹힌다**는 점입니다. MCP가 도구 통합을 표준화하고, LangGraph가 에이전트 그래프를 표준화합니다. 한 시스템이 두 표준을 함께 따르면, 도구·에이전트 둘 다 다른 시스템으로 옮기는 비용이 낮아집니다.

정리하면, LangGraph는 그래프 기반 에이전트 표현과 LangChain 생태계의 도구를 결합해 멀티 에이전트 시스템을 표준화하며, langchain-mcp-adapters가 MCP를 그 안에 자연스럽게 합류시킵니다. MultiServerMCPClient·ToolNode·subgraph·checkpointing이 핵심 부품입니다.

다음 단원인 5.2.2에서는 대화 기반 협력을 강조하는 AutoGen과 MCP의 결합을 살펴봅니다.
