# 5.1.2 LangChain 핵심 구조

5.1.1에서 LLM 오케스트레이션이 왜 필요한지, 그리고 단순 API 호출만으로는 복잡한 LLM 애플리케이션을 구축하기 어렵다는 점을 살펴보았습니다. 프롬프트를 구성하고, 모델을 호출하고, 응답을 파싱하고, 그 결과를 다음 단계로 넘기는 일련의 과정을 매번 직접 작성하면 코드가 빠르게 복잡해집니다. LangChain은 바로 이 문제를 해결하기 위해 만들어진 오케스트레이션 프레임워크입니다. 이 단원에서는 LangChain이 제공하는 핵심 추상화 계층을 하나씩 살펴보고, 이 추상화들을 조합하여 하나의 체인을 구성하는 방법을 다룹니다.

LangChain을 이해하려면, 먼저 이 프레임워크가 어떤 구조로 이루어져 있는지 전체 그림을 파악하는 것이 좋습니다. LangChain은 LLM 애플리케이션을 만들 때 반복적으로 필요한 작업들을 각각 독립된 구성요소로 분리합니다. 프롬프트를 만드는 일, 모델을 호출하는 일, 모델의 출력을 원하는 형태로 변환하는 일이 각각 별도의 객체로 존재합니다. 이렇게 분리된 구성요소를 순서대로 연결하면, 입력이 들어왔을 때 프롬프트 생성부터 최종 출력까지 자동으로 흘러가는 파이프라인이 만들어집니다. LangChain은 이 파이프라인을 **체인(Chain)**이라고 부릅니다.

LangChain의 핵심 구성요소는 크게 네 가지입니다. 모델을 감싸는 **LLM/ChatModel**, 프롬프트를 만드는 **PromptTemplate**, 출력을 변환하는 **OutputParser**, 그리고 이 세 요소를 하나로 엮는 **LCEL(LangChain Expression Language)**입니다. 아래 다이어그램은 이 구성요소들이 어떻게 연결되는지를 보여줍니다.

```
LangChain 체인의 기본 흐름

사용자 입력 (변수)
     |
     v
+------------------+
| PromptTemplate   |  변수를 받아 완성된 프롬프트 생성
+------------------+
     |
     v
+------------------+
| LLM / ChatModel  |  프롬프트를 모델에 전달하고 응답 수신
+------------------+
     |
     v
+------------------+
| OutputParser     |  모델 응답을 원하는 형식으로 변환
+------------------+
     |
     v
최종 출력 (문자열, 딕셔너리, 객체 등)
```

이 구조가 LangChain의 기본 뼈대입니다. 이제 각 구성요소를 하나씩 살펴보겠습니다.

LangChain에서 모델을 다루는 방식부터 시작합니다. LLM 제공자마다 API 형태가 다릅니다. OpenAI의 GPT를 호출하는 코드와 Anthropic의 Claude를 호출하는 코드는 요청 형식, 인증 방식, 응답 구조가 모두 다릅니다. 모델을 바꿀 때마다 호출 코드 전체를 수정해야 한다면, 프레임워크를 쓰는 의미가 줄어듭니다. LangChain은 이 문제를 해결하기 위해 모든 모델을 동일한 인터페이스로 감쌉니다.

LangChain은 모델 추상화를 두 가지로 나눕니다. **LLM**과 **ChatModel**입니다. 이 둘은 모델을 호출한다는 점에서 같지만, 입력과 출력의 형태가 다릅니다.

**LLM** 추상화는 하나의 문자열을 입력받아 하나의 문자열을 반환합니다. "다음 문장을 완성하시오: 오늘 날씨가"라는 텍스트를 그대로 모델에 전달하고, 모델이 생성한 텍스트를 문자열로 돌려받는 것입니다. 이 방식은 텍스트 완성(text completion)을 제공하는 모델에 적합합니다.

**ChatModel** 추상화는 메시지 목록을 입력받아 메시지를 반환합니다. 여기서 메시지란 역할(role)과 내용(content)이 쌍을 이루는 구조입니다. 역할에는 시스템(system), 사용자(human), 어시스턴트(ai) 등이 있습니다. 시스템 메시지는 모델의 행동 지침을 설정하고, 사용자 메시지는 실제 질문이나 요청을 담으며, 어시스턴트 메시지는 모델의 이전 응답을 나타냅니다. 최근 출시되는 대부분의 모델은 이 메시지 기반 인터페이스를 사용하므로, 실무에서는 ChatModel을 훨씬 자주 사용합니다.

```python
from langchain_openai import ChatOpenAI

# ChatModel 생성: 모델 이름과 설정을 지정합니다.
model = ChatOpenAI(model="gpt-4o", temperature=0)

# invoke 메서드로 호출합니다.
# 문자열을 전달하면 내부에서 HumanMessage로 변환됩니다.
response = model.invoke("LLMOps란 무엇인가요?")
print(response.content)
```

위 코드에서 ChatOpenAI는 OpenAI의 채팅 모델을 감싸는 클래스입니다. model 매개변수에 사용할 모델 이름을 지정하고, temperature는 응답의 무작위성을 조절하는 값입니다. 0에 가까울수록 동일한 입력에 대해 비슷한 응답을 반환합니다. invoke 메서드는 입력을 받아 모델을 호출하고 응답을 반환합니다. 반환된 객체의 content 속성에 모델이 생성한 텍스트가 들어 있습니다.

모델을 Anthropic의 Claude로 바꾸고 싶다면, ChatOpenAI 대신 ChatAnthropic을 사용하면 됩니다. 나머지 코드는 동일하게 유지할 수 있습니다. 이것이 추상화의 핵심 이점입니다. 모델 제공자가 달라져도 호출하는 쪽의 코드를 변경할 필요가 없습니다.

다음으로, 프롬프트를 만드는 구성요소를 살펴봅니다. 모델에 전달할 프롬프트를 매번 문자열 연결로 만들면 여러 가지 문제가 생깁니다. 프롬프트의 구조가 코드 곳곳에 흩어지고, 동일한 프롬프트 패턴을 여러 곳에서 반복 작성하게 되며, 프롬프트만 별도로 관리하거나 교체하기가 어렵습니다. LangChain의 **PromptTemplate**은 프롬프트의 구조를 미리 정의해 두고, 실행 시점에 변수만 채워 넣는 방식으로 이 문제를 해결합니다.

**PromptTemplate**은 단일 문자열 프롬프트를 위한 템플릿입니다. 중괄호로 감싼 변수 자리(placeholder)를 정의해 두면, 나중에 실제 값을 넣어 완성된 프롬프트를 만들 수 있습니다.

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template(
    "다음 주제에 대해 3줄로 요약해 주세요: {topic}"
)

# 변수를 채워 프롬프트를 완성합니다.
prompt = template.invoke({"topic": "LLMOps"})
print(prompt.text)
# 출력: 다음 주제에 대해 3줄로 요약해 주세요: LLMOps
```

위 코드에서 {topic}이 변수 자리입니다. invoke 메서드에 딕셔너리를 전달하면 {topic} 위치에 "LLMOps"가 삽입되어 완성된 프롬프트가 만들어집니다.

ChatModel과 함께 쓸 때는 **ChatPromptTemplate**을 사용합니다. ChatPromptTemplate은 메시지 목록 형태의 프롬프트를 생성합니다. 시스템 메시지, 사용자 메시지 등 역할별로 템플릿을 구성할 수 있습니다.

```python
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "당신은 {role} 전문가입니다. 간결하게 답변하세요."),
    ("human", "{question}")
])

# 변수를 채워 메시지 목록을 생성합니다.
messages = template.invoke({
    "role": "LLMOps",
    "question": "프롬프트 관리가 왜 중요한가요?"
})
```

위 코드에서 from_messages 메서드는 튜플의 리스트를 받습니다. 각 튜플의 첫 번째 요소는 역할("system", "human")이고, 두 번째 요소는 해당 역할의 메시지 템플릿입니다. invoke를 호출하면 변수가 채워진 메시지 목록이 만들어집니다. 이 메시지 목록을 그대로 ChatModel에 전달할 수 있습니다. PromptTemplate은 단일 문자열을 만들고, ChatPromptTemplate은 메시지 목록을 만든다는 차이를 기억하면 됩니다.

모델이 응답을 반환하면, 그 응답을 원하는 형태로 변환해야 하는 경우가 많습니다. 예를 들어, 모델에게 JSON 형식으로 답하라고 요청했더라도, 실제 응답은 JSON 앞뒤에 설명 문구가 붙은 문자열일 수 있습니다. 또는 여러 항목을 쉼표로 구분한 텍스트를 파이썬 리스트로 변환하고 싶을 수 있습니다. 이런 변환 작업을 담당하는 것이 **OutputParser**입니다.

OutputParser는 모델의 원시 출력을 받아 프로그램에서 바로 사용할 수 있는 구조로 변환합니다. LangChain은 용도에 따라 여러 종류의 OutputParser를 제공합니다. 가장 기본적인 것은 **StrOutputParser**로, 모델 응답 객체에서 텍스트 부분만 추출하여 문자열로 반환합니다. **JsonOutputParser**는 모델 응답에서 JSON을 추출하여 파이썬 딕셔너리로 변환합니다. **CommaSeparatedListOutputParser**는 쉼표로 구분된 텍스트를 리스트로 변환합니다.

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()

# ChatModel의 응답 객체에서 텍스트만 추출합니다.
result = parser.invoke(response)
# result는 순수 문자열입니다.
```

StrOutputParser가 하는 일은 단순합니다. ChatModel의 응답 객체(AIMessage)에서 content 속성 값을 꺼내 문자열로 반환하는 것입니다. 단순해 보이지만, 뒤에서 설명할 LCEL 체인 안에서 구성요소를 일관되게 연결하려면 이 파서가 필요합니다. 모델 응답이 항상 AIMessage 객체로 나오기 때문에, 다음 단계에서 순수 문자열이 필요하다면 StrOutputParser를 거쳐야 합니다.

이제 가장 중요한 부분에 도달했습니다. 앞에서 살펴본 PromptTemplate, ChatModel, OutputParser는 각각 독립된 구성요소입니다. 이것들을 하나의 파이프라인으로 연결하는 방법이 **LCEL(LangChain Expression Language)**입니다.

LCEL이 왜 필요한지부터 생각해 보겠습니다. LCEL 없이 세 구성요소를 연결하려면, 프롬프트 템플릿의 출력을 변수에 저장하고, 그 변수를 모델의 invoke에 전달하고, 모델의 출력을 다시 변수에 저장하고, 그 변수를 파서의 invoke에 전달해야 합니다. 단계가 세 개일 때는 괜찮아 보이지만, 다섯 개, 열 개로 늘어나면 중간 변수가 많아지고 흐름을 파악하기 어려워집니다. LCEL은 파이프 연산자 `|`를 사용하여 구성요소를 순서대로 연결합니다. 앞 구성요소의 출력이 뒤 구성요소의 입력으로 자동 전달됩니다.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 각 구성요소를 정의합니다.
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 기술 문서 작성 전문가입니다."),
    ("human", "{topic}에 대해 한 문단으로 설명해 주세요.")
])

model = ChatOpenAI(model="gpt-4o", temperature=0)

parser = StrOutputParser()

# LCEL로 체인을 구성합니다.
chain = prompt | model | parser
```

위 코드에서 `prompt | model | parser`가 LCEL 표현식입니다. 파이프 연산자 `|`가 세 구성요소를 순서대로 연결하여 하나의 체인을 만듭니다. 이 체인은 하나의 실행 가능한 객체(Runnable)가 됩니다.

체인을 실행하는 방법은 구성요소를 개별로 실행할 때와 동일합니다. invoke 메서드에 입력값을 전달하면 됩니다.

```python
# 체인을 실행합니다.
result = chain.invoke({"topic": "LLMOps"})
print(result)
# 출력: LLMOps에 대한 한 문단 설명 (순수 문자열)
```

invoke를 호출하면 내부에서 다음 과정이 순서대로 일어납니다. 먼저, prompt가 {"topic": "LLMOps"} 딕셔너리를 받아 메시지 목록을 생성합니다. 다음으로, model이 그 메시지 목록을 받아 LLM API를 호출하고 AIMessage 객체를 반환합니다. 마지막으로, parser가 AIMessage에서 텍스트를 추출하여 문자열을 반환합니다. 개발자가 중간 변수를 직접 관리할 필요가 없습니다.

```
chain.invoke({"topic": "LLMOps"}) 실행 흐름

{"topic": "LLMOps"}
        |
        v
  [ChatPromptTemplate]
        |
   메시지 목록 생성
        |
        v
    [ChatOpenAI]
        |
   LLM API 호출, AIMessage 반환
        |
        v
  [StrOutputParser]
        |
   content 추출, 문자열 반환
        |
        v
   최종 결과 (문자열)
```

LCEL의 파이프 연산자는 파이썬의 `__or__` 매직 메서드를 활용한 것입니다. LangChain의 모든 구성요소는 **Runnable**이라는 공통 인터페이스를 구현합니다. Runnable은 invoke(단건 실행), batch(여러 입력 일괄 실행), stream(토큰 단위 스트리밍) 메서드를 갖고 있으며, 파이프 연산자로 다른 Runnable과 연결할 수 있습니다. 이 통일된 인터페이스 덕분에 어떤 구성요소든 자유롭게 조합할 수 있습니다.

LCEL의 이점은 단순히 코드가 짧아지는 것에 그치지 않습니다. 체인을 구성하면 **스트리밍**과 **배치 실행**이 자동으로 지원됩니다. invoke 대신 stream을 호출하면, 모델이 토큰을 생성할 때마다 그 토큰이 체인을 통해 즉시 전달됩니다. batch를 호출하면, 여러 입력을 동시에 처리하여 처리량을 높일 수 있습니다. 개별 구성요소를 직접 연결했다면 스트리밍이나 배치 처리를 별도로 구현해야 하지만, LCEL 체인에서는 추가 코드 없이 사용할 수 있습니다.

```python
# 스트리밍: 토큰이 생성될 때마다 출력합니다.
for chunk in chain.stream({"topic": "LLMOps"}):
    print(chunk, end="", flush=True)

# 배치: 여러 입력을 동시에 처리합니다.
results = chain.batch([
    {"topic": "LLMOps"},
    {"topic": "RAG"},
    {"topic": "프롬프트 엔지니어링"}
])
```

stream 메서드는 제너레이터를 반환하며, 모델이 토큰을 하나 생성할 때마다 해당 토큰 문자열이 yield됩니다. batch 메서드는 리스트를 입력받아 각 입력에 대한 결과를 리스트로 반환합니다.

지금까지 살펴본 체인은 프롬프트, 모델, 파서 세 개를 일직선으로 연결한 가장 단순한 형태입니다. 실제 애플리케이션에서는 여러 체인을 순차적으로 연결하거나, 조건에 따라 다른 경로로 분기하거나, 이전 대화 내용을 기억하는 메모리를 추가하는 등 더 복잡한 구성이 필요합니다. 이런 고급 구성 패턴은 5.1.4에서 다룹니다.

체인의 구성과 실행 과정을 전체적으로 정리하겠습니다. LangChain에서 체인을 만드는 과정은 세 단계로 나뉩니다. 첫째, 필요한 구성요소를 각각 생성합니다. 프롬프트 템플릿, 모델, 파서를 용도에 맞게 설정합니다. 둘째, LCEL의 파이프 연산자로 구성요소를 연결하여 체인을 만듭니다. 셋째, 체인의 invoke, stream, batch 메서드를 호출하여 실행합니다. 입력 데이터는 첫 번째 구성요소에 들어가고, 각 구성요소를 순서대로 통과하며, 마지막 구성요소의 출력이 최종 결과가 됩니다.

```
체인의 구성과 실행 3단계

1. 구성요소 생성
   +------------------+  +------------------+  +------------------+
   | PromptTemplate   |  | ChatModel        |  | OutputParser     |
   | (템플릿 정의)     |  | (모델, 설정 지정) |  | (출력 형식 지정)  |
   +------------------+  +------------------+  +------------------+

2. LCEL로 연결
   PromptTemplate  -->|-->  ChatModel  -->|-->  OutputParser
                (파이프 연산자로 체인 생성)

3. 실행
   chain.invoke({"변수": "값"})  --> 최종 결과
   chain.stream({"변수": "값"})  --> 토큰 단위 스트리밍
   chain.batch([{...}, {...}])   --> 일괄 처리 결과 리스트
```

정리하면, LangChain은 LLM 애플리케이션의 반복적인 작업을 독립된 구성요소로 분리하고, 이 구성요소들을 LCEL이라는 표현식 언어로 연결하여 체인을 구성하는 프레임워크입니다. 모델 추상화(LLM/ChatModel)는 서로 다른 모델 제공자를 동일한 인터페이스로 다룰 수 있게 하고, PromptTemplate과 ChatPromptTemplate은 프롬프트의 구조를 재사용 가능한 형태로 관리하며, OutputParser는 모델 응답을 프로그램이 사용할 수 있는 구조로 변환합니다. LCEL의 파이프 연산자는 이 구성요소들을 일직선으로 연결하여 invoke, stream, batch를 자동으로 지원하는 실행 가능한 체인을 만듭니다.

다음 단원인 5.1.3에서는 LlamaIndex 핵심 구조를 다룹니다. LlamaIndex가 문서와 인덱스를 중심으로 데이터 검색에 특화된 추상화를 어떻게 제공하는지, 그리고 LangChain과 어떤 점에서 다른지를 살펴봅니다.

이 단원을 마치면 LangChain의 핵심 추상화인 LLM/ChatModel, PromptTemplate, OutputParser, LCEL의 역할을 설명할 수 있고, 이 구성요소들을 조합하여 기본 체인을 구성할 수 있습니다.

<!-- INCOMPLETE: LangChain 아키텍처 개요, LLM과 ChatModel 추상화, PromptTemplate과 ChatPromptTemplate, OutputParser, LCEL (LangChain Expression Language), Chain 구성과 실행 -->
