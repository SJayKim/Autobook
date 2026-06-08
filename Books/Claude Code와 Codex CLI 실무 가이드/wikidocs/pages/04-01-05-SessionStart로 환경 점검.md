# 4.1.5 SessionStart로 환경 점검

세션이 시작된 직후 모델은 사용자가 무엇을 하다 멈췄는지, 현재 브랜치가 어디인지, 어떤 환경 변수가 비어 있는지 알지 못합니다. 사람이 매번 "지금 브랜치는 feature/x, 어제 작업한 파일은 ..."을 적어 주는 일은 비효율적이고 잘 까먹습니다. Claude Code의 SessionStart hook은 이 첫 인사 영역을 자동화해 둘 수 있는 자리입니다.

SessionStart는 새 세션이 처음 열릴 때 한 번 실행됩니다. 4.1.4에서 다룬 UserPromptSubmit이 메시지마다 매번 실행되는 데 비해, SessionStart는 한 세션 전체에 단 한 번 실행됩니다. 그래서 매번 보여 줄 필요는 없지만 한 번은 알려 두어야 하는 정보(현재 브랜치, 환경 변수 누락, MCP 서버 헬스 상태 등)를 출력하기에 적합합니다. UserPromptSubmit과 마찬가지로 SessionStart의 표준 출력은 모델 컨텍스트에 합쳐집니다.

이 hook에는 한 가지 유의할 점이 있습니다. SessionStart의 입력 JSON에는 `source` 필드가 들어오는데, 값이 두 갈래입니다. 한쪽은 `startup`으로, `claude` 명령으로 새로 세션을 띄울 때입니다. 다른 한쪽은 `resume`으로, `claude --resume`이나 사용자가 이전 세션을 이어서 열 때입니다. 같은 hook이라도 두 경우에 보여 줄 정보가 다릅니다. startup에서는 환경 전반을 짚어 줄 필요가 있고, resume에서는 이미 보여 줬던 정보 대신 그 사이 변경된 부분만 짚는 편이 좋습니다. 비슷한 이름의 SessionEnd hook은 세션이 닫힐 때 실행되는 별도 이벤트이며, 종료 시점의 정리 작업에 쓰입니다.

다음은 settings.json에 등록하는 항목입니다.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/session-start.sh"
          }
        ]
      }
    ]
  }
}
```

스크립트의 본체는 git 상태, 환경 변수, 외부 의존성 세 갈래를 짧게 출력합니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
source_kind="$(printf '%s' "$payload" | jq -r '.source // "startup"')"

branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-git')"
dirty="$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
last_commit="$(git log -1 --pretty='%h %s' 2>/dev/null || echo 'no-commit')"

echo "<session-info>"
echo "branch: ${branch} (dirty files: ${dirty})"
echo "last commit: ${last_commit}"

if [ "$source_kind" = "startup" ]; then
  for v in OPENAI_API_KEY ANTHROPIC_API_KEY GH_TOKEN; do
    if [ -z "${!v:-}" ]; then
      echo "env missing: ${v}"
    fi
  done

  if command -v gh >/dev/null 2>&1; then
    if ! gh auth status >/dev/null 2>&1; then
      echo "gh: not authenticated"
    fi
  fi
fi
echo "</session-info>"

exit 0
```

스크립트는 먼저 입력 JSON에서 source를 꺼냅니다. 그다음 git 브랜치, 더티 파일 수, 마지막 커밋 한 줄을 모읍니다. 이 세 줄은 startup과 resume 양쪽 모두에서 보여 줍니다. 같은 세션이라도 외부 셸에서 git 상태가 바뀔 수 있으므로, 매 세션 시작마다 한 번씩 표시해 두는 편이 안전합니다.

이어지는 분기는 startup에서만 실행됩니다. 필요한 환경 변수가 비어 있는지 점검하고, 비어 있는 변수 이름만 짧게 알립니다. 비밀 값을 출력하지 않고 이름만 보여 주는 것이 핵심입니다. gh CLI가 설치되어 있다면 인증 상태도 한 번 확인합니다. resume에서는 이 검사를 건너뛰어, 같은 안내가 반복되지 않도록 합니다.

MCP 서버 헬스 체크는 SessionStart에서 자주 하는 작업이지만, 시간을 잡아먹기 쉽습니다. 빠르게 끝내는 방법은 두 가지입니다. 첫째, 응답 대기 시간을 짧게 둡니다. stdio 기반 MCP 서버라면 `timeout 2s`로 감싸 2초 안에 답하지 않으면 실패로 간주합니다. 둘째, 서버별 헬스 체크를 직렬이 아니라 병렬로 돌립니다. 다음과 같이 짧게 작성할 수 있습니다.

```bash
check_mcp() {
  local name="$1"; local cmd="$2"
  if timeout 2s bash -c "$cmd" >/dev/null 2>&1; then
    echo "mcp ok: ${name}"
  else
    echo "mcp slow/down: ${name}"
  fi
}

if [ "$source_kind" = "startup" ]; then
  check_mcp "fs"     "ls .mcp-data" &
  check_mcp "github" "gh api user"  &
  wait
fi
```

`timeout 2s`로 응답 한계를 둔 뒤, 백그라운드로 띄우고 `wait`로 모두 모읍니다. 한 서버가 느려도 전체 점검이 2초 이상 늘어나지 않습니다. 결과는 `ok` 또는 `slow/down`처럼 한 단어로만 보고합니다. 자세한 진단은 모델이 필요할 때 사용자가 직접 명령을 부르도록 두는 편이 컨텍스트 절약에 좋습니다.

출력이 길어지지 않도록 가둘 기준도 정해 둡니다. 한 hook에서 출력할 줄 수의 상한을 정해 두고(예: 12줄), 그 이상이면 첫 줄에 요약, 두 번째 줄에 "자세한 점검은 /diag로"처럼 안내만 둡니다. 모델은 SessionStart의 출력을 매 메시지에 항상 보고 있는 셈이므로, 한 줄이라도 짧게 유지하는 것이 누적 토큰에 직접 영향을 줍니다.

전체 흐름을 정리한 다이어그램은 다음과 같습니다.

```
claude 실행 (또는 --resume)
        |
        v
SessionStart hook 트리거
  - source 판정 (startup / resume)
  - git branch, dirty, last commit
  - [startup만] env var, gh auth
  - [startup만] MCP 헬스(timeout, 병렬)
        |
        v
stdout → 모델 세션 컨텍스트 머리에 합쳐짐
```

이 흐름을 따라 만들어 두면, 세션을 처음 열 때 사용자는 무엇이 정상이고 무엇이 비어 있는지 한눈에 보고, 모델은 같은 정보를 컨텍스트의 머리에서 한 번 받아 두고 작업을 시작합니다. 사람과 모델이 같은 상태를 공유한 채로 첫 메시지를 주고받게 됩니다.

정리하면, SessionStart는 세션이 열릴 때 한 번 실행되어 git 상태, 환경 변수 누락, MCP 서버 헬스를 자동으로 짚어 줍니다. startup과 resume의 두 source를 구분해 중복 정보를 줄이고, timeout과 병렬 실행으로 점검 시간을 짧게 유지하며, 출력 줄 수에 상한을 두면 컨텍스트 부담 없이 안정적인 시작 의식을 만들 수 있습니다.

다음 단원인 5.1.1에서는 외부 도구를 모델에 표준 인터페이스로 연결하는 Model Context Protocol의 개념과 두 도구의 연결 방식 차이를 다룹니다.

이 단원을 마치면 새 세션과 재개 세션을 구분해 git·환경 변수·MCP 헬스를 빠르게 점검하고, 그 결과를 모델에게 컨텍스트 머리에 자동 첨부하는 SessionStart hook을 작성할 수 있습니다.
