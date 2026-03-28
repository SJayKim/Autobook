---
source_id: 050
title: "LangSmith Deployment — Control Plane Architecture & Agent Servers"
url: "https://docs.langchain.com/langsmith/control-plane"
type: docs
scraped_at: 2026-03-27
keywords: ["deployment", "kw_020"]
content_length: 1920
---

# LangSmith Deployment — Control Plane Architecture & Agent Servers

## 개요

LangSmith Deployment(구 LangGraph Platform, 2025년 10월 리브랜딩)는 프로덕션 환경에서 에이전트를 실행하기 위한 전용 인프라다. 조직이 에이전트를 빌드, 배포, 관리하는 방식을 표준화한다.

## Control Plane

Control Plane은 두 가지 구성 요소로 이루어진다:
1. **Control Plane UI**: 사용자가 LangGraph 서버(배포)를 생성하고 업데이트하는 인터페이스
2. **Control Plane APIs**: UI 경험을 지원하는 API 집합

사용자가 Control Plane UI를 통해 업데이트를 수행하면 해당 업데이트가 Control Plane 상태에 저장된다. Data Plane의 "listener" 애플리케이션이 Control Plane API를 주기적으로 폴링하여 변경사항을 감지한다.

**중요한 설계 원칙**: Control Plane은 Data Plane에 직접 연결을 시작하지 않는다. 단방향 폴링 구조로, Data Plane이 Control Plane을 폴링한다.

## Agent Servers

배포(Deployment)는 Agent Server 인스턴스다. Control Plane은 각 배포에 대해 자동으로 Postgres 데이터베이스를 생성하며, 이 데이터베이스가 배포의 영속성 레이어 역할을 한다. 개발자는 체크포인터를 별도로 설정하지 않아도 되며, 그래프에 대해 "자동으로 설정"된다.

## 배포 유형

| 유형 | 리소스 | 특징 |
|------|--------|------|
| **Development** | 1 CPU, 1 GB RAM | 단일 레플리카, 선점형 인프라, 내부 테스트용 |
| **Production** | 2 CPU, 2 GB RAM | 최대 10 레플리카, 자동 백업, 내구성 있는 인프라 |

한번 생성된 배포 유형은 변경할 수 없다.

## 비동기 배포 프로세스

인프라 프로비저닝은 수 분에 걸쳐 비동기로 진행된다. 초기 배포는 데이터베이스 생성으로 인해 시간이 더 걸리고, 이후 리비전은 데이터베이스가 이미 존재하므로 더 빠르게 배포된다.

## 모니터링

시스템은 CPU, 메모리 사용량, 컨테이너 재시작, 큐 메트릭을 추적한다. 각 배포에 대해 "동일한 이름으로 LangSmith 트레이싱 프로젝트가 자동 생성"되고, 환경 변수도 자동 설정된다.

## 배포 옵션

- **Cloud (SaaS)**: 완전 관리형, LangChain 호스팅
- **Hybrid**: SaaS Control Plane + 자체 호스팅 Data Plane — 민감한 데이터가 있지만 관리형 서비스를 원하는 팀에 적합
- **Self-hosted**: Control Plane과 Data Plane 모두 자체 호스팅
