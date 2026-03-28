---
source_id: 057
title: "Why LangGraph Platform for Agent Deployment — Production Challenges"
url: "https://blog.langchain.com/why-langgraph-platform/"
type: blog
scraped_at: 2026-03-27
keywords: ["deployment", "kw_020"]
content_length: 1760
---

# Why LangGraph Platform for Agent Deployment — Production Challenges

## 배경

LangGraph Platform(현 LangSmith Deployment)은 "더 오래 실행되고, 더 stateful하며, 더 bursty한" 에이전트의 배포 과제를 해결하기 위해 등장했다. 빠른 Stateless 에이전트는 람다 형태로 실행할 수 있지만, 복잡한 에이전트는 전용 인프라가 필요하다.

## 문제 카테고리별 해결책

### 장기 실행 에이전트

**문제**: 연결 유지 없이 백그라운드 실행 불가, 타임아웃으로 중단

**해결**:
- 폴링, 스트리밍, 웹훅 모니터링으로 오픈 연결 없이 백그라운드 실행 유지
- 확장된 처리 중 타임아웃 방지를 위한 하트비트 신호
- 워커 기반 격리 및 설정 가능한 재시도 로직
- 실행 중 실시간 중간 출력을 위한 다중 스트리밍 모드

### 버스티 부하

**문제**: 동시 트래픽 스파이크 시 요청 손실

**해결**:
- 동시 트래픽 스파이크 중 요청 손실 없는 태스크 큐
- Stateless 서버와 큐 구성 요소 간 수평 확장 (복잡한 로드 밸런싱 불필요)
- "더블 텍스팅" — 에이전트 응답 완료 전 사용자가 빠른 메시지 전송 — 처리를 위한 4가지 내장 전략

### Stateful 작업

**문제**: 세션 간 상태 관리를 위한 커스텀 인프라 구축 부담

**해결**:
- 세션 간 상태를 관리하는 최적화된 체크포인터 및 메모리 스토어 — 커스텀 인프라 불필요
- Human-in-the-loop 워크플로우 및 타임 트래블(이전 상태 검토/수정) 전용 엔드포인트
- 대화 스레드 및 메모리 항목에 TTL 첨부로 자동 정리

## 핵심 가치 제안

플랫폼을 통해 개발자는 배포 인프라를 직접 구축하는 대신 에이전트 동작에 집중할 수 있다.

## 배포 모델

| 모델 | 설명 | 적합 대상 |
|------|------|----------|
| Cloud (SaaS) | 완전 관리형 | 빠른 시작, 단순한 보안 요건 |
| Hybrid | SaaS Control Plane + 자체 Data Plane | 민감한 데이터, 관리형 서비스 선호 |
| Self-hosted | 완전 자체 호스팅 | 엄격한 데이터 거주 요건 |
