# 3.2.2 devcontainer로 격리 실행

3.2.1에서 다룬 sandbox 모드는 모델이 할 수 있는 동작을 제한하지만, 그 모든 동작은 결국 사용자의 호스트 운영체제 위에서 일어납니다. 호스트에는 보통 SSH 키, 다른 프로젝트의 토큰, 브라우저 쿠키 같은 민감 자원이 함께 놓여 있습니다. sandbox가 작업 디렉토리 밖을 막아 준다고 해도, 도구를 호스트에 직접 설치해 두면 실수로 다른 경로를 읽거나 시스템 명령이 의도 밖 자원에 접근하는 사고가 생길 수 있습니다.

이 부담을 줄이는 방법이 devcontainer로 격리 실행하는 것입니다. devcontainer는 VS Code가 정의한 컨테이너 기반 개발 환경 규격으로, `devcontainer.json` 한 파일에 컨테이너 이미지와 초기화 명령을 정리해 두면, 같은 환경을 누구든 똑같이 띄울 수 있습니다. 컨테이너 안쪽에서 Claude Code와 Codex CLI를 돌리면, 호스트는 컨테이너에 마운트한 경로 외에는 보이지 않게 됩니다.

가장 단순한 구성은 `.devcontainer/devcontainer.json`을 레포 루트에 두는 형태입니다. 컨테이너가 만들어진 직후 두 CLI를 한꺼번에 설치하도록 `postCreateCommand`를 둡니다.

```json
{
  "name": "agent-cli-sandbox",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:20",
  "postCreateCommand": "npm install -g @anthropic-ai/claude-code @openai/codex",
  "remoteEnv": {
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}",
    "OPENAI_API_KEY": "${localEnv:OPENAI_API_KEY}"
  },
  "mounts": [],
  "runArgs": ["--network=none"]
}
```

`postCreateCommand`는 컨테이너 생성 직후 한 번만 실행되는 초기화 명령입니다. 위 예시에서는 npm 글로벌 설치로 두 CLI를 함께 깔아 둡니다. 매 세션마다 다시 깔지 않아도 되도록 컨테이너 이미지의 초기화 단계에 묶어 두는 것입니다.

호스트 파일 시스템을 어디까지 보여 줄지는 `mounts`로 제어합니다. 위 예시는 빈 배열로 두어 명시적 마운트를 두지 않았습니다. 이 경우 VS Code devcontainer 기본 동작에 따라 작업 중인 워크스페이스만 컨테이너에 마운트되고, 호스트의 홈 디렉토리나 다른 프로젝트 폴더는 보이지 않습니다. 더 좁히고 싶다면 작업 디렉토리의 하위만 마운트하도록 별도 마운트 규칙을 두면 됩니다. 반대로 호스트 git 설정을 함께 쓰고 싶을 때는 `~/.gitconfig`만 골라 읽기 전용으로 마운트합니다. 모델은 마운트되지 않은 경로를 아예 인지하지 못하므로, 차단보다 한 단계 강한 격리가 됩니다.

네트워크는 보통 가장 위험한 채널입니다. 모델이 의도하지 않은 호스트로 데이터를 송신하거나, 외부에서 임의의 패키지를 받아 실행할 가능성을 닫아야 합니다. 가장 단순한 방법은 `runArgs`에 `--network=none`을 넣어 컨테이너의 네트워크 인터페이스 자체를 비활성화하는 것입니다. 이 상태에서는 컨테이너 안의 어떤 프로세스도 외부와 통신할 수 없으므로, 모델이 어떤 URL을 부르더라도 응답이 돌아오지 않습니다.

다만 모델 API 자체도 네트워크 통신을 필요로 합니다. `--network=none` 상태에서는 Claude Code나 Codex CLI가 모델 추론 요청을 보내지 못해 동작이 멎습니다. 실무에서는 프록시를 두고 그 프록시만 통과시키는 구성을 선호합니다. 컨테이너 안 환경 변수에 `HTTPS_PROXY=http://proxy:8080`을 두고, 프록시 쪽에서 모델 호출만 허용하면, 그 외 모든 외부 통신은 차단됩니다.

```json
{
  "remoteEnv": {
    "HTTPS_PROXY": "http://proxy.internal:8080",
    "HTTP_PROXY": "http://proxy.internal:8080",
    "NO_PROXY": "localhost,127.0.0.1"
  }
}
```

위 예시처럼 컨테이너에 프록시를 주입하면, 모든 외부 호출이 프록시를 거치게 됩니다. 모델 API 도메인만 허용 목록에 두면 외부 침투 면적이 크게 줄어듭니다.

토큰 주입은 호스트에 평문으로 두지 않는 것이 원칙입니다. 위 예시의 `remoteEnv`에서 `${localEnv:ANTHROPIC_API_KEY}` 표기는 컨테이너를 띄우는 순간 호스트의 환경 변수를 읽어 컨테이너 안 환경 변수로 전달하라는 지시입니다. 호스트 셸 환경 변수나 비밀 관리자에서 가져온 값이 컨테이너 안에서만 살아 있고, 컨테이너가 꺼지면 함께 사라집니다. 토큰을 파일로 마운트하지 않으면, 작업이 끝난 컨테이너 이미지에 비밀이 남지 않습니다.

CI나 원격 머신에서 같은 환경을 다시 띄울 때는 같은 `devcontainer.json`을 그대로 사용합니다. GitHub Actions에는 devcontainer를 빌드해 그 안에서 명령을 돌려 주는 액션이 있고, 직접 `docker run` 명령으로도 같은 이미지를 띄울 수 있습니다. 한 사람의 작업 환경과 자동화 환경이 한 파일로 묶여, 한쪽에서 잘 동작하던 작업이 다른 쪽에서는 동작하지 않는 격차를 줄여 줍니다.

```text
호스트  ─ devcontainer.json ─▶ 컨테이너
                                ├─ Claude Code / Codex CLI (postCreate에서 설치)
                                ├─ 작업 디렉토리 (mounts로 제한)
                                ├─ 토큰 (remoteEnv로 주입, 종료 시 휘발)
                                └─ 네트워크 (프록시 또는 --network=none)
```

이 그림은 호스트와 컨테이너 사이에 무엇이 어떤 통로로 흐르는지 한눈에 보여 줍니다. 마운트, 환경 변수, 네트워크의 세 통로만 통제하면 컨테이너는 호스트와 분리된 작업 공간이 됩니다.

정리하면, devcontainer는 `devcontainer.json` 하나로 컨테이너 이미지, 초기 설치, 마운트, 네트워크, 토큰 주입을 함께 정의해 두 CLI를 격리 실행하는 표준 방법입니다. 호스트 파일 시스템의 노출 범위와 네트워크 경로를 명시적으로 좁히고, 동일 구성으로 CI까지 확장할 수 있습니다.

다음 단원인 3.2.3에서는 sandbox·컨테이너로 큰 경계를 만든 위에, `rm -rf`나 `curl | sh` 같은 구체적 위험 명령을 두 도구에서 동시에 차단하는 레시피를 다룹니다.
