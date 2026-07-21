---
name: autobook
description: 자율 집필 모드. 병렬 배치 subagent 패턴으로 커리큘럼의 모든 토픽을 고속 작성 + 디스크 검증 + 누락 재작성.
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# AutoBook — 자율 집필 루프 (Orchestrator)

대상 책: **$ARGUMENTS**

> 이 스킬은 thin orchestrator로서, topic-writer subagent를 **병렬 배치**로 실행한다.
> 1차 전체 작성 → 디스크 검증 → 누락 재작성 → 최종 검증의 3-pass 구조.
> context 오염을 방지하여 70+ 토픽 고속 작성이 가능하다.

## 모드 선언

이 스킬은 **자율 모드**로 동작한다. Rules/5 "사람-AI 협업 절차"와의 관계:

| Rules/5 조항 | 수동 모드 (write-topic) | 자율 모드 (autobook) |
|-------------|----------------------|---------------------|
| §2.3 한 파일씩만 | 준수 | 병렬 배치 (1 에이전트 = 1 토픽, 동시 4개) |
| §2.4 사용자 독해 | 사용자 직접 확인 | 에이전트 내부 자가 점검으로 대체 |
| §2.5 피드백→보강 | 사용자 피드백 | 디스크 검증 → 누락 재작성으로 대체 |
| §2.6 다음 진행 조건 | 사용자 명시적 확인 | 배치 완료 → 자동 다음 배치 |
| §2.7 Rules 준수 점검 | 준수 | 준수 (에이전트 프롬프트에 Rules 참조 포함) |

Rules/1~4의 톤앤매너, 구조, 커리큘럼 규칙은 **모드 무관하게 완전 준수**한다.

---

## Phase 1: SETUP (1회)

### 1. 커리큘럼 확인

1. `02_Books/$ARGUMENTS/curriculum.json` 파일을 찾는다.
2. 없으면 → 커리큘럼을 직접 생성한다:
   - `Rules/curriculum.schema.json` 스키마 참조
   - 기존 교재 curriculum.json 구조 참고
   - 50+ 토픽 확보, DAG 선수관계 설정
3. 있으면 → 로드하여 전체 Phase, Section, Topic 구조를 파악한다.

### 2. 커리큘럼 검증

Python 스크립트로 다음을 검증한다:
- 토픽 수 >= 50
- ID 접두사 정합 (section.id가 phase.id를 접두사로, topic.id가 section.id를 접두사로)
- prerequisites의 모든 ID가 실제 topic.id로 존재
- DAG 순환 없음 (위상 정렬 가능)
- id_numeric_tuple 순서 (모든 선수 튜플이 본인보다 사전순으로 앞섬)
- learning_objectives >= 1개

**하나라도 FAIL이면 curriculum.json을 수정 후 재검증.**

### 3. Wikidocs 구조 초기화

`02_Books/$ARGUMENTS/wikidocs/` 하위 구조를 생성한다:

```
wikidocs/
├── README.md          ← 책 소개 (대상 독자, 구성 표)
├── TOC.md             ← 전체 목차 (Phase/Section/Topic 링크)
├── assets/
└── pages/
    ├── 00-들어가며.md
    ├── {pp}-{Phase제목}.md         ← Phase 개요 (9개)
    ├── {pp}-{ss}-{섹션제목}.md     ← Section 개요 (25개)
    └── (토픽 파일은 LOOP에서 생성)
```

- Phase 개요: Phase exit_capability를 한 문단으로 서술
- Section 개요: 해당 섹션이 다루는 범위를 1~2문장으로 서술
- 들어가며: 책 전체 개요, Phase별 흐름 소개
- **기존 파일이 있으면 덮어쓰지 않는다.**

### 4. 브랜치 및 로그 초기화

1. 오늘 날짜 기반 태그 생성 (예: `apr03`).
2. `git checkout -b autobook/{tag}` 실행.
3. `02_Books/$ARGUMENTS/results.tsv` 초기화:
   ```
   topic_id	title	status	score	timestamp	notes
   ```

### 5. 셋업 요약 출력

```
AutoBook 시작 (병렬 배치 아키텍처)
책: {$ARGUMENTS}
전체 토픽: {N}개
작성 완료: {M}개
남은 토픽: {N-M}개
브랜치: autobook/{tag}
```

셋업 완료 후 즉시 Phase 2로 진입한다. **사용자에게 확인을 묻지 않는다.**

---

## Phase 2: BATCH WRITE (병렬 집필)

> **핵심 원리:** 순차 1토픽이 아니라, 4개씩 병렬 배치로 topic-writer를 실행한다.
> 에이전트 완료 알림이 오면 즉시 다음 배치를 발사한다.

### 경로 공식

```
토픽 파일: 02_Books/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md
  pp = phase id를 2자리 zero-pad (예: "1" → "01")
  ss = section id의 두 번째 숫자를 2자리 zero-pad (예: "1.2" → "02")
  tt = topic id의 세 번째 숫자를 2자리 zero-pad (예: "1.2.3" → "03")
```

### ① SELECT BATCH — 다음 배치 선택

1. curriculum.json에서 **미작성** 토픽을 ID 순서(a.b.c 사전순)로 스캔한다.
2. `wikidocs/pages/`에서 이미 대응하는 `{pp}-{ss}-{tt}-*.md` 파일이 있는 토픽은 건너뛴다.
3. 미작성 토픽 중 **최대 4개**를 배치로 묶는다.
4. 모든 토픽이 작성 완료이면 → **Phase 3: VERIFY**로 이동.

### ② LAUNCH — 배치 병렬 실행

선택된 4개 토픽 각각에 대해 Agent 도구를 `run_in_background: true`로 **동시에** 호출한다.
**반드시 하나의 메시지에 4개 Agent 호출을 모두 포함한다.**

각 에이전트의 prompt:

```
다음 토픽을 집필해 주세요.

책 이름: {$ARGUMENTS}
책 경로: 02_Books/{$ARGUMENTS}
토픽 정보:
- id: {a.b.c}
- title: {title}
- section: {section_id} {section_title}
- phase: {phase_id} {phase_title}
- learning_objectives: {objectives 배열}
- learning_content: {keywords 배열}
- prerequisites: {prereq IDs}
- previous_topic: {prev_id} {prev_title}
- next_topic: {next_id} {next_title}

파일 경로: 02_Books/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md

01_Research/ 에 관련 자료가 없으므로 웹 조사를 primary로 사용합니다.
Rules/ 의 톤앤매너(합니다체, 서술형 문단, ## 헤더 금지, 직선 따옴표만) 및 문서 작성 규칙을 준수하세요.
```

**subagent_type: topic-writer** 를 사용한다.

### ③ WAIT & NEXT — 완료 대기 및 다음 배치

1. 에이전트 완료 알림을 수신한다.
2. 완료된 에이전트 수를 기록한다.
3. **즉시 다음 배치를 ① SELECT BATCH로 선택하여 ② LAUNCH한다.**
   - 이전 배치의 나머지 에이전트가 아직 실행 중이어도 다음 배치를 발사한다.
   - 동시 실행 에이전트 상한: **약 25개** (시스템 제한에 따라 조절)
4. 진행 현황을 간결하게 출력한다:
   ```
   {완료}/{전체} 토픽 완료. {진행중}개 진행 중.
   ```

### ④ REPEAT

- 미작성 토픽이 남아 있으면 ①로 돌아간다.
- 모든 토픽이 할당되었으면 나머지 에이전트 완료를 기다린다.
- **절대 멈추지 않는다. "계속할까요?" 묻지 않는다.**

---

## Phase 3: VERIFY (디스크 검증)

> **핵심:** 에이전트가 "완료"를 보고해도 파일이 디스크에 없을 수 있다.
> 반드시 디스크를 직접 확인한다.

### ① 전수 검증

Python 스크립트로 curriculum.json의 모든 토픽에 대해 대응하는 파일 존재를 확인한다:

```python
for topic in all_topics:
    prefix = f"{phase:02d}-{section:02d}-{topic:02d}"
    exists = any(f.startswith(prefix) for f in os.listdir(pages_dir))
    if not exists:
        missing.append(topic)
```

### ② 결과 분류

```
존재: {found}/70
누락: {missing_count}개
  {누락 토픽 ID와 제목 목록}
```

### ③ 분기

- **누락 0개**: Phase 4: FINISH로 이동
- **누락 있음**: Phase 3.5: REWRITE로 이동

---

## Phase 3.5: REWRITE (누락 재작성)

> **교훈:** 1에이전트 1토픽보다 **1에이전트 N토픽이 저장 신뢰도가 높다.**
> 재작성 배치에서는 한 에이전트에 최대 8토픽을 할당한다.

### ① 누락 토픽 배치 구성

누락된 토픽을 **8개씩** 묶어 재작성 배치를 구성한다.

### ② 재작성 에이전트 실행

각 배치에 대해 Agent를 `run_in_background: true`로 호출한다.

prompt 구조:

```
아래 {N}개 토픽의 파일이 누락되어 재작성이 필요합니다.
각 토픽을 순서대로 작성해 주세요.

책: {$ARGUMENTS} (02_Books/{$ARGUMENTS})
파일 경로 패턴: 02_Books/{$ARGUMENTS}/wikidocs/pages/{pp}-{ss}-{tt}-{제목}.md

1. id={a.b.c}, title="{title}"
   content: {keywords 배열}
   파일: {pp}-{ss}-{tt}-{제목}.md

2. id={a.b.c}, title="{title}"
   ...

각 파일은 반드시 실제로 Write 도구로 디스크에 저장하세요.
Rules/ 톤앤매너(합니다체, 서술형, ## 금지, 직선따옴표, 정리하면 요약, 다음 토픽 안내) 준수.
```

### ③ 재검증

재작성 에이전트 완료 후 **Phase 3: VERIFY를 다시 실행**한다.
- 여전히 누락이 있으면 → 남은 토픽만 모아 재작성 반복 (최대 3회)
- 3회 반복 후에도 누락이 있으면 → 사용자에게 알림

---

## Phase 4: FINISH (최종 마무리)

모든 토픽이 디스크에 존재하면:

### 1. TOC.md 최종 재빌드

curriculum.json 기반으로 전체 목차를 재생성한다.
- 존재하는 페이지는 링크로 연결
- 구조: Phase > Section > Topic

### 2. 최종 검증 출력

```
=== AutoBook 완료 ===
책: {$ARGUMENTS}
전체 토픽: {N}개
디스크 존재: {N}/{N} (100%)
전체 페이지 파일: {M}개 (토픽 + 개요 + 들어가며)
```

Phase별 완료 현황 테이블:

| Phase | 토픽 수 | 상태 |
|-------|---------|------|
| 1. ... | 7/7 | 완료 |
| 2. ... | 5/5 | 완료 |
| ... | ... | ... |

### 3. Git 커밋

```bash
git add "02_Books/{$ARGUMENTS}/wikidocs/"
git commit -m "feat: {$ARGUMENTS} 전체 {N}개 토픽 초판 완료"
```

### 4. 완료 알림

```
전체 초안 완료
브랜치: autobook/{tag}
토픽: {N}개
페이지: {M}개
```

---

## 핵심 원칙

1. **병렬 우선**: 순차 루프 대신 4개씩 병렬 배치. 에이전트 완료 즉시 다음 배치 발사.
2. **디스크 검증 필수**: 에이전트 보고를 신뢰하지 않는다. Phase 3에서 전수 검증.
3. **재작성은 N:1**: 누락 재작성 시 1에이전트에 8토픽 할당 (저장 신뢰도 향상).
4. **context 격리**: 각 토픽은 별도 subagent에서 실행. orchestrator는 메타데이터만 관리.
5. **불변 규칙 준수**: Rules/1~4의 커리큘럼, 톤앤매너, 구조 규칙은 그대로 유지.
6. **멈추지 않는다**: 사용자가 수동으로 중단할 때만 멈춘다. 에러 시 다음 배치로 진행.

---

## 에이전트 내부 동작 (topic-writer가 수행)

각 topic-writer 에이전트는 다음을 자체적으로 수행한다:

1. `Rules/3. 책 작성 톤앤 매너.md` 읽기
2. `Rules/4. 세부 개념 문서 작성 규칙.md` 읽기
3. `01_Research/` 관련 자료 탐색 (없으면 자체 지식 기반 작성)
4. 기존 작성된 토픽 파일 스타일 참고
5. 본문 작성:
   - `# a.b.c 제목` (최상단 제목 하나만)
   - `##` 이하 헤더 사용 금지
   - 합니다체 통일, 서술형 문단
   - 직선 따옴표만 (' ")
   - learning_content 전 항목 본문 반영
   - 새 용어마다 배경부터 설명
   - 3단계 이상 프로세스에 ASCII 다이어그램
   - "정리하면," 요약 + 다음 토픽 안내
6. 자가 점검:
   - 굵은 용어 밀도 (한 문단 3개 이하)
   - 추상 정의 후 2문단 이내 구체 사례
   - 번역투 ("~에 의해", "~를 수행한다") 검사
   - learning_content 커버리지 확인
7. Write 도구로 파일 저장
