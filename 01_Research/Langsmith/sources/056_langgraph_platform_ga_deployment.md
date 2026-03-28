---
source_id: 056
title: "LangGraph Platform GA — Agent Deployment Infrastructure"
url: "https://blog.langchain.com/langgraph-platform-ga/"
type: blog
scraped_at: 2026-03-27
keywords: ["deployment", "kw_020"]
content_length: 1920
---

# LangGraph Platform GA — Agent Deployment Infrastructure

## 개요

LangGraph Platform(2025년 5월 GA, 2025년 10월 "LangSmith Deployment"로 리브랜딩)은 에이전트를 대규모로 배포하고 관리하는 LangChain의 인프라다. 베타 기간에 LinkedIn, Uber, Klarna 등 약 400개 기업이 사용했다.

## 핵심 기능

**배포 및 인프라**:
- 1-클릭 배포로 몇 분 내 서비스 시작
- 세 가지 배포 모델: Cloud(SaaS), Hybrid, 완전 Self-hosted

**확장성 및 신뢰성**:
- 장기 실행, 비동기 에이전트-인간 협업, 버스티(bursty) 트래픽 패턴 처리
- 수평적 확장을 위한 내장 지원

**개발자 경험**:
- LangGraph Studio: 시각적 디버깅, 실시간 워크플로우 검사
- 실패한 단계를 되감고 재시도하는 체크포인팅

## 에이전트 특화 문제 해결

**장기 실행 에이전트**:
- 오픈 연결 없이 백그라운드 실행 유지
- 확장된 처리 중 타임아웃 방지를 위한 하트비트 신호
- 재시도 로직으로 예외 최소화

**버스티 부하 처리**:
- 동시 트래픽 스파이크 중 요청 손실 없는 태스크 큐
- 복잡한 로드 밸런싱 없이 Stateless 서버와 큐 구성 요소 간 수평 확장
- "더블 텍스팅" 시나리오 관리를 위한 4가지 내장 전략

**Stateful 작업**:
- 세션 간 상태 관리를 위한 최적화된 체크포인터 및 메모리 스토어
- Human-in-the-loop 워크플로우 및 타임 트래블 기능 전용 엔드포인트
- 자동 정리를 위한 스레드 및 메모리 항목에 TTL 첨부 지원

## API 및 기능

- 커스텀 사용자 경험을 위한 30개 API 엔드포인트
- 메모리 및 대화 기록을 지원하는 영속성 레이어
- Remote Graphs를 통한 다중 에이전트 아키텍처 지원
- 조직 내 검색을 위한 에이전트 레지스트리
- 다양한 에이전트 "어시스턴트"를 생성하는 버전 관리

## 가격 및 접근

- **Developer 티어**: 월 10만 노드 실행까지 무료
- **Plus/Enterprise**: Cloud 배포 활성화, Enterprise는 RBAC, 워크스페이스, Hybrid/Self-hosted 지원
