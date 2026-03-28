---
source_id: 029
title: "LangSmith 프롬프트 엔지니어링 핵심 개념 — 버전 관리, 커밋, 태그, 플레이그라운드"
url: "https://docs.langchain.com/langsmith/prompt-engineering-concepts"
type: docs
scraped_at: 2026-03-27
keywords: ["prompt versioning", "prompt playground"]
content_length: 2240
---

# LangSmith 프롬프트 엔지니어링 핵심 개념 — 버전 관리, 커밋, 태그, 플레이그라운드

## 프롬프트 기초

프롬프트는 모델의 행동을 안내하되 기본 능력을 변경하지 않는다. 두 가지 형식이 있다:

- **채팅 스타일(Chat-style)**: 역할(system, user, assistant)이 있는 메시지 목록
- **완성 스타일(Completion-style)**: 단일 문자열 형식 (하위 호환성 목적)

## 템플릿과 변수

템플릿(template)은 런타임에 채워지는 동적 자리표시자(placeholder)를 포함한 재사용 가능한 프롬프트다. `{변수명}` 형식으로 변수를 정의하면 입력값으로 자동 치환된다.

## 프롬프트 버전 관리 (Versioning)

### 커밋(Commits)

저장된 각 업데이트마다 **고유 커밋 해시(commit hash)**가 생성된다. 커밋을 통해:

- 변경 이력 전체 확인 가능
- 이전 버전 검토 및 복구 (rollback) 가능
- "Show diff" 토글로 커밋 간 차이(diff) 비교 가능
- 코드에서 `prompt_name:commit_hash` 형식으로 특정 버전 고정 참조 가능

```python
# 특정 커밋 해시로 프롬프트 불러오기
prompt = client.pull_prompt("joke-generator:12344e88")
```

### 태그(Tags)

태그는 커밋을 가리키는 인간 친화적 라벨이다. 환경(environment)별로 서로 다른 커밋을 안정적으로 참조하는 데 사용된다:

| 태그 용도 | 예시 |
|-----------|------|
| 환경 구분 | `production`, `staging`, `dev` |
| 버전 추적 | `v1`, `v2`, `latest` |
| 협업 공유 | 리뷰 대상 버전 공유 |

```python
# 태그로 프롬프트 불러오기 (커밋 해시 대신)
prompt = client.pull_prompt("joke-generator:prod")
```

## 플레이그라운드(Playground)

반복 테스트용 인터랙티브 인터페이스로, 다음 작업을 코드 없이 수행한다:

- 모델 변경 및 파라미터 조정
- 템플릿 변경 및 즉시 실행
- 출력 스키마(output schema) 구성
- 입력 변수 설정 후 단일 실행
- 여러 프롬프트 side-by-side 비교
- 데이터셋 기반 배치 테스트
