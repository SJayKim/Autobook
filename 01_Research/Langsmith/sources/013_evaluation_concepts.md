---
source_id: 013
title: "LangSmith Evaluation Concepts — Datasets, Evaluators, Experiments, Online/Offline"
url: "https://docs.langchain.com/langsmith/evaluation"
type: docs
scraped_at: 2026-03-27
keywords: ["datasets", "evaluators", "experiments", "online evaluation"]
content_length: 2840
---

# LangSmith Evaluation Concepts — Datasets, Evaluators, Experiments, Online/Offline

## 두 가지 평가 접근 방식

LangSmith는 두 가지 평가 접근 방식을 지원한다.

**Offline Evaluation (오프라인 평가)**: "Test before you ship" 철학으로, 개발 단계에서 큐레이션된 데이터셋 위에 평가를 실행하여 버전을 비교하고 회귀를 포착한다.

**Online Evaluation (온라인 평가)**: "Monitor in production" 철학으로, 프로덕션 실시간 트래픽에서 실제 사용자 상호작용을 평가하여 이슈를 감지한다.

## 핵심 개념

### Datasets
데이터셋은 평가의 기반이 되는 테스트 케이스 모음이다. 생성 경로는 다음과 같다:
- 수동 큐레이션된 테스트 케이스
- 과거 프로덕션 트레이스
- 합성 데이터 생성

각 예제(example)는 **input**과 **reference output** 쌍으로 구성된다. LangSmith 데이터셋은 버전 관리되어, 예제를 추가·수정·삭제할 때마다 새 버전이 생성된다.

### Evaluators
애플리케이션 성능을 점수화하는 함수들이다. 지원하는 평가 방법:
- **Human review**: 사람이 직접 검토
- **Code-based rules**: 결정론적 규칙 함수
- **LLM-as-judge**: LLM이 출력을 평가
- **Pairwise comparisons**: 두 실험 결과를 비교

### Experiments
특정 애플리케이션 버전을 데이터셋 위에서 평가한 결과물이다. 반복 횟수(repetitions), 동시성(concurrency), 캐싱 최적화를 설정할 수 있다.

### Runs & Threads
- **Runs**: 프로덕션 실행에서 생성되는 개별 트레이스
- **Threads**: 멀티턴 대화를 형성하는 관련 run들의 컬렉션으로, 온라인 평가의 단위가 된다

## 오프라인 평가 워크플로

1. 데이터셋 생성 (create dataset)
2. 평가 함수 정의 (define evaluators)
3. 실험 실행 (run experiment)
4. 결과 분석 (analyze results)

## 온라인 평가 워크플로

1. 배포 (deploy)
2. 평가 함수 구성 (configure evaluators)
3. 모니터링 (monitor)
4. 피드백 루프 수립 (establish feedback loop)

## Code Evaluators vs LLM Evaluators

**Code evaluators**는 결정론적 규칙 기반 함수로, 다음 확인에 적합하다:
- 챗봇 응답 구조가 비어 있지 않은지
- 생성된 코드가 컴파일되는지
- 분류 결과가 정확히 일치하는지

**LLM-as-judge evaluators**는 LLM을 사용하여 애플리케이션 출력을 점수화한다.

## 품질 평가 유형 (Heuristics)

- **응답 길이 / 지연 시간 / 특정 키워드**: quality heuristics
- **명확성, 일관성, 도움 정도, 톤**: reference-free LLM-as-judge
- **정확성, 사실 정확도, exact match**: reference-based evaluators
- **reference-based LLM-as-judge**: 레퍼런스 대비 비교 평가
