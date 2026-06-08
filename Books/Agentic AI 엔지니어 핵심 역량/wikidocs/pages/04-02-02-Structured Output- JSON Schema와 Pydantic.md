# 4.2.2 Structured Output: JSON Schema와 Pydantic

LLM을 시스템에 연결하다 보면 응답을 자연어 문장으로 받기보다 정해진 필드에 정해진 타입으로 받고 싶은 경우가 많아집니다. 분류 결과는 enum, 추출된 항목은 리스트, 사용자 정보는 객체로 받아야 그다음 단계의 코드가 if 분기와 try 블록 없이 깔끔하게 처리할 수 있습니다. 이 요구를 모델 측에서 명시적으로 받아 주는 기능이 **Structured Output**입니다. 이 단원에서는 JSON mode와 Structured Output API의 차이, Pydantic으로 스키마를 정의하고 검증하는 방법, invalid output이 나왔을 때의 retry 정책, 그리고 스키마를 너무 조이면 잃는 자유도, 마지막으로 코드와 이미지 같이 JSON으로 담기 어려운 출력의 처리를 다룹니다.

이 기능이 등장하기 전에는 흔히 두 가지 방법을 썼습니다. 첫째는 프롬프트에 'JSON으로만 답하세요'라고 적고 결과를 `json.loads`로 파싱하는 방법입니다. 가장 간단하지만 모델이 코드 블록 표시자를 끼우거나 마지막 콤마를 빼먹는 사고가 종종 일어나 운영에서는 불안합니다. 둘째는 OpenAI의 **JSON mode**처럼 응답이 반드시 유효한 JSON임을 보장하는 모드를 켜는 방법입니다. 이 모드는 출력이 항상 파싱 가능한 JSON임은 보장하지만 어떤 키와 어떤 타입이어야 하는지까지는 강제하지 않습니다. 그래서 키 이름이 매번 바뀌거나 필수 필드가 빠지는 일이 여전히 벌어집니다.

최근의 **Structured Output API**는 이 한계를 넘어, 모델이 따라야 할 JSON Schema 자체를 사용자가 지정합니다. 모델은 토큰을 생성하는 단계에서 그 스키마에 어긋나는 토큰을 아예 만들지 못하도록 제약된 디코딩을 수행합니다. 그 결과 응답은 100%에 가까운 확률로 스키마에 부합하는 JSON으로 돌아옵니다. OpenAI에서는 `response_format`에 스키마를 직접 넣거나 Pydantic 모델을 넘기는 방식이고, Anthropic·Google도 비슷한 형태의 도구를 제공합니다.

스키마를 손으로 적기보다 파이썬 코드로 정의하는 편이 유지보수에 훨씬 좋습니다. 이때 가장 널리 쓰이는 도구가 **Pydantic**입니다. Pydantic은 클래스 정의로부터 JSON Schema를 자동 생성해 주고, 모델 응답을 검증하는 객체로 한 번에 변환해 줍니다.

```python
from pydantic import BaseModel, Field
from typing import Literal

class Ticket(BaseModel):
    title: str = Field(description="이슈 한 줄 제목")
    priority: Literal["low", "mid", "high"]
    tags: list[str] = Field(default_factory=list, max_length=5)
    summary: str

resp = client.chat.completions.parse(
    model="gpt-4o", response_format=Ticket,
    messages=[
        {"role": "system", "content": "버그 리포트를 티켓으로 정규화합니다."},
        {"role": "user", "content": "로그인 후 마이페이지에서 새로고침하면 500..."},
    ],
)
ticket: Ticket = resp.choices[0].message.parsed
```

`response_format=Ticket` 한 줄이 두 가지를 동시에 해 줍니다. 첫째, Pydantic이 만든 JSON Schema가 모델 호출 본문에 함께 실려 모델이 그 형식만 만들도록 강제합니다. 둘째, 응답이 돌아오면 `parsed` 필드에 이미 검증을 통과한 `Ticket` 객체가 들어 있어, 그다음 코드에서 type hint와 IDE 자동완성이 그대로 살아 있습니다. 자연어 응답에서 가장 흔하던 'JSON 파싱 실패 → 정규식으로 어떻게든 살리기'라는 코드가 한 줄로 사라집니다.

Pydantic의 도움을 받으면 검증 규칙도 같은 클래스 안에 함께 적을 수 있습니다.

```python
from pydantic import field_validator
class Ticket(BaseModel):
    title: str
    priority: Literal["low", "mid", "high"]
    tags: list[str] = []

    @field_validator("tags")
    @classmethod
    def tags_lower(cls, v):
        return [t.lower() for t in v]
```

이런 검증기는 모델이 스키마를 통과시킨 응답을 한 번 더 정규화하는 자리입니다. 모델이 'High'라고 쓴 우선순위를 'high'로 바꾸거나, 태그의 공백을 다듬는 일을 호출 코드 곳곳에 흩어 두지 않고 한 모델 안에 모을 수 있습니다.

스키마가 강제되더라도 **invalid output**이 생길 여지가 완전히 사라지지는 않습니다. 첫째, 일부 모델은 Structured Output을 지원하지 않거나 일부 키워드(예: `additionalProperties`, `oneOf`)에 제약이 있어 스키마가 거부될 수 있습니다. 둘째, 모델이 비즈니스 규칙을 위반한 경우가 있습니다. 예를 들어 priority가 enum 안에 있긴 하지만 사용자가 보낸 본문과 의미가 어긋나는 식입니다. 셋째, 도구 호출과 결합한 흐름에서 모델이 도구의 결과를 잘못 해석해 빈 객체를 돌려주는 경우입니다. 이런 사고는 스키마 단계에서는 잡히지 않으므로 별도의 retry 정책이 필요합니다.

retry 정책의 기본형은 다음과 같습니다.

```python
def call_with_retry(messages, schema, max_retries=2):
    for attempt in range(max_retries + 1):
        resp = client.chat.completions.parse(
            model="gpt-4o", response_format=schema, messages=messages,
        )
        obj = resp.choices[0].message.parsed
        try:
            validate_business_rules(obj)
            return obj
        except ValueError as e:
            messages = messages + [
                {"role": "assistant", "content": resp.choices[0].message.content or ""},
                {"role": "user", "content": f"다음 규칙을 위반했습니다: {e}. 같은 형식으로 다시 만들어 주세요."},
            ]
    raise RuntimeError("structured output retry exhausted")
```

핵심은 두 가지입니다. 첫째, 모델이 만든 직전 응답을 assistant 메시지로 다시 보여 주고, 둘째, 무엇이 왜 틀렸는지를 user 메시지로 명확히 알리는 것입니다. 모델은 자기 응답과 오류 메시지를 동시에 보면 어디를 어떻게 고쳐야 하는지를 비교적 정확히 찾아냅니다. 그러나 retry는 비용을 곱하므로 보통 2회 이내로 묶고, 그 안에 실패하면 사용자에게 우아하게 보고하거나 단순 자연어 응답으로 떨어뜨리는 fallback을 둡니다.

스키마를 강제하는 일은 자유도를 잃는 일이기도 합니다. 자유도와 강제 사이의 trade-off를 한 그림으로 보면 다음과 같습니다.

```
자유 자연어 ── JSON mode ── 작은 스키마 ── 큰 스키마 ── 모두 enum화
     ↑                                                              ↑
다양·자연·창의                                          예측·검증·재사용
     ↑                                                              ↑
실패 처리 비용 ↑                                  표현력·뉘앙스 손실 ↑
```

왼쪽 끝은 모델이 가진 표현력을 다 풀어 두지만 후속 코드가 흩어진 정규식과 if 문으로 무거워집니다. 오른쪽 끝은 코드가 깔끔해지지만, 사용자가 보낸 미묘한 입력이 enum 어디에도 깔끔하게 들어가지 않을 때 모델이 부적합한 칸에 억지로 끼워 넣는 사고가 생깁니다. 그래서 실무에서는 두 끝의 중간 어딘가에서 균형을 잡습니다. 분류 라벨처럼 합의된 카테고리는 enum으로 박고, 자유 서술이 필요한 본문은 string 한 칸을 열어 두는 식의 혼합 구조가 안정적입니다.

스키마 강제가 가장 자주 비싸지는 경우는 모델이 모든 항목에 대해 답을 만들도록 압박받을 때입니다. 예를 들어 '이메일에서 사람, 회사, 일정을 모두 뽑아 주세요'를 모두 required로 묶어 두면, 사람만 있고 회사가 없는 이메일에서 모델이 가짜 회사명을 만들어 내는 일이 생깁니다. 이 문제는 스키마 자체로는 막을 수 없고, 각 필드를 `Optional`로 두고 'unknown인 경우 null로 두세요'를 description에 명시하는 식으로 해결합니다. 모델은 빈 자리를 채워 넣는 압박에서 풀려나야 환각이 줄어듭니다.

마지막으로 JSON에 담기 어려운 출력은 어떻게 다룰지 보겠습니다. 코드, 이미지, 대용량 파일이 대표적입니다. 코드는 일정 길이를 넘으면 JSON 문자열 안에 그대로 박아 두는 것이 비효율적입니다. 큰 따옴표와 줄바꿈을 모두 escape해야 하기 때문입니다. 이때는 다음 두 패턴이 자주 쓰입니다. 첫째, 작은 메타데이터만 JSON으로 받고 본문은 별도의 markdown 코드 블록으로 받는 혼합 응답입니다. 둘째, 모델의 출력은 메타데이터만 JSON으로 받고, 실제 파일 내용은 모델이 도구를 호출해 별도의 저장소에 쓰게 하는 분리 패턴입니다.

```
[ 응답 형식 결정 ]
   ├─ JSON 안에 짧은 코드 (수십 줄): 그대로 string 필드
   ├─ 큰 코드/긴 글: JSON에 메타데이터 + 별도 markdown 블록
   └─ 이미지/파일: 도구 호출로 저장소에 쓰고 ID만 JSON에 반환
```

이 분기가 정해지면 모델 입장에서도 한 번에 어떤 출력을 만들어야 하는지가 분명해집니다. 같은 정보를 두 곳에 동시에 만들지 않게 되어 환각이 줄고, 후속 시스템이 받는 데이터가 일관됩니다.

운영에서는 스키마 자체도 4.1.1의 프롬프트와 같은 수준으로 버전 관리해야 합니다. 스키마의 필드가 하나만 바뀌어도 모델의 응답 분포가 흔들리고, 다운스트림 코드가 같이 깨질 수 있습니다. 가장 단순한 방법은 Pydantic 클래스를 `TicketV2`, `TicketV3`처럼 이름으로 버전을 매기고, 로그에 어떤 버전의 스키마가 쓰였는지를 함께 남기는 것입니다. 회귀 평가 시점에는 이 버전 식별자가 모델 식별자와 함께 비교의 축이 됩니다.

정리하면, Structured Output API는 JSON mode가 보장해 주지 못하던 키와 타입까지 강제해 응답을 거의 확실하게 스키마에 맞춥니다. Pydantic으로 스키마를 코드로 정의하면 모델 호출과 응답 검증과 후속 코드의 type hint가 한 자리에 모이고, 비즈니스 규칙을 위반한 응답은 직전 응답과 오류 메시지를 함께 보여 주는 retry로 두 번 안에 회복합니다. 스키마를 너무 조이면 환각이 늘 수 있어 unknown 자리를 Optional로 열어 두고, 코드와 이미지처럼 JSON에 담기 어려운 출력은 메타데이터와 본문을 분리하는 패턴으로 다루는 편이 안정적입니다.

다음 단원인 4.3.1에서는 이렇게 잡힌 입출력 구조 위에서 도메인 적응 문제, 즉 Fine-tuning과 RAG와 Prompting 중 무엇을 언제 골라야 하는지를 다룹니다.
