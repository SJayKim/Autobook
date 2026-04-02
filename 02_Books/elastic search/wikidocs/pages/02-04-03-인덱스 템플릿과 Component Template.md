# 2.4.3 인덱스 템플릿과 Component Template

Elasticsearch를 운영하다 보면 인덱스를 하나만 만들어 쓰는 경우는 드뭅니다. 로그 데이터는 날짜별로 새 인덱스를 만들고, 서비스 확장에 따라 용도별 인덱스가 늘어납니다. 인덱스를 새로 만들 때마다 매핑, 샤드 수, 레플리카 수, 별칭 같은 설정을 일일이 지정하는 것은 반복 작업이면서 실수의 원인이 됩니다. 한 인덱스에만 샤드 수를 다르게 넣거나, 날짜 필드의 format을 빠뜨리는 일이 생길 수 있습니다.

이 문제를 해결하는 장치가 **인덱스 템플릿**(index template)입니다. 인덱스 템플릿은 "어떤 이름 패턴에 맞는 인덱스가 만들어질 때, 이 설정을 자동으로 적용하라"는 규칙을 미리 등록해 두는 기능입니다. 템플릿을 한 번 정의해 놓으면, 패턴에 맞는 이름으로 인덱스를 생성할 때마다 매핑, 설정, 별칭이 자동으로 부여됩니다. 사람이 매번 동일한 설정을 직접 입력할 필요가 없으므로, 수백 개의 인덱스에도 일관된 구성을 유지할 수 있습니다.

Elasticsearch에는 인덱스 템플릿의 구현이 두 가지 존재합니다. 하나는 과거에 사용하던 **레거시 템플릿**이고, 다른 하나는 현재 권장되는 **조합형 템플릿**(composable template)입니다. 레거시 템플릿은 `_template` API로 관리했습니다. 이 방식에서는 하나의 템플릿이 매핑, 설정, 별칭을 모두 한 덩어리로 담고 있었습니다. 구성 요소를 분리하거나 재사용하는 구조가 아니었기 때문에, 비슷한 설정을 여러 템플릿에 걸쳐 반복해서 작성해야 했습니다. 현재 이 API는 더 이상 권장되지 않으며, 조합형 템플릿으로 대체되었습니다.

조합형 템플릿은 `_index_template` API로 관리합니다. 레거시 방식과 가장 큰 차이는, 설정을 작은 단위로 분리한 뒤 조합할 수 있다는 점입니다. 이 작은 단위가 바로 **Component Template**이며, 뒤에서 자세히 다룹니다. 이 단원에서 '인덱스 템플릿'이라 하면, 특별한 언급이 없는 한 조합형 템플릿을 가리킵니다.

인덱스 템플릿의 핵심 요소는 **인덱스 패턴**(index_patterns)입니다. index_patterns는 이 템플릿이 어떤 이름의 인덱스에 적용될지를 결정하는 와일드카드 패턴입니다. 예를 들어 `["*orders"]`라고 지정하면, 이름이 "orders"로 끝나는 모든 인덱스에 이 템플릿의 설정이 적용됩니다. "sales-orders", "return-orders"처럼 이름이 다르더라도, 끝이 "orders"로 일치하면 동일한 매핑과 설정을 자동으로 받습니다.

아래 예시는 인덱스 템플릿을 생성하는 요청입니다.

```json
PUT _index_template/orders_template
{
  "index_patterns": ["*orders"],
  "priority": 300,
  "template": {
    "mappings": {
      "properties": {
        "order_date": {
          "type": "date",
          "format": "dd-MM-yyyy"
        }
      }
    },
    "settings": {
      "number_of_shards": 5,
      "number_of_replicas": 2
    },
    "aliases": {
      "all_orders": {}
    }
  }
}
```

이 요청의 각 부분을 살펴봅니다. `PUT _index_template/orders_template`에서 `_index_template`은 조합형 템플릿을 관리하는 엔드포인트이고, `orders_template`은 이 템플릿의 이름입니다. `index_patterns`는 앞서 설명한 대로 적용 대상 인덱스의 이름 패턴입니다. `priority`는 이 템플릿의 우선순위인데, 바로 아래에서 설명합니다. `template` 객체 안에는 실제로 인덱스에 적용될 매핑, 설정, 별칭이 들어갑니다. 이 예시에서는 order_date 필드를 date 타입으로 정의하고, 샤드 5개와 레플리카 2개를 설정하며, all_orders라는 별칭을 자동 부여합니다.

이 템플릿을 등록한 뒤 `PUT /my-sales-orders`로 새 인덱스를 만들면, 이름이 "orders"로 끝나므로 위 템플릿이 자동 적용됩니다. 사용자가 매핑이나 설정을 별도로 지정하지 않아도, order_date 필드와 샤드 설정, 별칭이 모두 부여된 상태로 인덱스가 생성됩니다.

이름 패턴이 동일한 템플릿이 여러 개 존재할 수 있습니다. 예를 들어 `*orders` 패턴을 사용하는 템플릿이 두 개 있고, 하나는 priority가 300이고 다른 하나는 1000이라고 가정합니다. 이때 Elasticsearch는 **우선순위**(priority)가 더 높은 템플릿의 설정을 적용합니다. priority 값이 클수록 우선순위가 높습니다. priority가 1000인 템플릿이 300인 템플릿보다 우선합니다.

여기서 주의할 점이 있습니다. 조합형 템플릿에서는 우선순위가 높은 템플릿 하나만 선택됩니다. 레거시 템플릿에서는 여러 템플릿이 겹치면 설정을 병합했지만, 조합형 템플릿에서는 가장 높은 priority를 가진 템플릿 한 개만 적용됩니다. 따라서 동일한 패턴에 대해 여러 템플릿을 두었을 때, 의도한 템플릿이 선택되도록 priority 값을 신중하게 설정해야 합니다.

인덱스 생성 시 템플릿 설정과 함께 사용자가 직접 지정한 설정이 있을 수도 있습니다. 예를 들어 `PUT /my-orders`를 호출하면서 body에 샤드 수를 3으로 직접 지정했다면, 템플릿에 샤드 수가 5로 정의되어 있더라도 사용자가 직접 지정한 3이 적용됩니다. 직접 지정한 설정은 항상 템플릿보다 우선합니다.

지금까지는 하나의 인덱스 템플릿이 매핑, 설정, 별칭을 모두 담고 있는 형태를 보았습니다. 이 방식은 간단하지만, 동일한 설정을 여러 템플릿에서 반복해야 하는 문제가 남아 있습니다. 예를 들어 주문 관련 템플릿과 결제 관련 템플릿이 동일한 샤드 설정을 사용한다면, 두 템플릿 모두에 같은 settings 블록을 작성해야 합니다. 나중에 샤드 수를 바꾸려면 두 템플릿을 모두 수정해야 합니다. 이런 중복과 관리 비용을 줄이기 위해 **Component Template**이 존재합니다.

Component Template은 매핑, 설정, 별칭 중 일부만 따로 떼어 독립적으로 정의한 재사용 가능한 블록입니다. Component Template 자체는 인덱스 패턴을 갖지 않습니다. 따라서 Component Template만으로는 인덱스에 아무 설정도 적용되지 않습니다. 반드시 인덱스 템플릿이 Component Template을 참조해야 실제로 동작합니다. 이 관계를 비유하면, Component Template은 부품이고 인덱스 템플릿은 그 부품을 조립한 완제품입니다.

Component Template은 `_component_template` API로 관리합니다. 아래는 설정(settings)만 담은 Component Template을 생성하는 예시입니다.

```json
PUT _component_template/settings_component
{
  "template": {
    "settings": {
      "number_of_shards": 5,
      "number_of_replicas": 2
    }
  }
}
```

이 요청은 settings_component라는 이름의 Component Template을 등록합니다. 내부에는 샤드 5개, 레플리카 2개라는 설정만 들어 있습니다. 매핑이나 별칭은 포함하지 않습니다.

같은 방식으로 매핑만 담은 Component Template도 만들 수 있습니다.

```json
PUT _component_template/mappings_component
{
  "template": {
    "mappings": {
      "properties": {
        "order_date": {
          "type": "date",
          "format": "dd-MM-yyyy"
        }
      }
    }
  }
}
```

별칭만 담은 Component Template도 별도로 만들 수 있습니다.

```json
PUT _component_template/aliases_component
{
  "template": {
    "aliases": {
      "all_orders": {},
      "sales_orders": {}
    }
  }
}
```

이렇게 설정, 매핑, 별칭을 각각 독립된 Component Template으로 분리했습니다. 이제 이 부품들을 하나의 인덱스 템플릿으로 조합합니다. 조합에 사용하는 필드가 **composed_of**입니다.

```json
PUT _index_template/composed_orders_template
{
  "index_patterns": ["*orders"],
  "priority": 500,
  "composed_of": [
    "settings_component",
    "mappings_component",
    "aliases_component"
  ]
}
```

composed_of 필드에 배열로 나열한 세 개의 Component Template이 이 인덱스 템플릿에 결합됩니다. 이름이 "orders"로 끝나는 인덱스가 생성되면, 세 Component Template의 설정이 모두 병합되어 적용됩니다. 결과적으로 앞서 본 단일 인덱스 템플릿과 동일한 구성을 만들어 내지만, 각 부분을 독립적으로 관리할 수 있다는 차이가 있습니다.

이 구조의 이점은 재사용에서 드러납니다. settings_component를 주문 관련 템플릿뿐 아니라 결제 관련 템플릿에서도 composed_of에 포함시키면, 두 템플릿이 동일한 샤드 설정을 공유합니다. 나중에 샤드 수를 바꾸려면 settings_component 하나만 수정하면, 이를 참조하는 모든 인덱스 템플릿에 변경이 반영됩니다.

composed_of 배열에서 순서도 의미가 있습니다. 배열의 뒤쪽에 위치한 Component Template이 앞쪽보다 우선합니다. 만약 두 Component Template이 동일한 설정 키를 가지고 있다면, 뒤에 나열된 Component Template의 값이 앞의 값을 덮어씁니다. 또한 인덱스 템플릿 자체의 template 객체에 설정을 직접 넣으면, 그 값이 모든 Component Template보다 우선합니다.

이 우선순위 규칙을 정리하면 다음과 같습니다.

```
설정 적용 우선순위 (높은 것이 낮은 것을 덮어씀)

1. 인덱스 생성 시 사용자가 직접 지정한 설정  (가장 높음)
2. 인덱스 템플릿 자체의 template 객체 설정
3. composed_of 배열의 뒤쪽 Component Template
4. composed_of 배열의 앞쪽 Component Template   (가장 낮음)
```

인덱스 템플릿은 **데이터 스트림**(data stream)과도 연결됩니다. 데이터 스트림은 시계열 데이터를 자동으로 롤오버되는 인덱스 시퀀스로 관리하는 기능입니다. 로그, 메트릭 같이 시간 순서대로 계속 쌓이는 데이터에 적합합니다. 데이터 스트림을 사용하려면 반드시 인덱스 템플릿을 먼저 만들어야 합니다. 템플릿에 `"data_stream": {}` 필드를 추가하면, 해당 패턴으로 생성되는 인덱스가 데이터 스트림의 뒷받침 인덱스(backing index)로 동작합니다. 데이터 스트림의 뒷받침 인덱스는 롤오버 조건(크기, 문서 수, 시간 등)에 따라 자동으로 새로 생성되는데, 이때마다 인덱스 템플릿의 설정이 자동 적용됩니다. 템플릿 없이는 데이터 스트림이 새 뒷받침 인덱스를 어떤 매핑과 설정으로 만들어야 하는지 알 수 없으므로, 둘은 반드시 함께 사용됩니다.

템플릿을 등록한 뒤, 실제로 인덱스를 만들기 전에 어떤 설정이 적용될지 미리 확인하고 싶을 때가 있습니다. Elasticsearch는 이를 위해 **시뮬레이션 API**를 제공합니다. 시뮬레이션은 인덱스를 실제로 생성하지 않고, 어떤 매핑, 설정, 별칭이 적용되는지 결과만 돌려줍니다.

시뮬레이션에는 두 가지 방식이 있습니다. 첫 번째는 특정 인덱스 이름을 기준으로 시뮬레이션하는 것입니다.

```json
POST _index_template/_simulate_index/my-new-orders-index
```

이 요청은 "my-new-orders-index"라는 이름으로 인덱스를 만든다면 어떤 템플릿이 매칭되고 어떤 설정이 적용되는지를 보여 줍니다. 이름이 "orders"로 끝나므로 앞서 등록한 composed_orders_template이 매칭되고, 그 결과로 병합된 매핑, 설정, 별칭 전체가 응답에 포함됩니다.

두 번째는 특정 템플릿 자체를 시뮬레이션하는 것입니다.

```json
POST _index_template/_simulate/orders_template
```

이 요청은 orders_template이 적용되었을 때 최종 결과가 어떻게 되는지를 보여 줍니다. 해당 템플릿이 composed_of로 참조하는 Component Template들의 설정이 병합된 상태를 확인할 수 있습니다.

시뮬레이션 API는 실제 인덱스를 만들지 않으므로, 운영 환경에서도 부담 없이 사용할 수 있습니다. 템플릿을 새로 등록하거나 Component Template을 수정한 뒤, 의도한 대로 설정이 병합되는지 검증하는 용도로 활용합니다.

아래 다이어그램은 인덱스 템플릿과 Component Template의 관계, 그리고 인덱스 생성까지의 흐름을 정리한 것입니다.

```
Component Template (부품)              인덱스 템플릿 (완제품)
+---------------------+
| settings_component  |---+
| (shards, replicas)  |   |
+---------------------+   |    +-------------------------------+
                           +--->|                               |
+---------------------+   |    | composed_orders_template      |
| mappings_component  |---+    |   index_patterns: ["*orders"] |     인덱스 생성
| (order_date: date)  |   |    |   priority: 500               |---> PUT /my-sales-orders
+---------------------+   |    |   composed_of: [위 3개]       |     -> 템플릿 자동 적용
                           +--->|                               |
+---------------------+   |    +-------------------------------+
| aliases_component   |---+
| (all_orders, ...)   |
+---------------------+
```

정리하면, 인덱스 템플릿은 이름 패턴에 맞는 인덱스가 생성될 때 매핑, 설정, 별칭을 자동으로 적용하는 규칙입니다. 현행 조합형 템플릿(`_index_template` API)은 레거시 `_template` API를 대체하며, Component Template을 composed_of로 조합하여 설정의 재사용성과 관리 편의를 높입니다. 여러 템플릿이 같은 패턴에 매칭될 때는 priority가 높은 템플릿이 선택되고, 인덱스 생성 시 직접 지정한 설정은 항상 최우선입니다. 데이터 스트림을 사용하려면 반드시 인덱스 템플릿을 먼저 정의해야 하며, 시뮬레이션 API로 설정 병합 결과를 사전 검증할 수 있습니다.

다음 단원인 2.4.4에서는 인덱스 별칭을 다룹니다.

이 단원을 마치면 인덱스 템플릿으로 인덱스 자동 설정을 구성할 수 있고, Component Template을 조합하여 재사용 가능한 매핑 블록을 관리할 수 있습니다.
