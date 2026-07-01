# Project 08 — MarketScope AI (Map-Based AI Commercial-District Analysis SaaS)

> **한 줄:** 지도에서 상권을 고르고 자연어 한 줄로 물으면 AI가 실시간으로 분석해 주는, 실제 운영 중인 상권분석 SaaS.
> **헤드라인 숫자:** 프로덕션 라이브 v0.4.0 · 서울 1,650개 상권 / 약 14.6만 건 실데이터 · ReAct 7종 Tool · E2E 66/66 + 스모크 28/28.
> 1인 풀스택 사이드 프로젝트(기획·설계·프론트엔드·백엔드·AI Agent·인프라 전부) · 2026.01~현재 운영 중 · live: http://marketscope.robitlabs.co.kr/ · GitHub SJayKim.

---

## 0. 이 프로젝트로 증명할 것 (What this proves about you)

- **기획부터 인프라까지 혼자 만들어 실제 배포까지 한 end-to-end 실행력.** ← 사이드 프로젝트에서 가장 강한 신호. "0에서 1까지 혼자 다 했다."
- **풀스택 폭:** AI 에이전트(ReAct 7 Tool) + 프론트(지도 연동) + 데이터 파이프라인(ETL 약 14.6만 건)을 한 프로젝트 안에서 전부.
- **환각을 줄이는 정확성 설계:** 그냥 LLM을 부르는 게 아니라, Entity Linking과 Abstention으로 "믿고 쓸 수 있게" 만든 점.
- **테스트로 품질을 보증:** E2E 66/66 + 프로덕션 스모크 28/28.

> 이 프로젝트는 "Tell me about a side project" 또는 "혼자서 뭔가를 끝까지 만들어 본 경험"에 꺼내는 카드입니다. Project 05가 "운영 규모"의 카드라면, 이건 **"혼자, 0에서 1까지, 실제 배포까지"**의 카드입니다.

---

## 1. 생각 구조 (5-Beat skeleton, 이 프로젝트 버전)

| Beat | 이 프로젝트에서 말할 내용 |
|------|---------------------------|
| **1 Headline** | 지도에서 상권을 고르고 자연어로 물으면 AI가 분석해 주는 SaaS를 혼자 만들어 실제 운영 중 |
| **2 Problem** | 기존 상권분석 서비스(Openup 등)는 정적 대시보드 + 수동 필터 → 사용자가 직접 지표를 찾아 비교해야 함. 소상공인에겐 너무 번거로움 |
| **3 Decision** | 핵심 결정은 "대화형"으로. LangGraph **ReAct 에이전트**가 7종 Tool을 스스로 골라 엮어 복합 질의를 실시간 분석 |
| **4 Hard Part** | (1) 신뢰성 — Entity Linking + Abstention으로 환각 차단 (2) 지도↔챗봇 양방향 동기화. 게다가 이 전부를 혼자 |
| **5 Result** | 프로덕션 라이브 v0.4.0, 서울 1,650개 상권 / 약 14.6만 건, ReAct 7 Tool, E2E 66/66 + 스모크 28/28 |

> 핵심 메시지 한 줄: **"It's one person taking an AI product all the way — from the map UI down to the data pipeline and the infra — and actually shipping it to production."**

---

## 2. 모범답안 (Model Answers)

### 🟢 Version A — Elevator (약 30초, 쉬운 영어)

> In short, I built **MarketScope AI** — a live web service that analyzes commercial districts with AI. It's a side project, and I built the whole thing by myself. You pick an area on the map — say, Gangnam Station — and just ask in plain language, like "How would a cafe do here?" The AI reads the real data and answers in seconds, right on the map. Most tools out there just show you a static dashboard and make you dig through the numbers yourself. Mine does the thinking for you. And it's **live in production** right now, with real data for about **1,650** commercial districts in Seoul.

> **핵심 표현**
> - "I built the whole thing by myself" = 전부 혼자 만들었다 (solo 강조)
> - "in plain language" = 평범한 말로 = 자연어로
> - "does the thinking for you" = 대신 생각해 준다
> - "live in production" = 실제 운영 중인
> **전달 팁:** "by myself"와 "1,650"에서 또박또박 멈추세요. 사이드 프로젝트의 힘은 "혼자 끝까지"입니다.

---

### 🟡 Version B — Standard (약 75초, 자연스러운 영어) ← 기본값

> So, MarketScope AI is a **map-based commercial-district analysis** service — basically, an AI that helps small business owners and real estate investors size up a neighborhood before they commit. It's a **solo side project**: I did everything myself, from the planning and the UI down to the backend, the AI agent, and the infra. And it's live in production.
>
> The problem I started with is that the existing tools — like the public ones in Korea — give you a static dashboard and a pile of manual filters. You have to know which metric to look at, find it, and compare it yourself. For a regular shop owner, that's just too much work.
>
> So the **key decision** was to make it conversational. You select a district on the map and ask something like "How are cafe sales trending at Gangnam Station?" or "Compare it with Hongdae," and the AI analyzes it in real time. Under the hood, that's a **LangGraph ReAct agent** — it reasons, picks the right tool, looks at the result, and repeats. I gave it **seven tools** — foot traffic, sales, stores, district comparison, and so on — and it chains them automatically. So "should I open a cafe here?" becomes sales, then stores, then a recommendation, fused into one answer.
>
> The **hardest part** was trust. An AI that confidently makes up numbers is worse than no AI. So I added two things: **entity linking**, which maps messy district names — abbreviations, typos — to the right area, and **abstention**, where if a tool fails or comes back empty, the AI says it doesn't have the data instead of guessing.
>
> And it **shipped** — it's live at version 0.4.0, with real data for about **1,650** districts in Seoul, roughly **146,000** records. I also kept it tested end to end: **66 out of 66** E2E tests pass, plus 28 smoke tests against production. So the whole thing — agent, map, data pipeline — actually runs, by myself, in production.

> **핵심 표현**
> - "solo side project" = 1인 사이드 프로젝트
> - "from the planning ... down to the infra" = 기획부터 인프라까지 (전 영역 오너십)
> - "make it conversational" = 대화형으로 만들다
> - "under the hood" = 내부적으로는 (구현 관점 진입 표현)
> - "chains them automatically" = (도구를) 자동으로 엮는다
> - "confidently makes up numbers" = 자신 있게 숫자를 지어낸다 (= 환각)
> - "it shipped" = 출시했다 / 배포를 끝냈다
> **전달 팁:** Problem-Decision-Hard part-Result 네 군데에서 잠깐씩 멈추세요. 마지막 "by myself, in production"은 자신 있게.

---

### 🔴 Version C — Deep Dive (약 2~3분, 고급 영어) ← "더 자세히" 요청 시

> Sure, let me go deeper — and since I built all of it, I can go top to bottom.
>
> The brief I set myself was simple: one person, end to end, and it has to actually ship and be trustworthy enough that a shop owner would act on it.
>
> The core is the AI chat. It's a **LangGraph ReAct agent** — reason, act, observe, looping up to **five** times — running on the **Claude API with tool use**, prompted to behave like a Korean commercial-district consultant. I gave it **seven tools**: foot traffic, sales, stores, district comparison, industry recommendation, risk, and population. The agent picks and chains them on its own. So "how about a cafe at Gangnam Station?" turns into a sales call, then a stores call, then a recommendation, fused into one narrative answer.
>
> The detail I'm most proud of is the **accuracy layer**, because that's where most of these things fall apart. The single biggest failure was users typing district names that don't match the database — abbreviations, nicknames, typos. So I built **entity linking**: prefix and trigram matching against the canonical names, backed by a **learning alias table** that remembers past resolutions, so the system absorbs messy input over time. And I paired it with **abstention** — if a tool fails or returns nothing, the agent explicitly says it doesn't have that data instead of inventing a number. For an analysis product, a confident wrong answer is the worst thing you can ship, so I designed for "I don't know" on purpose.
>
> On the front end, it's Next.js with **Kakao Map** for Korean map accuracy and **deck.gl** for fast heatmap and polygon rendering. The map and the chat are wired both ways through a **Zustand** store: clicking a polygon kicks off analysis, and the AI's response carries **map_cmd** events that move, zoom, and highlight the map back. The answers render as rich cards — summary, compare, recommend, risk — with inline Recharts charts, and the whole thing streams over **FastAPI server-sent events**, so you watch the agent think — thinking, tool, text, card, done — in real time.
>
> Underneath, there's a data pipeline: an **ETL** that pulls four Seoul open-data services plus the shapefile polygons every quarter — about **146,000** records across **1,650** districts — into Postgres with PostGIS. I used a **repository pattern**, so a single environment variable, USE_MOCK, flips the whole app between a database-less mock mode and real data — which is also what keeps the tests fast. And I wired up **Langfuse** for tracing, with user feedback fed back into the trace scores so I can improve on real usage.
>
> And it's all verified — Playwright scenarios from preflight to negative cases, **66 out of 66** E2E plus **28** production smoke tests. It's live right now at version 0.4.0.

> **핵심 표현 (고급)**
> - "top to bottom / end to end" = 처음부터 끝까지, 전 영역
> - "reason, act, observe, looping up to five times" = ReAct 루프를 영어로 푸는 법
> - "picks and chains them on its own" = 스스로 고르고 엮는다
> - "that's where most of these things fall apart" = 대개 거기서 무너진다
> - "a learning alias table that remembers past resolutions" = 과거 해석을 기억하는 학습형 별칭 테이블
> - "I designed for 'I don't know' on purpose" = 일부러 '모른다'를 설계에 넣었다
> - "wired both ways" = 양방향으로 연결했다
> - "server-sent events" = 서버가 밀어주는 실시간 스트리밍(SSE)
> - "flips the whole app ... with one environment variable" = 변수 하나로 모드 전환
> **전달 팁:** 길어서, 중간에 "Want me to zoom in on the agent side or the data side?"로 면접관 반응을 확인하세요. 한 번에 다 쏟지 마세요.

---

## 3. 꼬리질문 대비 (Follow-up Q&A)

**Q1. Why build this as a side project, and what did you learn doing it solo?**
> Honestly, I wanted to prove I could take something from an idea all the way to production by myself — not just the model, but the UI, the data pipeline, and the infra. Doing it solo forced real tradeoffs about scope: I shipped a mock mode first so I could test the whole flow before the data was ready, then swapped in real data. The biggest lesson was that the hard part of an AI product isn't the model call — it's everything around it: clean data, accurate entity resolution, and knowing when to say "I don't know."
> *(한국어 메모: "혼자 = 전 영역 오너십"으로 답하고, 배운 점은 "모델보다 그 주변이 어렵다"로 마무리. 성숙한 시니어 신호입니다.)*

**Q2. What's the business model?**
> It's **freemium**. The free tier gives you five analyses a day and a basic report — enough to try it and get value. The premium tier removes the limit and unlocks the deeper stuff: heatmaps, sales simulation, and PDF reports. The idea is that a curious shop owner starts free, and someone seriously scouting a location pays for the depth. The tier gating and the payments are the next phase I'm building.
> *(한국어 메모: 무료/프리미엄 경계를 구체적 기능으로. "진지한 사용자가 깊이에 돈을 낸다"는 가치 논리. Phase 2(결제·Tier 게이팅)가 진행 예정임을 덧붙이면 솔직하고 좋습니다.)*

**Q3. How is this different from existing tools like Openup?**
> The existing ones are static dashboards with manual filters — you have to know the metric, find it, and compare it yourself. Mine is conversational: you ask in one plain sentence, and the AI picks the data, runs the comparison, and visualizes it on the map for you. So it turns "go research this" into "just ask."
> *(한국어 메모: "정적 대시보드 + 수동 필터" vs "자연어 한 줄"을 대비. 차별점은 한 문장으로 압축하는 게 강합니다.)*

**Q4. How do you stop the AI from hallucinating numbers?**
> Two layers. **Entity linking** makes sure a messy district name maps to the right real area before any analysis runs — prefix and trigram matching plus a learning alias table. And **abstention**: if a tool fails or returns nothing, the agent says it doesn't have the data instead of guessing. For an analysis tool, a confident wrong number is the worst thing you can ship, so I designed for "I don't know" on purpose.
> *(한국어 메모: Entity Linking + Abstention 두 축. "오답보다 기권이 낫다"는 설계 철학을 분명히 말하세요.)*

**Q5. Why a ReAct agent with seven tools instead of one big prompt?**
> Because real questions are compound. "Should I open a cafe here?" isn't one lookup — it's sales, then stores, then a recommendation. A ReAct agent reasons about what it needs, calls the right tool, looks at the result, and decides the next step, up to five loops. One giant prompt can't fetch live data or pick its own path like that. The tools keep every answer grounded in actual records.
> *(한국어 메모: "복합 질의"가 핵심 이유. ReAct = 필요한 도구를 스스로 골라 엮음. 단일 프롬프트와 대비하면 설계 의도가 또렷합니다.)*

**Q6. How did you make sure it actually works in production?**
> I leaned on tests hard, since I was solo and couldn't eyeball everything. I have Playwright scenarios in rings — preflight, features, journeys, and negative cases — 66 out of 66 passing, plus 28 smoke tests that run against the live site. And because I can flip the app into mock mode with one environment variable, I can regression-test the whole flow without a database. That's how I keep shipping changes without breaking the live version.
> *(한국어 메모: "혼자라서 테스트에 의존"이 솔직하고 좋습니다. Ring 0-3, 66/66 + 스모크 28/28, USE_MOCK 회귀까지 묶어 품질 보증 신호로.)*

---

## 4. 핵심 표현·어휘 (Key phrases & vocabulary)

| English | 뜻 / 쓰임 |
|---------|-----------|
| commercial-district analysis | 상권 분석 (이 프로젝트의 도메인) |
| end to end / top to bottom | 처음부터 끝까지, 전 영역 |
| solo side project | 1인 사이드 프로젝트 |
| ship / it shipped / live in production | 출시하다 / 배포 완료 / 실제 운영 중 |
| make it conversational | 대화형으로 만들다 |
| ReAct agent | 추론-행동-관찰 루프 에이전트 |
| tool use / chain tools | 도구 호출 / 도구를 엮다 |
| entity linking | 지명 같은 엔티티를 정규화·매칭 |
| abstention | 모르면 기권 (추측하지 않음) |
| hallucinate / make up numbers | 환각하다 / 숫자를 지어내다 |
| under the hood | 내부적으로는 (구현 관점) |
| wired both ways / bidirectional sync | 양방향으로 연결 / 양방향 동기화 |
| server-sent events (SSE) | 서버가 밀어주는 실시간 스트리밍 |
| data pipeline / ETL | 데이터 수집·적재 파이프라인 |
| freemium / tier gating | 무료+유료 모델 / 등급별 기능 제한 |
| smoke test | 핵심 기능만 빠르게 점검하는 테스트 |

---

## 5. 발음 주의 (Delivery watch-outs)

| 단어 | 강세 / 주의 |
|------|-------------|
| commercial | kuh-MUR-shul |
| district | DIS-trikt (끝 -ct 끝까지) |
| conversational | kon-ver-SAY-shuh-nul |
| entity | EN-ti-tee |
| trigram | TRY-gram |
| abstention | ab-STEN-shun |
| hallucinate | huh-LOO-si-nayt |
| polygon | PAH-lee-gon |
| freemium | FREE-mee-um |
| Kakao | kuh-KOW (한 단어로 빠르게) |
| 1,650 | "one thousand six hundred fifty" (개수니까 또박또박) |
| 146,000 | "a hundred forty-six thousand" |
| v0.4.0 | "version zero point four point zero" |

> **마지막 점검:** 이 프로젝트의 힘은 **"혼자, 끝까지, 실제 배포"**입니다. "by myself", "end to end", "it shipped", "live in production" 네 표현을 자신 있게 던지세요.
