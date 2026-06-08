# 4.1.3 PostToolUse로 포맷·린트 자동화

코드를 편집할 때마다 사람이 직접 포맷터와 린터를 돌리는 일은 잊기 쉽습니다. 에이전트가 한 세션에서 수십 개의 파일을 손대는 상황이라면 이 비용은 더 커집니다. 4.1.2에서 PreToolUse로 위험한 도구 호출을 사전에 막는 법을 익혔다면, 이 단원에서는 반대편의 통제 지점인 PostToolUse를 활용합니다. PostToolUse는 도구 호출이 끝난 직후에 동작하므로, 결과물에 손을 대거나 후처리 검증을 자동으로 끼워 넣기에 적합합니다.

먼저 PostToolUse가 언제 실행되는지부터 짚습니다. Claude Code 하네스는 모델이 도구를 호출하면 그 호출을 실제로 수행한 뒤, 결과를 모델에게 돌려보내기 직전에 등록된 PostToolUse hook을 차례로 부릅니다. 대상 도구는 Edit, Write, Bash 등 거의 모든 도구가 될 수 있으며, matcher 필드로 특정 도구만 잡아낼 수 있습니다. PreToolUse가 도구 호출의 인자를 검사한다면, PostToolUse는 도구가 실제로 어떤 결과를 내놓았는지까지 함께 볼 수 있습니다.

hook 스크립트에는 표준 입력으로 JSON이 한 덩어리 들어옵니다. 핵심 필드는 두 가지입니다. **tool_input**은 모델이 도구에 보낸 인자입니다. Edit이라면 파일 경로와 변경 내용이, Bash라면 실행한 명령 문자열이 들어 있습니다. **tool_response**는 도구가 반환한 결과로, Edit·Write의 경우 변경된 파일 경로, Bash의 경우 표준 출력과 표준 에러, 종료 코드가 담깁니다. PostToolUse 스크립트는 이 두 필드를 함께 읽어, '무엇을 했는지'와 '결과는 어땠는지'를 동시에 판단할 수 있습니다.

자동 포맷의 가장 흔한 구성은 Edit과 Write가 끝났을 때 변경 파일에 prettier, ruff, gofmt 같은 포맷터를 부르는 것입니다. 다음은 settings.json에 등록하는 hook 설정의 예입니다.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/format-on-edit.sh"
          }
        ]
      }
    ]
  }
}
```

matcher에 `Edit|Write` 두 도구를 묶고, type을 command로 두어 외부 스크립트를 부릅니다. 명령은 프로젝트 루트 기준의 상대 경로로 적었습니다. 같은 자리에서 prettier를 인라인으로 부르는 것도 가능하지만, 분기 로직이 길어지면 스크립트로 빼는 편이 읽기 쉽습니다.

이어지는 `format-on-edit.sh`는 표준 입력으로 들어오는 JSON에서 변경된 파일 경로를 꺼낸 뒤, 확장자별로 다른 포맷터를 부릅니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
file_path="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty')"

if [ -z "$file_path" ] || [ ! -f "$file_path" ]; then
  exit 0
fi

case "$file_path" in
  *.ts|*.tsx|*.js|*.jsx|*.json|*.md)
    npx --no-install prettier --write "$file_path" >&2 ;;
  *.py)
    ruff format "$file_path" >&2
    ruff check --fix "$file_path" >&2 ;;
  *.go)
    gofmt -w "$file_path" >&2 ;;
  *) exit 0 ;;
esac

exit 0
```

스크립트는 먼저 표준 입력을 통째로 받아 jq로 `tool_input.file_path`를 꺼냅니다. 경로가 비어 있거나 실제 파일이 없으면 그대로 종료합니다. 확장자별로 prettier, ruff, gofmt를 각각 부르고, 출력은 표준 에러로 흘려보냅니다. 표준 출력이 아니라 표준 에러로 보내는 까닭은 PostToolUse의 표준 출력이 사용자에게는 보이지만 모델 컨텍스트에는 합쳐지지 않게 하기 위함입니다. 변경 파일 하나에만 포맷터를 돌리므로, 레포 전체를 훑는 비용이 들지 않습니다.

린트 실패를 모델에게 다시 알리는 일도 같은 hook으로 처리합니다. PostToolUse 스크립트가 종료 코드 2로 끝나면, Claude Code는 표준 에러에 적힌 내용을 모델에게 보냅니다. 이때 모델은 이를 도구 결과에 덧붙은 후행 메시지로 받아, 다음 응답에서 잘못된 부분을 스스로 고치려고 합니다. 주의할 점은 종료 코드 2가 직전 도구 호출을 되돌리지는 않는다는 점입니다. 파일은 이미 변경된 상태이고, 모델이 추가 편집을 통해 보정해야 합니다.

다음은 린트 실패를 모델에게 알리는 보강된 부분 예입니다.

```bash
if ! ruff check "$file_path" >/tmp/ruff.out 2>&1; then
  cat /tmp/ruff.out >&2
  echo "ruff check failed on $file_path. Please fix above errors." >&2
  exit 2
fi
```

ruff check가 실패하면 그 출력을 표준 에러로 흘리고, 한 줄짜리 한국어 또는 영어 안내를 추가한 뒤 종료 코드 2로 끝냅니다. 모델은 다음 턴에서 같은 파일을 다시 열어 수정을 시도합니다. 안내 문구는 짧고 구체적으로 적어야 모델이 헤매지 않습니다.

테스트 자동 실행은 욕심을 부리면 비용이 빠르게 늘어납니다. 한 글자만 고쳐도 전체 테스트가 돌면 토큰과 시간이 폭증합니다. 두 가지 조건으로 절약합니다. 첫째, 변경된 파일과 같은 디렉터리의 테스트만 부릅니다. pytest라면 `pytest tests/ -k 모듈명`처럼 범위를 좁히고, vitest라면 `vitest related --run`을 씁니다. 둘째, 도구 호출이 연속으로 일어나는 동안에는 테스트를 건너뛰고, 일정 시간 idle한 마지막 변경에서만 실행합니다. 이를 위해 hook 안에서 가장 최근 실행 타임스탬프를 임시 파일에 적어 두고, 일정 간격이 지난 경우에만 테스트를 부르는 식의 분기를 추가합니다.

스크립트 실행 시간 자체를 짧게 유지하는 캐시도 중요합니다. prettier와 ruff는 캐시 디렉터리를 인자로 받아, 같은 파일에 대한 반복 검사 비용을 줄여 줍니다. 다음과 같이 한 줄로 적용할 수 있습니다.

```bash
ruff check --cache-dir .ruff_cache "$file_path"
npx prettier --cache --cache-location .prettiercache --write "$file_path"
```

캐시 디렉터리는 프로젝트 루트의 .gitignore에 추가해 두면 깔끔합니다. 캐시가 살아 있는 동안에는 단일 파일 포맷이 수십 ms 안에 끝나, 모델의 다음 응답까지의 지연이 거의 늘지 않습니다.

전체 흐름을 한 번 더 정리하면 다음과 같습니다.

```
모델이 Edit 호출
        |
        v
도구 실행 (파일 변경)
        |
        v
PostToolUse(Edit|Write) hook 트리거
        |
        v
.claude/hooks/format-on-edit.sh
  - tool_input.file_path 추출
  - 확장자별 포맷터 실행
  - 린트 실패 시 stderr + exit 2
        |
        v
모델에게 결과(+stderr) 전달
```

정리하면, PostToolUse는 도구 호출 직후에 동작해 변경 파일을 자동 포맷하고, 실패 시 stderr와 종료 코드 2로 모델에게 다시 알릴 수 있습니다. 변경 파일 단위 처리, 캐시, 조건부 테스트 실행을 함께 적용하면 컨텍스트와 시간을 아끼면서도 코드 품질을 일정하게 유지할 수 있습니다.

다음 단원인 4.1.4에서는 UserPromptSubmit hook으로 모든 사용자 메시지에 정책 문구를 자동으로 끼워 넣는 방법을 다룹니다.

이 단원을 마치면 Edit과 Write 직후에 prettier·ruff·gofmt를 자동으로 돌리고, 린트 실패를 모델에게 다시 흘려 보내는 PostToolUse hook을 직접 작성할 수 있습니다.
