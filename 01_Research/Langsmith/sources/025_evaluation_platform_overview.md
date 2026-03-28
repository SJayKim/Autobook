---
source_id: 025
title: "LangSmith Evaluation Platform — 전체 기능 개요 (Agent Trajectory, Multi-modal, Human Review)"
url: "https://www.langchain.com/langsmith/evaluation"
type: web
scraped_at: 2026-03-27
keywords: ["evaluators", "datasets", "annotation queues", "multi-turn evaluation", "online evaluation"]
content_length: 2480
---

# LangSmith Evaluation Platform — 전체 기능 개요 (Agent Trajectory, Multi-modal, Human Review)

## 플랫폼 평가 유형 전체 목록

LangSmith 평가 플랫폼은 다음 평가 방법을 통합 지원한다:

### Offline Evaluation (개발 단계)
- 큐레이션된 데이터셋에 대한 평가 실행
- 버전 비교 및 회귀 감지

### Online Evaluation (프로덕션)
- 에이전트와의 사용자 상호작용을 실시간으로 점수화
- 성능 및 품질 모니터링

## Evaluator 지원 유형

| 유형 | 설명 |
|------|------|
| Human evaluation | Annotation queue를 통한 인간 검토 |
| Heuristic checks | 출력 유효성 검사, 코드 컴파일 확인 |
| LLM-as-judge | 사용자 정의 기준으로 점수화 |
| Pairwise comparisons | 두 출력 상대 비교 |
| Custom Python/TypeScript | 비즈니스 로직 적용 커스텀 평가 |

## Human Feedback & Annotation 워크플로

1. 검토할 run을 annotation queue에 플래그 처리
2. 해당 분야 전문가(subject-matter experts)에게 배정
3. 임베디드 UI 렌더링으로 검토
4. 표준화된 공유 점수 기준(rubric)으로 피드백

## LLM-as-Judge 신뢰성 향상

- 인간 검토자가 불일치를 표시(flag)하여 자동 평가의 실패 모드 발견
- 반복적으로 자동 메트릭을 보정(calibrate)

## Agent-specific Evaluation

에이전트 평가는 단순 출력 비교를 넘어선다:
- 에이전트가 수행한 **전체 단계 궤적(full trajectory of steps)** 캡처
- **도구 호출(tool calls)** 내역 분석
- **추론 경로(reasoning)** 디버깅

## Multi-modal Evaluation

평가 대상을 텍스트에 한정하지 않는다:
- **Conversation evals**: 대화 전체 평가
- **Multi-modal evals**: 이미지, 오디오, 문서 포함 평가

## Prompt Optimization 연계

Playground에서 프롬프트를 실험하고, 다양한 프롬프트 버전이나 모델 제공자 간 출력을 비교할 수 있다. AI 지원 프롬프트 개선 및 UI에서 직접 평가 스케일링을 지원한다.

## 플랫폼 핵심 가치

> "Score user interactions with your agent in real-time to detect issues and measure quality."

실시간 점수화 → 이슈 감지 → 품질 개선의 피드백 루프를 자동화한다.
