---
source_id: 031
title: "LangSmith 프롬프트 태그와 SDLC 통합 — commit hash, 태그 기반 환경 분리"
url: "https://changelog.langchain.com/announcements/prompt-tags-in-langsmith-for-version-control"
type: web
scraped_at: 2026-03-27
keywords: ["prompt versioning"]
content_length: 1320
---

# LangSmith 프롬프트 태그와 SDLC 통합 — commit hash, 태그 기반 환경 분리

## 프롬프트 태깅(Prompt Tagging) 기능 개요

LangSmith의 프롬프트 태깅 기능은 개별 커밋에 버전 태그(예: `dev`, `staging`, `v2`)를 붙여 환경별 버전을 체계적으로 관리한다.

## 태그 생성 및 관리

세 가지 핵심 작업:

1. **생성(Create)**: 프롬프트 히스토리의 Commits 탭에서 태그 추가
2. **이동(Move)**: 다른 커밋으로 태그 재할당 — 배포 시 태그만 이동하면 코드 변경 불필요
3. **삭제(Delete)**: 커밋에 영향 없이 태그만 제거

## SDK를 통한 태그 참조

```python
# 태그를 커밋 식별자로 사용
prompt = client.pull_prompt("joke-generator:prod")
```

커밋 해시 대신 태그를 사용하면 코드 수정 없이 프롬프트 버전을 교체할 수 있다.

## 환경별 활용 패턴

| 환경 | 태그 예시 | 활용 목적 |
|------|-----------|-----------|
| 프로덕션 | `prod` | 안정적으로 검증된 버전 |
| 스테이징 | `staging` | QA 및 검증 환경 |
| 개발 | `dev` | 진행 중인 작업 추적 |
| 버전 릴리스 | `v1`, `v2` | 마일스톤 버전 고정 |

## 배포 워크플로우

1. 새 커밋 생성 (프롬프트 수정 후 저장)
2. 스테이징 환경에서 검증
3. `staging` 태그를 새 커밋으로 이동
4. 검증 완료 후 `prod` 태그를 동일 커밋으로 이동
5. 코드베이스 변경 없이 프로덕션 업데이트 완료
