---
source_id: 028
title: "LangSmith Playground — 프롬프트 빌드 및 Side-by-Side 비교"
url: "https://changelog.langchain.com/announcements/build-prompts-faster-and-compare-in-langsmith-playground"
type: web
scraped_at: 2026-03-27
keywords: ["prompt playground"]
content_length: 980
---

# LangSmith Playground — 프롬프트 빌드 및 Side-by-Side 비교

## 개요

LangSmith Playground에 프롬프트를 더 빠르게 빌드하고 여러 설정을 나란히 비교하는 기능이 추가되었다 (출시: 2024년 7월 17일).

## 핵심 기능: Side-by-Side 비교

탭 전환이나 컨텍스트 전환 없이, 여러 프롬프트와 모델 설정을 한 화면에서 동시에 비교할 수 있다.

> "No more juggling tabs or context-switching — you can now compare multiple prompts and model configurations side-by-side in LangSmith's Playground."

## 활성화 방법

1. LangSmith Playground 사이드바로 이동
2. "Compare" 버튼 클릭 → 비교 모드 활성화

## 통합 워크플로우

단일 뷰(single view)에서 다음 세 가지 활동을 연속적으로 수행할 수 있다:

1. **프롬프트 생성 및 테스트** — 에디터에서 직접 프롬프트 작성 및 즉시 실행
2. **설정값 변경 실험** — 모델, 파라미터, 시스템 메시지 변경 후 즉각 비교
3. **데이터셋 기반 평가** — 저장된 데이터셋을 불러와 전체 예시 집합에 대해 실험 실행

## 효과

- 반복(iteration) 속도 향상: 설정 변경 후 결과를 즉시 확인
- 모델 프로바이더 간 성능 비교가 단일 인터페이스에서 가능
- 개발자와 비개발자 모두 코드 없이 프롬프트 품질 검증 가능
