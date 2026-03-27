# Claude Code 핵심 기능 가이드

## 목차
1. [기술적 배경과 해결하려는 문제](#기술적-배경과-해결하려는-문제)
2. [CLAUDE.md](#1-claudemd---영구-지시-시스템)
3. [Subagents](#2-subagents---하위-에이전트-시스템)
4. [Skills](#3-skills---재사용-가능한-워크플로우)
5. [Hooks](#4-hooks---라이프사이클-자동화)
6. [기능 비교표](#기능-비교표)
7. [실전 프로젝트 구성 예시](#실전-프로젝트-구성-예시)

---

## 기술적 배경과 해결하려는 문제

### LLM 기반 코딩 에이전트의 근본적 한계

Claude Code는 LLM(대규모 언어 모델) 기반의 CLI 코딩 에이전트다. LLM에는 몇 가지 근본적 한계가 있고, 아래 4가지 기능은 각각 특정 한계를 해결하기 위해 설계되었다.

| 문제 | 원인 | 해결 기능 |
|------|------|-----------|
| **세션 간 기억 상실** | LLM은 대화가 끝나면 모든 컨텍스트를 잃음 | **CLAUDE.md** |
| **컨텍스트 윈도우 한계** | 한 번에 처리할 수 있는 토큰 수 제한 | **Subagents** |
| **반복 작업의 비일관성** | 같은 지시를 매번 다시 해야 하고, 매번 결과가 다를 수 있음 | **Skills** |
| **비결정적 행동** | LLM은 확률적으로 동작하므로 "항상" 특정 행동을 보장할 수 없음 | **Hooks** |

### 왜 이 4가지가 필요한가?

**CLAUDE.md** - LLM은 stateless하다. 어제 대화에서 "우리 프로젝트는 2-space 인덴트를 쓴다"고 알려줘도, 오늘 새 세션에서는 모른다. CLAUDE.md는 매 세션 시작 시 자동으로 로드되는 영구 지시 파일로, 프로젝트의 규칙과 컨텍스트를 항상 주입한다.

**Subagents** - 복잡한 코드베이스에서 탐색, 분석, 수정을 한 컨텍스트에서 모두 하면 윈도우가 금방 찬다. Subagent는 독립된 컨텍스트 윈도우에서 작업하고 요약만 반환하므로, 메인 대화의 컨텍스트를 보호한다.

**Skills** - "PR 리뷰해줘"라고 매번 같은 10줄짜리 지시를 반복하는 것은 비효율적이다. Skills는 재사용 가능한 프롬프트/워크플로우를 파일로 정의하고 `/명령어`로 즉시 호출한다.

**Hooks** - "파일 수정 후 반드시 prettier를 돌려라"라고 CLAUDE.md에 써도, LLM이 가끔 빼먹을 수 있다. Hooks는 특정 이벤트에 셸 명령을 **자동 실행**하여 결정론적(deterministic) 동작을 보장한다.

---

## 1. CLAUDE.md - 영구 지시 시스템

### 개념

CLAUDE.md는 Claude에게 프로젝트별 지시사항을 전달하는 마크다운 파일이다. 매 세션 시작 시 자동으로 로드되어, 코딩 규칙, 빌드 명령어, 아키텍처 정보 등을 Claude가 항상 알고 있게 한다.

### 배치 위치와 로딩 우선순위

| 스코프 | 위치 | 우선순위 | 용도 |
|--------|------|----------|------|
| **관리 정책** | `C:\Program Files\ClaudeCode\CLAUDE.md` | 최고 | 조직 전체 (IT 관리, 제외 불가) |
| **프로젝트** | `./CLAUDE.md` 또는 `./.claude/CLAUDE.md` | 높음 | 팀 공유 (VCS에 커밋) |
| **사용자** | `~/.claude/CLAUDE.md` | 중간 | 개인 설정 (모든 프로젝트 적용) |
| **하위 디렉토리** | `./<subdir>/CLAUDE.md` | 낮음 | 해당 디렉토리 파일 접근 시 lazy-load |
| **규칙 파일** | `./.claude/rules/*.md` | 중간 | 주제별, 경로별 규칙 |

Claude Code는 작업 디렉토리에서 상위로 올라가며 모든 CLAUDE.md를 찾아 로드한다.

### CLAUDE.md에 넣어야 할 것 vs 넣지 말아야 할 것

**넣어야 할 것:**
- 빌드/테스트 명령어 (`npm test`, `cargo build`)
- 코딩 컨벤션 (인덴트, 네이밍, 패턴)
- 프로젝트 아키텍처와 모듈 구조
- 일반적인 워크플로우와 프로세스
- 디버깅 팁과 알려진 이슈

**넣지 말아야 할 것:**
- 개인 선호 (→ `~/.claude/CLAUDE.md` 사용)
- 대량의 참조 문서 (→ `@` import로 분리)
- 민감한 정보 (→ 환경변수나 `.local.json` 사용)
- 가끔만 필요한 지시 (→ Skills 사용)

### 작성 원칙

- **200줄 이하**를 목표로 한다. 길면 컨텍스트를 많이 소모하고 준수율이 떨어진다.
- **구체적으로** 작성한다: "코드를 잘 포맷해라" ✗ → "2-space 인덴트를 사용해라" ✓
- **검증 기준**을 포함한다: Claude가 실행할 수 있는 확인 명령어
- **예제**를 넣는다: 좋은 패턴과 나쁜 패턴을 비교

### 파일 import

```markdown
# 프로젝트 개요
자세한 내용은 @README 참조

# Git 워크플로우
@docs/git-instructions.md 참조

# 개인 설정
@~/.claude/my-project-instructions.md
```

`@path` 구문으로 외부 파일을 불러올 수 있다. 상대경로는 importing 파일 기준, 최대 5단계 깊이까지 지원.

### .claude/rules/ 디렉토리

대규모 프로젝트에서는 주제별 규칙 파일로 분리할 수 있다:

```
.claude/
├── CLAUDE.md
└── rules/
    ├── code-style.md      # 항상 로드
    ├── testing.md          # 항상 로드
    └── frontend/
        └── react.md        # 경로 조건부 로드 (아래 참조)
```

경로 스코프 규칙 (특정 파일 작업 시에만 로드):

```yaml
---
paths:
  - "src/components/**/*.tsx"
  - "src/**/*.handler.ts"
---

# React 컴포넌트 규칙
- 모든 컴포넌트는 props 타입을 명시할 것
- 커스텀 훅은 use 접두사를 붙일 것
```

### 효과적인 상황

- 팀 전체가 동일한 코딩 규칙을 따르게 하고 싶을 때
- 새 팀원(또는 자기 자신)이 새 세션을 시작할 때마다 같은 설명을 반복하지 않고 싶을 때
- 프로젝트별 빌드/배포 명령어가 다를 때

---

## 2. Subagents - 하위 에이전트 시스템

### 개념

Subagent는 독립된 컨텍스트 윈도우에서 특정 작업을 수행하는 전문 에이전트다. 메인 대화와 분리되어 실행되고, 작업 결과(요약)만 반환한다.

### 내장 Subagent 종류

| Agent | 모델 | 도구 | 용도 |
|-------|------|------|------|
| **Explore** | Haiku (빠름) | 읽기 전용 | 코드베이스 탐색, 검색 |
| **Plan** | 상속 | 읽기 전용 | 구현 전략 설계 |
| **General-purpose** | 상속 | 전체 | 복잡한 멀티스텝 작업 |

### 핵심 동작 방식

**격리(Isolation):**
- 각 subagent는 별도의 컨텍스트 윈도우에서 동작
- 메인 대화의 컨텍스트를 소모하지 않음
- Subagent끼리 중첩 호출 불가 (무한 재귀 방지)

**컨텍스트:**
- CLAUDE.md는 subagent에도 로드됨
- 부모 세션의 권한을 상속하되, 도구 제한 가능
- 매 호출마다 새로운 인스턴스 생성 (SendMessage로 이전 에이전트 재개 가능)

### 커스텀 Subagent 만들기

`.claude/agents/code-reviewer/SKILL.md`:

```yaml
---
name: code-reviewer
description: 코드 변경 후 자동으로 리뷰. 사전에 적극적으로 사용.
tools: Read, Grep, Glob, Bash
model: sonnet
maxTurns: 10
---

당신은 시니어 코드 리뷰어입니다. 호출 시:

1. git diff로 최근 변경사항 확인
2. 수정된 파일에 집중
3. 우선순위별 피드백:
   - Critical (반드시 수정)
   - Warning (수정 권장)
   - Suggestion (고려)
```

### Frontmatter 주요 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `name` | string | 고유 식별자 (소문자, 하이픈) |
| `description` | string | 언제 사용할지 (자동 호출 기준) |
| `tools` | list | 허용할 도구 목록 |
| `model` | string | `sonnet`, `opus`, `haiku` |
| `maxTurns` | int | 최대 턴 수 |
| `isolation` | string | `worktree` 설정 시 git worktree 격리 |
| `memory` | string | 영구 메모리: `user`, `project`, `local` |

### Worktree 시스템

`isolation: "worktree"` 설정 시, subagent가 별도의 git worktree(리포지토리 복사본)에서 작업한다:

- 메인 작업 디렉토리에 영향을 주지 않음
- 변경이 없으면 자동 정리
- 변경이 있으면 수동으로 머지/정리 가능

### 언제 사용하면 효과적인가

**사용해야 할 때:**
- 대량의 출력이 생기는 작업 (테스트 실행, 대규모 검색)
- 메인 컨텍스트를 보호하고 싶을 때
- 독립적이고 자체 완결적인 작업
- 병렬로 여러 작업을 동시에 처리하고 싶을 때

**사용하지 않아야 할 때:**
- 빈번한 상호작용이 필요한 작업
- 빠른 단건 수정
- 지연시간이 중요한 경우

---

## 3. Skills - 재사용 가능한 워크플로우

### 개념

Skills는 Claude가 특정 작업을 수행하는 방법을 정의한 재사용 가능한 마크다운 파일이다. `/skill-name`으로 호출하거나, Claude가 관련성을 판단하여 자동으로 로드한다.

**CLAUDE.md와의 핵심 차이:**
- CLAUDE.md는 매 세션마다 항상 로드 → 컨텍스트를 항상 소모
- Skills는 호출 시에만 로드 → 필요할 때만 컨텍스트 사용

### 파일 위치

| 위치 | 스코프 | 공유 가능 |
|------|--------|-----------|
| `~/.claude/skills/<name>/SKILL.md` | 모든 프로젝트 | 아니오 (로컬) |
| `.claude/skills/<name>/SKILL.md` | 단일 프로젝트 | 예 (커밋 가능) |

### Skill 파일 구조

```
my-skill/
├── SKILL.md           # 메인 지시사항 (필수)
├── template.md        # Claude가 채울 템플릿
├── examples/          # 예제 출력
└── scripts/           # 헬퍼 스크립트
```

### SKILL.md 작성법

```yaml
---
name: deploy
description: 프로덕션 배포 워크플로우
disable-model-invocation: true   # 수동 호출만 허용
user-invocable: true             # /deploy로 사용자 호출 가능
allowed-tools: Read, Bash
---

배포 프로세스:
1. `npm test` 실행하여 모든 테스트 통과 확인
2. `npm run build` 실행
3. 빌드 결과물 검증
4. 배포 대상에 push
```

### 호출 방식 제어

| 설정 | 사용자 호출 | Claude 자동 호출 | 용도 |
|------|-------------|------------------|------|
| 기본값 | O | O | 일반적인 스킬 |
| `disable-model-invocation: true` | O | X | 부작용이 있는 작업 (배포, 메시지 전송) |
| `user-invocable: false` | X | O | 배경 지식 (레거시 시스템 정보) |

### 인자 전달

```yaml
---
name: fix-issue
description: GitHub 이슈 수정
---

이슈 $ARGUMENTS를 코딩 표준에 따라 수정하세요:
1. 이슈 읽기
2. 수정 구현
3. 테스트 작성
```

사용: `/fix-issue 123` → "이슈 123을 코딩 표준에 따라 수정하세요..."

### 동적 컨텍스트 주입

```yaml
---
name: pr-summary
---

## PR 컨텍스트
- Diff: !`gh pr diff`
- 코멘트: !`gh pr view --comments`

이 PR을 요약하세요...
```

`` !`command` `` 구문은 skill 로드 시 즉시 실행되어 결과로 대체된다.

### 효과적인 상황

- 반복적으로 같은 지시를 내리는 작업 (PR 리뷰, 이슈 수정, 배포)
- 팀원 간 워크플로우를 표준화하고 싶을 때
- 복잡한 멀티스텝 작업을 한 명령어로 실행하고 싶을 때
- 컨텍스트를 절약하면서 필요할 때만 지시를 로드하고 싶을 때

---

## 4. Hooks - 라이프사이클 자동화

### 개념

Hooks는 Claude Code의 특정 이벤트 시점에 셸 명령이 **자동으로** 실행되는 시스템이다. LLM의 확률적 특성을 보완하여, 특정 행동이 **항상** 일어나도록 보장한다.

### 핵심 차이: 왜 CLAUDE.md가 아니라 Hooks인가?

| | CLAUDE.md | Hooks |
|---|---|---|
| 실행 방식 | LLM이 지시를 읽고 **따르려고 시도** | 시스템이 **자동으로 실행** |
| 보장 수준 | 확률적 (가끔 빼먹을 수 있음) | 결정론적 (100% 실행) |
| 용도 | 가이드라인, 규칙 | 강제 실행, 차단, 자동화 |

### 이벤트 흐름과 Hook 위치

```
사용자가 프롬프트 제출
  ↓
[UserPromptSubmit] hook 실행
  ↓
Claude가 처리 후 도구 결정
  ↓
[PreToolUse] hook 실행 (차단 가능!)
  ↓
차단되지 않으면 도구 실행
  ↓
[PostToolUse] hook 실행
  ↓
Claude가 결과 사용
  ↓
Claude 응답 완료
  ↓
[Stop] hook 실행
```

### 주요 이벤트 종류

| 이벤트 | 발생 시점 | matcher 예시 |
|--------|----------|--------------|
| `SessionStart` | 세션 시작/재개 | `startup`, `resume`, `compact` |
| `UserPromptSubmit` | 프롬프트 제출 시 | (없음) |
| `PreToolUse` | 도구 실행 전 (차단 가능) | `Bash`, `Edit\|Write` |
| `PostToolUse` | 도구 실행 성공 후 | `Edit\|Write` |
| `Stop` | Claude 응답 완료 시 | (없음) |
| `Notification` | 알림 발생 시 | `permission_prompt` |
| `SubagentStart` | subagent 생성 시 | `Explore`, 커스텀 이름 |
| `PreCompact` | 컨텍스트 압축 전 | `manual`, `auto` |

### 설정 방법

`settings.json`에 작성:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./.claude/hooks/validate-bash.sh"
          }
        ]
      }
    ]
  }
}
```

### 설정 파일 위치

| 위치 | 스코프 |
|------|--------|
| `~/.claude/settings.json` | 모든 프로젝트 (개인) |
| `.claude/settings.json` | 단일 프로젝트 (팀 공유) |
| `.claude/settings.local.json` | 단일 프로젝트 (로컬 전용) |
| 관리 정책 | 조직 전체 |

### Hook 타입

**Command (가장 일반적):**
```json
{ "type": "command", "command": "bash script.sh" }
```

**Prompt (판단이 필요한 경우):**
```json
{ "type": "prompt", "prompt": "이 작업이 완료되었는지 확인하세요." }
```

**Agent (도구 접근이 필요한 검증):**
```json
{ "type": "agent", "prompt": "모든 테스트가 통과하는지 확인하세요.", "timeout": 120 }
```

**HTTP (외부 서비스 연동):**
```json
{ "type": "http", "url": "http://localhost:8080/hooks/tool-use" }
```

### 종료 코드의 의미

| 코드 | 의미 | 동작 |
|------|------|------|
| **0** | 성공 | 진행. stdout이 Claude 컨텍스트에 추가 |
| **2** | 차단 | 도구 실행 중단. stderr가 Claude에게 피드백으로 전달 |
| **그 외** | 오류 | 진행. stderr는 로그에만 기록 |

### 실전 패턴

**파일 수정 후 자동 포맷팅:**
```json
{
  "PostToolUse": [{
    "matcher": "Edit|Write",
    "hooks": [{
      "type": "command",
      "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
    }]
  }]
}
```

**보호 파일 수정 차단:**
```bash
#!/bin/bash
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path')
if [[ "$FILE" == *.env* ]] || [[ "$FILE" == .git* ]]; then
  echo "Blocked: 보호된 파일입니다" >&2
  exit 2
fi
exit 0
```

**컨텍스트 압축 후 중요 지시 재주입:**
```json
{
  "SessionStart": [{
    "matcher": "compact",
    "hooks": [{
      "type": "command",
      "command": "echo 'npm을 사용하지 말고 Bun을 사용하세요. 커밋 전 테스트를 실행하세요.'"
    }]
  }]
}
```

### 효과적인 상황

- 코드 수정 후 반드시 린터/포맷터를 실행해야 할 때
- 특정 파일(.env, 인증 정보)의 수정을 원천 차단하고 싶을 때
- 위험한 셸 명령어 실행을 사전에 검증하고 싶을 때
- 외부 시스템(Slack, 모니터링)과 자동 연동하고 싶을 때

---

## 기능 비교표

| | CLAUDE.md | Skills | Subagents | Hooks |
|---|---|---|---|---|
| **정체** | 영구 지시 파일 | 재사용 워크플로우 | 격리된 에이전트 | 자동 실행 명령 |
| **로딩 시점** | 매 세션 시작 | 호출 시 or 자동 | 호출 시 | 이벤트 발생 시 |
| **컨텍스트 소모** | 항상 | 호출 시에만 | 별도 윈도우 | 없음 |
| **실행 보장** | 확률적 | 확률적 | 확률적 | 결정론적 |
| **설정 형식** | Markdown | YAML + Markdown | YAML + Markdown | JSON (settings) |
| **주요 용도** | 프로젝트 규칙 | 반복 작업 자동화 | 복잡한 작업 위임 | 강제 규칙 적용 |
| **공유 가능** | VCS 커밋 | VCS 커밋 | VCS 커밋 | VCS 커밋 |

---

## 실전 프로젝트 구성 예시

### 전체 디렉토리 구조

```
my-project/
├── CLAUDE.md                        # 프로젝트 지시사항
├── .claude/
│   ├── CLAUDE.md                    # 프로젝트별 오버라이드
│   ├── settings.json                # 프로젝트 설정 + hooks
│   ├── settings.local.json          # 로컬 전용 설정 (gitignore)
│   ├── rules/
│   │   ├── code-style.md            # 코딩 표준 (항상 로드)
│   │   ├── testing.md               # 테스트 규칙
│   │   └── frontend/
│   │       └── react.md             # React 전용 (경로 조건부)
│   ├── agents/
│   │   ├── code-reviewer/SKILL.md   # 코드 리뷰 에이전트
│   │   └── db-validator/SKILL.md    # DB 검증 에이전트
│   ├── skills/
│   │   ├── deploy/SKILL.md          # /deploy 명령
│   │   └── pr-review/SKILL.md       # /pr-review 명령
│   └── hooks/
│       ├── protect-files.sh         # 파일 보호 스크립트
│       └── validate-bash.sh         # Bash 검증 스크립트
```

### 이 구조에서 각 기능의 역할

1. **CLAUDE.md**: "이 프로젝트는 TypeScript를 쓰고, 2-space 인덴트이고, `npm test`로 테스트한다"
2. **rules/react.md**: React 컴포넌트 파일 작업 시에만 "props 타입을 명시하고, 커스텀 훅은 use 접두사를 붙여라"
3. **agents/code-reviewer**: 코드 변경 후 독립된 컨텍스트에서 체계적으로 리뷰
4. **skills/deploy**: `/deploy`로 표준화된 배포 프로세스 실행
5. **hooks**: 파일 수정 시 자동 포맷팅, .env 파일 수정 차단

### 판단 기준: 어디에 넣을까?

```
"이 규칙을 항상 알아야 하나?"
  → Yes → CLAUDE.md 또는 rules/

"반복적인 워크플로우인가?"
  → Yes → Skills

"독립적이고 무거운 작업인가?"
  → Yes → Subagent

"100% 실행이 보장되어야 하나?"
  → Yes → Hooks
```
