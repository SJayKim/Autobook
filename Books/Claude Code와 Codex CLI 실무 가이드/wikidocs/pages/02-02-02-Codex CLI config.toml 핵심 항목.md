# 2.2.2 Codex CLI config.toml 핵심 항목

Codex CLI도 모델·권한·외부 서버를 설정 파일로 통제한다는 점에서는 Claude Code와 같지만, 파일 형식과 위치가 다릅니다. 2.2.1에서 다룬 settings.json은 JSON 형식이며 프로젝트와 사용자 양쪽에 분산되어 있었습니다. Codex CLI는 사용자 홈 한 곳의 TOML 파일에 모든 설정을 모으고, 프로젝트별 변형은 같은 파일 안의 **profile** 블록으로 분리합니다. 이 단원에서는 config.toml의 위치와 환경 변수 우선순위, 핵심 필드, MCP 서버 등록, profile 분리, CLI 플래그와의 우선순위 관계를 정리합니다.

config.toml의 기본 위치는 **~/.codex/config.toml**입니다. Codex CLI는 세션을 시작할 때 이 파일 한 개를 읽고, 같은 사용자 계정의 모든 프로젝트에 동일한 기본값을 적용합니다. 프로젝트마다 다른 설정이 필요하면 파일을 여러 개로 쪼개지 않고 한 파일 안에서 profile로 나눕니다. 환경 변수로 같은 값을 덮어쓰고 싶을 때는 `CODEX_` 접두를 가진 변수를 쓰며, 환경 변수가 파일보다 더 우선합니다. 마지막으로 CLI 실행 시 붙이는 플래그가 가장 높은 우선순위를 가집니다.

```
우선순위(낮음 → 높음)
~/.codex/config.toml         (사용자 기본)
~/.codex/config.toml의 profile  (프로필 활성화 시 적용)
CODEX_* 환경 변수            (셸 단위 덮어쓰기)
CLI 플래그                   (이번 실행만 적용)
```

이제 최상위에서 자주 쓰는 필드를 풀어 보겠습니다. **model**은 세션의 기본 모델 이름으로, 비용·성능을 사용자 단위로 통일할 때 둡니다. **model_provider**는 모델을 제공하는 백엔드 식별자로, OpenAI 외에 호환 API를 쓰는 경우에 바꿉니다. **approval_policy**는 모델이 명령을 실행하기 전에 사용자에게 확인을 받을 빈도를 결정하며 untrusted·on-failure·on-request·never 중 하나입니다. **sandbox_mode**는 파일 시스템과 네트워크 접근을 어디까지 허용할지를 결정하며 read-only·workspace-write·danger-full-access 중 하나입니다. approval_policy와 sandbox_mode가 어떻게 결합되는지는 3.1.2와 3.2.1에서 자세히 다룹니다.

```toml
model = "gpt-5-codex"
model_provider = "openai"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_TOKEN = "${GITHUB_TOKEN}" }

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "/repo"]
```

`[mcp_servers.NAME]` 섹션은 외부 MCP 서버를 등록하는 자리로, 각 서버마다 한 블록씩 만듭니다. **command**는 서버 실행 명령, **args**는 명령에 붙는 인자 배열, **env**는 그 서버에만 주입되는 환경 변수입니다. 위 예시는 stdio 방식의 서버를 등록한 형태이며, 표준 입출력으로 JSON-RPC 메시지를 주고받습니다. SSE 방식 서버를 쓰고 싶다면 command 대신 URL을 받는 필드를 사용하는 형태가 되며, 이 부분은 5장에서 자세히 풀어 갑니다.

profile은 같은 사용자 계정에서 프로젝트나 작업 성격별로 다른 모드를 쓰고 싶을 때 사용합니다. 형식은 `[profiles.NAME]` 블록이며, 그 안에 최상위와 같은 필드를 적으면 됩니다. 활성화는 `codex --profile NAME` 또는 `CODEX_PROFILE=NAME` 환경 변수로 합니다.

```toml
[profiles.review]
approval_policy = "never"
sandbox_mode = "read-only"

[profiles.dangerous]
approval_policy = "on-request"
sandbox_mode = "danger-full-access"
```

위 예시에서 review profile은 코드 리뷰처럼 파일을 읽기만 하면 되는 작업을 위해 sandbox를 read-only로 묶고, 모델에게 매번 확인을 묻지 않아도 안전하도록 approval_policy를 never로 둡니다. dangerous profile은 컨테이너 안에서 호스트 자원을 적극적으로 만져야 하는 특수 작업에만 활성화하며, 평상시에는 절대 켜지 않습니다. 한 사용자 계정 안에서도 이렇게 명확히 분리해 두면 실수로 위험한 모드가 일상에 흘러드는 일을 막을 수 있습니다.

CLI 플래그와 config의 관계를 마지막으로 정리합니다. `--ask-for-approval untrusted` 같은 플래그는 이번 실행 한 번에만 적용되며, config.toml과 환경 변수와 profile을 모두 무시하고 가장 우선합니다. 같은 맥락에서 `--sandbox read-only`도 한 번의 실행을 강제로 읽기 전용으로 묶을 때 씁니다. 이 우선순위는 두 가지 상황에서 유용합니다. 첫째는 평소 설정을 그대로 두고 한 번만 더 보수적으로 가고 싶을 때이고, 둘째는 자동화 스크립트에서 환경에 상관없이 동일한 동작을 강제하고 싶을 때입니다.

정리하면, Codex CLI의 모든 설정은 ~/.codex/config.toml 한 파일에 모이고 환경 변수와 CLI 플래그가 위에서 덮어쓰는 구조입니다. model·model_provider·approval_policy·sandbox_mode가 최상위 핵심 필드이며, [mcp_servers.NAME]으로 외부 서버를 등록하고 [profiles.NAME]으로 프로젝트별 모드를 분리합니다. 같은 정보를 여러 파일로 흩지 않고 한 파일 안에서 명확히 나누는 것이 Codex CLI 설정 운용의 출발점입니다.

다음 단원인 3.1.1에서는 Claude Code의 permissions 모델을 패턴 단위로 깊이 풀어 봅니다.

이 단원을 마치면 config.toml의 주요 섹션을 이해하고 profile을 분리해 프로젝트별로 다른 모드를 안전하게 운용할 수 있게 됩니다.
