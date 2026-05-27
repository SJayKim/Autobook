# 10.3.1 LLM Gateway 설계

여러 Agent와 RAG·도구 라우터까지 가세하면 한 회사의 LLM 호출은 빠르게 일 수백만 건이 됩니다. 호출을 만든 쪽이 모델 키, 비용 제어, 재시도 정책, 캐시 정책을 각자 짜기 시작하면 사고는 시간 문제입니다. 이번 단원은 그 모든 호출을 한 박스를 통해 흘려보내는 LLM Gateway의 설계를 다룹니다. 면접 케이스로는 'GPT, Claude, 사내 vLLM을 함께 쓰는 회사의 공통 LLM 인프라를 설계하세요'에 해당합니다.

요구사항을 숫자로 고정합니다. 일 호출 500만 건, peak QPS 200, 평균 응답 토큰 800, 동시 사용 모델 5종, 사용 팀 30개, 월 LLM 예산 30만 달러, 한 호출 평균 latency 2초 이내, 모델 사고 발생 시 5초 안에 fallback 가능해야 합니다. 이 숫자가 캐시 적중률 목표와 quota 분배의 단위를 정합니다.

이 위에 고수준 다이어그램을 그립니다.

```
   [Client SDK / Agent Platform]
              |
              v
   +------------------------+
   |   Auth + Tenant 식별   |
   +-----------+------------+
               |
               v
   +------------------------+
   |   Quota / Budget 검사  |
   +-----------+------------+
               |
               v
   +------------------------+        +-----------------+
   |   Cache Lookup          |<------>|  Cache Store    |
   |  (Prefix + Semantic)    |        |  (Redis+Vec)    |
   +-----------+------------+        +-----------------+
               | miss
               v
   +------------------------+
   |   Router 정책           |
   |  (model·region·class)  |
   +-----+-------+-------+--+
         v       v       v
   +---------++--------++---------+
   | OpenAI  || Anthr. || vLLM   |
   | Adapter || Adapter|| Adapter |
   +----+----++---+----++----+----+
        \         |         /
         v        v        v
        +-------------------+
        | Fallback / Retry  |
        +---------+---------+
                  |
                  v
        +-------------------+
        |  Observability    |
        |  Trace + 감사     |
        +-------------------+
```

박스별 책임을 답니다. **Auth**는 클라이언트의 토큰을 검증하고 tenant·user·team을 식별합니다. 이 단계의 출력 `context`는 이후 모든 박스에 전달됩니다. **Quota/Budget**은 사전 차단입니다. 팀별 월 예산과 시간당 토큰 quota를 검사해 한도를 넘으면 즉시 429로 거절합니다. 사후 정산이 아니라 사전 차단이 핵심입니다. 사고 후 청구서가 도착하는 패턴은 항상 분쟁으로 끝납니다.

**Provider abstraction**은 다음 박스입니다. OpenAI, Anthropic, vLLM, Bedrock 같은 공급자별 SDK 차이를 한 인터페이스 뒤에 숨깁니다. Adapter는 입력 메시지·tool 정의를 공급자 포맷으로 바꾸고, 응답을 다시 공통 schema로 정규화합니다. 공통 schema는 OpenAI Chat Completions 호환을 기본으로 두고 사내 확장 필드를 더하는 형태가 흔합니다. 새 공급자 추가는 Adapter 한 클래스 작성으로 끝나야 합니다.

**Routing 정책**의 결정 변수는 네 가지입니다. 첫째, 모델 등급. 'gpt-4 tier, claude-sonnet tier, 사내 14B tier' 같은 등급을 두고 호출자가 명시적으로 등급을 요청하거나 자동 라우팅을 허용합니다. 둘째, region. 데이터 거주성 요구에 따라 EU·KR·US로 라우팅을 강제합니다. 셋째, 비용·latency 균형. 현재 트래픽이 평균 latency를 넘으면 가벼운 모델로 자동 fallback합니다. 넷째, 실험 분기. A/B 트래픽 분기를 router 단에서 잡으면 client 코드 변경 없이 실험이 굴러갑니다.

**Fallback**은 사고 흡수의 마지막 줄입니다. 일차 모델이 실패하거나 timeout이 나면 미리 정의된 fallback 사다리를 따라 다음 모델로 재시도합니다. 사다리는 보통 세 단입니다. 동일 공급자의 같은 모델 → 다른 region → 다른 공급자의 동급 모델. 마지막 단까지 실패하면 client에 표준 에러를 돌려주고 trace에 사고를 표시합니다. fallback은 자동 retry와 다릅니다. retry는 같은 모델을 다시 부르는 것이고, fallback은 다른 모델로 옮기는 것입니다. 동시에 무한 fallback이 되지 않도록 'max 3 hops, 총 wall-clock 5초' 같은 hard limit을 둡니다.

다음은 캐시입니다. **Prefix Cache**는 같은 시스템 프롬프트·tool 정의가 반복될 때 그 prefix의 KV cache를 모델 서버에서 재사용하는 기능이며, gateway 측에서는 캐시 키를 정확히 분리해 hit율을 높이도록 메시지 정규화를 담당합니다. 같은 prefix가 들어가도 사용자 ID나 timestamp가 prompt 안에 박혀 있으면 hit률이 0이 됩니다. Gateway는 prefix와 동적 영역을 분리해 client가 명시적으로 dynamic 필드를 표시하게 강제합니다. 잘 정리하면 prefix cache hit률은 60% 이상으로 올라갑니다.

**Semantic Cache**는 한 단계 더 나갑니다. 사용자 질의의 의미가 같으면 모델을 부르지 않고 이전 응답을 돌려줍니다. 키는 query의 임베딩이고 값은 응답 본문입니다. 비교는 코사인 유사도 임계값으로 합니다. 사용 시점에는 두 가지 주의가 따라옵니다. 첫째, 동의어가 정답을 바꾸는 도메인에서는 매우 보수적인 임계값을 씁니다. 둘째, 시간에 민감한 답은 TTL을 짧게 두거나 캐시를 끕니다. 'OpenAI의 어제 발표' 같은 질의를 캐시에 가두면 사고가 됩니다. semantic cache hit이라도 미세하게 다른 입력이라 trace에는 'cache_hit_semantic'으로 별도 표시해 둡니다.

캐시는 비용과 latency를 동시에 줄입니다. prefix는 latency 위주, semantic은 비용 위주의 효과가 큽니다. 둘을 합쳐 30~50% 절감을 노릴 수 있고, 캐시 적중률을 일 단위로 보면서 cap을 조정합니다.

**Quota·Budget**의 구현은 두 층으로 나눕니다. 빠른 path는 Redis에 'team:tokens_used_today' 같은 카운터를 두고 호출 직전에 +N 시도 후 한도 초과면 거절합니다. 느린 path는 일 1회 배치로 청구 데이터와 카운터를 대조해 drift를 보정합니다. budget은 비용 단위로 따로 둡니다. 토큰을 그대로 두면 모델 가격 변동이 곧 의도치 않은 한도 변경이 됩니다. 한도는 'team_A: 일 100달러, 월 2,500달러'처럼 화폐 단위로 적어 둡니다. 80% 도달 알림과 95% 자동 throttle 같은 단계도 함께 답니다.

**관측·감사**가 마지막 박스입니다. 모든 호출은 trace에 다음 항목을 기록합니다. trace_id, tenant, team, user, model, prompt_len, response_len, latency_ms, cache_hit_type, cost_usd, status. 이 11개 칼럼이 운영의 표준 자료가 됩니다. 감사는 별도 흐름으로 쪼개 둡니다. 민감 산업의 경우 prompt와 response 전문을 별도 append-only 저장소에 7년 보관해야 할 수 있습니다. 일반 trace와 같은 저장소에 넣으면 비용이 폭발하니 cold tier로 분리합니다.

면접 트레이드오프는 셋입니다. 첫째, **gateway 단일 vs 사이드카**. 단일 gateway는 운영이 깔끔하지만 단일 장애점이 됩니다. peak QPS 200 정도는 multi-AZ 단일 cluster로 충분하고, 그 이상은 region별 독립 cluster를 둡니다. 둘째, **router의 자율성**. router가 자동으로 모델을 고르는 편의는 크지만, latency 회귀와 품질 회귀가 함께 발생할 수 있어 클라이언트가 등급을 명시할 수 있는 escape hatch를 항상 둡니다. 셋째, **캐시의 보수성**. semantic cache는 hit률과 정확도의 줄다리기입니다. 일반 챗봇은 공격적으로 키우고, 금융·의료는 prefix만 쓰고 semantic은 끕니다.

확장 시나리오 한 줄씩. 새 모델 추가는 Adapter 클래스와 routing 정책 한 줄로 끝납니다. 사고 시 panic switch로 한 공급자를 전체 차단하는 토글을 둡니다. 비용 폭주 알림은 quota 80% 도달 webhook과 함께 Slack에 자동 전송합니다. 멀티 region는 각 region에 독립 gateway를 두고 client SDK가 가장 가까운 region을 자동 선택합니다.

정리하면, LLM Gateway는 Auth·Quota·Cache·Router·Adapter·Fallback·Observability 일곱 박스를 한 줄로 잇는 single entry point입니다. provider abstraction과 fallback 사다리는 모델 사고를 흡수하고, prefix와 semantic 캐시는 비용과 latency를 함께 줄이며, quota는 사후 청구가 아니라 사전 차단으로 잡습니다.

다음 단원인 10.3.2에서는 이 인프라 위에서 가장 어려운 응용 사례 중 하나인 Coding Agent 플랫폼을 어떻게 설계하는지를 살펴봅니다.
