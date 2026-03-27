---
name: write-topic
description: 커리큘럼의 세부 주제(a.b.c) 하나에 대응하는 단원 파일을 작성한다. subagent 패턴으로 리서치·작성·평가를 격리 수행.
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# 단원 파일 작성 (Subagent 패턴)

대상 토픽: **$ARGUMENTS** (비어있으면 다음 미작성 토픽을 자동 감지)

## 절차

### 1단계: 대상 토픽 확정

1. `교재/` 하위에서 curriculum.json을 찾는다.
2. `$ARGUMENTS`가 토픽 ID(예: `1.2.3`)이면 해당 토픽을 선택.
3. `$ARGUMENTS`가 비어있으면: `wikidocs/pages/`에서 `{pp}-{ss}-{tt}-*.md` 패턴으로 기존 토픽 파일들을 스캔하여 순서상 첫 미작성 토픽을 선택.
4. 해당 토픽의 `learning_objectives`, `learning_content`, `prerequisites`, `lab`을 읽는다.
5. 모든 선수 토픽의 단원 파일이 `wikidocs/pages/`에 존재하는지 확인한다. 없으면 사용자에게 알린다.
6. 토픽 메타데이터를 추출한다:
   - 선수 토픽 .md 파일 경로 목록 (`wikidocs/pages/{pp}-{ss}-{tt}-*.md`)
   - 다음 토픽 정보 (ID, 제목)
   - 출력 파일 경로: `교재/{책이름}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md`
   - 책이름

### 2단계: 조사 — Agent "topic-researcher" 호출

Agent 도구로 `topic-researcher` agent를 호출한다.

**prompt:**
```
토픽 {a.b.c} "{title}" 리서치를 수행하라.

책이름: {책이름}
learning_content: {keywords 배열}
learning_objectives: {objectives 배열}
prerequisites: {prereq IDs}

자료 기지: 01_Research/
출력 경로: 교재/{책이름}/._research/{a.b.c}_findings.md

위 출력 경로에 findings 파일을 작성하라.
```

### 3단계: 본문 작성 — Agent "topic-writer" 호출

Agent 도구로 `topic-writer` agent를 호출한다.

**prompt:**
```
토픽 {a.b.c} "{title}" 단원을 작성하라.

책이름: {책이름}
findings 경로: 교재/{책이름}/._research/{a.b.c}_findings.md
출력 경로: 교재/{책이름}/wikidocs/pages/{pp}-{ss}-{tt}-{토픽제목}.md

curriculum 메타데이터:
- learning_objectives: {objectives}
- learning_content: {keywords}
- prerequisites: {prereq IDs}

선수 토픽 파일:
{선수 토픽 .md 경로 목록}

다음 토픽: {next_id} "{next_title}"

반드시 Rules/3, Rules/4를 읽고 준수하라.
```

### 4단계: 자동 평가 — Agent "topic-evaluator" 호출

Agent 도구로 `topic-evaluator` agent를 호출한다. Fresh context에서 평가.

**prompt:**
```
토픽 {a.b.c} "{title}" 단원을 10점 기준으로 평가하라.

파일 경로: {출력 경로}
curriculum.json 경로: 교재/{책이름}/curriculum.json

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

평가 결과를 사용자에게 표시한다.

### 5단계: 사용자에게 전달

작성한 파일과 평가 결과를 사용자에게 안내하고 다음을 요청한다:

> 단원을 읽어보시고, 이해가 되지 않는 부분이 있으면 말씀해 주세요.
> 이 단원의 학습 목표: [learning_objectives 내용]
> 목표를 자기 말로 설명할 수 있으신지 확인해 주세요.
>
> 자동 평가 결과: {score}/10
> {FAIL 항목이 있으면 FAIL 목록과 사유 표시}

**사용자가 이해 완료를 확인할 때까지 다음 토픽으로 넘어가지 않는다.**
피드백이 있으면 Agent "topic-reviser"를 호출하여 targeted edit으로 수정한다 (추측으로 문장만 덧붙이지 않음).

### 5.5단계: TOC 갱신

`교재/{책이름}/wikidocs/TOC.md`를 curriculum.json 기반으로 재생성한다.
- 존재하는 페이지만 링크로 연결한다.
- 미작성 토픽은 제목만 표시한다 (링크 없음).

### 6단계: 정리

findings 파일을 삭제한다:
```
rm 교재/{책이름}/._research/{a.b.c}_findings.md
```
