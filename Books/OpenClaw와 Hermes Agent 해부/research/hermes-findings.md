# Hermes Agent 심층 리서치 findings (기준일: 2026-07-21)

> 교재 집필용 내부 자료. 공식 문서 허브(hermes-agent.nousresearch.com/docs) 하위 아키텍처·메모리·스킬·보안·설치·FAQ·메시징 문서, GitHub README·릴리스, NVIDIA 공식 블로그, 제3자 분석 등 19개 페이지를 직접 읽고 교차 검증한 결과다.
> 최종 교재 본문에는 출처 URL을 표기하지 않는다(내부 검증용으로만 사용).
> 참고: hermes-agent.org는 공식 GitHub를 링크하는 서드파티 정보 사이트이며, 공식 사이트는 hermes-agent.nousresearch.com이다.

## A. 정체와 역사

- 제작사: Nous Research — Hermes 모델 시리즈를 만들어 온 AI 연구조직. 공식 문서가 "Built by model trainers at Nous Research"라고 명시.
- 공개: 2026년 2월 25일 GitHub 공개. 발표는 블로그가 아니라 트윗 한 줄 — "Meet Hermes Agent, the open source agent that grows with you".
- 라이선스: MIT. 주 언어 Python 81.6%. 저장소 github.com/NousResearch/hermes-agent.
- 공식 정의(README): "The self-improving AI agent built by Nous Research. It's the only agent with a built-in learning loop — it creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions".
- 2026-07-21 현재 상태: 약 218,000 stars / 41,100 forks, 최신 릴리스 v0.19.0 "The Quicksilver Release" (2026-07-20).
- 성장 타임라인(스냅샷별): 6주 57,200 stars·274+ 기여자(4/11) → 5/21 160,175 stars·26,000 forks·400 contributors·PyPI 주간 53,134 다운로드 → 3개월 140k+(NVIDIA 표기) → 4개월 미만 175k·390+ 기여자. 제3자 기사 간 수치 편차가 있으므로 날짜 없는 인용은 피할 것.
- OpenClaw fork 여부: 독자 구현이며 fork가 아님. "Hermes is not a fork. Built under an MIT license by Nous Research, it launched February 2026 as an independent project". 공식 README·FAQ에도 fork 서술은 전혀 없고, 대신 이주 도구만 제공: "If you're coming from OpenClaw, Hermes can automatically import your settings, memories, skills, and API keys" — hermes claw migrate 명령, hermes setup 마법사가 ~/.openclaw를 자동 감지. 기술적으로도 OpenClaw는 TypeScript/Node.js, Hermes는 Python으로 코드베이스가 다름.
- 배경 맥락: OpenClaw(2025-11 출시, 2026-01-30 리런치 48시간 만에 100k stars)의 창립자 Peter Steinberger는 2026년 2월 OpenAI에 합류했고 OpenClaw는 OpenAI가 후원하는 독립 재단으로 이관됨. 2026-04-03 "Anthropic blocking" 사건 이후 Hermes가 OpenClaw 대안으로 자리매김했다는 기록(Hermes Atlas 리포트).
- 릴리스 주기: v0.4.0(3/23, 버그픽스 200+·어댑터 6종 추가·OAuth 2.1), v0.8.0(4/8, 209 PRs·라이브 모델 전환), v0.13.0(5/7, "8 P0 fixes, default redaction on"), v0.17.0 "The Reach Release"(6/19, Photon 경유 iMessage), v0.18.0 "The Judgment Release"(7/1, "100% of P0 and P1 issues closed"·Mixture-of-Agents 정식 옵션), v0.18.1(7/7, 약 660 PRs 누적), v0.19.0(7/20, "First-turn time-to-first-token dropped ~80% on every platform").

## B. 전체 아키텍처

공식 개발자 문서(developer-guide/architecture)가 상세히 기술. 테스트 약 25,000개.

- AIAgent 코어 (run_agent.py) — (i) 모든 인터페이스가 공유하는 단일 에이전트 루프. provider 선택, 시스템 프롬프트 조립, 툴 실행·오류 복구, 대화 콜백(clarify/sudo/approval), SQLite 세션 저장 담당. chat completions·responses·Anthropic Messages 3가지 API 모드 지원. (ii) 공식 명시 이유: "one AIAgent class serves CLI, gateway, ACP, batch, and API server. Platform differences live in the entry point, not the agent" — 플랫폼별 동작 불일치 제거. (iii) 개념: 단일 코어 + 얇은 어댑터, Ports & Adapters(hexagonal architecture)식 분리.
- 엔트리포인트 3종 — CLI(cli.py, 대화형 TUI), Gateway(gateway/run.py, 상주 daemon), ACP Adapter(acp_adapter/, VS Code·Zed·JetBrains용 stdio/JSON-RPC). (iii) 개념: Adapter 패턴, JSON-RPC IPC.
- 프롬프트 시스템 (agent/prompt_builder.py) — (i) 시스템 프롬프트를 stable(에이전트 정체성·툴 안내·스킬 목록) → context(컨텍스트 파일) → volatile(메모리·프로필·타임스탬프) 3계층 순서로 조립. prompt_caching.py가 Anthropic prefix caching 브레이크포인트 적용, context_compressor.py가 임계 초과 시 중간 턴을 lossy 요약. (ii) 공식 이유: "Prompt Stability — 시스템 프롬프트는 대화 중 불변(/model 같은 명시 동작 제외)" + 메모리의 "frozen snapshot pattern"으로 LLM prefix cache 성능 보존. (iii) 개념: prompt cache 최적화를 위한 안정 프리픽스 배치, 계층형 컨텍스트 조립.
- Provider 런타임 해석 (hermes_cli/runtime_provider.py) — (i) (provider, model) 튜플을 (api_mode, api_key, base_url)로 매핑. 18+ 프로바이더, OAuth 플로우, credential pool, 모델 alias 처리. CLI·gateway·cron·ACP가 동일 resolver 사용. (iii) 개념: Resolver/Registry, 설정과 실행의 분리.
- 툴 시스템 (tools/registry.py) — (i) 약 28개 toolset에 70+ 툴. 각 툴이 JSON schema 선언, model_tools.py가 디스패치. import 시점에 registry.register()로 자기등록 — "no manual enrollment lists". (ii) 명시 이유: Loose Coupling — 선택 서브시스템(MCP·플러그인·메모리·RL)은 registry 패턴과 조건부 게이팅 사용. (iii) 개념: Registry 패턴 + import-time self-registration(플러그인 발견).
- 터미널 백엔드 6종 (tools/environments/) — (i) local, Docker, SSH, Daytona, Modal, Singularity. (ii) 이유: 실행 격리 수준을 배포 환경에 맞게 선택(보안 문서 — local은 위험명령 검사, docker는 컨테이너가 경계). (iii) 개념: Strategy 패턴, sandbox boundary.
- 세션 저장소 (hermes_state.py) — (i) SQLite + FTS5 전문검색. 압축 전후 lineage(parent/child) 추적, 플랫폼별 격리, atomic write. (iii) 개념: embedded DB, full-text search.
- 메시징 Gateway (gateway/) — (i) 플랫폼 어댑터들을 관리하는 daemon. 각 어댑터가 네이티브 이벤트를 통일된 MessageEvent로 변환. 인증(allowlist + DM pairing), slash command 디스패치, hook 시스템, cron 실행 담당. (iii) 개념: Message Gateway/Adapter 패턴, 이벤트 정규화.
- 플러그인 시스템 — (i) ~/.hermes/plugins/(사용자), .hermes/plugins/(프로젝트), pip entry point 3경로 발견. 툴·훅·CLI 명령 등록. memory provider와 context engine은 single-select 특수 타입. (iii) 개념: entry-point 기반 플러그인 아키텍처.
- Cron (cron/) — (i) "First-class agent tasks (not shell scripts)". 잡은 JSON 저장, 스킬·스크립트 첨부, 결과를 임의 플랫폼으로 배달. (ii) 이유(추정): 셸 크론 대신 에이전트 프롬프트를 스케줄링해 스킬·메모리 자산을 재사용.
- MLOps 계층 — (i) batch_runner.py 배치 트래젝토리 생성, Atropos 연동 RL 학습, ShareGPT 포맷 trajectory export. (ii) 이유(추정): 모델 트레이너인 Nous가 에이전트 사용 데이터를 학습 플라이휠로 쓸 수 있게 설계 — 문서 명시 근거는 "Built by model trainers" 표현뿐.
- 공식 설계 원칙 6개(문서의 표 그대로): Prompt Stability / Observable Execution(모든 툴 호출을 콜백으로 가시화) / Interruptible(API 호출·툴 실행 취소 가능) / Platform-Agnostic Core / Loose Coupling / Profile Isolation(-p <name>별 HERMES_HOME·설정·메모리·세션·gateway PID 분리).
- NVIDIA 블로그의 공식 표현: "Self-Evolving Skills", "Contained Sub-Agents", "Reliability by design", "an active orchestration layer, not a thin wrapper".

## C. 실행 모델

- 프로세스 모델 4종: CLI(단일 사용자·대화형·종료 시 소멸), Gateway(상주 daemon, 프로필별 PID 격리로 다중 인스턴스 동시 실행), ACP(에디터가 spawn하는 stdio 서브프로세스), Cron(gateway에 내장되어 tick).
- Daemon 구동: hermes gateway install(user/system 서비스 등록), start, stop, status.
- 데이터 플로우(공식 문서 기술): CLI는 HermesCLI.process_input() → AIAgent.run_conversation() → 프롬프트 조립 → provider 해석 → API 호출 → 툴 디스패치 루프 → SQLite 저장. Gateway는 플랫폼 이벤트 → 어댑터 → MessageEvent → GatewayRunner._handle_message() → 인증 → 세션 해석 → 히스토리 로드한 AIAgent 생성 → 어댑터로 배달.
- Cron 잡 실행: 스케줄러 tick → 만기 잡 로드 → 히스토리 없는 fresh AIAgent 생성 → 스킬을 컨텍스트로 주입 → 실행 → 지정 플랫폼 배달 → 상태 갱신. 랜딩 페이지 표현: "Natural-language scheduling for reports, backups, and briefings — running unattended through the gateway, focused every time".
- 멀티세션: 세션은 리셋 전까지 메시지 간 유지("persist across messages until they reset"), /title 세션명으로 명명, CLI에서 hermes -c로 복원. 그룹챗에서는 [SILENT], NO_REPLY 등 silence token으로 응답 억제하면서 히스토리 유지.
- 서브에이전트: "Isolated subagents with their own conversations, terminals, and Python RPC scripts for zero-context-cost pipelines" — delegate_task 툴로 병렬 위임.

## D. 메모리 시스템

- 2층 파일 + 1층 DB 구조. 파일: ~/.hermes/memories/의 MEMORY.md(2,200자 제한 ≈ 800토큰 — 환경 사실·프로젝트 컨벤션·툴 특성·교훈)와 USER.md(1,375자 제한 ≈ 500토큰 — 정체성·타임존·커뮤니케이션 선호·기술 수준). DB: ~/.hermes/state.db SQLite + FTS5에 모든 CLI·메시징 세션 저장.
- 큐레이션 방식: memory 툴의 add/replace(부분문자열 매칭)/remove 3동작. 핵심 설계 — "memory does not auto-compact: when a write would exceed the limit, the memory tool returns an error" → 에이전트가 스스로 통합·정리하도록 강제. 제한된 용량이 "focused, curated content"를 강제한다고 명시.
- "never forgets" 구현의 실체 = 3계층 조합: (1) 항상 로드되는 소형 큐레이션 파일(frozen snapshot으로 세션 시작 시 1회 주입 — prefix cache 보존 목적 명시), (2) 무제한 세션 아카이브를 FTS5로 검색(hermes sessions list, 요약 없이 원문 검색), (3) 절차 지식은 스킬 파일로 이관. 제3자 분석: "context retrieval is deterministic rather than probabilistic" — 벡터 검색 대신 결정적 조회.
- 축적 방식: "Agent-curated memory with periodic nudges" — 에이전트가 주기적 넛지를 받아 기억할 가치를 판단. auxiliary.background_review로 백그라운드 리뷰를 저렴한 모델로 라우팅 가능.
- 사용자 모델링: "Honcho dialectic user modeling" — 세션을 거듭하며 사용자 심층 프로필 구축.
- 외부 memory provider 플러그인 8종: Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory — hermes memory setup으로 설정, knowledge graph·semantic search 등 보강.
- 설정 키: memory_enabled, write_approval(쓰기 승인 게이트), memory_char_limit: 2200, user_char_limit: 1375, display.memory_notifications: off|on|verbose. 저장 전 injection 패턴·credential 유출 스캔.

## E. 자가 개선 스킬 시스템

- 스킬 = 필요 시 로드되는 온디맨드 지식 문서. 포맷: SKILL.md + YAML frontmatter(name, description, version, platforms, metadata.hermes.tags/category) + 본문 섹션 When to Use / Procedure / Pitfalls / Verification. 저장 위치: ~/.hermes/skills/가 "the primary directory and source of truth".
- 자동 생성 트리거: skill_manage 툴로 에이전트가 "completed a complex task (5+ tool calls) successfully" 또는 "discovered a non-trivial workflow"일 때 스스로 생성. 동작: create / patch(토큰 효율적 부분 수정 — 사용 중 자가 개선의 실제 메커니즘) / edit(구조 개편) / delete / write_file·remove_file(보조 파일).
- 토큰 관리: "progressive disclosure pattern to minimize token usage" — Level 0 skills_list() 메타데이터(~3k tokens) → Level 1 skill_view(name) 전문 → Level 2 skill_view(name, path) 개별 파일. /skill-name slash 호출, 스킬 스태킹 가능.
- 승인 게이트: skills.write_approval: true 설정 시 에이전트 작성 스킬이 ~/.hermes/pending/skills/에 스테이징되어 /skills pending, /skills approve [id]로 인간 검토.
- 표준·생태계: agentskills.io 오픈 표준 호환. 설치 소스 7종 — official, skills.sh(Vercel), /.well-known/skills/index.json 엔드포인트, GitHub 직접(openai/skills, anthropics/skills), hermes skills tap add 커스텀 탭, 직접 URL, 커뮤니티(ClawHub·LobeHub·browse.sh). 명령: hermes skills browse/search/install/check/update, 번들은 ~/.hermes/skill-bundles/ YAML로 스킬 묶음+지침 정의.
- 설치 보안: 허브 스킬 전수 보안 스캔, trust level builtin~community, "--force does not override a dangerous scan verdict".
- 번들 스킬: 랜딩 기준 40+ 내장 (예: plan, axolotl, github-pr-workflow, duckduckgo-search, excalidraw, ocr-and-documents), 커뮤니티 스킬 라이브러리 17종(4월 기준, 최대 4,132 stars).
- 효과 주장: "agents with 20+ self-created skills complete similar tasks 40% faster" (Nous 벤치마크 인용, 토큰·wall-clock 기준) — 제3자 전달이므로 원 벤치마크는 미확인. 교재에서는 주장 출처의 성격을 밝히지 말고 수치 단정을 피하며 서술.

## F. 채널과 통합

- "16+" 주장은 검증되며 실제로는 초과 — 공식 메시징 문서 기준 24개 플랫폼: Telegram(bot token), Discord(bot token), Slack(OAuth), Google Chat(OAuth), WhatsApp(Baileys 브리지·QR 스캔), WhatsApp Cloud API, Signal(전화번호 pairing), SMS(Twilio), Email(SMTP/IMAP), Home Assistant, Mattermost, Matrix(homeserver), DingTalk, Feishu/Lark, WeCom, WeCom Callback, Weixin(WeChat), BlueBubbles(iMessage — Mac 서버 필요), QQBot, Yuanbao, Microsoft Teams, LINE, ntfy(webhook), IRC.
- 시점별 증가: 4월 14개 → 6/19 v0.17.0에서 Photon 경유 iMessage 추가 → 7월 24개. 아키텍처 문서는 "20 platform adapters"로 기술(문서 갱신 시차).
- 연결 구조: 단일 gateway daemon이 전 플랫폼을 통합 라우팅, 어댑터가 네이티브 이벤트를 MessageEvent로 정규화. 모든 채널이 동일한 메모리·세션 스토어 공유("unified memory").
- 그 외 통합: MCP 클라이언트(tools/mcp_tool.py, 임의 MCP 서버 연결), ACP로 IDE 통합, Home Assistant·Obsidian·Google Workspace·k8s 등 실사용 보고.

## G. 모델 연동

- Model-neutral 구조: runtime_provider.py가 18+ 프로바이더를 단일 인터페이스로 추상화, chat completions·responses·Anthropic Messages 3가지 API 모드 지원. hermes model로 구성, /model로 대화 중 전환(v0.8.0부터 라이브 전환).
- 지원 경로: Nous Portal(OAuth), OpenRouter(200+ 모델), OpenAI, 커스텀 OpenAI 호환 endpoint, 로컬 vLLM. Ollama·LM Studio는 "out-of-the-box", llama.cpp 서버도 연결 가능.
- Nous Portal 구조: "Nous Research's unified subscription gateway". hermes setup --portal → 브라우저 OAuth → refresh token을 ~/.hermes/auth.json에 저장하고 요청마다 단기 JWT 발행("eliminating long-lived API key exposure"). "300+ frontier models, one bill" — Claude Opus 4.7/4.6·Sonnet 4.6, GPT-5.5/5.5 Pro/5.3 Codex, Gemini, DeepSeek, Qwen, Kimi, GLM 등. 툴 게이트웨이 포함: Firecrawl 웹검색, FAL 이미지 생성(9모델), OpenAI TTS, Browser Use 클라우드 브라우저, Modal 클라우드 샌드박스(애드온). hermes portal info로 구독 상태 확인.
- Portal 가격(제3자 정리·Teknium 트윗 교차): Free $0(pay-as-you-go 크레딧 $10부터), Plus $20/월($22 크레딧), Super $100/월($110 크레딧), Ultra $200/월 + 가입·갱신 보너스 크레딧. 공식 문서 자체는 가격을 싣지 않음.
- 자사 Hermes 4 모델과의 관계(주의): Portal에서 Hermes-4-70B·Hermes-4-405B를 "heavily discounted rates"로 제공하지만, 공식 문서가 "not recommended for use inside Hermes Agent"라고 명시 — chat 최적화 튜닝이라 고속 tool-calling에 부적합. 즉 이름만 공유할 뿐 에이전트가 자사 모델 종속이 아님.
- 로컬/NVIDIA: DGX Spark(128GB unified memory, 1 PFLOP)와 RTX PC·RTX PRO 워크스테이션 공식 지원. "up to 3x faster token generation running Qwen 3.6 models with llama.cpp"(RTX PRO), Qwen 3.6 35B는 약 20GB VRAM으로 120B급 성능이라고 소개(수치는 원문 재확인 권장 — 보수적으로 서술). 무료 로컬 가이드 /docs/guides/run-nemotron-3-ultra-free도 별도 존재.
- v0.18.0부터 Mixture-of-Agents가 first-class 모델 옵션.
- OpenRouter "가장 많이 쓰이는 에이전트" 주장 근거: NVIDIA 공식 블로그가 "most used agent in the world according to OpenRouter"라고 인용. 수치 근거 — 5/10 일일 224B tokens vs OpenClaw 186B로 #1 등극(누적은 당시 OpenClaw 9.17T > Hermes 6.35T), 5/21 일일 458B(#1) vs 173B(#2), 누적도 8.14T vs 7.18T로 역전. 일일·누적 모두 1위라는 서술은 5월 중순 이후 스냅샷 기준.

## H. 보안

- 공식 8층 "defense-in-depth security model": user authorization / dangerous command approval / file write safety / container isolation / MCP credential filtering / context file scanning / cross-session isolation / input sanitization.
- 실행 격리: terminal.backend — local(위험명령 검사 활성), ssh, docker(컨테이너가 경계: --cap-drop ALL + 선별 복원, --security-opt no-new-privileges, --pids-limit 256, tmpfs nosuid/noexec), singularity/modal/daytona.
- 명령 승인: approvals.mode smart(기본 — 보조 LLM이 위험도 평가, 저위험 자동 승인)/manual/off. 하드라인 블록리스트는 YOLO 모드(--yolo, HERMES_YOLO_MODE=1)에서도 유지: rm -rf /, fork bomb :(){ :|:& };:, 파일시스템 포맷, 신뢰 불가 URL의 shell 파이프. approvals.deny로 fnmatch 글롭 거부 규칙, approvals.timeout 기본 60초(무응답=거부).
- 파일·자격증명 보호: ~/.ssh/, ~/.aws/, ~/.kube/, /etc/sudoers, auth.json, .env 계열 항시 쓰기 차단. HERMES_WRITE_SAFE_ROOT로 쓰기 샌드박스. terminal/execute_code에서 KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|AUTH 포함 환경변수 자동 제거, MCP 서브프로세스는 PATH, HOME 등 최소 집합만 통과, 에러 메시지에서 ghp_...·sk-...·bearer token 자동 redaction.
- 프롬프트 인젝션 방어: 컨텍스트 파일을 시스템 프롬프트 포함 전 스캔(지시 무력화 문구, 숨김 HTML 주석, zero-width 유니코드, curl 유출 시도) → "[BLOCKED: <filename> contained potential prompt injection]". Tirith pre-exec 명령 스캐너(SHA-256 검증 설치, homograph·pipe-to-interpreter 탐지). SSRF 방어 상시 활성: RFC1918·loopback·link-local(클라우드 메타데이터 169.254.169.254 포함)·CGNAT 차단 + 리다이렉트 체인 재검증.
- Gateway 인증: 6단계 판정 순서(플랫폼 allow-all → DM pairing 승인 목록 → 플랫폼 allowlist → 글로벌 allowlist → 글로벌 allow-all → 기본 거부). DM pairing: 8자 코드·1시간 TTL·10분당 1회 제한·5회 실패 시 1시간 잠금·chmod 0600.
- 공급망: hermes_cli/security_advisories.py가 오염 패키지(예: poisoned mistralai) 경고, lazy dependency는 in-tree allowlist + PyPI 이름 설치만 허용(git/file URL 금지).
- 텔레메트리 없음 주장 검증: FAQ 원문 — "Hermes Agent does not collect telemetry, usage data, or analytics. Your conversations, memory, and skills are stored locally in ~/.hermes/", "API calls go only to the LLM provider you configure". 오픈소스라 코드 검증 가능하나 독립 감사 자료는 발견 못함.
- 보안 실적·비판: 2026-05 기준 agent-specific CVE 0건 vs OpenClaw는 2026-03 한 달에 9 CVEs(최고 CVSS 9.9). 비판 — "memory is a liability as well as a feature. An agent that remembers everything also stores everything", "Treat auto-generated skills as drafts that need your approval", "Do not expose the web UI publicly without authentication", "For mission-critical automation — treat it as maturing, not mature", SQLite 세션 아카이브는 파일 기반 대비 가독성이 낮아 감사가 어려움.

## I. 실무 포인트

- 설치: curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash — 실제 동작: Python 3.11(uv 경유)·Node.js v22·ripgrep·ffmpeg 자동 설치, repo를 ~/.hermes/hermes-agent/에 클론, venv 구성, ~/.local/bin/hermes 심링크. 전제조건은 git뿐(Linux는 curl·xz-utils 추가). Windows 네이티브는 iex (irm https://hermes-agent.nousresearch.com/install.ps1).
- 지원 OS: Linux, macOS, WSL2, Windows 네이티브, Android(Termux). 데스크톱 앱 별도 제공(macOS 12+, Windows 10/11, Linux). 설치 후 hermes setup(마법사, ~/.openclaw 감지 시 마이그레이션 제안), hermes model, hermes tools, hermes gateway setup. 업데이트는 hermes update가 설치 방식(pip/git/Homebrew/NixOS)을 감지해 안내.
- 하드웨어·비용: 공식 최소 사양 미명시. 실사용 보고 — $5~20/월 VPS(Hetzner·DigitalOcean), Raspberry Pi 4, Mac Mini, "32GB Ubuntu laptop에서 4-agent 시스템 24/7 systemd 운영", k8s + 공유 PVC 엔터프라이즈 배포. 소프트웨어는 무료, 비용 = LLM API + 호스팅. 실측 월 비용: API $30-65, 총액 $15-50. 한 사용자는 OpenRouter 조합 전환으로 토큰 지출 90% 절감($130→$10/5일).
- 활용 사례(공식 user-stories 145건 분류): personal assistant 44건(이메일 요약·일정·저널링), developer workflow 65건(코드리뷰 자동화·멀티에이전트 파이프라인), business ops 16건(티켓 트리아지·영업), research 9건, content 11건. 패턴 예: "Hermes가 Telegram으로 태스크를 받아 Claude Code 세션을 spawn해 코딩을 시키고 결과를 회신".
- 알려진 함정: WSL2에서 "WSL's systemd support is unreliable" → gateway는 foreground/tmux 권장, WSL2 Chrome 제어는 /browser connect 대신 MCP bridge 권장. 모델 전환·credential 회전이 prefix cache를 무효화해 "다음 턴 전체 재과금". 로컬 모델은 직접 실행보다 느릴 수 있음. Docker에서 pairing 승인은 -u hermes 필요. Windows 파일 쓰기는 encoding="utf-8" 명시.
- 베스트 프랙티스(공식 tips): 프로젝트 루트 AGENTS.md(자동 주입), ~/.hermes/SOUL.md로 페르소나 고정, 기존 .cursorrules 자동 인식, /compress로 컨텍스트 요약, /usage·/insights(30일 패턴), /sethome으로 cron 배달 채널 지정, delegate_task로 병렬화, 프로덕션은 terminal.backend: docker + 플랫폼별 allowlist + DM pairing + 비root 실행 + ~/.hermes/logs/ 모니터링, GATEWAY_ALLOW_ALL_USERS=true 절대 금지.
- OpenClaw 대비 선택 기준(제3자): 메모리 감사 가능성(파일 기반)·관리형 호스팅·멀티모델 라우팅이 필요하면 OpenClaw, "an agent that genuinely improves over months of use"와 저비용 VPS 자가호스팅이 목적이면 Hermes.

## 데이터 신뢰도 주의

- 스타 수는 출처마다 스냅샷 시점이 달라 114k(5/10)~218k(7/21)로 편차 — 날짜와 함께 인용하거나 시점을 뭉뚱그리지 말 것.
- "40% faster" 벤치마크는 자체 주장의 제3자 전달로 원자료 미확인 — 단정 서술 금지.
- 초기 버전 사용기(제3자)의 "6개 플랫폼"·"self-learning 기본 비활성"은 현행 공식 문서(24개 플랫폼, 자동 스킬 생성 내장)와 상충 — 현행 공식 문서를 정본으로 삼는다.
