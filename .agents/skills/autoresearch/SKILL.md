---
name: autoresearch
description: 자연어 입력(주제, URL, 키워드)을 받아 웹+논문 자료를 자동 수집하고, 01_Research/{topic}/ 에 토픽별로 정리하여 저장한다.
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# AutoResearch — 자동 자료 수집 (Orchestrator)

입력: **$ARGUMENTS**

> 이 스킬은 thin orchestrator로서, 키워드 확장·웹 수집·논문 수집·종합 분석을 각각 격리된 subagent에 위임한다.
> context 오염을 방지하여 대량 소스 수집이 가능하다.

---

## ⚠️ Agent 호출 규칙

**반드시 전용 agent를 사용한다. `topic-researcher` 등 다른 agent로 대체하지 않는다.**

| Phase | Agent 도구 호출 시 `subagent_type` | 모델 |
|-------|-------------------------------------|------|
| Phase 1 | `research-planner` | sonnet |
| Phase 2 | `web-collector` | sonnet |
| Phase 3 | `source-synthesizer` | sonnet |

---

## Phase 0: PARSE — 입력 해석

### 1. 입력 파싱

`$ARGUMENTS`를 아래 규칙으로 파싱한다:

| 패턴 | 해석 |
|------|------|
| `https://...` | URL → 직접 scrape 대상 |
| `"quoted terms"` | 키워드 → 검색 쿼리 |
| `--min N` | 최소 소스 수 오버라이드 (기본값: 30) |
| `--target N` | 목표 소스 수 오버라이드 (기본값: 60) |
| 그 외 텍스트 | 주제 → 키워드 확장 대상 |

### 2. 디렉토리명 결정

주제 텍스트에서 디렉토리명을 생성한다:
- 공백을 `_`로 치환
- 특수문자 제거
- 예: "Agentic AI 메모리 시스템" → `Agentic_AI_메모리_시스템`

### 3. 디렉토리 구조 생성

```
01_Research/{topic_name}/
  _meta/
    config.json
    keyword_map.json
    progress.tsv
  sources/
  synthesis/
```

디렉토리가 이미 존재하면 → config.json을 로드하여 상태를 확인한다.

### 4. Resume 판정

- `config.json`의 status가 `"completed"` → "이미 완료된 리서치입니다. 재수집하려면 --force를 사용하세요." 안내 후 종료.
  - 단, `$ARGUMENTS`에 `--force`가 있으면 status를 `"in_progress"`로 리셋하고 계속.
- status가 `"in_progress"` → keyword_map.json에서 미수집 키워드를 확인하고 Phase 2부터 이어서 수집.
- config.json이 없으면 → 신규 생성.

### 5. config.json 초기화

```json
{
  "topic": "{주제}",
  "input_raw": "/autoresearch {$ARGUMENTS}",
  "created_at": "{ISO timestamp}",
  "status": "in_progress",
  "params": {
    "min_sources": 30,
    "target_sources": 60,
    "coverage_threshold": 0.8
  },
  "keywords": {
    "seed": [],
    "expanded": [],
    "covered": [],
    "uncovered": []
  },
  "stats": {
    "total_sources": 0,
    "valid_sources": 0,
    "keyword_coverage": 0,
    "total_content_chars": 0
  }
}
```

### 6. 셋업 요약 출력

```
AutoResearch 시작
주제: {topic}
디렉토리: 01_Research/{topic_name}/
최소 소스: {min_sources}개
목표 소스: {target_sources}개
커버리지 기준: {coverage_threshold * 100}%
```

---

## Phase 1: PLAN — Agent "research-planner" 호출

Agent 도구로 `research-planner` agent를 호출한다.

> **`subagent_type: "research-planner"`** — 다른 agent를 사용하지 않는다.

**prompt:**
```
"{주제}" 주제에 대한 키워드 맵과 검색 전략을 수립하라.

주제: {topic}
seed 키워드: {seed keywords 또는 "없음"}
URL: {URL 목록 또는 "없음"}
출력 디렉토리: 01_Research/{topic_name}/

01_Research/ 하위에 기존 관련 자료가 있으면 확인하여 사전 매핑하라.
keyword_map.json을 01_Research/{topic_name}/_meta/keyword_map.json에 저장하라.
config.json의 keywords.seed/expanded를 업데이트하라.
```

**결과 처리:**
- keyword_map.json을 읽어 클러스터 목록을 파악한다.
- 총 키워드 수와 클러스터 수를 사용자에게 보고한다.

---

## Phase 2: COLLECT — Agent "web-collector" 반복 호출

> **`subagent_type: "web-collector"`** — 다른 agent를 사용하지 않는다.

이 Phase에서는 **웹 자료와 논문 자료를 모두 수집**한다. web-collector agent가 두 가지를 병행 처리한다.

### 수집 루프

```
WHILE NOT stop_condition:
  1. keyword_map.json에서 미수집 클러스터 선택
     - status가 "uncovered"인 키워드가 포함된 클러스터 우선
  2. 현재 sources/ 파일 수를 카운트하여 시작 번호 결정
  3. Agent "web-collector" 호출 (해당 클러스터)
  4. 수집 결과 반영:
     - sources/ 파일 수 재카운트
     - config.json stats 갱신
     - keyword_map.json에서 매칭된 키워드의 status를 "covered"로 변경
     - config.json keywords.covered/uncovered 갱신
  5. Stop 조건 체크
  6. 중간 상태 출력
```

### web-collector 호출 prompt

```
클러스터 "{cluster_name}" ({cluster_id})의 웹+논문 자료를 수집하라.

대상 키워드:
{keyword별 primary + variants + search_queries + paper_queries 목록}

직접 수집 URL: {있으면 목록, 없으면 "없음"}
출력 디렉토리: 01_Research/{topic_name}/
소스 번호 시작: {current_count + 1}

sources/{NNN}_{name}.md 형식으로 저장하라.
_meta/progress.tsv에 로그를 추가하라.

웹 자료와 논문 자료를 모두 수집하라.
```

### Stop 조건

아래 중 하나라도 만족하면 수집 루프를 종료한다:

1. `valid_sources >= min_sources` AND `keyword_coverage >= coverage_threshold`
2. `valid_sources >= target_sources` (강제 상한)
3. 미수집 클러스터가 없음

### 중간 상태 출력

```
수집 진행: {N}개 소스 (웹 {W}개 / 논문 {P}개), 커버리지 {X}%, 남은 클러스터 {M}개
```

---

## Phase 3: SYNTHESIZE — Agent "source-synthesizer" 호출

Agent 도구로 `source-synthesizer` agent를 호출한다.

> **`subagent_type: "source-synthesizer"`** — 다른 agent를 사용하지 않는다.

**prompt:**
```
"{주제}" 주제의 수집 자료를 종합 분석하라.

출력 디렉토리: 01_Research/{topic_name}/

소스가 50개를 초과하면 클러스터별 중간 종합(Phase A)을 먼저 수행한 뒤 최종 종합(Phase B)을 작성하라.
소스가 50개 이하이면 바로 최종 종합을 작성하라.

출력물:
1. keyword_findings.md — 키워드별 발견 사항
2. topic_overview.md — 전체 주제 종합 요약 + 교재 챕터 구조 제안
3. gap_analysis.md — 미충족 영역 분석

synthesis/ 디렉토리에 저장하라.
config.json status를 "completed"로 업데이트하라.
```

---

## Phase 4: REPORT — 완료 보고

```
수집 결과 요약:
  주제: {topic}
  소스: {total_sources}개 수집 / {valid_sources}개 유효
    웹: {web_count}개, 논문: {paper_count}개
  키워드 커버리지: {coverage}%
  미충족 영역: {uncovered keywords 리스트}

산출물:
  01_Research/{topic_name}/synthesis/topic_overview.md  — 종합 요약
  01_Research/{topic_name}/synthesis/keyword_findings.md — 키워드별 발견
  01_Research/{topic_name}/synthesis/gap_analysis.md     — 갭 분석

다음 단계:
  - /curriculum {topic} 으로 커리큘럼 생성 가능
  - gap_analysis.md에서 부족한 영역 확인 후 추가 수집 가능
```

---

## 핵심 원칙

1. **Orchestrator는 메타데이터만 관리**: config.json, keyword_map.json만 읽고 쓴다. 소스 본문은 subagent가 처리.
2. **Context 격리**: 무거운 본문 처리는 전부 subagent에 위임. agent 간 데이터 교환은 파일 시스템 경유.
3. **전용 Agent 사용**: 반드시 `research-planner`, `web-collector`, `source-synthesizer`를 subagent_type으로 지정한다.
4. **웹+논문 병행 수집**: web-collector가 공식 문서/블로그와 학술 논문을 모두 수집한다.
5. **Resume 지원**: 중단 후 재실행 시 미수집 키워드부터 이어서 수집.
6. **Fallback**: firecrawl 실패 시 WebSearch/WebFetch로 대체.
7. **품질 기준**: 소스당 500자 이상, 키워드 커버리지 80% 이상.
