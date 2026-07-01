# Project 01 — ReAct + Reflexion Self-Improving AI Agent

> **한 줄:** 직원이 자연어로 요청하면 사내 플랫폼 API를 호출해 처리하고, 실패하면 스스로 반성해 재시도를 줄이는 자기 개선형 AI 에이전트.
> **헤드라인 숫자:** 동일 작업 재시도 약 55% 감소 · 17개 도구 연결 · 5개 관측(Observability) Spec.
> 소속 Plantynet · 2025.09~현재 · 3명 팀(Front·Back·AI) · AI Agent 로직 전체(설계·구현·배포) 단독 담당.

---

## 0. 이 프로젝트로 증명할 것 (What this proves about you)

- **"LLM을 쓰는 사람"이 아니라 "실패에서 스스로 배우는 에이전트를 설계하는 사람."** ← Reflexion 설계 능력. 당신의 가장 큰 차별점.
- 운영 LLM의 비결정성(non-determinism)을 **관측 가능하게(observable)** 만든 LLMOps 감각.
- **설문으로 실제 페인포인트를 정량화**한 문제정의 능력 — 추측이 아니라 데이터로 시작했다는 점.

> 이 프로젝트는 "에이전트를 직접 설계·운영해봤는가"를 묻는 질문에 **가장 강한 카드**입니다. "Tell me about an agent you built"에 이걸 꺼내세요.

---

## 1. 생각 구조 (5-Beat skeleton, 이 프로젝트 버전)

| Beat | 이 프로젝트에서 말할 내용 |
|------|---------------------------|
| **1 Headline** | 사내 플랫폼에 붙는 자기 개선형 AI 에이전트를 만들었다. 실패에서 스스로 배워 동일 작업 재시도를 약 55% 줄였다 |
| **2 Problem** | 단순 에이전트는 Tool Calling 실패 시 같은 실수를 반복하거나 멈춤. 게다가 구두 요청 중심이라 Spec 문서·이력이 누락됨 |
| **3 Decision** | ReAct(추론+행동)에 실패 시 자기반성(Reflexion)을 추가. 실패를 problem/solution 쌍으로 장기기억에 저장해 재주입, LangGraph로 구현 |
| **4 Hard Part** | 운영 LLM의 비결정성 + 비용. 2단계 Evaluator(규칙→LLM)로 비용 통제, 5개 관측 Spec으로 운영을 보이게 |
| **5 Result** | 동일 유형 재시도 약 55% 감소, 17개 도구 연결, Spec 자동 생성으로 설문 1순위(기획-개발 간극) 해소 |

> 핵심 메시지 한 줄: **"The whole project was about making an agent that learns from its own failures instead of repeating them."**

---

## 2. 모범답안 (Model Answers)

### 🟢 Version A — Elevator (약 30초, 쉬운 영어)

> In short, I built an AI agent for our internal work platform. People just type what they want in **plain language** — like "write a spec document" or "summarize this sprint" — and the agent calls the right tools to do it. The hard part was that when a tool call failed, a normal agent would **repeat the same mistake** or just stop. So I made it stop, **reflect** on why it failed, save that lesson, and use it next time. That cut the average number of retries for the same kind of task by about **fifty-five percent**.

> **핵심 표현**
> - "in plain language" = 자연어로, 쉬운 말로
> - "the right tools" = 알맞은 도구
> - "repeat the same mistake" = 같은 실수를 반복하다
> - "reflect on why it failed" = 왜 실패했는지 돌아보다
> - "save that lesson" = 그 교훈을 저장하다
> - "cut ... by about fifty-five percent" = 약 55% 줄이다
> **전달 팁:** "fifty-five percent"에서 또박또박 멈추세요. 숫자가 이 답변의 힘입니다.

---

### 🟡 Version B — Standard (약 75초, 자연스러운 영어) ← 기본값

> So, this was an AI agent project at **Plantynet**. We have an internal work-management platform, and the idea was to let employees just ask for things in **natural language** — "write a spec document," "summarize this sprint" — and have the agent call the platform's APIs to actually do it.
>
> The real problem was **failure**. When a tool call went wrong, a plain agent would either repeat the same mistake or get stuck. On top of that, a lot of our collaboration was verbal, so spec documents and work history kept getting lost — and a **survey** we ran before building confirmed those were the top two pain points.
>
> So the key decision was to go beyond a simple **ReAct** loop. ReAct is just reasoning and acting, and on its own it couldn't break the failure loop. I added a **reflection step**: when the agent fails, it writes down the problem and a possible solution, stores that in a **long-term memory**, and re-injects it the next time a similar situation comes up. I built that whole flow — actor, tool executor, evaluator, and reflection — in **LangGraph**.
>
> The tricky part was cost and reliability in production. Checking every failure with an LLM is expensive, so the evaluator runs in **two stages** — a cheap keyword rule first, then an LLM only for the precise judgment. And if the same failure happens **three times**, it stops early instead of burning calls.
>
> As a result, the average number of retries for the same kind of task dropped by about **fifty-five percent**. We connected **seventeen** tools, and the agent now auto-generates spec documents, which directly fixed that number-one complaint from the survey.

> **핵심 표현**
> - "in natural language" = 자연어로 (업계 표준 표현)
> - "get stuck" = (진행이) 막히다, 멈추다
> - "go beyond a simple ReAct loop" = 단순 ReAct 루프를 넘어서다
> - "a reflection step" = 자기반성 단계
> - "re-inject it the next time" = 다음번에 다시 주입하다
> - "in two stages" = 2단계로
> - "stops early" = 일찍 멈추다 (Early Stopping)
> **전달 팁:** Problem-Decision-Result 비트에서 잠깐씩 멈춰 호흡을 끊으면 구조가 또렷이 들립니다.

---

### 🔴 Version C — Deep Dive (약 2~3분, 고급 영어) ← "더 자세히" 요청 시

> Sure, let me go a bit deeper on the design.
>
> The goal was a self-improving agent sitting on top of our internal platform — an **MCP host** that turns a natural-language request into real API calls. The constraint I cared about most was **failure recovery**. A plain ReAct agent reasons and acts in a loop, but when a tool call fails, it tends to either loop on the same wrong action or give up. That's the gap I wanted to close.
>
> So my core design was to add a **Reflexion** stage on top of ReAct. The flow has four roles, and I implemented all of them in **LangGraph**: an actor that decides the next action, a tool executor that runs it, an evaluator that judges the result, and a reflection step. The piece I'm most proud of is the long-term memory — I call it the **LessonsStore**. When the agent fails, it doesn't just retry blindly; it distills the failure into a **problem-and-solution pair**, stores it, and then re-injects the matching lesson into the prompt whenever a similar situation comes up. And to avoid burning tokens forever, if the exact same failure happens three times, it triggers **early stopping**.
>
> The evaluator itself is where the cost engineering lives. Judging every result with an LLM would be expensive, so it runs in **two stages**: first a cheap keyword rule that catches obvious errors, and only then a precise LLM judgment that checks whether the result actually matches the user's intent. Cheap filter first, expensive judge second.
>
> The other hard part was operating an LLM in production, where behavior is **non-deterministic**. You can't just hope it works — you have to make it **observable**. So I defined **five observability specs**: request tracing, prompt and response logging, token usage, latency, and error tracking. For tooling I went with **Langfuse** — which is LLM-specific and self-hostable — plus Sentry, Grafana, and Prometheus. I also split error tracking into **five categories** — LLM, parse, tool, agent-logic, and system — so when something breaks, I know which layer to look at. On deployment, I separated the agent service from the MCP server with **Docker Compose**, so I can redeploy just the agent without dropping the MCP connections.
>
> The end result: retries for the same type of task dropped by about **fifty-five percent**, we wired up **seventeen** tools across three layers, and the two top survey complaints — the planning-versus-dev gap and lost verbal history — got solved by auto-generated spec docs and feed-based history tracking.

> **핵심 표현 (고급)**
> - "self-improving agent / MCP host" = 자기 개선형 에이전트 / MCP 호스트
> - "failure recovery" = 실패 복구
> - "distills the failure into a problem-and-solution pair" = 실패를 problem/solution 쌍으로 압축
> - "re-injects the matching lesson into the prompt" = 맞는 교훈을 프롬프트에 재주입
> - "early stopping" = 조기 종료 (반복 실패 차단)
> - "non-deterministic / observable" = 비결정적 / 관측 가능한
> - "cheap filter first, expensive judge second" = 싼 필터 먼저, 비싼 판단 나중
> **전달 팁:** 길어서, 면접관 표정을 보며 "Want me to go deeper on any part?"로 중간 점검하면 좋습니다.

---

## 3. 꼬리질문 대비 (Follow-up Q&A)

**Q1. What's the difference between ReAct and Reflexion, and why did you need both?**
> ReAct is the base loop — the agent reasons about what to do, takes an action, and looks at the result. The problem is, on its own it has no memory of why something failed, so it tends to repeat the same mistake. Reflexion adds that missing piece: after a failure, the agent reflects, writes down what went wrong and how to fix it, and carries that forward. So ReAct is "think and act," and Reflexion is "learn from what just went wrong." I needed both because acting without learning was exactly the failure loop I was trying to break.
> *(한국어 메모: 둘의 역할 분담 — ReAct=행동, Reflexion=학습 — 을 한 문장으로 대비시키면 깔끔합니다.)*

**Q2. How does the agent actually "remember" past failures?**
> I store each failure as a problem-and-solution pair in a long-term memory I call the LessonsStore. It's not the full conversation — just a distilled lesson. When a new request looks similar to a past failure, I pull the matching lesson and re-inject it into the prompt, so the model goes in already knowing what to avoid. And if the same failure repeats three times, I stop early instead of looping forever.
> *(한국어 메모: "전체 대화가 아니라 압축된 교훈만 저장"이 비용·품질 양쪽에서 똑똑한 선택임을 강조하세요.)*

**Q3. Why is the evaluator two stages instead of just using the LLM?**
> Cost. If I sent every single result to an LLM to judge, that gets expensive fast. So the first stage is a cheap keyword rule that catches obvious errors with no model call at all. Only what gets past that goes to the second stage, where an LLM checks whether the result really matches the user's intent. Cheap filter first, expensive judge second — same idea as a fast path and a slow path.
> *(한국어 메모: "fast path / slow path" 비유는 면접관이 바로 이해합니다. 비용 의식을 보여주는 답.)*

**Q4. You said the LLM is non-deterministic in production. How did you handle that?**
> You can't make an LLM fully deterministic, so instead of fighting it, I made it observable. I defined five observability specs — request tracing, prompt and response logging, token usage, latency, and error tracking — and wired them up with Langfuse, Sentry, Grafana, and Prometheus. I also bucket every error into one of five categories — LLM, parse, tool, agent-logic, or system — so when something goes wrong I can tell which layer to look at right away. The point isn't to remove the randomness; it's to never be blind to it.
> *(한국어 메모: "비결정성을 없애는 게 아니라 보이게 만든다"가 LLMOps 핵심 메시지. 그대로 외우세요.)*

**Q5. How did you decide what to build in the first place?**
> I didn't want to guess, so before writing any code I ran a survey with our developers and planners to quantify the actual pain points. The top complaint was that requirements kept getting misaligned between planning and development, and the second was that verbal requests left no history. That ranking is what shaped the product — auto-generated spec documents for the first one, and feed-based history tracking for the second.
> *(한국어 메모: "추측 대신 설문으로 정량화"는 시니어 신호. 1순위·2순위를 해결책과 1:1로 연결하세요.)*

**Q6. Why separate the agent and the MCP server in deployment?**
> I ran them as two services with Docker Compose so they're decoupled. The agent logic changes a lot — that's where I iterate — but the MCP server and its tool connections are pretty stable. By splitting them, I can redeploy just the agent without tearing down the MCP connections every time. It keeps deployments fast and avoids unnecessary downtime on the part that didn't change.
> *(한국어 메모: "자주 바뀌는 것과 안 바뀌는 것을 분리"가 배포 설계의 핵심 원리임을 보여주는 답.)*

---

## 4. 핵심 표현·어휘 (Key phrases & vocabulary)

| English | 뜻 / 쓰임 |
|---------|-----------|
| ReAct (reasoning + acting) | 추론하고 행동하는 에이전트 기본 루프 |
| Reflexion | 실패 후 자기반성으로 학습하는 패턴 |
| self-improving agent | 자기 개선형 에이전트 |
| tool calling | 도구 호출 (에이전트가 API·함수를 부름) |
| MCP host / MCP server | 도구 연결을 담당하는 호스트 / 서버 |
| long-term memory | 장기기억 (실패 교훈 저장소) |
| re-inject into the prompt | 프롬프트에 다시 주입 |
| early stopping | 조기 종료 (반복 실패 차단) |
| evaluator | 평가기 (결과 판정) |
| observability | 관측 가능성 (운영 상태를 보이게) |
| non-deterministic | 비결정적 (같은 입력에 다른 출력) |
| request tracing | 요청 추적 |
| decouple / separate services | 서비스 분리 (독립 배포) |
| pain point | 페인 포인트 (실제 불편) |

---

## 5. 발음 주의 (Delivery watch-outs)

| 단어 | 강세 / 주의 |
|------|-------------|
| Reflexion | ri-FLEK-shun (reflection과 비슷, x는 k+sh 소리) |
| ReAct | "ree-ACT" (리-액트, 두 토막으로 또렷이) |
| evaluator | ee-VAL-yoo-ay-ter |
| observability | ub-zer-vuh-BIL-i-tee |
| non-deterministic | non-di-ter-MIN-is-tic |
| latency | LAY-ten-see |
| Langfuse | "LANG-fuse" (랭-퓨즈) |
| LangGraph | "LANG-graf" |
| Gemini | JEM-in-ee (제미니). 끝을 "-나이"로 빼지 않기 |
| 17 | "seventeen" (seventy 아님!) |
| 55% | "fifty-five percent" — v 소리, th 아님 |

> **마지막 점검:** 이 프로젝트의 힘은 "약 55% 감소"와 "에이전트가 실패에서 스스로 배운다"입니다. 이 두 가지를 또렷이, 자신 있게.
