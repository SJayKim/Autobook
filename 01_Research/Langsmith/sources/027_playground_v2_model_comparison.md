---
source_id: 027
title: "LangSmith Playground v2 — 확장 모델 지원, 동시 실행, 통합 레이아웃"
url: "https://changelog.langchain.com/announcements/langsmith-playground-v2-more-models-better-compatibility-faster-testing"
type: web
scraped_at: 2026-03-27
keywords: ["prompt playground"]
content_length: 1180
---

# LangSmith Playground v2 — 확장 모델 지원, 동시 실행, 통합 레이아웃

## 개요

LangSmith Playground v2는 더 많은 모델 제공자(provider)를 지원하고, 단일 인터페이스에서 다양한 설정을 실험할 수 있도록 개선된 버전이다.

## 확장된 모델 지원

v2에서 새롭게 추가된 지원 모델 및 제공자:

- **모델**: Llama 3.1, Mistral Large, Gemma 2, Gemini 1.5 Pro 등
- **제공자**: Vertex AI, Mistral, Google Generative AI 등 다양한 외부 API 제공자

## 동시 실행 (Concurrent Outputs)

단일 클릭으로 동일한 프롬프트에서 최대 5개의 출력을 동시에 생성할 수 있다. 이를 통해 모델 응답의 일관성(consistency)을 신속하게 검증한다.

## 도구 호출(Tool Use) 지원

도구 호출(tool calling)을 지원하는 모든 LangChain 모델에 대해 Playground에서 도구 사용을 테스트할 수 있다.

## 통합 레이아웃

Playground는 LangSmith 전체에 깊이 통합되어 있어, 다음 작업을 동일한 표준화된 인터페이스에서 수행한다:

- 트레이스 디버깅 (Trace debugging)
- 프롬프트 생성 및 편집
- 데이터셋 기반 평가

## 비교 모드 (Compare Mode)

여러 프롬프트와 모델 설정을 나란히(side-by-side) 비교할 수 있다. Playground 사이드바에서 "Compare" 버튼을 클릭하면 비교 모드가 활성화되며, 탭 전환 없이 동일 화면에서 설정값 변경 실험과 데이터셋 평가를 동시에 수행한다.
