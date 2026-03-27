# AutoResearch Skill 구현 계획

작성일: 2026-03-27

## 목적

자연어 입력(주제, URL, 키워드)을 받아 **책 집필에 충분한 분량**의 자료를 자동으로 수집하고, `01_Research/{topic}/` 에 토픽별로 정리하여 저장하는 skill.

수집된 자료는 이후 `/curriculum` → `/autobook` 파이프라인의 입력이 된다.

---

## 1. 분량 기준

참고 벤치마크: `agentic_ai_papers/summaries/agent_memory_pdfs/` (PDF 72개, 텍스트 포함 총 118파일)

| 기준 | 값 | 근거 |
|------|-----|------|
| **최소 소스 수** | 30개 | PDF 72개의 ~40%. 웹 문서는 논문보다 밀도가 낮으므로 하한 |
| **목표 소스 수** | 50~70개 | 벤치마크와 유사한 커버리지 확보 |
| **최소 고유 키워드 커버리지** | 80% | 초기 키워드 맵에서 80% 이상이 1개+ 소스에 매핑되어야 함 |
| **소스당 최소 콘텐츠** | 500자 이상의 추출 본문 | 빈 스크랩이나 에러 페이지 제외 |
| **Stop 조건** | (소스 수 >= 30) AND (키워드 커버리지 >= 80%) |

> 사용자가 `/autoresearch {주제} --min 20 --target 40` 같은 형태로 오버라이드 가능하도록 기본값만 설정.

---

## 2. 입력 형태

자연어 형태로 유연하게 수용한다:

```
/autoresearch Agentic AI 메모리 시스템
/autoresearch https://arxiv.org/abs/2401.xxxxx
/autoresearch "knowledge graph" "agent memory" "RAG"
/autoresearch Agentic AI Trends --min 20 --target 40
```

### 입력 파싱 규칙

| 패턴 | 해석 |
|------|------|
| `https://...` | URL → 직접 scrape 후 관련 키워드 자동 추출 |
| `"quoted terms"` | 키워드 → 검색 쿼리로 사용 |
| 그 외 텍스트 | 주제 → 키워드 확장 후 검색 |
| `--min N` | 최소 소스 수 오버라이드 |
| `--target N` | 목표 소스 수 오버라이드 |

---

## 3. 산출물 구조

```
01_Research/
  {topic_name}/                       ← 예: Agentic_AI_Memory
    _meta/
      config.json                     ← 입력 파라미터, 키워드맵, 진행상태
      keyword_map.json                ← 키워드 → 소스 매핑 (커버리지 추적)
      progress.tsv                    ← 소스별 수집 로그
    sources/
      001_{source_name}.md            ← 개별 소스 (본문 + 메타데이터)
      002_{source_name}.md
      ...
    synthesis/
      topic_overview.md               ← 전체 주제 종합 요약
      keyword_findings.md             ← 키워드별 발견 사항 정리
      gap_analysis.md                 ← 미충족 키워드/영역 분석
```

### 개별 소스 파일 포맷 (`sources/NNN_{name}.md`)

```markdown
---
source_id: 001
title: "..."
url: "..."                            ← 또는 file_path (로컬 논문)
type: web | paper | docs | blog
scraped_at: 2026-03-27T10:00:00
keywords: ["keyword1", "keyword2"]
content_length: 3200
---

# {title}

{추출된 본문 — markdown}
```

### config.json 스키마

```json
{
  "topic": "Agentic AI Memory",
  "input_raw": "/autoresearch Agentic AI 메모리 시스템",
  "created_at": "2026-03-27T10:00:00",
  "status": "in_progress | completed | stopped",
  "params": {
    "min_sources": 30,
    "target_sources": 60,
    "coverage_threshold": 0.8
  },
  "keywords": {
    "seed": ["agent memory", "..."],
    "expanded": ["episodic memory", "working memory", "..."],
    "covered": ["agent memory", "..."],
    "uncovered": ["..."]
  },
  "stats": {
    "total_sources": 45,
    "valid_sources": 42,
    "keyword_coverage": 0.85,
    "total_content_chars": 250000
  }
}
```

### keyword_map.json 스키마

```json
{
  "keywords": [
    {
      "id": "kw_001",
      "primary": "agent memory",
      "variants": {
        "synonyms": ["LLM memory", "memory module"],
        "abbreviations": [],
        "broader": ["AI memory systems"],
        "narrower": ["episodic memory", "working memory", "semantic memory"],
        "related_tech": ["MemGPT", "memory bank", "context window"],
        "translations": ["에이전트 메모리"]
      },
      "search_queries": [
        "agent memory architecture",
        "LLM memory module design",
        "에이전트 메모리 시스템"
      ],
      "cluster": "memory_core",
      "status": "uncovered",
      "matched_sources": []
    }
  ],
  "clusters": [
    {
      "id": "memory_core",
      "name": "메모리 핵심 구조",
      "keywords": ["kw_001", "kw_002", "kw_003"]
    }
  ]
}
```

> **핵심:** 각 키워드의 `variants`를 Phase 2에서 검색 쿼리로 활용한다.
> 원본 키워드로만 검색하면 놓치는 자료를, 동의어/약어/상위·하위 개념으로 보완 수집한다.

---

## 4. 워크플로우 아키텍처

Claude Code 기능별 역할 분담 (가이드 기준):

| 기능 | 역할 | 근거 |
|------|------|------|
| **Skill** (`/autoresearch`) | Orchestrator — 루프 제어, 상태 관리 | 재사용 가능한 워크플로우 정의 |
| **Subagent** (`research-planner`) | 키워드 확장, 검색 전략 수립 | 독립 context에서 분석 작업 격리 |
| **Subagent** (`web-collector`) | firecrawl로 웹 수집 + 정제 | 대량 출력을 메인 context에서 격리 |
| **Subagent** (`source-synthesizer`) | 수집 자료 종합, 갭 분석 | 전체 소스를 읽는 무거운 작업 격리 |
| **Hook** (PostToolUse) | 수집 파일 저장 시 자동 키워드맵 업데이트 | 결정론적 상태 추적 보장 |
| **CLAUDE.md/rules** | 수집 품질 기준, 톤 규칙 | 매 세션 자동 로드 |

---

## 5. 상세 워크플로우

### Phase 0: PARSE — 입력 해석 (inline, Skill 내부)

```
1. $ARGUMENTS를 파싱하여 주제/URL/키워드/옵션 분리
2. 01_Research/{topic_name}/ 디렉토리 구조 생성
3. config.json 초기화
4. 기존 디렉토리가 있으면 → config.json 로드하여 이어서 수집 (resume)
```

### Phase 1: PLAN — Agent "research-planner" 호출

**목적:** 주제를 구조화된 키워드 맵과 검색 전략으로 확장

**Agent 정의:**
```yaml
---
name: research-planner
model: sonnet
tools: Read, Grep, Glob, WebSearch, Write
maxTurns: 15
---
```

**프로세스:**
```
1. 입력 주제/키워드에서 핵심 개념 축 도출
2. 개념 축별 하위 키워드 확장 (10~20개 수준)
3. 각 키워드에 대해 Semantic Variants 생성:
   - 동의어 (synonym): "agent memory" ↔ "LLM memory"
   - 약어/풀네임: "RAG" ↔ "retrieval augmented generation"
   - 상위 개념 (broader): "agent memory" → "AI memory systems"
   - 하위 개념 (narrower): "agent memory" → "episodic memory", "working memory"
   - 관련 기술명 (related): "agent memory" → "MemGPT", "memory bank"
   - 영문/한글 쌍: "지식 그래프" ↔ "knowledge graph"
4. 키워드 간 관계 그래프 생성 (교재 챕터 구조의 씨앗)
5. 검색 전략 수립:
   - 각 키워드별 추천 검색 쿼리 (원본 + variants 조합)
   - URL이 입력으로 주어졌으면 해당 사이트 중심 크롤 전략
   - 로컬 논문 기지(agentic_ai_papers/) 활용 가능 여부 확인
6. keyword_map.json 초기 작성 (variants 포함)
7. config.json의 keywords.seed/expanded 업데이트
```

**결과:** keyword_map.json + 검색 전략 (~200 tokens 요약 반환)

### Phase 2: COLLECT — Agent "web-collector" 반복 호출

**목적:** 키워드별로 웹 자료 수집. 가장 무거운 단계.

**Agent 정의:**
```yaml
---
name: web-collector
model: sonnet
tools: Read, Write, Bash, WebSearch, WebFetch, mcp__firecrawl__firecrawl_search, mcp__firecrawl__firecrawl_scrape, mcp__firecrawl__firecrawl_crawl, mcp__firecrawl__firecrawl_map, mcp__firecrawl__firecrawl_check_crawl_status
maxTurns: 30
---
```

**호출 단위:** 키워드 클러스터별 (관련 키워드 3~5개 묶음)

**프로세스 (각 호출마다):**
```
1. 할당된 키워드 클러스터에 대해 유의어/관련어 확장 (Semantic Expansion)
   - 각 키워드마다 동의어, 약어, 상위/하위 개념, 관련 기술명을 2~5개 생성
   - 예: "agent memory" → ["agent memory", "LLM memory", "memory module",
          "episodic memory for agents", "agent context management"]
   - 예: "RAG" → ["RAG", "retrieval augmented generation",
          "retrieval-augmented LLM", "retrieve and generate"]
   - 확장된 키워드는 keyword_map.json의 variants 필드에 기록
2. 원본 키워드 + 확장 키워드 각각으로 검색 실행
   - firecrawl_search(원본 키워드, limit=10)
   - firecrawl_search(확장 키워드 조합, limit=5) × 1~2회
   - 결과를 합산하고 URL 기준으로 중복 제거
   - 결과 중 관련도 높은 URL 선별
3. 선별된 URL을 firecrawl_scrape로 본문 추출
   - formats: ["markdown"], onlyMainContent: true
   - 500자 미만이면 폐기
4. URL 입력이 있었으면 firecrawl_map + firecrawl_crawl로 사이트 구조 탐색
   - 관련 하위 페이지도 수집
5. 로컬 논문 기지에 관련 논문이 있으면:
   - summaries/ 요약 파일 읽기
   - 필요시 PDF 텍스트 추출본에서 키워드 검색
   - 논문 내용을 소스 파일로 저장 (type: paper)
6. 각 소스를 sources/NNN_{name}.md로 저장
   - 소스 frontmatter의 keywords 필드에 원본+확장 키워드 중 매칭된 것 기록
7. progress.tsv에 로그 추가
```

**Orchestrator 루프 (Skill 내부):**
```
WHILE NOT stop_condition:
  1. keyword_map.json에서 미수집 키워드 클러스터 선택
  2. Agent "web-collector" 호출 (해당 클러스터)
  3. config.json 갱신 (stats, covered keywords)
  4. Stop 조건 체크:
     - total_sources >= min_sources AND coverage >= threshold → STOP
     - total_sources >= target_sources → STOP (강제)
     - 미수집 키워드가 없음 → STOP
  5. 중간 상태 출력:
     "수집 진행: {N}개 소스, 커버리지 {X}%, 남은 클러스터 {M}개"
```

### Phase 3: SYNTHESIZE — Agent "source-synthesizer" 호출

**목적:** 수집된 소스를 종합하여 교재 집필에 바로 쓸 수 있는 형태로 정리

**Agent 정의:**
```yaml
---
name: source-synthesizer
model: opus
tools: Read, Write, Glob, Grep
maxTurns: 20
---
```

**프로세스:**
```
1. sources/ 전체 파일 스캔
2. 키워드별 발견 사항 정리 → keyword_findings.md
   - 각 키워드에 대해 어떤 소스에서 어떤 정보를 얻었는지
   - 소스 간 합의/불일치 사항
3. 전체 주제 종합 요약 → topic_overview.md
   - 주제의 핵심 개념, 하위 영역, 현재 트렌드
   - 교재 챕터 구조 제안 (curriculum 생성의 사전 입력)
4. 갭 분석 → gap_analysis.md
   - 커버리지 미달 키워드
   - 추가 조사 필요 영역
   - 소스 품질이 낮은 영역
5. config.json status를 "completed"로 업데이트
```

### Phase 4: REPORT — 완료 보고 (inline, Skill 내부)

```
수집 결과 요약:
  주제: {topic}
  소스: {N}개 수집 / {M}개 유효
  키워드 커버리지: {X}%
  미충족 영역: {리스트}

다음 단계:
  - /curriculum {topic} 으로 커리큘럼 생성 가능
  - 01_Research/{topic}/synthesis/topic_overview.md에서 종합 요약 확인
  - 01_Research/{topic}/synthesis/gap_analysis.md에서 부족한 영역 확인
```

---

## 6. 구현할 파일 목록

### 신규 생성

| 파일 | 유형 | 설명 |
|------|------|------|
| `.claude/skills/autoresearch/SKILL.md` | Skill | Orchestrator 스킬 정의 |
| `.claude/agents/research-planner.md` | Agent | 키워드 확장 + 검색 전략 |
| `.claude/agents/web-collector.md` | Agent | firecrawl 기반 웹 수집 |
| `.claude/agents/source-synthesizer.md` | Agent | 수집 자료 종합 |
| `.claude/rules/research-collecting.md` | Rule | 수집 시 품질 기준 (path scope: 01_Research/) |

### 수정 필요

| 파일 | 변경 내용 |
|------|-----------|
| `CLAUDE.md` | 프로젝트 구조에 01_Research/ 설명 추가, 워크플로우에 `/autoresearch` 추가 |
| `.claude/settings.json` | (선택) PostToolUse hook으로 소스 저장 시 자동 카운팅 |
| `.claude/skills/curriculum/SKILL.md` | 01_Research/ 자료 참조 경로 안내 추가 |

---

## 7. Agent 간 Context 격리 전략

```
Skill (Orchestrator)
  │
  ├─ [Phase 1] research-planner (sonnet, 15턴)
  │    └─ 산출: keyword_map.json
  │
  ├─ [Phase 2] web-collector × N회 (sonnet, 30턴)
  │    └─ 산출: sources/NNN_*.md (파일 시스템 경유)
  │    └─ 클러스터별 호출 → 각 호출이 독립 context
  │    └─ Orchestrator는 config.json만 읽어 진행률 추적
  │
  └─ [Phase 3] source-synthesizer (opus, 20턴)
       └─ 산출: synthesis/*.md
```

**핵심 원리:**
- Orchestrator(Skill)는 메타데이터(config.json, keyword_map.json)만 관리 → context 경량
- 무거운 본문 처리는 전부 subagent에 위임 → context 오염 방지
- Agent 간 데이터 교환은 **파일 시스템** 경유 (subagent끼리 직접 통신 불가)
- web-collector를 클러스터별로 분리 호출 → 한 번에 소스 5~10개씩 수집, 각 호출 독립

---

## 8. Firecrawl MCP 활용 전략

| 도구 | 용도 | 호출 시점 |
|------|------|-----------|
| `firecrawl_search` | 키워드 기반 웹 검색 | Phase 2 — 각 키워드 클러스터별 |
| `firecrawl_scrape` | 단일 URL 본문 추출 | Phase 2 — 검색 결과 URL 또는 사용자 제공 URL |
| `firecrawl_map` | 사이트 구조 탐색 | Phase 2 — URL 입력 시 관련 페이지 발견 |
| `firecrawl_crawl` | 다중 페이지 크롤링 | Phase 2 — 문서 사이트 전체 수집 (limit 제한) |

### 검색 → 스크랩 2단계 워크플로우 (Semantic Expansion 포함)

```
1. keyword_map.json에서 대상 키워드의 primary + variants 로드
2. 다중 쿼리 검색:
   a. firecrawl_search(primary 키워드, limit=10)           → URL Set A
   b. firecrawl_search(synonym/related 조합, limit=5)      → URL Set B
   c. firecrawl_search(한글 번역 키워드, limit=5)           → URL Set C (선택)
3. URL 합산 + 중복 제거 → 최종 URL 목록 (10~15개)
4. 관련도 높은 URL 5~7개 선별
5. firecrawl_scrape(url, formats=["markdown"], onlyMainContent=true) × 5~7회
6. 500자 미만 결과 폐기
7. 유효 결과를 sources/ 파일로 저장
8. 매칭된 키워드(primary + 어떤 variant로 발견됐는지) 기록
```

> 예시: "RAG" 키워드 검색 시
> - 1차: `"RAG agent"` → 주요 결과
> - 2차: `"retrieval augmented generation LLM"` → 1차에서 놓친 학술/기술 문서
> - 3차: `"검색 증강 생성"` → 한글 자료 보완

### URL 입력 시 사이트 탐색 워크플로우

```
1. firecrawl_scrape(url) → 메인 페이지 본문 추출
2. firecrawl_map(url, search="관련키워드") → 하위 페이지 URL 발견
3. 관련 URL을 firecrawl_scrape로 개별 수집
4. 또는 firecrawl_crawl(url, limit=20, maxDiscoveryDepth=2) 으로 일괄 수집
```

---

## 9. Resume (이어서 수집) 지원

```
/autoresearch Agentic AI Memory    ← 01_Research/Agentic_AI_Memory/ 이미 존재

1. config.json 로드
2. status가 "completed"이면 → "이미 완료된 리서치입니다. 재수집하려면 --force 옵션을 사용하세요."
3. status가 "in_progress"이면 →
   - keyword_map.json에서 미수집 키워드 확인
   - sources/ 파일 수 카운트
   - Phase 2부터 이어서 수집
4. progress.tsv 로그를 이어서 기록
```

---

## 10. autobook 파이프라인 연계

```
/autoresearch {주제}          ← 자료 수집
  ↓
01_Research/{topic}/          ← 수집 결과 저장
  ↓
/curriculum {책이름}          ← 커리큘럼 생성 시 01_Research/ 참조
  ↓
02_Books/{책이름}/            ← 교재 생성
  ↓
/autobook {책이름}            ← 자율 집필 루프
```

**curriculum skill 연계:**
- `/curriculum` 실행 시 `01_Research/{관련주제}/synthesis/topic_overview.md`를 curriculum-researcher에게 사전 컨텍스트로 전달
- 키워드맵을 활용하여 더 정밀한 토픽 분할 가능

**autobook skill 연계:**
- topic-researcher가 `01_Research/` 소스를 논문 기지와 동급으로 참조
- 이미 수집된 자료가 있으면 웹 검색 최소화 → 속도 향상

---

## 11. 구현 우선순위

| 순서 | 작업 | 예상 규모 |
|------|------|-----------|
| **1** | Skill 파일 작성 (`autoresearch/SKILL.md`) | 중 |
| **2** | Agent 3개 작성 (planner, collector, synthesizer) | 중 |
| **3** | Rule 파일 작성 (`research-collecting.md`) | 소 |
| **4** | CLAUDE.md 업데이트 | 소 |
| **5** | curriculum skill에 01_Research/ 연계 추가 | 소 |
| **6** | (선택) Hook 추가 — 소스 저장 시 자동 카운팅 | 소 |
| **7** | 테스트 — 소규모 주제로 end-to-end 검증 | 중 |
