---
source_id: 041
title: "LangSmith — Cost Tracking (Token Usage, Provider Cost Breakdown)"
url: "https://docs.langchain.com/langsmith/cost-tracking"
type: docs
scraped_at: 2026-03-27
keywords: ["cost and token tracking", "LLM 비용", "provider cost breakdown", "token usage"]
content_length: 3180
---

# LangSmith — Cost Tracking (Token Usage, Provider Cost Breakdown)

## 개요

에이전트를 대규모로 운영하면 사용량 기반 비용이 상당히 발생합니다. LangSmith는 주요 제공자의 LLM 토큰 사용량과 비용을 자동으로 기록하며, 커스텀 비용 데이터 제출도 지원합니다.

## 토큰 및 비용 분류

비용은 세 가지 범주로 나뉩니다.

| 범주 | 설명 | 예시 |
|------|------|------|
| **입력(Input)** | 프롬프트 토큰 | 캐시 읽기, 텍스트, 이미지 입력 |
| **출력(Output)** | 응답 토큰 | 추론(Reasoning), 텍스트, 이미지 출력 |
| **기타(Other)** | 그 외 비용 | 도구 호출, 검색, 커스텀 실행 비용 |

## UI에서 비용 확인 — 3가지 뷰

### 1. 트레이스 트리 (Trace Tree)

개별 트레이스의 가장 상세한 토큰 사용량과 비용을 표시합니다. 각 부모/자식 실행의 집계 값을 포함합니다.

### 2. 프로젝트 통계 (Project Stats)

프로젝트 전체의 총 토큰 사용량과 비용을 집계하여 보여줍니다.

### 3. 대시보드 (Dashboard)

시간 경과에 따른 비용 추세를 탐색하며, 입출력 토큰별 비용 분석이 가능합니다.

## 비용 추적 방식

### 방식 1: 토큰 기반 자동 계산

필수 요소:
1. **토큰 수 제공**: `usage_metadata` 필드로 입출력 토큰 정보 전달
2. **모델 정보 지정**: `ls_provider`, `ls_model_name` 지정
3. **가격 설정**: 모델 가격 테이블에서 per-token 가격 설정

Python SDK 예시:
```python
# 방법 A — run에 직접 설정
run = get_current_run_tree()
run.set(usage_metadata={
    "input_tokens": 27,
    "output_tokens": 13,
    "input_token_details": {"cache_read": 10}
})

# 방법 B — 반환값에 포함
return {
    "message": "...",
    "usage_metadata": {
        "input_tokens": 27,
        "output_tokens": 13
    }
}
```

비용 계산 로직: 세부 토큰 타입(cache_read, reasoning 등) 가격부터 적용하고, 남은 토큰에는 기본 가격을 적용합니다.

### 방식 2: 직접 비용 지정

비선형 가격 체계(예: Gemini 단계별 가격)를 위해 클라이언트에서 비용을 직접 계산하여 제출합니다.

```python
run.set(usage_metadata={
    "input_cost": 1.1e-6,
    "input_cost_details": {"cache_read": 2.3e-7},
    "output_cost": 5.0e-6
})
```

## 커스텀 가격 설정 (Model Price Map)

모델 가격 테이블(`smith.langchain.com/settings/workspaces/models`)에서 새 항목 생성 시 지정 항목:

- **모델명**: 사람이 읽을 수 있는 이름
- **입력 가격**: 100만 입력 토큰당 비용 ($/1M tokens)
- **입력 가격 분석**: `cache_read`, `video`, `audio` 등 타입별 가격
- **출력 가격**: 100만 출력 토큰당 비용
- **출력 가격 분석**: `reasoning`, `image` 등 타입별 가격
- **정규식 패턴**: `ls_model_name` 매칭용
- **제공자(Provider)**: `ls_provider` 매칭용

## Provider 지원 현황

자동 가격 계산을 지원하는 주요 제공자: OpenAI, Anthropic, Google Gemini, 기타 OpenAI 호환 모델

멀티모달 토큰(이미지, 오디오)과 캐시 읽기(cache reads)도 지원합니다.

## 비-LLM 실행 비용 추적

도구 호출 등 LLM이 아닌 실행 유형도 비용 추적 가능합니다.

```python
run = get_current_run_tree()
run.set(usage_metadata={"total_cost": 0.0015})
```

## 주요 제한사항

모델 가격 맵 업데이트는 이미 기록된 트레이스에 소급 적용되지 않습니다. 가격을 변경해도 과거 트레이스의 비용 수치는 변경 전 가격으로 유지됩니다.
