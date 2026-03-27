---
name: autobook
description: 자율 집필 모드. orchestrator + subagent 패턴으로 커리큘럼의 모든 토픽을 자동으로 작성-평가-수정 루프.
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# AutoBook — 자율 집필 루프 (Orchestrator)

대상 책: **$ARGUMENTS**

> 이 스킬은 thin orchestrator로서, 리서치·작성·평가·수정을 각각 격리된 subagent에 위임한다.
> context 오염을 방지하여 50+ 토픽 연속 작성이 가능하다.
> 사용자가 수동으로 중단할 때까지 절대 멈추지 않는다.

---

## SETUP (1회)

### 1. 커리큘럼 확인

1. `교재/$ARGUMENTS/curriculum.json` 파일을 찾는다.
2. 없으면 → "먼저 `/curriculum $ARGUMENTS`를 실행하세요." 안내 후 종료.
3. 있으면 → 로드하여 전체 Phase, Section, Topic 구조를 파악한다.
4. `교재/$ARGUMENTS/wikidocs/pages/`에서 `{pp}-{ss}-{tt}-*.md` 패턴으로 작성된 토픽 파일 수를 계산한다.

### 2. Wikidocs 구조 확인

1. `교재/$ARGUMENTS/wikidocs/` 디렉토리가 없으면 생성한다:
   - `wikidocs/pages/`, `wikidocs/assets/` 디렉토리 생성.
   - README.md, TOC.md, Phase/섹션 개요 페이지 생성 (curriculum SKILL 4.5단계와 동일).
2. 이미 존재하면 그대로 사용한다.

### 3. 브랜치 및 로그 초기화

1. 오늘 날짜 기반 태그 생성 (예: `mar27`).
2. `git checkout -b autobook/{tag}` 실행.
3. `교재/$ARGUMENTS/results.tsv` 초기화:
   ```
   topic	score	attempt	status	issues
   ```
4. `교재/$ARGUMENTS/._research/` 디렉토리 생성.
5. `.gitignore`에 `._research/` 추가 (없으면 생성).
6. stale `._research/` 파일이 있으면 정리.
7. 셋업 요약 출력:
   ```
   AutoBook 시작 (Subagent 아키텍처)
   책: {$ARGUMENTS}
   전체 토픽: {N}개
   작성 완료: {M}개
   남은 토픽: {N-M}개
   브랜치: autobook/{tag}
   ```

### 4. 자율 루프 진입

셋업 완료 후 즉시 루프에 진입한다. **사용자에게 확인을 묻지 않는다.**

---

## LOOP (무한 반복)

> **핵심 원리:** orchestrator는 메타데이터만 관리하고, 무거운 작업은 subagent에 위임한다.
> 토픽당 orchestrator context 비용: ~3-4KB (50+ 토픽 여유)

### 경로 공식

```
토픽 파일: 교재/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md
  pp = phase id를 2자리 zero-pad (예: "1" → "01")
  ss = section id의 두 번째 숫자를 2자리 zero-pad (예: "1.2" → "02")
  tt = topic id의 세 번째 숫자를 2자리 zero-pad (예: "1.2.3" → "03")
```

### ① SELECT — 다음 토픽 선택 (inline, ~2KB)

1. curriculum.json에서 토픽을 ID 순서(a.b.c 사전순)로 스캔한다.
2. `wikidocs/pages/`에서 이미 대응하는 `{pp}-{ss}-{tt}-*.md` 파일이 있는 토픽은 건너뛴다.
3. 첫 번째 미작성 토픽을 선택한다.
4. 선수 토픽(prerequisites)의 `.md` 파일이 모두 `wikidocs/pages/`에 존재하는지 확인한다.
   - 누락된 선수가 있으면: 해당 선수를 먼저 작성 대상으로 변경.
5. 모든 토픽이 작성 완료이면 → **FINISH** 단계로 이동.
6. 해당 토픽의 메타데이터를 추출한다:
   - `topic_id`, `title`, `learning_objectives`, `learning_content`, `prerequisites`
   - 선수 토픽 .md 파일 경로 목록 (`wikidocs/pages/{pp}-{ss}-{tt}-*.md`)
   - 다음 토픽 정보 (ID, 제목)
   - 출력 파일 경로: `교재/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md`

### ② RESEARCH — Agent "topic-researcher" 호출

Agent 도구로 `topic-researcher` agent를 호출한다.

**prompt:**
```
토픽 {a.b.c} "{title}" 리서치를 수행하라.

책이름: {$ARGUMENTS}
learning_content: {keywords 배열}
learning_objectives: {objectives 배열}
prerequisites: {prereq IDs}

자료 기지: 01_Research/
출력 경로: 교재/{$ARGUMENTS}/._research/{a.b.c}_findings.md

위 출력 경로에 findings 파일을 작성하라.
```

**결과:** "findings 작성 완료" (~100 tokens)

### ③ WRITE — Agent "topic-writer" 호출

Agent 도구로 `topic-writer` agent를 호출한다.

**prompt:**
```
토픽 {a.b.c} "{title}" 단원을 작성하라.

책이름: {$ARGUMENTS}
findings 경로: 교재/{$ARGUMENTS}/._research/{a.b.c}_findings.md
출력 경로: 교재/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md

curriculum 메타데이터:
- learning_objectives: {objectives}
- learning_content: {keywords}
- prerequisites: {prereq IDs}

선수 토픽 파일:
- 교재/{$ARGUMENTS}/wikidocs/pages/{prereq_pp}-{prereq_ss}-{prereq_tt}-{선수토픽제목}.md

다음 토픽: {next_id} "{next_title}"

반드시 Rules/3, Rules/4를 읽고 준수하라.
```

**결과:** "Wrote {path}" (~100 tokens)

### ④ GIT COMMIT (inline)

```
git add "교재/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md"
git commit -m "write: {a.b.c} {토픽제목}"
```

### ⑤ EVALUATE — Agent "topic-evaluator" 호출

Agent 도구로 `topic-evaluator` agent를 호출한다. **fresh context에서 output만 평가.**

**prompt:**
```
토픽 {a.b.c} "{title}" 단원을 10점 기준으로 평가하라.

파일 경로: 교재/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md
curriculum.json 경로: 교재/{$ARGUMENTS}/curriculum.json

해당 토픽의 curriculum 메타데이터:
- learning_objectives: {objectives}
- learning_content: {keywords}
- prerequisites: {prereq IDs}

결과를 아래 포맷으로 반환하라:
SCORE: {N}/10
PASS: {항목번호들}
FAIL: {항목번호들}
DETAILS:
- item{N}: {구체적 사유}
```

**결과:** "SCORE: N/10, PASS: ..., FAIL: ..., DETAILS: ..." (~500 tokens)

### ⑥ DECIDE — 판정 및 분기 (inline)

evaluator 결과에서 SCORE를 파싱한다.

```
IF score == 10:
  → status = "pass"
  → 커밋 유지, 다음 토픽으로 진행

ELIF score >= 7:
  → status = "revise"
  → Agent "topic-reviser" 호출 (아래 참조)
  → 수정 후 git commit -m "revise: {a.b.c} round {N}"
  → Agent "topic-evaluator" 재호출 (fresh context에서 재평가)
  → 최대 3라운드까지 반복
  → 3라운드 후에도 10점 미달이면 현재 상태로 keep, 다음 토픽으로

ELSE (score <= 6):
  → status = "fail"
  → 파일 삭제
  → git reset HEAD~1 (커밋 취소)
  → ②RESEARCH부터 동일 토픽 완전 재작성 (1회만 재시도)
  → 재시도도 6점 이하면 skip, 다음 토픽으로
```

**reviser 호출 prompt:**
```
토픽 {a.b.c} "{title}" 단원의 FAIL 항목을 수정하라.

파일 경로: 교재/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md
findings 경로: 교재/{$ARGUMENTS}/._research/{a.b.c}_findings.md

evaluator 결과:
SCORE: {N}/10
FAIL: {항목번호들}
DETAILS:
- item{N}: {구체적 사유}

curriculum 메타데이터:
- learning_objectives: {objectives}
- learning_content: {keywords}

FAIL 항목만 targeted edit으로 수정하라. 전체를 재작성하지 마라.
```

### ⑥.5 TOC UPDATE (inline)

토픽 작성/수정 완료 후 `교재/{$ARGUMENTS}/wikidocs/TOC.md`를 curriculum.json 기반으로 재생성(rebuild)한다.
- 존재하는 페이지만 링크로 연결한다.
- 미작성 토픽은 제목만 표시한다 (링크 없음).

### ⑦ LOG — 결과 기록 (inline)

`교재/$ARGUMENTS/results.tsv`에 한 줄 추가:
```
{topic_id}\t{score}/10\t{attempt}\t{status}\t{issues}
```

- topic_id: 토픽 ID (예: 1.1.1)
- score: 획득 점수 (예: 10/10)
- attempt: 시도 횟수 (1, 2, 3...)
- status: pass / revise / fail / skip
- issues: FAIL 항목 요약 (PASS면 "-")

### ⑧ CLEANUP (inline)

```
rm 교재/{$ARGUMENTS}/._research/{a.b.c}_findings.md
```

### ⑨ REPEAT

- **절대 멈추지 않는다.**
- "계속할까요?" 묻지 않는다.
- 다음 미작성 토픽이 있으면 ①로 돌아간다.
- 에러가 발생하면 해당 토픽을 skip하고 다음으로 진행한다.

---

## FINISH — 전체 완료 시

모든 토픽이 작성되면:

1. **TOC.md 최종 rebuild**: curriculum.json 기반으로 전체 목차를 재생성한다.
2. **전체 pages/ 파일 존재 확인**: 모든 토픽에 대응하는 파일이 있는지 확인한다.
3. **누락 파일 경고**: 누락된 파일이 있으면 목록을 출력한다.
4. **진행 현황 출력**: Phase별, Section별 완료 상태 대시보드.

2. **results.tsv 요약 통계**:
   ```
   전체: {N}개 토픽
   pass (1회 통과): {A}개
   revise (수정 후 통과): {B}개
   fail → 재작성: {C}개
   skip: {D}개
   평균 점수: {avg}/10
   ```

3. **재작성 후보**: 점수가 낮은(8점 이하) 토픽 목록 제시.

4. **완료 알림**:
   ```
   ✓ 전체 초안 완료
   브랜치: autobook/{tag}
   results.tsv에서 상세 결과를 확인하세요.
   ```

---

## 핵심 원칙

1. **자율성**: 사용자 확인 없이 자동 진행. Rules/5의 "사용자 확인 후 다음 토픽" 규칙을 "자동 평가 후 자동 진행"으로 대체.
2. **품질 기준**: 10점 만점 자동 채점. 7점 이상이면 수정 후 진행, 6점 이하면 재작성.
3. **context 격리**: 리서치·작성·평가·수정을 각각 별도 subagent에서 실행. evaluator는 리서치 흔적이 없는 fresh context에서 평가.
4. **불변 규칙 준수**: Rules/1~4의 커리큘럼, 톤앤매너, 구조 규칙은 그대로 유지.
5. **중단 조건**: 사용자가 수동으로 중단할 때만 멈춘다. 에러 시 skip 후 계속.
6. **기록**: 모든 시도를 results.tsv에 기록하여 추적 가능하게 한다.
