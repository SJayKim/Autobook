---
description: 01_Research/ 하위 자료 수집 시 품질 기준 자동 리마인더
globs: "01_Research/**/*"
---

# 자료 수집 품질 기준

01_Research/ 하위 파일을 작성할 때 반드시 준수할 사항:

1. **소스 파일 포맷**: sources/*.md는 반드시 frontmatter(source_id, title, url, type, scraped_at, keywords, content_length)를 포함한다.
2. **최소 콘텐츠**: 500자 미만의 추출 본문은 저장하지 않는다 (빈 스크랩, 에러 페이지 제외).
3. **중복 방지**: 동일 URL의 소스를 중복 저장하지 않는다. 저장 전 기존 sources/를 확인한다.
4. **키워드 매핑**: 각 소스 파일의 keywords 필드에 keyword_map.json의 어떤 키워드와 매칭되는지 기록한다.
5. **진행 로그**: 소스 저장/폐기 시 _meta/progress.tsv에 로그를 추가한다.
6. **synthesis 일관성**: synthesis/ 파일은 sources/의 실제 내용만 근거로 작성한다. 추측이나 외부 지식을 혼합하지 않는다.
