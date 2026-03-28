---
source_id: 014
title: "LangSmith — Manage Datasets (Versioning, CSV Import, Production Traces, Splits)"
url: "https://docs.langchain.com/langsmith/manage-datasets"
type: docs
scraped_at: 2026-03-27
keywords: ["datasets"]
content_length: 2760
---

# LangSmith — Manage Datasets (Versioning, CSV Import, Production Traces, Splits)

## 데이터셋 구조

LangSmith에서 **Dataset**은 **Examples**의 집합이다. 각 Example은 다음으로 구성된다:
- `input`: 애플리케이션에 전달하는 파라미터
- `reference output` (optional): 기대하거나 참조하는 출력

데이터셋 스키마는 매우 유연하여 임의 구조를 정의할 수 있다.

## 버전 관리 (Versioning)

예제를 추가·수정·삭제할 때마다 새 버전이 자동 생성된다. 버전은 타임스탬프로 추적되며, 과거 데이터셋 상태를 조회할 수 있다. 중요한 버전에는 "prod" 같은 시맨틱 태그를 붙일 수 있다.

```python
# 버전 태그 지정
client.update_dataset_tag(dataset_id, tag="prod", as_of=timestamp)

# 특정 버전의 examples 조회
client.list_examples(dataset_id, as_of="prod")
```

## CSV Import

LangSmith는 CSV 파일에서 데이터셋을 임포트할 수 있다. CSV 열(column)을 input/output 필드로 매핑하여 레퍼런스 데이터셋으로 변환한다. 이 데이터셋을 기반으로 LLM이 자체 출력을 품질 지표로 평가하도록 구성할 수 있다.

### 결과 CSV 내보내기
```python
# 실험 결과를 CSV로 내보내기 (beta)
from langsmith.testing import get_test_results
results = get_test_results(experiment_name="my-experiment")
results.to_csv("results.csv")
```

## 프로덕션 트레이스에서 데이터셋 생성

실패한 사용자 상호작용 등 실제 트레이스에서 평가 데이터셋을 구축할 수 있다:

```python
# 트레이스에서 examples 읽어 데이터셋 생성
runs = client.list_runs(project_name="production", filter="...")
for run in runs:
    client.create_example(
        inputs=run.inputs,
        outputs=run.outputs,
        dataset_id=dataset.id
    )
```

UI에서도 트레이스를 직접 선택하여 데이터셋에 추가할 수 있다.

## 필터링 & 분할 (Filtering & Splitting)

- 메타데이터 쿼리나 특정 데이터셋 split(test, training 등)으로 서브셋 평가 가능
- `list_examples`의 메타데이터 필터링과 split 선택 지원

```python
# 특정 split 선택
client.list_examples(dataset_id, splits=["test", "validation"])

# 메타데이터 필터링
client.list_examples(dataset_id, metadata={"difficulty": "hard"})
```

## 공유 및 내보내기

- 데이터셋을 공개 공유 링크로 배포 가능 (LangSmith 계정 없이도 접근)
- 내보내기 형식: **CSV**, **JSONL**, **OpenAI fine-tuning format**

## 실험 트레이스 재활용

평가 실행 후 평가 기준으로 필터링한 실험 트레이스를 다시 데이터셋에 추가하여 반복적으로 개선 가능하다.
