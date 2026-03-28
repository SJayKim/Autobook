---
source_id: 021
title: "LangSmith — Multi-turn Evaluation (대화 평가, Agent Trajectory, Thread-level Scoring)"
url: "https://blog.langchain.com/insights-agent-multiturn-evals-langsmith/"
type: blog
scraped_at: 2026-03-27
keywords: ["multi-turn evaluation", "online evaluation"]
content_length: 2640
---

# LangSmith — Multi-turn Evaluation (대화 평가, Agent Trajectory, Thread-level Scoring)

## Multi-turn Evals 개요

Multi-turn Evals는 단일 요청-응답 쌍이 아닌 **대화 전체(end-to-end interaction)**를 평가하는 LangSmith의 신규 기능이다. 에이전트가 사용자의 목표를 전체 상호작용에 걸쳐 달성했는지 측정한다.

> "Multi-turn Evals help you measure whether your agent accomplished the user's goal across an entire interaction."

## 평가 차원 (3가지 핵심 측정 지표)

### 1. Semantic Intent (의미적 의도)
사용자가 대화에서 실제로 달성하려 했던 것이 무엇인지 파악한다.

### 2. Semantic Outcomes (의미적 결과)
태스크가 성공적으로 완료됐는지, 실패했다면 어디서 막혔는지 판단한다.

### 3. Agent Trajectory (에이전트 궤적)
전체 상호작용 흐름 추적. 포함 사항:
- 도구 호출(tool calls) 내역
- 결정 패턴(decision-making patterns)
- 대화 경로(conversation path)

## 기술 아키텍처

### Threads 기반
LangSmith의 **threads** 개념 위에서 동작한다. 멀티턴 교환은 threads로 표현되며, 이것이 multi-turn eval의 실행 단위가 된다.

### Online Evaluation으로 동작
Multi-turn evals는 **online evaluations**으로 실행된다. 대화가 완료되면 자동으로 활성화된다.

### Idle Time 설정
Thread-level evaluator를 처음 구성할 때 **idle time**을 정의한다. 마지막 트레이스 이후 일정 시간이 지나면 해당 thread를 완료된 것으로 간주하고 평가를 시작한다.

```
idle_time = 300  # 마지막 메시지 후 5분 경과 시 평가 시작
```

## LLM-as-Judge 통합

Multi-turn eval은 **LLM-as-judge** 방법론을 사용한다. 사용자가 thread 전체를 평가하기 위한 점수 프롬프트(scoring prompt)를 정의한다.

평가 프롬프트에는 전체 대화 내용, 도구 호출 기록, 원하는 평가 기준이 포함된다.

## Single-turn vs Multi-turn 비교

| 항목 | Single-turn Eval | Multi-turn Eval |
|------|-----------------|----------------|
| 평가 단위 | 개별 run (단일 메시지) | Thread (대화 전체) |
| 실행 시점 | run 완료 즉시 | Thread idle 후 |
| 측정 지표 | 단일 응답 품질 | 목표 달성 여부, 궤적 |
| 적합한 경우 | 단순 Q&A, 분류 | 멀티스텝 에이전트 |

## 사용 가능 대상

모든 LangSmith 사용자가 사용 가능하다. 추가 Thread-level 기능(메트릭, 대시보드, 자동화, SDK 지원)은 후속 릴리스에 예정되어 있다.

## Changelog 출처

공식 발표: "Evaluate end-to-end agent interactions with Multi-turn Evals"
(https://changelog.langchain.com/announcements/evaluate-end-to-end-agent-interactions-with-multi-turn-evals)
