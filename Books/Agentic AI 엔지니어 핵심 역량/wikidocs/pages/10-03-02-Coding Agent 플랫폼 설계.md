# 10.3.2 Coding Agent 플랫폼 설계

Phase 10의 마지막 사례는 Coding Agent 플랫폼입니다. GitHub Copilot Workspace, Cursor Agent, Devin, Claude Code 같은 제품들이 같은 문제 공간을 다릅니다. 이 단원은 'Issue 하나가 들어오면 패치를 만들고 테스트를 돌려 PR을 띄우는 Agent를 사내에 만든다고 가정하고 화이트보드에 설계하세요'라는 면접 케이스를 압축해 다룹니다. 핵심은 repo 인덱싱, issue 이해, patch 생성, sandbox 테스트, PR 자동화의 다섯 단계와 그 한계입니다.

요구사항을 숫자로 고정합니다. 한 회사의 repo 200개, 평균 코드 라인 50만, 일 issue 1,000건, 그중 자동 해결 시도 대상 200건, 한 시도의 wall-clock 30분 한도, 테스트 시간 평균 5분, 평균 LLM 비용 시도당 1.5달러, 자동 머지 비율 목표 20%입니다. 이 숫자가 인덱싱 빈도와 sandbox 동시성을 정합니다.

이 위에 고수준 다이어그램을 그립니다.

```
   [Issue Tracker]                  [Git Repo]
        |                                |
        v                                v
   +----------+                  +---------------+
   | Issue    |                  | Repo Indexer  |
   | Listener |                  | (AST + Embed) |
   +----+-----+                  +-------+-------+
        |                                |
        v                                v
   +-----------------+         +------------------+
   | Issue Analyzer  |<--------|  Code Search API |
   |  (재현·분류)    |         |  (path + symbol) |
   +--------+--------+         +------------------+
            |
            v
   +-----------------+
   | Patch Planner   |---> 후보 파일 목록 + 변경 계획
   +--------+--------+
            |
            v
   +-----------------+
   | Patch Generator |---> diff (LLM)
   +--------+--------+
            |
            v
   +-----------------+        +------------------+
   |  Sandbox 빌더   |------->|  Test Runner     |
   | (컨테이너 격리) |        |  (lint·unit·e2e) |
   +--------+--------+        +---------+--------+
            |                           |
            +-----------+---------------+
                        v
                +----------------+
                |  Verdict       |
                | pass / fail    |
                +-------+--------+
                        |
                        v
                +----------------+
                | PR Manager     |
                | (draft·review) |
                +----------------+
```

다이어그램의 좌측 두 박스가 데이터 기반입니다. **Repo Indexer**는 두 종류의 인덱스를 만듭니다. 하나는 AST 기반 symbol 인덱스로 함수·클래스·모듈 단위의 위치와 시그니처를 들고 있습니다. 다른 하나는 코드 chunk 임베딩 인덱스로 자연어 질의에서 관련 코드를 찾을 때 사용합니다. AST 인덱스는 정확한 호출 그래프와 정의-사용 관계를 답할 수 있고, embedding 인덱스는 'Stripe 결제 실패를 처리하는 곳'처럼 의미 기반 검색에 답합니다. 둘이 함께여야 Coding Agent가 정상 동작합니다.

**Repo 인덱싱과 코드 임베딩**의 빈도는 CDC 기반이 자연스럽습니다. push 이벤트가 오면 변경된 파일 단위로 인덱스를 갱신합니다. 50만 라인 repo를 매번 통째로 다시 임베딩하면 시간과 비용이 무너집니다. 파일·함수 단위 incremental 갱신이 표준입니다. chunk 단위는 함수 또는 클래스 한 단위가 흔합니다. 너무 작게 자르면 호출 맥락이 끊기고, 너무 크면 임베딩의 의미가 흐려집니다.

다음은 **Issue 이해 단계**입니다. Issue Analyzer는 issue 본문, 첨부 로그, 재현 절차를 입력으로 받아 세 가지를 만듭니다. 하나, 분류 라벨(bug, feature, refactor, infra). 둘, 후보 영역 키워드 5~10개. 셋, 재현 가능성 점수입니다. 재현이 어려운 issue를 무작정 자동 해결하면 환각 패치가 늘어납니다. 재현 점수가 임계값 미만이면 사람에게 돌려보내고, 이상이면 다음 단계로 보냅니다. 흔히 빠뜨리는 단계가 이 게이트입니다. 분류·재현 단계 없이 모든 issue를 Patch Planner에 넣으면 자동 머지율은 5% 밑으로 떨어집니다.

**Patch Planner**는 issue와 코드 검색 결과를 합쳐 변경 계획을 만듭니다. 출력은 자유 텍스트가 아니라 구조화된 계획입니다. 'edit `payments/stripe.py` 함수 `handle_charge_failed` 본문 수정, 새 테스트 `tests/test_stripe.py::test_charge_failed_retry` 추가' 같은 형태입니다. 구조화가 중요한 이유는 다음 박스인 Patch Generator가 명확한 입력으로 동작해야 환각을 줄일 수 있기 때문입니다. Planner가 후보 파일 5개를 넘으면 issue를 분할하거나 사람 검토로 보내는 정책도 함께 둡니다.

**Patch Generator**는 LLM 호출로 실제 diff를 만듭니다. 입력은 Planner의 계획, 해당 파일의 현재 본문, 그리고 인접 호출자 함수의 본문입니다. 출력은 unified diff 형식으로 강제합니다. 자연어 응답을 받아 코드를 추출하는 방식은 실패율이 높습니다. diff 적용이 실패하면 한 번 self-repair로 재시도하고, 두 번 실패하면 후보를 폐기합니다. 한 turn당 diff 생성 횟수는 보통 2~3회로 제한해 비용 폭주를 막습니다.

핵심 안전장치는 **Sandbox에서 Test 실행**입니다. patch는 절대 main repo에 직접 쓰지 않습니다. 각 시도는 격리된 컨테이너에서 새 워크트리에 patch를 적용한 뒤 빌드, lint, unit test, 필요 시 e2e test를 차례로 돌립니다. 컨테이너 이미지는 repo의 dev container 정의를 그대로 따르도록 강제합니다. 환경 차이가 곧 패치 사고로 이어지기 때문입니다. test runner는 다음 세 결과를 만듭니다. 빌드 성공 여부, 테스트 통과 비율, 회귀 테스트 목록. 회귀가 하나라도 발생하면 verdict는 즉시 fail로 표시합니다.

sandbox는 자원 한도를 가집니다. CPU·메모리·디스크·실행 시간이 모두 cgroup으로 묶입니다. 한 시도 30분 한도를 넘기면 컨테이너를 강제 종료합니다. 보안 측면에서 sandbox는 외부 네트워크 접근을 기본 차단하고, 패키지 mirror와 회사 내부 API만 화이트리스트로 열어 둡니다. 외부 패키지 설치가 임의로 가능한 sandbox는 supply chain 공격의 통로가 됩니다.

**PR Manager**가 마지막 박스입니다. verdict가 pass면 draft PR을 자동 생성합니다. PR 본문에는 다음을 포함합니다. 원본 issue 링크, Planner가 만든 변경 계획, 변경 라인 수, 통과한 테스트 목록, 시도 비용. 사람 reviewer는 이 다섯 항목으로 빠르게 머지 여부를 결정할 수 있습니다. verdict가 fail이면 PR을 만들지 않고 trace를 사람에게 알립니다. 'fail을 PR로 띄우지 않는다'가 신뢰의 핵심입니다.

여기서 **PR 자동화 한계**를 솔직히 답합니다. 셋입니다. 첫째, 명세가 모호한 issue는 어떤 Agent도 정답을 만들지 못합니다. 자동 머지율 상한은 issue 품질이 결정합니다. 둘째, 큰 리팩토링은 한 번에 시도해서는 안 됩니다. 변경 라인 200줄이 넘는 자동 PR은 사람 reviewer가 신뢰하지 못합니다. 셋째, 보안과 권한이 얽힌 코드는 자동 영역에서 제외합니다. payment, auth, secret 경로의 파일은 modify 후보에서 hard exclude를 두는 편이 안전합니다. 이 세 한계를 솔직히 말하는 답이 'Coding Agent의 한계'를 묻는 면접 질문에 가장 잘 맞습니다.

운영 지표는 다섯입니다. `attempt_rate`(일 시도 수), `pass_rate`(verdict 통과 비율), `merge_rate`(사람이 머지한 비율), `regression_introduced`(머지 후 1주 내 회귀 발생 건수), `cost_per_merge`(머지된 PR당 LLM 비용). pass_rate가 50%여도 merge_rate가 10%면 reviewer 신뢰가 무너졌다는 신호입니다. 두 지표를 함께 봐야 시스템 상태가 보입니다.

면접 트레이드오프는 셋입니다. 첫째, **LLM 단일 호출 vs Agent 루프**. 한 번 호출로 큰 diff를 만들면 빠르지만 회귀가 잦고, ReAct 루프로 작은 변경을 반복하면 비용이 들지만 안정합니다. 보통 작은 변경 루프가 운영 결과가 좋습니다. 둘째, **인덱싱의 깊이**. 호출 그래프까지 정확히 들고 있으면 patch 품질이 오르지만 인덱서가 무거워집니다. 100만 라인 이하 repo는 풀 호출 그래프, 그 이상은 디렉토리 단위 abstraction만 두는 절충이 자연스럽습니다. 셋째, **자율성 vs human-in-the-loop**. 자동 머지는 신뢰가 충분한 영역에서만 허용합니다. 처음부터 draft PR만 만들고 사람이 머지하는 정책으로 시작해 신뢰가 누적될 때 자동 머지 허용 영역을 좁게 넓혀 갑니다.

확장 시나리오 한 줄씩. 멀티 언어 repo는 Indexer를 언어별 plugin 구조로 만듭니다. 모노레포는 패키지 단위 sandbox 격리를 강화합니다. 보안 사고 사후 대응에 쓰려면 'CVE 핫픽스 모드'를 별도 모드로 두고 더 빠른 단축 루트를 허용합니다. CI 통합은 PR Manager가 기존 CI 파이프라인 위에 얹는 형태로 추가합니다.

정리하면, Coding Agent 플랫폼은 Repo Indexer(AST+임베딩)·Issue Analyzer·Patch Planner·Patch Generator·Sandbox Test·PR Manager 여섯 박스를 한 줄로 잇고, 자동 머지율은 issue 품질·patch 크기·sandbox 신뢰의 곱으로 결정됩니다. 신뢰 누적 모델로 자동성을 늘려 가고, 보안·권한 코드는 hard exclude로 시작하는 보수 정책이 합격선입니다.

이 단원으로 Phase 10이 끝납니다. 지금까지 살펴본 RAG, Ingestion, Agent Platform, Multi-Agent, 1,000 Tool 시스템, LLM Gateway, Coding Agent 일곱 케이스는 면접 화이트보드에서 가장 자주 등장하는 설계 문제이자, 실무에서 그대로 만나는 시스템이기도 합니다. 다음 단원인 11.1.1부터는 이 시스템들을 안전하게 운영하기 위한 보안과 안전 주제로 넘어가, 가장 먼저 prompt injection의 공격과 방어를 다룹니다.
