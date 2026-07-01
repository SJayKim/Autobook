# Project 03 — Milvus-Based Agentic RAG System

> **한 줄:** 한국어 매거진 플랫폼의 기사를 의미 기반으로 검색하고, LlamaGuard로 안전한 답변을 생성하는 Agentic RAG 챗봇.
> **헤드라인 숫자:** Top-5 recall 약 35% 향상 · 15만 청크 중 12% 노이즈 제거 · 입력·출력 LlamaGuard 안전 검증.
> 소속 Plantynet · 2025.04~2025.12 · AI 파트 2명 · 검색 엔진 / 전처리 / 에이전트 전담.

---

## 0. 이 프로젝트로 증명할 것 (What this proves about you)

- **검색 품질을 모델이 아니라 "데이터부터" 끌어올린 엔지니어.** ← 가장 강한 차별점. 하이브리드 검색 설계 + 15만 청크 중 12% 노이즈 제거로 Top-5 recall 약 35% 향상.
- **생성형 AI의 안전성을 "설계"에 넣은 사람.** 입력과 출력 양쪽을 LlamaGuard로 검사하는 Safety Layer를 에이전트 흐름에 내장.
- **도구를 비교·선정하는 의사결정 능력.** Pinecone·Qdrant·Milvus를 명확한 기준(자체 호스팅 + 하이브리드 지원)으로 비교한 뒤 Milvus 선택.

> 이 프로젝트는 **"검색(retrieval)을 깊게 안다"**와 **"안전·운영까지 본다"**를 동시에 보여주는 카드입니다. RAG·LLM 직무에 가장 직접적으로 연결됩니다.

---

## 1. 생각 구조 (5-Beat skeleton, 이 프로젝트 버전)

| Beat | 이 프로젝트에서 말할 내용 |
|------|---------------------------|
| **1 Headline** | 한국어 매거진 플랫폼용 의미 기반 기사 검색 챗봇(Agentic RAG)을 만들었다 |
| **2 Problem** | 기존엔 키워드 매칭뿐 → "여름에 읽기 좋은 글" 같은 의미 질문에 무력. 생성 답변의 안전 검증 체계도 없었음 |
| **3 Decision** | Dense(BGE-M3) + BM25 하이브리드 검색 + reranker + 문맥 윈도우 설계. 벡터 DB는 비교 후 Milvus 선택(자체 호스팅·하이브리드) |
| **4 Hard Part** | 검색 품질을 데이터부터: 15만 청크 중 12% 노이즈 제거. 거기에 입출력 LlamaGuard 안전 레이어 |
| **5 Result** | Top-5 recall 약 35% 향상, 입출력 안전 검증, Docker Compose 3-tier 단일 명령 배포 |

> 핵심 메시지 한 줄: **"The whole project was about making search understand meaning, not just keywords — and making every answer safe by design."**

---

## 2. 모범답안 (Model Answers)

### 🟢 Version A — Elevator (약 30초, 쉬운 영어)

> In short, I built a search chatbot for a Korean magazine platform. Before this, the search only matched exact keywords, so a question like "a good article to read in summer" just didn't work — there's no keyword to match. So I built a **RAG** system that searches by meaning, not just words. I combined two kinds of search — meaning-based vectors and keyword-based **BM25** — and then re-ranked the results. That improved our **Top-5 recall** by about **35%** over keyword search. On top of that, I check both the question and the answer with a safety model called **LlamaGuard**, so unsafe content is blocked on both ends.

> **핵심 표현**
> - "only matched exact keywords" = 정확한 키워드만 매칭했다 (= 의미는 못 봄)
> - "searches by meaning, not just words" = 단어가 아니라 의미로 검색
> - "re-ranked the results" = 결과를 재정렬했다
> - "Top-5 recall by about 35%" = 상위 5개 재현율 약 35%
> - "blocked on both ends" = 입력·출력 양쪽에서 차단
> **전달 팁:** "about 35%"에서 또박또박 멈추세요. recall의 끝 -ll, both의 th 끝소리를 끝까지.

---

### 🟡 Version B — Standard (약 75초, 자연스러운 영어) ← 기본값

> So, this was an **Agentic RAG** project for a Korean magazine platform — basically a chatbot that finds articles from a natural-language question. Before this, search was pure **keyword matching**, so a semantic question like "a good article to read in summer" had nothing to match on. And there was no safety check on the AI's generated answers at all.
>
> So the **key decision** was the retrieval design. I built a **hybrid search**: dense vectors from **BGE-M3** for meaning, plus **BM25** sparse search for exact terms. Then I re-rank the merged results and pull in a **context window** — the chunks right before and after each hit — so the model has enough context to answer well. That took our **Top-5 recall** up about **35%** versus keyword search.
>
> For the vector database, I compared **Pinecone, Qdrant, and Milvus**, and went with **Milvus**, because I could self-host it and it supports hybrid search natively.
>
> The part I'm most proud of is that I pushed quality from the **data** side too. Out of about **150,000** chunks, I removed roughly **12%** as noise — things under 100 characters, junk special characters, or chunks that failed Korean tokenization. And for safety, every input and every output goes through **LlamaGuard**, so unsafe content is caught on both ends. The whole stack — Milvus, the FastAPI backend, and the Streamlit frontend — comes up with a single **Docker Compose** command.

> **핵심 표현**
> - "Agentic RAG" = 에이전트형 RAG (에이전트가 검색·생성 흐름을 제어)
> - "nothing to match on" = 매칭할 대상이 없다 (키워드 검색의 한계)
> - "hybrid search ... dense ... sparse" = 하이브리드 검색 (의미 벡터 + 키워드)
> - "context window" = 문맥 윈도우 (검색된 청크 앞뒤 문맥)
> - "compared A, B, and C, and went with ___" = 비교 후 선택 (의사결정 시그널, 꼭 쓰세요)
> - "pushed quality from the data side" = 데이터 단에서 품질을 끌어올림
> - "caught on both ends" = 양쪽 끝에서 잡힘
> **전달 팁:** 결정(hybrid)·DB 선택·데이터+안전, 세 군데에서 잠깐씩 멈추면 구조가 또렷이 들립니다.

---

### 🔴 Version C — Deep Dive (약 2~3분, 고급 영어) ← "더 자세히" 요청 시

> Sure, let me go a bit deeper on the design.
>
> The goal was an **agentic RAG** system for a Korean magazine platform: a user asks in natural language, and the agent retrieves the right articles and generates a safe answer. The old system only did **keyword matching**, so anything semantic — "a good article to read in summer" — fell through, because there's no literal keyword to hit. And generated answers had no safety validation at all.
>
> On retrieval, I designed a **hybrid** pipeline. Dense embeddings from **BGE-M3** capture meaning, **BM25** handles exact terms, and then **BGE-Reranker-v2-M3** re-orders the merged candidates. On top of that I add a **context window** — I pull the chunks immediately before and after each retrieved chunk, so the model sees enough surrounding text to answer well. That combination lifted **Top-5 recall** by about **35%** over pure keyword search. For magazine-level recommendations I used Milvus **Group Search** — instead of scoring single chunks, it scores the query against every chunk in a magazine and ranks the magazines by their best match. For the database itself, I evaluated **Pinecone, Qdrant, and Milvus**, and chose **Milvus** specifically because I could self-host it and it supports hybrid search natively.
>
> Two parts were the real engineering. First, **data quality**: out of roughly **150,000** chunks, I dropped about **12%** — around 18,000 — as noise. The rules were chunks under 100 characters, chunks full of special characters, and chunks that failed **KoNLPy** Korean tokenization. Cleaning the index at the source is what made retrieval trustworthy. Second, **safety by design**: the agent runs a fixed flow — **Safety Guard, then Reasoning, then Tool Calling, then Response** — and **LlamaGuard** inspects both the user input and the final output, so unsafe content is blocked on both ends. I stream tokens back over **SSE**, and I keep conversation history in a thread-based **checkpoint store**, so multi-turn context survives.
>
> For delivery, the whole three-tier stack — Milvus, a FastAPI backend, and a Streamlit frontend — comes up with a single **Docker Compose** command. The services are isolated on an internal Docker bridge network, and volume mounts keep the data persistent across restarts. Right now I'm learning how to port that same setup onto AWS and Kubernetes.

> **핵심 표현 (고급)**
> - "fell through" = (걸러지지 않고) 빠져나가다 / 처리되지 못하다
> - "re-orders the merged candidates" = 병합된 후보를 재정렬한다
> - "ranks the magazines by their best match" = 최고 유사도 기준으로 매거진을 순위 매김 (Group Search)
> - "self-host" = 자체 호스팅하다
> - "cleaning the index at the source" = 인덱스를 소스 단계에서 정제
> - "safety by design" = 설계 단계부터 안전성 (사후가 아니라 구조에 내장)
> - "blocked on both ends" = 입력·출력 양 끝에서 차단
> - "checkpoint store" = 체크포인트 저장소 (대화 이력 보존)
> - "port ... onto AWS and Kubernetes" = AWS·쿠버네티스로 이식
> **전달 팁:** 길어서 중간에 면접관 표정을 보며 "Want me to go deeper on the retrieval or the safety side?"로 한 번 끊어주면 좋습니다.

---

## 3. 꼬리질문 대비 (Follow-up Q&A)

**Q1. Why hybrid search instead of just dense vectors?**
> Two reasons. Dense vectors from BGE-M3 are great at meaning, but they can miss an exact term — a specific name or keyword. BM25 catches those literal matches. Combining both, then re-ranking, gives me semantic recall without losing precise keyword hits. That's what got Top-5 recall up about 35% over keyword-only search.
> *(한국어 메모: dense = 의미, sparse(BM25) = 정확 일치. "둘의 약점을 서로 보완한다"는 논리로 답하면 설계 의도가 분명해집니다.)*

**Q2. Why Milvus over Pinecone or Qdrant?**
> I compared all three against two needs. I wanted to self-host the database, for control, and I needed native hybrid search — dense plus sparse — for my retrieval design. Milvus met both of those, so I went with it over Pinecone and Qdrant.
> *(한국어 메모: 자체 호스팅 + 네이티브 하이브리드, 딱 두 기준만으로 답하세요. 다른 DB의 세부를 지어내지 말 것.)*

**Q3. How did you make the answers safe?**
> Safety is built into the agent flow. Every request runs through a Safety Guard first, then Reasoning, then Tool Calling, then the Response. And LlamaGuard inspects both the input and the output — so an unsafe question is caught before retrieval, and an unsafe generated answer is caught before it reaches the user. It's checked on both ends, not just once.
> *(한국어 메모: 흐름(Safety Guard → Reasoning → Tool Calling → Response) + 입출력 양쪽 LlamaGuard. "both ends"를 강조하세요.)*

**Q4. Why remove 12% of the chunks — didn't you lose information?**
> No, that 12% was noise, not signal. These were chunks under 100 characters, chunks full of special characters, or chunks that failed KoNLPy Korean tokenization. They don't carry real meaning, so embedding them just adds bad matches to the index. Cleaning them out at the source is a big part of why retrieval quality went up.
> *(한국어 메모: 노이즈 정의(100자 미만 / 특수문자 / 토큰화 실패)를 또렷이. "정보가 아니라 노이즈였다"가 핵심.)*

**Q5. What's the context window, and why add it?**
> When I retrieve a chunk, I also pull the chunks immediately before and after it. A single chunk can be too narrow to answer from — it might cut off mid-thought. Adding that surrounding context gives the model enough text to generate a complete, grounded answer.
> *(한국어 메모: "청크 단위가 좁아서 앞뒤를 더 가져온다"는 한 줄 직관으로 설명하면 충분합니다.)*

**Q6. How do you deploy and run the whole system?**
> It's three tiers — Milvus as the vector DB, FastAPI for the backend, and Streamlit for the frontend — and it all comes up with a single Docker Compose command. The services talk over an internal Docker bridge network, so they're isolated, and volume mounts keep the data persistent across restarts. I'm currently learning how to move that same setup onto AWS and Kubernetes.
> *(한국어 메모: 3-tier + 단일 명령 + 브릿지 격리 + 볼륨 영속성 + (성장) K8s 학습 중. 마지막의 성장 의지가 플러스 포인트입니다.)*

---

## 4. 핵심 표현·어휘 (Key phrases & vocabulary)

| English | 뜻 / 쓰임 |
|---------|-----------|
| Agentic RAG | 에이전트형 검색증강생성 (에이전트가 검색·생성 흐름을 제어) |
| hybrid search | 하이브리드 검색 (dense 벡터 + sparse 키워드) |
| dense vector / sparse (BM25) | 밀집 벡터(의미) / 희소 검색(정확 일치) |
| reranker / re-rank | 재정렬기 / 재정렬하다 |
| recall | 재현율 (찾아야 할 것 중 실제로 찾은 비율) |
| context window | 문맥 윈도우 (검색 청크의 앞뒤 문맥) |
| chunk | 청크 (문서를 쪼갠 검색 단위) |
| noise / clean the index | 노이즈 / 인덱스를 정제하다 |
| tokenization | 토큰화 (여기선 KoNLPy 한국어 토큰화) |
| self-host | 자체 호스팅하다 |
| safety layer / safety by design | 안전 레이어 / 설계 단계부터 안전 |
| on both ends | 양쪽 끝에서 (입력·출력 모두) |
| checkpoint store | 체크포인트 저장소 (대화 이력 보존) |
| token streaming (SSE) | 토큰 스트리밍 (서버에서 실시간 전송) |
| three-tier | 3계층 (DB · 백엔드 · 프론트엔드) |

---

## 5. 발음 주의 (Delivery watch-outs)

| 단어 | 강세 / 주의 |
|------|-------------|
| Milvus | "MIL-vus" — V를 B로 새지 않기 (밀버스 X) |
| Agentic | a-JEN-tik |
| recall | ri-CALL (뒤 강세). 끝 -ll 끝소리 |
| reranker | ree-RANK-er — R/L 또렷이 |
| hybrid | HY-brid |
| BM25 | "B-M twenty-five" |
| BGE-M3 | "B-G-E M three" |
| LlamaGuard | "LLA-ma-guard" (라마가드) |
| KoNLPy | "코-엔-엘-파이" (ko-N-L-py) |
| Qdrant | "Q-drant" 또는 "QUAD-rant" |
| tokenization | toh-ken-eye-ZAY-shun |
| 35% | "about thirty-five percent" |
| 150,000 | "a hundred and fifty thousand" |
| 12% | "twelve percent" |

> **마지막 점검:** 이 프로젝트의 힘은 **"recall 약 35% 향상"**과 **"데이터부터 안전까지 설계로 풀었다"**입니다. 이 두 메시지를 또렷이, 자신 있게.
