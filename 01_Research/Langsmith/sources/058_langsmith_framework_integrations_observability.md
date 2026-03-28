---
source_id: 058
title: "LangSmith Observability — Framework-Agnostic Integrations"
url: "https://www.langchain.com/langsmith/observability"
type: web
scraped_at: 2026-03-27
keywords: ["framework integrations", "kw_019"]
content_length: 1580
---

# LangSmith Observability — Framework-Agnostic Integrations

## 프레임워크 독립성

LangSmith는 "OpenAI SDK, Anthropic SDK, Vercel AI SDK, LlamaIndex, 또는 커스텀 구현으로 구축된 애플리케이션을 트레이스할 수 있으며, LangChain만이 아니다"라고 명시한다. 즉, **"어떤 LLM 프레임워크와도"** 동작한다.

## 지원 SDK 언어

LangSmith는 여러 언어용 SDK를 제공한다:
- **Python SDK**: `pip install -U langsmith`
- **TypeScript/JavaScript SDK**: `npm install langsmith`
- **Go SDK**: 공식 지원
- **Java SDK**: 공식 지원

## 통합 방식

**Native 트레이싱**: 주요 에이전트 프레임워크에 대한 네이티브 트레이싱 지원

**OpenTelemetry 지원**: OTel 기반 트레이스 내보내기 (`POST /otel/v1/traces`)

## LangChain 에코시스템 통합

LangSmith는 세 가지 LangChain 에코시스템 도구와 깊은 통합을 제공한다:

1. **LangChain**: "모든 모델 프로바이더로 에이전트를 빠르게 시작"
2. **LangGraph**: "저수준 제어로 신뢰할 수 있는 에이전트 빌드"
3. **Deep Agents**: "복잡한 작업을 위한 장기 실행 에이전트 빌드"

## 주요 관찰 기능

- LLM 호출 입력/출력 트레이싱
- 도구 호출 및 체인 단계 추적
- 에이전트 성능, 리소스 소비, 시스템 동작 추적
- 복잡한 워크플로우에서 단계별 실행 시각화
- 비결정론적 LLM 동작 디버깅
- 에이전트 추론 과정 이해

## LangGraph 특화 통합

LangGraph와의 통합은 강력한 관측 레이어를 생성한다:
- 에이전트 성능, 리소스 소비, 시스템 동작 추적 가능
- 복잡한 워크플로우의 단계별 실행을 자세한 트레이스로 시각화
- Zero-code 변경으로 LangSmith에 자동 연결 (환경 변수만 설정)

## LlamaIndex 연동 접근

LlamaIndex는 LangFuse 및 OpenTelemetry와 기본 통합을 제공하며, LangSmith와의 연동은 `@traceable` 데코레이터 또는 OTel 브리지를 활용한다. 프로덕션 환경을 위한 '원클릭 관찰성' 기능도 지원한다.

## CrewAI, AutoGen 통합

CrewAI와 AutoGen은 공식 통합 목록에 포함된다. LangSmith의 `@traceable` 데코레이터를 에이전트 실행 함수에 적용하거나, 프레임워크별 제공되는 콜백/훅 메커니즘으로 연결한다.
