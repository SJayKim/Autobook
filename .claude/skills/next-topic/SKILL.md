---
name: next-topic
description: 커리큘럼 순서상 다음 미작성 토픽을 찾아 정보를 보여주고, 사용자 확인 후 작성을 시작한다.
user-invocable: true
allowed-tools: Read, Glob, Grep
---

# 다음 토픽 확인

## 절차

### 1단계: 현재 상태 파악

1. `교재/` 하위에서 curriculum.json을 찾아 로드한다.
2. `교재/{책이름}/wikidocs/pages/` 디렉토리를 스캔하여 기존 토픽 파일 목록을 수집한다.
   - 파일명 `{pp}-{ss}-{tt}-` 패턴에서 토픽 ID를 추출하여 작성 완료된 토픽 ID 목록을 만든다.
   - pp → phase, ss → section 두 번째 숫자, tt → topic 세 번째 숫자.

### 2단계: 다음 토픽 결정

1. curriculum.json의 모든 토픽을 순서대로 나열한다:
   - `prerequisite_ordering.mode`가 `global_sequence`이면 global_sequence 순.
   - 그 외에는 id를 (a,b,c) 정수 튜플로 파싱하여 사전순.
2. 이 순서에서 **첫 번째로 대응하는 .md 파일이 없는** 토픽을 찾는다.
3. 해당 토픽의 모든 prerequisites에 대응하는 파일이 존재하는지 확인한다.
   - 선수 파일이 없으면: 그 선수 토픽을 먼저 작성해야 한다고 안내.

### 3단계: 토픽 정보 표시

다음 토픽을 사용자에게 보여준다:

```
## 다음 토픽

- **ID:** a.b.c
- **제목:** [title]
- **Phase:** [phase title]
- **섹션:** [section title]
- **학습 목표:** [learning_objectives]
- **다룰 내용:** [learning_content]
- **선수 토픽:** [prerequisites]
- **실습:** [lab 정보 또는 없음]
- **파일 경로:** wikidocs/pages/{pp}-{ss}-{tt}-{title}.md
```

### 4단계: 사용자 확인

> 이 토픽의 단원 파일을 작성할까요?

사용자가 확인하면 `/write-topic a.b.c` 워크플로우를 진행한다.
사용자가 다른 토픽을 원하면 해당 ID로 진행한다.
