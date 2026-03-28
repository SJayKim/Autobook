# Gap Analysis: LangSmith

## 커버리지 미달 영역

### 1. 보안과 접근 제어 (Access Control)

키워드 맵에 포함되지 않았으나 교재 필요성이 높은 영역이다. 소스에서 RBAC(역할 기반 접근 제어), 조직(Organization) 관리, 멤버 초대, API 키 로테이션 전략, Secret 관리 등에 대한 직접적인 설명이 거의 없다. Self-hosted 소스(052, 053)에서 인증 옵션(OAuth/SSO/Basic)은 언급되지만, 세밀한 권한 제어 방법은 다루지 않는다. 교재 작성 시 공식 문서의 "Organization & Access" 섹션을 별도로 조사할 필요가 있다.

### 2. CI/CD 파이프라인 통합

소스 전반에서 LangSmith를 개발 워크플로에 통합하는 방법이 단편적으로만 등장한다. GitHub Actions, GitLab CI 등 CI/CD 도구에서 `evaluate()`를 자동 실행하고 실험 결과를 기준으로 배포를 게이팅하는 패턴에 대한 전용 소스가 없다. 이 주제는 LangSmith를 ML 테스팅 파이프라인으로 활용하는 독자에게 중요하다.

### 3. LangSmith 요금제와 플랜별 기능 차이

Insights Agent가 Plus/Enterprise 전용이라는 정보(소스 045)와 Self-hosted가 Enterprise 전용이라는 정보(소스 052)는 있지만, Developer/Plus/Enterprise 플랜별 세부 기능 차이와 가격 구조를 설명하는 소스가 없다. 교재 독자가 플랜 선택 시 참고할 내용이 부족하다.

### 4. TypeScript/JavaScript SDK 심층 내용

소스 대부분이 Python SDK를 중심으로 예시를 제공한다. TypeScript/JavaScript SDK에 대해서는 동등한 기능이 존재함을 언급하는 수준에 그치며, TS 전용 패턴이나 Next.js/Node.js 환경에서의 통합 예시가 부족하다.

### 5. LangGraph Studio 디버깅

소스 056에서 "LangGraph Studio: 시각적 디버깅, 실시간 워크플로우 검사"를 언급하지만 전용 소스가 없다. Deployment와 연계된 시각적 디버깅 도구 활용 방법은 교재 독자에게 유용할 수 있다.

---

## 소스 품질이 낮은 영역

### 약한 소스 목록

**소스 026, 028**: content_length가 1,420자, 980자로 매우 짧다. Playground에서 평가 실행(026)과 Side-by-Side 비교(028)의 기본 정보는 충분하지만, 상세한 구성 단계나 엣지 케이스는 다루지 않는다.

**소스 037, 042, 043, 045**: 블로그/changelog 성격의 짧은 발표 자료(1,000~1,800자)다. 기능 소개와 동기 부여 내용은 좋지만, 단독으로는 교재 집필에 부족하다. 더 상세한 공식 문서 소스(035, 039, 041)와 함께 사용해야 한다.

**소스 027, 028, 030, 031**: Playground v2 발표(027)와 Prompt Tags(030, 031)에 대한 changelog 소스는 기능 개요를 제공하지만, 실제 사용 시나리오와 코드 예시가 부족하다. 소스 029가 이를 상당 부분 보완하지만, 프롬프트 관리 섹션은 실습 예시 추가 조사를 권장한다.

**소스 046**: ActiveWizards 블로그(외부 기고)로, LangSmith 공식 기능이 아닌 LangSmith + Prometheus + Grafana 통합 아키텍처를 다룬다. 내용 자체는 유효하나, LangSmith 자체 기능 설명으로 혼동하지 않도록 주의해야 한다.

---

## 추가 조사 권장 영역

### 우선순위 높음

**1. Polly 프롬프트 최적화 도구**
소스 026에서 한 줄로만 언급된다("Polly 도구를 활용하면 평가 실행 전에 프롬프트를 자동 최적화"). 실제 작동 방식, 최적화 알고리즘, 제약 조건 등에 대한 전용 소스가 없다. 교재에 포함하려면 공식 문서를 추가로 조사해야 한다.

**2. Agent Evaluation (Trajectory Evaluation) 심층 내용**
소스 025에서 "에이전트가 수행한 전체 단계 궤적 캡처"를 언급하지만, 구체적인 trajectory evaluator 구성 방법과 예시가 부족하다. Multi-turn Eval(소스 021)이 이와 관련되지만 별개의 주제로 보인다. Agentic 평가의 세부 방법론을 다루는 추가 소스가 필요하다.

**3. TypeScript SDK 통합 예시**
전반적으로 Python 편향이 강하다. TypeScript 사용자를 위한 별도 섹션을 포함하려면 TypeScript SDK 전용 튜토리얼과 예시를 추가로 수집해야 한다.

**4. LangSmith 보안 가이드**
API 키 관리, 데이터 암호화, 네트워크 분리(VPC 등) 관련 보안 설정에 대한 공식 문서를 조사해야 한다.

### 우선순위 보통

**5. 실제 운영 사례(Case Studies)**
LinkedIn, Uber, Klarna가 LangGraph Platform 베타 사용자로 언급되지만(소스 056) 구체적인 사용 패턴이 없다. 실무 적용 예시가 있으면 교재의 설득력이 높아진다.

**6. LangSmith와 Weights & Biases / MLflow 비교**
실험 관리 분야의 기존 도구와 비교하는 내용이 없다. 독자가 도구 선택 시 참고할 수 있는 비교 관점이 교재에 있으면 유용하다.

**7. 데이터 보존 정책 상세**
기본 400일 보존(소스 001), Extended Data Retention 액션(소스 035), Self-hosted TTL 정책(소스 053) 정보는 있으나, 플랜별 보존 정책 차이와 비용 영향이 명확하지 않다.

---

## 교재 작성 시 주의 사항

### 1. 리브랜딩으로 인한 명칭 혼동

LangGraph Platform이 2025년 10월 "LangSmith Deployment"로 리브랜딩되었다. 교재 작성 시 이 전환을 명확하게 설명하지 않으면 독자 혼란이 발생한다. 소스 050에서 "LangSmith Deployment(구 LangGraph Platform, 2025년 10월 리브랜딩)"으로 명시하는 방식을 교재에서도 따른다.

### 2. SDK 버전 의존성 주의

여러 기능이 SDK 버전 조건을 요구한다. 주요 버전 조건:
- evaluate() 단일 API 통합: SDK v0.2 이상
- @traceable 평가자 단순화 시그니처: SDK v0.2 이상
- LANGSMITH_PROJECT 환경 변수(JS SDK): v0.2.16 이상
- OpenTelemetry 통합: langsmith>=0.3.18 (0.4.25 이상 권장)
- TracingMiddleware: langsmith>=0.1.133

교재 코드 예시에서는 최신 SDK 기준으로 작성하되, 버전별 차이를 명확히 표기한다.

### 3. 공식 문서 URL 변경 가능성

LangSmith 문서가 `docs.langchain.com/langsmith/`와 `docs.smith.langchain.com/` 두 도메인에 분산되어 있다. 교재에서 URL을 직접 인용하는 경우 최신 URL로 확인이 필요하다. 소스 기준일은 2026-03-27이며, 이후 URL이 변경될 수 있다.

### 4. Insights Agent 접근 제한

Insights Agent는 LangSmith Plus 및 Enterprise 클라우드 사용자만 사용 가능하다. Developer 플랜 독자에게 이 기능을 소개할 때 접근 제한을 명확히 안내해야 한다.

### 5. Self-hosted와 Cloud 기능 차이

일부 기능이 Cloud 전용이거나 Self-hosted에서 다르게 동작할 수 있다. Insights Agent, Polly 등 최신 기능의 Self-hosted 지원 여부를 작성 전에 확인해야 한다.

### 6. 평가자 시그니처의 버전 차이

SDK v0.1과 v0.2의 평가자 시그니처가 다르다. v0.1은 `Run`과 `Example` 객체를 직접 받지만, v0.2는 `inputs`, `outputs`, `reference_outputs` 딕셔너리를 받는다. 교재에서 두 버전의 코드 예시가 혼재하면 독자 혼란이 발생하므로 일관성을 유지한다.

### 7. LangChain Hub와 LangSmith Hub 명칭 구분

소스에서 "LangChain Hub"와 "LangSmith Prompt Hub"가 혼용된다. 공식적으로는 LangChain Hub가 공개 프롬프트 공유 레지스트리이며, LangSmith의 프롬프트 관리 기능(버전 관리, Playground)과 통합된 시스템이다. 교재에서 명칭을 통일하고 범위를 명확히 구분해야 한다.
