# 워크플로우 리팩터 계획서

작성일: 2026-03-27
상태: 계획 수립 완료, 실행 대기

---

## 배경

전체 스킬 8개, 에이전트 8개, 규칙 5+3개를 검토한 결과, 규칙-구현 간 괴리, 워크플로우 충돌, 에이전트 설계 결함 등 12개 개선 항목을 식별했다. 이 문서는 각 항목의 현황, 수정 방안, 대상 파일, 실행 순서를 정의한다.

---

## Phase 1: 규칙-구현 정합성 (Critical)

### 1-A. 온톨로지 규칙과 실제 구현의 괴리 해소

**현황:**
- Rules/2 (§2.1 Stage A): "최소 50개 쿼리로 `list_documents`, `query_data`, `get_chunks` 수행" 요구
- Rules/4 (§2): "온톨로지 우선(Primary), 웹 보완(Secondary)" 조사 순서 명시
- Rules/5 (§2.1, §2.5): 온톨로지 도구를 핵심 조사 수단으로 전제
- **실제 구현:** 어떤 에이전트/스킬에도 `list_documents`, `query_data`, `get_chunks` 도구가 정의되어 있지 않음. topic-researcher는 `01_Research/` 파일 + WebSearch로 대체 중

**수정 방안:**

Rules/는 수정 불가(훅 보호)이므로, 규칙의 "온톨로지"를 현재 구현의 "사전 수집 자료(01_Research/)"로 매핑하는 해석 문서를 작성한다.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/rules/ontology-mapping.md` (신규) | glob: `**/curriculum.json`, `01_Research/**/*` 트리거. "온톨로지 도구 → 01_Research/ 조사"로 매핑하는 해석 리마인더 작성 |
| `.claude/agents/topic-researcher.md` | 프로세스 §1 설명을 "사전 수집 자료 = 온톨로지 대체" 명시로 보강. 01_Research/ 미존재 시 웹 전용 모드로 전환하는 fallback 절차 추가 |
| `.claude/agents/curriculum-researcher.md` | "01_Research/synthesis/가 있으면 온톨로지 조사 대체로 간주" 명시 |

**해석 리마인더 초안:**
```markdown
---
name: ontology-mapping
description: Rules의 온톨로지 도구 참조를 현재 구현(01_Research/)으로 매핑하는 해석 가이드
globs: ["**/curriculum.json", "01_Research/**/*"]
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
```

---

### 1-B. Rules/5 자율 모드 예외 규정 명시

**현황:**
- Rules/5 §2.3: "같은 세션에서 여러 파일을 생성하거나, 사용자 확인 없이 연속으로 여러 단원을 일괄 추가하는 방식 금지"
- Rules/5 §2.6: "사용자가 목표 달성을 인정할 때까지 현재 파일에서 멈춘다"
- `/autobook`: "사용자에게 확인을 묻지 않는다", "절대 멈추지 않는다"
- 현재 autobook SKILL.md 핵심 원칙 §1에 "Rules/5의 규칙을 자동 평가로 대체"라고 적혀 있지만, 이것이 Rules/ 원문과 어떤 관계인지 모호

**수정 방안:**

autobook/SKILL.md에 Rules/5 적용 범위를 명확히 선언하고, 자율 모드에서 사용자 확인을 자동 평가로 대체하는 근거를 구조화한다.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/skills/autobook/SKILL.md` | 상단에 "모드 선언" 섹션 추가: Rules/5는 수동 모드(write-topic) 전용, autobook은 자율 모드로서 §2.4/2.5/2.6의 "사용자 확인"을 "topic-evaluator 자동 채점 ≥ 7점"으로 대체 |
| `.claude/skills/write-topic/SKILL.md` | 상단에 "이 스킬은 Rules/5 수동 모드를 따른다" 명시 |

**autobook 모드 선언 초안:**
```markdown
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
```

---

## Phase 2: 에이전트 설계 결함 수정 (High)

### 2-A. topic-writer: findings 부족 시 대응 프로토콜 추가

**현황:**
- topic-writer는 WebSearch/WebFetch 사용 금지 (context 오염 방지)
- findings에 없는 내용은 채울 수 없음 → learning_content 미충족 또는 hallucination 위험
- 현재 "findings에 없는 내용을 추측으로 작성하지 않는다"는 제약만 있고, 부족 시 어떻게 해야 하는지 정의 없음

**수정 방안:**

writer가 findings 부족을 감지하면 INCOMPLETE 마커를 남기고 조기 종료하는 프로토콜을 추가한다. orchestrator(autobook/write-topic)가 이를 감지하면 researcher를 보강 호출한다.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/agents/topic-writer.md` | §제약에 "findings 부족 프로토콜" 추가 |
| `.claude/skills/autobook/SKILL.md` | ③WRITE 단계에 "INCOMPLETE 감지 → researcher 재호출" 분기 추가 |
| `.claude/skills/write-topic/SKILL.md` | 3단계에 동일 분기 추가 |

**topic-writer 추가 내용:**
```markdown
## findings 부족 프로토콜

learning_content 키워드 중 findings에서 충분한 정보를 찾을 수 없는 항목이 있으면:

1. 해당 키워드를 본문에서 최소한으로 언급하되, 심층 설명은 생략한다.
2. 파일 최하단에 아래 마커를 남긴다:
   ```
   <!-- INCOMPLETE: {누락 키워드1}, {누락 키워드2} -->
   ```
3. 반환 메시지를 "Wrote {경로} (INCOMPLETE: {누락 키워드})"로 변경한다.

orchestrator는 INCOMPLETE를 감지하면 누락 키워드에 대해 researcher를 재호출하고, 보강된 findings로 reviser를 호출하여 해당 부분만 보완한다.
```

**autobook ③WRITE 수정:**
```
③-1. WRITE 결과에서 "INCOMPLETE"를 감지한다.
③-2. INCOMPLETE이면:
  - 누락 키워드를 파싱한다.
  - topic-researcher를 해당 키워드 한정으로 재호출한다.
    prompt에 "보강 조사: {누락 키워드만}"을 명시한다.
  - 보강 findings를 기존 findings에 append한다.
  - topic-reviser를 호출하여 INCOMPLETE 부분만 보완한다.
  - INCOMPLETE 마커를 제거한다.
③-3. INCOMPLETE가 아니면 ④로 진행한다.
```

---

### 2-B. topic-evaluator: learning_content를 프롬프트에 포함

**현황:**
- evaluator는 fresh context에서 동작하여 findings를 볼 수 없음 (의도적 설계)
- 그러나 learning_content도 curriculum.json에서 직접 읽어야 하는 구조
- 현재 autobook/write-topic의 evaluator 호출 prompt에 learning_content를 이미 포함하고 있음 (확인 완료)
- **문제:** evaluator가 Grep으로 키워드 매칭만 하면 "키워드가 있다" ≠ "키워드를 제대로 설명했다"

**수정 방안:**

evaluator 항목 2의 판정 기준을 "존재" → "존재 + 최소 설명량"으로 강화한다.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/agents/topic-evaluator.md` | 항목 2 판정 기준에 "키워드 주변 2문단 이내에 설명적 문장이 동반되어야 PASS" 조건 추가 |

**수정 내용:**
```markdown
**항목 2: learning_content 커버리지**
- curriculum.json의 learning_content 각 항목(키워드)이 본문에 존재하는가?
- Grep으로 각 키워드를 본문에서 검색. 전 항목이 반영되어야 PASS.
- [추가] 키워드가 단순 언급(1회, 나열 속)에 그치면 FAIL. 해당 키워드 전후 2문단 이내에 설명적 서술(배경, 정의, 메커니즘 중 하나 이상)이 있어야 PASS.
```

---

### 2-C. topic-reviser: findings 경로 전달 보장

**현황:**
- reviser 입력 명세에 "findings 파일 경로 (내용 보완 필요시만)"이라고 적혀 있음
- autobook의 reviser 호출 prompt에는 findings 경로가 이미 포함되어 있음 (확인 완료)
- **문제:** write-topic의 5단계(사용자 피드백 → reviser 호출)에서는 findings 경로 전달이 명시되어 있지 않음. 6단계에서 findings를 삭제하므로 순서에 따라 reviser가 findings를 참조할 수 없을 수 있음

**수정 방안:**

write-topic의 reviser 호출 시 findings 경로를 명시적으로 전달하고, findings 삭제 시점을 "모든 수정 완료 후"로 명확히 한다.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/skills/write-topic/SKILL.md` | 5단계의 reviser 호출 설명에 findings 경로 포함. 6단계 삭제 조건에 "5단계 수정이 모두 완료된 후에만" 명시 |

**수정 내용 (write-topic 5단계):**
```markdown
피드백이 있으면 Agent "topic-reviser"를 호출하여 targeted edit으로 수정한다.

**reviser prompt:**
```
토픽 {a.b.c} "{title}" 단원을 수정하라.

파일 경로: {출력 경로}
findings 경로: 02_Books/{책이름}/._research/{a.b.c}_findings.md

사용자 피드백:
{피드백 내용}

curriculum 메타데이터:
- learning_objectives: {objectives}
- learning_content: {keywords}

피드백 내용을 반영하여 targeted edit으로 수정하라.
```
```

---

### 2-D. autobook: skip 토픽 연쇄 영향 경고

**현황:**
- 점수 ≤6이면 1회 재시도 후 skip
- skip된 토픽이 다른 토픽의 prerequisite이면 연쇄 skip 발생
- 현재 results.tsv에 skip을 기록하지만, 후속 영향에 대한 처리 없음

**수정 방안:**

skip 발생 시 해당 토픽을 prerequisite로 가진 토픽 목록을 즉시 계산하고, 경고를 results.tsv에 기록한다. 연쇄 skip이 3개 이상 누적되면 루프를 일시 정지하고 사용자에게 판단을 요청한다.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/skills/autobook/SKILL.md` | ⑥DECIDE의 skip 분기에 "연쇄 영향 분석" 단계 추가 |

**추가 내용 (⑥ DECIDE skip 분기):**
```markdown
ELSE (score <= 6, 재시도도 실패):
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

---

## Phase 3: 워크플로우 중복/효율성 (Medium)

### 3-A. wikidocs 초기화 로직 통합

**현황:**
- `/curriculum` (4.5단계): wikidocs 전체 구조 생성 (README, TOC, Phase/Section 개요, 들어가며)
- `/autobook` (SETUP 2): "디렉토리가 없으면 생성" + "curriculum SKILL 4.5단계와 동일"
- 둘 다 실행하면 중복 생성 또는 덮어쓰기 위험

**수정 방안:**

autobook의 SETUP 2를 "존재 확인 → 없으면 생성" 전용으로 축소하고, 생성 로직은 curriculum에만 두기.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/skills/autobook/SKILL.md` | SETUP §2를 아래로 교체 |

**수정 내용:**
```markdown
### 2. Wikidocs 구조 확인

1. `02_Books/$ARGUMENTS/wikidocs/pages/` 디렉토리가 존재하는지 확인한다.
2. **존재하면:** 그대로 사용. 기존 파일을 덮어쓰지 않는다.
3. **존재하지 않으면:** `/curriculum` 스킬의 4.5단계와 동일한 구조를 생성한다:
   - `wikidocs/pages/`, `wikidocs/assets/` 디렉토리 생성
   - README.md, TOC.md 스켈레톤 생성
   - Phase/섹션 개요 페이지, `00-들어가며.md` 생성
4. 이미 일부만 존재하는 경우 (예: pages/는 있지만 README.md가 없는 경우):
   - 누락된 파일만 보완 생성한다. 기존 파일은 건드리지 않는다.
```

---

### 3-B. TOC 재빌드 최적화

**현황:**
- autobook: 매 토픽 작성 후 TOC.md 전체 재생성 (⑥.5)
- write-topic: 매 토픽 후 재생성 (5.5단계)
- 50+ 토픽 기준으로 불필요한 반복

**수정 방안:**

autobook에서는 TOC 재빌드를 Phase 완료 시점 + 최종 FINISH에서만 수행하도록 변경한다. write-topic은 단건이므로 유지.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/skills/autobook/SKILL.md` | ⑥.5를 조건부로 변경 |

**수정 내용:**
```markdown
### ⑥.5 TOC UPDATE (조건부)

TOC 재빌드는 아래 조건에서만 수행한다:
1. 현재 토픽이 해당 Phase의 **마지막 토픽**인 경우 (Phase 완료 시점)
2. 현재 토픽이 전체 커리큘럼의 **마지막 토픽**인 경우
3. 누적 10개 토픽마다 (10, 20, 30... 번째 토픽)

그 외에는 TOC 재빌드를 건너뛴다. FINISH 단계에서 최종 재빌드를 수행하므로 누락 없음.
```

---

### 3-C. web-collector 중복 URL 방지

**현황:**
- 같은 URL이 여러 키워드 클러스터에서 반복 수집 가능
- research-collecting.md 규칙 §3: "동일 URL의 소스를 중복 저장하지 않는다. 저장 전 기존 sources/를 확인한다"
- web-collector 에이전트 프롬프트에 "기존 sources/ 확인" 로직이 약함

**수정 방안:**

web-collector 에이전트 프로세스에 "수집 전 기존 URL 목록 로드" 단계를 추가한다.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/agents/web-collector.md` | 프로세스 최상단에 "기존 URL 인덱스 구축" 단계 추가 |

**추가 내용:**
```markdown
### 0. 기존 소스 URL 인덱스 (수집 전 필수)

1. `sources/*.md` 파일의 frontmatter에서 `url` 필드를 Grep으로 추출한다:
   `Grep("^url:", "01_Research/{topic_name}/sources/")`
2. 추출된 URL 목록을 메모리에 보관한다.
3. 이후 모든 수집 단계에서 URL이 이 목록에 있으면 스킵하고 progress.tsv에 "duplicate_skip"으로 기록한다.
```

---

### 3-D. progress 스킬에 results.tsv 통합

**현황:**
- `/autobook`이 results.tsv에 점수/시도/상태를 기록
- `/progress`는 curriculum.json + pages/ 파일 존재만 확인
- autobook 실행 결과에 대한 품질 지표가 progress에 반영되지 않음

**수정 방안:**

progress에 results.tsv 파싱 섹션을 추가한다.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/skills/progress/SKILL.md` | 1단계에 results.tsv 로드 추가, 3단계에 품질 통계 섹션 추가 |

**추가 내용 (1단계):**
```markdown
5. `02_Books/{책이름}/results.tsv`가 존재하면 파싱한다.
   - 토픽별 최종 점수, 시도 횟수, 상태(pass/revise/fail/skip) 매핑
```

**추가 내용 (3단계, 리포트 하단):**
```markdown
### 품질 통계 (autobook 실행 시)

results.tsv가 존재하면 아래를 추가 표시한다:

- 평균 점수: {avg}/10
- 1회 통과: {N}개 ({%}%)
- 수정 후 통과: {N}개 ({%}%)
- skip: {N}개 ({%}%)
- 재작성 후보 (8점 이하): {토픽 목록}
```

---

## Phase 4: 선수 관계 품질 게이트 강화 (Low-Medium)

### 4-A. prerequisite 검증에 품질 조건 추가

**현황:**
- 모든 스킬에서 prerequisite 충족 = 해당 .md 파일 존재
- evaluator가 FAIL로 판정하거나 skip된 토픽도 "충족"으로 간주

**수정 방안:**

results.tsv가 존재하는 경우(autobook 모드), prerequisite 토픽의 status가 "pass" 또는 "revise"인지 추가 확인한다. "skip"이면 경고를 출력한다.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/skills/autobook/SKILL.md` | ①SELECT의 선수 확인에 results.tsv 조건 추가 |

**수정 내용 (①SELECT 4번):**
```markdown
4. 선수 토픽 검증:
   a. 각 prerequisite의 `.md` 파일이 `wikidocs/pages/`에 존재하는지 확인한다.
   b. results.tsv가 존재하면, 각 prerequisite의 최종 status를 확인한다:
      - "pass" 또는 "revise": 정상 진행
      - "skip": 경고 출력 ("선수 토픽 {id}이(가) skip 상태입니다. 품질 저하 가능성이 있습니다.")
        → 경고만 출력하고 진행은 허용 (skip 토픽의 파일이 존재하지 않으므로 자동 보류됨)
      - results.tsv에 없음: 수동 작성된 것으로 간주, 정상 진행
```

---

### 4-B. source-synthesizer 컨텍스트 폭발 방지

**현황:**
- source-synthesizer가 100+ 소스를 한 번에 읽어 종합
- opus 컨텍스트(200K) 내에서도 100+ 소스 전문은 부담

**수정 방안:**

2단계 종합 구조를 도입한다: 클러스터별 중간 종합 → 최종 종합.

**대상 파일 및 작업:**

| 파일 | 작업 |
|------|------|
| `.claude/agents/source-synthesizer.md` | 프로세스를 2단계로 분리 |
| `.claude/skills/autoresearch/SKILL.md` | Phase 3 호출을 2단계로 분리하거나, synthesizer 에이전트 내부에서 처리하도록 위임 |

**수정 내용:**
```markdown
## 프로세스

### Phase A: 클러스터별 중간 종합 (소스 50개 초과 시)

소스가 50개를 초과하면 클러스터별로 나누어 종합한다:

1. keyword_map.json에서 클러스터 목록을 읽는다.
2. 각 클러스터에 해당하는 소스만 필터링하여 읽는다.
3. 클러스터별 중간 요약을 `synthesis/_cluster_{id}.md`에 저장한다.

소스가 50개 이하이면 Phase A를 건너뛰고 Phase B로 직행한다.

### Phase B: 최종 종합

Phase A를 수행한 경우:
- `synthesis/_cluster_*.md` 중간 요약들을 읽어 최종 종합을 작성한다.

Phase A를 건너뛴 경우:
- sources/*.md를 직접 읽어 최종 종합을 작성한다.

출력: keyword_findings.md, topic_overview.md, gap_analysis.md
```

---

## 실행 순서 및 의존성

```
Phase 1 (규칙 정합성) ─ 선행 필수, 다른 수정의 기반
├── 1-A: ontology-mapping.md 신규 + agent 2개 수정
└── 1-B: autobook/write-topic SKILL 모드 선언 추가

Phase 2 (에이전트 설계) ─ Phase 1 완료 후
├── 2-A: topic-writer findings 부족 프로토콜
├── 2-B: topic-evaluator 항목 2 강화 (독립)
├── 2-C: write-topic reviser 경로 전달 (독립)
└── 2-D: autobook skip 연쇄 경고 (독립)

Phase 3 (효율성) ─ Phase 2와 병렬 가능
├── 3-A: wikidocs 초기화 통합 (독립)
├── 3-B: TOC 재빌드 최적화 (독립)
├── 3-C: web-collector 중복 방지 (독립)
└── 3-D: progress results.tsv 통합 (독립)

Phase 4 (품질 게이트) ─ Phase 2-D, 3-D 이후
├── 4-A: prerequisite 품질 조건 (2-D의 results.tsv 활용)
└── 4-B: synthesizer 2단계 종합 (독립)
```

---

## 수정 대상 파일 요약

| 파일 | 수정 항목 | 작업 유형 |
|------|----------|----------|
| `.claude/rules/ontology-mapping.md` | 1-A | **신규 생성** |
| `.claude/agents/topic-researcher.md` | 1-A | 수정 |
| `.claude/agents/curriculum-researcher.md` | 1-A | 수정 |
| `.claude/agents/topic-writer.md` | 2-A | 수정 |
| `.claude/agents/topic-evaluator.md` | 2-B | 수정 |
| `.claude/agents/topic-reviser.md` | (변경 없음, 현재 설계 적절) | - |
| `.claude/agents/web-collector.md` | 3-C | 수정 |
| `.claude/agents/source-synthesizer.md` | 4-B | 수정 |
| `.claude/skills/autobook/SKILL.md` | 1-B, 2-A, 2-D, 3-A, 3-B, 4-A | 수정 (가장 많은 변경) |
| `.claude/skills/write-topic/SKILL.md` | 1-B, 2-A, 2-C | 수정 |
| `.claude/skills/progress/SKILL.md` | 3-D | 수정 |
| `.claude/skills/autoresearch/SKILL.md` | 4-B | 수정 |

변경 없는 파일: `curriculum`, `next-topic`, `validate-curriculum`, `review-topic` 스킬, `research-planner` 에이전트

---

## 기존 리팩터 계획과의 관계

`memory/plan_workflow_refactor.md`에 정의된 5개 항목(maxTurns, compact hook, tools 필드명, 디렉토리 구조, 비표준 필드)은 **인프라 레벨** 개선이다. 본 계획서의 12개 항목은 **워크플로우 로직 레벨** 개선이다. 두 계획은 독립적으로 실행 가능하며, 병합할 필요 없다.

단, 기존 계획의 "항목 1: maxTurns 추가"와 "항목 2: compact hook"은 본 계획 Phase 2/3의 에이전트 수정 시 함께 적용하면 효율적이다.
