# 1.1.1 Claude Code와 Codex CLI 한눈에 비교

터미널에서 코딩을 도와주는 에이전트 도구로 Claude Code와 Codex CLI를 함께 검토하는 팀이 늘고 있습니다. 두 도구는 비슷한 일을 한다고 알려져 있지만, 동작 모델과 권한 모델이 다릅니다. 어떤 작업에 어느 쪽을 골라야 할지 판단하려면, 차이점부터 또렷이 정리해야 합니다.

먼저 회사와 라이선스, 설치 형태를 봅니다. Claude Code는 Anthropic이 만들고, npm 패키지 `@anthropic-ai/claude-code`로 전역 설치합니다. 사용에는 Anthropic 계정과 API 키 또는 구독 키가 필요합니다. Codex CLI는 OpenAI가 만들었고, npm 패키지 `@openai/codex` 외에 Homebrew와 소스 빌드도 지원합니다. 핵심 동작 코드는 공개 저장소에서 확인할 수 있고, OpenAI API 키 또는 ChatGPT 로그인으로 인증합니다.

```bash
# Claude Code 설치
npm install -g @anthropic-ai/claude-code

# Codex CLI 설치
npm install -g @openai/codex
```

두 명령 모두 전역 바이너리를 한 개 만들어 줍니다. Claude Code는 `claude`로 진입하고, Codex CLI는 `codex`로 진입합니다.

다음은 **기본 동작 모델**의 차이입니다. Claude Code는 **대화형 루프**를 기본으로 잡습니다. 사용자가 메시지를 보내면 모델이 도구를 호출하고, 결과를 같은 대화 컨텍스트에 누적한 채 다음 응답을 만듭니다. 한 세션이 길게 이어지며, 여러 파일을 읽고 고치는 작업이 자연스럽게 묶입니다. Codex CLI는 대화형도 지원하지만, **작업 단위 실행**을 일급 시민으로 둡니다. `codex exec "..."` 한 줄로 비대화형 작업을 띄우고, 끝나면 결과를 보고하고 종료합니다.

**권한 모델**은 가장 큰 차이가 드러나는 영역입니다. Claude Code는 `permissions` 객체로 도구·인자 단위의 허용·거부·문의 규칙을 둡니다. `Bash(git status)`처럼 명령까지 매처에 적을 수 있고, 매치되지 않으면 사용자에게 묻거나 차단합니다. Codex CLI는 두 축을 분리합니다. 한 축은 **sandbox**로, 파일 시스템과 네트워크 자체에 한계를 둡니다. 다른 축은 **approval policy**로, 모델이 권한 밖 동작을 시도할 때 어떻게 응답할지 정합니다. 두 축의 조합으로 안전 수준이 결정됩니다.

**확장 지점**도 이름과 위치가 다릅니다. 정리하면 다음과 같습니다.

| 항목 | Claude Code | Codex CLI |
| --- | --- | --- |
| 회사·라이선스 | Anthropic, 비공개 소스 | OpenAI, 오픈 소스 |
| 설치 | npm 전역 | npm·Homebrew·소스 |
| 인증 | Anthropic 계정·API 키 | OpenAI API 키·ChatGPT 로그인 |
| 진입 명령 | `claude` | `codex`, `codex exec` |
| 동작 모델 | 대화형 루프 | 대화형 + 작업 단위 |
| 권한 모델 | permissions(allow·deny·ask) | sandbox + approval policy |
| 확장: 컨텍스트 | CLAUDE.md | AGENTS.md |
| 확장: 정책 | hook(PreToolUse 등) | approval policy 분기 |
| 확장: 외부 도구 | MCP(settings.json) | MCP(config.toml) |
| 확장: 위임 | subagent(.claude/agents/) | profile, codex exec 분리 |
| 확장: 재사용 | skill, 슬래시 커맨드 | profile, shell wrapper |

표만 보면 비슷해 보이지만, 안전장치를 어디에 둘지 결정할 때 갈림길이 나타납니다. Claude Code는 한 세션 안에서 hook이 도구 호출 전후를 가로채 정책을 강제합니다. Codex CLI는 세션 자체를 sandbox로 가두고, 한계를 넘는 시도에 대해 approval policy로 묻거나 거부합니다.

마지막으로 어떤 작업에 어느 쪽이 적합한지 한 줄 기준을 둡니다. 여러 파일을 오래 만지는 탐색·편집 작업은 Claude Code가 자연스럽고, 짧은 작업을 비대화형으로 여러 개 돌리거나 강한 격리가 필요한 작업은 Codex CLI가 유리합니다. 두 도구를 한 레포에서 함께 쓰는 구성도 가능하며, 후반부에서 그 방법을 다룹니다.

정리하면, Claude Code는 대화형 루프와 hook 중심 정책을 강점으로 두고, Codex CLI는 작업 단위 실행과 sandbox·approval 두 축을 강점으로 둡니다. 두 도구의 차이는 위 표 한 장으로 요약할 수 있습니다.

다음 단원인 1.1.2에서는 두 도구의 하네스 구조를 더 깊이 들여다보며, 사용자 입력이 도구 호출에 이르기까지 거치는 통제·피드백 계층을 그림으로 비교합니다.
