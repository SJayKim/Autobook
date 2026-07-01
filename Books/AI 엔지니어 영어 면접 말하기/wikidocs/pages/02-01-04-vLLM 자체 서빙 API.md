# Project 04 — vLLM-Based In-House Text-Processing API

> **한 줄:** 사내 기사 요약·분류·태깅을 외부 API 없이 처리하는 자체 LLM 서빙 API.
> **헤드라인 숫자:** 외부 API 비용 100% 제거 · 응답 약 65% 단축 · 요약 길이 수렴 92% · 6종 API 통합.
> 소속 Plantynet · 2024.10~2025.04 · 3명 팀 · 중간 LLM 로직·서빙 API 설계 / 개발 / 배포 전담.

---

## 0. 이 프로젝트로 증명할 것 (What this proves about you)

- **"모델을 쓰는 사람"이 아니라 "모델을 직접 서빙하는 인프라를 설계·선정하는 사람."** ← 서빙 방식 3가지를 비교한 뒤 in-process vLLM을 고른 인프라 의사결정.
- 비용과 레이턴시를 **동시에** 잡은 성과: 외부 API 호출 비용 100% 제거 + 평균 응답 약 65% 단축.
- 기존 연동을 깨지 않는 **점진 마이그레이션** 설계 (v0 → v1, 6종 API를 한 서비스로 통합).
- 도구를 목적에 맞게: 단순 서빙엔 vLLM, 분기·재시도가 필요한 곳에만 LangGraph.

> 이 프로젝트는 "아키텍처를 결정한 경험" 또는 "비용을 줄인 경험" 질문에 꺼내세요. **세 가지 옵션을 비교한 이야기**가 핵심 카드입니다.

---

## 1. 생각 구조 (5-Beat skeleton, 이 프로젝트 버전)

| Beat | 이 프로젝트에서 말할 내용 |
|------|---------------------------|
| **1 Headline** | 기사 요약·분류·태깅을 외부 API 없이 처리하는 사내 자체 LLM 서빙 API를 만들었다 |
| **2 Problem** | 요약·분류·태깅을 외부 LLM API에 의존 → 비용과 응답 속도가 둘 다 문제 |
| **3 Decision** | 서빙 방식 3가지(외부 API / vLLM 별도 서버 / in-process)를 비교 → in-process vLLM 채택. 외부 API 비용 100% 제거, 응답 약 65% 단축 |
| **4 Hard Part** | 6종 API를 기존 연동을 깨지 않고 이전 + 분기·재시도가 필요한 흐름. → v0/v1 점진 전환, v1에 LangGraph |
| **5 Result** | 외부 API 비용 0, 응답 약 65% 단축, 6종 API 단일 서비스화, 요약 길이 수렴 약 92% |

> 핵심 메시지 한 줄: **"The whole project was about bringing our text processing in-house — so we pay nothing per call and respond a lot faster."**

---

## 2. 모범답안 (Model Answers)

### 🟢 Version A — Elevator (약 30초, 쉬운 영어)

> In short, I built an in-house API that handles article summarizing, classifying, and tagging for us. Before this, we paid an outside API for all of that, and it was both expensive and slow. So we decided to run the model ourselves, inside our own service. I used **vLLM** right inside our FastAPI app, so there's no outside call at all. That cut our external API cost by **100 percent** — we pay nothing per call now — and it brought the response time down by about **65 percent**. We also put six of these tools into one single service. It was a nice win on both cost and speed.

> **핵심 표현**
> - "in-house" = 외주·외부가 아니라 자체적으로
> - "run the model ourselves" = 우리가 직접 모델을 돌리다 (= self-host)
> - "no outside call at all" = 외부 호출이 아예 없다
> - "cut our cost by 100 percent" = 비용을 100% 줄이다
> **전달 팁:** "100 percent"와 "65 percent"에서 또박또박 멈추세요. 이 두 숫자가 답변의 힘입니다.

---

### 🟡 Version B — Standard (약 75초, 자연스러운 영어) ← 기본값

> So this was an **in-house LLM serving** project. We needed to summarize, classify, and tag news articles, and at first we did all of that through an external LLM API. The problem was that it hit us on two sides at once — the cost per call and the response time were both too high.
>
> So the **key decision** was how to serve the model ourselves. I looked at three options: keep the external API, run **vLLM** as a separate server, or run it **in-process** — right inside the FastAPI app. I went with in-process, because it removes the network hop between services and keeps everything in one container. That cut the external API cost by **100 percent**, since we self-host now, and it brought the average response time down by about **65 percent**. To keep the GPU busy, I leaned on vLLM's **continuous batching**, and I used an **asyncio semaphore** to cap concurrency so we don't blow past GPU memory.
>
> The other half was **migration**. We had six of these endpoints — summary, classification, tagging — and I couldn't break the existing integrations. So I rolled it out in two stages: **v0** was plain vLLM serving, and **v1** added a **LangGraph** agent for the flows that needed branching and retries, like making a summary land within a target length. That convergence step now succeeds about **92 percent** of the time.
>
> So in the end, we own the whole stack, the per-call cost is gone, responses are about 65 percent faster, and all six tools live in one service.

> **핵심 표현**
> - "serve the model ourselves" = 모델을 자체 서빙하다
> - "in-process / a separate server" = 같은 프로세스 안 / 별도 서버 (서빙 구조 두 갈래)
> - "removes the network hop" = 서비스 간 네트워크 경유를 없앤다 (지연 감소)
> - "continuous batching" = 연속 배칭 (vLLM 핵심 용어, 꼭 쓰세요)
> - "cap concurrency" = 동시 처리량에 상한을 두다
> - "blow past GPU memory" = GPU 메모리를 넘겨버리다 (구어체)
> **전달 팁:** Problem-Decision-Migration 세 비트 사이에서 0.5초씩 끊으면 구조가 또렷이 들립니다.

---

### 🔴 Version C — Deep Dive (약 2~3분, 고급 영어) ← "더 자세히" 요청 시

> Sure, let me go deeper on the design.
>
> The starting point was that our summarization, classification, and tagging all went through an external LLM API, and that cost us on both price and latency. So the core question was how to bring the model in-house. I compared three serving setups: the existing external API, vLLM as its own **separate service**, and vLLM running **in-process** — meaning the model runs inside the same FastAPI process that serves the requests. I chose in-process. A separate vLLM server would have been easier to scale on its own, but it adds a network hop and another service to deploy and watch. In-process keeps the request, the batching, and the GPU all in one place, which for our scale was simpler and faster. That's how we got the external API cost down to zero — a **100 percent** cut — and the average response time down by roughly **65 percent**.
>
> The piece I'm most proud of on the serving side is how concurrency is handled. vLLM does **token-level continuous batching**, so instead of waiting for a whole batch to finish, new requests join the batch as soon as there's room — that's what keeps the GPU efficient under load. But the risk there is GPU memory: too many requests at once and you run out of VRAM. So I guard it with an **asyncio semaphore** that caps how many requests are in flight, which keeps memory safe without killing throughput.
>
> The second hard part was migration. We had six endpoints already wired into other systems, so a big-bang rewrite was off the table. I did it in two versions running side by side: **v0** was straight vLLM serving, and **v1** layered a **LangGraph** agent on top for the flows that needed real control flow — branching and retries. The clearest example is summary length. We want a summary to land within a target range — roughly **70 to 130 percent** of the target — so the agent checks the output, and if it's off, it loops and retries until it converges. That now succeeds about **92 percent** of the time. For long documents I used a **Map-Refine** approach — pull bullet points out of each chunk first, then turn those bullets into clean prose.
>
> On the delivery side, it's all containerized with **Docker** and the **NVIDIA Container Toolkit** for GPU access, and I used a **multi-stage Dockerfile** so the heavy build dependencies don't end up in the runtime image — that keeps the image small. Docker Compose handles startup and updates. There's also a small **Gradio** UI so the planning team can test any endpoint themselves without calling me. So in the end: no external API cost, about 65 percent faster, six tools in one service, and a clean two-version migration path.

> **핵심 표현 (고급)**
> - "bring the model in-house" = 모델을 자체 인프라로 들이다
> - "token-level continuous batching" = 토큰 단위 연속 배칭
> - "requests in flight" = 처리 중인(동시에 떠 있는) 요청
> - "a big-bang rewrite was off the table" = 한 번에 갈아엎는 방식은 선택지에서 제외
> - "real control flow — branching and retries" = 진짜 제어 흐름 (분기·재시도)
> - "land within a target range" = 목표 범위 안에 들어오다 (수렴)
> - "multi-stage Dockerfile" = 다단계 도커파일 (이미지 경량화)
> **전달 팁:** 길어서, "Want me to go deeper on the serving or the migration side?"로 중간 점검하면 자연스럽습니다.

---

## 3. 꼬리질문 대비 (Follow-up Q&A)

**Q1. Why in-process vLLM instead of a separate vLLM server?**
> A separate server is easier to scale on its own, but it adds a network hop and another service to deploy and watch. For our scale, keeping vLLM in-process — inside the FastAPI app — was simpler and lower latency, and we got the cost win either way since we self-host. If we later needed to scale serving independently from the API, I'd revisit the separate-server option.
> *(한국어 메모: "장단점을 알고 골랐다 + 조건이 바뀌면 다시 본다"가 시니어 신호입니다.)*

**Q2. How did you migrate six endpoints without breaking existing integrations?**
> I ran two versions side by side. v0 was plain vLLM serving that matched the old behavior, so existing callers kept working untouched. v1 added the LangGraph agent for the flows that needed branching and retries. Teams could move endpoint by endpoint instead of all at once, so nothing broke during the switch.
> *(한국어 메모: 점진 전환의 핵심은 "옛 동작을 그대로 보존한 v0"입니다. 이 한 문장을 빼먹지 마세요.)*

**Q3. How do you keep concurrent requests from running out of GPU memory?**
> Two things work together. vLLM's continuous batching packs requests efficiently at the token level, and on top of that I use an asyncio semaphore to cap how many requests are in flight. The semaphore is the hard ceiling that keeps us from exceeding GPU memory, while batching keeps throughput high under that ceiling.

**Q4. What is the summary-length convergence, and how do you hit 92 percent?**
> We want a summary to land within a target range — about 70 to 130 percent of the target length. In v1, the LangGraph agent generates, checks the length, and if it's outside the range it adjusts and retries in a loop until it converges. That control flow is exactly why I brought in LangGraph, and it lands in range about 92 percent of the time.

**Q5. Why LangGraph instead of just writing the retry loop yourself?**
> I could have hand-coded it, but the flows got more complex than a single retry — conditional branching and retry with state. LangGraph gives me an explicit graph for that control flow, so it's easier to read, extend, and debug than a pile of if-statements. For the simple v0 path I didn't use it at all — only where the branching actually justified it.
> *(한국어 메모: "단순한 곳엔 안 썼다"가 도구 남용을 안 한다는 신호입니다.)*

**Q6. How did you deploy it, and how do non-engineers test it?**
> Everything runs in a Docker container with the NVIDIA Container Toolkit for GPU access, and I used a multi-stage Dockerfile so build dependencies stay out of the runtime image, which keeps it small. Docker Compose handles startup and updates. And I added a small Gradio UI so the planning team can try any endpoint themselves — that cut a lot of back-and-forth.

---

## 4. 핵심 표현·어휘 (Key phrases & vocabulary)

| English | 뜻 / 쓰임 |
|---------|-----------|
| in-house | 자체적으로 / 사내에서 (외주·외부 반대) |
| self-host | 직접 호스팅하다 (외부 API 대신) |
| in-process | 같은 프로세스 안에서 (별도 서버 아님) |
| serving | (모델) 서빙·응답 제공 |
| continuous batching | 연속 배칭 (요청을 토큰 단위로 이어 묶음) |
| in flight | 처리 중인 (동시에 떠 있는 요청) |
| network hop | 서비스 간 네트워크 경유 (지연 요인) |
| cap concurrency | 동시 처리량에 상한을 두다 |
| converge / convergence | (목표 범위로) 수렴하다 |
| branching and retries | 조건 분기와 재시도 |
| side by side | 나란히 (v0/v1 병행) |
| big-bang rewrite | 한 번에 갈아엎는 재작성 (피한 것) |
| control flow | 제어 흐름 (분기·반복) |
| multi-stage build | 다단계 빌드 (이미지 경량화) |

---

## 5. 발음 주의 (Delivery watch-outs)

| 단어 | 강세 / 주의 |
|------|-------------|
| vLLM | "V-L-L-M" (브이-엘-엘-엠). 첫소리 **V**, B로 새지 않기 |
| FastAPI | "fast-A-P-I" (패스트 에이-피-아이) |
| asyncio | ay-SINK-ee-oh (혹은 "AY-sink-eye-oh") |
| semaphore | SEM-uh-for |
| LangGraph | "lang-graph" (랭-그래프), 끝 -ph = f |
| Gradio | GRAH-dee-oh |
| in-process | in-PROSS-ess, 한 단어처럼 붙여서 |
| converge | kun-VERJ — **V** 소리, 끝 -j |
| latency | LAY-ten-see |
| 100% | "by **one hundred** percent" — 끝의 t 살리기 |
| ~65% | "about **sixty-five** percent" |
| 92% | "about **ninety-two** percent" |

> **마지막 점검:** 이 프로젝트의 힘은 "외부 API 비용 100% 제거"와 "응답 약 65% 단축"입니다. **자체 서빙으로 둘 다 잡았다**는 한 문장으로 또렷이 마무리하세요.
