# 6.2.1 Codex CLI 작업 분해와 profile

한 레포에서 코드 리뷰만 시키고 싶을 때가 있고, 변경을 곧바로 적용하게 두고 싶을 때가 있습니다. 같은 도구를 매번 손으로 옵션을 바꿔 가며 호출하다 보면 권한 실수가 누적되기 쉽습니다. 6.1.2에서 본 Plan mode가 Claude Code 쪽에서 단계 합의를 강제하는 장치였다면, Codex CLI에서는 작업의 성격을 미리 묶어 둔 **profile**과 한 번에 마치는 **비대화형 실행**이 같은 역할을 합니다. 이 단원에서는 두 장치를 함께 써서 큰 작업을 여러 갈래로 나누어 돌리는 방법을 정리합니다.

먼저 profile이라는 말을 풀어 두겠습니다. Codex CLI에서 profile은 ~/.codex/config.toml 안에 정의하는 **이름이 붙은 설정 묶음**입니다. 모델, sandbox 모드, approval policy, MCP 서버 목록 같은 항목을 한 묶음으로 저장해 두고, CLI를 호출할 때 `--profile NAME`으로 한 번에 골라 쓸 수 있게 합니다. 2.2.2에서 본 config.toml의 최상위 필드가 기본값을 정한다면, profile은 그 위에 덮어쓰는 변형판입니다.

읽기 전용 정찰과 쓰기 실행을 분리한 두 profile을 예로 잡아 보겠습니다.

```toml
# ~/.codex/config.toml

model = "gpt-5-codex"
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[profiles.scout]
model = "gpt-5-codex"
sandbox_mode = "read-only"
approval_policy = "never"

[profiles.builder]
model = "gpt-5-codex"
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

최상위에 둔 세 줄은 profile을 따로 지정하지 않았을 때의 기본값입니다. 그 아래의 `[profiles.scout]`는 코드 베이스를 훑고 보고만 하는 정찰용입니다. sandbox가 read-only이므로 파일 쓰기와 네트워크 호출이 막혀 있고, approval policy가 never이므로 권한 밖 동작을 사용자에게 묻는 일도 없이 그냥 거부됩니다. `[profiles.builder]`는 실제 변경을 적용하는 작업용입니다. sandbox는 작업 디렉토리에 쓰기를 허용하는 workspace-write이며, approval policy는 on-request로 두어 모델이 그 한계를 벗어나는 일을 시도할 때만 사용자에게 묻습니다. 같은 모델, 같은 레포에서 두 모드를 매번 손으로 토글하는 대신 `codex --profile scout` 또는 `codex --profile builder`로 부르면 됩니다.

profile을 골라 비대화형으로 한 번에 끝내는 형태가 `codex exec`입니다.

```bash
codex --profile scout exec "src/payments 디렉토리의 결제 로직을 읽고 \
   비동기 처리 누락이 있는지 점검 보고서를 docs/notes/payments.md로 작성해 줘"
```

`codex` 다음에 둔 `--profile scout`가 어떤 설정 묶음으로 돌릴지를 정하고, `exec` 뒤의 따옴표 안 문장이 한 번에 처리할 작업 지시입니다. 대화형 세션과 달리 `exec`는 시작과 끝이 명확합니다. 표준 출력으로 결과 요약이 나오고, 작업이 끝나면 셸로 제어가 돌아옵니다. read-only profile과 결합하면 보고서를 쓰는 동작이 안 되니, 위 예처럼 docs 하위로 메모를 떨궈 두고 싶다면 보고서 경로를 workspace-write가 허용하는 디렉토리 안으로 두거나 builder profile로 바꾸어 다시 호출해야 합니다. 이 분리가 어색해 보일 수 있지만, 정찰 단계에서 코드가 변경되지 않는다는 보장을 얻는 대가입니다.

여러 작업을 한꺼번에 돌릴 때는 격리 단위를 무엇으로 잡을지를 먼저 정합니다. 가장 단순한 격리 단위는 **작업 디렉토리** 자체입니다. 같은 레포의 사본을 두 디렉토리에 만들어 두고 한쪽은 scout, 다른 쪽은 builder로 동시에 돌리면 sandbox가 서로 다른 파일 트리만 보게 되어 충돌이 생기지 않습니다. 다음 단순한 격리 단위는 **profile**입니다. 디렉토리는 같아도 sandbox와 approval policy가 다르므로, 한 번에 한 profile만 그 디렉토리를 만지게 순서를 정해 돌리면 변경 사항이 섞이지 않습니다. 더 엄격한 격리가 필요하면 3.2.2에서 본 devcontainer를 별도로 띄워 컨테이너 단위로 분리합니다.

```
[큰 작업]
  ├─ scout profile        (read-only)
  │     └─ codex exec "..."  →  분석 노트
  ├─ builder profile      (workspace-write)
  │     └─ codex exec "..."  →  코드 변경
  └─ review profile       (read-only)
        └─ codex exec "..."  →  diff 검토
```

이 그림은 큰 작업 하나를 세 갈래로 나눠 돌리는 표준 흐름입니다. 정찰로 시작해 변경을 적용하고, 변경 후에 다시 read-only로 돌려 결과를 점검합니다. 세 단계가 같은 모델이라도 sandbox와 approval policy가 다르므로 각 단계의 자유도와 위험이 다르게 묶여 있고, 단계 사이에 사람이 끼어들어 확인할 자연스러운 멈춤 지점이 생깁니다.

`codex` 명령 외에 더 큰 단위의 작업을 띄우는 통로로 Codex Cloud가 있습니다. 이는 코드를 클라우드 환경에서 격리된 컨테이너로 받아 실행시키는 호출 방식입니다. 본 토픽 범위에서는 깊이 다루지 않지만, 흐름만 짚자면 로컬에서 작업 명세를 작성해 클라우드로 전송하고, 결과 diff와 로그를 회수해 로컬 레포에 적용하는 순서입니다. profile과 sandbox는 클라우드 측에서 사전에 묶여 있는 형태이며, 호출하는 쪽은 어떤 작업 단위를 보낼지에 집중합니다.

각 작업이 끝난 뒤 검토 워크플로는 두 갈래로 나누어 잡는 것이 무난합니다. 첫째는 표준 출력 로그입니다. `codex exec`가 토해 낸 로그는 작업 실행 중 모델이 무엇을 호출하고 어떤 결과를 받았는지가 시간 순서로 정리되어 있어, 이를 한 파일로 저장해 둡니다. 둘째는 작업 디렉토리의 diff입니다. `git diff`나 IDE의 변경점 보기로 어떤 파일이 어떻게 바뀌었는지를 사람이 직접 살피고, 의도와 맞지 않는 변경이 섞여 있는지를 확인합니다. profile 분리 덕에 scout 단계에서는 diff가 비어 있어야 정상이라는 사실이 보장 항목이 되고, builder 단계에서만 의미 있는 변경이 발생하는 것을 단계의 정상 종료 조건으로 잡을 수 있습니다.

정리하면, Codex CLI에서는 config.toml의 `[profiles.NAME]`으로 sandbox·approval·model 묶음을 이름으로 묶어 두고, `codex --profile NAME exec "..."`로 한 작업을 한 번에 끝내는 형태로 큰 일을 여러 갈래로 나눕니다. 정찰은 read-only, 적용은 workspace-write, 검토는 다시 read-only로 단계를 분리하면 자유도와 안전이 단계마다 명확해지고, 작업 디렉토리·profile·컨테이너 중 하나를 격리 단위로 골라 병렬과 순차 실행을 통제할 수 있습니다.

다음 단원인 6.2.2에서는 이렇게 띄운 작업을 백그라운드로 두고 진행 상황을 비파괴적으로 모니터링하는 방법을 다룹니다.

이 단원을 마치면 Codex CLI의 profile을 분리하고 codex exec로 작업 단위를 나누어 동일 레포에서 여러 모드를 운용할 수 있게 됩니다.
