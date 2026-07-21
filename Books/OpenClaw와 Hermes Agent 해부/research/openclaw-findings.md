# OpenClaw 심층 리서치 findings (기준일: 2026-07-21)

> 교재 집필용 내부 자료. 공식 문서·GitHub·Wikipedia·보안 보도 등 18개 이상 페이지를 실제 fetch하여 교차 검증한 결과다.
> 최종 교재 본문에는 출처 URL을 표기하지 않는다(내부 검증용으로만 사용).

## A. 정체와 역사

- 정체: OpenClaw는 "자유·오픈소스 자율 AI 에이전트로, LLM을 통해 작업을 실행하며 메신저 플랫폼을 주 사용자 인터페이스로 삼는다." 공식 문서는 "Any OS gateway for AI agents across Discord, Google Chat, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo, and more"로 자기 정의한다 (docs.openclaw.ai, Wikipedia).
- 제작자: Peter Steinberger (오스트리아 개발자, PSPDFKit 창업자). 자신을 "vibe coder"로 칭하며 2025년 11월 개인 실험 프로젝트로 시작. 전신은 Clawd(→ Molty로 개칭)라는 별도 프로젝트.
- 개명 연혁 (정확한 날짜): Warelay(2025-11-24) → CLAWDIS(2025-12-03) → Clawdbot(2026-01-02) → Moltbot(2026-01-27, Anthropic의 상표 이의 제기 후, 랍스터 테마 유지) → OpenClaw(2026-01-30, Steinberger가 "이전 이름이 입에 잘 붙지 않았다"고 언급).
- 라이선스: MIT License. 저장소 github.com/openclaw/openclaw. TypeScript/Node.js 기반.
- 스타 수 추이: Wikipedia 기준 2026-03-02에 247,000 stars / 47,700 forks. 2026-03-04경 250,000 stars 돌파. GitHub README 현재값은 384k stars / 80.6k forks. 리런치 48시간 만에 100k stars.
- 최신 버전: v2026.7.1 (2026-07-14 릴리스). 릴리스 태그 형식은 vYYYY.M.D(CalVer). 532 contributors. Control UI 전면 개편, GPT-5.6 및 Muse 지원. "장기 실행 에이전트를 보고·복구·거버넌스하기 쉽게" 만드는 안정판.
- 거버넌스/재단: 2026-02-14~15 Steinberger가 OpenAI 합류를 발표하며 OpenClaw를 재단으로 이관하겠다고 밝힘. 2026-07-08 OpenClaw Foundation을 501(c)(3) 비영리로 공식 출범(Dave Morin & Peter Steinberger 발표). Steinberger는 기술 스튜어드십 유지, OpenAI·NVIDIA·Microsoft·Tencent가 파트너로 참여. MIT 라이선스·오픈·독립 유지, 유급 maintainer 고용.
- 생태계 파장: Microsoft가 내부적으로 "Project Lobster"에서 "ClawPilot" 테스트(2026-05), Google이 경쟁 에이전트 "Remy" 개발 착수(2026-05), Tencent·Z.ai가 OpenClaw 기반 서비스 발표. 중국 정부는 2026-03 국유기업·정부기관 사무용 PC에서 OpenClaw 앱 실행을 제한("무단 데이터 삭제·유출, 과도한 에너지 사용" 사유).

## B. 전체 아키텍처

핵심 설계 원칙: "brains and muscles" — 외부 LLM(Claude 4.6, GPT-5.x, Ollama 로컬 등)이 '뇌', 로컬 설치본이 파일시스템·메신저와 상호작용하는 '근육'. 그리고 "software building software" — 새 기능이 필요하면 플러그인을 받는 게 아니라 에이전트에게 스스로 코드를 써서 확장하라고 요청.

1. Gateway (게이트웨이)
   - 역할: 단일 상시 실행 프로세스로 모든 메시징 표면을 소유(WhatsApp via Baileys, Telegram via grammY, Slack, Discord, Signal, iMessage, WebChat). 기본 바인딩 127.0.0.1:18789의 WebSocket 서버. 같은 포트에서 canvas HTTP(/__openclaw__/canvas/, /__openclaw__/a2ui/)도 서빙. cron 스케줄러도 게이트웨이 프로세스 내부에서 실행됨("Cron runs inside the Gateway process, not inside the model. The Gateway must be running for schedules to fire").
   - 왜: 공식 근거 — "호스트당 WhatsApp 세션이 하나만 존재하도록" 세션 충돌 방지 + 프로바이더 관리 중앙화 + 포트 파편화 제거. WebSocket은 스트리밍 응답과 실시간 이벤트를 위한 full-duplex 통신에 필요.
   - 개념/패턴: control plane / central hub (message broker), single-writer 패턴, full-duplex RPC over WebSocket.

2. Agent Runtime (내부 코어 = Pi)
   - 역할: 메시지를 액션+응답으로 바꾸는 실행 단위. 내부 코어는 Mario Zechner가 만든 미니멀 코딩 에이전트 Pi를 기반으로 하며 OpenClaw는 그 위에 채널 연결을 붙임. Pi는 "가장 짧은 시스템 프롬프트"와 Read/Write/Edit/Bash 4개 툴만 가진 tiny core.
   - 왜: 최소 코어 + 자기확장(코드가 코드를 작성·실행). Pi는 MCP를 의도적으로 미지원(mcporter로 CLI 노출로 대체) — 철학적 선택.
   - 개념/패턴: minimal-core + extension architecture, tree-structured sessions(브랜칭), model-agnostic SDK.

3. Sessions (세션) — 에이전트/워크스페이스별 격리 상태 (상세 C).

4. Control-plane clients (macOS 앱, CLI, Web Control UI, automations)
   - 역할: WebSocket으로 게이트웨이에 접속해 RPC(health, status, send, agent, system-presence) 요청 및 이벤트(tick, agent, presence, shutdown) 구독. Web Control UI는 Lit 웹컴포넌트 SPA, /chat에서 서빙.
   - 개념/패턴: client-server RPC, pub/sub 이벤트 스트림.

5. Nodes (노드, 컴패니언 디바이스) — role: node로 접속하는 주변장치 (상세 F).

6. Plugin channels (플러그인 채널) — 메신저 연동 (상세 F).

7. Skills / ClawHub — 스킬 시스템·레지스트리 (상세 E).

와이어 프로토콜: JSON 텍스트 프레임, 최초 connect 프레임 필수. 요청-응답 {type:"req", id, method, params} → {type:"res", id, ok, payload|error}, 서버 푸시 {type:"event", event, payload, seq?, stateVersion?}. 모든 연결은 nonce 챌린지 서명 필요(signature payload v3는 platform·device family까지 바인딩).

## C. 실행 모델

Agent loop 동작 순서 (5단계) — "the serialized, per-session run that turns a message into actions and a reply: intake, context assembly, model inference, tool execution, streaming, persistence":
1. agent RPC가 파라미터 검증·세션 해석·메타데이터 저장 후 즉시 { runId, acceptedAt } 반환(완료 대기 안 함).
2. agentCommand가 모델 기본값 해석·스킬 로드·runEmbeddedAgent 호출.
3. runEmbeddedAgent가 핵심 처리: per-session/global 큐로 run 직렬화, 모델+auth 프로파일 해석, OpenClaw 세션 빌드, 런타임 이벤트 구독, assistant/tool 델타 스트리밍, run timeout 강제.
4. subscribeEmbeddedAgentSession이 런타임 이벤트를 스트림별 라우팅(tool/assistant/lifecycle).
5. agent.wait이 lifecycle 종료/에러 폴링 후 { status: ok|error|timeout, startedAt, endedAt, error? } 반환.

lanes/queue 직렬화: run은 session key(session lane)별로 직렬화, 선택적으로 global lane 통과 → "tool/session races" 방지. 채널마다 큐 모드(steer/followup/collect/interrupt) 선택. 추가로 transcript 쓰기는 파일 기반 session write lock으로 보호(프로세스 인식, 다른 프로세스/인프로세스 큐 우회 writer도 차단). 기본 60초 타임아웃(OPENCLAW_SESSION_WRITE_LOCK_ACQUIRE_TIMEOUT_MS), non-reentrant 기본.

Session 관리·저장 포맷/경로:
- 라우팅: DM은 기본 공유 세션(session.dmScope로 조정: main/per-peer/per-channel-peer(권장)/per-account-channel-peer), 그룹/룸/채널은 격리, cron은 실행마다 새 세션, webhook은 hook별 격리.
- 저장: 런타임 세션 ~/.openclaw/agents/<agentId>/agent/openclaw-agent.sqlite(SQLite), 아카이브 transcript ~/.openclaw/agents/<agentId>/sessions/, 레거시 마이그레이션 소스 sessions.json. lifecycle 타임스탬프 sessionStartedAt/lastInteractionAt/updatedAt.
- 리셋 정책: none(compaction으로 성장 관리) / daily(기본 04시 새 세션) / idle(비활동 임계 후). 둘 다 설정 시 먼저 만료되는 쪽 승리. heartbeat·cron은 리셋 타이머를 연장하지 않음.
- 유지보수: session.maintenance { mode: "enforce", pruneAfter: "30d", maxEntries: 500 }.

Heartbeat vs Cron — 차이와 존재 이유:
- Heartbeat: 메인 세션 내부의 주기적 턴. 기본 주기 "30m"(Anthropic OAuth/토큰 인증 시 "1h"로 완화), "0m"로 비활성화. HEARTBEAT.md 체크리스트를 읽고 처리할 게 없으면 HEARTBEAT_OK 반환(기본 숨김). 주요 config: agents.defaults.heartbeat.{every, model, isolatedSession, lightContext, skipWhenBusy, target, activeHours}. 큐/레인/cron 바쁠 때, activeHours 밖, 파일이 빈 경우(reason=empty-heartbeat-file) 스킵. 존재 이유: 수동 프롬프트 없이 배경의 긴급 항목을 표면화하되 대화 문맥 유지·대화 스팸 회피.
- Cron: 게이트웨이 프로세스 내부의 분리된 백그라운드 작업(자체 task 레코드). 스케줄 문법 4종 — one-shot(--at), interval(--every), cron expr(--cron "0 9 * * 1"), exit trigger(--on-exit). 세션 타입 main/isolated(실행마다 새 transcript·세션ID)/current/session:custom-id. 페이로드 --system-event/--message/--command/--script. 저장은 SQLite(cron.store는 논리 키일 뿐 직접 편집 금지), sessionRetention: "24h". 비활성화 OPENCLAW_SKIP_CRON=1. 딜리버리 announce/webhook/none. 존재 이유: isolated run은 사람이 없는 무인 자동화용 — "최종 응답 자체가 산출물이어야 함". Heartbeat는 대화 신선도를 건드리지 않는 능동 모니터링, cron은 자율 배치 작업.

Sub-agent 지원: sessions_spawn 툴로 백그라운드 sub-agent를 deliver: false로 global subagent lane에 시작 → 즉시 { status: "accepted", runId, childSessionKey } 반환, 이후 반드시 sessions_yield로 현재 턴 종료 후 완료 이벤트를 다음 메시지로 수신(폴링 금지). 세션 키 agent:<agentId>:subagent:<uuid>. context 모드 isolated(기본, 토큰 절감)/fork(요청자 transcript 분기). sub-agent는 기본적으로 message 툴 미부여 + gateway/agents_list/session_status/cron 상실(툴 오용 방지). config: subagents.{maxSpawnDepth:1, maxChildrenPerAgent:5, maxConcurrent:8, runTimeoutSeconds:0, delegationMode:"suggest"}. maxSpawnDepth:2로 orchestrator 패턴(main→orchestrator→workers). 완료는 push 기반 announce(안정적 idempotency key, 실패 시 큐 라우팅→지수 백오프 재시도). 세션은 archiveAfterMinutes(기본 60) 후 *.deleted.<timestamp>로 rename 아카이브.

## D. 메모리 시스템

워크스페이스 파일 구조 (기본 경로 ~/.openclaw/workspace; OPENCLAW_PROFILE 설정 시 ~/.openclaw/workspace-<profile>; override는 OPENCLAW_WORKSPACE_DIR 또는 agents.defaults.workspace):
- SOUL.md — 페르소나·톤·경계. 매 세션 시작에 주입(개성 정의, "첫 번째로 주입되는 파일").
- IDENTITY.md — 에이전트 정체성/유저 호칭. 매 세션 로드.
- AGENTS.md — 에이전트 운영 지침(SOP): 규칙·메시지 라우팅·보안정책·스코프. 매 세션 시작 로드.
- USER.md — 함께 일하는 사람에 대한 컨텍스트("에이전트가 당신을 안다고 느끼게" 함).
- TOOLS.md — 로컬 툴·관례 노트(툴 가용성 제어 아님, 가이드일 뿐).
- HEARTBEAT.md — heartbeat 실행용 짧은 체크리스트(토큰 소모 방지 위해 짧게).
- STARTUP.md — 게이트웨이 재시작 시 자동 실행 체크리스트(옵션).
- ONBOARDING.md / BOOTSTRAP.md — 신규 워크스페이스 1회성 정체성 확립 의식. 워크스페이스가 구성 완료로 보이면 삭제.
- MEMORY.md — 큐레이션된 장기 기억(durable facts, preferences, decisions, 요약). 세션 시작에 로드.
- memory/YYYY-MM-DD.md (또는 -<slug>) — 일일 작업 노트·관찰·세션 요약·원시 컨텍스트.
- DREAMS.md(옵션), skills/, canvas/(예: canvas/index.html).
- 워크스페이스가 "구성됨"으로 간주되는 조건: SOUL.md/IDENTITY.md/USER.md가 스타터 템플릿에서 달라지거나 memory/ 폴더 존재.

컨텍스트 주입 방식: 장기 기억(MEMORY.md)은 세션 시작에 자동 로드하되, 부트스트랩 예산 초과 시 디스크 파일은 온전히 두고 컨텍스트 주입 사본만 truncate. 일일 노트는 memory_search/memory_get용으로 인덱싱되나 매 턴 부트스트랩 프롬프트에는 주입 안 함. 문자 제한: 파일당 agents.defaults.bootstrapMaxChars(기본 20,000), 전체 합계 agents.defaults.bootstrapTotalMaxChars(문서 소스에 따라 60,000 또는 150,000으로 상이 표기 — 수치 인용 시 주의).

Compaction 처리: 대화 compaction이 교환을 요약하기 직전, OpenClaw는 "silent turn"을 돌려 중요한 컨텍스트를 메모리 파일에 저장하라고 에이전트에 상기(자동 memory flush). config agents.defaults.compaction.memoryFlush.enabled. 설계 근거: durable 요약(MEMORY.md)과 작업 컨텍스트(memory/*.md)를 분리해 recall 효율과 컨텍스트 윈도 제약을 동시에 다루고 "no hidden state"(디스크에 쓴 것만 지속)를 보존.

## E. 스킬 시스템

SKILL.md 구조 (YAML frontmatter + markdown):
- 필수 frontmatter: name(스킬 식별자 겸 슬래시 명령), description.
- 선택: user-invocable(기본 true), disable-model-invocation(기본 false, 프롬프트엔 안 넣고 슬래시 명령만), command-dispatch: "tool" + command-tool(모델 우회해 툴 직접 호출), homepage.
- 게이팅 metadata.openclaw(JSON5): os("darwin"|"linux"|"win32"), requires.bins(PATH에 존재해야 하는 바이너리), requires.anyBins, requires.env(환경변수), requires.config(openclaw.json 경로가 truthy), always(모든 게이트 우회), primaryEnv.

로딩/디스커버리 — 6개 소스 엄격 우선순위(높→낮): (1) 워크스페이스 <workspace>/skills, (2) 프로젝트 에이전트 <workspace>/.agents/skills, (3) 개인 에이전트 ~/.agents/skills, (4) 관리형 ~/.openclaw/skills, (5) 번들(설치 동봉), (6) skills.load.extraDirs + 플러그인 스킬. 같은 이름이면 최상위 소스 승리. 최대 6단계 중첩.

프롬프트 진입: 세션 시작 시 (1) 게이팅·allowlist 적용해 유효 스킬 목록 해석, (2) env·API키를 process.env에 주입, (3) 유효 스킬을 compact XML 블록으로 컴파일해 시스템 프롬프트에 주입, (4) run 종료 후 원래 env 복원. 비용은 스킬당 결정적·선형(약 97자 + 필드 길이, 대략 24토큰). 예산 초과 시 skills.limits.maxSkillsPromptChars로 이름 우선 보존. 세션 시작 시 스냅샷, SKILL.md 변경 감지 또는 새 세션에만 반영.

ClawHub (공개 레지스트리 clawhub.ai): openclaw skills install @owner/<slug>, openclaw skills install git:owner/repo@ref, openclaw skills install ./path --as my-tool, --global(→ ~/.openclaw/skills). 커뮤니티 스킬 활성화 전 clawhub.skill.verify.v1 trust envelope 검증. config는 skills.entries.<name>.{enabled, apiKey, env, config}.

## F. 채널과 노드

지원 메신저 + 연결 라이브러리:
- WhatsApp — Baileys (QR 페어링, 디스크 상태 큼, install-on-demand)
- Telegram — grammY (Bot API, 봇 토큰만 필요, 가장 단순)
- Slack — Bolt SDK (워크스페이스 앱, 멀티-DM은 그룹챗으로 라우팅)
- Discord — Discord Bot API + Gateway
- Signal — signal-cli
- iMessage — macOS 네이티브 imsg 브리지(서명된 Mac 또는 SSH 래퍼 필요)
- WebChat — WebSocket (게이트웨이 내장 UI)
- 그 외 공식 플러그인: Matrix, IRC, LINE, Mattermost, Microsoft Teams, Google Chat, Feishu, Nextcloud Talk, Nostr, QQ Bot, SMS, Synology Chat, Tlon, Twitch, Voice Call, Zalo, Zalo Personal. 외부 플러그인: WeChat(Tencent iLink, QR), Yuanbao, Zalo ClawBot.
- 여러 채널 동시 실행 가능("configure multiple and OpenClaw will route per chat"). DM 페어링·allowlist 강제.

Nodes (모바일/데스크톱 컴패니언):
- 역할: macOS/iOS/watchOS/Android/headless Linux·Windows 주변장치가 role: "node"로 게이트웨이에 접속. 노드는 게이트웨이 서비스를 실행하지 않으며, 채널 메시지는 게이트웨이에 도착하지 노드에 도착하지 않음(관심사 분리).
- 명령 패밀리: canvas.present/canvas.eval/canvas.snapshot(WebView), camera.list/camera.snap/camera.clip, screen.record, location.get, system.run/system.which/system.notify, device.info/contacts.search/photos.latest/reminders.list 등.
- 페어링: 노드가 서명된 device identity 제시 → 게이트웨이가 role: node 페어링 요청 생성(5분 만료) → openclaw devices approve <requestId>로 승인 → device token 발급. 위험 명령(camera.snap, screen.record, sms.send)은 gateway.nodes.allowCommands로 명시적 opt-in 필요.
- 플랫폼별 기본: iOS=카메라·위치·연락처·사진·모션, Android=+SMS·알림·통화기록·헬스·설치앱, macOS=화면녹화·데스크톱 제어·접근성 입력, watchOS=최소(device info·알림).
- 설계 근거: 메시징·모델 오케스트레이션은 중앙 집중, 디바이스 고유 기능은 전문 엔드포인트로 분산 → 중앙 제어·감사 추적 유지하며 네이티브 센싱 활용.

## G. 모델 연동

- 지원 프로바이더: OpenAI, Anthropic, GitHub Copilot, OpenRouter, Ollama, LM Studio. 참조 형식 provider/model (예: openai/gpt-5.6, anthropic/claude-sonnet-4-6).
- 기본/권장 모델: 신규 셋업 시 OpenAI API키는 openai/gpt-5.6 선택, Anthropic은 유틸리티 작업에 claude-haiku-4-5 기본. heartbeat 기본 모델 예시는 anthropic/claude-opus-4-6. README상 OpenAI(ChatGPT/Codex)가 주요 구독 프로바이더로 소개.
- failover/라우팅: 계층적 폴백 체인 — (1) agents.defaults.model.primary → (2) agents.defaults.model.fallbacks(순차) → (3) 각 프로바이더 내부에서 auth-profile 로테이션 후 다음 fallback 모델로. 사용자가 /model로 명시 선택하면 그 세션에 strict(도달 불가 시 무음 폴백 대신 가시적 실패), 기본값은 전체 폴백 체인. auto-fallback은 임시 — 원 primary를 주기적으로 재프로브해 복구 시 auto 선택 해제. agents.defaults.modelPolicy.allow로 allowlist(정확 ref 또는 provider/* 접두 와일드카드), auth는 openclaw models auth CLI + SecretRef(해석된 시크릿이 아닌 소스 마커 저장).

## H. 보안

공식 보안 모델:
- 위협 모델: "personal-assistant trust boundary" — 게이트웨이당 신뢰 운영자 1인 전제. 적대적 멀티테넌트 경계가 아님. 3계층: identity first → scope next → model last("조작을 가정하고 blast radius를 제한하도록 설계").
- Pairing / DM 정책: 모든 DM 채널의 dmPolicy — pairing(기본 권장, 미지 발신자는 시간제한 페어링 코드 후 승인까지 무시)/allowlist/open(allowlist에 "*" 명시 opt-in 필요, 최후 수단)/disabled. sessionKey는 라우팅 셀렉터일 뿐 인증 토큰 아님(빈번한 오해).
- Gateway bind: gateway.bind = loopback(기본, 로컬만, 안전 baseline)/lan/tailnet/custom. 게이트웨이는 기본적으로 인증 요구(fail-closed, 유효 auth 경로 없으면 WebSocket 거부). auth 모드 token(권장, 긴 랜덤)/password(OPENCLAW_GATEWAY_PASSWORD)/trusted-proxy(trustedProxies 밖 프록시 헤더는 로컬 취급 안 함).
- Sandboxing: 기본 Docker 기반. agents.defaults.sandbox { mode:"all", scope:"agent"(에이전트별 컨테이너), workspaceAccess:"ro" }. workspaceAccess: none/ro(/agent 읽기전용 마운트)/rw(/workspace 읽기쓰기). 교차 에이전트 접근 방지는 scope:"agent" 유지 또는 "session".
- 프롬프트 인젝션 공식 입장: "시스템 프롬프트만으로 해결 안 됨(soft guidance)". 하드 강제는 툴 정책·exec 승인·샌드박싱·채널 allowlist. "모델 선택이 중요 — 인젝션 저항성은 tier마다 다르며, 툴 사용 에이전트나 비신뢰 콘텐츠를 읽는 에이전트를 약한 모델 tier에서 돌리지 말 것". 웹검색·붙여넣은 로그·첨부는 기본 적대적으로 취급. openclaw security audit [--deep|--fix|--json] 제공.

알려진 사고·취약점:
- CVE-2026-25253 (CVSS 8.8, CWE-669): Control UI의 gatewayUrl 쿼리 파라미터 부적절 처리 → 확인 없이 자동 WebSocket 연결로 authToken 탈취(Cross-Site WebSocket Hijacking) → loopback 바인딩이어도 로컬 게이트웨이 장악·RCE. 2026-02 초 공개, 2026.1.29 미만 버전 영향. 패치는 게이트웨이 URL 확인 모달 추가. 조치: 2026.1.29+ 업데이트 + 전체 auth 토큰 로테이션.
- 노출 인스턴스 사태: SecurityScorecard가 2026-02-09에 인터넷 직접 노출 40,214 인스턴스 / 28,663 고유 IP 발견, 63% 취약, 12,812건 RCE 가능, 549건 과거 침해 연관, 1,493건 알려진 취약점 연관. 지리적으로 중국>미국>싱가포르 집중. 다른 측정치: Bitsight 30,000+(1/27~2/8), The Register 135,000+, HackMag 220,000+ (측정 방식·시점 상이). 근본 원인: 기본 loopback이지만 Docker/VPS 배포 시 0.0.0.0:18789(또는 :::18789)로 바인딩 + 인증 미설정 "quick start" 문화.
- Endor Labs 6종 취약점(2026-02-18 공개): CVE-2026-26322(SSRF in Gateway tool, 7.6), CVE-2026-26319(Telnyx webhook 인증 누락, 7.5), CVE-2026-26329(browser upload path traversal, High), GHSA-56f2-hvwg-5743(image tool SSRF, 7.6), GHSA-pg2v-8xwh-qhcc(Urbit auth SSRF, 6.5), GHSA-c37p-4qqg-3p76(Twilio webhook 인증 우회, 6.5). 모두 패치됨.
- ClawJacked: 악성 웹사이트가 localhost 게이트웨이 포트로 WebSocket 열고 패스워드 brute-force해 에이전트 장악 → 2026.2.25+ 패치. Hunt.io는 /api/export-auth로 인증 없이 저장 API 토큰 접근 가능한 17,500+ 인스턴스 식별.
- 공급망(ClawHub): ClawHavoc 리포트가 악성 코드 포함 스킬 다수 발견(환경변수=API키·Slack토큰·DB크리덴셜 탈취). Cisco AI 보안팀이 2026-01-28 서드파티 스킬의 데이터 유출·프롬프트 인젝션 확인. VirusTotal이 "수백 개 악성 스킬"을 멀웨어 전달 채널로 탐지, Tom's Hardware는 2026-01 말 최소 14개 악성 스킬 문서화.
- 비-취약점(설계상): 정책/인증/샌드박스 우회 없는 순수 프롬프트 인젝션 체인, 단일 공유 호스트의 적대적 멀티테넌트 가정, loopback 전용 배포 findings는 no-action 처리.

## I. 실무 포인트

- 설치 요구사항: Node 22.22.3+ / 24.15+ / 25.9+(Node 24 기본, 인스톨러가 자동 처리). 지원 OS: macOS, Linux, Windows(네이티브 앱·PowerShell CLI·WSL2). 자동 인스톨러 curl -fsSL https://openclaw.ai/install.sh | bash (mac/Linux/WSL2), iwr -useb https://openclaw.ai/install.ps1 | iex (Windows PS). 패키지매니저 npm install -g openclaw@latest && openclaw onboard --install-daemon (pnpm은 pnpm approve-builds -g 추가, bun도 지원). 검증 openclaw --version / openclaw doctor / openclaw gateway status. 대시보드 http://127.0.0.1:18789/, 설정 파일 ~/.openclaw/openclaw.json.
- 데몬: openclaw onboard --install-daemon — macOS LaunchAgent, Linux/WSL2 systemd user service, Windows Scheduled Task(Startup 폴더 폴백).
- 권장 배포 형태: 로컬(loopback)이 안전 baseline. 컨테이너/클라우드 문서 지원 — Docker, Podman, Kubernetes, VPS(DigitalOcean, Hetzner, Fly.io, GCP, Azure, Railway, Render 선언형). 원격 노출 시 Tailscale Serve 등 identity-aware 접근 권장(게이트웨이 auth 모드에 trusted-proxy/tailnet 포함).
- API 토큰 비용 이슈: heartbeat가 기본 30분마다 도는 만큼 토큰 소모 관리가 핵심 — isolatedSession(세션 분리로 토큰 절감), lightContext(HEARTBEAT.md만 유지), tasks 블록(due 없으면 스킵), Anthropic OAuth/토큰 인증 시 주기 1h로 완화. sub-agent도 기본 isolated context로 토큰 하향. 스킬은 프롬프트당 스킬 수만큼 선형 토큰 비용(스킬당 ~24토큰+).
- 활용 사례: 아침 브리핑 cron(openclaw cron create "0 9 * * 1" "Summarize overnight updates." --session isolated --announce), 데일리 스탠드업(custom 세션으로 컨텍스트 누적), heartbeat 능동 모니터링, sub-agent 병렬 리서치/장기 작업, Voice Wake·Talk Mode, Live Canvas 시각 워크스페이스, 노드로 카메라·위치·화면녹화.
- 알려진 함정 & 베스트 프랙티스: (1) VPS 배포 시 0.0.0.0:18789 노출이 최대 함정 → gateway.bind: loopback 유지 + sudo ufw deny 18789/tcp. (2) 반드시 2026.2.25+로 패치 후 API키·OAuth 토큰 로테이션. (3) ClawHub 스킬은 검증·allowlist만 사용(공급망 위험). (4) 툴 사용 에이전트는 최신·강력 모델 tier 사용(약한 모델 인젝션 위험). (5) ~/.openclaw/ 권한 700/파일 600 + 풀디스크 암호화, 공유 호스트는 전용 OS 유저. (6) 멀티유저는 테넌트별 격리 게이트웨이. (7) 구성 변경·노출 전 openclaw security audit --deep 실행.

## 데이터 신뢰도 주의

- 스타 수(247k@2026-03 vs 384k 현재), 노출 인스턴스 수(30k~220k), bootstrapTotalMaxChars(60,000 vs 150,000)는 출처·시점별 편차가 있다. 교재 본문에서는 시점을 병기하거나 보수적 수치를 쓴다.
- 일부 2차 보안 매체가 기본 포트를 3000으로 표기하나 공식 문서·다수 소스는 18789이 정확 — 포트는 18789을 정본으로 사용한다.
