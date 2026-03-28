---
source_id: 052
title: "LangSmith Self-Hosted on Kubernetes — Helm Chart & Data Residency"
url: "https://docs.langchain.com/langsmith/kubernetes"
type: docs
scraped_at: 2026-03-27
keywords: ["self-hosted LangSmith", "kw_021"]
content_length: 2140
---

# LangSmith Self-Hosted on Kubernetes — Helm Chart & Data Residency

## 개요

Self-hosted LangSmith는 Enterprise Plan의 부가 기능으로, 보안이 중요한 대규모 고객을 위해 설계되었다. Enterprise 플랜을 사용 중이라면 AWS, GCP, Azure의 자체 Kubernetes 클러스터에서 LangSmith를 실행할 수 있으며, "데이터가 환경 밖으로 나가지 않는다."

## 지원 Kubernetes 배포판

- Google Kubernetes Engine (GKE)
- Amazon EKS (AWS 전용 가이드 제공)
- Azure AKS (Azure 전용 가이드 제공)
- OpenShift 4.14+
- Minikube, Kind (개발 전용)

## 사전 요구사항

**라이선스**: LangSmith 라이선스 키 필요 (sales@langchain.dev 문의)

**클러스터 사양**:
- 최소 16 vCPU, 64GB RAM 권장
- ClickHouse 전용 노드: 4 vCPU, 16GB 할당 가능 메모리
- 동적 PV 프로비저너 또는 SSD 백업 스토리지 클래스 (7000 IOPS, 1000 MiB/s)

**필수 설정 항목**:
- API Key Salt: "임의의 문자열"
- JWT Secret (선택, 기본 인증용)

## Helm Chart 배포

```bash
# LangChain Helm 레포지토리 추가
helm repo add langchain https://langchain-ai.github.io/helm/

# 설정 파일로 배포
helm upgrade -i langsmith langchain/langsmith \
  --values langsmith_config.yaml \
  --version <version> \
  -n <namespace>
```

`langsmith_config.yaml`에는 라이선스 키, API salt, 관리자 자격증명, 인증 설정을 포함한다.

## 아키텍처 구성 요소

**Stateless 서비스**:
- **Frontend**: Nginx 서버, UI 제공 및 API 요청 라우팅 — "사용자에게 노출되는 유일한 컴포넌트"
- **Backend**: 비즈니스 로직 처리 API 서버
- **Platform Backend**: 인증 처리
- **Queue Service**: 비동기 트레이스 처리
- **Playground Service**: LLM 상호작용

**Persistent 스토리지 서비스**:
- **ClickHouse**: 대용량 트레이스 및 피드백 저장
- **PostgreSQL**: 메타데이터, 사용자, 조직 정보
- **Redis**: 캐싱 및 큐잉
- **Blob storage** (선택): 대용량 첨부파일

## Data Residency

LangSmith는 관리형 클라우드, BYOC(Bring Your Own Cloud), Self-hosted 옵션을 제공해 데이터 거주 요건을 충족시킨다.

Self-hosted 인스턴스는 모든 정보를 로컬에 저장하지만, 다음 용도로 `https://beacon.langchain.com`에 대한 이그레스가 필요하다:
- 라이선스 검증
- 청구 목적 사용량 보고
- 원격 지원을 위한 운영 메타데이터

Air-gapped 환경(완전 오프라인)에서는 이 이그레스를 차단하는 "오프라인 모드" 설정이 가능하다.

## 고급 설정

- **외부 ClickHouse**: 외부 ClickHouse 데이터베이스 연결
- **외부 PostgreSQL/Redis**: 외부 관리형 인스턴스 사용
- **SSO 통합**: OIDC 호환 프로바이더 (Google Workspace 포함)
- **Custom TLS**: 자체 서명 인증서 또는 Mutual TLS 지원
- **데이터 보존**: TTL 기반 자동 트레이스 정리

## Post-Deployment 권장사항

1. DNS 및 SSL/TLS 암호화 설정
2. Single Sign-On(SSO) 구현
3. 외부 PostgreSQL 및 Redis 연결
4. 대용량 파일 처리를 위한 Blob 스토리지 설정
