# 3.1.3 Bulk API

3.1.2에서 문서를 한 건씩 생성, 조회, 수정, 삭제하는 CRUD API를 살펴보았습니다. PUT /_doc으로 문서를 만들고, POST /_update로 수정하고, DELETE /_doc으로 지우는 방식이었습니다. 문서가 몇 건일 때는 이 방식으로 충분합니다. 그런데 로그 데이터를 하루에 수백만 건 적재해야 하거나, 기존 데이터베이스의 레코드 수만 건을 Elasticsearch로 옮겨야 하는 상황을 떠올려 봅니다. 한 건마다 HTTP 요청을 보내면, 매 요청마다 TCP 연결을 맺고 응답을 기다리는 시간이 누적됩니다. 만 건이면 만 번의 왕복이 발생합니다. 네트워크 왕복 비용이 실제 인덱싱 시간보다 커지는 것입니다.

이 문제를 해결하는 방법은 여러 작업을 하나의 요청에 묶어 보내는 것입니다. Elasticsearch는 이를 위해 **Bulk API**를 제공합니다. Bulk API를 사용하면 한 번의 HTTP 요청으로 수백에서 수천 건의 인덱싱, 수정, 삭제를 동시에 처리할 수 있습니다. 네트워크 왕복이 한 번으로 줄어들기 때문에, 대량 데이터를 다루는 상황에서 처리 속도가 크게 향상됩니다.

Bulk API의 엔드포인트는 **_bulk**입니다. 3.1.1에서 Elasticsearch REST API의 URL 패턴이 '/{인덱스}/{엔드포인트}' 형태를 따른다는 것을 배웠습니다. Bulk API도 같은 규칙을 따릅니다. 인덱스를 URL에 포함하면 해당 인덱스에 대해서만 작업하고, 생략하면 요청 본문에서 인덱스를 개별 지정합니다.

```
POST /_bulk
POST /my_index/_bulk
```

첫 번째 형태는 인덱스를 지정하지 않은 것이므로, 요청 본문의 각 작업마다 어느 인덱스에 보낼지를 명시해야 합니다. 두 번째 형태는 모든 작업이 my_index 인덱스를 대상으로 합니다. 대부분의 경우 하나의 인덱스에 대량으로 넣는 상황이 많으므로, 두 번째 형태를 자주 사용합니다.

Bulk API의 요청 본문은 일반적인 JSON과 다른 형식을 사용합니다. 이 형식을 **NDJSON**(Newline Delimited JSON)이라고 부릅니다. NDJSON은 JSON 객체를 한 줄에 하나씩 놓고, 줄바꿈 문자로 구분하는 형식입니다. 일반 JSON 배열처럼 대괄호로 감싸거나 쉼표로 연결하지 않습니다.

왜 일반 JSON 배열을 쓰지 않는지 의문이 들 수 있습니다. Elasticsearch가 NDJSON을 채택한 이유는 메모리 효율 때문입니다. JSON 배열이면 전체를 메모리에 읽어 들여 파싱해야 합니다. 문서 수만 건이 담긴 요청을 한꺼번에 파싱하면 메모리 사용량이 급증합니다. 반면 NDJSON은 한 줄씩 읽어 처리할 수 있으므로, 전체를 메모리에 올리지 않고도 순차적으로 처리할 수 있습니다.

Bulk API의 NDJSON 본문은 **액션 줄**과 **소스 줄**이 번갈아 나오는 구조입니다. 액션 줄은 "어떤 작업을 할 것인가"를 지정하고, 소스 줄은 "어떤 데이터를 사용할 것인가"를 담습니다. 이 두 줄이 한 쌍을 이룹니다.

```
{ "index": { "_index": "my_index", "_id": "1" } }
{ "field1": "value1", "field2": "value2" }
```

첫 번째 줄이 액션 줄입니다. "index"라는 키가 작업 종류를 나타냅니다. 그 안의 "_index"는 대상 인덱스, "_id"는 문서 ID입니다. 두 번째 줄이 소스 줄입니다. 실제로 저장할 문서 데이터가 들어갑니다. 3.1.2에서 PUT /_doc/{id}로 보내던 요청 바디와 같은 내용입니다.

중요한 규칙이 있습니다. 각 줄은 반드시 한 줄로 작성해야 합니다. JSON을 보기 좋게 들여쓰기하는 이른바 "pretty print"를 하면 안 됩니다. Elasticsearch는 줄바꿈 문자를 기준으로 액션 줄과 소스 줄을 구분하기 때문입니다. 또한 마지막 줄 뒤에도 반드시 줄바꿈 문자가 있어야 합니다.

Bulk API가 지원하는 액션은 네 가지입니다. index, create, update, delete가 그것입니다. 하나씩 살펴봅니다.

**index** 액션은 문서를 인덱싱합니다. 해당 ID의 문서가 없으면 새로 생성하고, 이미 있으면 덮어씁니다. 3.1.2에서 PUT /_doc/{id}가 같은 ID에 다시 호출하면 덮어쓴다고 했던 것과 동일한 동작입니다. 액션 줄 다음에 소스 줄이 반드시 따라옵니다.

```
{ "index": { "_index": "products", "_id": "101" } }
{ "name": "Wireless Mouse", "price": 29900 }
```

**create** 액션은 문서를 생성하되, 해당 ID의 문서가 이미 존재하면 실패합니다. 3.1.2에서 PUT /_create/{id}가 중복 시 409 Conflict를 반환하던 것과 같은 동작입니다. 중복 방지가 필요한 경우에 사용합니다. 액션 줄 다음에 소스 줄이 따라옵니다.

```
{ "create": { "_index": "products", "_id": "102" } }
{ "name": "Keyboard", "price": 59000 }
```

**update** 액션은 기존 문서를 부분 수정합니다. 3.1.2에서 POST /_update/{id}로 "doc" 키 안에 변경할 필드를 넣었던 것과 같습니다. 소스 줄에 "doc" 키를 포함하여 수정할 필드를 지정합니다.

```
{ "update": { "_index": "products", "_id": "101" } }
{ "doc": { "price": 24900 } }
```

**delete** 액션은 문서를 삭제합니다. 삭제는 데이터를 보낼 필요가 없으므로, 다른 액션과 달리 소스 줄이 없습니다. 액션 줄 하나만 씁니다.

```
{ "delete": { "_index": "products", "_id": "102" } }
```

아래 다이어그램은 네 가지 액션의 구조를 정리한 것입니다.

```
Bulk API 액션별 NDJSON 구조

index   :  액션 줄  +  소스 줄    -> 없으면 생성, 있으면 덮어씀
create  :  액션 줄  +  소스 줄    -> 없으면 생성, 있으면 실패
update  :  액션 줄  +  소스 줄    -> 기존 문서 부분 수정
delete  :  액션 줄  (소스 없음)   -> 문서 삭제
```

이 네 가지 액션을 하나의 Bulk 요청에 섞어서 보낼 수 있습니다. 예를 들어 문서 두 건을 인덱싱하고, 한 건을 수정하고, 한 건을 삭제하는 요청을 한 번에 보낼 수 있습니다.

```
POST /products/_bulk
{ "index": { "_id": "201" } }
{ "name": "Monitor", "price": 350000 }
{ "index": { "_id": "202" } }
{ "name": "Webcam", "price": 89000 }
{ "update": { "_id": "201" } }
{ "doc": { "price": 329000 } }
{ "delete": { "_id": "202" } }
```

URL에 인덱스 이름 products를 지정했으므로, 각 액션 줄에서 "_index"를 생략할 수 있습니다. 모든 작업이 products 인덱스를 대상으로 합니다. 이 요청 하나로 인덱싱 두 건, 수정 한 건, 삭제 한 건이 처리됩니다.

curl 명령으로 Bulk API를 호출할 때는 Content-Type 헤더와 --data-binary 옵션에 주의해야 합니다.

```bash
curl -X POST "localhost:9200/_bulk" \
  -H "Content-Type: application/json" \
  --data-binary "@bulk_request.json"
```

Content-Type 헤더에 'application/json' 또는 'application/x-ndjson'을 지정합니다. --data-binary 옵션은 파일 내용을 있는 그대로 전송합니다. 일반적인 -d 옵션을 사용하면 curl이 줄바꿈 문자를 제거할 수 있습니다. NDJSON에서 줄바꿈은 각 줄을 구분하는 핵심 요소이므로, 줄바꿈이 사라지면 파싱 오류가 발생합니다. 반드시 --data-binary를 사용합니다.

Bulk API 요청을 보내면 Elasticsearch는 각 작업의 결과를 개별적으로 응답합니다. 한 가지 중요한 특성이 있습니다. 요청에 포함된 작업 중 일부가 실패해도, 나머지 작업은 정상적으로 처리됩니다. 예를 들어 열 건의 인덱싱 요청 중 두 건이 매핑 오류로 실패하더라도, 나머지 여덟 건은 정상적으로 인덱싱됩니다. Bulk API는 전체를 원자적으로 처리하는 트랜잭션이 아닙니다.

이러한 특성 때문에 응답을 반드시 확인해야 합니다. 응답 본문에는 **errors** 필드가 있습니다. 이 필드가 false이면 모든 작업이 성공한 것입니다. true이면 하나 이상의 작업이 실패한 것이므로, **items** 배열을 살펴봐야 합니다. items 배열에는 요청에 포함된 각 작업의 결과가 순서대로 담깁니다. 각 항목에는 상태 코드(status)와 오류 정보(error)가 포함됩니다. 실패한 항목만 골라내어 원인을 파악하고, 필요하면 해당 작업만 재시도합니다.

응답을 확인하는 흐름을 정리하면 다음과 같습니다.

```
Bulk 응답 처리 흐름

  응답 수신
      |
      v
  errors 필드 확인
      |
  +---+---+
  |       |
  v       v
false    true
  |       |
  v       v
전체     items 배열 순회
성공         |
             v
        각 item의 status 확인
             |
        +----+----+
        |         |
        v         v
     2xx 성공   4xx/5xx 실패
                  |
                  v
            error 필드에서
            원인 파악 후
            재시도 판단
```

대량 작업 중 일부가 실패하는 원인은 여러 가지입니다. 매핑에 맞지 않는 데이터를 보냈거나, 존재하지 않는 인덱스에 create를 시도했거나, 클러스터의 처리 용량이 초과된 경우 등입니다. 클러스터가 과부하 상태일 때 Elasticsearch는 상태 코드 429(TOO_MANY_REQUESTS)를 반환합니다. 이 응답은 "지금은 처리할 수 없으니 나중에 다시 보내라"는 뜻입니다.

429 응답을 받았을 때의 재시도 전략은 **지수 백오프**(exponential backoff)가 일반적입니다. 지수 백오프란 재시도 간격을 점점 늘리는 방식입니다. 첫 번째 재시도는 1초 후, 두 번째는 2초 후, 세 번째는 4초 후처럼 간격을 두 배씩 늘립니다. 실패 직후 곧바로 재시도하면 이미 과부하 상태인 클러스터에 부담을 더하므로, 간격을 두어 클러스터가 회복할 시간을 확보합니다.

```
지수 백오프 재시도 흐름

시도 1 -> 429 응답 -> 1초 대기 -> 시도 2 -> 429 응답 -> 2초 대기 -> 시도 3 -> 200 성공
```

재시도할 때 주의할 점이 있습니다. 전체 요청을 다시 보내는 것이 아니라, 실패한 항목만 모아서 새 Bulk 요청을 구성해야 합니다. 이미 성공한 항목까지 다시 보내면 중복 인덱싱이 발생합니다. index 액션은 덮어쓰기이므로 데이터가 손상되지는 않지만, 불필요한 부하가 생깁니다.

Bulk API의 성능을 좌우하는 핵심 요소 중 하나가 **배치 크기**입니다. 배치 크기란 한 번의 Bulk 요청에 담는 데이터의 양을 말합니다. 배치가 너무 작으면 네트워크 왕복 비용이 여전히 크고, 너무 크면 Elasticsearch 노드의 메모리를 과도하게 점유하거나 타임아웃이 발생합니다.

적절한 배치 크기는 환경마다 다르지만, 일반적인 출발점은 요청 하나당 5MB에서 15MB 사이입니다. 문서 건수로 따지면 대략 1,000건에서 5,000건 정도입니다. 이 범위에서 시작하여 처리 속도와 오류율을 관찰하며 조정합니다. 수십 MB를 넘기는 요청은 메모리 압박과 타임아웃 위험이 높아지므로 피하는 것이 좋습니다.

배치 크기를 조정하는 과정은 다음과 같습니다.

```
배치 크기 최적화 단계

1. 1,000건 (또는 5MB)으로 시작
2. 처리 시간과 오류율 측정
3. 오류 없으면 건수를 늘림 (예: 3,000건)
4. 다시 측정
5. 429 오류나 타임아웃이 나타나면 직전 크기로 복귀
6. 안정적인 지점을 운영 배치 크기로 확정
```

Bulk 인덱싱의 처리량을 더 높이려면, 단일 스레드로 요청을 보내는 것만으로는 Elasticsearch 클러스터의 인덱싱 용량을 모두 활용하기 어렵습니다. 여러 스레드나 프로세스에서 Bulk 요청을 동시에 보내면 클러스터 자원을 더 효율적으로 사용할 수 있습니다. 다만 동시 요청 수를 과도하게 늘리면 CPU와 메모리 사용량이 급증하므로, 429 응답이 나타나지 않는 범위 안에서 조정합니다.

대량 인덱싱을 수행할 때 성능을 추가로 끌어올리는 방법이 있습니다. Elasticsearch는 기본적으로 인덱스를 주기적으로 새로고침(refresh)하여 새로 인덱싱된 문서를 검색 가능한 상태로 만듭니다. 또한 레플리카 샤드에 데이터를 복제합니다. 이 두 가지 작업은 인덱싱 중에 지속적으로 자원을 소모합니다. 대량 적재가 진행되는 동안에는 이를 일시적으로 끄고, 적재가 끝난 뒤에 다시 켜면 인덱싱 속도가 크게 향상됩니다.

```
PUT /my_index/_settings
{
  "index": {
    "refresh_interval": "-1",
    "number_of_replicas": 0
  }
}
```

"refresh_interval"을 "-1"로 설정하면 자동 새로고침을 끕니다. "number_of_replicas"를 0으로 설정하면 레플리카 복제를 중단합니다. 대량 적재가 완료된 후에는 이 값을 원래대로 돌려야 합니다. refresh_interval은 기본값인 "1s"(1초)로, number_of_replicas는 운영 환경에 맞는 값으로 복원합니다. 이 설정을 복원하지 않으면 새로 인덱싱한 문서가 검색에 나타나지 않고, 레플리카가 없어 데이터 안전성이 떨어집니다.

대부분의 프로그래밍 언어에서는 Elasticsearch 클라이언트 라이브러리가 Bulk API를 더 편리하게 사용할 수 있도록 **bulk helper** 함수를 제공합니다. bulk helper는 문서 목록을 받아 NDJSON 형식으로 변환하고, 배치 크기에 맞게 나누어 보내고, 실패한 항목을 자동으로 재시도하는 기능을 갖추고 있습니다. 직접 NDJSON 문자열을 조립하고 재시도 로직을 구현하는 수고를 줄여 줍니다.

Python의 elasticsearch-py 라이브러리는 helpers.bulk() 함수를 제공합니다. 이 함수는 generator나 리스트 같은 iterable을 받아 내부적으로 배치를 나누어 _bulk 엔드포인트로 전송합니다. chunk_size 파라미터로 한 번에 보낼 문서 수를 지정할 수 있습니다.

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

es = Elasticsearch("http://localhost:9200")

actions = [
    {"_index": "products", "_id": str(i), "_source": {"name": f"item_{i}", "price": i * 1000}}
    for i in range(10000)
]

success, errors = bulk(es, actions, chunk_size=1000)
```

actions 리스트에 만 건의 문서를 담았지만, helpers.bulk()가 chunk_size=1000에 따라 1,000건씩 열 번의 Bulk 요청으로 나누어 보냅니다. 반환값의 success는 성공 건수, errors는 실패 항목 목록입니다.

Java의 Elasticsearch Client는 BulkRequest 객체를 사용합니다. 여러 개의 IndexRequest를 add() 메서드로 추가한 뒤, client.bulk()를 호출하여 한 번에 실행합니다.

```java
BulkRequest bulkRequest = new BulkRequest();
for (int i = 0; i < 1000; i++) {
    bulkRequest.add(new IndexRequest("products")
        .id(String.valueOf(i))
        .source("name", "item_" + i, "price", i * 1000));
}
BulkResponse response = client.bulk(bulkRequest, RequestOptions.DEFAULT);
```

BulkResponse의 hasFailures() 메서드로 실패 여부를 확인하고, 실패한 항목만 골라 재시도할 수 있습니다.

JavaScript의 @elastic/elasticsearch 라이브러리는 helpers.bulk() 함수를 제공합니다. 배열이나 readable stream을 데이터 소스로 받아 자동으로 배치를 나누어 전송합니다.

```javascript
const { Client } = require("@elastic/elasticsearch");
const client = new Client({ node: "http://localhost:9200" });

const documents = [
  { name: "item_1", price: 1000 },
  { name: "item_2", price: 2000 },
  // ...
];

const result = await client.helpers.bulk({
  datasource: documents,
  onDocument(doc) {
    return { index: { _index: "products" } };
  },
});
```

datasource에 문서 배열을 넘기고, onDocument 콜백에서 각 문서에 적용할 액션을 반환합니다. 라이브러리가 NDJSON 변환, 배치 분할, 전송을 모두 처리합니다.

세 라이브러리 모두 공통적인 장점을 가집니다. NDJSON 문자열을 직접 조립할 필요가 없고, 재시도와 오류 처리 로직이 내장되어 있으며, 스트리밍 방식으로 동작하여 전체 데이터를 메모리에 올리지 않아도 됩니다.

```
클라이언트 라이브러리 bulk helper 비교

라이브러리                데이터 입력         배치 제어            오류 처리
---------------------------------------------------------------------
Python elasticsearch-py   generator/list     chunk_size 파라미터  (success, errors) 반환
Java Elasticsearch Client BulkRequest.add()  수동 분할 필요       hasFailures() 확인
JavaScript @elastic/es    배열/stream         자동 분할            result 객체 반환
```

정리하면, Bulk API는 여러 건의 인덱싱, 수정, 삭제를 하나의 HTTP 요청에 묶어 처리하는 기능입니다. _bulk 엔드포인트에 NDJSON 형식으로 액션 줄과 소스 줄 쌍을 보내며, index, create, update, delete 네 가지 액션을 지원합니다. 응답의 errors 필드로 실패 여부를 확인하고, items 배열에서 개별 결과를 파싱합니다. 실패한 항목은 지수 백오프 방식으로 재시도합니다. 배치 크기는 5MB에서 15MB 사이에서 시작하여 환경에 맞게 조정합니다.

다음 단원인 3.2.1에서는 Query context vs Filter context를 다룹니다. 검색 요청에서 점수 계산이 필요한 경우와 단순 필터링만 하면 되는 경우를 구분하는 방법을 살펴봅니다.

이 단원을 마치면 Bulk API의 NDJSON 형식을 이해하고 대량 인덱싱을 수행할 수 있으며, Bulk API 응답에서 오류 항목을 식별할 수 있습니다.
