# 1.2.2 Codex CLI 설치와 첫 세션

Codex CLI는 한 번에 한 작업을 분명히 마치는 방식을 선호하는 환경에 잘 맞습니다. 다만 첫 세션을 띄울 때 sandbox 모드와 approval policy를 함께 잡지 않으면, 기본값이 무엇인지 모른 채 강한 권한으로 명령이 흐를 수 있습니다. 이 단원에서는 설치, 인증, 첫 명령 실행, 그리고 안전한 첫 모드 설정까지를 순서대로 정리합니다.

설치 방법은 세 가지입니다. npm 전역, Homebrew, 소스 빌드 중 환경에 맞는 한 가지를 고릅니다.

```bash
# 옵션 1: npm 전역
npm install -g @openai/codex

# 옵션 2: Homebrew (macOS·Linux)
brew install codex

# 옵션 3: 소스 빌드 (오픈 소스 저장소를 클론한 뒤)
# 빌드 가이드는 저장소 README를 따른다.
```

세 가지 중 가장 빠른 길은 npm입니다. Homebrew는 macOS·Linux에서 시스템 패키지 관리와 함께 묶기 편하고, 소스 빌드는 사내 정책으로 사전 검토된 바이너리만 허용해야 하는 경우에 씁니다. 설치 후 `codex --version`이 응답하는지 확인합니다.

인증은 두 갈래입니다. 첫째는 **OpenAI API 키**를 환경 변수에 넣는 방식입니다. `OPENAI_API_KEY`를 셸에 등록해 두면 Codex CLI가 자동으로 사용합니다. 둘째는 **ChatGPT 로그인** 방식으로, `codex login` 명령이 브라우저를 열어 계정 인증을 진행합니다. API 키 방식은 사용량이 API 계정에서 차감되고, ChatGPT 로그인 방식은 구독 플랜의 한도가 적용됩니다. 둘은 결제 경로가 다르므로, 팀에서 어느 쪽을 표준으로 둘지 미리 정합니다.

```bash
export OPENAI_API_KEY="sk-..."   # 방식 A: API 키
codex login                      # 방식 B: ChatGPT 로그인
```

인증을 마치면 작업 폴더로 이동해 첫 명령을 실행합니다. 한 줄 명령은 다음 두 형태가 있습니다.

```bash
# 대화형 모드 (Claude Code의 claude와 유사한 진입)
codex

# 비대화형 실행 (한 작업만 시키고 종료)
codex exec "이 디렉터리의 README를 한 문단으로 요약해 줘"
```

`codex`는 대화형 세션을 띄워 사용자와 모델이 여러 차례 주고받게 합니다. `codex exec`는 작업 한 단위를 비대화형으로 돌리고, 결과를 표준 출력과 변경된 파일로 회수합니다. 두 형태 모두 현재 작업 디렉터리를 기준 폴더로 잡으며, 그 폴더 안의 `AGENTS.md`가 있으면 자동으로 읽어 컨텍스트에 포함합니다. 작업 디렉터리는 이후 sandbox 범위의 기준이 되는 핵심 정보이므로, 의도하지 않은 폴더에서 띄우지 않도록 주의합니다.

이제 **sandbox 모드**를 짚습니다. Codex CLI의 기본 sandbox는 `workspace-write`입니다. 이 모드는 작업 디렉터리 안의 파일을 읽고 쓸 수 있지만, 그 바깥의 파일과 네트워크는 막습니다. 둘러보기만 하고 변경은 막고 싶다면 `read-only`로 한 단계 낮춥니다. 모든 제약을 풀고 호스트 전체에 접근해야 하는 드문 경우에만 `danger-full-access`를 쓰며, 이름 그대로 위험이 큰 모드입니다. 모드 전환은 CLI 플래그로 가능합니다.

```bash
# read-only로 전환 (정찰·코드 리뷰용)
codex --sandbox read-only

# workspace-write 기본 모드 (명시적으로 지정)
codex --sandbox workspace-write
```

다음은 **approval policy**입니다. sandbox가 막은 동작에 대해 모델이 어떻게 요청해야 하는지를 정합니다. 네 가지 선택지가 있습니다. `untrusted`는 권한 밖 동작을 시도할 때마다 사용자 확인을 받습니다. `on-failure`는 한 번 실패한 뒤 같은 요청이 다시 올 때 사용자에게 묻습니다. `on-request`는 모델이 명시적으로 권한 상승을 요청할 때만 묻습니다. `never`는 묻지 않고 거부합니다. 첫 세션은 **on-request** 권장입니다. 일반 작업은 sandbox 안에서 그대로 진행되고, 모델이 정말 필요하다고 판단할 때만 사용자에게 묻기 때문에, 불필요한 확인이 줄어들면서도 권한 상승 시점은 분명해집니다.

```bash
# 첫 세션 권장 조합
codex --sandbox workspace-write --ask-for-approval on-request
```

이 한 줄을 첫 세션의 표준으로 두면, 작업 디렉터리 안에서 자유롭게 변경하면서도 그 바깥으로 나가는 시도는 사용자가 인지하게 됩니다. 익숙해진 뒤에는 정책을 `config.toml`에 옮겨 두면 매번 플래그를 적지 않아도 같은 효과를 얻습니다.

정리하면, npm·Homebrew·소스 중 한 가지로 Codex CLI를 설치하고, OpenAI API 키나 ChatGPT 로그인으로 인증한 뒤, `codex` 또는 `codex exec`로 첫 명령을 띄웁니다. 첫 세션은 sandbox를 `workspace-write`로, approval policy를 `on-request`로 잡는 조합이 안전합니다.

다음 단원인 2.1.1에서는 Claude Code가 자동으로 읽는 `CLAUDE.md`를 효과적인 섹션 구조로 작성하는 패턴을 다룹니다.
