---
source_id: 047
title: "LangSmith Python SDK — @traceable, wrap_openai, RunTree API"
url: "https://pypi.org/project/langsmith/"
type: docs
scraped_at: 2026-03-27
keywords: ["SDK integration", "kw_018"]
content_length: 1820
---

# LangSmith Python SDK — @traceable, wrap_openai, RunTree API

## 설치

```bash
pip install -U langsmith
```

## @traceable 데코레이터

`@traceable` 데코레이터는 함수 실행을 자동으로 LangSmith에 기록한다. 데코레이터를 붙인 함수가 다른 instrumented 코드를 호출하면 중첩 트레이스(nested trace)가 자동 생성된다.

```python
from langsmith import traceable

@traceable
def my_function(text: str):
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": text}]
    )
```

데코레이터는 내부적으로 RunTree 객체를 생성하고 입력/출력을 캡처하며, 자식 실행에 컨텍스트를 전파하고, 오류 및 예외를 처리하며, 데이터를 배치로 LangSmith API에 전송한다.

## wrap_openai 통합

OpenAI 클라이언트를 래핑하면 모든 API 호출이 자동으로 LangSmith에 기록된다.

```python
from openai import OpenAI
from langsmith.wrappers import wrap_openai

client = wrap_openai(OpenAI())
# 이제 OpenAI 클라이언트를 평소처럼 사용하면 모든 호출이 LangSmith에 기록된다.
```

`@traceable`과 `wrap_openai`를 함께 사용하면 애플리케이션 로직의 중첩 트레이스가 생성된다.

## RunTree API (수동 트레이싱)

LangChain 없이 수동으로 트레이싱이 필요할 때 `RunTree` 객체를 사용한다.

```python
from langsmith.run_trees import RunTree

parent_run = RunTree(
    name="My Chat Bot",
    run_type="chain",
    inputs={"text": "Summarize meetings."}
)
parent_run.post()
```

`RunTree`의 필수 속성:
- **name** (str): 컴포넌트 식별자
- **run_type** (str): "llm", "chain", "tool" 중 하나
- **inputs** (dict): 컴포넌트 입력값
- **outputs** (dict, optional): 반환값
- **error** (str, optional): 오류 메시지

`create_child()`로 자식 실행을 생성해 계층적 트레이스를 구성하고, `post()`, `end()`, `patch()` 메서드로 데이터를 저장한다.

## 환경 변수 설정

```bash
export LANGSMITH_API_KEY="your-api-key"
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"  # 기본값
export LANGSMITH_PROJECT="my-project"  # 선택, 기본값 "default"
```

## 주요 사용 사례

- LLM 애플리케이션 트레이스 기록 및 디버깅
- 기존 실행으로부터 데이터셋 생성
- 캡처된 데이터에 대한 평가 실행
- LangChain 애플리케이션 또는 독립 Python 코드와 통합
