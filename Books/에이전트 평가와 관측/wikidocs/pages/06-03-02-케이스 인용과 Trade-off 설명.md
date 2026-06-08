# 6.3.2 케이스 인용과 Trade-off 설명

앞 단원에서 다섯 차원으로 답하는 표준 형식을 잡았다면, 이 단원에서는 그 답변에 사례를 어떻게 끼워 넣을지를 다룹니다. 사례를 인용하는 까닭은 단순히 박식해 보이기 위해서가 아니라, 본인이 내린 결정의 근거를 외부 레퍼런스에 연결해 청자가 검증 가능한 지점에 놓아 주기 위해서입니다. 같은 결정도 "이렇게 하기로 했다"고 말하는 것과 "JPMorgan이 이런 이유로 이렇게 풀었기에 우리도 그 패턴을 변형해 적용했다"고 말하는 것은 신뢰의 무게가 다릅니다.

이 책에서 본 여섯 사례를 한 문장씩 핵심 교훈으로 압축해 두면 인용이 빨라집니다. Anthropic Multi-Agent Research System은 prototype에서 production으로 갈 때 full production tracing이 들어가야 비로소 실패 원인을 분리할 수 있다는 사례입니다. Replit Agent는 가드레일조차 창의적 prompting으로 뚫리고 prescriptive eval만으로는 잡지 못하는 패턴이 있어 reactive eval과 hybrid 평가 스택이 필요하다는 사례입니다. JPMorgan LLM Suite는 250K 직원 규모에서 모델·보안·관측·거버넌스를 한 플랫폼에 모으고 8주 release train으로 거버넌스와 속도를 동시에 잡은 사례입니다. Klarna는 단일 메트릭에 최적화하면 hidden quality가 무너져 인간 상담사 재고용에 이르고 hybrid 모델로 회귀하게 된다는 반면교사 사례입니다. Palantir AIP는 비결정적 에이전트의 거버넌스를 다섯 차원으로 정의해 사실상 표준이 된 사례입니다. Demystifying Evals는 평가 환경의 isolation과 shared state 차단이 메트릭의 무결성을 좌우한다는 일반화 가이드입니다. 이 여섯 줄을 머릿속에 띄워 두면 어떤 질문이 와도 어느 사례가 적합한지 바로 매핑할 수 있습니다.

상황별 인용 매핑을 더 구체적으로 잡으면 다음과 같습니다. "프로토타입과 프로덕션의 차이가 무엇인가"라는 질문에는 Anthropic의 tracing 도입 전후 사례가 기본형이 됩니다. "평가는 어떻게 만들어 가는가"라는 질문에는 Replit의 reactive eval과 GPT-4o 자동 교체 발견 사례가 가장 효과적입니다. "거버넌스와 속도를 어떻게 같이 가져가는가"라는 질문에는 JPMorgan의 단일 API + 8주 release train이 표준 답안입니다. "단일 메트릭으로 평가하면 안 되는 이유가 무엇인가"라는 질문에는 Klarna의 CSAT 47% 증가와 인간 재고용의 역설이 가장 강합니다. "production 시스템의 거버넌스 차원을 어떻게 정의하는가"라는 질문에는 Palantir의 다섯 차원이 그대로 답이 됩니다. "평가 환경의 무결성은 어떻게 보장하는가"라는 질문에는 Demystifying Evals의 isolated trial 원칙과 git history 사례가 적합합니다. 질문 패턴별로 1번 인용을 미리 잡아 두면 답변에서 망설이는 시간이 사라집니다.

```
[ 질문 패턴 → 적절한 사례 ]

prototype/production 갭        → Anthropic tracing
가드레일/평가의 한계            → Replit reactive eval
거버넌스 + 속도                → JPMorgan 8주 release train
단일 메트릭의 함정             → Klarna hybrid 회귀
거버넌스 5차원                → Palantir AIP
평가 환경 무결성              → Demystifying Evals
프라이버시 보존 관측           → Anthropic 비공개 + 패턴 가시성
멀티에이전트 emergent behavior → Anthropic Lead + Subagent
```

여기서 한 단계를 더 올라가는 기법이 단순 인용에서 비교·대조로 옮기는 것입니다. 단순 인용은 "Klarna 사례처럼 단일 메트릭에 최적화하면 안 됩니다"로 끝나지만, 비교·대조는 "Klarna는 비용 절감을 단일 축으로 잡았다가 hybrid로 회귀했고, 같은 시기에 JPMorgan은 측정 가능한 문서 중심 프로세스부터 단계적으로 도입해 안정화 후에야 post-check로 이동했다, 이 둘의 차이는 다차원 KPI를 설계 단계에 넣었느냐 사후에 발견했느냐의 차이다"로 풀립니다. 비교·대조는 청자에게 사례 두 개를 동시에 활용한다는 인상을 주고, 본인이 사례를 외운 사람이 아니라 사례를 도구로 쓰는 사람이라는 신호를 보냅니다.

또 하나 자주 빠뜨리는 요소가 한계와 반례 함께 제시입니다. 어떤 사례도 만능이 아니므로, 인용한 사례의 한계를 같이 짚어 주는 답변이 더 단단합니다. 예컨대 Palantir의 다섯 차원을 답으로 내놓으면서 "이 다섯 차원은 엔터프라이즈 스케일을 전제로 한 것이라, 5명 이하 스타트업에서 그대로 적용하면 거버넌스 비용이 속도를 압도할 수 있다, 그래서 우리는 관측 차원만 baseline으로 잡고 나머지는 단계적으로 채우고 있다"고 말하면, 같은 사례 인용이지만 사고의 깊이가 다르게 느껴집니다. JPMorgan의 8주 release train도 마찬가지로, 한국의 작은 조직에서는 그대로 옮기면 시한 압박이 부담이 될 수 있고 4주나 격주로 변형해야 한다는 식의 한계가 따라붙어야 인용이 살아납니다. Klarna 사례는 강력하지만 모든 도메인에 그대로 일반화되지는 않으며, B2B 워크플로 자동화처럼 정량 정확도가 더 중요한 영역에서는 hidden quality 차원의 비중이 다르다는 점도 짚을 수 있습니다.

마지막으로 사례를 본인 시스템에 옮기는 방법을 풀어 두는 것이 인용의 마무리입니다. 사례는 인용에서 끝나지 않고 본인 결정과 어떻게 연결되는지 보여 줘야 답변이 닫힙니다. 예컨대 Anthropic의 비공개 + 패턴 가시성 패턴은 한국 상권 분석처럼 소상공인 데이터를 다루는 시스템에서 그대로 차용 가능하다는 식으로, 사례의 어느 조각을 본인 시스템에 옮겼고 어디는 변형했는지를 한두 문장으로 정리하면 됩니다. 6.1의 self-audit으로 약한 차원을 짚고, 6.2의 도입 로드맵으로 그 차원을 어느 시점까지 어떤 사례를 변형해 채울지를 말하면, 이 책 전체가 답변 한 덩어리에 녹아듭니다.

이제 책 전체를 한 번 회고하겠습니다. Phase 1에서는 에이전트 평가가 LLM 평가와 어떻게 다른지, 비결정성과 trajectory가 만드는 평가의 어려움, tool selection error·planning loop·hallucinated reasoning·premature termination이라는 failure mode taxonomy, 그리고 Klarna 사례로 본 단일 메트릭의 함정을 다뤘습니다. Phase 2에서는 골든 데이터셋 구축, LLM-as-Judge의 편향과 보정, trajectory 평가의 단계별 정확도, τ-bench·AgentBench·SWE-bench 학술 벤치마크, 그리고 평가 환경의 isolation을 통해 offline 평가 파이프라인을 설계했습니다. Phase 3에서는 실 트래픽 기반 online 평가, reactive vs prescriptive, LangSmith와 Langfuse의 trace 모델, 한국 기업의 의사결정 차원, OpenTelemetry GenAI semantic conventions를 따라 무벤더 락인 관측 스택까지 짰습니다. Phase 4에서는 tiered autonomy, circuit breaker, fallback routing, 임계치 기반 HITL과 escalation path로 신뢰성과 안전 패턴을 묶었습니다. Phase 5에서는 Anthropic·Replit·JPMorgan·Klarna·Palantir 다섯 케이스 스터디로 패턴을 추출했고, Phase 6에서는 self-audit·도입 로드맵·KPI 설계·거버넌스와 속도의 균형을 거쳐 마지막에 시스템 설명 framework와 케이스 인용까지 도착했습니다. 평가에서 시작해 관측을 거쳐 거버넌스로, 거버넌스에서 다시 실전 활용으로 이어지는 한 호가 그려집니다.

정리하면, 케이스 인용은 단순히 사례를 외우는 일이 아니라 질문 패턴별 매핑(Anthropic·Replit·JPMorgan·Klarna·Palantir·Demystifying Evals 여섯 줄), 비교·대조로 사고를 한 단계 올리기, 한계와 반례를 함께 제시해 단단함을 더하기, 그리고 본인 시스템에 어떻게 옮길지를 마지막에 닫아 주기로 완성됩니다. 이 흐름이 6.3.1의 다섯 차원 답변과 합쳐지면, 본인의 멀티에이전트 시스템을 production 수준으로 설명하는 표준 답변 한 세트가 갖춰집니다.

이 책을 마치면 비결정적 에이전트 시스템을 평가의 단위와 failure mode taxonomy로 분해하고, offline·online 평가 파이프라인과 LangSmith·Langfuse·OpenTelemetry 기반 관측 스택을 도입 의사결정과 함께 구성하며, tiered autonomy·circuit breaker·fallback·HITL의 신뢰성 패턴을 결합하고, Anthropic·Replit·JPMorgan·Klarna·Palantir 사례에서 추출한 교훈을 본인 시스템에 변형 적용하며, Palantir의 다섯 차원으로 self-audit과 도입 로드맵을 짜고, 면접·문서에서 일관된 framework로 시스템을 설명하면서 trade-off와 한계까지 함께 제시할 수 있습니다. 비결정적 시스템을 프로덕션에 올리는 일은 한 번에 정복되지 않고 평가·관측·거버넌스의 작은 결정들이 누적되며 단단해지는 작업이며, 이 책이 그 누적의 첫 한 호가 되었기를 바랍니다.
