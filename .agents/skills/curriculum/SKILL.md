---
name: curriculum
description: 커리큘럼 JSON 생성 또는 계속. subagent 리서치 → 원자적 개념 목록 → JSON 초안 → 검증 루프.
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# 커리큘럼 생성/계속

책 이름(주제): **$ARGUMENTS**

## 절차

아래 절차를 반드시 순서대로 수행한다. 단계를 건너뛰지 않는다.

### 1단계: 기존 상태 확인

1. `02_Books/$ARGUMENTS/curriculum.json`이 이미 존재하는지 확인한다.
   - 존재하면: 로드 후 **3단계(검증/개선)**부터 재개한다.
   - 없으면: 2단계부터 시작한다.
2. `02_Books/$ARGUMENTS/` 디렉토리가 없으면 생성한다.
3. `02_Books/$ARGUMENTS/._research/` 디렉토리가 없으면 생성한다.
4. `02_Books/$ARGUMENTS/wikidocs/` 디렉토리가 이미 존재하는지 확인한다 (resume 대응).

### 2단계: 개념 조사 — 사전 수집 자료 확인 + Agent "curriculum-researcher" 호출

#### 2-1. 사전 수집 자료 확인

`01_Research/` 하위에 관련 리서치가 있는지 확인한다:
1. `01_Research/` 디렉토리를 Glob으로 탐색하여 `$ARGUMENTS` 주제와 관련된 디렉토리를 찾는다.
2. 관련 디렉토리가 있고 `synthesis/topic_overview.md`가 존재하면:
   - topic_overview.md를 읽어 주제 종합 요약과 챕터 구조 제안을 파악한다.
   - 이 내용을 curriculum-researcher에게 사전 컨텍스트로 전달한다.
3. 관련 디렉토리가 없으면: 사전 컨텍스트 없이 진행한다.

#### 2-2. Agent "curriculum-researcher" 호출

Agent 도구로 `curriculum-researcher` agent를 호출하여 웹 리서치를 격리 수행한다.

**prompt:**
```
"{$ARGUMENTS}" 주제에 대한 커리큘럼 리서치를 수행하라.

책이름: {$ARGUMENTS}
출력 경로: 02_Books/{$ARGUMENTS}/._research/curriculum_research.md

{사전 수집 자료가 있으면:}
사전 수집된 주제 개요가 있다. 참고하여 리서치를 보완하라:
---
{topic_overview.md 내용 요약}
---

공식 문서, 스펙, 신뢰할 수 있는 자료를 최소 10개 이상 조사하여
원자적 개념 목록, 개념 간 관계, 커버리지 공백, 난이도 계층 제안을 정리하라.
```

리서치 완료 후 `02_Books/{$ARGUMENTS}/._research/curriculum_research.md`를 읽어 조사 결과를 파악한다.
조사 결과를 사용자에게 보여주고, 커리큘럼 범위/깊이에 대해 합의한다.

### 3단계: 커리큘럼 JSON 작성

`Rules/1. 커리큘럼 계층 규칙.md`에 따라 Phase/섹션/세부 주제를 배치한다.

**작성 기준:**
- 원자적 개념 목록과 토픽을 1:1 또는 근접하게 대응.
- 각 토픽: learning_objectives 1문장(최대 2), learning_content에 키워드 나열, prerequisites에 선수 id.
- Phase마다 exit_capability 작성.
- 총 토픽 수 50개 이상. 미달이면 세부 주제를 더 분할.
- `curriculum.schema.json`에 맞는 JSON 형식.

`02_Books/$ARGUMENTS/curriculum.json`에 저장한다.

### 4단계: 검증/개선 루프

`Rules/2. 커리큘럼 작성 규칙.md` §2.3에 따라 반복 검증한다.

**검증 항목:**
- [ ] 토픽 총 개수 >= 50
- [ ] 각 토픽이 단일 초점 (목표가 여럿이면 분할)
- [ ] prerequisites DAG에 순환 없음
- [ ] 선수 ID가 모두 존재하고 본인보다 앞섬
- [ ] learning_content가 한 토픽에 과도하면 분할
- [ ] Phase exit_capability와 토픽 범위가 정합
- [ ] 병합으로 토픽을 줄인 흔적 없음
- [ ] 섹션당 토픽 수 적정 (2~20개 범위 권장)

결함이 있으면 수정하고 다시 검증한다.
**사용자에게 최종 커리큘럼을 보여주고 합의를 받은 뒤에만 확정한다.**

### 4.5단계: Wikidocs 구조 초기화

1. `02_Books/$ARGUMENTS/wikidocs/` 디렉토리 생성.
2. `02_Books/$ARGUMENTS/wikidocs/pages/` 디렉토리 생성.
3. `02_Books/$ARGUMENTS/wikidocs/assets/` 디렉토리 생성.
4. **README.md 생성**: curriculum.json의 title, Phase별 제목/exit_capability로 책 소개.
5. **TOC.md 스켈레톤 생성**: 전체 Phase > 섹션 > 토픽 계층 구조 (아직 파일 미존재하므로 링크만 선점).
6. **pages/00-들어가며.md 생성**: 책 도입 페이지 (curriculum title 기반).
7. **Phase 개요 페이지 생성**: `pages/{pp}-{Phase제목}.md`
   - pp = phase id를 2자리 zero-pad.
   - 내용: exit_capability + 하위 섹션/토픽 목록.
8. **섹션 개요 페이지 생성**: `pages/{pp}-{ss}-{섹션제목}.md`
   - ss = section id의 두 번째 숫자를 2자리 zero-pad.
   - 내용: 하위 토픽별 제목 + learning_objectives 요약.

### 5단계: 완료 확인

사용자에게 다음을 안내한다:
- 커리큘럼 확정 완료.
- wikidocs 구조 초기화 완료.
- `/next-topic`으로 첫 단원 작성을 시작할 수 있음.
- `/validate-curriculum`으로 언제든 재검증 가능.
