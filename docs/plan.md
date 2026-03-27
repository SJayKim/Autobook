# AutoBook 구현 계획

> autoresearch의 "자율 실험 루프" 개념을 기술 교재 집필에 적용하는 프로젝트

---

## 컨셉: autoresearch → autobook 대응

| autoresearch | autobook |
|---|---|
| `train.py` (에이전트가 수정하는 파일) | 챕터 `.md` 파일 (에이전트가 작성하는 파일) |
| `prepare.py` (고정, 평가 기준) | `Rules/` 폴더 (고정, 품질 기준) |
| `program.md` (에이전트 지시서) | `/autobook` 스킬 (자율 집필 지시서) |
| `uv run train.py` (5분 학습) | `/write-topic` (챕터 작성) |
| `val_bpb` 점수 (낮을수록 좋음) | 7점 만점 품질 점수 (높을수록 좋음) |
| `results.tsv` (실험 결과 기록) | `results.tsv` (챕터별 평가 기록) |
| keep / discard / crash | pass / revise / fail |
| 시간당 ~12회 실험 | 시간당 ~4회 챕터 (작성 ~10분 + 평가 ~5분) |

---

## 자율 루프 흐름

```
┌─────────────────────────────────────────────────┐
│  SETUP (1회)                                     │
│  1. curriculum.json 존재 확인                     │
│  2. /progress로 현재 진행상황 파악                 │
│  3. 실험 브랜치 생성 (autobook/{tag})              │
│  4. results.tsv 초기화 (헤더만)                    │
└──────────────┬──────────────────────────────────┘
               ▼
┌─────────────────────────────────────────────────┐
│  LOOP FOREVER:                                   │
│                                                  │
│  ① SELECT  - 다음 미작성 토픽 자동 선택            │
│             - 선수 토픽 파일 존재 확인              │
│                                                  │
│  ② WRITE   - 웹 조사 (온톨로지 MCP 없으면 웹만)    │
│             - 톤앤매너/구조 규칙 준수하여 작성       │
│             - git commit                          │
│                                                  │
│  ③ EVALUATE - 7개 체크리스트 자동 채점             │
│              - 점수 산출 (0~7점)                   │
│                                                  │
│  ④ DECIDE                                        │
│     점수 7   → PASS   (커밋 유지, 다음 토픽으로)    │
│     점수 5~6 → REVISE (수정 후 재평가, 최대 3회)    │
│     점수 ≤4  → FAIL   (삭제 후 완전 재작성)         │
│                                                  │
│  ⑤ LOG     - results.tsv에 기록                   │
│  ⑥ REPEAT  - 절대 멈추지 않음                     │
│              사람이 중단할 때까지 계속               │
└─────────────────────────────────────────────────┘
```

---

## 평가 시스템 (7개 체크리스트 → 자동 채점)

기존 `/review-topic`의 7개 항목을 점수화:

| # | 항목 | 자동 판정 방법 | 배점 |
|---|------|---------------|------|
| 1 | 경로/파일명 규칙 | 파일시스템: `{a}_{Phase}/{a.b}_{섹션}/{a.b.c}_{토픽}.md` 패턴 매치 | 1점 |
| 2 | `learning_content` 커버리지 | curriculum.json 키워드 vs 본문 grep. 전 항목 반영 여부 | 1점 |
| 3 | `learning_objectives` 검증 가능 | 목표 문장의 핵심 동사/개념이 본문에 존재하는지 | 1점 |
| 4 | 선수 범위 준수 | prerequisite 파일 존재 여부 + 본문에서 미정의 개념 참조 없음 | 1점 |
| 5 | 톤앤매너 준수 | 합니다체 확인, 곡선 따옴표 검출, AI체 패턴 검출, 출처 표기 검출 | 1점 |
| 6 | 배경 우선 설명 | 새 용어 등장 시 정의 전에 배경 문단 존재 여부 | 1점 |
| 7 | 본문 구조 | `# a.b.c` 제목 존재, `##` 없음, "정리하면," 존재, 다음 단원 안내 존재 | 1점 |

**판정 기준:**
- 7점: PASS → 즉시 다음 토픽
- 5~6점: REVISE → 부족한 항목만 수정 후 재평가 (최대 3라운드)
- 4점 이하: FAIL → 파일 삭제 후 완전 재작성

---

## 프로젝트 구조

```
C:\Users\cyon1\OneDrive\Desktop\autoresearch\
│
├── Rules/                              ← 불변 규칙 (수정 금지)
│   ├── 1. 커리큘럼 계층 규칙.md
│   ├── 2. 커리큘럼 작성 규칙.md
│   ├── 3. 책 작성 톤앤 매너.md
│   ├── 4. 세부 개념 문서 작성 규칙.md
│   ├── 5. 사람-AI 협업 집필 절차.md
│   └── curriculum.schema.json
│
├── .claude/
│   ├── hooks/
│   │   └── protect-rules.sh            ← Rules/ 수정 차단 훅
│   ├── skills/
│   │   ├── curriculum/SKILL.md          ← /curriculum {책이름}
│   │   ├── write-topic/SKILL.md         ← /write-topic {a.b.c}
│   │   ├── next-topic/SKILL.md          ← /next-topic
│   │   ├── review-topic/SKILL.md        ← /review-topic {a.b.c}
│   │   ├── progress/SKILL.md            ← /progress
│   │   ├── validate-curriculum/SKILL.md ← /validate-curriculum
│   │   └── autobook/SKILL.md           ← /autobook {책이름} ★ 핵심 신규
│   ├── rules/
│   │   ├── curriculum-editing.md        ← curriculum.json 편집 시 자동 로드
│   │   └── topic-writing.md             ← 교재/*.md 편집 시 자동 로드
│   ├── settings.json                    ← 훅 설정
│   └── settings.local.json              ← MCP 서버 설정
│
├── 교재/{책이름}/                        ← 산출물 (자동 생성)
│   ├── curriculum.json
│   ├── results.tsv                      ← 자율 루프 결과 로그
│   └── {a}_{Phase}/
│       └── {a.b}_{섹션}/
│           └── {a.b.c}_{토픽}.md
│
├── CLAUDE.md                            ← 프로젝트 메인 문서
└── plan.md                              ← 이 파일
```

---

## 현재 진행 상태

### 완료

| # | 작업 | 상태 |
|---|------|------|
| 1-a | Rules/ 폴더 6개 파일 복사 | ✅ 완료 |
| 2 | Skills 6개 복사 (curriculum, write-topic, next-topic, review-topic, progress, validate-curriculum) | ✅ 완료 |
| 3-a | .claude/settings.local.json 복사 | ✅ 완료 |

### 미완료

| # | 작업 | 설명 |
|---|------|------|
| 3-b | .claude/settings.json | 훅 설정 (PreToolUse → protect-rules.sh) |
| 3-c | .claude/hooks/protect-rules.sh | Rules/ 폴더 수정 차단 스크립트 |
| 3-d | .claude/rules/curriculum-editing.md | curriculum.json 편집 시 자동 리마인더 |
| 3-e | .claude/rules/topic-writing.md | 교재 .md 편집 시 자동 리마인더 |
| 4 | **`/autobook` 스킬 생성** | ★ 핵심. 자율 루프 지시서 |
| 5 | CLAUDE.md 작성 | 프로젝트 메인 진입점 |

---

## `/autobook` 스킬 상세 설계

### 메타데이터

```yaml
name: autobook
description: 자율 집필 모드. 커리큘럼의 모든 토픽을 자동으로 작성-평가-수정 루프.
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
```

### 셋업 단계

1. `교재/$ARGUMENTS/curriculum.json` 존재 확인 (없으면 "먼저 /curriculum 실행" 안내)
2. 커리큘럼 로드하여 전체 토픽 수, 작성 완료 수 파악
3. 오늘 날짜 기반 실험 태그 제안 (예: `mar26`)
4. `git checkout -b autobook/{tag}` 브랜치 생성
5. `교재/$ARGUMENTS/results.tsv` 초기화:
   ```
   topic	score	attempt	status	issues
   ```
6. 셋업 완료 확인 후 자율 루프 진입

### 자율 루프 (LOOP FOREVER)

```
1. 다음 미작성 토픽 선택
   - curriculum.json에서 ID 순서대로 스캔
   - 이미 .md 파일이 있는 토픽은 건너뜀
   - 선수 토픽 파일 존재 확인

2. 챕터 작성
   - 해당 토픽의 learning_objectives, learning_content, prerequisites 확인
   - 웹 조사 (WebSearch, WebFetch)로 내용 수집
   - Rules/3. 톤앤매너, Rules/4. 작성규칙에 따라 본문 작성
   - 파일 저장: 교재/{책이름}/{a}_{Phase}/{a.b}_{섹션}/{a.b.c}_{토픽}.md
   - git commit -m "write: {a.b.c} {토픽제목}"

3. 자동 평가 (7점 만점)
   - 체크리스트 7항목을 프로그래밍적으로 판정
   - 각 항목 PASS(1점) / FAIL(0점) 산출

4. 판정 및 분기
   IF score == 7:
     → status = "pass"
     → 커밋 유지, 다음 토픽으로
   ELIF score >= 5:
     → status = "revise"
     → FAIL 항목만 수정
     → 재평가 (최대 3라운드)
     → 3라운드 후에도 7점 미달이면 그 상태로 keep하고 다음으로
   ELSE (score <= 4):
     → status = "fail"
     → 파일 삭제, git reset
     → 동일 토픽 완전 재작성 (1회만 재시도)
     → 재시도도 4점 이하면 skip하고 다음으로

5. results.tsv에 기록
   {topic_id}\t{score}/7\t{attempt}\t{status}\t{issues}

6. 절대 멈추지 않는다
   - "계속할까요?" 묻지 않는다
   - 아이디어가 떨어져도 다음 토픽이 있으면 계속
   - 모든 토픽을 다 쓰면 전체 리뷰 루프로 전환
```

### 전체 완료 시 동작

모든 토픽이 작성되면:
1. `/progress` 형태의 최종 리포트 출력
2. results.tsv 요약 통계 출력 (pass/revise/fail 비율)
3. 점수가 낮은 토픽 목록을 재작성 후보로 제시
4. 사용자에게 "전체 초안 완료" 알림

---

## results.tsv 형식

```
topic	score	attempt	status	issues
1.1.1	7/7	1	pass	-
1.1.2	5/7	1	revise	톤앤매너(곡선따옴표), 구조(정리하면 누락)
1.1.2	7/7	2	pass	-
1.1.3	3/7	1	fail	learning_content 미반영(3항목), 배경설명 누락, 구조위반
1.1.3	6/7	2	pass	learning_content 1항목 미반영(허용)
1.2.1	7/7	1	pass	-
```

---

## 기존 Rules 프로젝트와의 차이

| 항목 | Rules (기존) | AutoBook (신규) |
|------|-------------|----------------|
| 진행 방식 | 사람이 매 토픽 읽고 피드백 | 에이전트가 자율 판단 |
| 속도 | 사람 속도에 맞춤 | 밤새 자동 (시간당 ~4토픽) |
| 품질 보장 | 사람의 이해도 확인 | 7점 자동 채점 |
| 멈추는 조건 | 사용자가 목표 달성 확인 | 사용자가 수동 중단 |
| 피드백 루프 | 사람 ↔ AI 대화 | AI 자체 평가 → 수정 |
| 적합한 상황 | 학습 목적 (깊이 중시) | 초안 대량 생성 (커버리지 중시) |

**핵심 변경:** `5. 사람-AI 협업 집필 절차.md`의 "사용자 확인 후 다음 토픽" 규칙을 "자동 평가 후 자동 진행"으로 대체. 나머지 규칙(톤앤매너, 구조, 커리큘럼)은 그대로 유지.

---

## 실행 시나리오

```bash
# 1. 커리큘럼이 이미 있다면 바로:
/autobook {책이름}

# 2. 커리큘럼이 없다면 먼저:
/curriculum {책이름}
# → 커리큘럼 완성 후
/autobook {책이름}
```

에이전트가 밤새 돌면서 50개+ 토픽의 초안을 자동 생성.
아침에 사용자가 results.tsv와 생성된 파일들을 확인.
