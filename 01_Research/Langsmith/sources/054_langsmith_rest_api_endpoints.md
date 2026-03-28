---
source_id: 054
title: "LangSmith REST API — Runs, Datasets, Feedback Endpoints"
url: "https://docs.langchain.com/langsmith/run-evals-api-only"
type: docs
scraped_at: 2026-03-27
keywords: ["API and SDK reference", "kw_024"]
content_length: 2060
---

# LangSmith REST API — Runs, Datasets, Feedback Endpoints

## 개요

LangSmith REST API는 Python 또는 TypeScript SDK를 사용하지 않는 환경에서도 LangSmith 리소스를 관리할 수 있는 범용 인터페이스다. 평가 실행, 실험 관리, 피드백 추적을 다양한 프로그래밍 언어에서 자동화할 수 있다.

## 인증

모든 API 요청은 헤더 기반 API 키 인증이 필요하다:

```python
headers = {"x-api-key": os.environ["LANGSMITH_API_KEY"]}
```

멀티테넌트 설정에서는 `X-Tenant-Id` 헤더로 워크스페이스를 지정할 수 있다.

**API 호스트**: `https://api.smith.langchain.com` (Self-hosted 또는 EU 리전에서는 변경 가능)

**키 종류**:
- **Service Key**: 프로덕션 권장 (쉬운 로테이션, 단일 담당자 의존 없음)
- **Personal Token**: 로컬 개발용

## 핵심 엔드포인트

### Datasets (데이터셋)

```
GET  /api/v1/examples           # 데이터셋에서 예제 조회
POST /api/v1/datasets/comparative  # 비교 실험 생성
```

예제 조회 파라미터: `dataset` (dataset_id)

### Runs (실행)

```
POST  /api/v1/runs              # 새 실행 생성
PATCH /api/v1/runs/{run_id}     # 실행 업데이트 (출력, end_time)
POST  /api/v1/runs/query        # 필터링으로 실행 쿼리
```

실행 생성 시 필수 필드:
- `id`: 실행 UUID
- `name`: 실행 이름
- `run_type`: "chain" 또는 "llm"
- `inputs`: 입력 데이터
- `reference_example_id`: 데이터셋 예제 연결
- `session_id`: 실험 연결
- `parent_run_id` (선택): 부모-자식 관계

### Sessions/Experiments (실험)

```
POST  /api/v1/sessions            # 실험 생성
PATCH /api/v1/sessions/{session_id}  # 실험 종료
```

실험 생성 필드:
- `start_time`: 시작 시각
- `reference_dataset_id`: 데이터셋 연결
- `name`: 실험 이름
- `description`, `extra` (선택): 메타데이터

### Feedback (피드백)

```
POST /api/v1/feedback  # 평가 피드백 추가
```

피드백 필드:
- `run_id`: 대상 실행 ID
- `key`: 메트릭 이름 (예: "correctness")
- `score`: 수치값 (1.0 = 정답, 0.0 = 오답)
- `comment` (선택): 설명
- `feedback_group_id`: 관련 피드백 그룹화 (비교 실험용)
- `comparative_experiment_id`: 비교 실험 ID

## 처리량 패턴

| 엔드포인트 | 처리량 | 용도 |
|------------|--------|------|
| `POST /runs/batch` | 높음 | 다수 실행 효율적 수집 |
| `POST /runs/multipart` | 매우 높음 | 대용량 페이로드 |
| `POST /otel/v1/traces` | 높음 | OpenTelemetry span 내보내기 |
| `POST /runs/query` | 낮음 | 메타데이터 필터링 쿼리 |

## Pairwise 실험

`/datasets/comparative`로 여러 실험의 출력을 비교 평가할 수 있다. 모델 응답의 선호도 순위를 매기는 비교 평가에 활용된다.
