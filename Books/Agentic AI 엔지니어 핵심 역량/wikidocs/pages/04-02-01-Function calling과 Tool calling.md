# 4.2.1 Function calling과 Tool calling

LLM이 자기가 모르는 것을 알아내고, 자기가 할 수 없는 일을 시킬 수 있게 된 결정적 장치가 **tool calling**입니다. 모델은 텍스트만 만들 수 있다는 한계를 가지고 있지만, 사용자가 미리 정의해 둔 함수들의 명세를 함께 보여 주면 모델은 그 함수를 부르는 호출문을 텍스트로 만들어 냅니다. 시스템은 그 호출문을 받아 실제 함수를 실행하고 결과를 다시 모델에게 돌려줍니다. 이 한 번의 왕복이 모델을 단순한 문장 생성기에서 외부 시스템과 대화하는 에이전트로 바꿉니다. 이 단원에서는 tool 스키마를 설계하는 방법, description이 도구 선택 정확도에 미치는 영향, 병렬 호출 처리, 도구 결과를 다시 모델에게 주입하는 패턴, 그리고 도구 실패 처리까지를 정리합니다.

용어부터 정리합시다. OpenAI는 초기에 이 기능을 function calling이라고 불렀고, 이후 여러 도구를 묶는 개념까지 포괄하기 위해 **tool calling**으로 명칭을 넓혔습니다. Anthropic은 처음부터 tool use라는 이름을 썼습니다. 어느 쪽이든 본질은 같습니다. 모델에게 부를 수 있는 함수들의 스키마를 보여 주고, 모델이 그 함수 중 하나(또는 여럿)를 정해진 인자와 함께 호출하라는 신호를 텍스트가 아니라 구조화된 필드로 돌려받는 것입니다. 이 책에서는 두 용어를 같은 뜻으로 사용합니다.

tool 스키마는 보통 세 가지 필드로 구성됩니다. 함수의 이름인 **name**, 함수가 무엇을 하는지를 자연어로 설명하는 **description**, 그리고 함수가 받는 인자들의 JSON Schema인 **parameters**입니다. 가장 단순한 예를 보면 다음과 같습니다.

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "도시 이름을 받아 현재 기온과 날씨 상태를 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "도시 이름. 예: '서울', 'Tokyo'."},
                "unit": {"type": "string", "enum": ["c", "f"], "default": "c"},
            },
            "required": ["city"],
        },
    },
}]
```

세 필드는 그냥 문서가 아닙니다. 모델은 이 텍스트 자체를 보고 어느 도구를 부를지, 어떤 인자를 줄지를 결정합니다. 그래서 name은 의미가 분명한 영어 동사구로 짧게 쓰고, description은 '무엇을 하는가, 어떤 입력이 적절한가, 무엇을 하지 않는가'를 한두 문장 안에 담는 것이 좋습니다. parameters에는 가능하면 enum과 default를 적극적으로 두어 모델이 자유롭게 만든 문자열이 형식을 깨는 일을 막아야 합니다.

이 스키마를 함께 넣고 모델을 호출하면 응답은 평범한 텍스트가 아닌 tool_calls 필드가 채워진 객체로 돌아옵니다.

```python
resp = client.chat.completions.create(
    model="gpt-4o", tools=tools,
    messages=[{"role": "user", "content": "서울 날씨 어때?"}],
)
call = resp.choices[0].message.tool_calls[0]
# call.function.name == "get_weather"
# call.function.arguments == '{"city": "서울"}'
result = get_weather(**json.loads(call.function.arguments))
```

모델은 자기가 함수를 직접 실행하지 않습니다. 시스템이 그 호출문을 해석해 실제 함수를 부르고, 결과를 다음 호출의 메시지로 다시 넣어 줘야 모델이 그 결과를 알 수 있습니다. 이 왕복이 4.1.1에서 본 메시지 흐름의 한가운데에 끼는 구조입니다.

도구 선택 정확도를 끌어올리는 가장 큰 레버는 description의 품질입니다. 같은 도구라도 'get the weather'라는 무미건조한 설명을 'returns current temperature and conditions for a city; do not use for forecasts beyond today'처럼 적용 범위와 한계까지 명시한 설명으로 바꾸면, 모델이 다른 도구와 헷갈리는 빈도가 눈에 띄게 줄어듭니다. description은 일종의 라우팅 키워드 모음입니다. 사용자가 '내일 비 오나요?'라고 물었을 때 위 도구를 부르지 않게 만드는 것은 description 안의 'do not use for forecasts beyond today' 한 줄입니다.

이 효과를 가장 강하게 느끼는 시점은 도구 수가 늘었을 때입니다. 도구가 5개 정도일 때는 모델이 거의 헷갈리지 않지만, 30개가 넘어가면 description이 비슷한 도구들 사이에서 잘못된 선택이 늘어납니다. 이 문제를 다루는 패턴은 두 가지입니다. 첫째는 description에 '언제 이 도구를 쓴다, 언제 쓰지 않는다'를 명시적으로 적는 것입니다. 둘째는 모델 호출을 두 단계로 나눠, 첫 호출에서 도구 카테고리를 라우팅하고 두 번째 호출에서 그 카테고리 안의 도구만 노출하는 방식입니다.

**병렬 tool call**은 모델이 한 번의 응답에서 여러 도구를 동시에 호출할 수 있게 하는 기능입니다. '서울과 도쿄의 날씨를 비교해 줘'라는 요청에 모델은 `get_weather(city="서울")`과 `get_weather(city="도쿄")` 두 호출을 한 응답 안에 함께 담아 줄 수 있습니다. 시스템은 두 호출을 비동기로 동시에 실행하고, 결과를 두 개의 tool 메시지로 한꺼번에 다음 호출에 넣어 줍니다. 지연 시간이 큰 도구가 많은 시스템에서는 이 한 줄의 차이로 사용자 응답 시간이 절반 가까이 줄 수 있습니다.

```python
async def run_tools(tool_calls):
    coros = [exec_tool(c) for c in tool_calls]
    return await asyncio.gather(*coros)
```

병렬 호출이 가능하다고 항상 좋은 것은 아닙니다. 후속 도구가 앞 도구의 결과에 의존해야 하는 경우라면 직렬로 진행해야 합니다. 모델은 보통 의존 관계가 보이는 작업은 순차 호출을, 독립적인 조회 작업은 병렬 호출을 알아서 골라 줍니다. 다만 의존 관계가 모호한 작업에서는 description에 '결과에 다른 도구를 사용해야 한다면 한 번에 하나씩 호출하세요'와 같은 힌트를 추가하면 흐름이 안정됩니다.

도구가 실행되고 나면 그 결과를 모델에게 어떻게 보여 줄지가 다음 문제입니다. 가장 흔한 패턴은 도구의 반환값을 문자열로 직렬화해 role이 'tool'인 메시지로 넣는 것입니다. 이때 결과의 크기와 형식이 중요합니다. 결과가 너무 크면 4.1.3에서 본 컨텍스트 예산을 갉아먹고, 너무 자유로운 문자열이면 다음 응답이 흔들립니다. 안정적인 운영에서는 도구 결과도 작은 JSON으로 포맷을 통일합니다.

```python
messages.append({"role": "assistant", "tool_calls": tool_calls})
for call, result in zip(tool_calls, results):
    messages.append({
        "role": "tool",
        "tool_call_id": call.id,
        "content": json.dumps({"ok": True, "data": result}, ensure_ascii=False),
    })
next_resp = client.chat.completions.create(model="gpt-4o", tools=tools, messages=messages)
```

`tool_call_id`가 핵심입니다. 모델이 한 번에 여러 도구를 부른 경우, 어떤 결과가 어떤 호출에 대응하는지를 이 ID로 묶어 줘야 합니다. ID가 빠지면 모델은 두 결과를 헷갈려 잘못된 자리에 갖다 붙일 수 있습니다. 결과 본문은 가능하면 핵심 필드만 추려 보내고, 원본은 별도 저장소에 두고 ID로 참조하게 만드는 편이 컨텍스트 절약에 좋습니다.

이 모든 흐름을 한 그림으로 정리하면 다음과 같습니다.

```
[ user 입력 ]
     ↓
[ 모델 호출 (tools 함께 제공) ]
     ↓
[ tool_calls 응답 ] ─── 도구 0개: 곧장 응답 사용
     ↓ (도구 N개)
[ 도구 실행 (병렬 또는 직렬) ]
     ↓
[ tool 결과를 messages에 주입 ]
     ↓
[ 모델 재호출 ] → 다음 tool_calls 또는 최종 응답
```

이 루프가 0회 또는 여러 회 도는 모습이 LLM 호출과 에이전트를 나누는 분기점입니다. 한 번의 사용자 요청이 몇 회의 루프를 도는지에는 상한을 두는 편이 안전합니다. 무한히 도는 모델은 비용을 빠르게 태우고, 같은 도구를 반복해서 부르는 흐름을 만들 수 있습니다.

마지막으로 도구 실패 처리입니다. 도구는 외부 시스템에 닿아 있는 만큼 실패 모드가 다양합니다. 인자 검증 실패, 외부 API의 4xx/5xx, 타임아웃, 권한 부족, 그리고 모델이 잘못된 JSON을 만든 경우까지 모두 다른 경로의 실패입니다. 이 모두를 모델에게 똑같이 '에러'라고 돌려주면 모델은 같은 호출을 그대로 다시 시도하기 쉽습니다. 그래서 도구 결과 메시지의 형식을 다음과 같이 표준화하는 패턴이 자주 쓰입니다.

```json
{ "ok": false, "error_type": "invalid_arg",
  "message": "city must be a non-empty string",
  "retryable": false }
```

`error_type`과 `retryable`을 함께 주면 모델은 단순 재시도가 통하는 일시 오류와, 인자를 고쳐야 통하는 영구 오류를 구분해 행동합니다. retryable이 false인 오류에서는 모델이 같은 인자로 재호출하지 않고 사용자에게 다시 묻거나 다른 도구를 시도합니다. 시스템 쪽에서도 한 번의 사용자 요청에서 같은 도구가 정확히 같은 인자로 두 번 이상 호출되면 호출을 차단하고 합성된 오류를 돌려주는 가드를 두면, 무한 루프와 비용 폭주를 함께 막을 수 있습니다.

정리하면, tool calling은 모델에게 함수 스키마를 보여 주고 호출문을 구조화된 필드로 받아 다시 실행 결과를 주입하는 왕복 구조이며, name·description·parameters 세 필드가 도구 선택의 첫 번째 레버입니다. 도구가 많아질수록 description은 적용 범위와 한계까지 적어야 하며, 병렬 호출은 독립 조회에만 적용하고 도구 결과는 작은 표준 JSON으로 모델에게 돌려줘야 안정적입니다. 실패는 인자 오류와 일시 오류를 구분해 retryable 플래그로 모델에게 알려야 같은 실수를 반복하지 않게 만들 수 있습니다.

다음 단원인 4.2.2에서는 이 흐름의 다른 쪽 끝, 모델의 출력 자체를 JSON Schema와 Pydantic으로 강제하는 구조화 출력을 다룹니다.
