# Wikidocs 구조 전환 + 초보자 친화성 강화 계획

## Context

현재 autobook 워크플로우는 토픽 파일을 `교재/{책이름}/{a}_{Phase}/{a.b}_{섹션}/{a.b.c}_{토픽}.md` 중첩 구조로 출력한다. 이를 위키독스에 바로 업로드할 수 있는 flat `pages/` 구조로 전환하고, Phase/섹션 개요 페이지 자동 생성을 워크플로우에 포함시킨다. 동시에 초보자 친화성 기준을 평가 단계뿐 아니라 작성 단계에서도 강화한다.

## 변경 대상 파일 (10개)

| # | 파일 | 변경 범위 |
|---|------|-----------|
| 1 | `CLAUDE.md` | 프로젝트 구조 설명 업데이트 |
| 2 | `.claude/skills/curriculum/SKILL.md` | wikidocs 초기화 단계 추가 |
| 3 | `.claude/skills/autobook/SKILL.md` | 경로 전환 + 개요 생성 + TOC 업데이트 |
| 4 | `.claude/skills/write-topic/SKILL.md` | 경로 전환 + TOC 업데이트 |
| 5 | `.claude/skills/next-topic/SKILL.md` | 경로 표시 변경 |
| 6 | `.claude/skills/review-topic/SKILL.md` | 경로 탐색 변경 |
| 7 | `.claude/skills/progress/SKILL.md` | 파일 스캔 변경 |
| 8 | `.claude/agents/topic-writer.md` | 자가 점검 체크리스트 추가 |
| 9 | `.claude/agents/topic-evaluator.md` | 항목 1 경로 패턴 변경 |
| 10 | `.claude/rules/topic-writing.md` | 파일 경로 항목 업데이트 |

---

## Step 1: `CLAUDE.md` — 프로젝트 구조 업데이트

산출물 구조 섹션을 다음으로 교체:

```
교재/{책이름}/
  curriculum.json
  results.tsv
  ._research/
  wikidocs/
    README.md             ← 책 소개 (자동 생성)
    TOC.md                ← 목차 (자동 생성/갱신)
    assets/               ← 이미지
    pages/
      00-들어가며.md
      {pp}-{Phase제목}.md           ← Phase 개요
      {pp}-{ss}-{섹션제목}.md       ← 섹션 개요
      {pp}-{ss}-{tt}-{토픽제목}.md  ← 토픽 본문
```

워크플로우 섹션에서 "문서 작성 구조는 wikidocs에 바로 업로드할 수 있는 flat pages/ 구조" 명시.

---

## Step 2: `.claude/skills/curriculum/SKILL.md` — wikidocs 초기화

4단계(검증)와 5단계(완료) 사이에 **"4.5단계: Wikidocs 구조 초기화"** 추가:

1. `교재/$ARGUMENTS/wikidocs/` 디렉토리 생성
2. `교재/$ARGUMENTS/wikidocs/pages/` 디렉토리 생성
3. `교재/$ARGUMENTS/wikidocs/assets/` 디렉토리 생성
4. **README.md 생성**: curriculum.json의 title, Phase별 제목/exit_capability로 책 소개
5. **TOC.md 스켈레톤 생성**: 전체 Phase > 섹션 > 토픽 계층 구조 (아직 파일 미존재하므로 링크만 선점)
6. **pages/00-들어가며.md 생성**: 책 도입 페이지 (curriculum title 기반)
7. **Phase 개요 페이지 생성**: `pages/{pp}-{Phase제목}.md` (6개)
   - 내용: exit_capability + 하위 섹션/토픽 목록
8. **섹션 개요 페이지 생성**: `pages/{pp}-{ss}-{섹션제목}.md` (25개)
   - 내용: 하위 토픽별 제목 + learning_objectives 요약

기존 상태 확인(1단계)에도 `wikidocs/` 디렉토리 존재 여부 체크 추가 (resume 대응).

---

## Step 3: `.claude/skills/autobook/SKILL.md` — 핵심 오케스트레이터 전환

### SETUP 변경

- **1.4**: 파일 스캔 대상을 `교재/$ARGUMENTS/wikidocs/pages/`로 변경. `{pp}-{ss}-{tt}-*.md` 패턴으로 매칭.
- **2**: wikidocs 디렉토리가 없으면 생성 (README.md, TOC.md, 개요 페이지 포함).

### 경로 공식 정의 (LOOP 상단에 명시)

```
토픽 파일: 교재/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md
  pp = phase id를 2자리 zero-pad (예: "1" → "01")
  ss = section id의 두 번째 숫자를 2자리 zero-pad (예: "1.2" → "02")
  tt = topic id의 세 번째 숫자를 2자리 zero-pad (예: "1.2.3" → "03")
```

### LOOP 각 단계 변경

- **① SELECT**: 출력 경로를 `wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md`로 변경. 선수 파일 경로도 동일 패턴.
- **③ WRITE**: prompt 내 출력 경로/선수 경로 모두 wikidocs 경로로 변경.
- **④ GIT COMMIT**: `git add` 경로를 `wikidocs/pages/` 하위로 변경.
- **⑤ EVALUATE**: prompt 내 파일 경로 변경.
- **⑥ DECIDE**: reviser prompt 내 파일 경로 변경.

### 새 단계 추가: TOC UPDATE (⑦ LOG 직전)

토픽 작성/수정 완료 후 `wikidocs/TOC.md`를 curriculum.json 기반으로 재생성(rebuild). 존재하는 페이지만 링크, 미작성 토픽은 제목만 표시.

### FINISH 변경

최종 완료 시:
1. TOC.md 최종 rebuild
2. 전체 pages/ 파일 존재 확인
3. 누락 파일 경고

---

## Step 4: `.claude/skills/write-topic/SKILL.md` — 경로 전환

- **1단계**: 기존 파일 스캔을 `wikidocs/pages/` 대상으로 변경. `{pp}-{ss}-{tt}-` 접두사로 토픽 ID 매칭.
- **3단계**: prompt 내 출력 경로를 `wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md`로 변경. 선수 파일 경로도 동일.
- **5단계 이후**: TOC.md 갱신 단계 추가 (새 토픽 페이지 링크 반영).

---

## Step 5: `.claude/skills/next-topic/SKILL.md` — 경로 표시

- **1단계**: `wikidocs/pages/` 스캔. 파일명 `{pp}-{ss}-{tt}-` 패턴에서 토픽 ID 추출.
- **3단계**: 토픽 정보에 `파일 경로: wikidocs/pages/{pp}-{ss}-{tt}-{title}.md` 추가.

---

## Step 6: `.claude/skills/review-topic/SKILL.md` — 경로 탐색

- **1단계**: 토픽 ID가 주어지면 `wikidocs/pages/{pp}-{ss}-{tt}-*` 패턴으로 탐색.
- **항목 1 (경로/파일명)**: 기대 패턴을 `pages/{pp}-{ss}-{tt}-{토픽제목}.md`로 변경.

---

## Step 7: `.claude/skills/progress/SKILL.md` — 파일 스캔

- **1단계**: `교재/{책이름}/wikidocs/pages/` 스캔.
- **1.4**: `{pp}-{ss}-{tt}-` 접두사에서 토픽 ID를 파싱 (pp → phase, ss → section 2nd digit, tt → topic 3rd digit).

---

## Step 8: `.claude/agents/topic-writer.md` — 초보자 친화성 강화 (R2)

현재 lines 67-75에 "초보자 친화적 작성 원칙" 8개 항목이 이미 있다. 여기에 **완료 전 자가 점검** 섹션을 추가:

```markdown
## 완료 전 자가 점검

파일을 저장하기 전에 다음을 확인한다:
1. 각 문단을 훑으며 **새 굵은 용어**가 3개 이상 한 문단에 몰려 있지 않은지 확인.
2. 추상적 정의를 쓴 곳에서 2문단 이내에 구체 사례(코드, 시나리오, 수치)가 있는지 확인.
3. 3단계 이상 프로세스를 서술한 곳에 ASCII 다이어그램이나 표가 있는지 확인.
4. "~에 의해", "~를 수행한다" 같은 번역 투/명사화를 검색하여 수정.
5. 80자를 넘는 문장을 찾아 분리.
```

이 자가 점검은 evaluator 항목 8-10과 동일 기준이지만, **작성 시점에서 선제적으로 적용**하여 평가 FAIL을 예방한다.

---

## Step 9: `.claude/agents/topic-evaluator.md` — 항목 1 패턴 변경

**항목 1 (경로/파일명 규칙)** 변경:

Before:
```
파일 경로가 `{a}_{Phase}/{a.b}_{섹션}/{a.b.c}_{토픽}.md` 패턴과 일치하는가?
```

After:
```
파일 경로가 `wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md` 패턴과 일치하는가?
(pp=phase 2자리, ss=섹션 2자리, tt=토픽 2자리, 제목은 curriculum.json title과 대응)
```

---

## Step 10: `.claude/rules/topic-writing.md` — 경로 항목 업데이트

항목 5 (파일 경로)를 변경:

Before: `교재/{책이름}/{a}_{Phase}/{a.b}_{섹션}/{a.b.c}_{토픽}.md`
After: `교재/{책이름}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽}.md`

globs 패턴 `교재/**/*.md`는 새 경로도 매칭하므로 변경 불필요.

---

## 실행 순서

1. Step 1 (CLAUDE.md) — 구조 설명 기반
2. Step 10 (topic-writing.md rule) — 경로 참조 먼저 통일
3. Step 9 (topic-evaluator.md) — 평가 기준 경로 맞춤
4. Step 8 (topic-writer.md) — 자가 점검 추가
5. Step 2 (curriculum SKILL) — 초기화 단계 추가
6. Step 3 (autobook SKILL) — 핵심 오케스트레이터 (가장 큰 변경)
7. Step 4 (write-topic SKILL) — 수동 모드 경로 전환
8. Step 5 (next-topic SKILL) — 경로 표시
9. Step 6 (review-topic SKILL) — 경로 탐색
10. Step 7 (progress SKILL) — 스캔 변경

---

## 검증 방법

1. **단위 검증**: 각 파일 수정 후 해당 skill/agent 내 경로 참조가 모두 `wikidocs/pages/` 기준인지 Grep 확인
2. **통합 검증**: 새 테스트 책으로 `/curriculum test-book` → `/next-topic` → `/write-topic` 순으로 1개 토픽 작성하여 위키독스 구조 정상 생성 확인
3. **TOC 검증**: 토픽 작성 후 TOC.md에 해당 페이지 링크가 정상 반영되는지 확인
4. **평가 검증**: `/review-topic`으로 새 경로의 파일을 정상 탐색/평가하는지 확인
