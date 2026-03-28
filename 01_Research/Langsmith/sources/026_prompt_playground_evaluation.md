---
source_id: 026
title: "LangSmith — Prompt Playground에서 평가 실행 (Run Evaluation from Playground)"
url: "https://docs.langchain.com/langsmith/run-evaluation-from-prompt-playground"
type: docs
scraped_at: 2026-03-27
keywords: ["prompt playground", "prompt versioning"]
content_length: 1420
---

# LangSmith — Prompt Playground에서 평가 실행 (Run Evaluation from Playground)

## 개요

LangSmith Playground는 프롬프트 편집과 평가를 단일 인터페이스에서 수행할 수 있는 통합 환경이다. 코드 없이 데이터셋 기반 실험을 실행할 수 있으며, 평가자(Evaluator)를 직접 붙여 결과를 측정한다.

## 데이터셋 기반 실험 실행

- 기존 저장된 프롬프트를 선택하거나 새로 생성하여 실험에 추가한다.
- 데이터셋의 입력 키(input key)가 프롬프트 변수(variable)와 일치해야 한다. 최대 15개 변수를 지원한다.
- 데이터셋의 모든 예시(example)에 대해 프롬프트를 실행하면, 데이터셋 상세 페이지에 실험(experiment) 항목이 생성된다.

## Evaluator 추가

- `+Evaluator` 버튼을 클릭하여 LLM-as-a-judge 또는 맞춤형 코드 평가자(custom code evaluator)를 Playground에 추가한다.
- 평가자는 각 예시의 출력에 대해 자동으로 점수를 매긴다.
- 인라인으로 데이터셋을 생성하거나 기존 데이터셋에 예시를 추가하는 작업도 Playground를 벗어나지 않고 수행할 수 있다.

## 프롬프트 최적화 (Polly)

- Polly 도구를 활용하면 평가 실행 전에 프롬프트를 자동 최적화할 수 있다.

## 프롬프트 커밋 연동

- 실험 결과가 만족스러우면 Playground에서 직접 프롬프트 허브(Hub)에 커밋하여 나중에 코드에서 해시로 참조할 수 있다.
- 커밋된 프롬프트는 `client.pull_prompt("prompt-name:commit_hash")` 형식으로 특정 버전을 불러올 수 있다.
