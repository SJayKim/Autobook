# 5.1.3 Codex CLI에 MCP 서버 추가

Codex CLI에서도 외부 도구를 늘리려면 MCP 서버를 등록해야 합니다. 다만 Claude Code와 등록 위치가 다르고, 같은 서버라도 적어 두는 방식이 미묘하게 다릅니다. 5.1.2에서 Claude Code 쪽 등록을 익혔다면, 이번에는 Codex CLI에서 동일한 작업을 하는 방법을 정리합니다. 한 레포에서 두 도구를 함께 쓸 때 어떻게 짝을 맞춰 두는지도 함께 봅니다.

Codex CLI는 모든 설정을 `~/.codex/config.toml` 한 파일에 모읍니다. 2.2.2에서 본 것처럼 이 파일은 TOML 형식이며, 섹션이 `[대괄호]`로 시작합니다. MCP 서버는 `[mcp_servers.NAME]` 블록으로 적습니다. `NAME` 자리에는 사용자가 정하는 서버 식별자가 들어가고, 이 이름이 이후 도구 이름의 접두어로 쓰입니다. 예를 들어 `filesystem`이라는 이름으로 등록하면, 모델이 호출하는 도구 이름은 `filesystem` 네임스페이스 아래에 묶입니다.

블록 안에는 세 개의 핵심 필드가 들어갑니다. `command`는 서버를 띄우는 실행 파일의 이름이나 절대 경로입니다. `args`는 그 실행 파일에 넘길 인자를 문자열 배열로 적습니다. `env`는 자식 프로세스에 주입할 환경 변수를 키·값으로 적는 인라인 테이블입니다. Codex CLI는 이 세 값을 들고 stdio 방식으로 서버를 띄웁니다. 서버 프로세스의 표준 입력과 표준 출력이 JSON-RPC 메시지를 주고받는 통로 역할을 합니다.

아래는 파일 시스템 서버를 등록하는 최소 예시입니다.

```toml
[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
env = { NODE_NO_WARNINGS = "1" }
```

여기서 `command = "npx"`는 Node 패키지를 한 번에 받아 실행하는 도구를 부르겠다는 뜻입니다. `args` 배열의 첫 원소 `-y`는 설치 확인 프롬프트를 건너뛰는 npx 옵션이며, 두 번째 원소는 받아 올 패키지 이름, 세 번째 원소는 서버에 넘기는 작업 디렉토리입니다. `env`의 `NODE_NO_WARNINGS`는 Node가 stderr로 띄우는 경고가 JSON-RPC 통신과 섞이지 않도록 막아 줍니다. 환경 변수에 토큰을 넣어야 한다면 같은 자리에 `GITHUB_TOKEN = "ghp_..."`처럼 적을 수 있지만, 비밀값은 직접 적기보다 셸의 환경 변수에서 가져오도록 두는 편이 안전합니다.

profile마다 다른 MCP 서버 구성을 두고 싶다면 `[profiles.NAME]` 섹션 아래에 같은 모양을 다시 적습니다. profile은 2.2.2에서 본 것처럼 작업 모드 묶음입니다. 예를 들어 정찰용 profile에서는 읽기 전용 서버만 노출하고, 실행용 profile에서는 더 강한 서버까지 허용할 수 있습니다.

```toml
[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]

[profiles.review]
sandbox_mode = "read-only"
approval_policy = "never"

[profiles.review.mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_TOKEN = "$GITHUB_TOKEN" }
```

위 구성은 전역으로 `filesystem` 서버를 두고, `review` profile에서는 추가로 `github` 서버를 활성화합니다. profile은 CLI에서 `codex --profile review`로 골라 들어갑니다. 같은 서버를 profile마다 다르게 켜고 끌 수도 있는데, 빈 블록으로 덮어쓰거나 `disabled = true`를 적는 방식으로 끄도록 두는 구성이 많습니다. 구체 표기는 설치된 Codex CLI 버전의 도움말로 확인합니다.

Claude Code와 Codex CLI에 동일 서버 구성을 공유하려면, 두 파일이 같은 정보를 가리키도록 맞춰 둡니다. Claude Code는 5.1.2에서 본 것처럼 `.mcp.json`이나 `settings.json`의 `mcpServers` 객체에 JSON 형식으로 적습니다. Codex CLI는 TOML 형식으로 적습니다. 형식은 다르지만 의미는 같으므로, 한쪽을 단일 기준 문서로 두고 나머지를 손으로 옮겨 두는 팀이 많습니다. 다음 그림이 두 도구의 관계를 정리합니다.

```
공통 의도: "filesystem 서버를 /work에 띄우고 모델에 노출한다"
                |
       +--------+--------+
       |                 |
  .mcp.json         ~/.codex/config.toml
  (Claude Code)     (Codex CLI)
       |                 |
       v                 v
   mcpServers       [mcp_servers.filesystem]
   객체에 JSON       블록에 TOML 필드
```

Codex CLI에서 MCP 도구가 실제로 호출될 때는 3.1.2에서 본 approval policy가 한 번 더 개입합니다. MCP 호출도 도구 호출의 한 종류이므로, 정책이 `untrusted`나 `on-request`라면 처음 보는 도구가 호출될 때 승인 창이 뜹니다. 반대로 정책이 `never`인 상태에서 작업을 자동으로 흘려보내려 한다면, MCP 도구가 일으키는 부수 효과까지 미리 검토해 둬야 합니다. sandbox 모드도 마찬가지여서, `read-only` profile에 파일을 쓰는 MCP 도구를 두면 호출 자체는 가능해도 쓰기 시점에서 sandbox가 거부합니다. 정책과 sandbox, MCP 서버 권한 셋이 같은 작업을 세 겹으로 둘러싼다고 생각하면 안전합니다.

등록한 서버가 동작하는지 확인할 때는 Codex CLI를 실행해 도구 목록을 받는 방식이 가장 빠릅니다. `codex` 세션 안에서 도구 목록을 출력하도록 지시하거나, `codex exec`로 짧은 쿼리를 한 번 보내 보면 됩니다. 서버가 묵묵부답이면 보통 두 가지 원인 중 하나입니다. 첫째, `command`가 PATH에서 찾을 수 없거나 인자가 잘못된 경우입니다. 둘째, 서버 자체가 stderr에 경고를 흘려서 stdio 채널을 깨뜨린 경우입니다. 후자는 `NODE_NO_WARNINGS` 같은 환경 변수로 잡거나, 서버 패키지가 권장하는 시작 옵션을 살펴 해결합니다.

정리하면, Codex CLI에서 MCP 서버는 `~/.codex/config.toml`의 `[mcp_servers.NAME]` 블록에 `command`, `args`, `env`로 적고, profile마다 다르게 활성화할 수 있습니다. Claude Code와 동일 서버를 두고자 한다면 `.mcp.json`과 짝을 맞춰 형식만 다르게 적습니다. MCP 호출은 approval policy와 sandbox 모드의 검사를 추가로 통과해야 하므로, 세 겹의 안전망 안에서 도구가 동작한다는 점을 기억해 둡니다.

다음 단원인 5.2.1에서는 자주 쓰는 작업을 슬래시 커맨드와 skill로 묶어, 한 줄 호출로 재사용하는 방법을 다룹니다.

이 단원을 마치면 `config.toml`의 MCP 서버 블록을 직접 작성하고, profile별로 다르게 활성화하며, Claude Code와 동일 서버 구성을 공유하는 구성을 설명할 수 있습니다.
