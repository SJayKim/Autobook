---
source_id: 048
title: "LangSmith SDK GitHub README — Integration Patterns"
url: "https://github.com/langchain-ai/langsmith-sdk/blob/main/python/README.md"
type: docs
scraped_at: 2026-03-27
keywords: ["SDK integration", "kw_018"]
content_length: 1640
---

# LangSmith SDK GitHub README — Integration Patterns

## @traceable 데코레이터

```python
from langsmith import traceable

@traceable
def my_function(text: str):
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": text}]
    )
```

데코레이터는 이 함수를 "자동 트레이스(auto-trace)"하며, 수동 계측 없이 입력과 출력을 캡처한다.

## wrap_openai 통합

```python
from openai import OpenAI
from langsmith import wrappers

client = wrappers.wrap_openai(OpenAI())
```

래핑 후 모든 OpenAI 호출은 자동으로 LangSmith에 기록된다. `@traceable`과 함께 사용하면 애플리케이션 로직의 중첩 트레이스가 구성된다.

## RunTree API

수동 트레이싱을 위한 저수준 API:

```python
from langsmith.run_trees import RunTree

parent_run = RunTree(
    name="My Chat Bot",
    run_type="chain",
    inputs={"text": "Summarize meetings."}
)
parent_run.post()
```

RunTree 핵심 속성:
- **name**: 컴포넌트 식별자
- **run_type**: "llm", "chain", "tool" 중 하나
- **inputs**: 컴포넌트 입력값
- **outputs** (optional): 반환값
- **error** (optional): 오류 메시지

`create_child()`로 자식 실행을 추가해 계층 트레이스를 구성하고, `post()`, `end()`, `patch()`로 라이프사이클을 관리한다.

## SDK 설정

필수 환경 변수:
- `LANGSMITH_API_KEY`: 인증 키
- `LANGSMITH_ENDPOINT`: API 엔드포인트 (기본값 또는 EU 리전)
- `LANGSMITH_PROJECT`: 프로젝트 이름 (기본값 "default")

설치: `pip install -U langsmith`

## TypeScript SDK

JavaScript/TypeScript 환경에서도 동일한 패턴을 제공한다. npm 패키지 `langsmith`로 설치하며, `traceable` 래퍼 함수와 `wrapOpenAI` 유틸리티를 지원한다.
