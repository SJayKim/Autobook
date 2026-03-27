---
description: curriculum.json 파일을 편집할 때 자동 로드
globs: "**/curriculum.json"
---

# curriculum.json 편집 리마인더

curriculum.json을 수정할 때 반드시 준수할 사항:

1. **스키마 준수**: `Rules/curriculum.schema.json`에 정의된 구조를 따른다.
2. **계층 규칙**: `Rules/1. 커리큘럼 계층 규칙.md`의 Phase > Section > Topic 구조를 유지한다.
3. **작성 규칙**: `Rules/2. 커리큘럼 작성 규칙.md`의 4대 필수 속성을 만족한다:
   - 하나의 토픽 = 하나의 초점
   - 파일과 토픽 1:1 대응
   - 최소 50개 토픽
   - 상세 교재 수준
4. **선수 관계**: prerequisites는 반드시 DAG(비순환)를 유지한다.
5. **검증**: 수정 후 `/validate-curriculum`으로 검증한다.
6. **ID 연속성**: 기존 토픽의 ID를 변경하면 이미 작성된 단원 파일과 불일치가 발생한다. 신중하게 변경한다.
