# 7.4.2 ML Inference 파이프라인

7.4.1에서 RAG 파이프라인을 구성할 때, 인제스트 파이프라인의 inference 프로세서로 문서 인덱싱 시 자동으로 임베딩을 생성하는 방법을 간략히 소개했습니다. 이 단원에서는 ML Inference 파이프라인을 더 깊이 다룹니다. 7.1.3에서 임베딩 모델 배포와 기본적인 inference 프로세서 설정을 다뤘으니, 여기서는 필드 매핑, 파이프라인 체이닝, 배치 성능, 모니터링까지 확장합니다.

**inference 인제스트 프로세서**는 6.2.3에서 다룬 인제스트 파이프라인의 프로세서 중 하나입니다. 문서가 인덱싱될 때 ML 노드에 배포된 모델을 호출하고, 모델의 출력을 문서에 추가합니다. 임베딩 생성뿐 아니라 텍스트 분류, 개체명 인식, 감성 분석 등 다양한 추론 작업을 수행할 수 있습니다.

inference 프로세서를 설정할 때 핵심은 **model_id**와 **input_output** 필드 매핑입니다.

```json
PUT _ingest/pipeline/ml-embedding-pipeline
{
  "processors": [
    {
      "inference": {
        "model_id": "sentence-transformers__all-minilm-l6-v2",
        "input_output": [
          {
            "input_field": "content",
            "output_field": "content_embedding"
          }
        ]
      }
    }
  ]
}
```

**model_id**는 7.1.3에서 eland로 업로드하고 _deploy API로 배포한 모델의 식별자입니다. Elasticsearch가 이 ID로 ML 노드에 있는 모델을 찾아 호출합니다.

**input_output**은 어떤 문서 필드를 모델 입력으로 사용하고, 모델 출력을 어떤 필드에 저장할지를 지정합니다. input_field에 문서의 텍스트 필드명을, output_field에 결과를 저장할 필드명을 넣습니다. 모델이 text_embedding 태스크 타입이면 output_field에 벡터 배열이 저장됩니다.

여러 필드에 대해 임베딩을 생성해야 하는 경우가 있습니다. 예를 들어 제목과 본문에 각각 별도의 임베딩을 만들고 싶다면 input_output 배열에 항목을 추가합니다.

```json
{
  "inference": {
    "model_id": "sentence-transformers__all-minilm-l6-v2",
    "input_output": [
      { "input_field": "title", "output_field": "title_embedding" },
      { "input_field": "content", "output_field": "content_embedding" }
    ]
  }
}
```

title 필드의 텍스트로 title_embedding을 생성하고, content 필드의 텍스트로 content_embedding을 생성합니다. 한 번의 프로세서 호출로 두 필드를 처리합니다.

실무에서는 임베딩 생성 외에 다른 전처리를 함께 수행해야 하는 경우가 많습니다. 예를 들어 HTML 태그를 제거한 뒤 임베딩을 생성하거나, 임베딩 생성 후 특정 메타데이터를 추가하는 식입니다. 이때 **파이프라인 체이닝**을 사용합니다.

파이프라인 체이닝은 하나의 파이프라인 안에 여러 프로세서를 순서대로 배치하는 것입니다. 프로세서는 배열에 나열된 순서대로 실행됩니다.

```json
PUT _ingest/pipeline/full-ml-pipeline
{
  "processors": [
    {
      "html_strip": {
        "field": "raw_content",
        "target_field": "content"
      }
    },
    {
      "inference": {
        "model_id": "sentence-transformers__all-minilm-l6-v2",
        "input_output": [
          { "input_field": "content", "output_field": "content_embedding" }
        ]
      }
    },
    {
      "set": {
        "field": "indexed_at",
        "value": "{{_ingest.timestamp}}"
      }
    }
  ]
}
```

이 파이프라인은 세 단계를 거칩니다. 첫째, html_strip 프로세서가 raw_content의 HTML 태그를 제거하고 깨끗한 텍스트를 content 필드에 저장합니다. 둘째, inference 프로세서가 content를 임베딩 모델에 넣어 벡터를 생성합니다. 셋째, set 프로세서가 인덱싱 시점의 타임스탬프를 indexed_at 필드에 기록합니다.

```
문서 입력
  │
  ├─ [1] html_strip: raw_content → content (태그 제거)
  │
  ├─ [2] inference: content → content_embedding (벡터 생성)
  │
  ├─ [3] set: indexed_at = 현재 시각
  │
  └─ 인덱싱 완료
```

대량의 문서를 인덱싱할 때는 **배치 inference 성능**이 중요합니다. Bulk API를 사용하여 한 번에 여러 문서를 보내면, Elasticsearch가 내부적으로 inference 요청을 배치로 처리하여 처리량을 높입니다.

배치 성능을 높이는 방법은 세 가지입니다. 첫째, Bulk API의 배치 크기를 적절히 조절합니다. 너무 작으면 네트워크 오버헤드가 크고, 너무 크면 ML 노드의 큐가 쌓입니다. 100~500건 단위로 시작하여 조절하는 것이 일반적입니다.

둘째, 7.1.3에서 다룬 number_of_allocations를 늘려 모델 인스턴스 수를 증가시킵니다. 인스턴스가 많을수록 동시에 처리할 수 있는 추론 요청이 늘어납니다.

셋째, ML 노드의 CPU와 메모리를 충분히 확보합니다. 임베딩 모델은 CPU 집약적이므로, ML 노드에 충분한 CPU 코어를 할당해야 병목이 발생하지 않습니다.

**ML Inference 모니터링**은 파이프라인이 안정적으로 동작하는지 확인하는 데 필수적입니다. 7.1.3에서 소개한 모델 통계 API를 사용합니다.

```
GET _ml/trained_models/sentence-transformers__all-minilm-l6-v2/_stats
```

응답에서 확인할 주요 항목은 다음과 같습니다. inference_count는 총 추론 횟수입니다. average_inference_time_ms는 추론 한 건당 평균 소요 시간입니다. 이 값이 급격히 증가하면 ML 노드에 부하가 걸리고 있다는 신호입니다. queue_count는 처리 대기 중인 요청 수입니다. 지속적으로 높다면 number_of_allocations를 늘려야 합니다.

6.4.3에서 다룬 클러스터 모니터링과 함께 ML 노드의 상태도 주기적으로 확인하는 것이 좋습니다. Kibana의 Machine Learning 페이지에서 배포된 모델의 상태, 처리량, 오류율을 시각적으로 확인할 수 있습니다.

마지막으로 **Elastic AI Assistant** 연동에 대해 간략히 소개합니다. Elastic AI Assistant는 Kibana에 내장된 대화형 AI 인터페이스입니다. Elasticsearch에 저장된 데이터를 기반으로 질문에 답변하거나, 보안 이벤트를 분석하는 데 사용합니다. 내부적으로 ML Inference 파이프라인과 동일한 인프라를 활용하여 임베딩 생성과 검색을 수행합니다. Elastic AI Assistant의 세부 설정은 이 토픽의 범위를 벗어나므로, ML Inference 파이프라인이 이런 고수준 기능의 기반이 된다는 점만 짚고 넘어갑니다.

정리하면, ML Inference 파이프라인은 inference 인제스트 프로세서를 핵심으로 합니다. model_id로 배포된 모델을 지정하고, input_output으로 입출력 필드를 매핑합니다. 파이프라인 체이닝으로 전처리와 임베딩 생성을 하나의 흐름으로 엮고, Bulk API와 number_of_allocations 조정으로 배치 성능을 높입니다. 모델 통계 API와 Kibana ML 페이지로 추론 성능과 큐 상태를 모니터링합니다.

다음 단원인 7.5.1에서는 Elasticsearch의 또 다른 ML 기능인 이상 감지(Anomaly Detection) Job 설정을 다룹니다.

이 단원을 마치면 ML Inference 프로세서로 인덱싱 시 자동 임베딩 생성 파이프라인을 구성할 수 있습니다.
