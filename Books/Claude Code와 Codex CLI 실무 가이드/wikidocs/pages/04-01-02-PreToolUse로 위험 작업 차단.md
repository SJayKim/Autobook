# 4.1.2 PreToolUse로 위험 작업 차단

3.2.3에서 위험 명령 차단의 큰 그림을 그리고, 4.1.1에서 hook 전체 지도를 보았습니다. 이제 가장 자주 쓰이는 hook 한 가지를 골라 실제 동작하는 스크립트까지 만들어 봅니다. PreToolUse는 모델이 도구를 부르려는 순간에 끼어드는 hook으로, 인자를 한 번 검사해 위험 패턴이면 차단하고 안전한 명령만 통과시키는 자리입니다.

`permissions.deny`의 매처 표기만으로 잡지 못하는 패턴이 있습니다. 셸 명령은 `&&`로 이어지거나, 따옴표·환경 변수로 모양이 바뀌거나, 공백 개수만 달라져도 매처를 빗겨 갑니다. PreToolUse hook은 도구 호출 직전에 인자 전체를 문자열로 받아 정규식으로 검사할 수 있어, 매처보다 한 단계 정교한 검증이 가능합니다.

PreToolUse hook이 받는 입력 JSON의 구조부터 짚어 둡니다. 표준 입력으로 다음 필드가 들어옵니다.

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/foo",
    "description": "임시 폴더 삭제"
  }
}
```

`tool_name`은 호출하려는 도구 이름입니다. `Bash`, `Write`, `Edit`, `Read`처럼 도구마다 식별자가 정해져 있습니다. `tool_input`은 도구별로 모양이 다른 인자 객체입니다. `Bash`는 `command`, `Write`는 `file_path`와 `content`, `Edit`는 `file_path`·`old_string`·`new_string` 식으로 필드가 들어옵니다. hook 스크립트는 `tool_name`을 보고 어떤 검사를 할지 정하고, 그 도구의 인자 모양에 맞춰 `tool_input`을 파싱합니다.

다음은 Python으로 작성한 차단 스크립트입니다. 위험 패턴 목록을 정규식으로 두고, 매치되면 종료 코드 2로 빠져나오며 stderr에 사유를 적습니다.

```python
#!/usr/bin/env python3
# .claude/hooks/block_dangerous.py
import json
import re
import sys

DANGEROUS_BASH = [
    (r"\brm\s+(-[rRfF]+\s+)+/", "루트나 절대 경로에 대한 rm -rf 는 금지합니다"),
    (r"\bgit\s+push\s+.*(--force|-f)\b", "force push 는 금지합니다. 새 브랜치와 PR 을 사용하십시오"),
    (r"\b(curl|wget)\s+[^|;]*\|\s*sh\b", "검증되지 않은 스크립트의 파이프 실행은 금지합니다"),
    (r":\(\)\s*\{.*\};\s*:", "포크 폭탄으로 추정되는 패턴입니다"),
]

DANGEROUS_PATH = [
    r"^/etc/",
    r"^/usr/",
    r"\.env(\.|$)",
    r"^~?/\.ssh/",
    r"^~?/\.aws/",
]

def block(reason: str) -> None:
    print(reason, file=sys.stderr)
    sys.exit(2)

def main() -> None:
    payload = json.load(sys.stdin)
    tool = payload.get("tool_name", "")
    args = payload.get("tool_input", {}) or {}

    if tool == "Bash":
        cmd = args.get("command", "")
        for pattern, reason in DANGEROUS_BASH:
            if re.search(pattern, cmd):
                block(f"차단: {reason}\n명령: {cmd}")

    if tool in ("Write", "Edit"):
        path = args.get("file_path", "")
        for pattern in DANGEROUS_PATH:
            if re.search(pattern, path):
                block(f"차단: 보호 경로에 대한 쓰기 시도 ({path})")

    sys.exit(0)

if __name__ == "__main__":
    main()
```

스크립트 흐름은 단순합니다. 표준 입력에서 JSON을 읽고, `tool_name`에 따라 다른 검사를 합니다. `Bash` 도구에서는 명령 문자열을 위험 패턴 목록과 정규식으로 대조합니다. `Write`와 `Edit` 도구에서는 `file_path`를 보호 경로 패턴과 대조합니다. 어느 한 쪽이라도 매치되면 stderr에 사유를 쓰고 종료 코드 2로 끝납니다. 모든 검사를 통과하면 종료 코드 0으로 끝나, 도구 호출이 정상적으로 진행됩니다.

같은 동작을 Bash로도 쓸 수 있습니다. 의존성이 더 적어 컨테이너 안에서도 가볍게 돌릴 수 있다는 장점이 있습니다.

```bash
#!/usr/bin/env bash
# .claude/hooks/block_dangerous.sh
set -euo pipefail

payload=$(cat)
tool=$(echo "$payload" | jq -r '.tool_name // ""')
command=$(echo "$payload" | jq -r '.tool_input.command // ""')
path=$(echo "$payload" | jq -r '.tool_input.file_path // ""')

block() {
  echo "차단: $1" 1>&2
  exit 2
}

if [ "$tool" = "Bash" ]; then
  case "$command" in
    *"rm -rf /"*|*"rm -fr /"*) block "절대 경로에 대한 rm 은 금지합니다";;
    *"git push --force"*|*"git push -f"*) block "force push 는 금지합니다";;
    *"| sh"*|*"| bash"*) block "파이프 셸 실행은 금지합니다";;
  esac
fi

if [ "$tool" = "Write" ] || [ "$tool" = "Edit" ]; then
  case "$path" in
    /etc/*|/usr/*|*".env"|*/.ssh/*) block "보호 경로 쓰기 금지: $path";;
  esac
fi

exit 0
```

PowerShell이 기본인 환경에서도 같은 골격을 옮길 수 있습니다. 표준 입력에서 JSON을 받아 `ConvertFrom-Json`으로 객체로 만들고, `tool_name`과 `tool_input`을 같은 방식으로 검사합니다. 어떤 언어를 쓰든 입력 JSON 모양과 종료 코드 규칙은 동일합니다.

`settings.json`에는 다음과 같이 등록합니다.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit",
        "hooks": [
          { "type": "command", "command": "python .claude/hooks/block_dangerous.py" }
        ]
      }
    ]
  }
}
```

`matcher` 필드는 어떤 도구에서 hook을 부를지 정하는 정규식입니다. `Bash|Write|Edit` 세 도구에만 hook을 매치해 두면, `Read` 같은 가벼운 도구 호출까지 검사로 막혀 느려지는 문제를 피할 수 있습니다. 검사 대상이 늘어날수록 매처도 함께 늘립니다.

차단할 때 사용자에게 어떤 사유를 보여 줄지가 모델의 다음 행동을 좌우합니다. 단지 "blocked"라고만 끝내면 모델은 같은 시도를 다른 표현으로 반복하기 쉽습니다. 사유 메시지는 짧고 분명하게, 그리고 대안을 함께 적습니다. 예를 들어 force push 차단 메시지에 "새 브랜치와 PR을 사용하십시오"를 함께 적어 두면, 모델은 다음 시도에서 새 브랜치 워크플로로 자연스럽게 옮겨 갑니다.

위험 패턴은 광범위하게 잡을수록 오탐도 늘어납니다. 정상 작업까지 막아 버리면 hook 자체가 무력화되기 쉽습니다. 오탐을 줄이는 한 가지 방법은 **화이트리스트 보조**입니다. 매치된 명령이 차단 목록에 들어가더라도, 명백히 안전하다고 표시한 패턴이면 통과시킵니다. 예를 들어 `rm -rf` 일반은 막되, `rm -rf node_modules`나 `rm -rf .next` 같은 빌드 산출물 삭제는 통과시키는 식입니다.

```python
SAFE_BASH = [
    r"\brm\s+-rf\s+node_modules\b",
    r"\brm\s+-rf\s+\.next\b",
    r"\brm\s+-rf\s+dist\b",
]

# block 직전에 화이트리스트 확인
for safe in SAFE_BASH:
    if re.search(safe, cmd):
        sys.exit(0)
```

이 짧은 분기를 차단 결정 직전에 두면, 익숙한 빌드 산출물 정리는 막힘 없이 진행됩니다. 화이트리스트는 좁게 두는 것이 핵심이고, 새 항목을 추가할 때마다 동료가 한 번 검토할 수 있게 코드 리뷰 대상에 두는 것이 안전합니다.

정리하면, PreToolUse hook은 표준 입력으로 받는 `tool_name`과 `tool_input`을 파싱해 위험 패턴을 정규식으로 검사하고, 종료 코드 2와 stderr 메시지로 도구 호출을 차단하는 자리입니다. Python·Bash·PowerShell 어디서든 같은 골격으로 작성하고, 매처와 화이트리스트로 오탐을 통제합니다.

다음 단원인 4.1.3에서는 도구 호출이 끝난 직후에 동작하는 PostToolUse hook으로, 파일 편집 직후 포맷·린트·테스트를 자동으로 돌리는 방법을 다룹니다.
