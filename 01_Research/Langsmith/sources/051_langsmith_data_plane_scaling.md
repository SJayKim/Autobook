---
source_id: 051
title: "LangSmith Data Plane — Infrastructure & Autoscaling"
url: "https://docs.langchain.com/langsmith/data-plane"
type: docs
scraped_at: 2026-03-27
keywords: ["deployment", "kw_020"]
content_length: 1740
---

# LangSmith Data Plane — Infrastructure & Autoscaling

## 핵심 구성 요소

Data Plane은 세 가지 주요 부분으로 구성된다:
1. **Agent Server 배포**: 실제 에이전트가 실행되는 서버
2. **지원 인프라**: PostgreSQL, Redis, Secrets store, Autoscaler
3. **Listener 애플리케이션**: Control Plane과 동기화하는 컴포넌트

각 인프라 역할:
- **PostgreSQL**: 사용자 데이터, 실행 결과, 메모리, 기본 체크포인트 백엔드
- **Redis**: 서버-워커 간 통신, 임시 메타데이터 저장
- **Secrets store**: 환경 변수 보안 저장
- **Autoscaler**: 수요에 따른 컨테이너 용량 자동 조정

## Listener 애플리케이션

Listener는 주기적으로 Control Plane API를 쿼리해 배포 생성, 업데이트, 삭제 여부를 판단한다. 이를 통해 현재 배포 상태가 원하는 상태와 일치하도록 보장한다.

## Redis 통신 패턴

Redis는 서버와 백그라운드 워커 간 양방향 통신을 지원한다:
- **List 기반 wake-up 신호**: 새 실행에 대한 알림
- **String/PubSub 채널**: 취소 요청 전달
- **PubSub 채널**: 실행 중 스트리밍 출력 브로드캐스트

주의: "Redis에는 사용자나 실행 데이터가 저장되지 않는다."

## 오토스케일링 전략

Production 배포는 세 가지 독립 메트릭을 기반으로 최대 10개 컨테이너까지 자동 확장된다:

| 메트릭 | 목표값 |
|--------|--------|
| CPU 사용률 | 75% |
| 메모리 사용률 | 75% |
| 대기 중 실행 수 | 컨테이너당 10개 |

오토스케일러는 가장 많은 컨테이너를 요구하는 메트릭을 선택한다.

**스케일 다운 예시**: 현재 컨테이너 1개, 대기 실행 20개 → 오토스케일러가 2개로 확장 (20 ÷ 2 = 10 대기 실행/컨테이너)

스케일 다운은 30분 쿨다운 후 실행되어 과도한 변동을 방지한다.

## Hybrid 및 Self-hosted 배포

조직은 Hybrid 또는 Self-hosted 배포에서 커스텀 PostgreSQL 및 Redis 인스턴스를 지정할 수 있다. 공유 인스턴스에서 별도 데이터베이스를 사용하는 방식도 지원된다.

## 장기 실행 에이전트 지원

- 오픈 연결 유지 없이 백그라운드 실행, 폴링, 스트리밍, 웹훅 모니터링 지원
- 확장된 처리 중 타임아웃 방지를 위한 하트비트 신호
- 최소 예외와 빠른 복구를 위한 워커 기반 격리 및 재시도 로직
