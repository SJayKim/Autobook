# 5.1.2 Claude Code에 MCP 서버 추가

이전 단원 5.1.1에서 MCP가 외부 도구를 표준 인터페이스로 모델에 노출하는 약속이라는 점, 그리고 Claude Code가 두 위치(.mcp.json과 settings.json의 mcpServers)에 서버를 등록한다는 점을 정리했습니다. 이 단원에서는 실제로 서버를 추가하고, 권한을 부여하고, 응답이 없을 때 디버깅하는 절차를 다룹니다.

가장 간단한 방법은 `claude mcp add` 명령을 쓰는 것입니다. 명령 한 줄로 서버를 등록하고, Claude Code가 알아서 적절한 위치의 설정 파일에 항목을 적어 줍니다. 기본 형태는 다음과 같습니다.

```bash
claude mcp add github -- npx -y @modelcontextprotocol/server-github
```

명령의 앞부분은 두 토막입니다. `mcp add` 다음에는 서버의 **이름**을 적습니다. 여기서는 `github`라는 이름을 쓰겠다는 뜻이며, 이 이름이 권한 매처에 들어가는 식별자가 됩니다. 그 뒤의 `--`는 인자 구분자이며, 이후의 모든 토큰을 서버를 띄우는 **명령과 인자**로 그대로 넘깁니다. 예시에서는 npx로 공식 MCP github 서버 패키지를 띄웁니다. `-y` 옵션은 npx의 설치 확인 프롬프트를 건너뛰게 합니다.

이 명령이 실행되면 Claude Code는 등록 결과를 설정 파일에 기록합니다. 같은 효과를 직접 적는다면, 프로젝트 루트의 `.mcp.json`에 다음과 같이 둘 수 있습니다.

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

이 JSON은 한 서버를 정의합니다. `command`는 실제로 실행할 바이너리이고, `args`는 그 인자 배열입니다. `env`는 자식 프로세스에게 추가로 넘겨 줄 환경 변수입니다. 값 자리에 `${GITHUB_TOKEN}`처럼 적어 두면 현재 쉘의 환경 변수를 대입합니다. 토큰을 JSON에 직접 박지 않고 환경 변수를 거치게 두는 까닭은 두 가지입니다. 첫째, 비밀 값이 settings 파일과 함께 git에 올라가는 사고를 막습니다. 둘째, 사용자마다 다른 토큰을 한 설정 파일로 공유할 수 있습니다.

같은 내용을 settings.json에 둘 수도 있지만, 의미가 약간 다릅니다. .mcp.json은 한 프로젝트의 팀 공유용 등록을 모아 두는 자리입니다. git에 함께 올려 두면, 새 팀원이 레포를 받자마자 같은 MCP 서버를 자동으로 갖게 됩니다. 반면 settings.json에 등록한 MCP 서버는 그 settings 파일의 적용 범위(전역·프로젝트·로컬)를 그대로 따르므로, 개인용으로 한정하거나 다른 사람이 보지 못하게 둘 때 적합합니다. 정리하면 다음과 같은 기준을 두면 됩니다.

```
.mcp.json
  - 프로젝트의 모든 사용자가 같이 쓸 서버
  - git에 함께 올라감, 비밀 값은 env 변수로 우회

~/.claude/settings.json (전역)
  - 모든 프로젝트에서 공통으로 띄울 서버

.claude/settings.local.json (로컬)
  - 개인용·실험용, git에서 제외
```

서버를 등록했다면 그다음 단계는 권한 부여입니다. 5.1.1에서 본 대로 Claude Code는 MCP 도구를 권한 시스템에서 별도의 이름으로 다루며, 표기는 `mcp__SERVERNAME__TOOLNAME` 형식입니다. 구분자가 밑줄 두 개라는 점에 다시 한번 주의합니다. 예를 들어 github 서버의 list_issues 도구는 `mcp__github__list_issues`가 됩니다. 이 표기를 permissions에 넣어, 호출별로 허용·문의·차단을 분리합니다.

```json
{
  "permissions": {
    "allow": [
      "mcp__github__list_issues",
      "mcp__github__get_issue"
    ],
    "ask": [
      "mcp__github__create_issue",
      "mcp__github__update_issue"
    ],
    "deny": [
      "mcp__github__delete_repository"
    ]
  }
}
```

이 설정은 읽기 계열 호출은 자동 허용, 쓰기 계열 호출은 매번 사용자에게 묻기, 가장 파괴적인 호출은 차단합니다. 같은 패턴을 모든 MCP 서버에 동일하게 적용하면, 읽기는 매끄럽게 흐르되 쓰기 동작은 한 번씩 사람의 눈을 통과합니다. 와일드카드를 남발해 `mcp__github__*`를 통째로 allow에 넣지 않는 편이 좋습니다. 일부 서버는 이름이 비슷한 위험한 도구를 묶어 둘 때가 있어, 와일드카드가 의도치 않은 권한 확장을 만들기 쉽습니다.

이제 운영에서 가장 자주 만나는 상황을 다룹니다. 서버를 등록했는데 도구 목록이 나타나지 않거나 호출이 응답하지 않을 때입니다. 디버깅 순서는 다음과 같이 잡으면 빠릅니다.

```
1) claude mcp list로 등록 상태 확인
       |
       v
2) 서버 명령을 같은 셸에서 손으로 실행
   (npx, node, python 명령이 정상 종료 없이 stdin 대기 상태인지)
       |
       v
3) env가 제대로 전달되는지 확인
   (printenv 또는 echo $VAR로 토큰 비어 있는지)
       |
       v
4) Claude Code 디버그 모드로 재실행
   (--debug 또는 환경 변수 ANTHROPIC_LOG=debug)
       |
       v
5) hook과 권한 매처 점검
   (allow/ask/deny에서 mcp__... 표기가 맞는지)
```

첫 단계인 `claude mcp list`는 현재 인식된 서버와 출처를 한 줄씩 보여 줍니다. 예상한 서버가 빠져 있다면 등록 파일의 위치를 점검합니다. 다음 단계에서 서버 명령을 셸에서 직접 띄워 보는 까닭은, stdio 기반 MCP 서버는 정상 동작하면 표준 입력을 기다리며 가만히 떠 있어야 한다는 점을 확인하기 위해서입니다. 즉시 종료되거나 에러 메시지가 흐르면, 그 단계에서 원인을 잡습니다. 가장 흔한 원인은 `npx`가 패키지를 찾지 못하거나, 토큰 환경 변수가 비어 있어 서버가 시작 직후 종료하는 경우입니다.

세 번째 단계에서 환경 변수를 점검할 때는 토큰의 실제 값을 출력하지 않습니다. `printenv | grep TOKEN | head`처럼 키 이름만 확인하거나, 길이를 보고 비어 있지 않은지 정도만 봅니다. 비밀 값을 직접 콘솔에 띄우는 습관이 들면 4.1.4의 정책 주입이나 settings.local.json 격리가 무력해집니다.

네 번째 단계의 디버그 모드는 도구 호출과 응답의 원문을 보여 주므로, "분명 서버는 떠 있는데 모델이 도구를 부르지 못한다"는 상황의 원인을 빠르게 좁힙니다. 이름 철자가 어긋났거나, 서버가 빈 tools 목록을 돌려주는 경우가 자주 발견됩니다.

마지막 단계는 권한 매처입니다. 호출은 도착했는데 permissions.deny에 무심코 들어간 패턴이 그것을 막고 있을 수 있습니다. `mcp__server__*` 같은 와일드카드가 의도치 않게 잡고 있는지 확인하고, 필요한 도구는 정확한 이름으로 allow에 넣습니다. 5.1.1 표에서 보았듯 권한 표기의 구분자는 밑줄 두 개이며, 이 점이 가장 자주 틀리는 부분입니다.

서버를 더 이상 쓰지 않거나 잠시 끄고 싶을 때는 등록을 직접 지우거나 비활성화합니다. .mcp.json에서는 해당 객체 항목을 제거하면 되고, settings.json에서는 mcpServers의 키를 제거하면 됩니다. `claude mcp remove NAME` 명령으로 같은 효과를 줄 수도 있습니다. 한 번에 한 서버씩 끄면서 도구 목록이 정상 갱신되는지 확인하는 편이 안전합니다.

정리하면, Claude Code의 MCP 서버 등록은 `claude mcp add` 명령이나 .mcp.json/.claude/settings.json 편집으로 이루어집니다. 비밀 값은 env 필드의 환경 변수 치환을 통해 주입하고, 권한은 `mcp__server__tool` 표기를 allow·ask·deny에 적어 호출별로 통제합니다. 응답이 없을 때는 mcp list, 직접 실행, env 점검, 디버그 모드, 권한 매처의 5단계 순서로 좁혀 갑니다.

다음 단원인 5.1.3에서는 Codex CLI의 config.toml에 같은 형태의 MCP 서버를 등록하고, profile별로 서로 다른 묶음을 활성화하는 방법을 다룹니다.

이 단원을 마치면 Claude Code에 MCP 서버를 등록하고, 환경 변수로 토큰을 안전하게 주입하며, `mcp__server__tool` 표기로 권한을 부여하고, 응답이 없을 때 5단계 절차로 원인을 좁힐 수 있습니다.
