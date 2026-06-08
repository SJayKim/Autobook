# 3.1.2 Codex CLI approval policy

Claude Code는 명령 단위로 허용·차단·확인을 패턴으로 적는 방식이었습니다(3.1.1). Codex CLI는 다른 길을 택합니다. 패턴 목록을 길게 두기보다 '모델이 명령을 부를 때 사용자에게 얼마나 자주 확인을 받을 것인가'라는 정책 하나를 골라 두고, 그 정책을 sandbox 모드와 결합해 위험도를 조절합니다. 이 단원에서는 네 가지 approval policy의 동작 모델, sandbox와의 결합, 팀 상황별 적정 선택, CLI 플래그로 일시 전환하는 패턴, 정책별 위험·생산성 트레이드오프를 정리합니다.

approval policy는 다음 네 값 중 하나입니다. **untrusted**는 모델이 명령을 부를 때마다 사용자에게 확인을 받는 가장 보수적인 정책입니다. **on-failure**는 평소에는 자동으로 통과하지만 명령이 실패했거나 sandbox에 막혀 결과를 못 받았을 때만 확인을 받습니다. **on-request**는 모델이 스스로 '이 명령은 사람의 확인이 필요해 보인다'고 판단할 때만 확인을 받습니다. **never**는 어떤 경우에도 사용자에게 묻지 않고 모델이 자율로 실행합니다.

```
정책          확인 시점                          말로 풀면
untrusted    모든 명령 실행 전                  '한 줄도 자동으로 돌리지 마'
on-failure   실패·sandbox 차단 발생 시          '문제 생기면 그때만 물어'
on-request   모델이 필요하다고 판단 시          '네가 스스로 판단해서 물어'
never        없음                                '전부 알아서 돌려'
```

각 정책이 sandbox 모드와 결합되는 방식을 풀어 보겠습니다. sandbox 모드는 파일 시스템과 네트워크 접근을 어디까지 허용할지를 결정하며 read-only·workspace-write·danger-full-access 세 값이 있습니다(2.2.2). approval policy는 그 위에서 '실행 자체를 자동으로 통과시킬지 사람에게 물을지'를 결정합니다. 두 축이 독립적으로 보이지만 실제로는 서로 보완 관계입니다.

read-only sandbox와 on-failure를 결합하면, 모델은 파일을 읽고 명령을 돌릴 수 있지만 어떤 명령도 디스크를 바꾸지 못합니다. 코드를 바꾸려는 시도는 sandbox에 막혀 실패하고, on-failure 정책이 그제야 사용자에게 확인을 묻습니다. 이 결합은 정찰·리뷰 작업에서 안전과 속도를 동시에 잡습니다. workspace-write sandbox와 on-request를 결합하면, 모델은 작업 디렉토리 안에서 파일을 자유롭게 쓰지만 위험해 보이는 결정에서만 사람을 부릅니다. 이 결합이 일반 개발 작업에 가장 자주 권장되는 조합입니다.

danger-full-access와 never의 결합은 가장 강력하면서 가장 위험합니다. 모델은 호스트의 어떤 파일·네트워크 자원에도 접근할 수 있고 사용자는 한 번도 묻지 않습니다. 이 조합은 격리된 일회용 컨테이너 안이거나, 자동화 파이프라인의 마지막 단계처럼 다른 안전망이 충분히 둘러싼 환경에서만 정당화됩니다. 일상적인 로컬 개발에서 이 조합을 켜는 것은 사고로 직결되기 쉽습니다.

팀 환경에서 정책별 적정 시나리오를 정리하면 다음과 같습니다.

```
시나리오                                권장 정책        sandbox          비고
처음 도입하는 팀, 보수적 운용            untrusted       read-only        매 명령 확인
정찰·리뷰 작업                          on-failure      read-only        실패 시만 확인
일반 개발 작업                          on-request      workspace-write  모델 판단에 위임
신뢰 환경에서 자동화                    never           workspace-write  격리·로그 필수
일회용 컨테이너에서 전권                never           danger-full      별도 격리 환경
```

CLI 플래그로 정책을 일시 전환하는 패턴도 자주 씁니다. config.toml에 평소 정책을 on-request로 두었더라도, 잠깐 더 보수적으로 가고 싶을 때는 `codex --ask-for-approval untrusted "..."`로 실행 한 번만 untrusted로 바꿀 수 있습니다. 반대로 자동화 스크립트에서 항상 never로 강제해야 한다면 `codex --ask-for-approval never`를 스크립트 안에 박아 두면 환경 설정과 무관하게 동일하게 동작합니다. 플래그가 config보다 우선하므로, 평소 설정을 건드리지 않고도 한 번씩 다르게 가져갈 수 있습니다.

```bash
# 평소 설정: on-request + workspace-write
codex "src/api 폴더의 타입 에러를 고쳐 줘"

# 이번 한 번만 더 보수적으로
codex --ask-for-approval untrusted "src/api 폴더의 타입 에러를 고쳐 줘"

# 코드 리뷰 profile로 잠깐 전환
codex --profile review "src/api 폴더의 위험 패턴을 정리해 줘"
```

마지막으로 정책별 위험·생산성 트레이드오프를 정리합니다. untrusted는 사고 위험이 가장 낮지만 매 명령마다 흐름이 끊겨 생산성이 가장 낮습니다. on-failure는 평소에는 흐름이 끊기지 않다가 실패할 때만 확인을 받으므로 정찰 작업의 균형점입니다. on-request는 모델 판단에 위임하기 때문에 모델의 안전 감각에 의존하지만, 잘 훈련된 모델 기준으로 가장 자연스러운 균형을 보입니다. never는 생산성은 최고이나 사고 시 손실이 즉시 일어나므로 안전망이 다른 층에 갖춰져 있어야 합니다.

```
정책          위험 노출    흐름 끊김    적정 환경
untrusted     매우 낮음    매우 잦음    민감 레포, 초기 도입
on-failure    낮음         가끔         정찰·리뷰
on-request    보통         가끔         일반 개발
never         높음         없음         격리·자동화
```

정리하면, Codex CLI의 approval policy는 사용자 확인 빈도를 untrusted·on-failure·on-request·never 네 단계로 묶은 정책입니다. sandbox 모드와 결합하여 안전과 속도의 균형을 잡으며, 평소 정책은 config.toml에 두고 일시 전환은 CLI 플래그로 처리하는 것이 표준 운용 방식입니다. 정책마다 위험과 생산성의 트레이드오프가 분명하므로, 시나리오별로 한 칸씩 조정하는 감각이 핵심입니다.

다음 단원인 3.2.1에서는 sandbox 모드 세 가지의 동작을 더 깊이 살펴보고 작업별 선택 기준을 정리합니다.

이 단원을 마치면 네 가지 approval policy의 차이를 설명하고, 팀 상황과 작업 성격에 맞는 정책을 선택할 수 있게 됩니다.
