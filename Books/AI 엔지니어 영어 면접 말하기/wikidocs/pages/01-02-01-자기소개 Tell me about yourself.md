# 02. Self-Introduction — "Tell me about yourself"

> 면접의 첫 질문이자 가장 중요한 30~120초. 여기서 "차별점 한 줄 + 하나의 흐름(thread)"을 심으면,
> 이후 모든 프로젝트 질문이 그 흐름의 증거로 들립니다.

---

## 0. 자기소개로 증명할 것

- **차별점 한 줄:** "LLM을 만드는 사람"이 아니라 **"운영에 들어간 LLM의 품질을 규모 있게 검증하는 시스템까지 만드는 사람."**
- **하나의 흐름:** 임베딩-검색(석사 연구) → 서빙 → 에이전트 → 평가·운영 → 풀스택. 한 방향으로 깊어졌다.
- **일하는 방식:** 기술은 목적이 아니라 문제 해결의 도구. 비즈니스 가치 기준으로 우선순위를 잡는다.

---

## 1. 생각 구조 (Self-intro skeleton)

자기소개는 5-비트가 아니라 **Present → Thread → Proof → Fit** 4-비트로 갑니다.

| Beat | 한국어 | 시작 표현 (trigger) |
|------|--------|---------------------|
| **1 Present** | 지금의 나 + 차별점 한 줄 | "I'm a Gen-AI engineer with about four years ... What sets me apart is ..." |
| **2 Thread** | 어떻게 여기까지 왔나 (하나의 줄기) | "I actually started from ___, and kept going deeper in one direction ..." |
| **3 Proof** | 대표 성과 1~2개 (숫자) | "Most recently, I ___." |
| **4 Fit** | 무엇을 찾고 있나 / 왜 여기 | "Now I'm looking for a role where ___." |

> 핵심 원칙: **이력서를 시간순으로 읊지 마세요.** 회사 8개 나열 = 실패. "하나의 줄기 + 대표 증거"만.
> 길이는 **90초 이내**. 길면 면접관이 흥미를 잃습니다.

---

## 2. 모범답안 (Model Answers)

### 🟢 Version A — Elevator (약 30초, 쉬운 영어)

> I'm a Gen-AI and ML engineer with around **four years** of experience, mostly in LLM systems and search. What makes me a bit different is that I don't just build models — I build the systems that **check whether they actually work in production**. For example, I recently built a pipeline that evaluated about **600,000** production LLM outputs automatically, with no human review. Right now, I'm looking for a role where I can keep working on real, production-grade AI systems **end to end**.

> **핵심 표현**
> - "What makes me a bit different is ..." = 제 차별점은 ~ (자기소개 황금 문장)
> - "I don't just build models — I build the systems that ..." = 모델만 만드는 게 아니라 ~하는 시스템까지
> - "end to end" = 처음부터 끝까지 (전 구간)
> **전달 팁:** 첫 문장은 외워서 **자신 있게**. 첫인상이 여기서 결정됩니다. "600,000"에서 또박또박.

---

### 🟡 Version B — Standard (약 80초, 자연스러운 영어) ← 기본값

> Sure. I'm a Gen-AI and ML engineer with about **four years** of experience. If I had to sum up what sets me apart, it's this: I don't stop at building an LLM — I build the systems that **verify its quality at scale once it's running in production**.
>
> I actually started from **recommendation and search**. My master's research was on embedding-based recommendation — turning user preferences into vectors and finding items by similarity — and I kept deepening in that one direction ever since. That took me from **vector search** services, to **serving** our own LLMs in-house, to **agent** systems, and most recently to **LLM evaluation and operations**.
>
> A couple of results I'm proud of: I built an evaluation pipeline that judged around **600,000** production summaries with no human review, and I fine-tuned a smishing-detection model that took the F1 score from **28 percent up to 96**. On the side, I also built and shipped a full-stack AI SaaS that's **live in production**.
>
> So I've touched the whole pipeline — collection, search, serving, generation, and evaluation. Now I'm looking for a team where I can keep working on production AI systems **end to end**, and go deeper on the operations side.

> **핵심 표현**
> - "If I had to sum up what sets me apart, it's this: ..." = 차별점을 한마디로 하면
> - "I kept deepening in that one direction" = 한 방향으로 계속 깊어졌다
> - "a couple of results I'm proud of" = 자랑스러운 결과 몇 가지
> - "I've touched the whole pipeline" = 전 구간을 다뤄봤다
> **전달 팁:** Thread 비트("started from ... kept deepening")에서 손으로 단계를 그리듯 천천히. 흐름이 들리게.

---

### 🔴 Version C — Deep Dive (약 2분, 고급 영어) ← "조금 더 자세히 소개해달라" 시

> Of course. I'm a Gen-AI and ML engineer with about four years of experience, and the thread that ties my whole career together is **embeddings and search** — it just kept evolving into bigger problems.
>
> It started in grad school at **UNIST**, where my master's thesis was a recommendation system built on a convolutional autoencoder — representing user preferences as **latent vectors** and recommending by vector similarity. That idea became the foundation for everything after. At my first company, I turned it into real services: a movie recommender on **pgvector**, and then a travel chatbot for the Busan tourism office that's **still live in production** today.
>
> At my current company, I pushed further down the stack. I moved our text processing off external APIs by **serving our own LLM in-process** — that cut external API cost by a hundred percent and dropped latency by about **65 percent**. I built an **agentic RAG** system with hybrid search that improved Top-5 recall by around **35 percent**, and a self-improving **Reflexion** agent that learns from its own failures, which cut repeated retries by about **55 percent**. I also fine-tuned a **smishing detector** that took real-world F1 from **28 percent to over 95**.
>
> But the project that best captures what I care about is the most recent one: an **evaluation pipeline** that scored around **600,000** production LLM summaries with no human in the loop. The challenge was cost — so I compressed five quality criteria into a single judge call, about a **fifth** of the cost, while keeping quality. That's the part of me that's a bit different: I care as much about **knowing an LLM is good in production** as about building it.
>
> Outside work, I built a full-stack AI SaaS solo, from planning to infrastructure, and shipped it live. So at this point I've worked across the entire pipeline. The way I work is simple: I treat technology as a **tool for solving a real problem**, not as the goal — I start from the user's pain and the business value, then pick the approach. And I'm looking for a team where I can keep doing exactly that, end to end.

> **핵심 표현 (고급)**
> - "the thread that ties my whole career together is ___" = 제 커리어 전체를 관통하는 줄기는 ~
> - "I pushed further down the stack" = 스택을 더 깊이 파고들었다
> - "with no human in the loop" = 사람이 개입하지 않고
> - "the project that best captures what I care about" = 제가 중시하는 걸 가장 잘 보여주는 프로젝트
> - "a tool for solving a real problem, not the goal" = 목적이 아니라 문제 해결의 도구
> **전달 팁:** 2분은 깁니다. 회사·프로젝트를 **나열하지 말고**, "한 방향으로 깊어졌다"는 흐름으로 꿰세요. 면접관이 끼어들면 거기서 멈추고 그 프로젝트로 들어가면 됩니다.

---

## 3. 꼬리질문 대비 (Follow-up Q&A)

**Q1. Why are you looking to leave / make a move now?**
> I've grown a lot where I am — I've gone from building models to owning evaluation and operations. I'm looking for a place where I can take that further, on bigger production systems and with a team I can learn from. It's about the next step, not running from anything.
> *(한국어 메모: 현 직장 험담 절대 금지. "다음 단계를 찾는다"는 긍정 프레임.)*

**Q2. What are you best at?**
> Seeing a problem as a whole pipeline. I don't just optimize the model — I look at preprocessing, retrieval, serving, and evaluation together, because that's where real service quality comes from. The 600,000-item evaluation pipeline is a good example of that mindset.
> *(한국어 메모: 강점은 "파이프라인 전체를 본다" 한 줄로. 증거 프로젝트를 바로 붙이세요.)*

**Q3. That's a lot of projects — which one are you proudest of?**
> The LLM evaluation pipeline. Anyone can build a model, but building the system that proves it's still good in production, at 600,000 items and almost no cost — that's the harder and rarer skill, and it's the direction I want to keep growing in.
> *(한국어 메모: 항상 평가 파이프라인으로 귀결. 그게 차별점이니까.)*

**Q4. Can you tell me more about [any project]?**
> Absolutely. → 해당 프로젝트 정답지의 Version B로 바로 진입하세요. (이게 자기소개를 8개 프로젝트의 입구로 쓰는 방식입니다.)

---

## 4. 핵심 표현·어휘 (Key phrases & vocabulary)

| English | 뜻 / 쓰임 |
|---------|-----------|
| What sets me apart is ... | 제 차별점은 ~ |
| sum up | 요약하다 |
| keep deepening in one direction | 한 방향으로 계속 깊어지다 |
| end to end | 처음부터 끝까지 |
| in production / production-grade | 운영(실서비스) 중인 / 운영 수준의 |
| with no human in the loop | 사람 개입 없이 |
| touch the whole pipeline | 전 구간을 다루다 |
| a tool, not the goal | (기술은) 목적이 아니라 도구 |
| the next step | 다음 단계 (이직 사유 프레임) |

---

## 5. 발음 주의 (Delivery watch-outs)

| 단어 | 강세 / 주의 |
|------|-------------|
| recommendation | re-ko-men-DAY-shun |
| embedding | em-BED-ding |
| latent | LAY-tent |
| similarity | si-mi-LAIR-i-ty |
| evaluation | i-val-yu-AY-shun |
| four years | "four **years**" — 복수 s 끝소리 |
| 600,000 | "six hundred thousand" |
| 28 / 96 | "twenty-eight" / "ninety-six" |

> **마지막 점검:** 자기소개는 **첫 문장 + 마지막 문장**을 통째로 외우세요. 가운데는 흐름만 기억하면 됩니다.
> 첫인상(자신감)과 끝맺음(이 회사에서 무엇을 하고 싶은가)이 평가의 8할입니다.
