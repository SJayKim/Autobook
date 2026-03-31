---
description: 온톨로지 도구를 01_Research/ 파일 시스템 조사로 대체하는 매핑 규칙
globs: "01_Research/**/*"
---

# 온톨로지 → 01_Research 매핑

Rules/2, 4, 5에서 언급하는 온톨로지 도구는 현재 프로젝트에서 다음으로 대체한다:

| Rules 원문 | 현재 구현 |
|-----------|----------|
| `list_documents` | `Glob("01_Research/{topic}/sources/*.md")` |
| `query_data(keyword)` | `Grep(keyword, "01_Research/{topic}/")` |
| `get_chunks(doc_id)` | `Read("01_Research/{topic}/sources/{NNN}_*.md")` |
| "온톨로지 우선 조사" | 01_Research/ 디렉토리 탐색 우선, 웹은 보완용 |
| "50개 쿼리" | learning_content 키워드별 최소 2회 이상 01_Research/ 검색 |

01_Research/에 관련 자료가 없는 경우 웹 조사를 primary로 전환한다.
