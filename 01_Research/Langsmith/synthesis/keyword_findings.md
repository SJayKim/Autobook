# Keyword Findings: LangSmith

소스 58개(001~058)를 기준으로 25개 키워드별 조사 결과를 정리한다.

---

## 클러스터 1: 관찰성 및 추적 (Observability & Tracing)

### kw_001: tracing

**핵심 메커니즘**

트레이싱은 LLM 애플리케이션의 단일 요청 처리 과정 전체를 기록하는 메커니즘이다. 하나의 Trace는 루트 Run(= root run)을 정점으로 하는 계층 구조를 형성하며, 각 노드는 LLM 호출, 체인 실행, 도구 호출 등 단위 작업을 나타낸다. 최대 25,000개의 Run을 포함할 수 있고, 데이터 보존 기간은 기본 400일이다.

트레이싱 활성화는 환경 변수 `LANGSMITH_TRACING=true`와 `LANGSMITH_API_KEY` 설정으로 완료된다. 계측(instrumentation) 방법은 세 가지다. 첫째, `@traceable` 데코레이터(Python)/`traceable` 래퍼(TS)를 함수에 붙이는 방법이다. 둘째, `wrap_openai()`로 OpenAI 클라이언트를 래핑하는 방법이다. 셋째, `RunTree` 객체를 직접 생성하는 수동 방식이다. 분산 서비스 환경에서는 `langsmith-trace` 헤더와 `baggage` 헤더로 컨텍스트를 전파한다.

**소스 매핑**

- 001: Trace / Run / Project 개념 정의, 계층 구조 (dotted_order), Run 최대 25,000개, 400일 보존
- 002: 설치 및 환경 변수 설정 퀵스타트 (LANGSMITH_TRACING, LANGSMITH_API_KEY, wrap_openai)
- 003: @traceable 데코레이터 심층 가이드 (run_type 지정, 중첩 트레이스, langsmith_extra)
- 006: REST API 직접 트레이싱 (POST /runs, PATCH /runs, multipart 배치)
- 007: 분산 트레이싱 — langsmith-trace / baggage 헤더, FastAPI TracingMiddleware
- 009: OpenTelemetry 연동 (langsmith[otel] 패키지, LANGSMITH_OTEL_ENABLED 변수)
- 047, 048: Python SDK GitHub README — @traceable, wrap_openai, RunTree 패턴
- 058: 프레임워크 독립적 트레이싱 (Python/TS/Go/Java SDK, OTel 지원)

**합의 사항**: 모든 소스가 `@traceable`+`wrap_openai` 조합을 권장 패턴으로 제시한다. REST API 직접 사용은 가능하지만 비권장이다.

---

### kw_002: runs

**핵심 메커니즘**

Run은 단일 작업 단위를 나타내는 스팬(span)이다. 7가지 run_type이 있다: `llm`, `chain`, `tool`, `retriever`, `embedding`, `prompt`, `parser`. run_type은 UI 렌더링, 토큰 카운팅, 비용 계산, Playground 연동 방식에 영향을 준다.

Run의 계층 구조는 `parent_run_id`로 연결된다. 루트 Run의 ID가 `trace_id`가 되며, `dotted_order` 문자열(타임스탬프+UUID 조합)이 시퀀스와 깊이를 인코딩한다. LLM Run에서 토큰 카운팅과 비용 계산이 작동하려면 `run_type="llm"`, 올바른 메시지 포맷, `ls_provider`/`ls_model_name` 메타데이터, `usage_metadata` 네 가지가 모두 필요하다.

**소스 매핑**

- 001: Run 정의("단일 작업 단위를 나타내는 스팬"), run_type 목록, 계층 구조
- 011: run_type별 상세 역할, LLM Run 로깅 요구사항 4가지
- 012: RunTree API 레퍼런스 (post/patch 메서드, 파라미터 목록)
- 003, 005, 008: @traceable에서 run 생성 방식

**합의 사항**: run_type="llm" 설정이 토큰/비용 추적의 전제조건임을 복수 소스가 확인한다.

---

### kw_003: projects

**핵심 메커니즘**

Project는 관련 트레이스의 컨테이너다. 환경 변수 `LANGSMITH_PROJECT`(또는 구 버전의 `LANGCHAIN_PROJECT`)로 정적 지정하거나, `@traceable(project_name=...)` 파라미터로 런타임에 동적 지정한다. 동적 지정이 환경 변수보다 우선한다. 지정한 프로젝트가 없으면 첫 트레이스 수신 시 자동 생성된다. 기본값은 `"default"` 프로젝트다.

LangSmith Deployment(구 LangGraph Platform)에서는 배포 생성 시 동일 이름의 트레이싱 프로젝트가 자동 생성되고 환경 변수도 자동 설정된다.

**소스 매핑**

- 001: Project = "트레이스 컬렉션" 정의
- 004: 정적(env var) vs 동적(runtime) 프로젝트 할당 상세 예시
- 050: Deployment와 Project 자동 연동

**합의 사항**: 소스 간 일치. `LANGSMITH_PROJECT` 환경 변수(JS SDK >=0.2.16 필요)와 `LANGCHAIN_PROJECT` 모두 유효하다.

---

### kw_004: tags and metadata

**핵심 메커니즘**

태그(Tags)는 문자열 배열로 런을 분류·필터링하는 데 사용된다. 메타데이터(Metadata)는 key-value 딕셔너리로 추가 컨텍스트 정보(앱 버전, 환경, 사용자 ID 등)를 저장한다. 둘 다 UI 필터, 자동화 규칙 필터, 커스텀 대시보드의 Group By 기준으로 활용된다.

설정 방법은 세 가지다. 첫째, `@traceable(tags=[...], metadata={...})`로 정적 선언. 둘째, `get_current_run_tree()`로 실행 중 동적 업데이트. 셋째, 호출 시 `langsmith_extra={"tags": [...], "metadata": {...}}`로 오버라이드.

멀티턴 대화에서는 `session_id`/`thread_id`/`conversation_id` 메타데이터 키가 예약되어 있으며, 스레드 집계(토큰, 비용)가 올바르게 동작하려면 모든 자식 런에도 전파해야 한다.

**소스 매핑**

- 001: 태그/메타데이터 개념 정의
- 005: 설정 방법 3가지 상세 예시 (정적/동적/호출 시)
- 008: 태그·메타데이터 기반 필터링, 쿼리 연산자 (is/contains/is one of/>/<)
- 009: OpenTelemetry baggage 헤더로 메타데이터 전파
- 010: thread_id / session_id / conversation_id 예약 키
- 034: 대시보드 Group By 기준으로 태그/메타데이터 활용

**합의 사항**: 태그와 메타데이터는 필터링, 자동화, 대시보드 모든 레이어에 공통으로 활용된다.

---

## 클러스터 2: 평가 체계 (Evaluation)

### kw_005: datasets

**핵심 메커니즘**

Dataset은 Example들의 컬렉션이다. 각 Example은 `input`(필수)과 `reference output`(선택)으로 구성된다. 스키마는 자유 형식이다. 데이터셋 유형은 key-value, chat, split dataset 세 가지다.

버전 관리: 예제 추가/수정/삭제마다 새 버전이 자동 생성된다. 타임스탬프로 추적하며, `"prod"` 같은 시맨틱 태그를 붙여 특정 버전을 코드에서 안정적으로 참조할 수 있다. 데이터셋 생성 경로는 수동 큐레이션, CSV 임포트, 프로덕션 트레이스 변환 세 가지다.

**소스 매핑**

- 013: Dataset / Evaluator / Experiment 개념 정의, 오프라인/온라인 평가 구분
- 014: 버전 관리(타임스탬프/태그), CSV 임포트, 프로덕션 트레이스로 데이터셋 생성
- 024: 데이터셋에 Evaluator 바인딩 (이후 실험에 자동 채점 적용)
- 025: 데이터셋 생성 경로 전체 목록

**합의 사항**: 소스 간 일치. 데이터셋 버전 관리와 프로덕션 트레이스 재활용 워크플로가 강조된다.

---

### kw_006: evaluators

**핵심 메커니즘**

Evaluator는 애플리케이션 출력 품질을 점수화하는 함수다. `evaluate()` 함수에 배열로 전달된다. SDK v0.2+ 시그니처: `def my_eval(inputs: dict, outputs: dict, reference_outputs: dict) -> bool | int | float | str`. 반환값은 딕셔너리 래핑 없이 기본 타입을 직접 반환한다.

유형: Heuristic(결정론적 코드), LLM-as-judge(모델 기반), Pairwise(두 출력 비교), Custom Code(UI에서 Python 작성, 제한적 라이브러리). 데이터셋에 바인딩하면 이후 생성되는 모든 실험에 자동 적용된다.

**소스 매핑**

- 015: Evaluator 유형 전체, 시그니처, Code evaluator 허용 라이브러리
- 023: SDK v0.2 통합 API — evaluate() 단일 함수, 단순화된 시그니처
- 024: 데이터셋 바인딩 Evaluator (LLM-as-judge / Custom Code)
- 025: 평가 플랫폼 전체 기능 목록

**합의 사항**: SDK v0.2에서 evaluate()가 세 가지 이전 메서드를 통합했다는 점이 여러 소스에서 강조된다.

---

### kw_007: LLM-as-judge

**핵심 메커니즘**

LLM-as-judge는 judge 역할의 LLM에 입력, 출력, 점수 루브릭을 제공하고 추론과 함께 점수를 산출하는 방법론이다. 단일 정답이 없는 대화형 텍스트 평가에 적합하다.

구성 단계: 프롬프트 설정(커스텀 작성 또는 Hub에서 선택) → 모델 선택 → 점수 루브릭 정의(Boolean/Categorical/Continuous). 변수 매핑은 mustache(`{{variable}}`) 또는 f-string(`{variable}`) 형식을 지원한다.

평가 유형: Reference-free(명확성, 일관성, 도움 정도, 톤, 간결성), Reference-based(정확성, 사실 정확도, 정확 일치, Hallucination 감지). UI 내장 유형은 Hallucination / Correctness / Conciseness 세 가지다.

**소스 매핑**

- 015: LLM-as-judge evaluator UI 설정
- 016: Reference-free vs Reference-based 상세 설명, 루브릭 3가지 타입
- 025: 신뢰성 향상 방법 (인간 검토자가 불일치를 표시하여 보정)

**합의 사항**: Reference-free와 Reference-based 구분, 루브릭 3가지 타입이 여러 소스에서 일관되게 등장한다.

---

### kw_008: experiments

**핵심 메커니즘**

Experiment는 특정 데이터셋 위에서 특정 애플리케이션 버전을 평가한 결과물이다. `evaluate()` 함수로 실행하며, `experiment_prefix`, `num_repetitions`, `max_concurrency` 파라미터로 제어한다.

`num_repetitions`는 각 예제를 반복 실행하는 횟수로, 비결정론적 LLM 출력의 분산을 측정할 때 유용하다. Comparison View에서 여러 실험을 나란히 배치하고 baseline 대비 회귀를 컬러 코딩으로 표시한다.

**소스 매핑**

- 013: Experiment 개념 정의, 오프라인 평가 워크플로
- 017: evaluate() 기본 사용, num_repetitions, Comparison View, Pairwise evaluation
- 022: evaluate() 함수에서 pairwise evaluator 시그니처, randomize_order 파라미터
- 023: SDK v0.2 — evaluate() 통합 API

**합의 사항**: 소스 간 일치. Pairwise 비교가 절대 점수보다 신뢰할 수 있다는 점이 반복 강조된다.

---

### kw_009: annotation queues

**핵심 메커니즘**

Annotation Queue는 인간 어노테이터가 Run에 피드백을 붙이는 스트림라인된 인터페이스다. Single-run queue(한 번에 하나의 Run)와 Pairwise Annotation Queue(두 Run을 나란히 A/B 비교) 두 가지가 있다.

Rubric 설정으로 검토자 가이드라인과 피드백 키를 정의한다. `Reviewer count`는 Run이 "완료" 처리되기까지 필요한 어노테이터 수이며, `Reservations` 기능으로 중복 검토를 방지한다. 큐에 Run을 추가하는 방법은 UI 수동 선택, 대량 선택, 자동화 규칙 트리거 세 가지다.

**소스 매핑**

- 018: Single-run queue / PAQ 생성 절차, Rubric, Reservations, 검토 워크플로
- 022: PAQ — 두 실험 선택하여 Pairwise Annotation Queue 생성
- 025: Human Feedback 워크플로 전체 (큐 생성 → 전문가 배정 → 표준화 Rubric)
- 035: 자동화 규칙에서 Annotation Queue로 라우팅하는 액션

**합의 사항**: 자동화 규칙과 Annotation Queue가 연계되는 워크플로가 여러 소스에서 확인된다.

---

### kw_010: online evaluation

**핵심 메커니즘**

Online Evaluation은 프로덕션 트래픽에서 실시간으로 품질을 모니터링하는 기능이다. 독성 감지, RAG Hallucination 확인, 품질 드리프트 탐지, 성능 이상 감지에 활용한다.

설정: Tracing 프로젝트의 Evaluators 탭에서 + New Evaluator로 추가. 필터로 평가 대상 Run을 한정하고, Sampling Rate(0~1)로 평가할 비율을 조정한다. Backfill 기능으로 과거 트레이스를 소급 평가할 수 있다.

Multi-turn Eval은 Online Evaluation의 확장으로, Thread 단위로 동작하며 Idle Time 설정으로 대화 완료 시점을 판단한다.

**소스 매핑**

- 013: 오프라인/온라인 평가 구분, 온라인 평가 워크플로 4단계
- 019: Evaluator 설정, 필터, Sampling Rate, Backfill 기능, 멀티모달 지원
- 021: Multi-turn Eval이 Online Evaluation으로 동작하는 메커니즘, Idle Time

**합의 사항**: 소스 간 일치. Sampling Rate를 통한 비용 제어가 중요하게 강조된다.

---

### kw_014: feedback

**핵심 메커니즘**

Feedback은 Run에 품질 신호를 붙이는 메커니즘이다. 데이터 모델: `run_id`/`trace_id`, `key`(피드백 이름), `score`(수치), `value`(이진), `comment`(텍스트), `correction`(구조화된 수정)으로 구성된다.

생성 방법: `client.create_feedback(run_id, key, score, comment)`. Thumbs Up/Down 패턴은 별도 키(`user_liked`/`user_disliked`) 방식과 단일 키(`user_feedback`, score=1/-1) 방식 두 가지로 구현한다. 자동 evaluator 점수, 인간 어노테이션, 최종 사용자 반응을 단일 인터페이스로 통합한다.

**소스 매핑**

- 020: Feedback 데이터 모델 전체, Thumbs Up/Down 두 가지 패턴, Python SDK 예시
- 034: 대시보드 Feedback Scores 섹션 (상위 5개 피드백 유형 집계)
- 036: Alerts에서 Feedback Score를 모니터링 메트릭으로 사용

**합의 사항**: Feedback이 Alerts, 대시보드, 자동화 규칙, Annotation Queue와 연동되는 구조임이 여러 소스에서 확인된다.

---

### kw_023: multi-turn evaluation

**핵심 메커니즘**

Multi-turn Evals는 단일 요청-응답이 아닌 대화 전체(end-to-end)를 평가한다. 3가지 측정 지표: Semantic Intent(사용자 의도 파악), Semantic Outcomes(태스크 성공 여부), Agent Trajectory(도구 호출 내역, 의사결정 패턴, 대화 경로).

LangSmith의 Threads 개념 위에서 Online Evaluation으로 동작한다. Thread-level evaluator 구성 시 Idle Time을 설정하고, 마지막 트레이스 이후 해당 시간이 경과하면 평가를 시작한다. LLM-as-judge 방법론을 사용하며, 사용자가 Thread 전체를 평가하는 scoring prompt를 정의한다.

**소스 매핑**

- 021: Multi-turn Evals 개요, 3가지 측정 지표, Threads 기반 아키텍처, Idle Time
- 043: Insights Agent와 Multi-turn Evals 결합 블로그

**합의 사항**: 소스 간 일치. Multi-turn Eval은 Online Evaluation의 특수 형태임이 명확히 명시된다.

---

## 클러스터 3: 프롬프트 관리 (Prompt Management)

### kw_011: prompt playground

**핵심 메커니즘**

Prompt Playground는 프롬프트 작성, 테스트, 평가를 코드 없이 수행하는 통합 인터페이스다. Playground v2는 다중 모델 제공자(Vertex AI, Mistral, Gemini 등)를 지원하고, 동시에 최대 5개 출력을 생성하는 Concurrent Outputs 기능을 제공한다.

비교 모드(Compare Mode): 여러 프롬프트와 모델 설정을 나란히 비교한다. 데이터셋 기반 실험도 Playground 내에서 직접 실행할 수 있으며, 결과가 만족스러우면 Hub에 바로 커밋한다. Polly 도구로 프롬프트 자동 최적화도 가능하다. 트레이스 디버깅, 프롬프트 생성/편집, 데이터셋 평가 세 가지 활동을 단일 인터페이스에서 수행한다.

**소스 매핑**

- 026: Playground에서 데이터셋 기반 평가 실행, Polly, Hub 커밋 연동
- 027: Playground v2 — 확장된 모델 지원, Concurrent Outputs, 비교 모드
- 028: Side-by-side 비교 기능 추가 (2024년 7월)
- 029: Playground에서 프롬프트 엔지니어링 개념 (템플릿 변수)

**합의 사항**: v2에서 기능이 크게 확장되었음이 여러 소스에서 확인된다. Playground가 LangSmith 전체에 통합된 중앙 인터페이스 역할을 한다.

---

### kw_012: prompt versioning

**핵심 메커니즘**

저장된 각 프롬프트 업데이트마다 고유 커밋 해시(commit hash)가 자동 생성된다. `client.pull_prompt("prompt-name:commit_hash")`로 특정 버전을 코드에서 고정 참조한다. "Show diff" 토글로 커밋 간 변경사항을 시각적으로 비교한다.

태그(Tags)는 커밋을 가리키는 인간 친화적 라벨이다. `production`, `staging`, `dev`, `v1`, `v2` 등으로 환경별 버전을 관리한다. 태그를 새 커밋으로 이동(move)하기만 하면 코드 변경 없이 프로덕션 업데이트가 완료된다.

**소스 매핑**

- 029: 커밋 해시 / 태그 개념, 코드에서 버전 고정 참조 방법
- 030: Diff View, 태그 생성/이동/삭제 UI
- 031: 태그 기반 SDLC 통합, 환경별 배포 워크플로 5단계

**합의 사항**: 커밋 해시로 버전 고정, 태그로 환경 분리하는 패턴이 일관된다.

---

### kw_013: LangChain Hub

**핵심 메커니즘**

LangChain Hub는 프롬프트를 공유하고 재사용하는 중앙 저장소다. `hub.pull("handle/prompt-name")` / `hub.push("handle/prompt-name", prompt)`로 프롬프트를 다운로드/업로드한다. 탐색 기준: 정렬(최신/즐겨찾기/조회/다운로드순), 필터(use case, model, language).

LangSmith SDK와 통합: `client.push_prompt()` / `client.pull_prompt()`로 프로그래매틱 관리. 모델과 함께 RunnableSequence로 저장하거나, 구조화된 출력 스키마를 포함하여 저장할 수 있다. 캐싱 설정으로 네트워크 호출을 최소화한다.

**소스 매핑**

- 032: Hub 설계 목적, pull/push 워크플로, 커뮤니티 협업 설계
- 033: 프로그래매틱 관리 (push_prompt, pull_prompt, 모델+프롬프트 함께 저장, 캐싱)

**합의 사항**: Hub가 Playground, 버전 관리와 통합된 단일 프롬프트 레지스트리임이 확인된다.

---

## 클러스터 4: 모니터링 및 자동화 (Monitoring & Automation)

### kw_015: monitoring dashboards

**핵심 메커니즘**

두 가지 대시보드 유형: Prebuilt Dashboard(프로젝트별 자동 생성)와 Custom Dashboard(사용자 정의). Prebuilt는 6개 섹션으로 구성된다: Traces(횟수/지연시간/오류율), LLM Calls(호출 수/지연시간), Cost & Tokens, Tools(상위 5개), Run Types, Feedback Scores(상위 5개).

커스텀 대시보드는 프로젝트 선택 → 메트릭 선택(Y축) → 데이터 분할 → 차트 유형 선택의 순서로 구성한다. Group By(태그/메타데이터/실행 이름)와 Data Series(수동 필터 정의) 두 가지 분할 방식이 있다.

**소스 매핑**

- 034: Prebuilt / Custom 대시보드 구성 전체, P50/P99 지연시간 지표
- 046: LangSmith + Prometheus + Grafana 통합 아키텍처, P50/P90/P99 히스토그램

**합의 사항**: 두 소스가 P50/P99 지연시간 지표를 공통으로 강조한다. 034는 LangSmith 내장 기능, 046은 외부 도구(Prometheus/Grafana) 연동을 다룬다.

---

### kw_016: automation rules

**핵심 메커니즘**

Automation Rules는 필터 조건 + 샘플링 레이트 + 액션의 세 요소로 구성된다. 필터 유형: 지연시간, 오류, 사용자 피드백, 메타데이터/태그, 텍스트 검색, AI 쿼리(자연어를 필터 조건으로 자동 변환). 샘플링 레이트(0~1)로 고비용 액션(LLM 평가 등)을 일부 샘플에만 적용해 비용을 절감한다.

4가지 액션: Add to Dataset, Add to Annotation Queue, Trigger Webhook, Extend Data Retention.

**소스 매핑**

- 035: 자동화 규칙 3요소 상세 (필터 유형 8가지, 샘플링, 액션 4가지)
- 044: 자동화 규칙 블로그 — 필터링 옵션 심층 설명, 샘플링 비용 절감 효과

**합의 사항**: 소스 간 일치. AI 쿼리 필터가 새 기능으로 두 소스 모두에서 언급된다.

---

### kw_017: alerts

**핵심 메커니즘**

Alerts는 프로젝트별로 설정하며 4가지 메트릭을 지원한다: Run Count, Errors(수/비율), Feedback Score, Latency. 임계값 설정 구성요소: 집계 방법(평균/백분율/카운트) + 비교 연산자 + 임계값 + 집계 윈도우(5분/15분) + 피드백 키(Feedback Score 알림만). 알림 전달 방식: PagerDuty(인시던트 관리)와 Custom Webhook(Slack 등).

**소스 매핑**

- 036: Alerts 임계값 설정 상세, Webhook 알림 필수/선택 설정
- 037: 지원 메트릭 3가지, PagerDuty/Webhook 알림 방식
- 038: PagerDuty 통합 단계별 설정 (서비스 생성, Integration Key 획득)

**합의 사항**: 세 소스가 동일 기능을 다루며 일치한다. PagerDuty + Webhook 두 채널이 공통으로 확인된다.

---

### kw_022: Insights Agent

**핵심 메커니즘**

Insights Agent는 대규모 트레이스 데이터에서 자동으로 패턴을 발견하는 AI 기반 분석 도구다. 4단계 프로세스: 트레이스 요약(Summary Model) → 클러스터링(Thinking Model) → 범주화(자동/사용자 정의) → 세부 분류.

분석 모드: 사용 패턴 분석, 실패 모드 발견(부정적 피드백 기반 클러스터링), 커스터마이징(분류 카테고리 정의, 시간 범위 필터, 속성 추가). Executive Summary로 주요 결과 요약. 보고서 생성에 최대 15분 소요. LangSmith Plus 및 Enterprise 대상(2025년 10월 23일 GA).

**소스 매핑**

- 039: Insights Agent 작동 방식(4단계), 분석 기능(사용 패턴/실패 모드), Executive Summary
- 040: 에이전트 특수성(비결정론적/무제한 입력), 기존 분석 도구와의 차별점
- 043: Insights Agent + Multi-turn Evals 결합 블로그
- 045: GA 발표 (2025년 10월), 세 가지 핵심 분석 모드

**합의 사항**: 네 소스가 일관된 내용을 제공하며, 클러스터링 기반 패턴 발견이 핵심 차별점으로 강조된다.

---

### kw_025: cost and token tracking

**핵심 메커니즘**

비용은 Input(프롬프트 토큰), Output(응답 토큰), Other(도구 호출/검색 등) 세 범주로 나뉜다. 자동 계산 요건: `usage_metadata` 필드 + `ls_provider`/`ls_model_name` 메타데이터 + 모델 가격 테이블. 수동 비용 제출로 LLM 외 도구·검색 비용도 추적 가능하다("full-stack cost tracking").

확인 위치: 트레이스 트리(실행별 상세), 프로젝트 통계(집계), 대시보드(시간별 추이). 커스텀 가격 설정으로 기업 협상 요금이나 커스텀 모델에도 정확한 비용 보고가 가능하다.

**소스 매핑**

- 041: 비용 추적 개요, 자동 계산 vs 수동 제출, 3가지 확인 위치
- 042: "full-stack cost tracking" 개념, 수동 비용 제출 지원, 커스텀 가격 설정

**합의 사항**: 두 소스가 일치. 041은 공식 문서, 042는 changelog 발표 내용으로 상호 보완한다.

---

## 클러스터 5: 통합 및 배포 인프라 (Integration & Infrastructure)

### kw_018: SDK integration

**핵심 메커니즘**

Python SDK(`pip install langsmith`), TypeScript SDK(`npm install langsmith`), Go SDK, Java SDK 네 가지를 공식 지원한다. Python SDK의 주요 패턴: `@traceable` 데코레이터, `wrap_openai()`/`wrap_anthropic()` 래퍼, `RunTree` 저수준 API. TypeScript SDK는 동등한 기능을 제공한다.

`@traceable`은 내부적으로 RunTree 객체를 생성하고 입력/출력을 캡처하며, 자식 실행에 컨텍스트를 전파하고 오류를 처리하며 배치로 API에 전송한다. `RunTree`는 `LANGSMITH_TRACING` 환경 변수 없이도 `LANGSMITH_API_KEY`만으로 동작한다.

**소스 매핑**

- 047: Python SDK 설치, @traceable / wrap_openai / RunTree 패턴
- 048: GitHub README — @traceable 내부 동작 설명
- 058: 4개 언어 SDK 목록 (Python/TS/Go/Java)

**합의 사항**: 소스 간 일치. @traceable + wrap_openai 조합이 권장 패턴으로 반복된다.

---

### kw_019: framework integrations

**핵심 메커니즘**

LangSmith는 프레임워크 독립적으로 동작한다("어떤 LLM 프레임워크와도"). LangChain/LangGraph와의 통합이 가장 심층적이며, 환경 변수 설정만으로 자동 트레이싱이 활성화된다.

공식 지원 에이전트 프레임워크(11개): LangChain, LangGraph, CrewAI, AutoGen(Mastra), Claude Agent SDK, OpenAI Agents SDK, Microsoft Agent Framework, Google ADK, PydanticAI, Vercel AI SDK, Semantic Kernel. LLM 프로바이더: Anthropic, OpenAI, Google Gemini, Amazon Bedrock, Mistral, DeepSeek. LlamaIndex는 @traceable 또는 OpenTelemetry 브리지로 연동한다.

**소스 매핑**

- 049: 에이전트 프레임워크 11개 목록, LangGraph 통합 Zero-code 방식
- 058: 프레임워크 독립성 선언, 4개 언어 SDK, OTel 지원

**합의 사항**: 두 소스가 일치. Zero-code 환경 변수 설정으로 LangChain/LangGraph 자동 트레이싱이 가능하다는 점이 핵심 차별점으로 강조된다.

---

### kw_020: deployment

**핵심 메커니즘**

LangSmith Deployment(2025년 10월, 구 LangGraph Platform)는 에이전트를 프로덕션에 배포하는 전용 인프라다. Control Plane(UI + API) + Data Plane(Agent Server + PostgreSQL + Redis + Autoscaler) 아키텍처. 단방향 폴링 설계: Data Plane이 Control Plane을 주기적으로 폴링하여 변경사항을 감지한다.

배포 유형: Development(1 CPU/1GB, 단일 레플리카)와 Production(2 CPU/2GB, 최대 10 레플리카 오토스케일링). 오토스케일링은 CPU 75%, 메모리 75%, 대기 실행 수 10개/컨테이너 세 메트릭 기준으로 동작한다. 배포 옵션: Cloud SaaS, Hybrid(SaaS Control Plane + 자체 Data Plane), 완전 Self-hosted.

**소스 매핑**

- 050: Control Plane 아키텍처, Agent Server, 배포 유형, 배포 옵션
- 051: Data Plane 구성요소(PostgreSQL/Redis/Autoscaler), 오토스케일링 3개 메트릭
- 056: LangGraph Platform GA 발표, 에이전트 특화 기능(장기 실행/버스티 부하/Stateful)
- 057: 배포 과제 3가지와 해결책 (장기 실행/버스티 부하/Stateful 작업)

**합의 사항**: 네 소스가 일치. 장기 실행 에이전트, 버스티 부하, Stateful 작업 세 가지가 핵심 해결 과제로 반복된다.

---

### kw_021: self-hosted LangSmith

**핵심 메커니즘**

Self-hosted LangSmith는 Enterprise Plan 부가 기능으로, 데이터가 자체 환경 밖으로 나가지 않는다. Kubernetes(프로덕션 권장, Helm 차트)와 Docker Compose(개발/소규모) 두 가지 배포 방식을 지원한다.

Kubernetes 요건: 최소 16 vCPU/64GB RAM, ClickHouse 전용 노드(4 vCPU/16GB), 7000 IOPS SSD. 아키텍처: Stateless 서비스(Frontend/Backend/Platform Backend/Queue Service/Playground Service/ACE Backend) + Persistent 스토리지(ClickHouse/PostgreSQL/Redis). ClickHouse가 대용량 트레이스 저장소 역할을 한다. 인증: OAuth/SSO(OIDC, 권장)와 Basic 인증.

**소스 매핑**

- 052: Kubernetes Helm 차트 배포, 지원 K8s 배포판, 사전 요구사항
- 053: Docker Compose 배포, 아키텍처 구성요소, 인증 옵션, 데이터 보존 정책

**합의 사항**: 두 소스가 상호 보완한다. 052는 공식 문서, 053은 DeepWiki 심층 분석으로 동일 내용을 다른 각도에서 제공한다.

---

### kw_024: API and SDK reference

**핵심 메커니즘**

LangSmith REST API 호스트: `api.smith.langchain.com`. 인증: `x-api-key` 헤더. 멀티테넌트: `X-Tenant-Id` 헤더. API 키 유형: Service Key(프로덕션, 쉬운 로테이션)와 Personal Token(로컬 개발).

주요 엔드포인트: `POST /runs`(실행 생성), `PATCH /runs/{run_id}`(실행 업데이트), `POST /runs/query`(필터 쿼리), `GET /api/v1/examples`(예제 조회), `POST /api/v1/datasets/comparative`(비교 실험 생성), `POST /api/v1/feedback`(피드백 생성). 배치 수집: `POST /runs/batch`(높은 처리량)와 `POST /runs/multipart`(매우 높은 처리량).

**소스 매핑**

- 054: REST API 핵심 엔드포인트, 인증, 실행 생성 필수 필드
- 055: 엔드포인트별 처리량 비교, API 키 유형, 피드백 신호 유형

**합의 사항**: 두 소스가 일치. 배치 수집 엔드포인트별 처리량 차이가 강조된다.

---

## 소스 커버리지 요약

| 클러스터 | 키워드 수 | 소스 수 | 커버리지 |
|---------|---------|--------|--------|
| 관찰성 및 추적 | 4 | 18 | 매우 풍부 |
| 평가 체계 | 8 | 20 | 풍부 |
| 프롬프트 관리 | 3 | 8 | 충분 |
| 모니터링 및 자동화 | 5 | 12 | 충분 |
| 통합 및 배포 인프라 | 5 | 10 | 충분 |

전체 25개 키워드 모두 1개 이상의 소스에서 커버됨. config.json의 keyword_coverage = 1.0 확인.
