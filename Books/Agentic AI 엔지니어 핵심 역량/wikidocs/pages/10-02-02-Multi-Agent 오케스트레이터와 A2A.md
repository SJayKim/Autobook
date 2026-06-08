# 10.2.2 Multi-Agent 오케스트레이터와 A2A

한 Agent로 풀 수 있는 문제는 빠르게 한계에 닿습니다. 시스템 프롬프트를 길게 늘리고 tool을 50개 넘게 묶으면 모델은 길을 잃습니다. 이 시점에서 자주 등장하는 답이 multi-agent입니다. 면접 케이스로는 'Research Agent, Coding Agent, QA Agent를 합쳐 보고서 생성 시스템을 설계하세요'에 해당합니다. 핵심은 supervisor가 전문성을 가진 specialist들을 어떻게 부르고, 어떤 메시지 모델로 주고받으며, 장기 실행을 어떻게 견디게 하느냐입니다.

요구사항을 숫자로 고정합니다. 한 번의 사용자 요청에 평균 3개 specialist가 협업, 한 협업 세션은 5분 이상 30분 이하, 동시 세션 1,000건, specialist는 총 10종이고 각자 평균 5개 tool을 가집니다. 한 세션의 LLM 호출은 평균 20회, 비용은 0.5달러 안팎입니다. 이 숫자가 supervisor의 throughput, 메시지 큐 깊이, 영속화 빈도를 정합니다.

이 위에 고수준 다이어그램을 그립니다.

```
                       [사용자 요청]
                              |
                              v
                  +-------------------------+
                  |      Supervisor         |
                  |  (계획·라우팅·종료)     |
                  +-----+-------+-------+---+
                        |       |       |
              +---------+       |       +---------+
              v                 v                 v
   +----------------+ +----------------+ +----------------+
   | Researcher A.  | | Coder Agent    | |  QA  Agent     |
   | tools: search, | | tools: repo,   | | tools: lint,   |
   |        scrape  | |  patch, build  | |  test, eval    |
   +-------+--------+ +-------+--------+ +-------+--------+
            \                |                  /
             \               v                 /
              +----- A2A 메시지 버스(큐) ------+
                              |
                              v
                  +-------------------------+
                  | Session Store (영속화)  |
                  |  - 메시지 로그          |
                  |  - 부분 결과            |
                  +-------------------------+
```

박스별 책임을 답니다. **Supervisor**는 전체 세션의 주인입니다. 사용자 요청을 받아 어느 specialist에게 어떤 sub-task를 줄지 결정하고, 결과를 모아 다음 단계를 정합니다. 종료 조건도 supervisor가 가집니다. **Specialist Agent**는 한정된 tool과 좁은 시스템 프롬프트를 가진 작은 Agent입니다. supervisor가 자신을 부를 때만 깨어나고, 자신의 영역 밖 도구는 호출하지 않습니다. 책임을 좁힌 만큼 평가도 specialist 단위로 따로 돌릴 수 있어 회귀 추적이 쉬워집니다.

**Supervisor 책임**을 좀 더 풀어 보겠습니다. 첫째, plan 작성과 갱신입니다. 처음 받은 요청을 sub-task 트리로 분해하고, 각 sub-task에 specialist를 매핑합니다. 둘째, 라우팅입니다. specialist 카탈로그에서 sub-task에 가장 잘 맞는 후보를 고릅니다. 셋째, 통합입니다. 여러 specialist의 부분 결과를 합쳐 사용자가 받을 최종 답을 만듭니다. 넷째, 종료 판단입니다. plan이 모두 끝났는지, 더 이상 새 sub-task가 필요 없는지를 결정합니다. 종료 조건을 명시하지 않으면 supervisor는 무한히 sub-task를 생성합니다. 안전장치로 'max_turn 10, max_cost 5달러, max_wall_clock 30분' 같은 hard limit을 함께 둡니다.

**Specialist Agent 분리**의 기준은 '도구의 결이 다른가'입니다. 검색 tool과 코드 빌드 tool이 한 Agent에 같이 들어가면 시스템 프롬프트가 비대해지고 모델이 도구 선택을 잘못합니다. 한 Agent의 tool은 7개 안팎까지가 안정선이고, 그 이상은 분리 신호로 봅니다. 사고가 났을 때 책임의 경계가 명확해지는 부수 효과도 따라옵니다. Researcher가 잘못된 자료를 가져왔는지, Coder가 패치를 잘못 짰는지를 trace에서 한눈에 가릅니다.

가운데 핵심은 **Handoff 프로토콜**입니다. supervisor가 specialist를 부를 때 그냥 함수 호출처럼 인자를 넘기는 방식과, 한 대화에 다른 페르소나가 들어와 이어서 답하는 방식 두 가지가 자주 쓰입니다. 전자는 'task envelope'라 부르고 후자는 'persona swap'이라 부릅니다. envelope 방식이 더 명시적이라 영속화·재시도가 쉽고 실무에서 다수입니다. envelope에는 최소한 다섯 필드가 들어갑니다. `task_id`, `goal`, `inputs`, `constraints`, `expected_output_schema`입니다. 이 다섯이 명확하면 specialist가 받자마자 일을 시작할 수 있습니다.

이 envelope를 실어 나르는 채널이 **A2A 메시지 모델**입니다. A2A(Agent-to-Agent)는 두 Agent가 직접 통신할 때 쓰는 메시지 스키마와 전달 규약을 가리킵니다. 단순한 함수 호출과 다른 점 세 가지를 외워 두면 됩니다. 첫째, 비동기 기본입니다. specialist가 30초 이상 걸리는 일을 할 수 있어 supervisor는 응답을 기다리지 말고 callback 또는 polling으로 받습니다. 둘째, 상태 식별자입니다. 모든 메시지에 `session_id`와 `task_id`를 담아 어느 세션의 어느 sub-task에 속하는지 잃지 않습니다. 셋째, schema 강제입니다. 입력과 출력이 JSON Schema 또는 protobuf로 고정되어 supervisor가 specialist의 결과를 신뢰하고 합칠 수 있습니다. 흔한 메시지 타입은 `task.start`, `task.progress`, `task.result`, `task.error` 네 가지입니다.

메시지를 큐로 보낼지 직접 HTTP로 보낼지는 선택입니다. 1,000건 동시 세션, 30분 실행 같은 요구에서는 큐가 거의 강제됩니다. supervisor 인스턴스가 떨어져도 큐에 남은 메시지를 다른 인스턴스가 이어 처리합니다. 큐 위에서 동작하면 우선순위와 retry도 자연스럽게 들어옵니다. 짧은 요청은 동기 HTTP로도 가능하지만 운영을 두 모드로 유지하면 복잡해지니 한 모드로 통일하는 편이 좋습니다.

**장기 실행과 영속화**가 multi-agent의 마지막 관문입니다. 30분짜리 세션 도중 supervisor 워커가 죽으면 어떻게 이어가야 할지를 미리 정해 둡니다. 세션 단위의 모든 상태를 RDB의 `sessions`·`tasks`·`messages` 세 테이블에 직렬화합니다. 각 task는 `pending`, `running`, `done`, `failed` 상태를 가지며, 워커가 부팅 시 자기 lock의 running task를 다시 집어 들거나 다른 워커에게 넘깁니다. 이 동작을 가능하게 하려면 specialist 호출이 idempotent해야 합니다. 같은 task_id가 두 번 처리돼도 결과가 같도록 task_id를 부작용의 키로 씁니다.

여기서 자주 빠지는 부분이 **부분 실패** 처리입니다. 한 sub-task가 실패했을 때 전체를 다시 돌리지 말고, supervisor가 'replan' 결정을 내려 실패한 부분만 다시 시도하거나 다른 specialist로 대체합니다. 이 결정도 trace에 남깁니다. 운영 6개월 뒤 'replan이 가장 자주 일어나는 sub-task 종류는 무엇인가'를 묻는 회의를 할 때 trace가 답을 줘야 합니다.

면접 트레이드오프는 셋입니다. 첫째, **Supervisor 단일 vs 계층**. 작은 시스템은 supervisor 한 명이 충분하지만, sub-task가 다시 협업이 필요한 복잡한 도메인에서는 specialist 그룹마다 sub-supervisor를 두는 계층 구조가 등장합니다. 단 계층이 깊어질수록 디버깅이 급격히 어려워집니다. 둘째, **A2A 직접 통신 vs supervisor 경유**. specialist끼리 직접 메시지를 주고받으면 빠르지만 trace 복원이 어렵습니다. supervisor 경유 모델은 latency가 한 hop 더 들지만 한 곳에서 모든 흐름이 보입니다. 셋째, **자율성 수준**. specialist가 자체 plan을 짤지, supervisor 지시만 따를지의 결정입니다. 자체 plan은 유연하지만 비용이 들고, 지시 추종은 결정론적이지만 한계가 큽니다. 흔한 절충은 'specialist는 한 sub-task 안에서만 ReAct, 세션 단위 plan은 supervisor가 독점'입니다.

확장 시나리오 한 줄씩. 새 specialist 추가는 카탈로그 INSERT와 라우팅 정책 한 줄이면 끝납니다. 모델 교체는 specialist 단위로 따로 합니다. human-in-the-loop는 supervisor가 특정 sub-task에서 사용자 승인 메시지를 큐로 보내고, 응답이 올 때까지 세션을 `paused` 상태로 두는 방식으로 자연스럽게 들어옵니다.

정리하면, multi-agent 시스템은 책임이 좁은 specialist를 supervisor가 plan·라우팅·통합·종료의 네 책임으로 조율하는 구조이고, A2A 메시지 모델은 비동기·session_id·schema 강제 세 가지를 통해 장기 실행과 부분 실패를 견디게 합니다. 영속화는 task 단위 상태 머신과 idempotent 호출 키로 잡습니다.

다음 단원인 10.2.3에서는 specialist 한 명이 다뤄야 할 도구 수가 1,000개로 폭증했을 때 라우팅·캐싱·평가를 어떻게 설계하는지를 살펴봅니다.
