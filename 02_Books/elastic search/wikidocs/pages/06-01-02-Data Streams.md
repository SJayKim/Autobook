# 6.1.2 Data Streams

로그, 메트릭, 이벤트처럼 시간 순서로 끊임없이 생성되는 데이터를 Elasticsearch에 저장하려면, 인덱스를 날짜별로 만들고, 오래된 인덱스는 롤오버하고, ILM 정책으로 정리하는 과정을 반복해야 합니다. 6.1.1에서 다룬 ILM이 수명주기 자동화를 담당하지만, 인덱스 이름을 날짜 패턴으로 관리하고, 별칭으로 쓰기 대상을 전환하는 작업까지 직접 설계하면 구성이 복잡해집니다.

**Data Stream**은 이 복잡함을 해결하기 위해 Elasticsearch가 제공하는 추상 계층입니다. 하나의 Data Stream 이름 아래 여러 개의 인덱스가 자동으로 생성되고 관리됩니다. 사용자는 Data Stream 이름만 알면 데이터를 넣고 검색할 수 있고, 그 아래에서 인덱스가 몇 개 만들어지는지, 어떤 인덱스가 현재 쓰기 대상인지를 직접 신경 쓸 필요가 없습니다.

Data Stream이 적합한 데이터에는 공통된 특성이 있습니다. 첫째, 데이터에 타임스탬프가 반드시 포함되어 있습니다. 둘째, 데이터가 주로 추가(append) 방식으로 쌓이며, 기존 문서를 수정하거나 삭제하는 일은 드뭅니다. 로그 파일, 애플리케이션 이벤트, 인프라 메트릭, 감사 기록 등이 대표적인 예입니다.

Data Stream 내부에는 **backing index**라는 숨겨진 인덱스들이 존재합니다. backing index는 Elasticsearch가 자동으로 생성하고 이름을 부여합니다. 이름 규칙은 다음과 같습니다.

```
.ds-<data-stream-이름>-<날짜>-<세대번호>
```

예를 들어 logs-nginx라는 Data Stream의 첫 번째 backing index는 `.ds-logs-nginx-2024.01.15-000001`과 같은 이름을 갖습니다. 세대번호는 롤오버가 발생할 때마다 1씩 증가합니다.

여러 backing index 중 가장 최근에 생성된 것이 **쓰기 인덱스(write index)**입니다. 새로 들어오는 모든 문서는 이 쓰기 인덱스에 저장됩니다. 롤오버 조건(크기, 문서 수, 경과 시간)이 충족되면, Elasticsearch가 새 backing index를 만들어 쓰기 인덱스로 전환합니다. 이전 backing index는 읽기 전용이 됩니다.

```
Data Stream: logs-nginx
  ├── .ds-logs-nginx-2024.01.15-000001  (읽기 전용)
  ├── .ds-logs-nginx-2024.02.15-000002  (읽기 전용)
  └── .ds-logs-nginx-2024.03.15-000003  (쓰기 인덱스) ← 새 문서 저장
```

Data Stream의 모든 문서에는 **@timestamp** 필드가 필수입니다. 이 필드는 date 또는 date_nanos 타입으로 매핑되어야 합니다. 인덱스 템플릿에서 @timestamp 매핑을 명시하지 않으면, Elasticsearch가 자동으로 date 타입을 할당합니다. @timestamp가 없는 문서를 인덱싱하면 오류가 발생합니다.

Data Stream을 생성하려면 먼저 인덱스 템플릿을 만들어야 합니다. 2.4.3에서 다룬 인덱스 템플릿에 data_stream 옵션을 추가하면, 해당 패턴에 맞는 이름으로 데이터를 인덱싱할 때 자동으로 Data Stream이 생성됩니다.

```json
PUT _index_template/my_logs_template
{
  "index_patterns": ["logs-*"],
  "data_stream": {},
  "template": {
    "settings": {
      "index.lifecycle.name": "my_ilm_policy"
    }
  },
  "priority": 200
}
```

이 템플릿의 각 부분을 살펴보겠습니다. index_patterns는 Data Stream 이름이 일치해야 하는 패턴입니다. "logs-*"로 설정하면 logs-로 시작하는 모든 이름이 이 템플릿에 매칭됩니다. data_stream 필드를 빈 객체로 두면, 이 템플릿이 Data Stream용임을 선언합니다. template.settings 안의 index.lifecycle.name은 6.1.1에서 생성한 ILM 정책을 연결합니다. priority는 여러 템플릿이 같은 패턴에 매칭될 때 우선순위를 결정합니다. 숫자가 클수록 우선합니다.

템플릿을 생성한 뒤, 해당 패턴에 맞는 이름으로 문서를 인덱싱하면 Data Stream이 자동으로 만들어집니다.

```json
POST logs-my-app/_doc
{
  "@timestamp": "2024-01-15T10:00:00",
  "level": "INFO",
  "message": "Application started"
}
```

logs-my-app이라는 Data Stream이 아직 없으면 이 시점에 자동 생성됩니다. backing index도 함께 만들어지고, 해당 문서가 쓰기 인덱스에 저장됩니다.

Data Stream에 대한 검색은 일반 인덱스 검색과 동일합니다. Data Stream 이름을 대상으로 검색하면 모든 backing index를 자동으로 탐색합니다.

```json
GET logs-my-app/_search
{
  "query": {
    "range": {
      "@timestamp": {
        "gte": "now-7d",
        "lte": "now"
      }
    }
  }
}
```

이 쿼리는 최근 7일간의 로그를 조회합니다. Elasticsearch는 @timestamp 범위에 해당하는 backing index만 선택적으로 탐색하므로, 전체 backing index를 스캔하지 않아도 됩니다.

Data Stream과 ILM의 연동은 자연스럽습니다. 인덱스 템플릿에서 ILM 정책을 지정하면, 각 backing index가 해당 정책의 페이즈를 순서대로 거칩니다. Hot 페이즈의 rollover 조건이 충족되면 새 backing index가 생성되고, 이전 backing index는 Warm, Cold, Delete 페이즈로 자동 전환됩니다.

Data Stream은 추가 전용(append-only) 설계를 따릅니다. Data Stream 이름을 대상으로 직접 update나 delete 요청을 보낼 수 없습니다. 이미 저장된 문서를 수정해야 할 경우에는 backing index 이름을 직접 지정하거나, update_by_query, delete_by_query API를 사용합니다. 이는 시계열 데이터의 특성상 기존 데이터를 변경하는 일이 거의 없기 때문에 취한 설계 결정입니다.

Data Stream을 삭제하면 그 아래의 모든 backing index가 함께 삭제됩니다. 특정 backing index만 개별로 삭제할 수도 있지만, 쓰기 인덱스는 삭제할 수 없습니다. 오래된 backing index만 정리하고 싶다면 ILM의 delete 페이즈에 맡기는 것이 안전합니다.

정리하면, Data Stream은 시계열 데이터를 위한 추상 계층으로, 하나의 이름 아래 여러 backing index를 자동으로 관리합니다. @timestamp 필드가 필수이며, 인덱스 템플릿에 data_stream 옵션을 설정하여 생성합니다. ILM 정책을 연결하면 backing index가 Hot에서 Delete까지 자동으로 전환되므로, 시계열 데이터의 수명주기를 체계적으로 운영할 수 있습니다.

다음 단원인 6.1.3에서는 Searchable Snapshot을 다룹니다. Cold와 Frozen 티어에서 스냅샷을 직접 검색하여 스토리지 비용을 절감하는 방법을 알아봅니다.

이 단원을 마치면 Data Stream을 생성하고 시계열 데이터를 인덱싱할 수 있으며, Data Stream의 backing index 구조를 설명할 수 있습니다.
