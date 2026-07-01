# Project 06 — Visit Busan Travel Scheduling Chatbot

> **한 줄:** 부산관광공사 공식 사이트에 탑재된 AI 여행 챗봇 — 자연어로 여행 조건을 말하면 관광지를 추천하고 일정까지 자동 구성한다.
> **헤드라인:** 부산관광공사 공식 사이트에 **상용 운영 중 (live in production)** · 5명 팀 AI 리드 · 자연어 추천 + 자동 일정 구성.
> 소속 AIO2O · 2024.01~2024.10 · 5명 팀 · AI 파트 리드 (벡터 DB 구축 / 추천 알고리즘 / 챗봇 개발) 전담.

---

## 0. 이 프로젝트로 증명할 것 (What this proves about you)

- **"데모를 만드는 사람"이 아니라 "공공기관에서 상용 운영되는 서비스를 리드한 사람."** ← 이 프로젝트의 가장 강한 카드. 숫자 지표가 없어도 "live in production on a public institution's official site"가 그 자체로 신뢰입니다.
- 비기술 이해관계자(관광공사 데이터팀 · 기획자)와 협업하고 **MVP 범위를 협의**하는 능력 — 2주 데모 사이클로 피드백을 흡수.
- 도메인 적용력: 리뷰 텍스트(긍·부정 키워드 · 해시태그)를 벡터에 녹여, 키워드 검색을 **의미 기반 검색**으로 바꾼 점.
- 배포까지 책임지는 오너십: Docker Compose 컨테이너화 + .env 환경 분리 + 배포 자동화.

> 이 프로젝트의 카드는 "**숫자**"가 아니라 "**실제로 쓰이는 제품**"입니다. "Tell me about something you shipped" 또는 협업·오너십을 묻는 질문에 꺼내세요.

---

## 1. 생각 구조 (5-Beat skeleton, 이 프로젝트 버전)

| Beat | 이 프로젝트에서 말할 내용 |
|------|---------------------------|
| **1 Headline** | 부산관광공사 공식 사이트에 상용 운영 중인 AI 여행 챗봇의 AI 파트를 리드했다 (자연어 추천 + 자동 일정 구성) |
| **2 Problem** | 기존 검색은 "도시 / 1박 2일 / 맛집" 같은 고정 필터뿐 → "아이랑 갈 조용한 곳" 같은 자연어엔 대응 불가 |
| **3 Decision** | 영화 추천에서 쓰던 2단계(메타 필터 → 벡터 유사도)를 여행에 적용. 리뷰의 긍·부정 키워드·해시태그를 벡터에 녹여 의미 기반 검색으로 |
| **4 Hard Part** | 비기술 이해관계자(데이터팀·기획자)와 스키마·범위 조율 + 배포. → 2주 데모 사이클 + Docker Compose/.env |
| **5 Result** | 공식 사이트에 상용 배포(live in production). 5명 팀 AI 리드로 벡터 DB·추천·챗봇 전부 오너십 |

> 핵심 메시지 한 줄: **"The whole project was about turning a plain-language travel wish into a real itinerary — and actually shipping it live on a public tourism site."**

---

## 2. 모범답안 (Model Answers)

### 🟢 Version A — Elevator (약 30초, 쉬운 영어)

> In short, I led the AI part of a travel chatbot that's now **live** on Busan's official tourism website. You just type what kind of trip you want — in plain language, like "a quiet place I can visit with my kids" — and it recommends real spots and builds a full schedule for you. The old search only had fixed filters, like city and number of days, so it couldn't handle a request like that. The trick was that we pulled keywords and hashtags out of user reviews and used them to match by **meaning**, not just keywords. I was the AI lead on a team of five, and the best part is — it's a real product people actually use, not just a demo.

> **핵심 표현**
> - "live on ... website" = (사이트에) 상용 운영 중
> - "in plain language" = 평범한 말로, 자연어로
> - "match by meaning, not just keywords" = 키워드가 아니라 의미로 매칭
> - "not just a demo" = 데모가 아니라 (실제 제품)
> **전달 팁:** 숫자가 없는 답변이라, "**live**"와 "**not just a demo**"에 힘을 주세요. 이 두 표현이 신뢰를 만듭니다.

---

### 🟡 Version B — Standard (약 75초, 자연스러운 영어) ← 기본값

> So, this was an AI travel chatbot for the Busan Tourism Organization, and it's **live in production** on their official site right now. The idea is simple: you describe the trip you want in your own words, and it recommends attractions and builds the whole itinerary for you. Before this, their travel search was just **fixed filters** — pick a city, pick two days, pick "restaurants." So if someone typed something natural like "a quiet place I can go with my kids," the old system had nothing to match it against.
>
> So the **key decision** was to make the search **meaning-based** instead of keyword-based. I took a two-stage recommendation approach — first a **metadata filter** on things like region, number of nights, and category, and then a **vector similarity** search on top. The part I'm proud of is what went into that vector: I pulled positive and negative keywords and **hashtags** out of the user reviews and folded them into the embedding. So the system matches on what a place actually feels like, not just its name or its official tags.
>
> The hardest part wasn't really the model — it was working with **non-technical stakeholders**. I talked directly with the tourism organization's data team to line up the data schema and the update cycle, and I had to negotiate scope with the planner — between the itinerary logic they wanted and the recommendation quality we could realistically ship. We handled that by shipping a **demo every two weeks** and folding their feedback back in.
>
> In the end, it went **live in production** on the official Visit Busan site, and it still recommends spots and auto-builds itineraries from plain-language requests. I was the **AI lead** on a team of five, so I owned the vector database, the recommendation algorithm, and the chatbot itself. The takeaway for me was that the review-text trick — turning messy opinions into something searchable — was what actually made the recommendations feel relevant.

> **핵심 표현**
> - "live in production" = 상용 운영 중 (업계 표준 표현, 꼭 쓰세요)
> - "fixed filters" = 고정 필터
> - "meaning-based instead of keyword-based" = 의미 기반 vs 키워드 기반
> - "fold A into B" = A를 B에 녹여 넣다
> - "non-technical stakeholders" = 비기술 이해관계자
> - "ship a demo every two weeks" = 2주마다 데모를 내놓다
> **전달 팁:** Problem → Decision → Hard part 사이에서 0.5초씩 끊으면 구조가 또렷이 들립니다. "live in production"은 천천히, 또박또박.

---

### 🔴 Version C — Deep Dive (약 2~3분, 고급 영어) ← "더 자세히" 요청 시

> Sure, let me go a bit deeper, especially on the recommendation design.
>
> The starting point was an algorithm I'd actually built before. On an earlier project at the same company — a **movie** recommendation system — I'd designed a **two-stage** approach: a **metadata filter** to narrow the candidate set, then a **vector similarity** search to rank by meaning. For the travel chatbot, I adapted that same pattern to a completely different domain. The metadata stage filters on **region**, number of **nights**, and **category**, which cheaply cuts the space down to plausible places before any heavy similarity work runs.
>
> The interesting part is the vector itself. A travel spot isn't just its name and address — what people actually care about lives in the **reviews**. So instead of embedding only the official description, I **extracted positive and negative keywords and hashtags from the user reviews** and integrated them into the vector input. That's the one detail I'd highlight: a place that reviewers keep calling "quiet" or "good with kids" ends up **close in vector space** to a query that asks for exactly that — even if those words never appear in the official write-up. That's what turned it from keyword matching into genuine **semantic search**. And once a set of spots is selected, the system doesn't stop at a list — it **auto-composes them into a day-by-day itinerary**.
>
> The other half of the project was getting it into production with non-technical partners. I coordinated directly with the tourism organization's **data team** on the schema and the refresh cadence, and I negotiated the **MVP scope** with the planner — balancing the itinerary logic they wanted against the recommendation quality we could ship on time. We ran on a **two-week demo cycle** so feedback never piled up. For deployment, I containerized the **API server and the vector database** with **Docker Compose**, split the per-environment settings into **.env** files, and automated the deploy. The result is a real, **live product** on Busan's official tourism site — and as the AI lead on a five-person team, I owned that whole path, from the vector DB to the chatbot.

> **핵심 표현 (고급)**
> - "adapted that same pattern to a different domain" = 같은 패턴을 다른 도메인에 적용
> - "close in vector space" = 벡터 공간에서 가깝다
> - "semantic search" = 의미 기반 검색 (필수 용어)
> - "auto-compose them into an itinerary" = 그것들을 일정으로 자동 구성
> - "refresh cadence" = 갱신 주기
> - "negotiate the MVP scope" = MVP 범위를 협의하다
> - "per-environment settings" = 환경별 설정
> **전달 팁:** 길어서 중간에 "Want me to go deeper on the recommendation part?"로 호흡을 한 번 끊으면 좋습니다. itinerary 발음(eye-TIN-uh-rer-ee)만 미리 입에 붙여두세요.

---

## 3. 꼬리질문 대비 (Follow-up Q&A)

**Q1. Why two stages — why not just one vector search over everything?**
> Mostly efficiency and control. The metadata filter — region, nights, category — cheaply narrows the candidates to plausible places first, so the vector similarity step only runs on a small, relevant set. It also gives me a hard guarantee on the non-negotiable conditions; if someone says Busan for two nights, I don't want a semantically "similar" place in another city sneaking in. Meaning-based ranking is great, but some conditions should just be filters.
> *(한국어 메모: "효율 + 제약 보장" 두 축. 벡터가 만능이 아니라 필터로 보장할 건 보장한다는 게 시니어 신호.)*

**Q2. How did the review keywords actually improve the recommendations?**
> The official descriptions are written by the venue, so they're polished and all sound the same — "beautiful view, great experience." The real signal is in the reviews: whether a place is actually quiet, crowded, kid-friendly, hard to park at. By extracting positive and negative keywords and hashtags from those reviews and putting them into the vector, the system can match on how a place really feels, not just how it's marketed. That's the difference between matching the word and matching the meaning.
> *(한국어 메모: "공식 설명은 다 비슷하다 → 리뷰에 진짜 신호가 있다"는 통찰을 강조. 이 프로젝트의 핵심 기술 포인트.)*

**Q3. This sounds like your movie recommender. What did you have to change for travel?**
> The skeleton carried over — metadata filter, then vector similarity — but the domain was different in two ways. First, the metadata: a movie filters on things like genre, while travel filters on region, length of stay, and category. Second, and bigger, travel has to produce a **plan**, not just a ranked list. A good movie rec is one title; a good travel rec is several places arranged into a sensible day-by-day itinerary. So I added the itinerary-composition step on top of the ranking.
> *(한국어 메모: 재사용한 것(2단계 뼈대) vs 새로 만든 것(일정 구성)을 명확히 나눠 답하면 좋습니다.)*

**Q4. You mention non-technical stakeholders a lot. What was hard about that?**
> The hard part is that the planner and I optimize for different things. They want rich itinerary logic; I care about whether the recommendation quality holds up. Early on, those pull in different directions. What worked was making it concrete — instead of arguing in the abstract, we shipped a demo every two weeks, looked at real outputs together, and let that drive the scope. Once there's something to point at, "I want X" turns into "this specific result is off," which is much easier to act on.
> *(한국어 메모: 비기술 이해관계자와의 긴장을 "데모로 구체화해서 해소"한 점이 핵심. 추상 논쟁 → 구체 산출물.)*

**Q5. How did you deploy it, and how do you keep environments straight?**
> I containerized both the API server and the vector database with Docker Compose, so the whole stack comes up the same way everywhere. Environment-specific things — endpoints, credentials, and so on — live in **.env** files, so the same image runs in dev or in production just by swapping the env file. And the deploy itself is automated, so pushing a new version isn't a manual, error-prone ritual.
> *(한국어 메모: Docker Compose + .env 분리 + 배포 자동화, 이 3점만 또렷이.)*

**Q6. There's no headline metric here. How do you know it worked?**
> Honestly, I don't have a single headline number to quote here. But the strongest signal is that it's **live in production** on a public institution's official site and still running — a tourism organization doesn't put a chatbot on its front-facing site unless it clears their bar. The real validation was the bi-weekly demos with the client and the fact that it passed their review and shipped. If I did it again, I'd instrument click-through and itinerary completion from day one, so I'd have that number to point to.
> *(한국어 메모: 지표 없음을 솔직히 인정 + "상용 배포 자체가 검증" + "다음엔 지표 심겠다"가 성숙한 답. 절대 숫자를 지어내지 마세요.)*

---

## 4. 핵심 표현·어휘 (Key phrases & vocabulary)

| English | 뜻 / 쓰임 |
|---------|-----------|
| live in production | 상용 운영 중 (이 프로젝트의 헤드라인) |
| natural language | 자연어 (사람이 평소 쓰는 말) |
| fixed filters | 고정 필터 (도시·일수 같은 정해진 조건) |
| meaning-based / semantic search | 의미 기반 검색 |
| keyword matching | 키워드 매칭 (의미 검색의 반대편) |
| two-stage approach | 2단계 방식 |
| metadata filter | 메타데이터 필터 (1단계) |
| vector similarity | 벡터 유사도 (2단계) |
| embedding | 임베딩 (텍스트의 벡터 표현) |
| fold A into B | A를 B에 녹여 넣다 |
| close in vector space | 벡터 공간에서 가깝다 |
| auto-compose an itinerary | 일정을 자동 구성하다 |
| non-technical stakeholders | 비기술 이해관계자 |
| MVP scope | 최소 기능 범위 |
| refresh cadence / update cycle | 갱신 주기 |
| containerize | 컨테이너화하다 |
| AI lead / own the whole path | AI 파트 리드 / 전 과정을 책임지다 |

---

## 5. 발음 주의 (Delivery watch-outs)

| 단어 | 강세 / 주의 |
|------|-------------|
| itinerary | eye-TIN-uh-rer-ee — 강세 2번째 음절. 가장 자주 틀리는 단어 |
| vector | VEK-ter — V는 윗니로 아랫입술 (B로 새지 않기) |
| embedding | em-BED-ding |
| algorithm | AL-guh-ri-thum |
| semantic | si-MAN-tik |
| metadata | MET-uh-day-tuh |
| hashtag | HASH-tag — 끝 -g 까지 |
| stakeholder | STAYK-hohl-der |
| schema | SKEE-muh |
| production | pruh-DUK-shun |
| recommendation | rek-uh-men-DAY-shun |
| Busan | "BOO-san" — 또박또박 |

> **마지막 점검:** 이 프로젝트엔 자랑할 숫자가 없습니다. 대신 "**live in production**"과 "**official Busan tourism site**"를 또렷이, 자신 있게 말하세요. 그리고 itinerary(eye-TIN-uh-rer-ee) 발음만 미리 입에 붙여두면 끝입니다.
