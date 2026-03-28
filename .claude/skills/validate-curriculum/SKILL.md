---
name: validate-curriculum
description: 커리큘럼 JSON을 스키마 + 규칙 기준으로 심층 검증하여 구조화된 리포트를 출력한다.
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash
---

# 커리큘럼 검증

대상: **$ARGUMENTS** (비어있으면 `02_Books/*/curriculum.json`을 자동 탐지)

## 검증 절차

### 1단계: 커리큘럼 로드

1. 대상 curriculum.json을 찾아 읽는다.
2. `Rules/curriculum.schema.json`을 읽는다.

### 2단계: 구조 검증

JSON 구조가 스키마에 맞는지 확인한다:
- 필수 루트 필드: `schema_version`, `curriculum_id`, `numbering`, `phases[]`
- 각 phase: `id`, `title`, `sections[]`
- 각 section: `id`, `phase_id`, `title`, `topics[]`
- 각 topic: `id`, `section_id`, `title`, `order`, `learning_objectives`, `learning_content`, `prerequisites`
- ID 형식: phase `a`, section `a.b`, topic `a.b.c`
- `numbering.phase_base`가 0 또는 1이고 문서 전체에서 일관적인지

### 3단계: 규칙 기반 검증

아래 항목을 모두 검사하고 pass/fail/warning으로 분류한다:

**필수 (fail이면 수정 필요):**
- [ ] 세부 주제 총 개수 >= 50
- [ ] 각 topic.id가 소속 section.id를 접두사로 가짐
- [ ] 각 section.id가 소속 phase.id를 접두사로 가짐
- [ ] prerequisites의 모든 ID가 실제 topic.id로 존재
- [ ] prerequisites DAG에 순환 없음 (위상 정렬 가능)
- [ ] prerequisite_ordering.mode가 id_numeric_tuple이면: 모든 선수 (a,b,c) 튜플이 본인보다 사전순으로 앞섬
- [ ] prerequisite_ordering.mode가 global_sequence이면: 모든 선수 global_sequence < 본인
- [ ] 각 topic의 learning_objectives가 1개 이상

**경고 (검토 권장):**
- [ ] learning_objectives가 3개 이상인 토픽 (단일 초점 위반 가능성)
- [ ] Phase에 exit_capability가 없는 경우
- [ ] 한 섹션에 토픽 20개 초과
- [ ] 한 섹션에 토픽 1~2개만 있는 경우
- [ ] learning_content가 빈 배열인 토픽
- [ ] 동일한 title을 가진 토픽이 여러 개

### 4단계: 리포트 출력

아래 형식으로 결과를 정리한다:

```
## 커리큘럼 검증 리포트

### 기본 정보
- 파일: [경로]
- curriculum_id: [값]
- Phase 수: [N]
- 섹션 수: [N]
- 토픽 수: [N]

### 검증 결과

| # | 항목 | 결과 | 비고 |
|---|------|------|------|
| 1 | 토픽 수 >= 50 | PASS/FAIL | ... |
| 2 | ID 접두사 정합 | PASS/FAIL | ... |
| ... | ... | ... | ... |

### FAIL 항목 상세
[각 실패 항목에 대해 구체적 위치와 수정 방안]

### WARNING 항목 상세
[각 경고 항목에 대해 구체적 위치와 권장 조치]
```
