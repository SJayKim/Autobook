# AutoBook 개선 계획

두 가지 독립적 개선 축을 하나의 실행 계획으로 통합한 문서이다.

- **축 A — 초보자 친화적 평가기준 확장**: 7점 → 10점 체계 전환, 인지 부하·구체-추상 순서·한국어 문장 품질 항목 추가
- **축 B — Subagent 아키텍처 전환**: 모놀리식 context → orchestrator + subagent 패턴으로 전환하여 context 오염 방지 및 50+ 토픽 연속 작성 가능

두 축은 의존 관계가 있다: 축 B의 evaluator agent는 축 A의 10점 채점 기준을 사용해야 하므로, **축 A를 먼저 확정한 뒤 축 B를 구현**한다.

---

# Part A: 초보자 친화적 평가기준 통합

## A.1 Context

현재 autobook 워크플로우의 평가 체계는 7점 만점(7항목)으로, 구조·커버리지·톤앤매너 중심이다. `docs/improvement_plan/beginner_friendly_technical_writing_research.md`에 정리된 교육학·인지과학 연구 결과(파인만 기법, 인지 부하 이론, CPA, 이중 코딩, 한국어 문장 품질 등)를 평가기준으로 통합하여 **초보자가 실제로 이해할 수 있는 글인지**를 검증하는 체계로 확장한다.

기존 7항목과 겹치지 않으면서, LLM이 자동 채점 가능한 수준으로 구체화한 **3개 신규 항목**을 추가하여 10점 만점 체계로 전환한다.

---

## A.2 신규 평가 항목 (항목 8–10)

### 항목 8: 인지 부하 관리

| 서브체크 | 기준 | 검증 방법 |
|----------|------|-----------|
| 8a. 한 문단 한 개념 | 한 문단에 무관한 두 개념이 섞이면 FAIL | 문단별 읽기 → 개념 단일성 판정 |
| 8b. 새 용어 밀도 | 한 문단에 새 굵은 용어(`**term**`) 3개 이상이 충분한 설명 없이 등장하면 FAIL | 문단별 `**...**` 패턴 카운트 |
| 8c. 학습 목표 외 탈선 없음 | 5줄 이상 문단이 learning_content 어떤 항목과도 무관하고 구조적 역할(도입/전환/정리)도 아니면 FAIL | learning_content 키워드 매칭 |

**근거**: 인지 부하 이론(청킹), 메이어 일관성 원칙, 유혹적 세부사항 배제

### 항목 9: 구체-추상 순서와 시각 보조

| 서브체크 | 기준 | 검증 방법 |
|----------|------|-----------|
| 9a. 구체 사례 선행 | 추상적 정의/매커니즘에 구체 사례(코드, 시나리오, 수치)가 2문단 이내에 동반되지 않으면 FAIL | 정의 패턴("~은/는 ~입니다") 식별 → 인근 코드블록/사례 확인 |
| 9b. 핵심 프로세스 시각 보조 | 3단계 이상 프로세스 서술 시 시각 보조(ASCII 다이어그램, 표, 코드블록) 최소 1개 없으면 FAIL | 단계 패턴 검출 → 코드펜스/테이블 존재 확인 |

**근거**: CPA(구체→추상), 이중 코딩 이론, 메이어 공간 인접성 원칙

### 항목 10: 한국어 문장 품질

| 서브체크 | 기준 | 검증 방법 |
|----------|------|-----------|
| 10a. 번역 투 | "~에 의해 수행되는", "~하는 것이 가능하다", "~에 대한 ~에 대한" 등 3건 이상이면 FAIL | Grep 정규식 |
| 10b. 명사화 남용 | "처리를 수행한다", "확인을 진행한다" 등 `을/를 (수행\|진행\|실시\|실행)` 3건 이상이면 FAIL | Grep 정규식 |
| 10c. 장문 | 마침표 없이 80자 초과 문장 5건 이상이면 FAIL | 문장 분리 → 길이 측정 |

**근거**: 카카오엔터프라이즈 테크니컬 라이팅 지침, 한국어 문장 품질 연구

---

## A.3 점수 체계 변경

| 항목 | 기존 | 변경 |
|------|------|------|
| 총점 | 7점 | **10점** |
| pass | == 7 (100%) | == **10** (100%) |
| revise 임계 | >= 5 (71%) | >= **7** (70%) |
| fail 임계 | <= 4 (57%) | <= **6** (60%) |
| 재작성 후보 | 6점 이하 | **8점 이하** |
| results.tsv | `{score}/7` | `{score}/10` |

---

## A.4 파일별 수정 명세

### 파일 A: `.claude/skills/autobook/SKILL.md`

**수정 1 — ③ EVALUATE 섹션 (line 114~153)**
- 기존 항목 1~7 유지
- 항목 7 뒤에 항목 8, 9, 10 추가 (위 정의 그대로)
- 점수 산출 공식: `총점 = 항목1 + ... + 항목10 (0~10점)`

**수정 2 — ④ DECIDE 섹션 (line 155~176)**
- `score == 7` → `score == 10`
- `score >= 5` → `score >= 7`
- `score <= 4` → `score <= 6`

**수정 3 — ⑤ LOG 섹션 (line 183)**
- `{score}/7` → `{score}/10`

**수정 4 — FINISH 섹션 (line 206~217)**
- `평균 점수: {avg}/7` → `{avg}/10`
- `6점 이하` → `8점 이하`

**수정 5 — 핵심 원칙 (line 231)**
- `7점 만점` → `10점 만점`
- `5점 이상이면 수정 후 진행, 4점 이하면 재작성` → `7점 이상이면 수정 후 진행, 6점 이하면 재작성`

### 파일 B: `.claude/skills/review-topic/SKILL.md`

**수정 1 — 섹션 제목 (line 20)**
- `7항목 체크리스트` → `10항목 체크리스트`

**수정 2 — 항목 7 뒤에 항목 8, 9, 10 추가** (autobook과 동일 정의)

**수정 3 — 리포트 테이블 (line 70~79)**
- 행 3개 추가:
  ```
  | 8 | 인지 부하 관리 | PASS/FAIL | ... |
  | 9 | 구체-추상 순서/시각 보조 | PASS/FAIL | ... |
  | 10 | 한국어 문장 품질 | PASS/FAIL | ... |
  ```

### 파일 C: `.claude/skills/write-topic/SKILL.md`

**수정 1 — 3단계 본문 작성, 포맷 블록 뒤 (line 65 이후)**

"초보자 친화적 작성 원칙" 가이드 블록 추가:
```
**초보자 친화적 작성 원칙:**
- 한 문단에 한 개념만 담는다. 새 개념이 등장하면 문단을 나눈다.
- 구체 사례를 먼저, 추상 원리를 나중에 배치한다.
- 3단계 이상 프로세스에는 시각 보조(ASCII 다이어그램, 표)를 넣는다.
- 한 문단에 새 굵은 용어를 3개 이상 쏟아붓지 않는다.
- 번역 투를 피한다. ("~에 의해 수행되는" → "~가 수행하는")
- 명사화 남용을 피한다. ("처리를 수행한다" → "처리한다")
- 문장을 짧게 유지한다. 80자 초과 시 분리를 고려한다.
- learning_content와 무관한 탈선을 피한다.
```

**수정 2 — 4단계 자동 체크리스트 (line 86 이후)**

체크리스트 3개 추가:
```
- [ ] 한 문단에 한 개념만 다루고, 새 용어를 3개 이상 한꺼번에 도입하지 않았는가
- [ ] 추상적 정의마다 구체 사례가 2문단 이내에 동반되고, 복잡한 프로세스에 시각 보조가 있는가
- [ ] 번역 투·명사화 남용·80자 초과 장문이 과도하지 않은가
```

### 파일 D: `.claude/rules/topic-writing.md`

**수정 — 기존 3번 항목과 4번 항목 사이에 새 항목 삽입**

기존 `4. **파일 경로**`를 `5. **파일 경로**`로 번호 변경하고, 새 4번 추가:
```
4. **초보자 친화성**:
   - 한 문단에 한 개념, 새 굵은 용어 3개 이상 동시 도입 금지
   - 추상 정의 전후 2문단 이내에 구체 사례(코드, 시나리오, 수치) 배치
   - 3단계 이상 프로세스에 시각 보조(ASCII 다이어그램, 표) 필수
   - 번역 투("~에 의해", "~것이 가능하다"), 명사화 남용("처리를 수행") 지양
   - 장문(80자 초과) 지양, 의식적으로 분리
```

---

## A.5 의도적으로 제외한 연구 항목

| 연구 항목 | 제외 이유 |
|-----------|-----------|
| 파인만 기법 | 항목 6(배경 우선) + 항목 8(인지 부하)에 이미 포함 |
| 스캐폴딩/ZPD | 항목 4(선수 범위) + 커리큘럼 선수 체계로 이미 구현 |
| 메이어 12원칙 | 적용 가능한 것(일관성, 인접성)은 항목 8, 9에 반영. 나머지는 멀티미디어 전용 |
| SUCCESs 프레임워크 | Unexpected/Emotional/Stories는 이진 판정 불가. write-topic 가이드로만 참조 |
| 비유 품질 | 주관적 판단. 모든 토픽에 비유가 필수는 아님 |
| 역피라미드/주제문 | 항목 7(본문 구조) + 기존 포맷 템플릿으로 부분 커버 |
| 점진적 공개 | 커리큘럼 시스템 자체가 이미 점진적 공개 구조 |

---

# Part B: Subagent 아키텍처 전환

## B.1 Context

현재 `/autobook`, `/write-topic`, `/curriculum` 스킬은 모놀리식 구조로, 리서치·작성·평가를 모두 하나의 context window에서 수행한다. 토픽 하나당 100~300KB의 context가 누적되어, `/autobook` 루프에서 3~5개 토픽 이후 품질이 저하된다. Subagent를 활용하면 각 단계를 격리된 context에서 실행하여 오염을 방지하고, orchestrator의 context를 토픽당 ~3-4KB로 유지할 수 있다.

---

## B.2 아키텍처 변경

**현재 (모놀리식):**
```
/autobook → [SELECT → RESEARCH → WRITE → EVALUATE → DECIDE → LOG] 전부 한 context
```

**변경 후 (orchestrator + subagent):**
```
/autobook (thin orchestrator) →
  ① SELECT (inline, 경량)
  ② Agent: researcher → findings 파일 작성
  ③ Agent: writer → .md 파일 작성
  ④ Agent: evaluator → 점수 반환 (fresh context, 리서치 흔적 없음)
  ⑤ DECIDE + LOG (inline)
  ⑥ If revise → Agent: reviser → 파일 패치
  ⑦ CLEANUP → findings 삭제
  ⑧ REPEAT
```

**핵심 원리:** "context isolation is the #1 lever" — evaluator가 리서치 과정을 보면 동의 편향이 생긴다. Fresh context로 output만 평가해야 객관적이다.

---

## B.3 파일 구조

### 신규 생성
```
.claude/agents/
  topic-researcher.md      ← 3-tier 논문 리서치 + 웹 보완
  topic-writer.md          ← findings → .md 작성
  topic-evaluator.md       ← 10점 채점 (read-only, fresh context)
  topic-reviser.md         ← FAIL 항목만 수정
  curriculum-researcher.md ← 커리큘럼용 웹 리서치
```

### 수정 대상
```
.claude/skills/autobook/SKILL.md       ← thin orchestrator로 리팩터
.claude/skills/write-topic/SKILL.md    ← 같은 subagent 활용
.claude/skills/curriculum/SKILL.md     ← curriculum-researcher 활용
```

### 변경 없음
```
.claude/skills/next-topic/SKILL.md        ← read-only, 저용량
.claude/skills/review-topic/SKILL.md      ← read-only, 저용량
.claude/skills/validate-curriculum/SKILL.md
.claude/skills/progress/SKILL.md
```

### 임시 파일 (자동 생성/삭제)
```
교재/{책이름}/._research/              ← .gitignore에 추가
  {a.b.c}_findings.md                 ← researcher → writer 핸드오프
  curriculum_research.md               ← curriculum-researcher 핸드오프
```

---

## B.4 Agent 정의 상세

### 1. topic-researcher.md

| 항목 | 값 |
|------|-----|
| model | sonnet (정보 검색/요약, Opus 불필요) |
| color | cyan |
| tools | Read, Grep, Glob, Bash, WebSearch, WebFetch |

**입력 (prompt):** 토픽 ID, learning_content 키워드, learning_objectives, 책이름

**프로세스:**
1. `C:/Users/cyon1/OneDrive/Desktop/agentic_ai_papers/agent_memory_papers.md` 인덱스 매칭
2. `summaries/{NN}_{논문명}.md` 요약 읽기
3. 부족하면 `summaries/agent_memory_pdfs/` 텍스트 추출본 Grep
4. 논문으로 부족한 항목만 WebSearch + WebFetch
5. 결과를 `교재/{책}/._research/{a.b.c}_findings.md`에 구조화 저장

**출력 파일 포맷:**
```markdown
# Research Findings: {a.b.c} {title}

## 키워드별 조사 결과
### {keyword_1}
- 핵심 메커니즘: ...
- 논문 출처: {논문명} - {구체적 내용}
- 웹 보완: {공식 문서 내용}

### {keyword_2}
...

## 선수 토픽 맥락
- {prereq_id}: {한 줄 요약}

## 미충족 항목
- {커버리지 부족 키워드}
```

**Orchestrator context 비용:** ~100 tokens (vs 현재 ~100KB)

---

### 2. topic-writer.md

| 항목 | 값 |
|------|-----|
| model | opus (작성 품질이 핵심 산출물) |
| color | green |
| tools | Read, Write, Glob, Bash |

**입력 (prompt):** 토픽 ID, 책이름, findings 파일 경로, 선수 토픽 .md 경로 목록, 다음 토픽 정보, curriculum 메타데이터

**프로세스:**
1. `Rules/3. 책 작성 톤앤 매너.md`, `Rules/4. 세부 개념 문서 작성 규칙.md` 읽기
2. findings 파일 읽기
3. 선수 토픽 .md 파일 읽기 (이미 설명된 개념 파악)
4. 본문 작성 → 올바른 경로에 Write
5. 디렉토리 없으면 `mkdir -p`

**WebSearch/WebFetch 없음** — 추가 리서치를 차단하여 context 오염 방지. 모든 자료는 findings에 이미 있어야 한다.

**Orchestrator context 비용:** ~100 tokens (vs 현재 ~200KB)

---

### 3. topic-evaluator.md

| 항목 | 값 |
|------|-----|
| model | sonnet (패턴 매칭 + 체크리스트, Opus 불필요) |
| color | yellow |
| tools | Read, Grep, Glob |

**입력 (prompt):** 토픽 ID, 책이름, .md 파일 경로, curriculum 토픽 메타데이터

**프로세스:** 10점 채점 (Part A의 항목 1~10)

**핵심 설계:** Write/Edit/WebSearch/WebFetch 접근 없음. findings 파일 경로도 모름. 리서치 과정의 흔적이 전혀 없는 fresh context에서 output만 평가.

**10점 채점 기준:**

| 항목 | 검증 내용 |
|------|----------|
| 1. 경로/파일명 | `{a}_{Phase}/{a.b}_{섹션}/{a.b.c}_{토픽}.md` 패턴 일치, curriculum.json title 대응 |
| 2. learning_content 커버리지 | 각 키워드를 Grep으로 본문 검색. 전 항목 반영 시 PASS |
| 3. learning_objectives 검증 | 각 목표의 핵심 동사/개념이 본문에 존재, 본문만으로 달성 가능 |
| 4. 선수 범위 준수 | prerequisites .md 존재 확인, 선수 밖 개념 미참조 |
| 5. 톤앤매너 | 합니다체 통일, 곡선 따옴표 없음, AI체 패턴 없음, 출처/원서 표기 없음 |
| 6. 배경 우선 설명 | 새 용어에 정의 전 배경 문단 존재, 정의 한 줄 후 넘어감 없음 |
| 7. 본문 구조 | `# a.b.c 제목` 존재, `##` 이하 없음, "정리하면," 존재, 다음 단원 안내 |
| 8. 인지 부하 관리 | 한 문단 한 개념, 용어 밀도, 탈선 없음 |
| 9. 구체-추상 순서/시각 보조 | 구체 사례 선행, 프로세스 시각 보조 |
| 10. 한국어 문장 품질 | 번역 투, 명사화 남용, 장문 |

**출력 포맷 (text로 반환):**
```
SCORE: {N}/10
PASS: 1,2,4,5,8
FAIL: 3,6,10
DETAILS:
- item3: "X할 수 있다" 목표에 대응하는 설명이 본문에 부족
- item6: "RAG" 용어가 42행에서 배경 없이 등장
- item10: 번역 투 4건 검출 ("~에 의해" 2건, "~것이 가능하다" 2건)
```

**Orchestrator context 비용:** ~200-500 tokens

---

### 4. topic-reviser.md

| 항목 | 값 |
|------|-----|
| model | opus (기존 글의 흐름을 유지하면서 수정) |
| color | magenta |
| tools | Read, Edit, Grep, Glob |

**입력 (prompt):** 토픽 ID, .md 경로, evaluator의 FAIL 항목 + DETAILS, curriculum 메타데이터, findings 경로 (내용 보완 필요시만)

**프로세스:**
1. .md 파일 읽기
2. FAIL 항목별 targeted edit
3. 구조/톤 문제 (항목 1,5,7) → 직접 수정
4. 내용 문제 (항목 2,3,6) → findings 참조하여 보완

---

### 5. curriculum-researcher.md

| 항목 | 값 |
|------|-----|
| model | sonnet |
| color | cyan |
| tools | Read, WebSearch, WebFetch, Bash |

**입력 (prompt):** 책 주제/범위

**프로세스:** 현재 curriculum SKILL.md의 웹 조사 단계 (≥10개 주요 문서)를 격리 수행

**출력:** `교재/{책}/._research/curriculum_research.md`에 atomic concept 목록, 관계, 커버리지 갭 저장

---

## B.5 Orchestrator 리팩터 설계

### /autobook SKILL.md

#### SETUP (기존과 동일)
커리큘럼 확인, 브랜치 생성, results.tsv 초기화, `._research/` 디렉토리 생성 + `.gitignore`에 추가

#### LOOP (orchestrator 패턴)

```
① SELECT (inline)
   - curriculum.json 스캔, 첫 미작성 토픽 선택
   - 선수 확인
   - Context: ~2KB

② RESEARCH (Agent 호출)
   - Agent "topic-researcher" 호출
   - prompt에 토픽 메타데이터 전달
   - 결과: "findings 작성 완료" (~100 tokens)

③ WRITE (Agent 호출)
   - Agent "topic-writer" 호출
   - prompt에 findings 경로 + 토픽 메타데이터 전달
   - 결과: "Wrote {path}" (~100 tokens)

④ GIT COMMIT (inline)
   - git add + git commit -m "write: {a.b.c} {title}"

⑤ EVALUATE (Agent 호출)
   - Agent "topic-evaluator" 호출
   - prompt에 .md 경로 + 토픽 메타데이터 전달
   - 결과: "SCORE: N/10, FAIL: ..., DETAILS: ..." (~500 tokens)

⑥ DECIDE (inline)
   - score 파싱 → pass/revise/fail 분기
   - revise → Agent "topic-reviser" 호출 후 재평가 (최대 3라운드)
   - fail → 파일 삭제, git reset, 재시도 1회

⑦ LOG (inline)
   - results.tsv에 기록

⑧ CLEANUP (inline)
   - rm 교재/{책}/._research/{a.b.c}_findings.md

⑨ REPEAT
```

**Orchestrator context 예산:** 토픽당 ~3-4KB → 50+ 토픽 가능 (현재 3-5개에서 품질 저하)

#### Orchestrator가 Agent에 전달하는 prompt 템플릿

**researcher 호출 예시:**
```
토픽 {a.b.c} "{title}" 리서치를 수행하라.

책이름: {book}
learning_content: {keywords 배열}
learning_objectives: {objectives 배열}
prerequisites: {prereq IDs}

논문 기지: C:/Users/cyon1/OneDrive/Desktop/agentic_ai_papers/
출력 경로: 교재/{book}/._research/{a.b.c}_findings.md

위 출력 경로에 findings 파일을 작성하라.
```

**writer 호출 예시:**
```
토픽 {a.b.c} "{title}" 단원을 작성하라.

책이름: {book}
findings 경로: 교재/{book}/._research/{a.b.c}_findings.md
출력 경로: 교재/{book}/{a}_{phase}/{a.b}_{section}/{a.b.c}_{title}.md

curriculum 메타데이터:
- learning_objectives: {objectives}
- learning_content: {keywords}
- prerequisites: {prereq IDs}

선수 토픽 파일:
- 교재/{book}/{path_to_prereq_1}.md
- 교재/{book}/{path_to_prereq_2}.md

다음 토픽: {next_id} "{next_title}"

반드시 Rules/3, Rules/4를 읽고 준수하라.
```

**evaluator 호출 예시:**
```
토픽 {a.b.c} "{title}" 단원을 10점 기준으로 평가하라.

파일 경로: 교재/{book}/{a}_{phase}/{a.b}_{section}/{a.b.c}_{title}.md
curriculum.json 경로: 교재/{book}/curriculum.json

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

**reviser 호출 예시:**
```
토픽 {a.b.c} "{title}" 단원의 FAIL 항목을 수정하라.

파일 경로: 교재/{book}/{path}.md
findings 경로: 교재/{book}/._research/{a.b.c}_findings.md

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

---

### /write-topic SKILL.md

동일한 subagent 패턴이지만 사용자 인터랙션 유지:
1. 토픽 확정 (기존 1단계)
2. Agent "topic-researcher" 호출
3. Agent "topic-writer" 호출
4. Agent "topic-evaluator" 호출 (자동 체크)
5. 사용자에게 전달 + 피드백 대기
6. 피드백 시 Agent "topic-reviser" 또는 재작성

---

### /curriculum SKILL.md

1. 기존 상태 확인
2. Agent "curriculum-researcher" 호출 (웹 리서치 격리)
3. research 결과 파일 읽기
4. JSON 생성 (main context에서 — 구조 설계는 orchestrator 역할)
5. 검증 루프 (기존과 동일)

---

## B.6 Context 비용 비교 요약

| 단계 | 현재 (모놀리식) | 변경 후 (orchestrator) |
|------|----------------|----------------------|
| RESEARCH | ~100KB (논문+웹 전체) | ~100 tokens (결과 경로만) |
| WRITE | ~200KB (리서치+작성 누적) | ~100 tokens (완료 확인만) |
| EVALUATE | ~50KB (파일 재읽기) | ~500 tokens (점수+피드백) |
| REVISE | ~50KB (파일+피드백) | ~200 tokens (완료 확인만) |
| **토픽당 합계** | **~200-500KB** | **~3-4KB** |
| **50토픽 루프** | **context 한계 초과** | **~150-200KB (여유)** |

---

## B.7 리스크 및 대응

| 리스크 | 대응 |
|--------|------|
| Subagent가 Rules 미준수 | 각 agent .md에 Rules 파일 경로를 명시적으로 Read하도록 지시 + CLAUDE.md 자동 로드 |
| findings 포맷 불일치로 writer 실패 | researcher/writer 양쪽에 동일한 포맷 템플릿 명시 |
| evaluator가 너무 엄격/관대 | 현재 autobook의 10점 기준 그대로 이식 (구체적 Grep 기반) |
| orchestrator 크래시 시 ._research 잔류 | SETUP에서 stale ._research 정리 + .gitignore |
| 모델 비용 증가 (다중 agent 호출) | researcher/evaluator는 Sonnet 사용으로 상쇄. Opus는 writer/reviser에만 |

---

# 통합 실행 순서

## Phase 1: 평가기준 확장 (축 A)
1. `.claude/rules/topic-writing.md` — 자동 로드 리마인더 업데이트 (즉시 효과)
2. `.claude/skills/write-topic/SKILL.md` — 작성 시점 가이드 추가
3. `.claude/skills/review-topic/SKILL.md` — 리뷰 체크리스트 10항목 확장
4. `.claude/skills/autobook/SKILL.md` — 자동 평가·점수·임계값·로그 전면 업데이트

## Phase 2: Subagent 아키텍처 (축 B) — Phase 1 완료 후
5. `.claude/agents/` 디렉토리에 5개 agent 정의 파일 생성
6. `.claude/skills/autobook/SKILL.md` → thin orchestrator로 리팩터 (10점 채점 포함)
7. `.claude/skills/write-topic/SKILL.md` → subagent 호출 패턴 적용
8. `.claude/skills/curriculum/SKILL.md` → curriculum-researcher 분리

## Phase 3: 마무리
9. `CLAUDE.md` 업데이트 (`agents/`, `._research/` 설명 추가)
10. 기존 토픽 2~3개에 `/review-topic` 실행 — 신규 항목 8~10의 변별력 확인

---

# 검증

- 기존 작성된 토픽 2~3개(예: 2.1.1, 1.4.1)에 `/review-topic`을 실행하여 신규 항목 8~10이 의미 있는 차별화를 보이는지 확인
- 기존 results.tsv에 7/7로 기록된 토픽이 10/10이 되지 않아야 정상 (신규 기준의 변별력 확인)
- 각 agent를 직접 Agent 도구로 호출하여 단독 동작 확인
- `/autobook {책이름}`으로 2-3개 토픽 자율 작성 실행하여 통합 동작 확인
- 5개 토픽 이상 연속 작성 후 마지막 토픽 품질이 초기와 동등한지 확인
