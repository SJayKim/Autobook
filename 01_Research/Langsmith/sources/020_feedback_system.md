---
source_id: 020
title: "LangSmith — Feedback 시스템 (Run Feedback, User Feedback, Thumbs Up/Down, Score/Key)"
url: "https://docs.langchain.com/langsmith/agent-server-feedback"
type: docs
scraped_at: 2026-03-27
keywords: ["feedback"]
content_length: 2880
---

# LangSmith — Feedback 시스템 (Run Feedback, User Feedback, Thumbs Up/Down, Score/Key)

## Feedback 개요

LangSmith feedback 시스템은 run에 품질 신호를 붙이는 메커니즘이다. 자동 evaluator 점수, 인간 어노테이터 평가, 최종 사용자 반응을 통합하는 단일 인터페이스다.

## Feedback 데이터 모델

Feedback은 유연한 데이터 모델을 사용한다:
- **`run_id`** 또는 **`trace_id`**: 연결할 run 식별자
- **`key`**: 피드백 이름 (예: `"user-score"`, `"helpfulness"`)
- **`score`**: 수치 값
- **`value`**: 이진 지시자 (optional)
- **`comment`**: 텍스트 설명 (optional)
- **`correction`**: 구조화된 수정 사항 (optional)

## Python SDK로 Feedback 생성

```python
from langsmith import Client

client = Client()

# 기본 피드백 생성
client.create_feedback(
    run_id=run_id,
    key="user-score",
    score=1.0,
    comment="Very helpful response"
)

# 수정 사항 포함
client.create_feedback(
    run_id=run_id,
    key="correctness",
    score=0,
    correction={"expected": "Paris", "actual": "London"}
)
```

## Thumbs Up/Down 패턴

사용자 thumbs up/down을 모델링하는 두 가지 방식:

**방식 1 — 별도 키:**
```python
# 좋아요
client.create_feedback(run_id, key="user_liked", score=1)
# 싫어요
client.create_feedback(run_id, key="user_disliked", score=1)
```

**방식 2 — 단일 키 (권장):**
```python
# 좋아요: score=1
client.create_feedback(run_id, key="user_score", score=1)
# 싫어요: score=0 (또는 score=-1)
client.create_feedback(run_id, key="user_score", score=0)
```

피드백 키는 "user-score"이며 thumbs up은 1, thumbs down은 0으로 매핑하는 것이 관행이다.

## Feedback Config (타입 설정)

`feedback_config`로 피드백 해석 방식을 지정한다:

```python
from langsmith.schemas import FeedbackConfig

# Continuous (연속형)
config = FeedbackConfig(type="continuous", min=0, max=1)

# Categorical (범주형)
config = FeedbackConfig(type="categorical", categories=["good", "ok", "bad"])

# Freeform (자유형)
config = FeedbackConfig(type="freeform")
```

## Pre-signed URL 방식 (Agent Server)

서버 사이드에서 run을 생성할 때 `feedback_keys`를 포함하면, 응답에 pre-signed URL이 포함된다. 프론트엔드에서 이 URL로 POST/GET 요청을 전송하여 피드백을 제출한다.

```python
# feedback_keys를 포함한 streaming run 생성
response = client.runs.stream(
    thread_id=thread_id,
    assistant_id=assistant_id,
    input={"messages": [...]},
    feedback_keys=["user-score", "helpfulness"]
)

# 응답에서 feedback URLs 추출
for event in response:
    if event.event == "feedback":
        feedback_urls = event.data  # pre-signed URL들
```

프론트엔드 워크플로:
1. 서버에서 run 생성 + feedback URLs 반환
2. UI에서 thumbs 버튼 렌더링
3. 사용자 클릭 시 해당 URL로 POST 요청 전송

## Inline Feedback (UI에서 직접)

LangSmith UI의 트레이스 뷰에서 직접 run에 피드백을 붙일 수 있다. Annotation queue 없이도 즉시 피드백 추가 가능하다.
