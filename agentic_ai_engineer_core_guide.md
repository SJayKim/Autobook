# Agentic AI 엔지니어 핵심 역량 & 학습 가이드

> 4년차 이상 실무 경험자 기준. LeetCode + System Design + Agent 전반을 압축 정리.

---

## 1. 한 줄 정의

**Agentic AI 엔지니어 = LLM이 도구를 사용하고, 상태를 관리하며, 장기 작업을 안정적으로 수행하도록 시스템을 설계·구현·평가·운영하는 엔지니어.**

API 래퍼 개발자가 아니라 **"불안정한 모델 위에 안정적인 시스템을 얹는 사람"**.

---

## 2. 핵심 역량 맵

| 영역 | 학습 핵심 | 목표 수준 |
|---|---|---|
| **Coding (LeetCode)** | DS/Algo 패턴 11종 | Medium 안정, Hard 일부 |
| **System Design** | 분산 시스템 + AI 특화 설계 | RAG/Agent 플랫폼 화이트보드 설계 |
| **LLM 기본** | Prompt, Function calling, Structured output | 모델 안정 연결 |
| **RAG / GraphRAG** | Chunking, Hybrid search, Rerank, KG-RAG | 검색 품질 측정·개선 |
| **Agent Architecture** | ReAct, Reflexion, Plan-Execute, Multi-agent | 장기 작업 자동화 설계 |
| **Memory** | Short/Long-term, Episodic, Semantic | 맥락 관리 시스템 설계 |
| **MCP / Tool** | Server/Client, stdio vs HTTP, Gateway | 외부 시스템 표준 연동 |
| **Evaluation** | RAG eval, Agent eval, Regression | 자동 품질 검증 루프 |
| **Observability** | Tracing, Cost/Latency 모니터링 | 운영 디버깅 가능 |
| **Security** | Prompt injection, Tool permission | Agent 오작동 방지 |
| **Prompt Optimization** | DSPy, GEPA, TextGrad | 자동 프롬프트 개선 파이프라인 |

---

## 3. LeetCode 준비

**목표**: Medium 150~200문제 안정 풀이. AI 직군이어도 코테는 백엔드 기본기 검증용.

### 우선순위 패턴 11개

1. Array / HashMap
2. Two Pointers
3. Sliding Window
4. Stack / Queue (Monotonic Stack 포함)
5. Binary Search (답 이분 탐색 포함)
6. Tree DFS / BFS
7. Graph DFS / BFS / Union-Find / Topological Sort
8. Heap / Priority Queue (Top-K)
9. Intervals
10. Dynamic Programming (1D/2D, Knapsack, LIS)
11. Trie / Backtracking

### 학습 경로

- **NeetCode 150 → Blind 75 → LeetCode Top Interview 150**
- 한국 기업 대비: **프로그래머스 Lv.2~3 카카오/네이버 기출**, 백준 골드 티어
- 일 1~2문제 꾸준히 (헤이딜러처럼 take-home은 Medium 80% / Hard 20%)

### 면접 시 평가 포인트

- 시간/공간 복잡도 명확히 설명
- 엣지 케이스 먼저 언급
- 변수명·구조 깔끔하게
- 무리한 최적화보다 정확한 구현

---

## 4. System Design

### 4-1. 전통 시스템 디자인 (기본)

| 주제 | 핵심 |
|---|---|
| Scalability 기초 | Load Balancer, Cache (Redis, CDN), Sharding/Replication |
| API Design | REST vs GraphQL vs gRPC 선택 기준 |
| Message Queue | Kafka, RabbitMQ, SQS — 언제 무엇을 |
| Consistency | Strong vs Eventual, CAP |
| 안정성 패턴 | Rate Limiter, Circuit Breaker, Idempotency |
| Job Queue | Producer/Consumer, Retry, DLQ |

**추천 자료**: 『가상 면접 사례로 배우는 대규모 시스템 설계 기초』 1~2권, ByteByteGo

### 4-2. AI/LLM 특화 System Design (차별화 포인트)

| 주제 | 핵심 설계 포인트 |
|---|---|
| **RAG System** | Ingestion → Chunking → Embedding → Hybrid Retrieval → Rerank → Generate → Citation. **Freshness SLA** 고려. |
| **AI Agent Platform** | Planner, Tool Registry, Memory, Execution Engine, Guardrail |
| **Multi-Agent** | Orchestrator/Supervisor, Specialist Agent, Handoff, A2A |
| **LLM Gateway** | Model routing, Fallback, Semantic/Prefix Cache, Cost control |
| **Evaluation Platform** | Golden dataset, LLM-as-Judge, Regression test |
| **Coding Agent** | Repo indexing, Issue 분석, Patch 생성, Test 실행 |
| **MCP Architecture** | stdio vs Streamable HTTP, Gateway, Tool 수 임계점 관리 |

### 대표 면접 케이스

- "ChatGPT를 설계하세요" / "Perplexity를 설계하세요"
- "1000개 tool을 가진 Agent system을 어떻게 설계할 것인가"
- "RAG 시스템의 freshness를 어떻게 보장할 것인가"
- "Agent 실행 로그/Tracing 시스템을 설계하세요"

---

## 5. LLM / RAG / Agent 핵심

### 5-1. LLM 기본기

- Prompt engineering, System/User/Assistant 구조
- **Function calling / Tool calling** (필수)
- **Structured output** (JSON schema, Pydantic)
- Streaming, Token/Context window 관리
- Sampling 파라미터 (temperature, top-p)
- Fine-tuning vs RAG vs Prompting 의사결정

**실무 질문**:
- JSON output이 invalid하면? → retry + schema 강제
- Tool 선택 오류 줄이는 법? → description 개선, few-shot, routing layer
- 모델 변경 시 품질 저하 감지? → regression eval

### 5-2. RAG 핵심

**구성요소**: Loader → Parser → Chunker → Embedding → Vector DB → Retriever → Reranker → Generator → Citation → Eval

**Vector DB 옵션**: pgvector, Qdrant, Weaviate, Milvus, OpenSearch (hybrid)

**품질 개선 레버**:
- Chunk size/overlap 튜닝
- Metadata filtering
- **Hybrid search (BM25 + Dense)**
- Query rewriting / HyDE / Multi-query
- Reranking (Cohere, BGE-reranker)
- Citation으로 hallucination 억제

**GraphRAG / KG-RAG** (차별화):
- Microsoft GraphRAG, OG-RAG, KAG
- 테이블/관계형 데이터에 강함
- Cypher schema + fact node (시계열 처리)

### 5-3. Agent 패턴

| 패턴 | 사용 시점 |
|---|---|
| ReAct | 기본. Reasoning + Acting 반복 |
| Reflexion | 자기 결과 검토 후 수정 |
| Plan-and-Execute | 다단계 작업 |
| Tree of Thoughts | 탐색 필요한 작업 |
| Router Agent | 요청 분배 |
| Workflow (LangGraph) | 정해진 DAG 흐름 |
| Multi-Agent (Supervisor/Hierarchical/Swarm) | 전문성 분리 필요 시 |

**Agent 구성요소**: Planner / Executor / Tool Registry / Memory / State / Orchestrator / Guardrail / Evaluator / Tracer

### 5-4. Memory 설계

| 유형 | 용도 |
|---|---|
| Short-term | 현재 대화 맥락 (window/summary) |
| Long-term | 사용자/작업 정보 (vector/KV) |
| Episodic | 과거 실행 경험 |
| Semantic | 일반화된 지식 (RAG와 결합) |
| Procedural | 반복 절차/스킬 |

**핵심 질문 5개**: 무엇을 / 언제 / 어떻게 검색 / 어떻게 갱신 / 어떻게 보호.

### 5-5. MCP / Tool Integration

- **개념**: Tool, Resource, Prompt, Server, Client
- **Transport**: stdio (로컬) vs Streamable HTTP (원격)
- **실무 패턴**: MCP Gateway, security layering, tool 수 폭증 시 routing
- **예시**: Gmail, Calendar, GitHub, Slack, DB, File MCP

### 5-6. Prompt Optimization (트렌드)

- **DSPy**: 프롬프트를 모듈화·자동 컴파일
- **GEPA**: Generative Evolutionary Prompt Adaptation — Reflexion 경험 있다면 자연스러운 확장
- **TextGrad, OPRO**: gradient-like 최적화

---

## 6. Evaluation & Observability

### 6-1. Evaluation

| 영역 | 지표 |
|---|---|
| RAG 검색 | Context precision/recall |
| 답변 품질 | Faithfulness, Relevance, Correctness |
| Agent | Task success rate |
| Tool 사용 | Tool selection accuracy |
| 비용/속도 | Token usage, p50/p95/p99 latency |

**도구**: Ragas, DeepEval, LangSmith, **Langfuse**, Phoenix/Arize, TruLens

**평가 루프**: Golden dataset → 자동 실행 → 평가 → 실패 분석 → 수정 → Regression

### 6-2. Observability

**필수 로깅**: User input / System prompt version / Model / Retrieved docs / Tool I/O / Reasoning / Final answer / Token / Latency / Error

**운영 지표**: Task success rate, Tool failure rate, Hallucination rate, Cost per request, p95 latency, Retry count

---

## 7. Security & Safety

| 위험 | 방어 |
|---|---|
| Prompt Injection | 입력 검증, 분리된 컨텍스트, 탐지기 |
| Tool Abuse | Allowlist, Human approval, 권한 분리 |
| Data Leakage | 민감 정보 마스킹, output 검증 |
| Excessive Agency | 최소 권한 원칙, scope 제한 |
| Insecure Output | Downstream 입력 sanitize |
| Secret Exposure | Vault, env 격리, audit log |

---

## 8. 면접 핵심 질문

### Coding
- HashMap 중복 탐지 / BFS vs DFS / Top-K (Heap) / Sliding window / Graph cycle / DP 점화식

### Backend
- async 사용 시점 / Redis 활용처 / DB index 필요 시점 / Queue 비동기 / Idempotency 중요성

### System Design
- "RAG 시스템을 설계해보세요"
- "대용량 문서 ingestion pipeline"
- "LLM Gateway 설계"
- "Agent 실행 로그/Tracing 시스템"
- "Tool call 실패 시 retry/rollback"

### Agentic AI
- Agent vs Workflow 차이
- Multi-agent가 필요한 시점
- Memory 설계
- Tool selection 오류 감소 전략
- Human-in-the-loop 위치
- Prompt injection 방어

### Evaluation
- RAG 품질 평가법
- Agent 성공률 측정
- 모델 변경 regression test
- LLM-as-Judge 신뢰성 확보

---

## 9. 포트폴리오 추천

| 프로젝트 | 보여주는 역량 |
|---|---|
| **RAG 기반 Research Agent** ⭐ | RAG 전체 스택 + Agent + Eval (가장 추천) |
| Coding Agent | Repo 분석, PR 생성, test 자동화 |
| Data Analysis Agent | NL → SQL → 차트/리포트 |
| Document Agent | PDF 파싱 + 요약 + Q&A |
| Workflow Agent | Gmail/Calendar/Slack 자동화 |
| Evaluation Dashboard | Agent 품질 자동 평가 |

**Research Agent 1개 제대로 만들기 = Agentic AI 엔지니어 핵심 역량 대부분 증명 가능**

포함 기능: 문서 업로드 → 파싱 → Chunking → Embedding → Vector DB → Hybrid Search → Reranking → 출처 기반 답변 → Tool calling → Evaluation → Tracing

---

## 10. 학습 우선순위 (단계별 로드맵)

1. **Python Backend** — FastAPI, async, PostgreSQL, Redis, Docker
2. **LeetCode Medium** — 패턴 11개, 150~200문제
3. **System Design** — 전통 + AI 특화
4. **RAG** — OpenAI API, LangGraph, Vector DB, Reranker, Eval
5. **Agent** — Tool calling, Planner, Memory, Multi-agent, MCP, Tracing, Guardrail
6. **Evaluation** — Ragas, Langfuse, Regression
7. **Security** — Injection, Permission, Sandbox
8. **포트폴리오 프로젝트** — Research Agent 완성 + README + 설계문서 + 데모

---

## 11. 핵심 정리

Agentic AI 엔지니어의 차별점:

- **Agent 동작 구조 이해** (단순 LangChain 사용자가 아님)
- **Tool / Memory / State / Eval 설계 가능**
- **실패 케이스 줄여서 운영 가능한 시스템화**
- **LeetCode + System Design으로 엔지니어링 기본기 증명**

> 가장 좋은 준비 전략 = **LeetCode Medium + RAG System Design + 실제 Agent 프로젝트** 동시 진행.
