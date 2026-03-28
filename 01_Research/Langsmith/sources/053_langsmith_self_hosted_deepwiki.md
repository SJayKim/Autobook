---
source_id: 053
title: "Self-Hosting LangSmith — Architecture, Components & Operations"
url: "https://deepwiki.com/langchain-ai/langsmith-docs/6-self-hosting"
type: docs
scraped_at: 2026-03-27
keywords: ["self-hosted LangSmith", "kw_021"]
content_length: 2380
---

# Self-Hosting LangSmith — Architecture, Components & Operations

## 배포 방식

### Kubernetes (프로덕션 권장)

Helm을 통한 Kubernetes 배포가 프로덕션 표준이다.

```bash
helm install langsmith langchain/langsmith --values langsmith_config.yaml
```

클러스터 요건: 최소 16 vCPU, 64GB 메모리. ClickHouse 전용 노드 필요 (4 vCPU, 16GB).

### Docker Compose (개발/소규모)

- 최소 4 vCPU, 16GB 메모리
- `docker-compose up`으로 시작
- UI 접근: `http://localhost:1980`

## 핵심 아키텍처

**Stateless 서비스**:
- Frontend (Nginx): UI 제공, "사용자에게 노출되는 유일한 컴포넌트"
- Backend API: 비즈니스 로직
- Platform Backend: 인증
- Queue Service: 비동기 트레이스 처리
- Playground Service: LLM 상호작용
- ACE Backend: 코드 실행

**Persistent 스토리지**:
- **ClickHouse**: 대용량 트레이스 및 피드백 (전용 노드 권장)
- **PostgreSQL**: 메타데이터, 사용자, 조직 관리
- **Redis**: 캐싱 및 큐잉
- Blob Storage (선택적): 대용량 첨부파일

## 인증 옵션

**OAuth/SSO (권장)**: OIDC 호환 프로바이더 통합 (Google Workspace 포함)

**Basic 인증**: 사용자명/비밀번호 로그인, 설정 중 단일 "Default" 조직 생성

## 데이터 보존 정책

자동 TTL 기반 데이터 보존이 지원되며, 컴플라이언스와 스토리지 효율성을 위해 설정된 정책에 따라 트레이스가 자동 정리된다.

## 이그레스 요건

Self-hosted 인스턴스는 `beacon.langchain.com`으로의 이그레스가 필요하다:
- 라이선스 검증
- 청구 목적 사용량 보고
- 원격 지원을 위한 운영 메타데이터

## 외부 스토리지 서비스

- 외부 ClickHouse 데이터베이스 연결 지원
- LangSmith 관리형 ClickHouse (지원 리전의 VPC 필요)
- 외부 PostgreSQL 및 Redis 인스턴스

## 운영 및 유지보수

**사용량 모니터링**: 조직 사용량 차트가 5분마다 갱신되며 자동 생성된다.

**버전 관리**: Semantic versioning을 따르며, 기능, 변경사항, 마이그레이션 요구사항이 포함된 릴리스 노트를 제공한다.

## 일반적인 문제 해결

| 문제 | 해결책 |
|------|--------|
| ClickHouse 디스크 가득 참 | ClickHouse PVC 크기 증가 |
| 데이터베이스 버전 오류 | 이전 버전으로 복원 후 마이그레이션 재실행 |
| 413 Request Too Large | `frontend.maxBodySize` 설정 증가 |
| ClickHouse 권한 오류 | `users.xml`의 row policy grants 업데이트 |

## Custom TLS

Azure OpenAI, OpenAI, 커스텀 모델 서버에 대한 TLS 인증서 커스터마이제이션 지원 — 자체 서명 인증서 또는 Mutual TLS에 유용하다.
