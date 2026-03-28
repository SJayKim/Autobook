---
source_id: 019
title: "LangSmith — Online Evaluation (프로덕션 평가, Sampling Rate, Quality Drift)"
url: "https://docs.langchain.com/langsmith/online-evaluations"
type: docs
scraped_at: 2026-03-27
keywords: ["online evaluation"]
content_length: 2920
---

# LangSmith — Online Evaluation (프로덕션 평가, Sampling Rate, Quality Drift)

## Online Evaluation 개요

Online Evaluation은 프로덕션 트래픽에서 실시간으로 LLM 애플리케이션 품질을 모니터링하는 기능이다. 사용 목적:
- 독성(toxicity) 감지
- RAG의 Hallucination 확인
- 품질 드리프트(quality drift) 탐지
- 성능 이상(anomaly) 감지 및 알림

## 목적과 동기

프로덕션 LLM 트래픽에 직접 평가를 실행하면 성능과 품질을 지속적으로 모니터링할 수 있다. "지속적으로 품질을 측정하고 일관성을 보장한다."

## Evaluator 설정 방법

### UI 경로
1. 트레이싱 프로젝트의 **Evaluators** 탭으로 이동
2. **+ New Evaluator** 클릭
3. 이름 입력 및 동작 구성

### 필터 설정
특정 run에만 evaluator가 실행되도록 필터를 적용한다:
- 사용자 피드백이 불만족인 run
- 특정 tool 호출이 있는 run
- 커스텀 메타데이터 매칭 (예: customer tier = "enterprise")

UI에서 필터 설정 중 run을 직접 검사하여 더 쉽게 구성할 수 있다.

## Sampling Rate (샘플링 비율)

모든 요청을 평가하면 비용이 크기 때문에 샘플링 비율로 제어한다:

```
sampling_rate = 0.1  # 필터링된 run의 10%만 평가
```

규칙에 샘플링 비율을 지정하여 평가할 트레이스 비율을 조절한다. 충분한 표본으로 품질 저하와 드리프트를 탐지할 수 있는 수준을 설정한다.

## Backfill 기능

규칙 생성 시 "Apply to past runs" 토글을 활성화하면 지정된 날짜 이후의 과거 트레이스를 소급 평가한다. 진행 상황은 evaluator logs에서 추적할 수 있다.

## 멀티모달 콘텐츠 지원

트레이스에 기록된 base64 인코딩 콘텐츠 또는 첨부파일(이미지, 오디오, 문서)에도 evaluator를 적용할 수 있다. 활용 예시:
- 음성 변환(transcription) 유효성 검사
- 이미지 설명 정확도 확인

## 데이터 보존 영향

Evaluator를 실행하면 영향받는 트레이스가 **확장 보존(extended retention)**으로 자동 업그레이드된다. 이는 가격에 영향을 주지만 중요한 데이터를 분석을 위해 보존한다.

## Evaluator 유형

Online evaluator로 사용할 수 있는 방식:
1. **LLM-as-a-judge**: 정의된 기준과 점수 루브릭으로 LLM이 평가
2. **Custom Python logic**: 구조 확인, 출력 유효성 검사, 비즈니스 규칙 적용

## Quality Drift 감지

Online evaluation 점수를 시간 축으로 집계하면 품질 드리프트를 감지할 수 있다. 점수 추이가 특정 임계값 아래로 내려가면 알림을 구성하여 대응할 수 있다.
