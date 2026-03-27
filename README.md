# AutoBook

autoresearch의 "자율 실험 루프"를 기술 교재 집필에 적용하는 프로젝트.
Claude Code가 커리큘럼 생성부터 단원 작성, 자동 평가, 수정까지 자율적으로 수행합니다.

## 사용 시나리오

### A. 수동 모드 — 학습용, 깊이 중시

사용자가 직접 각 토픽을 확인하며 한 단원씩 진행합니다.

```
1. /curriculum 딥러닝입문      ← 커리큘럼 생성 (50개+ 토픽)
2. /validate-curriculum        ← 커리큘럼 검증
3. /next-topic                 ← 다음 미작성 토픽 확인
4. /write-topic 1.1.1          ← 단원 작성
5. /review-topic 1.1.1         ← 7개 체크리스트 리뷰
6. /progress                   ← 진행률 대시보드
7. → 3번으로 돌아가 반복
```

### B. 자율 모드 — 초안 대량 생성, 커버리지 중시

에이전트가 작성-평가-수정을 반복합니다. 사용자가 중단할 때까지 멈추지 않습니다.

```
1. /curriculum 딥러닝입문      ← 커리큘럼 생성 (이미 있으면 생략)
2. /autobook 딥러닝입문        ← 자율 루프 시작
   ┌─ ① 다음 미작성 토픽 선택
   │  ② 웹 조사 + 단원 작성 + git commit
   │  ③ 7점 만점 자동 채점
   │  ④ 7점→pass / 5~6점→revise(최대3회) / ≤4점→fail(재작성)
   │  ⑤ results.tsv 기록
   └─ ⑥ 다음 토픽으로 → ①반복
3. 사용자가 수동 중단
4. results.tsv + 생성된 파일 확인
```

### C. 혼합 모드

자율 모드로 초안을 대량 생성한 뒤, 수동 모드로 품질을 다듬습니다.

```
1. /autobook 딥러닝입문        ← 밤새 자율 집필
2. (다음 날) /progress         ← 결과 확인
3. results.tsv에서 낮은 점수 토픽 확인
4. /review-topic 2.3.1         ← 문제 토픽 리뷰
5. 직접 수정 또는 /write-topic으로 재작성
```

## 스킬

| 스킬 | 역할 |
|------|------|
| `/curriculum {책이름}` | 커리큘럼(curriculum.json) 생성 |
| `/validate-curriculum` | 커리큘럼 스키마/DAG 검증 |
| `/next-topic` | 다음 미작성 토픽 안내 |
| `/write-topic {a.b.c}` | 특정 토픽 단원 작성 |
| `/review-topic {a.b.c}` | 7개 항목 체크리스트 리뷰 |
| `/progress` | Phase/섹션별 진행률 대시보드 |
| `/autobook {책이름}` | 자율 집필 루프 |

## 프로젝트 구조

```
Rules/                         ← 불변 규칙 (수정 금지, 훅으로 보호)
.claude/
  hooks/protect-rules.sh       ← Rules/ 수정 차단 스크립트
  rules/                       ← 자동 리마인더 (편집 시 로드)
  skills/                      ← 7개 스킬 정의
  settings.json                ← 훅 설정
  settings.local.json          ← 권한 설정
교재/{책이름}/                   ← 산출물
  curriculum.json
  results.tsv                  ← 자율 루프 결과 로그
  {a}_{Phase}/{a.b}_{섹션}/{a.b.c}_{토픽}.md
```

## 평가 시스템

자율 모드에서 각 단원을 7개 항목으로 자동 채점합니다.

| # | 항목 | 배점 |
|---|------|------|
| 1 | 경로/파일명 규칙 | 1점 |
| 2 | learning_content 커버리지 | 1점 |
| 3 | learning_objectives 검증 가능 | 1점 |
| 4 | 선수 범위 준수 | 1점 |
| 5 | 톤앤매너 준수 | 1점 |
| 6 | 배경 우선 설명 | 1점 |
| 7 | 본문 구조 | 1점 |

- **7점**: PASS — 다음 토픽으로
- **5~6점**: REVISE — 수정 후 재평가 (최대 3회)
- **4점 이하**: FAIL — 삭제 후 재작성
