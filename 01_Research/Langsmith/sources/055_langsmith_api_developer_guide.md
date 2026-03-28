---
source_id: 055
title: "LangSmith API — Complete Developer Guide"
url: "https://agentsapis.com/langsmith-api/"
type: web
scraped_at: 2026-03-27
keywords: ["API and SDK reference", "kw_024"]
content_length: 1640
---

# LangSmith API — Complete Developer Guide

## API 기본 정보

LangSmith REST API는 언어나 환경에 관계없이 LangSmith 리소스를 관리하는 범용 인터페이스다. API는 SDK가 내부적으로 호출하는 엔드포인트들과 동일한 인터페이스를 제공한다.

**API 호스트**: `api.smith.langchain.com`

**인증 헤더**: `X-Api-Key` 또는 `x-api-key`

멀티테넌트 설정에서는 `X-Tenant-Id` 헤더로 워크스페이스 컨텍스트를 지정한다.

## 핵심 API 기능

**수집(Ingest) 작업**:
- 실행/트레이스 전송 (배치/멀티파트 포함)
- OpenTelemetry 트레이스 내보내기
- 피드백 생성
- 데이터셋 및 예제 생성

**쿼리 및 관리**:
- 시간 범위 및 메타데이터 필터로 실행 데이터 접근
- 데이터셋 내보내기
- 실험/평가 관리
- 관리 작업 자동화

## API 키 관리

API 키는 Settings 페이지에서 생성한다. 생성 시 한 번만 표시되므로 안전한 위치에 저장해야 한다.

**키 유형**:
- **Service Key**: 프로덕션 환경 권장, 쉬운 로테이션 지원
- **Personal Token**: 로컬 개발 전용

## 수집 엔드포인트별 처리량

| 엔드포인트 | 처리량 수준 | 설명 |
|------------|------------|------|
| `POST /runs/batch` | 높음 | 다수 실행 레코드 효율적 처리 |
| `POST /runs/multipart` | 매우 높음 | 대용량 페이로드 처리 |
| `POST /otel/v1/traces` | 높음 | OpenTelemetry span 내보내기용 |
| `POST /runs/query` | 낮음 | 메타데이터 필터링 지원 |

## 데이터셋 및 피드백

**데이터셋**: 평가용 정제된 예제(입력, 선택적 참조 출력, 메타데이터)의 컬렉션이다. API로 데이터셋 생성, 예제 추가, 피드백 신호 연결이 가능하다.

**피드백 신호 유형**:
- 수치 점수 (Numeric score)
- 카테고리 레이블 (Categorical label)
- 루브릭 버전 (Rubric version)

## 공식 API 문서

- ReDoc: `https://api.smith.langchain.com/redoc`
- Swagger UI: `https://api.smith.langchain.com/docs`
