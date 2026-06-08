# 3.1.1 Claude Code permissions 모델

settings.json(2.2.1)에서 가장 자주 쓰는 필드는 permissions였습니다. 자주 쓰지만 정확히 이해하지 않으면 두 가지 사고가 흔히 일어납니다. 첫째는 와일드카드를 너무 넓게 두어 파괴적 명령까지 자동 통과시키는 사고이고, 둘째는 차단 규칙을 적었는데도 모델이 우회 명령으로 실행해 버리는 사고입니다. 이 단원에서는 permissions 객체의 네 배열이 어떻게 결정에 관여하는지, 도구 매처를 어떤 표기로 적는지, 같은 명령이 allow와 deny에 동시에 들어 있을 때 어느 쪽이 이기는지, 그리고 작업 디렉토리 밖 경로를 어떻게 다루는지를 차례로 풀어 봅니다.

permissions 객체는 네 개의 배열을 가집니다. **allow**는 사전 동의 없이 통과시킬 패턴, **deny**는 어떤 경우에도 막을 패턴, **ask**는 통과 전에 사용자에게 한 번 확인을 받을 패턴, **additionalDirectories**는 작업 디렉토리 밖에서 추가로 접근을 허용할 디렉토리 목록입니다. 네 배열 모두 문자열의 배열이며, 각 문자열은 도구 매처 표기를 따릅니다.

도구 매처 표기는 `도구이름(인자 패턴)` 형태입니다. 도구 이름은 Bash·Read·Write·Edit처럼 모델이 호출할 수 있는 도구의 이름이고, 괄호 안에는 그 도구에 넘기는 인자에 대한 패턴을 둡니다. Bash의 경우 명령어 문자열을 패턴으로 잡으며, Read·Write·Edit는 파일 경로를 패턴으로 잡습니다. 패턴 안의 `*`는 임의 길이의 임의 문자열을 의미하며, `**`는 경로에서 디렉토리 경계를 넘어 매칭됩니다.

```
Bash(git status:*)       git status로 시작하는 모든 명령 (인자 무관)
Bash(npm test:*)         npm test로 시작하는 모든 명령
Read(./src/**)           ./src 아래 모든 파일·하위 디렉토리 읽기
Write(~/.ssh/**)         홈의 .ssh 아래 모든 쓰기
Edit(./.env*)            .env로 시작하는 파일 편집 (.env, .env.local 등)
```

Bash 매처에서 `:*`로 표기하는 부분은 명령의 인자 영역을 의미합니다. `Bash(git status:*)`는 `git status`, `git status -s`, `git status --porcelain`처럼 git status 다음에 무엇이 오든 모두 잡습니다. 반면 `Bash(git status)`처럼 콜론 별표가 없으면 정확히 인자가 없는 git status만 잡으므로 의도와 어긋나기 쉽습니다. 명령의 부분 문자열에 무엇이 들어 있는지로 매칭하고 싶다면 `Bash(*--force*)`처럼 양쪽에 별표를 두는 패턴도 가능합니다.

다음은 자주 쓰는 패턴을 정리한 표입니다.

```
의도                       패턴 예시
git 읽기 명령 전부 허용     "Bash(git status:*)", "Bash(git diff:*)", "Bash(git log:*)"
파괴적 git 차단             "Bash(git push --force:*)", "Bash(git reset --hard:*)"
프로젝트 소스 읽기          "Read(./src/**)", "Read(./tests/**)"
민감 파일 차단              "Read(./.env)", "Write(./.env*)", "Read(./secrets/**)"
홈 비밀 키 차단             "Read(~/.ssh/**)", "Read(~/.aws/credentials)"
패키지 설치 확인 받기       "Bash(npm install:*)", "Bash(pip install:*)"
```

이제 가장 중요한 결정 규칙을 못 박아 두겠습니다. **deny는 allow보다 항상 우선합니다.** 같은 명령이 allow와 deny에 동시에 들어 있으면 deny가 이깁니다. 이 순서는 두 가지 이유에서 중요합니다. 첫째, 와일드카드로 넓게 allow를 두면서도 위험한 가지를 deny로 잘라낼 수 있습니다. 예를 들어 `Bash(git:*)`로 git 명령을 전부 허용하면서 `Bash(git push --force:*)`를 deny에 두면 push --force만 막힙니다. 둘째, 사용자 기본 ~/.claude/settings.json에서 deny한 항목은 어떤 프로젝트 설정으로도 풀 수 없습니다. 팀 표준이나 회사 정책으로 절대 깨지면 안 되는 규칙을 가장 윗 레이어에 못 박는 방식으로 활용합니다.

ask는 allow와 deny 사이의 회색 지대를 처리합니다. 패턴이 ask에 매칭되면 모델은 명령을 부르기 전에 멈추고 사용자에게 한 번 확인을 받습니다. 사용자가 허락하면 그 명령만 실행되고 같은 세션의 이후 동일 명령도 잠깐 통과될 수 있으나, 다음 세션이 되면 다시 묻습니다. 작업 빈도가 어중간한 명령, 예컨대 의존성 추가나 마이그레이션처럼 자주 쓰지는 않지만 가끔 합리적인 명령을 ask에 두면 사고 없이 흐름을 이어 갈 수 있습니다.

```json
{
  "permissions": {
    "allow": [
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(npm test:*)",
      "Read(./src/**)",
      "Read(./tests/**)"
    ],
    "deny": [
      "Bash(git push --force:*)",
      "Bash(rm -rf:*)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(~/.ssh/**)",
      "Write(~/.ssh/**)"
    ],
    "ask": [
      "Bash(npm install:*)",
      "Bash(git push:*)",
      "Write(./src/**)"
    ],
    "additionalDirectories": [
      "/var/log/myapp"
    ]
  }
}
```

마지막으로 **additionalDirectories**를 풀어 보겠습니다. Claude Code의 도구는 기본적으로 작업 디렉토리(보통 프로젝트 루트) 아래에서만 파일을 읽고 쓰도록 제한됩니다. 디버그 로그가 `/var/log/myapp`처럼 프로젝트 밖에 있어 함께 봐야 할 때, 이 배열에 그 경로를 추가하면 해당 디렉토리도 작업 디렉토리처럼 취급됩니다. 그러나 additionalDirectories에 추가했다고 해서 deny에 적힌 패턴이 풀리지는 않습니다. 즉 `Read(~/.ssh/**)`를 deny에 두었다면 additionalDirectories에 홈을 넣어도 .ssh는 여전히 막힙니다. 이 구조 덕분에 '더 넓은 작업 범위'와 '절대 손대지 말아야 할 자리'를 동시에 운영할 수 있습니다.

흔히 빠지는 함정 하나를 짚어 두겠습니다. allow에 `Bash(*)`처럼 모든 셸 명령을 통과시키는 패턴을 두면 deny에 적힌 명시 패턴 외에는 전부 자동 실행됩니다. 모델이 새로운 명령 조합을 만들어 내면 deny에 없는 한 통과되므로, 사용자가 예상치 못한 명령이 자유롭게 돌게 됩니다. 권장 방향은 반대입니다. allow는 자주 쓰는 명령을 좁게 열거하고, 회색 명령은 ask에 두고, 위험한 명령만 deny에 못 박는 식으로 두면 새로 등장하는 명령에 대해 모델은 자연스럽게 사용자에게 묻게 됩니다.

정리하면, permissions는 allow·deny·ask·additionalDirectories 네 배열로 도구 호출의 허용·차단·확인·범위 확장을 결정합니다. 매처는 `도구이름(인자 패턴)` 형식이며 `:*`로 인자 영역을 잡습니다. deny는 allow보다 항상 우선하므로, 넓게 허용하고 위험을 잘라 내거나 좁게 허용하고 회색 지대를 ask로 보내는 두 운영 방식 모두 가능합니다. additionalDirectories는 작업 범위만 넓힐 뿐 deny 규칙을 풀지 못합니다.

다음 단원인 3.1.2에서는 Codex CLI 쪽의 approval policy 네 가지를 살펴보고 sandbox와 결합되는 방식을 정리합니다.

이 단원을 마치면 Claude Code의 권한 규칙을 패턴 단위로 작성하고, 우선순위와 함정을 설명할 수 있게 됩니다.
