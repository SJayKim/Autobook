---
source_id: 038
title: "LangSmith — Configuring PagerDuty Integration for Alerts"
url: "https://docs.langchain.com/langsmith/alerts-pagerduty"
type: docs
scraped_at: 2026-03-27
keywords: ["alerts", "PagerDuty", "metric alerts", "threshold configuration"]
content_length: 1920
---

# LangSmith — Configuring PagerDuty Integration for Alerts

## 개요

LangSmith의 PagerDuty 연동을 통해 중요한 LLM 애플리케이션 이슈가 발생하면 PagerDuty 인시던트를 자동으로 생성할 수 있습니다. 이를 통해 기존 인시던트 관리 워크플로우와 연계하여 신속한 대응이 가능합니다.

## 필수 사전 조건

- PagerDuty 관리자 권한이 있는 활성 계정
- 서비스 수준 권한 보유
- 방화벽이 LangSmith의 아웃바운드 트래픽을 차단하지 않아야 함

## 단계별 설정 방법

### 1단계: PagerDuty 서비스 생성

1. PagerDuty 로그인 후 **Services → Service Directory** 접근
2. **+ New Service** 클릭
3. 필수 정보 입력:
   - **이름**: 설명적 명칭 (예: "LangSmith Monitoring")
   - **설명**: 모니터링 애플리케이션 상세 정보
   - **에스컬레이션 정책**: 팀 정책 선택
   - **통합 유형**: "Events API V2" 선택
4. **Add Service** 클릭

### 2단계: 통합 키(Integration Key) 획득

1. 생성된 서비스 선택
2. **Integrations** 탭 접근
3. "Events API V2" 통합 찾기
4. **Integration Key** 복사 — 32자 영숫자 문자열

### 3단계: LangSmith 알림 구성

1. 알림 설정의 notification section에서 **PagerDuty** 선택
2. 키 아이콘 클릭하여 Integration Key를 "Workspace Secret"으로 저장 (권장)
3. **Severity** 옵션 구성 — PagerDuty 인시던트 우선순위에 매핑
4. **Send Test Alert** 클릭으로 연동 테스트
5. PagerDuty에서 인시던트 생성 여부 확인

## 중요 동작 방식

동일한 알림을 1시간 이내에 재수신하려면 PagerDuty에서 이전 인시던트를 먼저 해결(resolve)해야 합니다. 이는 PagerDuty의 중복 알림 억제(deduplication) 메커니즘 때문입니다.

## 문제 해결

- Integration Key 정확성 확인 (32자 영숫자)
- PagerDuty 서비스 활성 상태 확인
- Events API v2 활성화 여부 확인
- 방화벽 아웃바운드 설정 검증

## LangSmith가 지원하는 PagerDuty 메트릭

- **Error Rate**: 에러율이 임계값 초과 시 인시던트 생성
- **Latency P50/P90/P99**: 지연시간 백분위 지표 초과 시
- **Feedback Score**: 사용자 피드백 점수가 임계값 이하로 떨어질 때
