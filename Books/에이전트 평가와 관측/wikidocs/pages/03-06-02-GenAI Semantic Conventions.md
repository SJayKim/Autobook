# 3.6.2 GenAI Semantic Conventions

앞 단원에서 OpenTelemetry가 trace·metric·log를 한 표준에서 다루는 그릇이라는 점을 살폈습니다. 그릇이 같다고 해서 그 안에 담기는 데이터의 이름까지 자동으로 같아지지는 않습니다. 어떤 팀은 모델 이름을 model이라 적고 어떤 팀은 llm_model이라 적으면, 같은 collector를 거쳐도 도구마다 다르게 해석합니다. 이 단원은 이름의 약속, 즉 LLM 호출과 에이전트 단계를 표현할 때 어떤 속성과 메트릭을 어떤 이름으로 쓸지 정한 **GenAI semantic conventions**를 다룹니다.

먼저 단어부터 풀겠습니다. **Semantic conventions**, 한글로는 의미 규약이라 옮길 수 있는 이 표현은 OTel 안에서 데이터의 의미를 통일하기 위해 정한 속성 이름과 그 의미의 표준입니다. trace의 한 span에 'http.method'라고 적으면 모든 도구가 그것을 'HTTP 메서드'로 같이 이해하기 위한 약속입니다. GenAI semantic conventions는 이 약속을 LLM과 에이전트 영역에 맞춰 확장한 것으로, 'gen_ai.'로 시작하는 속성 이름들이 그 핵심을 이룹니다. 'gen_ai'는 generative AI의 줄임말로, 같은 LLM 호출이라도 어떤 도구가 받아 보든 같은 키 아래에서 같은 의미로 해석하도록 묶어 두기 위해 붙은 이름공간입니다.

이 표준에서 가장 먼저 자리잡는 속성은 **gen_ai.system**, **gen_ai.request.model**, 그리고 요청과 관련된 파라미터 묶음입니다. gen_ai.system은 호출하고 있는 모델 제공자가 누구인지를 적습니다. 'openai', 'anthropic', 'azure_openai'처럼 짧은 식별자가 들어갑니다. gen_ai.request.model은 그 안에서 고른 모델 이름을 적습니다. 'gpt-4o', 'claude-sonnet-4-5' 같은 값입니다. 요청 파라미터는 gen_ai.request.temperature, gen_ai.request.max_tokens, gen_ai.request.top_p처럼 요청에 실어 보낸 설정값이 각각 별도 속성으로 붙습니다. 이렇게 system과 model과 request 묶음만 표준 이름으로 정해 두면, span 한 개를 보고 어디에 어떤 모델로 어떤 설정으로 호출했는지를 누가 보든 같은 키에서 읽어 낼 수 있습니다.

이어서 LLM 호출의 핵심 내용물에 대한 속성이 들어갑니다. 입력으로 보낸 메시지는 **gen_ai.prompt**, 모델이 돌려준 응답은 **gen_ai.completion**이라는 이름공간 아래에 놓입니다. 한 호출에는 여러 메시지가 오갈 수 있으므로 gen_ai.prompt.0.role, gen_ai.prompt.0.content, gen_ai.prompt.1.role 같은 식으로 인덱스가 붙은 형태가 표준에서 권장됩니다. completion 쪽도 마찬가지로 gen_ai.completion.0.role, gen_ai.completion.0.content가 짝을 이룹니다. 이 부분은 prompt와 응답 본문을 그대로 담는 영역이라 데이터 양이 커지기 쉽고, 민감 정보가 들어가기도 합니다. 그래서 표준은 이 영역을 기록할지 말지를 SDK 차원에서 끄고 켤 수 있도록 권고합니다. 실무에서는 sampling 비율을 낮추거나 redaction을 거친 사본만 기록하는 방식이 흔히 쓰이고, 이 부분은 다음 단원에서 별도로 다룹니다.

에이전트가 도구를 부르는 호출도 표준이 별도로 다룹니다. **Tool call**에 해당하는 속성은 gen_ai.tool.name으로 도구 이름을, gen_ai.tool.call.id로 한 호출의 식별자를, gen_ai.tool.arguments와 gen_ai.tool.result 같은 키로 인자와 결과를 적도록 합니다. 한 단계에서 여러 도구를 호출했다면 호출마다 별도 자식 span으로 만들어 부모 span 아래에 매달고, 각 자식 span에 위 속성을 붙입니다. 이 구조 위에서 trajectory는 부모 span의 자식 트리를 따라가는 일이 됩니다. 이 부분은 표준이 어느 정도 자리잡았지만, 에이전트 특유의 multi-step 평가 점수나 정책 위반 같은 항목은 표준 영역 밖에 있어서 도구마다 자기 확장 속성으로 붙여 두는 것이 현실입니다.

토큰 사용량은 메트릭과 속성 두 곳에 모두 등장합니다. span 단위 속성으로는 gen_ai.usage.input_tokens, gen_ai.usage.output_tokens, gen_ai.usage.total_tokens가 한 호출의 토큰 수를 적고, 같은 정보를 시간 누적 메트릭 형태로 보낼 때는 gen_ai.client.token.usage 같은 카운터 형태가 정의됩니다. 비용 계산은 표준 자체가 직접 다루지 않습니다. 모델별 단가가 시간에 따라 바뀌기 때문에, 비용은 token usage를 받은 백엔드에서 곱셈을 거쳐 산출하는 방식이 일반적입니다. 지연도 별도 항목이 따로 있다기보다는 OTel의 기본 메트릭인 span 자체의 duration을 사용하는 쪽이 자연스럽습니다.

지금까지의 내용을 한 표로 정리하면 다음과 같습니다.

```
 영역             | 표준 속성 / 메트릭 예시
 ----------------+-----------------------------------------------
 모델 식별        | gen_ai.system, gen_ai.request.model
 요청 파라미터    | gen_ai.request.temperature / max_tokens / top_p
 입력 메시지      | gen_ai.prompt.{i}.role, gen_ai.prompt.{i}.content
 출력 메시지      | gen_ai.completion.{i}.role, gen_ai.completion.{i}.content
 도구 호출        | gen_ai.tool.name, gen_ai.tool.arguments, gen_ai.tool.result
 토큰 사용        | gen_ai.usage.input_tokens / output_tokens / total_tokens
 토큰 메트릭      | gen_ai.client.token.usage (counter)
```

이 표준이 의미를 가지려면 vendor가 자기 SDK 안에서 위 이름들에 자동으로 값을 채워 주어야 합니다. **Vendor별 매핑**의 현실은 도구마다 조금씩 다릅니다. OpenAI Python SDK 호출에 OTel 계측 라이브러리를 끼워 두면 위 속성 가운데 모델·토큰·메시지 항목은 자동으로 채워지는 경우가 많습니다. Anthropic SDK도 비슷한 자동 계측 라이브러리가 OTel 진영에서 만들어지고 있습니다. LangChain과 LangGraph는 자체 trace 모델 위에 OTel exporter 어댑터를 붙여 표준 속성을 함께 내보내는 작업이 진행되고 있고, LlamaIndex도 비슷한 방향입니다. Langfuse와 LangSmith는 OTLP endpoint로 들어오는 표준 속성을 자기 trace 모델로 받아들이는 쪽에서 매핑을 흡수합니다. 받는 쪽 도구가 표준 속성을 우선 해석하고, 표준에 없는 항목은 자기 확장 필드로 보존하는 방식이 일반적인 패턴입니다.

표준의 진행 상태를 사실 그대로 짚어 두는 일이 이 단원에서 중요합니다. **2025년 작업 항목**을 거칠게 분류하면 셋입니다. 첫째, 모델·토큰·prompt·completion에 해당하는 핵심 속성은 안정 단계에 가깝게 다듬어지고 있습니다. 둘째, 도구 호출과 multi-turn 대화의 표현은 안정화 직전에 와 있지만 일부 세부는 변동 가능 영역으로 남아 있습니다. 셋째, 에이전트의 multi-step trajectory, 평가 점수, 정책 위반 같은 영역은 표준화의 후순위 단계로, 도구별 확장 속성에 의존하는 비중이 큽니다. 따라서 새 코드에 OTel을 도입할 때는 핵심 속성에 대해서는 표준을 그대로 따르고, 표준에 없는 영역은 도구 확장 속성을 쓰되 나중에 표준 이름으로 옮길 수 있도록 한 곳에 묶어 두는 방식이 안전합니다.

이 표준이 코드에 어떻게 보이는지를 OTel Python SDK의 짧은 예로 보여 드리면 다음과 같습니다.

```python
from opentelemetry import trace
tracer = trace.get_tracer("agent")

with tracer.start_as_current_span("llm.call") as span:
    span.set_attribute("gen_ai.system", "anthropic")
    span.set_attribute("gen_ai.request.model", "claude-sonnet-4-5")
    span.set_attribute("gen_ai.request.temperature", 0.2)
    # ... 모델 호출 ...
    span.set_attribute("gen_ai.usage.input_tokens", 1325)
    span.set_attribute("gen_ai.usage.output_tokens", 412)
```

수동으로 적은 위 코드를 자동 계측 라이브러리가 대체로 대신해 줍니다. 직접 계측이 필요한 영역은 자체 도구 호출이나 자체 retrieval 단계처럼 SDK 바깥에 있는 부분이 됩니다.

정리하면, GenAI semantic conventions는 LLM과 에이전트 호출을 OTel trace 위에 표현하기 위해 'gen_ai.'로 시작하는 속성 이름과 메트릭을 정해 둔 약속입니다. 모델 식별과 요청 파라미터, prompt와 completion, tool call, token usage가 그 골격을 이루며, vendor마다 자동 계측 라이브러리와 endpoint 수신 매핑을 통해 이 골격을 채우거나 받아들이고 있습니다. 표준은 2025년에도 작업이 진행 중이라 핵심 영역과 미정 영역을 구분해서 다루는 자세가 필요합니다.

다음 단원인 3.6.3에서는 이 표준 위에서 OTel collector를 가운데에 두고 LangSmith·Langfuse·자체 ClickHouse 백엔드를 동시에 활용하면서 sampling과 PII redaction까지 함께 거는 무벤더 락인 설계를 정리하겠습니다.

이 단원을 마치면 gen_ai.system·gen_ai.request.model을 비롯한 모델 식별 속성, prompt와 completion 속성의 구조, tool call 표현 방식, token usage 속성과 메트릭, vendor별 매핑의 현실, 그리고 2025년 시점의 표준 진행 상태를 한 흐름으로 설명할 수 있습니다.
