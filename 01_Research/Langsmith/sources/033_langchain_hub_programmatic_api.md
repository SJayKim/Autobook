---
source_id: 033
title: "LangSmith — 프롬프트 프로그래매틱 관리 (push_prompt, pull_prompt, 버전 참조, 캐싱)"
url: "https://docs.langchain.com/langsmith/manage-prompts-programmatically"
type: docs
scraped_at: 2026-03-27
keywords: ["LangChain Hub", "prompt versioning"]
content_length: 3280
---

# LangSmith — 프롬프트 프로그래매틱 관리 (push_prompt, pull_prompt, 버전 참조, 캐싱)

## 설치 및 환경 설정

```bash
# Python
pip install -U langsmith  # 버전 >= 0.1.99

# TypeScript
yarn add langsmith langchain
```

환경 변수: `LANGSMITH_API_KEY`를 LangSmith 대시보드에서 생성한 API 키로 설정한다.

## 프롬프트 푸시 (push_prompt)

### 기본 프롬프트 푸시

```python
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

client = Client()
prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
url = client.push_prompt("joke-generator", object=prompt)
```

### 모델과 함께 푸시 (RunnableSequence)

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4.1-mini")
chain = prompt | model
client.push_prompt("joke-generator-with-model", object=chain)
```

### 구조화된 출력 스키마 포함 푸시

```python
from langchain_core.prompts.structured import StructuredPrompt
from pydantic import BaseModel, Field

class ResponseSchema(BaseModel):
    positive_sentiment: bool = Field(description="긍정적 감정 여부")

prompt = StructuredPrompt.from_messages_and_schema(
    [("system", "대화 감정 평가"), ("human", "{conversation}")],
    schema=ResponseSchema.model_json_schema()
)
client.push_prompt("sentiment-evaluator", object=prompt)
```

## 프롬프트 풀 (pull_prompt)

### 기본 풀

```python
# 비공개(private) 프롬프트: 핸들 불필요
prompt = client.pull_prompt("joke-generator")

# 공개(public) 프롬프트: 저자의 핸들 필요
prompt = client.pull_prompt("efriis/my-first-prompt")
```

### 특정 버전 참조

```python
# 커밋 해시로 특정 버전 고정
prompt = client.pull_prompt("joke-generator:12344e88")

# 태그로 환경별 버전 참조
prompt = client.pull_prompt("joke-generator:prod")
```

### 모델 포함 풀

```python
chain = client.pull_prompt("joke-generator-with-model", include_model=True)
chain.invoke({"topic": "cats"})
```

## LangChain 없이 사용하기

### OpenAI 포맷 변환

```python
from langsmith.client import Client, convert_prompt_to_openai_format
from openai import OpenAI

client = Client()
prompt = client.pull_prompt("joke-generator")
prompt_value = prompt.invoke({"topic": "cats"})
openai_payload = convert_prompt_to_openai_format(prompt_value)
response = OpenAI().chat.completions.create(**openai_payload)
```

### Anthropic 포맷 변환

```python
from langsmith.client import Client, convert_prompt_to_anthropic_format
from anthropic import Anthropic

prompt = client.pull_prompt("joke-generator")
prompt_value = prompt.invoke({"topic": "cats"})
anthropic_payload = convert_prompt_to_anthropic_format(prompt_value)
response = Anthropic().messages.create(**anthropic_payload)
```

## 프롬프트 캐싱

풀된 프롬프트를 메모리에 캐시하여 지연 시간과 API 호출 횟수를 줄인다.

```python
from langsmith.prompt_cache import configure_global_prompt_cache

configure_global_prompt_cache(
    max_size=200,        # 최대 캐시 항목 수 (기본: 100)
    ttl_seconds=7200,    # 캐시 유효 시간 초 (기본: 300)
    refresh_interval_seconds=600
)
```

오프라인 모드 지원:

```python
# 온라인: 캐시 내보내기
prompt_cache_singleton.dump("prompts_cache.json")

# 오프라인: 캐시에서 로드 (API 호출 없음)
configure_global_prompt_cache(ttl_seconds=None)
prompt_cache_singleton.load("prompts_cache.json")
```

## 프롬프트 목록 및 관리

```python
# 전체 프롬프트 나열
prompts = client.list_prompts()

# 필터링 (키워드 + 공개/비공개)
prompts = client.list_prompts(query="joke", is_public=False)

# 프롬프트 삭제
client.delete_prompt("joke-generator")

# 좋아요
client.like_prompt("efriis/my-first-prompt")
```
