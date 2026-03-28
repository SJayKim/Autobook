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

## 모드 선언

이 스킬은 **자율 모드**로 동작한다. Rules/5 "사람-AI 협업 절차"와의 관계:

| Rules/5 조항 | 수동 모드 (write-topic) | 자율 모드 (autobook) |
|-------------|----------------------|---------------------|
| §2.3 한 파일씩만 | 준수 | 준수 (1 토픽/루프 반복) |
| §2.4 사용자 독해 | 사용자 직접 확인 | topic-evaluator 자동 채점으로 대체 |
| §2.5 피드백→보강 | 사용자 피드백 | FAIL 항목 → topic-reviser 자동 수정 |
| §2.6 다음 진행 조건 | 사용자 명시적 확인 | SCORE ≥ 7 → 자동 진행 |
| §2.7 Rules 준수 점검 | 준수 | 준수 (evaluator 10항목에 포함) |

Rules/1~4의 톤앤매너, 구조, 커리큘럼 규칙은 **모드 무관하게 완전 준수**한다.

---

## SETUP (1회)

### 1. 커리큘럼 확인

1. `02_Books/$ARGUMENTS/curriculum.json` 파일을 찾는다.
2. 없으면 → `/curriculum $ARGUMENTS` 스킬을 자동 실행하여 커리큘럼을 생성한다. (멈추지 않는다)
3. 있으면 → 로드하여 전체 Phase, Section, Topic 구조를 파악한다.
4. `02_Books/$ARGUMENTS/wikidocs/pages/`에서 `{pp}-{ss}-{tt}-*.md` 패턴으로 작성된 토픽 파일 수를 계산한다.

### 2. Wikidocs 구조 확인

1. `02_Books/$ARGUMENTS/wikidocs/pages/` 디렉토리가 존재하는지 확인한다.
2. **존재하면:** 그대로 사용. 기존 파일을 덮어쓰지 않는다.
3. **존재하지 않으면:** `/curriculum` 스킬의 4.5단계와 동일한 구조를 생성한다:
   - `wikidocs/pages/`, `wikidocs/assets/` 디렉토리 생성
   - README.md, TOC.md 스켈레톤 생성
   - Phase/섹션 개요 페이지, `00-들어가며.md` 생성
4. 이미 일부만 존재하는 경우 (예: pages/는 있지만 README.md가 없는 경우):
   - 누락된 파일만 보완 생성한다. 기존 파일은 건드리지 않는다.

### 3. 브랜치 및 로그 초기화

1. 오늘 날짜 기반 태그 생성 (예: `mar27`).
2. `git checkout -b autobook/{tag}` 실행.
3. `02_Books/$ARGUMENTS/results.tsv` 초기화:
   ```
   topic	score	attempt	status	issues
   ```
4. `02_Books/$ARGUMENTS/._research/` 디렉토리 생성.
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
토픽 파일: 02_Books/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md
  pp = phase id를 2자리 zero-pad (예: "1" → "01")
  ss = section id의 두 번째 숫자를 2자리 zero-pad (예: "1.2" → "02")
  tt = topic id의 세 번째 숫자를 2자리 zero-pad (예: "1.2.3" → "03")
```

### ① SELECT — 다음 토픽 선택 (inline, ~2KB)

1. curriculum.json에서 토픽을 ID 순서(a.b.c 사전순)로 스캔한다.
2. `wikidocs/pages/`에서 이미 대응하는 `{pp}-{ss}-{tt}-*.md` 파일이 있는 토픽은 건너뛴다.
3. 첫 번째 미작성 토픽을 선택한다.
4. 선수 토픽 검증:
   a. 각 prerequisite의 `.md` 파일이 `wikidocs/pages/`에 존재하는지 확인한다.
   b. results.tsv가 존재하면, 각 prerequisite의 최종 status를 확인한다:
      - "pass" 또는 "revise": 정상 진행
      - "skip": 경고 출력 ("선수 토픽 {id}이(가) skip 상태입니다. 품질 저하 가능성이 있습니다.")
        → 경고만 출력하고 진행은 허용 (skip 토픽의 파일이 존재하지 않으므로 자동 보류됨)
      - results.tsv에 없음: 수동 작성된 것으로 간주, 정상 진행
   c. 누락된 선수가 있으면: 해당 선수를 먼저 작성 대상으로 변경.
5. 모든 토픽이 작성 완료이면 → **FINISH** 단계로 이동.
6. 해당 토픽의 메타데이터를 추출한다:
   - `topic_id`, `title`, `learning_objectives`, `learning_content`, `prerequisites`
   - 선수 토픽 .md 파일 경로 목록 (`wikidocs/pages/{pp}-{ss}-{tt}-*.md`)
   - 다음 토픽 정보 (ID, 제목)
   - 출력 파일 경로: `02_Books/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md`

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
출력 경로: 02_Books/{$ARGUMENTS}/._research/{a.b.c}_findings.md

위 출력 경로에 findings 파일을 작성하라.
```

**결과:** "findings 작성 완료" (~100 tokens)

### ③ WRITE — Agent "topic-writer" 호출

Agent 도구로 `topic-writer` agent를 호출한다.

**prompt:**
```
토픽 {a.b.c} "{title}" 단원을 작성하라.

책이름: {$ARGUMENTS}
findings 경로: 02_Books/{$ARGUMENTS}/._research/{a.b.c}_findings.md
출력 경로: 02_Books/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md

curriculum 메타데이터:
- learning_objectives: {objectives}
- learning_content: {keywords}
- prerequisites: {prereq IDs}

선수 토픽 파일:
- 02_Books/{$ARGUMENTS}/wikidocs/pages/{prereq_pp}-{prereq_ss}-{prereq_tt}-{선수토픽제목}.md

다음 토픽: {next_id} "{next_title}"

반드시 Rules/3, Rules/4를 읽고 준수하라.
```

**결과:** "Wrote {path}" 또는 "Wrote {path} (INCOMPLETE: {키워드})" (~100 tokens)

### ③-1. INCOMPLETE 감지 (inline)

WRITE 결과에서 "INCOMPLETE"를 감지한다.

INCOMPLETE이면:
1. 누락 키워드를 파싱한다.
2. topic-researcher를 해당 키워드 한정으로 재호출한다.
   prompt에 "보강 조사: {누락 키워드만}"을 명시한다.
3. 보강 findings를 기존 findings에 append한다.
4. topic-reviser를 호출하여 INCOMPLETE 부분만 보완한다.
5. INCOMPLETE 마커를 제거한다.

INCOMPLETE가 아니면 ④로 진행한다.

### ④ GIT COMMIT (inline)

```
git add "02_Books/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md"
git commit -m "write: {a.b.c} {토픽제목}"
```

### ⑤ EVALUATE — Agent "topic-evaluator" 호출

Agent 도구로 `topic-evaluator` agent를 호출한다. **fresh context에서 output만 평가.**

**prompt:**
```
토픽 {a.b.c} "{title}" 단원을 10점 기준으로 평가하라.

파일 경로: 02_Books/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md
curriculum.json 경로: 02_Books/{$ARGUMENTS}/curriculum.json

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
  → 재시도도 6점 이하면:
    → status = "skip"
    → 파일 삭제, git reset HEAD~1
    → 연쇄 영향 분석:
      1. curriculum.json에서 이 토픽을 prerequisites에 포함하는 토픽 목록을 추출한다.
      2. 해당 목록을 results.tsv에 WARNING 행으로 기록:
         `{topic_id}\t-\t-\tskip_warning\t선수 {skipped_id} skip으로 영향받는 토픽: {list}`
      3. 누적 skip 수를 카운트한다.
      4. 누적 skip >= 3이면:
         → "연속 skip이 3건 이상 발생했습니다. 계속 진행할까요?" 사용자 확인 요청
         → 사용자가 계속을 선택하면 루프 재개
    → 다음 토픽으로 (skip된 토픽의 후속 토픽은 prerequisite 검증에서 자동 보류)
```

**reviser 호출 prompt:**
```
토픽 {a.b.c} "{title}" 단원의 FAIL 항목을 수정하라.

파일 경로: 02_Books/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md
findings 경로: 02_Books/{$ARGUMENTS}/._research/{a.b.c}_findings.md

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

### ⑥.5 TOC UPDATE (조건부)

TOC 재빌드는 아래 조건에서만 수행한다:
1. 현재 토픽이 해당 Phase의 **마지막 토픽**인 경우 (Phase 완료 시점)
2. 현재 토픽이 전체 커리큘럼의 **마지막 토픽**인 경우
3. 누적 10개 토픽마다 (10, 20, 30... 번째 토픽)

그 외에는 TOC 재빌드를 건너뛴다. FINISH 단계에서 최종 재빌드를 수행하므로 누락 없음.

재빌드 시:
- `02_Books/{$ARGUMENTS}/wikidocs/TOC.md`를 curriculum.json 기반으로 재생성한다.
- 존재하는 페이지만 링크로 연결한다.
- 미작성 토픽은 제목만 표시한다 (링크 없음).

### ⑦ LOG — 결과 기록 (inline)

`02_Books/$ARGUMENTS/results.tsv`에 한 줄 추가:
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
rm 02_Books/{$ARGUMENTS}/._research/{a.b.c}_findings.md
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
