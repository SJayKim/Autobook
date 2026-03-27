# /autobook 워크플로우 상세 정의

## 개요

`/autobook {책이름}`은 thin orchestrator + subagent 패턴의 자율 집필 루프다.
orchestrator(메인 context)는 메타데이터 관리만 하고, 4종 subagent에 무거운 작업을 위임한다.

```
Orchestrator (메인 skill)
  ├─ topic-researcher  (sonnet) — 논문+웹 리서치 → findings
  ├─ topic-writer      (opus)   — findings → .md 본문
  ├─ topic-evaluator   (sonnet) — .md → 10점 채점 (fresh context)
  └─ topic-reviser     (opus)   — FAIL 항목 targeted edit
```

---

## PHASE 1: SETUP (1회)

### Step 1.1 — 커리큘럼 확인

```
입력: 교재/{책이름}/curriculum.json
없으면 → "먼저 /curriculum {책이름}을 실행하세요." 출력 후 종료
있으면 → 로드
```

- curriculum.json에서 전체 Phase > Section > Topic 구조를 파싱한다.
- 전체 토픽 수(N)를 계산한다.

### Step 1.2 — 작성 완료 토픽 스캔

```
스캔 대상: 교재/{책이름}/wikidocs/pages/
매칭 패턴: {pp}-{ss}-{tt}-*.md
```

- pp(2자리 phase), ss(2자리 section), tt(2자리 topic) 접두사로 토픽 ID를 역파싱한다.
- 작성 완료 수(M)를 계산한다.

### Step 1.3 — Wikidocs 구조 확인/생성

```
IF 교재/{책이름}/wikidocs/ 없으면:
  mkdir wikidocs/
  mkdir wikidocs/pages/
  mkdir wikidocs/assets/
  생성:
    wikidocs/README.md         ← 책 소개 (title + Phase별 exit_capability)
    wikidocs/TOC.md            ← 목차 스켈레톤 (링크 선점)
    wikidocs/pages/00-들어가며.md  ← 도입 페이지
    wikidocs/pages/{pp}-{Phase제목}.md      ← Phase 개요 (N개)
    wikidocs/pages/{pp}-{ss}-{섹션제목}.md   ← 섹션 개요 (N개)
ELSE:
  그대로 사용
```

### Step 1.4 — 브랜치 및 로그 초기화

```
1. tag = 오늘 날짜 (예: mar27)
2. git checkout -b autobook/{tag}
3. 교재/{책이름}/results.tsv 초기화:
   topic	score	attempt	status	issues
4. mkdir 교재/{책이름}/._research/
5. .gitignore에 ._research/ 추가
6. stale ._research/ 파일 정리
```

### Step 1.5 — 셋업 요약 출력

```
AutoBook 시작 (Subagent 아키텍처)
책: {책이름}
전체 토픽: {N}개
작성 완료: {M}개
남은 토픽: {N-M}개
브랜치: autobook/{tag}
```

### Step 1.6 — 자율 루프 진입

사용자 확인 없이 즉시 LOOP 진입.

---

## PHASE 2: LOOP (토픽당 반복)

### 경로 공식

```
토픽 파일: 교재/{책이름}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md

  pp = phase id → 2자리 zero-pad    (1 → "01")
  ss = section의 두 번째 숫자 → 2자리  (1.2 → "02")
  tt = topic의 세 번째 숫자 → 2자리    (1.2.3 → "03")

findings: 교재/{책이름}/._research/{a.b.c}_findings.md
```

---

### Step 2.1 — SELECT (inline, ~2KB)

orchestrator가 직접 수행한다.

```
1. curriculum.json 토픽을 ID 순서(a.b.c 사전순)로 스캔
2. wikidocs/pages/에 {pp}-{ss}-{tt}-*.md 파일이 있으면 → SKIP
3. 첫 번째 미작성 토픽 선택
4. prerequisites 확인:
   - 선수 .md가 모두 wikidocs/pages/에 존재? → OK
   - 누락 선수 있으면 → 그 선수를 먼저 작성 대상으로 변경
5. 전체 완료이면 → FINISH로 이동
6. 메타데이터 추출:
   - topic_id, title, learning_objectives, learning_content, prerequisites
   - 선수 토픽 .md 경로 목록
   - 다음 토픽 정보 (ID, 제목)
   - 출력 파일 경로
```

**context 비용:** ~2KB (메타데이터만)

---

### Step 2.2 — RESEARCH (subagent: topic-researcher)

```
Agent 호출:
  subagent_type: topic-researcher
  model: sonnet

prompt 전달 내용:
  - 토픽 ID, 제목
  - 책이름
  - learning_content (키워드 배열)
  - learning_objectives (목표 배열)
  - prerequisites (선수 IDs)
  - 논문 기지 경로: C:/Users/cyon1/OneDrive/Desktop/agentic_ai_papers/
  - 출력 경로: 교재/{책이름}/._research/{a.b.c}_findings.md
```

**researcher 내부 프로세스:**

```
1. 논문 자료 검색 (항상 수행)
   1차: agent_memory_papers.md 인덱스 매칭
   2차: summaries/{NN}_{논문명}.md 요약 읽기
   3차: 원문 심층 조사 (Grep/PDF Read)

2. 웹 보완 (논문 자료가 얇은 경우)
   WebSearch + WebFetch로 공식 문서/스펙 조사

3. 교차 확인
   논문 ↔ 웹 자료 간 메커니즘 끊김 → 재검색

4. findings 파일 작성
   키워드별 조사 결과 + 선수 토픽 맥락 + 미충족 항목
```

**orchestrator가 받는 결과:** `"findings 작성 완료"` (~100 tokens)

---

### Step 2.3 — WRITE (subagent: topic-writer)

```
Agent 호출:
  subagent_type: topic-writer
  model: opus

prompt 전달 내용:
  - 토픽 ID, 제목, 책이름
  - findings 경로
  - 출력 경로 (wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md)
  - learning_objectives, learning_content, prerequisites
  - 선수 토픽 .md 파일 경로 목록
  - 다음 토픽 정보
```

**writer 내부 프로세스:**

```
1. 규칙 파일 읽기
   - Rules/3. 책 작성 톤앤 매너.md
   - Rules/4. 세부 개념 문서 작성 규칙.md

2. 자료 읽기
   - findings 파일 → 키워드별 조사 결과 파악
   - 선수 토픽 .md → 이미 설명된 개념 파악

3. 본문 작성
   포맷:
     # a.b.c 제목
     [도입] → [배경→선수개념→정의→메커니즘] → [코드/다이어그램] → 정리하면, ... → 다음 단원 안내
   문체:
     합니다체, 직선 따옴표, ## 금지, 배경 우선, AI체/출처 금지

4. 자가 점검 (저장 전)
   ☐ 새 굵은 용어 3개 이상 한 문단 집중 없는지
   ☐ 추상 정의 후 2문단 이내 구체 사례 있는지
   ☐ 3단계+ 프로세스에 ASCII 다이어그램/표 있는지
   ☐ 번역 투/명사화 검색 후 수정
   ☐ 80자 초과 문장 분리

5. 파일 저장 (mkdir -p 후 Write)
```

**orchestrator가 받는 결과:** `"Wrote {출력 경로}"` (~100 tokens)

---

### Step 2.4 — GIT COMMIT (inline)

orchestrator가 직접 수행한다.

```bash
git add "교재/{책이름}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md"
git commit -m "write: {a.b.c} {토픽제목}"
```

---

### Step 2.5 — EVALUATE (subagent: topic-evaluator)

```
Agent 호출:
  subagent_type: topic-evaluator
  model: sonnet

prompt 전달 내용:
  - 토픽 ID, 제목
  - .md 파일 경로
  - curriculum.json 경로
  - learning_objectives, learning_content, prerequisites
```

**evaluator 내부 프로세스 — 10점 채점:**

```
항목 1: 경로/파일명 규칙
  wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md 패턴 일치?
  제목이 curriculum.json title과 대응?

항목 2: learning_content 커버리지
  각 키워드를 Grep으로 본문 검색. 전 항목 반영 시 PASS.

항목 3: learning_objectives 검증 가능
  각 목표의 핵심 동사/개념이 본문에 존재?

항목 4: 선수 범위 준수
  선수 .md 파일 존재 확인 + 범위 밖 개념 참조 없음?

항목 5: 톤앤매너
  합니다체 통일, 곡선 따옴표 검출, AI체/출처 표기 검출

항목 6: 배경 우선 설명
  새 용어에 배경 문단 있는지, 정의 한 줄만 쓰고 넘어가지 않는지

항목 7: 본문 구조
  # a.b.c 제목, ## 금지, "정리하면," 존재, 다음 단원 안내

항목 8: 인지 부하 관리
  8a. 한 문단 한 개념
  8b. 새 굵은 용어 3개 미만/문단
  8c. 무관한 5줄+ 문단 없음

항목 9: 구체-추상 순서/시각 보조
  9a. 추상 정의 후 2문단 이내 구체 사례
  9b. 3단계+ 프로세스에 시각 보조 1개+

항목 10: 한국어 문장 품질
  10a. 번역 투 3건 미만
  10b. 명사화 남용 3건 미만
  10c. 80자 초과 문장 5건 미만
```

**evaluator 제약:** Read/Grep/Glob만 사용. Write/Edit/WebSearch 없음. fresh context.

**orchestrator가 받는 결과:**
```
SCORE: {N}/10
PASS: {항목번호들}
FAIL: {항목번호들}
DETAILS:
- item{N}: {구체적 사유, 줄 번호 포함}
```
(~500 tokens)

---

### Step 2.6 — DECIDE (inline)

orchestrator가 직접 판정한다.

```
┌─────────────────────────────────────────────────────┐
│                    SCORE 파싱                        │
├──────────┬──────────────────────────────────────────┤
│ 10점     │ status = "pass"                          │
│          │ 커밋 유지 → 다음 토픽                      │
├──────────┼──────────────────────────────────────────┤
│ 7~9점    │ status = "revise"                        │
│          │ ┌─ REVISE LOOP (최대 3라운드) ──────────┐ │
│          │ │ 1. topic-reviser 호출 (FAIL 항목만)    │ │
│          │ │ 2. git commit "revise: {a.b.c} R{N}"  │ │
│          │ │ 3. topic-evaluator 재호출 (fresh)      │ │
│          │ │ 4. 10점이면 → break                    │ │
│          │ │ 5. 3라운드 후 미달 → keep, 다음 토픽    │ │
│          │ └──────────────────────────────────────┘ │
├──────────┼──────────────────────────────────────────┤
│ 0~6점    │ status = "fail"                          │
│          │ 1. 파일 삭제                              │
│          │ 2. git reset HEAD~1 (커밋 취소)           │
│          │ 3. ② RESEARCH부터 완전 재작성 (1회만)     │
│          │ 4. 재시도도 6점 이하 → skip, 다음 토픽    │
└──────────┴──────────────────────────────────────────┘
```

**reviser 호출 시 prompt:**
```
파일 경로: wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md
findings 경로: ._research/{a.b.c}_findings.md
evaluator 결과: SCORE, FAIL 항목, DETAILS
curriculum 메타데이터: learning_objectives, learning_content
→ FAIL 항목만 targeted edit. 전체 재작성 금지.
```

**reviser 내부 프로세스:**
```
구조/톤 (항목 1,5,7) → 직접 수정
내용 (항목 2,3,6)     → findings 참조하여 보완
선수 범위 (항목 4)     → 범위 밖 개념 제거/대체
초보자 (항목 8,9,10)  → 문단 분리, 사례 추가, 문장 다듬기
```

---

### Step 2.7 — TOC UPDATE (inline)

```
교재/{책이름}/wikidocs/TOC.md를 curriculum.json 기반으로 rebuild

- 존재하는 페이지 → 링크 연결
- 미작성 토픽    → 제목만 표시 (링크 없음)
```

---

### Step 2.8 — LOG (inline)

```
교재/{책이름}/results.tsv에 한 줄 추가:

{topic_id}\t{score}/10\t{attempt}\t{status}\t{issues}

예: 1.2.3	10/10	1	pass	-
예: 2.1.1	8/10	2	revise	item5,item10
```

---

### Step 2.9 — CLEANUP (inline)

```bash
rm 교재/{책이름}/._research/{a.b.c}_findings.md
```

---

### Step 2.10 — REPEAT

```
다음 미작성 토픽이 있으면 → Step 2.1로
에러 발생 시 → 해당 토픽 skip, 다음 토픽으로
절대 멈추지 않는다. "계속할까요?" 묻지 않는다.
```

---

## PHASE 3: FINISH (전체 완료 시)

```
1. TOC.md 최종 rebuild
   curriculum.json 기반 전체 목차 재생성

2. pages/ 파일 존재 확인
   모든 토픽에 대응하는 파일 있는지 검증

3. 누락 파일 경고
   누락 있으면 목록 출력

4. 진행 현황 대시보드
   Phase별, Section별 완료 상태

5. results.tsv 요약 통계
   전체: {N}개 토픽
   pass (1회 통과): {A}개
   revise (수정 후 통과): {B}개
   fail → 재작성: {C}개
   skip: {D}개
   평균 점수: {avg}/10

6. 재작성 후보
   8점 이하 토픽 목록

7. 완료 알림
   ✓ 전체 초안 완료
   브랜치: autobook/{tag}
   results.tsv에서 상세 결과를 확인하세요.
```

---

## 토픽 1개의 전체 흐름 요약

```
orchestrator          researcher(sonnet)    writer(opus)     evaluator(sonnet)    reviser(opus)
     │                      │                   │                  │                   │
     ├─ SELECT ────────────►│                   │                  │                   │
     │  (inline ~2KB)       │                   │                  │                   │
     │                      │                   │                  │                   │
     ├─ RESEARCH ──────────►│                   │                  │                   │
     │                      ├─ 논문 검색         │                  │                   │
     │                      ├─ 웹 보완           │                  │                   │
     │                      ├─ findings 작성     │                  │                   │
     │◄─ "완료" ────────────┤                   │                  │                   │
     │                      │                   │                  │                   │
     ├─ WRITE ─────────────►├──────────────────►│                  │                   │
     │                      │                   ├─ Rules 읽기      │                   │
     │                      │                   ├─ findings 읽기   │                   │
     │                      │                   ├─ 선수 .md 읽기   │                   │
     │                      │                   ├─ 본문 작성       │                   │
     │                      │                   ├─ 자가 점검       │                   │
     │◄─ "Wrote {path}" ───►├──────────────────┤                  │                   │
     │                      │                   │                  │                   │
     ├─ GIT COMMIT ─────────┤ (inline)          │                  │                   │
     │                      │                   │                  │                   │
     ├─ EVALUATE ──────────►├──────────────────►├─────────────────►│                   │
     │                      │                   │                  ├─ 10항목 채점       │
     │◄─ "SCORE: N/10" ────►├──────────────────►├─────────────────┤                   │
     │                      │                   │                  │                   │
     ├─ DECIDE ─────────────┤ (inline)          │                  │                   │
     │  10점 → pass         │                   │                  │                   │
     │  7~9점 → revise ────►├──────────────────►├─────────────────►├──────────────────►│
     │                      │                   │                  │                   ├─ targeted edit
     │◄─────────────────────┤                   │                  │                   │
     │  ≤6점 → fail/retry   │                   │                  │                   │
     │                      │                   │                  │                   │
     ├─ TOC UPDATE ─────────┤ (inline)          │                  │                   │
     ├─ LOG ────────────────┤ (inline)          │                  │                   │
     ├─ CLEANUP ────────────┤ (inline)          │                  │                   │
     ├─ REPEAT → Step 2.1   │                   │                  │                   │
     ▼                      ▼                   ▼                  ▼                   ▼
```

---

## 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| 자율성 | 사용자 확인 없이 자동 진행. 에러 시 skip 후 계속. |
| context 격리 | 4종 subagent가 각자의 context에서 실행. evaluator는 리서치 흔적 없는 fresh context. |
| 품질 기준 | 10점 만점 자동 채점. 7+ 수정, ≤6 재작성. |
| 불변 규칙 | Rules/1~4는 수정 불가 (hook으로 보호). |
| 기록 | 모든 시도를 results.tsv에 기록. |
| 중단 조건 | 사용자 수동 중단만. |

---

## 관련 파일 목록

| 파일 | 역할 |
|------|------|
| `.claude/skills/autobook/SKILL.md` | orchestrator 스킬 정의 |
| `.claude/agents/topic-researcher.md` | 리서치 에이전트 (sonnet) |
| `.claude/agents/topic-writer.md` | 작성 에이전트 (opus) |
| `.claude/agents/topic-evaluator.md` | 평가 에이전트 (sonnet) |
| `.claude/agents/topic-reviser.md` | 수정 에이전트 (opus) |
| `.claude/rules/topic-writing.md` | 교재 .md 편집 시 자동 리마인더 |
| `.claude/settings.json` | hook 설정 (Rules/ 보호) |
| `Rules/3. 책 작성 톤앤 매너.md` | 문체 규칙 |
| `Rules/4. 세부 개념 문서 작성 규칙.md` | 구조 규칙 |
