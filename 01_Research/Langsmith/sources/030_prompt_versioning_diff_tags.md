---
source_id: 030
title: "LangSmith 프롬프트 버전 관리 — Diff View와 Prompt Tags"
url: "https://changelog.langchain.com/announcements/diff-view-in-langsmith-s-prompt-hub"
type: web
scraped_at: 2026-03-27
keywords: ["prompt versioning"]
content_length: 1580
---

# LangSmith 프롬프트 버전 관리 — Diff View와 Prompt Tags

## Diff View: 커밋 간 변경사항 비교

LangSmith Prompt Hub에 Diff View 기능이 추가되어 커밋 간 변경사항을 시각적으로 비교할 수 있다.

### 사용 방법

1. Prompt Hub의 **Commits 탭** 접근
2. 우측 상단의 **Diff View 버튼** 활성화 (또는 "Show diff" 토글)
3. 선택한 커밋을 이전 버전과 비교하거나 여러 커밋 간 변경사항 탐색

### 버전 관리 특징

프롬프트의 모든 저장 업데이트는 자동으로 새 커밋을 생성하므로 명확한 변경 이력(audit trail)이 유지된다. SDK에서 특정 커밋을 참조하는 방법:

```python
# 커밋 해시로 특정 버전 고정
prompt = client.pull_prompt("prompt_name:commit_hash")
```

## Prompt Tags: 버전 태깅으로 환경 관리

커밋에 인간 친화적 태그를 부여하여 환경별 버전을 체계적으로 관리한다.

### 태그 관리 작업

| 작업 | 방법 |
|------|------|
| 생성 | 프롬프트 히스토리 Commits 탭에서 태그 추가 |
| 이동 | 다른 커밋으로 태그 재할당 |
| 삭제 | 커밋에 영향 없이 태그만 제거 |

### 환경별 활용 패턴

```python
# 프로덕션 버전 참조
prompt = client.pull_prompt("joke-generator:prod")

# 스테이징 버전 참조
prompt = client.pull_prompt("joke-generator:staging")
```

코드 수정 없이 태그가 가리키는 커밋만 변경하여 환경 전환을 관리한다.

## SDLC 통합

LangSmith는 웹훅(webhook) 트리거를 통해 프롬프트 변경 사항을 GitHub, 외부 데이터베이스, CI/CD 파이프라인과 자동으로 동기화할 수 있다. 주요 이점:

- **버전 관리**: 코드와 함께 프롬프트를 유지하는 GitHub 통합
- **워크플로우 자동화**: 프롬프트 변경 시 CI/CD 자동 배포
- **동기화**: 수동 복사-붙여넣기 제거
