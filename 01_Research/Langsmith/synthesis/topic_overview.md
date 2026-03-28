# Topic Overview: LangSmith

## 플랫폼 핵심 가치와 아키텍처

LangSmith는 LLM 애플리케이션의 전체 수명주기(개발 → 테스트 → 배포 → 운영)를 지원하는 관찰성 및 평가 플랫폼이다. LangChain Inc.가 개발하였으며, LangChain/LangGraph 생태계와 가장 깊이 통합되어 있지만 "어떤 LLM 프레임워크와도" 동작하는 프레임워크 독립적 설계를 표방한다.

핵심 가치 제안은 세 가지다. 첫째, 개발 단계에서 오프라인 평가로 회귀를 사전에 잡는다("Test before you ship"). 둘째, 프로덕션 단계에서 온라인 평가와 자동화 규칙으로 품질 드리프트를 실시간으로 감지한다("Monitor in production"). 셋째, 피드백 루프를 구축하여 트레이스 데이터가 새로운 데이터셋과 프롬프트 개선으로 선순환하도록 한다.

아키텍처는 두 레이어로 나뉜다. Observability Layer는 트레이스/런/프로젝트 구조로 실행 데이터를 수집하고, Evaluation & Management Layer는 이 데이터를 기반으로 평가, 프롬프트 관리, 모니터링, 배포를 처리한다.

---

## 주요 기능 영역 (5개 클러스터)

### 1. 관찰성 및 추적 (Observability & Tracing)

LLM 애플리케이션 실행 과정을 계층 구조(Trace → Run)로 기록한다. 계측 방법은 `@traceable` 데코레이터, `wrap_openai()` 래퍼, `RunTree` 저수준 API, OpenTelemetry 브리지 네 가지를 제공한다. 분산 서비스 환경에서는 `langsmith-trace`/`baggage` 헤더로 컨텍스트를 전파한다. 멀티턴 대화는 `thread_id`/`session_id` 메타데이터 키로 Thread 단위로 그룹화한다.

### 2. 평가 체계 (Evaluation)

오프라인 평가(데이터셋 기반 실험)와 온라인 평가(프로덕션 실시간) 두 트랙으로 구성된다. 평가자 유형은 Heuristic, LLM-as-judge, Pairwise, Custom Code, Human(Annotation Queue) 다섯 가지다. SDK v0.2부터 세 가지 이전 메서드가 단일 `evaluate()` 함수로 통합되었다. Multi-turn Eval은 Thread 단위로 Semantic Intent / Semantic Outcomes / Agent Trajectory 세 차원을 측정한다.

### 3. 프롬프트 관리 (Prompt Management)

Playground에서 프롬프트를 작성·테스트·비교하고, Commit 기반 버전 관리로 이력을 추적하며, 태그(`production`/`staging`/`dev`)로 환경별 배포를 관리한다. LangChain Hub는 공개 프롬프트 공유 레지스트리 역할을 한다. `client.pull_prompt("name:tag")`로 코드 변경 없이 프롬프트 버전을 교체할 수 있다.

### 4. 모니터링 및 자동화 (Monitoring & Automation)

Prebuilt/Custom 대시보드로 지연시간(P50/P99), 토큰/비용, 오류율, 피드백 점수를 추적한다. 자동화 규칙(필터 + 샘플링 레이트 + 액션)으로 트레이스를 자동 분류한다. Alerts는 메트릭 임계값 초과 시 PagerDuty/Webhook으로 알린다. Insights Agent는 클러스터링 기반 AI 분석으로 수천 건의 트레이스에서 사용 패턴과 실패 모드를 자동 발견한다(2025년 10월 GA, Plus/Enterprise).

### 5. 통합 및 배포 인프라 (Integration & Infrastructure)

Python/TypeScript/Go/Java SDK를 제공한다. 11개 에이전트 프레임워크와 공식 통합하며 LangChain/LangGraph는 Zero-code 자동 트레이싱을 지원한다. LangSmith Deployment(구 LangGraph Platform, 2025년 10월 리브랜딩)는 Control Plane + Data Plane 아키텍처로 에이전트를 프로덕션에 배포한다. Self-hosted 배포는 Kubernetes(Helm) 또는 Docker Compose로 구성하며, Enterprise 전용 기능이다.

---

## 현재 트렌드와 최신 기능 (2025년 기준)

- **Insights Agent GA** (2025년 10월): AI 기반 트레이스 패턴 분석 — 사용 패턴, 실패 모드 자동 발견
- **Multi-turn Evals**: 대화 전체를 평가하는 Thread-level evaluator — Semantic Intent/Outcomes/Trajectory
- **LangSmith Deployment 리브랜딩** (2025년 10월): LangGraph Platform → LangSmith Deployment 통합
- **Unified Cost Tracking**: LLM, 도구, 검색 비용을 통합 추적하는 full-stack cost tracking
- **Playground v2**: 다중 모델 지원 확장, Concurrent Outputs, Polly 자동 최적화
- **SDK v0.2**: evaluate() 단일 API로 통합, 평가자 시그니처 단순화
- **OpenTelemetry 지원**: OTel 기반 트레이스 내보내기로 기존 관찰성 인프라와 연동 가능

---

## 교재 챕터 구조 제안

아래 구조는 `/curriculum` 명령에서 바로 참고할 수 있도록 Phase > Section > Topic 수준까지 제안한다. 각 Topic에 learning_content 키워드 후보를 포함한다.

---

### Phase 1: LangSmith 관찰성 기초

**설명**: LLM 애플리케이션 실행 과정을 투명하게 기록하는 트레이싱 시스템의 구조와 설정 방법을 다룬다.

#### Section 1.1: 트레이싱 개념과 아키텍처

**1.1.1 LangSmith 플랫폼 개요와 설치**
- learning_content: LangSmith 플랫폼 역할, 설치(pip install langsmith), 환경 변수(LANGSMITH_TRACING, LANGSMITH_API_KEY), 첫 트레이스 확인

**1.1.2 트레이스와 런의 계층 구조**
- learning_content: Trace 정의(관련 Run의 컬렉션), Run 정의(단일 작업 단위), root run, child run, dotted_order, trace_id, parent_run_id, 최대 25,000 Run, 400일 보존

**1.1.3 런 유형과 LLM 런 로깅**
- learning_content: run_type 7가지(llm/chain/tool/retriever/embedding/prompt/parser), LLM Run 로깅 4가지 요건(run_type=llm, 메시지 포맷, ls_provider/ls_model_name, usage_metadata), 토큰 카운팅 활성화

#### Section 1.2: 계측 방법

**1.2.1 @traceable 데코레이터와 wrap_openai**
- learning_content: @traceable 데코레이터 사용법, traceable 래퍼(TypeScript), wrap_openai, 중첩 트레이스 자동 생성, 컨텍스트 전파

**1.2.2 RunTree API와 수동 계측**
- learning_content: RunTree 생성자 파라미터, post()/patch() 메서드, 부모-자식 계층 수동 구성, RunTree와 LANGSMITH_TRACING 독립성

**1.2.3 REST API를 통한 트레이싱**
- learning_content: POST /runs, PATCH /runs/{run_id}, POST /runs/multipart(배치), UUID v7, x-api-key 헤더

#### Section 1.3: 프로젝트와 메타데이터 관리

**1.3.1 프로젝트 설정과 동적 라우팅**
- learning_content: LANGSMITH_PROJECT 환경 변수, 동적 프로젝트 할당(@traceable project_name 파라미터), 런타임 오버라이드(langsmith_extra), 자동 프로젝트 생성

**1.3.2 태그와 메타데이터 활용**
- learning_content: 태그(문자열 배열) vs 메타데이터(key-value), 정적 선언(@traceable tags/metadata), 동적 업데이트(get_current_run_tree()), 호출 시 오버라이드(langsmith_extra), 필터링 활용

**1.3.3 멀티턴 대화 추적 (Threads)**
- learning_content: Thread 정의(단일 대화 트레이스 시퀀스), session_id/thread_id/conversation_id 예약 키, 자식 Run 전파 필요성, get_thread_history()

#### Section 1.4: 고급 트레이싱

**1.4.1 분산 트레이싱**
- learning_content: langsmith-trace 헤더, baggage 헤더, 클라이언트 측 run_tree.to_headers(), FastAPI TracingMiddleware, 크로스 서비스 트레이스 연결

**1.4.2 OpenTelemetry 통합**
- learning_content: langsmith[otel] 패키지, LANGSMITH_OTEL_ENABLED, OTel 속성 매핑, POST /otel/v1/traces, 기존 OTel 인프라와 연동

**1.4.3 트레이스 필터링과 검색**
- learning_content: UI 필터 바, 필터 연산자(is/contains/is one of/>/<), 태그/메타데이터 기반 필터, 전문 텍스트 검색, Traces 뷰 vs Runs 뷰

---

### Phase 2: LangSmith 평가 체계

**설명**: LLM 애플리케이션 출력 품질을 체계적으로 측정하고 개선하는 평가 파이프라인 구축 방법을 다룬다.

#### Section 2.1: 평가 기초 개념

**2.1.1 오프라인 평가와 온라인 평가 개요**
- learning_content: 오프라인 평가(Test before you ship), 온라인 평가(Monitor in production), 데이터셋-Evaluator-Experiment 관계, 평가 워크플로 4단계

**2.1.2 데이터셋 생성과 관리**
- learning_content: Dataset/Example 구조(input + reference output), 데이터셋 유형(key-value/chat/split), 버전 관리(자동 버전 생성, 타임스탬프 태그), CSV 임포트, 프로덕션 트레이스에서 데이터셋 생성

#### Section 2.2: 평가자(Evaluator) 유형

**2.2.1 Heuristic Evaluator와 Custom Code Evaluator**
- learning_content: Heuristic evaluator(결정론적 규칙), SDK v0.2 시그니처(inputs/outputs/reference_outputs → bool/int/float/str), Code evaluator(UI에서 Python 작성, 허용 라이브러리), 데이터셋 바인딩(이후 실험 자동 채점)

**2.2.2 LLM-as-Judge 평가**
- learning_content: LLM-as-judge 개념, 프롬프트 설정(커스텀/Hub), 변수 매핑(mustache/f-string), 모델 선택, 루브릭(Boolean/Categorical/Continuous), Reference-free vs Reference-based, UI 내장 유형(Hallucination/Correctness/Conciseness)

**2.2.3 Pairwise Evaluation**
- learning_content: Pairwise evaluator 개념(절대 점수 vs 상대 비교), evaluate() pairwise 시그니처(outputs: list[dict]), randomize_order(위치 편향 최소화), evaluate_comparative()

#### Section 2.3: 실험 실행과 비교

**2.3.1 evaluate() 함수와 실험 실행**
- learning_content: evaluate() 파라미터(data, evaluators, experiment_prefix, num_repetitions, max_concurrency), aevaluate()(비동기), 실험 결과 구조

**2.3.2 실험 비교와 회귀 탐지**
- learning_content: Comparison View(나란히 비교, 컬러 코딩), baseline 대비 회귀 탐지, num_repetitions(분산 측정), 실험에 기존 evaluator 추가(evaluate(existing_id, evaluators=[...]))

#### Section 2.4: 인간 평가와 피드백

**2.4.1 Annotation Queue와 인간 검토 워크플로**
- learning_content: Single-run queue vs Pairwise Annotation Queue(PAQ), Rubric 설정(피드백 키, 설명), Reviewer count, Reservations(중복 검토 방지), 큐 추가 방법(UI/자동화 규칙/데이터셋 실험)

**2.4.2 Feedback 시스템**
- learning_content: Feedback 데이터 모델(run_id, key, score, value, comment, correction), create_feedback() API, Thumbs Up/Down 두 가지 구현 패턴, 자동 evaluator 점수와 인간 피드백 통합

#### Section 2.5: 온라인 평가와 멀티턴 평가

**2.5.1 온라인 평가 설정**
- learning_content: Online Evaluator 설정(Evaluators 탭, + New Evaluator), 필터 설정, Sampling Rate(비용 제어), Backfill(소급 평가), 멀티모달 콘텐츠 지원

**2.5.2 Multi-turn Evaluation**
- learning_content: Multi-turn Evals 개념, Semantic Intent / Semantic Outcomes / Agent Trajectory 3가지 측정 지표, Threads 기반 아키텍처, Idle Time 설정, LLM-as-judge 통합

---

### Phase 3: 프롬프트 관리

**설명**: 프롬프트를 체계적으로 작성, 테스트, 버전 관리, 공유하는 방법을 다룬다.

#### Section 3.1: Prompt Playground

**3.1.1 Playground 기본 사용과 모델 비교**
- learning_content: Playground 인터페이스 구성(에디터/모델 설정/출력), Compare Mode(side-by-side 비교), Concurrent Outputs(최대 5개 동시 생성), 지원 모델 제공자(Vertex AI/Mistral/Gemini 등), 도구 호출 테스트

**3.1.2 Playground에서 데이터셋 기반 평가**
- learning_content: 데이터셋 연결(입력 키-변수 매핑, 최대 15개 변수), Evaluator 추가(+Evaluator 버튼), 인라인 데이터셋 생성, 평가 결과에서 Hub 커밋

**3.1.3 Polly를 활용한 프롬프트 최적화**
- learning_content: Polly 도구 개념, 자동 프롬프트 최적화, 최적화 전후 비교, Playground 통합 워크플로

#### Section 3.2: 프롬프트 버전 관리

**3.2.1 커밋과 버전 이력**
- learning_content: 자동 커밋 해시 생성, 버전 이력 전체 보기, Diff View(커밋 간 변경사항 시각화), 특정 버전 코드 참조(pull_prompt("name:hash")), 이전 버전 롤백

**3.2.2 태그 기반 환경 분리**
- learning_content: 태그 개념(커밋을 가리키는 인간 친화적 라벨), 태그 생성/이동/삭제, 환경별 태그(production/staging/dev/v1/v2), 태그 이동으로 코드 변경 없는 배포, SDLC 통합 워크플로 5단계

#### Section 3.3: LangChain Hub

**3.3.1 Hub에서 공개 프롬프트 활용**
- learning_content: Hub 설계 목적(모범 사례 공유), hub.pull() / hub.push(), 탐색 기준(정렬/필터), 버전 관리, 프롬프트 fork 및 커뮤니티 기여

**3.3.2 프로그래매틱 프롬프트 관리**
- learning_content: client.push_prompt() / client.pull_prompt(), 모델과 함께 저장(RunnableSequence), 구조화된 출력 스키마 포함 저장, 캐싱 설정, 환경 변수 설정(LANGSMITH_API_KEY)

---

### Phase 4: 모니터링과 자동화

**설명**: 프로덕션 환경에서 LLM 애플리케이션 품질을 지속적으로 관리하는 방법을 다룬다.

#### Section 4.1: 모니터링 대시보드

**4.1.1 Prebuilt 대시보드 활용**
- learning_content: Prebuilt Dashboard 6개 섹션(Traces/LLM Calls/Cost & Tokens/Tools/Run Types/Feedback Scores), P50/P99 지연시간 지표 해석, 토큰/비용 추적, 오류율 모니터링

**4.1.2 Custom 대시보드 구성**
- learning_content: 커스텀 대시보드 생성(프로젝트 선택→메트릭→분할→차트 유형), Group By(태그/메타데이터 기준 분할), Data Series(수동 필터 정의), 라인/막대 차트

**4.1.3 비용과 토큰 추적**
- learning_content: 비용 3분류(Input/Output/Other), 자동 계산 요건(usage_metadata + ls_provider/ls_model_name + 가격 테이블), 수동 비용 제출(도구/검색), 커스텀 가격 설정, 3가지 확인 위치(트레이스 트리/프로젝트 통계/대시보드)

#### Section 4.2: 자동화 규칙

**4.2.1 자동화 규칙의 구성과 설정**
- learning_content: 자동화 규칙 3요소(필터+샘플링+액션), 필터 유형 8가지(지연시간/오류/피드백/메타데이터/태그/텍스트/Trace attributes/AI 쿼리), 샘플링 레이트(0~1, 비용 절감), 액션 4가지(Add to Dataset/Annotation Queue/Webhook/Extend Retention)

**4.2.2 자동화 규칙 활용 패턴**
- learning_content: 실패 케이스 자동 데이터셋 추가 패턴, 부정 피드백 Annotation Queue 라우팅, Webhook 연동(Slack/PagerDuty), 자연어 AI 쿼리 필터 활용

#### Section 4.3: 알림 시스템

**4.3.1 메트릭 임계값 알림 설정**
- learning_content: Alerts 지원 메트릭 4가지(Run Count/Errors/Feedback Score/Latency), 임계값 설정 구성요소(집계방법/연산자/값/윈도우 5분 or 15분), 필터 적용(모델/도구 특정 알림)

**4.3.2 PagerDuty와 Webhook 연동**
- learning_content: PagerDuty 통합 설정(서비스 생성, Integration Key), Webhook 알림 설정(URL, 커스텀 헤더), Slack 알림 연동 패턴, 알림 채널 선택 전략

#### Section 4.4: Insights Agent

**4.4.1 Insights Agent의 작동 원리**
- learning_content: 4단계 프로세스(요약→클러스터링→범주화→세부분류), Summary Model vs Thinking Model 역할, 계층적 분류 구조, Executive Summary, 사용 패턴 분석 vs 실패 모드 발견

**4.4.2 Insights Agent 설정과 활용**
- learning_content: 자동 생성 방식(자연어 질문), 사용자 정의 속성(문자열/수치/Boolean), 필터 속성(filter_by), 시간 범위 필터링, 보고서 생성 시간(최대 15분), Plus/Enterprise 대상

---

### Phase 5: SDK 통합과 배포

**설명**: LangSmith SDK를 다양한 프레임워크에 통합하고 에이전트를 프로덕션에 배포하는 방법을 다룬다.

#### Section 5.1: SDK와 프레임워크 통합

**5.1.1 Python/TypeScript SDK 핵심 패턴**
- learning_content: SDK 설치(pip/npm), @traceable 내부 동작(RunTree 생성, 컨텍스트 전파, 배치 전송), wrap_openai/wrap_anthropic, RunTree 저수준 API, LANGSMITH_TRACING 없이 RunTree 사용

**5.1.2 LangChain/LangGraph 통합**
- learning_content: Zero-code 자동 트레이싱(환경 변수만으로), LangGraph 단계별 실행 시각화, 상태 전이 추적, 에이전트 추론 과정 디버깅, LangGraph Platform 자동 프로젝트 생성

**5.1.3 서드파티 프레임워크 통합**
- learning_content: CrewAI/AutoGen 통합 패턴, OpenAI Agents SDK/Claude Agent SDK 연동, Vercel AI SDK, LlamaIndex(OTel 브리지), 지원 프레임워크 11개 목록, 프레임워크 독립적 접근(4개 언어 SDK)

#### Section 5.2: API 참조

**5.2.1 LangSmith REST API 핵심 엔드포인트**
- learning_content: API 호스트(api.smith.langchain.com), 인증(x-api-key, X-Tenant-Id), Service Key vs Personal Token, 주요 엔드포인트(POST/PATCH /runs, /runs/query, /examples, /feedback), 배치 수집(batch vs multipart 처리량 비교)

**5.2.2 프로그래매틱 평가 API 활용**
- learning_content: API로 데이터셋 생성/예제 추가, 피드백 신호(수치 점수/카테고리 레이블), 실험 결과 조회, 관리 작업 자동화, 멀티테넌트 설정(X-Tenant-Id)

#### Section 5.3: 에이전트 배포 인프라

**5.3.1 LangSmith Deployment 아키텍처**
- learning_content: Control Plane(UI + API) vs Data Plane(Agent Server + 인프라), 단방향 폴링 설계(Data Plane이 Control Plane 폴링), Listener 애플리케이션, PostgreSQL/Redis/Autoscaler 역할, Development vs Production 배포 유형

**5.3.2 오토스케일링과 에이전트 특화 기능**
- learning_content: 오토스케일링 3개 메트릭(CPU 75%/메모리 75%/대기 실행 10개/컨테이너), 최대 10 레플리카, 장기 실행 에이전트 처리(하트비트/재시도), 버스티 부하 처리(태스크 큐, 더블 텍스팅 4가지 전략), Stateful 작업(체크포인터/메모리 스토어)

**5.3.3 Self-hosted LangSmith**
- learning_content: Kubernetes Helm 배포, Docker Compose(개발/소규모), 아키텍처 구성요소(Stateless 서비스 6개 + ClickHouse/PostgreSQL/Redis), 최소 요건(16 vCPU/64GB RAM), 인증 옵션(OAuth/SSO vs Basic), 데이터 보존 정책, Enterprise 전용 기능

---

## 커리큘럼 규모 요약

| Phase | Section 수 | Topic 수 |
|-------|-----------|---------|
| 1. 관찰성 기초 | 4 | 13 |
| 2. 평가 체계 | 5 | 11 |
| 3. 프롬프트 관리 | 3 | 7 |
| 4. 모니터링과 자동화 | 4 | 9 |
| 5. SDK 통합과 배포 | 3 | 8 |
| **합계** | **19** | **48** |

최소 50개 토픽 요건을 맞추려면 Phase 1의 Section 1.4를 2개 토픽으로 분리하거나, 각 Phase에서 중요 토픽을 1~2개 추가로 세분화하면 된다. 예를 들어 "LangSmith 계정 설정과 요금제" 입문 토픽, "테스트 자동화 CI/CD 통합" 토픽, "LangSmith 보안과 접근 제어" 토픽 등을 추가할 수 있다.
