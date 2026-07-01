# Project 07 — Skylife Movie Recommendation System

> **한 줄:** Skylife 위성방송 가입자에게 선호 장르·배우로 유사 영화를 추천하는 API. pgvector 2단계 추천(메타 필터 → 벡터 유사도)으로 추천 다양성을 끌어올림.
> **헤드라인:** pgvector 2단계 추천 · 추천 다양성(diversity) 개선 · 이후 벡터 검색 프로젝트들의 토대(석사 연구 → 실서비스 첫 구현).
> 소속 AIO2O · 2023.06~2023.12 · 4명 팀 · AI 파트(벡터 DB 설계·추천 알고리즘 개발) 전담.

---

## 0. 이 프로젝트로 증명할 것 (What this proves about you)

- **"연구를 실서비스로 옮기는 사람."** 석사 논문(Convolutional Autoencoder 기반 추천)의 아이디어를 처음으로 실제 가입자용 API로 구현한 출발점. ← 이 프로젝트의 가장 강한 서사.
- **문제를 다른 패러다임으로 환원하는 사고:** rule-based의 "늘 비슷한 결과" 한계를 벡터 유사도라는 전혀 다른 접근으로 해결.
- **토대를 만드는 사람:** 여기서 만든 2단계 추천(필터 → 벡터 유사도)이 이후 Visit Busan 챗봇 등 모든 벡터 검색 프로젝트의 뼈대가 됨.

> 이 프로젝트는 **숫자가 아니라 '서사'로 미는 카드**입니다. "Where did your vector / RAG work begin?" 또는 "어떻게 추천 시스템에 발을 들였나"에 이걸 꺼내세요. 무리해서 지표를 만들지 말고, **출발점 → 확장**의 이야기로 끌고 가세요.

---

## 1. 생각 구조 (5-Beat skeleton, 이 프로젝트 버전)

| Beat | 이 프로젝트에서 말할 내용 |
|------|---------------------------|
| **1 Headline** | Skylife 가입자용 영화 추천 API를 만들었다 — pgvector로 추천을 2단계로 재설계 |
| **2 Problem** | 기존엔 메타 필터·rule-based 로직만 사용 → 같은 조건이면 늘 비슷한 결과가 반복됨. 다양성이 없었다 |
| **3 Decision** | 영화 메타(장르·줄거리·감독·배우)를 임베딩해 pgvector에 저장. 추천을 2단계로 분리 — ① 메타 필터로 후보 축소 ② 설명 벡터 유사도로 순위 |
| **4 Hard Part** | rule-based의 경직성을 벡터로 어떻게 깨나 + 필터(제약)와 유사도(다양성)를 어떻게 한 파이프라인에 결합하나 |
| **5 Result** | 같은 조건에서도 유사하되 새로운 영화가 추천됨 → 다양성 개선. 이 2단계 알고리즘이 이후 Visit Busan 챗봇으로 확장됨 |

> 핵심 메시지 한 줄: **"This is where my master's research on embedding-based recommendation became a real product — and the two-stage design became the foundation for everything I built with vectors afterward."**

---

## 2. 모범답안 (Model Answers)

### 🟢 Version A — Elevator (약 30초, 쉬운 영어)

> In short, I built a movie recommendation API for Skylife, a satellite TV service. A subscriber tells us their favorite genres and actors, and we recommend similar movies. The old system only used simple filters and fixed rules, so it kept suggesting the same kinds of movies. I changed that. I turned each movie's information — its genre, plot, director, and cast — into a vector and stored it in Postgres with **pgvector**. Then I made the recommendation work in **two steps**: first, narrow down the candidates with a filter, then rank them by how similar the movie descriptions are. The result was more variety — for the same request, people got movies that were similar but still fresh. And that two-step design ended up being the base for a lot of my later work.

> **핵심 표현**
> - "the same kinds of movies" = 비슷비슷한 영화들 (반복 문제를 쉽게 표현)
> - "turn A into a vector" = A를 벡터로 바꾸다 (= embed)
> - "in two steps: first ..., then ..." = 2단계로: 먼저 ~, 그다음 ~
> - "similar but still fresh" = 비슷하지만 그래도 새로운 (다양성을 쉬운 말로)
> **전달 팁:** "two steps", "pgvector", "fresh"에서 또박또박. 숫자가 없는 프로젝트라 **'바뀐 점'(반복 → 다양성)**을 또렷이 대비시키는 게 힘입니다.

---

### 🟡 Version B — Standard (약 75초, 자연스러운 영어) ← 기본값

> So this was a movie recommendation system for Skylife, a satellite broadcaster. I was on the **AI side** — on a team of four, I designed the vector database and built the recommendation logic.
>
> Before this, the recommendations ran purely on **metadata filters and rule-based logic**. The problem was that under the same conditions, it kept returning the same kind of results — the variety just wasn't there. So we were asked to improve the recommendation quality.
>
> The **key decision** was to bring in **vector similarity**. I took each movie's metadata — genre, plot summary, director, and cast — embedded it, and stored it in **PostgreSQL using pgvector**. Then I split the recommendation into **two stages**: first, a metadata filter to narrow down the candidate pool, and then vector similarity on the movie descriptions to actually rank them.
>
> That two-stage design was the important part. The filter keeps the results **relevant**, and the similarity step brings in **diversity** — so even for the same request, you get movies that are close but still new. We also **containerized** the API with Docker, so dev, staging, and production stayed identical.
>
> The part I like most is where this came from. My master's research was on an embedding-based recommender, and this was the first time I put that idea into a real service. The same two-stage approach later grew into our **Visit Busan** travel chatbot.

> **핵심 표현**
> - "ran purely on ... rule-based logic" = 오로지 규칙 기반으로 돌아갔다
> - "bring in vector similarity" = 벡터 유사도를 도입하다
> - "narrow down the candidate pool" = 후보군을 좁히다 (1단계)
> - "keeps it relevant ... brings in diversity" = 관련성은 지키고 다양성은 더한다 (2단계의 핵심 대비)
> - "put that idea into a real service" = 그 아이디어를 실서비스로 옮기다
> **전달 팁:** Problem → Decision → Result 사이에서 0.5초씩 끊으세요. 마지막 문장(석사 연구 → Visit Busan)이 이 답변의 **클로징 펀치**이니 서두르지 말 것.

---

### 🔴 Version C — Deep Dive (약 2~3분, 고급 영어) ← "더 자세히" 요청 시

> Sure, let me go a bit deeper on the design.
>
> The starting point was actually a limitation I'd thought about during my master's. My thesis was a recommender built on a **convolutional autoencoder** — the idea was to compress a user's preferences into a **latent vector** and then recommend by vector similarity. Skylife was the first time I got to take that idea out of research and put it into a production service.
>
> The problem on the ground was concrete. The existing API recommended movies with **metadata filters and rule-based logic only**. That's fine for relevance, but it's rigid — for the same genre-and-actor input, you'd get more or less the same list every time. There was no notion of "close, but different."
>
> So the core of my design was a **two-stage pipeline**. In the first stage, I use the metadata filter as a **hard constraint** — genre, cast, and so on — to cut the catalog down to a sensible candidate set. In the second stage, I rank those candidates by **vector similarity**. To do that, I embedded the semantic side of each movie — genre, plot summary, director, cast — and stored those embeddings in **PostgreSQL with the pgvector extension**, so the similarity search runs right in the database, next to the data.
>
> The reason it's two stages and not one is the real insight. If you only filter, you get relevance but no diversity — same rules, same results. If you only do vector similarity, you get diversity but you can **drift** past the user's hard requirements. Splitting it lets the filter guarantee the constraints while the similarity step introduces variety — movies that are semantically close to what they like, but not the identical list they've already seen. That's how I improved the recommendation **diversity** without giving up relevance.
>
> On the delivery side, I **containerized** the API server with Docker. The Dockerfile pinned the environment, so development, staging, and production were identical — no "works on my machine" surprises.
>
> And the part I find satisfying is the through-line. That two-stage shape — a cheap filter to narrow, then vector similarity to rank — turned out to be reusable. It became the backbone of our **Visit Busan** travel chatbot later on, and really of every vector-search project I touched after this. Skylife was where it started.

> **핵심 표현 (고급)**
> - "compress preferences into a latent vector" = 선호를 잠재 벡터로 압축
> - "take it out of research into production" = 연구에서 실서비스로 옮기다
> - "hard constraint" = 하드 제약 (반드시 지켜야 하는 조건)
> - "drift past the user's hard requirements" = 사용자의 필수 조건을 벗어나 표류하다
> - "runs right in the database, next to the data" = DB 안에서, 데이터 바로 옆에서 돈다
> - "the through-line / the backbone" = 관통하는 줄기 / 뼈대
> **전달 팁:** 이 버전은 길어서 "the reason it's two stages and not one is the real insight"가 **하이라이트**입니다. 거기서 한 박자 쉬고 또박또박. 끝에 "Want me to go further on any part?"로 점검하면 자연스럽습니다.

---

## 3. 꼬리질문 대비 (Follow-up Q&A)

**Q1. Why two stages? Why not just do vector similarity over the whole catalog?**
> Because each stage solves a different problem. Pure vector similarity can **drift** — it might rank a movie that's semantically close but breaks a hard requirement, like the wrong genre. Pure filtering is safe but gives you no variety. So I let the filter handle the hard constraints first, then let similarity bring diversity **within** that safe set. You get relevance and freshness at the same time.
> *(한국어 메모: "각 단계가 다른 문제를 푼다 — 필터 = 제약, 벡터 = 다양성"으로 답하면 설계 의도가 분명해집니다.)*

**Q2. You say diversity improved — how did you measure it?**
> Honestly, I didn't have a formal offline diversity metric on this project — it was an early build. The signal was **qualitative**: for the same input, the old system returned essentially the same list, and the new one returned movies that were similar in feel but not the same titles. If I built it again, I'd track something like intra-list diversity or coverage so the claim is quantitative. But the direction of the change was clear.
> *(한국어 메모: 숫자가 없으니 솔직하게. "정성적이었다 + 다시 하면 이렇게 측정하겠다"가 가장 성숙한 답입니다. 절대 지표를 지어내지 마세요.)*

**Q3. Why pgvector instead of a dedicated vector database?**
> I keep the movie metadata and the embeddings together in **PostgreSQL**, so pgvector lets the filter and the similarity search happen in **one place** — no separate vector service to run or keep in sync. For the scale of a movie catalog, that was the simpler, more maintainable choice. A dedicated vector DB makes more sense once you outgrow that.
> *(한국어 메모: "데이터가 한곳에 있다 + 동기화할 별도 서비스 불필요 + 규모에 맞는 단순함" — 트레이드오프로 답하세요.)*

**Q4. What exactly did you embed — the whole movie?**
> The **semantic** parts — genre, plot summary, director, and cast. Those carry the "what this movie is actually about" signal, which is what you want similarity to capture. The harder categorical conditions stayed in the filter stage. So the two stages also split the data cleanly: structured fields for filtering, descriptive content for the embedding.
> *(한국어 메모: 임베딩 대상 = 장르·줄거리·감독·배우. "의미 신호는 벡터로, 범주 제약은 필터로" 분리한다고 답.)*

**Q5. Where did this project lead? How does it connect to your other work?**
> This was the **foundation**. The two-stage pattern — narrow with a cheap filter, then rank by vector similarity — became a template I reused. It grew into our **Visit Busan** travel chatbot, and it shaped how I approached every vector-search and retrieval problem after that. It also closed a loop for me personally, because it started as my master's research on embedding-based recommendation.
> *(한국어 메모: "출발점 → Visit Busan으로 확장 → 석사 연구와 연결"의 서사. 이 프로젝트의 핵심 카드이니 자신 있게.)*

**Q6. What would you do differently next time?**
> Two things. I'd add a real **diversity metric** up front, so I could prove the improvement instead of just describing it. And I'd experiment with how the two stages interact — for example, tuning how many candidates the filter passes to the ranking step, since that knob trades off relevance against variety. The core design held up well, though — that's exactly why it carried into later projects.
> *(한국어 메모: "다양성 지표 추가 + 필터 → 랭킹 후보 수 튜닝"으로 약점을 개선안으로 전환.)*

---

## 4. 핵심 표현·어휘 (Key phrases & vocabulary)

| English | 뜻 / 쓰임 |
|---------|-----------|
| recommendation system / recommender | 추천 시스템 |
| two-stage pipeline | 2단계 파이프라인 (필터 → 랭킹) |
| metadata filter | 메타데이터 필터 (1단계: 후보 축소) |
| vector similarity | 벡터 유사도 (2단계: 순위 매김) |
| embedding / embed | 임베딩 / 임베딩하다 (텍스트를 벡터로) |
| candidate pool / candidate set | 후보군 |
| hard constraint | 하드 제약 (반드시 지켜야 하는 조건) |
| diversity | 다양성 (추천이 다채로움) |
| relevance | 관련성 (입력과 얼마나 맞나) |
| rule-based | 규칙 기반 |
| rigid | 경직된 (유연하지 않은) |
| drift | (제약을) 벗어나 표류하다 |
| containerize | 컨테이너화하다 (Docker로) |
| right next to the data | 데이터 바로 옆에서 (DB 내부에서) |
| the backbone / the foundation | 뼈대 / 토대 |
| take it out of research into production | 연구를 실서비스로 옮기다 |

---

## 5. 발음 주의 (Delivery watch-outs)

| 단어 | 강세 / 주의 |
|------|-------------|
| recommendation | rek-uh-men-DAY-shun |
| pgvector | "P-G-vector" (피지-벡터). v를 b로 새지 않기 |
| PostgreSQL | "POST-gres" 로 줄여 말해도 됨 |
| similarity | sim-uh-LAIR-uh-tee |
| diversity | dy-VER-suh-tee |
| genre | "ZHAHN-ruh" (장르) — 첫소리는 j가 아니라 부드러운 '쥬' 소리 |
| vector | VEK-ter. v를 b로 새지 않기 |
| embedding | em-BED-ding |
| metadata | MET-uh-day-tuh |
| autoencoder | AW-toh-en-KOH-der |
| catalog | KAT-uh-log |
| Docker | DOK-er |

> **마지막 점검:** 이 프로젝트는 숫자가 아니라 **'서사'**로 미는 카드입니다. "My vector work started here" — 출발점에서 시작해 Visit Busan으로 확장됐다는 줄기를, 천천히 자신 있게.
