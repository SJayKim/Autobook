# 4.1.4 UserPromptSubmit으로 정책 주입

팀에서 정책을 정해도, 사용자가 모든 메시지마다 그것을 떠올려 직접 적어 주기를 기대하기는 어렵습니다. 메인 브랜치에 직접 push하지 말 것, 비밀번호로 보이는 문자열은 파일에 적지 말 것, 오늘 날짜는 며칠이라는 점 같은 정보는 사용자 메시지보다는 하네스가 자동으로 첨부해 주는 편이 안전합니다. Claude Code는 이를 위해 UserPromptSubmit이라는 hook을 제공합니다.

UserPromptSubmit은 사용자가 메시지를 입력해 전송한 직후, 모델에게 보내기 직전에 실행됩니다. 시점만 보면 단순하지만, 이 hook이 특별한 까닭은 **표준 출력의 처리 방식**에 있습니다. PostToolUse(4.1.3)의 표준 출력은 사용자에게만 보이고 모델 컨텍스트에는 합쳐지지 않지만, UserPromptSubmit의 표준 출력은 그 사용자 메시지 **앞에 그대로 덧붙어** 모델에게 전달됩니다. 이 동작이 정책 주입의 기반입니다.

이 hook의 입력 JSON에서 가장 중요한 필드는 `prompt`입니다. 사용자가 방금 보낸 원문이 그대로 담겨 있어, 키워드 검출이나 분기 처리에 쓸 수 있습니다. 그 밖에 세션 정보, 작업 디렉터리, 모델 이름이 함께 들어옵니다. 스크립트는 이 정보를 읽어, 무엇을 어떻게 주입할지 결정합니다.

가장 흔한 사용 예는 세션 컨텍스트 표기입니다. 오늘 날짜, 현재 git 브랜치, 운영 환경 이름을 매 메시지 앞에 짧게 붙여 두면, 모델이 시점과 위치를 헷갈리지 않습니다. 다음은 settings.json에 등록하는 hook 항목입니다.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/inject-policy.sh"
          }
        ]
      }
    ]
  }
}
```

UserPromptSubmit은 도구가 아니므로 matcher를 둘 필요가 없습니다. hooks 배열 안에 command 항목 하나를 두면, 모든 사용자 메시지에 대해 이 스크립트가 실행됩니다.

다음은 `inject-policy.sh`의 본체입니다. 표준 출력이 사용자 메시지 앞에 그대로 합쳐진다는 점을 머리에 두고 읽으면 흐름이 분명해집니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
prompt="$(printf '%s' "$payload" | jq -r '.prompt // empty')"

today="$(date +%Y-%m-%d)"
branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'no-git')"
env_name="${PROJECT_ENV:-local}"

cat <<EOF
<system-reminder>
Today is ${today}. Current git branch: ${branch}. Environment: ${env_name}.
- main 브랜치에 직접 push 금지. feature 브랜치 + PR로 진행.
- .env, secrets/ 경로의 파일을 출력하거나 수정하지 말 것.
</system-reminder>
EOF

if printf '%s' "$prompt" | grep -Eiq '(password|api[_-]?key|secret)\s*[:=]'; then
  echo "<system-reminder>" >&2
  echo "사용자 메시지에 자격 증명으로 보이는 문자열이 감지되었습니다." >&2
  echo "이 메시지의 비밀 값을 그대로 사용하지 말고 환경 변수로 대체하세요." >&2
  echo "</system-reminder>" >&2
fi

exit 0
```

스크립트는 표준 입력의 JSON에서 prompt를 꺼낸 뒤, 날짜·브랜치·환경 이름을 모아 한 덩어리의 시스템 리마인더를 표준 출력으로 내보냅니다. 이 출력은 그대로 사용자 메시지 앞에 합쳐져 모델에게 도달합니다. 모델 입장에서 보면 사용자가 매번 직접 적어 준 듯한 형태가 됩니다.

여기서 한 가지 관행을 둡니다. 주입 내용은 `<system-reminder>` 같은 짧은 마커로 감싸 두는 편이 좋습니다. 모델이 자기 컨텍스트의 어디까지가 사용자 발화이고 어디까지가 하네스가 끼워 넣은 정책인지 구분할 수 있어야, 정책을 지키는 정확도가 높아집니다. 마커 형식은 팀이 정해 두고 모든 hook이 동일하게 따르도록 합니다.

스크립트의 후반부는 민감 키워드 검출입니다. 사용자 메시지에 password, api_key, secret 같은 문자열이 등호나 콜론과 함께 나타나면, 표준 에러로 경고를 출력합니다. UserPromptSubmit의 표준 에러는 사용자에게 보이지만 모델에게는 합쳐지지 않으므로, 작성자 본인에게 즉시 주의를 환기시키는 용도로 적합합니다. 더 강한 차단이 필요하면 종료 코드 2로 끝내, 메시지 전송 자체를 막을 수도 있습니다.

```bash
if printf '%s' "$prompt" | grep -Eiq 'rm\s+-rf\s+/(\s|$)'; then
  echo "위험한 경로의 rm -rf 패턴이 감지되어 전송을 중단합니다." >&2
  exit 2
fi
```

이 분기는 사용자가 실수로 위험한 명령을 그대로 메시지에 옮긴 경우, 전송 자체를 막아 hook 차원의 마지막 안전망 역할을 합니다.

주입 길이는 컨텍스트에 직접 영향을 줍니다. 모든 사용자 메시지마다 같은 문장이 붙어 누적되므로, 백 문자가 늘면 한 세션 전체에서 수십 배의 토큰이 더 쌓일 수 있습니다. 절약을 위해 세 가지를 지킵니다. 첫째, 변하지 않는 사실은 CLAUDE.md에 두고, hook에는 매번 달라지는 값(날짜, 브랜치, 환경)만 둡니다. 둘째, 같은 세션 안에서 한 번만 보여 주어도 되는 안내는 SessionStart에서 처리하고, UserPromptSubmit에서는 반복합니다. 셋째, 분기 결과로 추가 문장을 끼우는 경우에는 한두 줄로 제한합니다.

프로젝트마다 다른 정책을 두는 일은 settings.json 단위로 깔끔하게 분리할 수 있습니다. 운영 레포에는 main push 금지·민감 파일 차단을 강조한 hook을 두고, 실험용 레포에는 더 가벼운 hook만 둡니다. 전역 정책은 `~/.claude/settings.json`에, 프로젝트 정책은 `.claude/settings.json`에, 개인 한정 정책은 `.claude/settings.local.json`에 적습니다. 두 위치의 UserPromptSubmit hook은 모두 실행되며, 출력은 순서대로 합쳐져 모델에게 도달합니다.

전체 데이터 흐름은 다음과 같이 한눈에 그릴 수 있습니다.

```
사용자 입력
        |
        v
UserPromptSubmit hook
  - 날짜·브랜치·환경 주입
  - 민감 키워드 검출(stderr 또는 exit 2)
        |
        v
hook stdout + 원문 메시지
        |
        v
모델에게 전달
```

정리하면, UserPromptSubmit은 표준 출력이 사용자 메시지 앞에 합쳐지는 점을 활용해, 매 메시지에 시점·환경·정책을 자동으로 끼워 넣을 수 있는 hook입니다. 시스템 리마인더 마커, 민감 키워드 검출, 길이 절약 원칙 세 가지를 함께 적용하면, 정책이 사람의 기억력에 의존하지 않고 일관되게 적용됩니다.

다음 단원인 4.1.5에서는 SessionStart hook으로 세션 시작 시점에 환경을 점검하고 준비 상태를 보고하는 방법을 다룹니다.

이 단원을 마치면 사용자 메시지 앞에 정책 문구를 자동으로 합치고, 위험 키워드를 검출해 경고하거나 차단하는 UserPromptSubmit hook을 작성할 수 있습니다.
