# 3.2.1 Codex CLI sandbox 모드 활용

Codex CLI로 같은 레포에 두 가지 작업을 시키는 상황을 떠올려 봅니다. 한쪽에서는 빠른 코드 리뷰만 시키고 싶고, 다른 쪽에서는 실제로 파일을 수정해 커밋까지 만들고 싶습니다. 두 작업을 같은 권한으로 돌리면, 리뷰 도중 모델이 충동적으로 파일을 고치거나 외부 서버에 요청을 보내는 일이 생깁니다. 작업 성격에 맞춰 권한을 갈아 끼우는 장치가 필요합니다.

Codex CLI는 이 문제를 sandbox 모드로 해결합니다. 3.1.2에서 다룬 approval policy가 사용자에게 묻는 흐름을 정한다면, sandbox는 모델이 처음부터 할 수 있는 동작의 한계를 정합니다. sandbox는 파일 시스템과 네트워크에 운영체제 수준의 제한을 걸어, 모델이 의도를 가지고 시도해도 그 경계 밖으로는 나가지 못하게 만듭니다.

Codex CLI에는 세 가지 sandbox 모드가 있습니다. **read-only**는 작업 디렉토리를 포함해 어떤 파일도 쓸 수 없고, 네트워크 요청도 차단됩니다. 읽기만 가능하므로 모델은 파일을 열어 분석한 결과를 답변으로만 돌려보냅니다. **workspace-write**는 작업 디렉토리 안쪽에 한해 쓰기를 허용하지만, 네트워크는 기본적으로 막아 둡니다. 모델은 코드를 고치고 테스트를 돌릴 수는 있어도, 외부 패키지 저장소나 임의의 API로 나가지는 못합니다. **danger-full-access**는 이름 그대로 모든 제한을 풉니다. 호스트의 임의 경로에 쓸 수 있고 네트워크도 열립니다.

세 모드의 차이를 표로 정리하면 다음과 같습니다.

| 모드 | 파일 쓰기 | 네트워크 | 적합한 작업 |
| --- | --- | --- | --- |
| read-only | 모두 차단 | 차단 | 코드 리뷰, 정찰, 질의응답 |
| workspace-write | 작업 디렉토리 안만 허용 | 기본 차단 | 일반 개발, 테스트 |
| danger-full-access | 제한 없음 | 허용 | 격리된 컨테이너 안에서만 |

read-only 모드는 정찰 작업에 잘 어울립니다. 새로 인수받은 레포의 구조를 파악하거나, 보안 검토를 시키거나, 함수 호출 관계를 추적할 때 사용합니다. 모델이 잘못 판단해 파일을 고치려 해도 운영체제가 거부하므로, 결과를 받기 전까지 레포는 손대지 않은 상태로 보존됩니다.

```bash
codex --sandbox read-only "src/ 디렉토리의 모듈 의존 관계를 정리해 줘"
```

이 명령은 한 번의 작업 동안 read-only sandbox를 강제합니다. 모델이 답변 중 파일을 쓰려 하면 시스템 호출이 거부되고, approval policy 설정에 따라 사용자에게 승격을 요청하거나 작업을 중단합니다.

workspace-write는 실제 개발 작업의 기본값입니다. 모델은 `cwd`로 진입한 디렉토리, 즉 작업 디렉토리 안쪽에서는 파일을 만들고 고치고 삭제할 수 있습니다. git 명령도 그 안에서 정상적으로 동작합니다. 다만 외부 호스트로 나가는 네트워크는 기본적으로 차단되어 있어, 새 패키지를 받거나 임의의 웹 API를 부르려면 별도 승격이 필요합니다. 이는 모델이 충동적으로 외부 의존성을 추가하지 못하게 막아 줍니다.

```bash
codex --sandbox workspace-write "버그 #123을 고치고 테스트를 추가해 줘"
```

이 명령은 한 작업 동안 작업 디렉토리에 쓰기를 허용합니다. 모델이 파일을 고치고 테스트를 돌릴 수 있지만, 네트워크 의존이 생기는 순간 sandbox가 막거나 approval로 넘깁니다.

danger-full-access는 모든 한계를 푸는 모드입니다. 호스트 어느 경로에든 쓰기가 가능하고 네트워크도 열립니다. 컨테이너 안처럼 외부와 격리된 환경에서만 정당화되며, 호스트 데스크톱에서 직접 켜는 것은 사고로 이어지기 쉽습니다. 이 모드를 일상적으로 쓰지 않는 것이 원칙이고, 부득이한 경우에도 일회성 명령에 한정해 사용합니다.

모드를 작업마다 갈아 끼우는 방법은 세 가지입니다. 첫째, CLI 플래그 `--sandbox`로 지정합니다. 작업 한 번에만 적용되어, 평소 설정을 건드리지 않고 일시 전환할 수 있습니다. 둘째, `~/.codex/config.toml`의 `sandbox_mode` 필드로 기본값을 정합니다. 셋째, profile 단위로 분리합니다. 정찰용 profile에는 read-only, 개발용 profile에는 workspace-write를 두고 `--profile` 플래그로 전환합니다.

```toml
# ~/.codex/config.toml

sandbox_mode = "workspace-write"
approval_policy = "on-request"

[profiles.recon]
sandbox_mode = "read-only"
approval_policy = "never"

[profiles.devbox]
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

이 설정에서 평소 명령은 workspace-write로 시작합니다. 정찰 작업에 들어갈 때는 `codex --profile recon "..."`으로 read-only로 전환합니다. profile은 사람이 어떤 모드인지 한 줄로 인지하게 해 주고, 실수로 다른 모드를 켜는 일을 줄입니다.

마지막으로 모드 전환을 on-request approval policy와 함께 두는 방법이 있습니다. 평소에는 read-only로 시작하고, 모델이 쓰기가 필요한 순간 사용자에게 승격을 요청하게 합니다. 사용자는 승인 시 작업 한 동안만 workspace-write로 올려 줄 수 있습니다. 모드를 명시적으로 묶어 두고, 변경은 매번 사용자가 확인하는 방식입니다.

정리하면, Codex CLI sandbox는 read-only, workspace-write, danger-full-access 세 모드로 모델 동작의 한계를 정합니다. 작업 성격에 맞춰 모드를 고르고, 전환은 CLI 플래그·config.toml·profile·on-request 승격 가운데 상황에 맞는 수단을 선택합니다.

다음 단원인 3.2.2에서는 sandbox만으로 부족한 상황을 위해, devcontainer로 두 도구를 컨테이너 안에서 격리해 실행하는 구성을 다룹니다.
