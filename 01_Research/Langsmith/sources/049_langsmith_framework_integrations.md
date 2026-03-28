---
source_id: 049
title: "LangSmith Framework Integrations — LangChain, LangGraph, CrewAI, AutoGen, Vercel AI SDK"
url: "https://docs.langchain.com/langsmith/integrations"
type: docs
scraped_at: 2026-03-27
keywords: ["framework integrations", "kw_019"]
content_length: 1780
---

# LangSmith Framework Integrations — LangChain, LangGraph, CrewAI, AutoGen, Vercel AI SDK

## 개요

LangSmith는 "많은 프레임워크 및 프로바이더와 연동된다"고 공식 문서가 명시한다. 에이전트 프레임워크부터 LLM 프로바이더까지 폭넓은 통합을 지원한다.

## LLM 프로바이더 통합

LangSmith는 주요 LLM 프로바이더와 직접 연동된다:
- **Anthropic**, **OpenAI**, **Google Gemini**
- **Amazon Bedrock**, **Mistral**, **DeepSeek**

LangChain은 100개 이상의 LLM 프로바이더에 대한 통합 인터페이스를 제공하며, 환경 변수 설정만으로 모델을 전환할 수 있다.

## 에이전트 프레임워크 통합

LangSmith가 공식 지원하는 에이전트 프레임워크:

| 프레임워크 | 설명 |
|----------|------|
| **LangChain** | LangChain ecosystem 핵심 |
| **LangGraph** | 상태 기반 에이전트 오케스트레이션 |
| **CrewAI** | 다중 에이전트 협업 |
| **AutoGen** (Mastra) | 자동화된 에이전트 대화 |
| **Claude Agent SDK** | Anthropic 공식 SDK |
| **OpenAI Agents SDK** | OpenAI 공식 SDK |
| **Microsoft Agent Framework** | 마이크로소프트 에이전트 생태계 |
| **Google ADK** | Google 에이전트 개발 키트 |
| **PydanticAI** | Pydantic 기반 AI 에이전트 |
| **Vercel AI SDK** | 웹 애플리케이션용 AI SDK |
| **Semantic Kernel** | 마이크로소프트 Semantic Kernel |

## LangChain / LangGraph 통합 방식

가장 심층적인 통합이다. 개발자가 모델을 초기화하면 LangSmith가 "자동으로 애플리케이션을 트레이스"한다 — 추가 설정 없이.

```python
import os
os.environ["LANGSMITH_API_KEY"] = "your-key"
os.environ["LANGSMITH_TRACING"] = "true"

# LangChain/LangGraph 코드 실행 시 자동 트레이스
```

LangGraph의 복잡한 워크플로우에서는 단계별 실행, 에이전트 추론 과정, 상태 전이를 시각화할 수 있다.

## LlamaIndex 연동

LlamaIndex는 LangFuse, OpenTelemetry와 기본 통합을 제공한다. LangSmith와의 연동은 `@traceable` 데코레이터 또는 OpenTelemetry 브리지를 통해 가능하다.

## Vercel AI SDK 통합

웹 애플리케이션에서 AI 기능을 구현할 때 사용하는 Vercel AI SDK도 공식 통합 목록에 포함된다. JavaScript/TypeScript 환경의 Next.js 앱에서 LangSmith 트레이싱을 활성화할 수 있다.

## 추가 도구 통합

- **Instructor**: 구조화된 출력 추출
- **Temporal**: 워크플로우 오케스트레이션
- **n8n**: 노코드/로우코드 자동화
- **Claude Code**: Anthropic Claude Code 통합
