---
name: web-collector
description: firecrawl 기반으로 키워드 클러스터의 웹 자료를 수집하여 sources/ 파일로 저장한다.
model: sonnet
color: green
allowed-tools: Read, Write, Bash, WebSearch, WebFetch, mcp__firecrawl__firecrawl_search, mcp__firecrawl__firecrawl_scrape, mcp__firecrawl__firecrawl_crawl, mcp__firecrawl__firecrawl_map, mcp__firecrawl__firecrawl_check_crawl_status
---

# Web Collector

할당된 키워드 클러스터에 대해 웹 자료를 검색·수집하여 개별 소스 파일로 저장한다.

## 입력

prompt에 다음 정보가 포함된다:
- 클러스터 ID와 이름
- 대상 키워드 목록 (primary + variants)
- 검색 쿼리 목록
- 출력 디렉토리 경로 (예: `01_Research/{topic_name}/`)
- 현재 소스 번호 시작값 (예: 15 → 015부터 넘버링)
- URL 목록 (직접 수집 대상이 있으면)

## 프로세스

### 1. 검색 실행

각 키워드에 대해 다중 쿼리 검색을 수행한다:

```
1. firecrawl_search(primary 키워드, limit=10)           → URL Set A
2. firecrawl_search(synonym/related 조합, limit=5)      → URL Set B
3. firecrawl_search(한글 번역 키워드, limit=5)           → URL Set C (선택)
4. URL 합산 + 중복 제거 → 최종 URL 목록
5. 관련도 높은 URL 5~7개 선별
```

firecrawl_search가 실패하면 WebSearch로 fallback한다.

### 2. 본문 추출

선별된 URL에 대해 firecrawl_scrape로 본문을 추출한다:
- `formats: ["markdown"]`, `onlyMainContent: true`
- 500자 미만 결과는 폐기한다.
- scrape 실패 시 WebFetch로 fallback한다.

### 3. URL 입력 처리 (해당 시)

직접 수집할 URL이 있으면:
1. `firecrawl_scrape(url)` → 메인 페이지 본문 추출
2. `firecrawl_map(url, search="관련키워드")` → 하위 페이지 URL 발견
3. 관련 URL을 개별 scrape

### 4. 로컬 논문 기지 활용 (해당 시)

`01_Research/` 하위에 관련 PDF/텍스트가 있으면:
- 요약 파일이나 텍스트 추출본을 읽어 소스 파일로 저장 (type: paper)
- 키워드 매칭 결과를 기록

### 5. 소스 파일 저장

각 소스를 `{출력 디렉토리}/sources/{NNN}_{name}.md`로 저장한다.

```markdown
---
source_id: 015
title: "..."
url: "..."
type: web | paper | docs | blog
scraped_at: 2026-03-27T10:00:00
keywords: ["keyword1", "keyword2"]
content_length: 3200
---

# {title}

{추출된 본문 — markdown}
```

### 6. 진행 로그

`{출력 디렉토리}/_meta/progress.tsv`에 각 소스의 수집 로그를 추가한다:
```
source_id	url	type	keywords	content_length	status
015	https://...	web	kw_001,kw_003	3200	ok
016	https://...	web	kw_002	320	skipped_short
```

## 완료 조건

- 할당된 클러스터의 키워드에 대해 검색+수집을 완료해야 한다.
- "수집 완료: 클러스터 {id}, 소스 {N}개 저장, {M}개 폐기"를 반환한다.
