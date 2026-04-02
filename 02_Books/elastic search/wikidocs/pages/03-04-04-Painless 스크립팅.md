# 3.4.4 Painless 스크립팅

3.4.3에서 function_score 쿼리의 script_score 함수를 살펴보았습니다. weight, field_value_factor, decay 함수로 표현할 수 없는 복잡한 점수 계산이 필요할 때 Painless 스크립트를 직접 작성한다고 소개했습니다. 그런데 script_score에서 짧은 코드 한 줄을 보여준 것만으로는 Painless가 어떤 언어인지, 어떻게 동작하는지, 성능 문제는 없는지 파악하기 어렵습니다. 이 단원에서는 Painless 언어 자체의 특징부터 시작하여, 점수 계산과 문서 변환에 활용하는 방법, 그리고 성능을 최적화하는 기법까지 다룹니다.

Elasticsearch에서 스크립트가 필요한 상황을 먼저 생각해 봅니다. 인덱스에 price라는 필드가 있고, 세금을 포함한 가격을 검색 결과에 함께 보여주고 싶다고 합시다. price * 1.1이라는 간단한 곱셈이지만, 이 계산 결과는 인덱스에 저장된 필드가 아닙니다. 매핑을 바꿔 새 필드를 추가하고 모든 문서를 다시 색인하는 방법도 있지만, 계산 로직이 바뀔 때마다 재색인하는 것은 부담이 큽니다. 이런 상황에서 Elasticsearch는 쿼리 시점에 스크립트를 실행하여 값을 계산하는 기능을 제공합니다. 그 스크립트를 작성하는 언어가 바로 **Painless**입니다.

Painless는 Elasticsearch 전용으로 설계된 스크립팅 언어입니다. 이름에 "painless"(고통 없는)를 붙인 이유가 있습니다. Elasticsearch는 과거에 Groovy라는 범용 스크립팅 언어를 사용했는데, Groovy는 JVM 위에서 실행되는 강력한 언어이지만 보안 취약점이 반복적으로 발견되었습니다. 악의적인 사용자가 스크립트를 통해 서버의 파일 시스템에 접근하거나, 임의의 시스템 명령을 실행하는 공격이 가능했습니다. Elasticsearch 팀은 이 문제를 근본적으로 해결하기 위해 처음부터 보안을 고려한 새 언어를 만들었고, 그것이 Painless입니다.

Painless의 핵심 특징은 세 가지입니다. 첫째, **샌드박스** 환경에서 실행됩니다. 샌드박스란 프로그램이 접근할 수 있는 범위를 엄격히 제한하는 격리 환경을 말합니다. Painless 스크립트는 파일 시스템, 네트워크, 시스템 명령에 접근할 수 없습니다. 오직 Elasticsearch가 허용한 API와 데이터에만 접근할 수 있습니다. 이 덕분에 외부 사용자가 검색 쿼리에 스크립트를 포함하더라도 서버가 위험에 노출되지 않습니다.

둘째, **정적 타입** 언어입니다. 모든 변수와 표현식의 타입이 컴파일 시점에 결정됩니다. int, double, boolean 같은 기본 타입과 String, Map, List 같은 복합 타입을 사용합니다. 정적 타입이라는 것은, 변수를 선언할 때 어떤 종류의 값을 담을지 미리 정해야 한다는 뜻입니다. 이 덕분에 스크립트를 실행하기 전에 타입 오류를 잡을 수 있고, 컴파일러가 효율적인 바이트코드를 생성할 수 있습니다.

셋째, **JVM 바이트코드로 컴파일**됩니다. Painless 스크립트는 텍스트 그대로 한 줄씩 해석되는 것이 아니라, Elasticsearch가 이를 JVM(자바 가상 머신) 바이트코드로 변환합니다. 바이트코드는 JVM이 직접 실행하는 저수준 명령어입니다. 이 과정 덕분에 Painless 스크립트의 실행 속도가 네이티브 자바 코드에 가깝습니다.

Painless의 문법은 자바와 유사합니다. 산술 연산자(+, -, *, /, %), 비교 연산자(<, >, ==, !=), 논리 연산자(&&, ||, !)를 사용하고, if/else 조건문과 for, while 반복문을 지원합니다. 자바를 접해 본 적이 있다면 익숙한 형태입니다. 자바를 모르더라도, 대부분의 프로그래밍 언어에서 공통으로 사용하는 문법이므로 어렵지 않습니다.

이제 Painless를 실제로 사용하는 첫 번째 맥락인 **script_score 쿼리**를 살펴봅니다. 3.4.3에서 function_score 안에 script_score 함수를 넣는 방식을 보았는데, Elasticsearch는 script_score를 독립적인 쿼리 타입으로도 제공합니다. function_score 쿼리의 여러 함수 중 하나로 쓰는 것과 달리, script_score 쿼리는 스크립트 하나만으로 점수를 계산할 때 간결하게 사용할 수 있습니다.

```json
{
  "query": {
    "script_score": {
      "query": {
        "match": { "title": "elasticsearch" }
      },
      "script": {
        "source": "Math.log(1 + doc['likes'].value) + _score"
      }
    }
  }
}
```

이 쿼리의 구조를 하나씩 살펴봅니다. "query" 안에 "script_score"를 선언합니다. 그 안에 두 부분이 있습니다. 첫 번째 "query"는 기본 검색 쿼리입니다. 위 예시에서는 title 필드에서 "elasticsearch"를 찾는 match 쿼리를 넣었습니다. 이 쿼리가 매칭된 문서 집합을 결정하고, 각 문서에 BM25 점수(_score)를 부여합니다. 두 번째 "script"는 최종 점수를 계산하는 Painless 코드입니다.

"source" 필드의 코드를 분석합니다. doc['likes'].value는 현재 문서의 likes 필드 값을 읽습니다. Math.log(1 + doc['likes'].value)는 좋아요 수에 1을 더한 뒤 자연로그를 취합니다. 1을 더하는 이유는 좋아요가 0인 문서에서 log(0)이 음의 무한대가 되는 것을 방지하기 위함입니다. 여기에 _score(BM25 점수)를 더하여 최종 점수를 만듭니다. 텍스트 관련성과 인기도를 모두 반영하는 점수가 됩니다.

여기서 **doc['field'].value**라는 접근 방식을 자세히 설명합니다. Painless 스크립트에서 문서의 필드 값을 읽는 방법은 크게 두 가지입니다. 하나는 doc['필드명'].value이고, 다른 하나는 params._source['필드명']입니다. 둘 다 같은 필드의 값을 반환하지만 내부 동작이 다릅니다.

doc['필드명'].value는 Elasticsearch가 메모리에 미리 로드해 둔 필드 데이터(doc values)를 읽습니다. doc values는 색인 시점에 열 기반 형태로 저장된 데이터입니다. 이미 메모리에 올라와 있으므로 접근 속도가 빠릅니다.

params._source['필드명']는 문서의 원본 JSON(_source)을 파싱하여 값을 꺼냅니다. _source는 문서를 색인할 때 저장한 원본 JSON 전체입니다. 매번 JSON 텍스트를 파싱해야 하므로 doc values 방식보다 훨씬 느립니다.

성능 차이가 크기 때문에, 스크립트에서 필드 값을 읽을 때는 doc['필드명'].value를 사용하는 것이 원칙입니다. params._source는 doc values로 접근할 수 없는 특수한 경우에만 사용합니다.

다음으로 **params 파라미터화**를 살펴봅니다. 앞서 3.4.3에서 params 객체로 가중치를 스크립트 외부에서 주입하는 예시를 잠깐 보았습니다. 이 기법이 왜 중요한지 성능 관점에서 설명합니다.

Elasticsearch는 Painless 스크립트를 처음 실행할 때 JVM 바이트코드로 컴파일합니다. 이 컴파일 과정에는 시간이 걸립니다. 같은 스크립트가 다시 실행되면, Elasticsearch는 **컴파일 캐시**에서 이미 컴파일된 결과를 꺼내 재사용합니다. 기본적으로 최대 100개의 컴파일된 스크립트가 캐시에 보관됩니다.

여기서 핵심은, 캐시의 키가 스크립트의 소스 코드 문자열이라는 점입니다. 소스 코드가 한 글자라도 다르면 Elasticsearch는 이를 다른 스크립트로 취급하고 새로 컴파일합니다. 아래 두 스크립트를 비교합니다.

```json
{
  "script": {
    "source": "0.5 * doc['likes'].value + 0.3 * doc['views'].value"
  }
}
```

```json
{
  "script": {
    "source": "0.7 * doc['likes'].value + 0.2 * doc['views'].value"
  }
}
```

두 스크립트는 구조가 같고 가중치만 다릅니다. 그런데 소스 코드 문자열이 다르기 때문에 Elasticsearch는 각각 별도로 컴파일합니다. 가중치 조합이 10가지이면 10번 컴파일이 발생합니다. 짧은 시간에 컴파일이 반복되면 Elasticsearch가 "too many dynamic script compilations" 오류를 발생시킬 수 있습니다.

params를 사용하면 이 문제가 해결됩니다.

```json
{
  "script": {
    "source": "params.likes_weight * doc['likes'].value + params.views_weight * doc['views'].value",
    "params": {
      "likes_weight": 0.5,
      "views_weight": 0.3
    }
  }
}
```

"source"의 코드는 항상 동일합니다. 달라지는 값은 "params"에 넣습니다. Elasticsearch는 source 문자열이 같으므로 캐시에서 컴파일된 바이트코드를 재사용하고, params 값만 바꿔서 실행합니다. 가중치를 아무리 자주 바꿔도 컴파일은 최초 한 번만 발생합니다.

이 원리를 정리하면 다음과 같습니다.

```
params 파라미터화와 컴파일 캐시

[값을 source에 직접 넣는 경우]

  "source": "0.5 * doc['likes'].value"   --> 컴파일 --> 캐시 저장 (키: 소스 코드 A)
  "source": "0.7 * doc['likes'].value"   --> 컴파일 --> 캐시 저장 (키: 소스 코드 B)
  "source": "0.9 * doc['likes'].value"   --> 컴파일 --> 캐시 저장 (키: 소스 코드 C)
  결과: 3번 컴파일

[params로 분리하는 경우]

  "source": "params.w * doc['likes'].value", "params": {"w": 0.5}  --> 컴파일 --> 캐시 저장
  "source": "params.w * doc['likes'].value", "params": {"w": 0.7}  --> 캐시 히트 (소스 동일)
  "source": "params.w * doc['likes'].value", "params": {"w": 0.9}  --> 캐시 히트 (소스 동일)
  결과: 1번 컴파일
```

스크립트를 작성할 때는 변할 수 있는 값을 source 안에 직접 쓰지 말고, 반드시 params로 분리하는 습관을 들이는 것이 좋습니다.

지금까지 검색 시 점수 계산에 Painless를 사용하는 방법을 살펴보았습니다. Painless는 검색뿐 아니라 문서를 변경하는 작업에도 사용됩니다. 대표적인 것이 **update 스크립트**입니다.

Elasticsearch에서 문서를 부분 수정할 때는 _update API를 사용합니다. 단순히 특정 필드의 값을 새 값으로 바꾸는 것은 "doc" 방식으로 충분합니다. 하지만 기존 값을 기반으로 계산하여 새 값을 설정해야 하는 경우가 있습니다. 예를 들어, 조회수 필드를 1 증가시키거나, 태그 배열에 새 항목을 추가하는 경우입니다. 이때 Painless 스크립트를 사용합니다.

```json
POST my-index/_update/1
{
  "script": {
    "source": "ctx._source.views += 1"
  }
}
```

이 요청은 ID가 1인 문서의 views 필드 값을 1 증가시킵니다. update 스크립트에서는 doc['field'].value 대신 **ctx._source**를 사용합니다. ctx는 "context"의 줄임말로, 현재 처리 중인 문서의 맥락 정보를 담고 있습니다. ctx._source는 그 문서의 원본 JSON에 해당합니다. update 작업에서는 값을 읽기만 하는 것이 아니라 값을 변경해야 하므로, 읽기 전용인 doc values가 아니라 변경 가능한 _source 객체를 사용하는 것입니다.

좀 더 복잡한 예시를 봅니다. 태그 목록에 새 태그가 없을 때만 추가하는 스크립트입니다.

```json
POST my-index/_update/1
{
  "script": {
    "source": "if (!ctx._source.tags.contains(params.new_tag)) { ctx._source.tags.add(params.new_tag) }",
    "params": {
      "new_tag": "elasticsearch"
    }
  }
}
```

ctx._source.tags는 문서의 tags 배열을 참조합니다. contains 메서드로 이미 해당 태그가 있는지 확인하고, 없을 때만 add로 추가합니다. 추가할 태그를 params로 분리했으므로, 같은 스크립트 구조로 어떤 태그든 추가할 수 있고 컴파일 캐시도 활용됩니다.

reindex(재색인) 작업에서도 ctx._source를 사용합니다. 예를 들어 필드 이름을 바꾸면서 문서를 새 인덱스로 복사하는 경우입니다.

```json
POST /_reindex
{
  "source": { "index": "old-index" },
  "dest": { "index": "new-index" },
  "script": {
    "source": "ctx._source.timestamp = ctx._source.remove('created_at')"
  }
}
```

ctx._source.remove('created_at')는 원본 문서에서 created_at 필드를 제거하면서 그 값을 반환합니다. 반환된 값을 ctx._source.timestamp에 대입하여 새 필드명으로 저장합니다. 결과적으로 created_at 필드가 timestamp로 이름이 바뀐 문서가 새 인덱스에 저장됩니다.

정리하면, doc['field'].value와 ctx._source는 용도가 다릅니다. 검색 시 점수 계산처럼 값을 읽기만 하는 맥락에서는 doc['field'].value를 사용합니다. 성능이 빠르고, 스크립트가 실행되는 검색 컨텍스트에서 최적화된 방식입니다. update나 reindex처럼 문서의 내용을 변경해야 하는 맥락에서는 ctx._source를 사용합니다. 변경 가능한 원본 JSON 객체이기 때문입니다.

```
필드 접근 방식 비교

방식                       | 읽기/쓰기 | 속도  | 사용 맥락
--------------------------|----------|-------|---------------------------
doc['field'].value        | 읽기 전용 | 빠름  | script_score, 검색 시 계산
ctx._source.field         | 읽기/쓰기 | 느림  | _update, reindex, ingest
```

Painless를 사용할 때 성능 면에서 주의할 점이 있습니다. 스크립트는 Lucene의 쿼리 최적화를 우회합니다. Lucene은 역색인, 캐시, 건너뛰기 등 다양한 최적화를 사용하여 쿼리를 빠르게 처리하는데, 스크립트는 이런 최적화의 혜택을 받지 못합니다. 문서 하나하나마다 스크립트를 실행해야 하기 때문입니다. 필터 없이 인덱스의 전체 문서에 스크립트를 실행하면 성능이 크게 저하됩니다. 반드시 query나 filter로 대상 문서를 먼저 좁힌 뒤 스크립트를 적용해야 합니다.

또한 자주 사용하는 스크립트는 **저장 스크립트(stored script)**로 등록하면 관리가 편합니다. 저장 스크립트는 클러스터 상태에 미리 등록해 두고, ID로 참조하여 실행하는 방식입니다.

```
POST _scripts/my_scoring_script
{
  "script": {
    "lang": "painless",
    "source": "doc['popularity'].value * params.boost"
  }
}
```

이 요청은 "my_scoring_script"라는 ID로 스크립트를 등록합니다. "lang"에 "painless"를 명시하고, "source"에 스크립트 코드를 넣습니다. 등록 이후에는 쿼리에서 source 대신 id로 참조합니다.

```json
{
  "query": {
    "script_score": {
      "query": { "match_all": {} },
      "script": {
        "id": "my_scoring_script",
        "params": { "boost": 2.0 }
      }
    }
  }
}
```

저장 스크립트는 두 가지 이점이 있습니다. 첫째, 스크립트 코드가 클러스터에 한 번만 저장되므로 여러 쿼리에서 동일한 로직을 재사용할 때 일관성을 유지할 수 있습니다. 둘째, 저장 시점에 컴파일이 완료되므로 쿼리 실행 시 컴파일 지연이 발생하지 않습니다.

정리하면, Painless는 Elasticsearch 전용 스크립팅 언어로, 샌드박스 보안, 정적 타입, JVM 바이트코드 컴파일이라는 세 가지 특징을 갖추고 있습니다. script_score 쿼리에서 커스텀 점수를 계산하고, update 작업에서 ctx._source를 통해 문서를 변경하며, 변할 수 있는 값은 params로 분리하여 컴파일 캐시를 활용합니다. 필드 값을 읽을 때는 doc['field'].value를, 문서를 변경할 때는 ctx._source를 사용합니다. 스크립트는 Lucene 최적화를 우회하므로 반드시 필터로 대상을 좁힌 뒤 적용해야 합니다.

다음 단원인 3.4.5에서는 Explain API와 스코어 디버깅을 다룹니다. 스크립트가 적용된 점수가 기대와 다를 때, Explain API로 점수 산출 과정을 단계별로 확인하는 방법을 살펴봅니다.

이 단원을 마치면 Painless 스크립트로 커스텀 스코어 계산과 필드 변환을 구현할 수 있고, 스크립트 캐싱과 파라미터화로 성능을 최적화할 수 있습니다.

<!-- INCOMPLETE: script_fields, Painless 디버깅 방법 -->
