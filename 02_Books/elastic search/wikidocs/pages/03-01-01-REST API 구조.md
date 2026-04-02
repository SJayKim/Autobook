# 3.1.1 REST API 구조

1.1.2에서 Elasticsearch를 설치하고 기동을 확인하는 과정에서, curl 명령으로 클러스터에 요청을 보내고 JSON 응답을 받는 장면을 접했습니다. 그때 사용한 방식이 바로 REST API입니다. Elasticsearch는 데이터를 저장하거나, 검색하거나, 클러스터 상태를 확인하는 등 거의 모든 조작을 이 REST API로 수행합니다. 별도의 드라이버나 특수한 프로토콜 없이, HTTP 요청 하나로 Elasticsearch와 대화할 수 있다는 뜻입니다. 이 단원에서는 REST API의 URL이 어떤 패턴으로 구성되는지, HTTP 메서드마다 어떤 의미를 갖는지, 요청과 응답의 구조를 어떻게 읽는지를 차례로 다룹니다.

REST는 Representational State Transfer의 약자입니다. 웹에서 자원(resource)을 다루기 위한 아키텍처 스타일로, 자원마다 고유한 URL을 부여하고, HTTP 메서드로 해당 자원에 어떤 동작을 할지 표현합니다. 예를 들어 웹 브라우저가 페이지를 불러올 때 사용하는 GET 요청도 REST의 한 형태입니다. Elasticsearch는 이 REST 원칙을 그대로 따르므로, 인덱스나 문서 같은 자원을 URL로 지정하고 HTTP 메서드로 조작합니다.

Elasticsearch REST API의 URL은 일정한 패턴을 따릅니다. 가장 기본적인 형태는 다음과 같습니다.

```
http://localhost:9200/{인덱스}/{엔드포인트}
```

맨 앞의 'http://localhost:9200'은 Elasticsearch가 요청을 수신하는 주소와 포트입니다. 1.1.2에서 설정한 기본 포트가 9200이었던 것을 떠올리면 됩니다. 그 뒤에 오는 경로가 실제로 어떤 자원에 어떤 작업을 할지 결정합니다.

경로의 첫 번째 부분에는 보통 **인덱스 이름**이 옵니다. 인덱스는 Elasticsearch에서 관련 문서를 묶어 두는 논리적 단위입니다. 예를 들어 'favorite_candy'라는 인덱스가 있다면, 이 인덱스에 속한 문서를 다룰 때 URL 경로가 '/favorite_candy'로 시작합니다.

경로의 두 번째 부분에는 **엔드포인트**가 옵니다. 엔드포인트는 수행하려는 작업의 종류를 나타냅니다. '_doc'은 개별 문서를 다루겠다는 뜻이고, '_search'는 검색을 실행하겠다는 뜻입니다. 밑줄('_')로 시작하는 엔드포인트는 Elasticsearch가 예약한 시스템 엔드포인트입니다.

몇 가지 예를 들어 보겠습니다.

```
PUT /favorite_candy/_doc/1        -- favorite_candy 인덱스에 ID가 1인 문서를 저장
GET /favorite_candy/_doc/1        -- favorite_candy 인덱스에서 ID가 1인 문서를 조회
POST /favorite_candy/_search      -- favorite_candy 인덱스에서 검색 실행
DELETE /favorite_candy/_doc/1     -- favorite_candy 인덱스에서 ID가 1인 문서를 삭제
```

인덱스 이름 없이 시작하는 URL도 있습니다. 클러스터 전체에 대한 작업이 그렇습니다. 1.1.2에서 클러스터 상태를 확인할 때 '/_cluster/health'라는 경로를 사용했는데, 이것은 특정 인덱스가 아니라 클러스터 전체를 대상으로 하므로 인덱스 이름이 빠져 있습니다. '_cat/indices', '_cat/nodes' 같은 경로도 마찬가지입니다.

이제 URL의 각 부분을 HTTP 메서드와 연결하여 살펴봅니다. **HTTP 메서드**는 URL이 가리키는 자원에 어떤 동작을 수행할지 지정하는 역할입니다. Elasticsearch에서 주로 사용하는 메서드는 다섯 가지입니다.

**GET**은 자원을 조회합니다. 데이터를 변경하지 않고, 현재 상태를 읽기만 합니다. 문서 한 건을 가져오거나, 검색 결과를 받거나, 클러스터 상태를 확인할 때 사용합니다.

**PUT**은 자원을 지정된 위치에 저장합니다. 인덱스를 새로 만들거나, 특정 ID를 가진 문서를 저장할 때 씁니다. 같은 위치에 이미 자원이 있으면 덮어씁니다.

**POST**는 자원을 생성하거나 처리를 요청합니다. PUT과 달리 ID를 지정하지 않아도 됩니다. 문서를 저장하면서 ID를 자동 생성하거나, 검색 쿼리를 본문에 담아 보낼 때 사용합니다. 부분 업데이트(_update)도 POST로 수행합니다.

**DELETE**는 자원을 삭제합니다. 특정 문서를 지우거나, 인덱스 전체를 제거할 때 사용합니다.

**HEAD**는 GET과 동일하게 동작하지만 응답 본문을 돌려주지 않습니다. 자원이 존재하는지 여부만 확인할 때 사용합니다. 예를 들어 특정 인덱스가 있는지 확인하려면 'HEAD /favorite_candy'를 보내고, 응답 상태 코드가 200이면 존재, 404이면 없음을 뜻합니다.

다음 표는 메서드별 의미를 정리한 것입니다.

```
HTTP 메서드    의미              예시
-----------    -------           ----------------------------
GET            조회 (읽기)       GET /favorite_candy/_doc/1
PUT            저장 (지정 위치)  PUT /favorite_candy/_doc/1
POST           생성/처리 요청    POST /favorite_candy/_doc
DELETE         삭제              DELETE /favorite_candy/_doc/1
HEAD           존재 확인         HEAD /favorite_candy
```

URL과 메서드만으로는 요청이 완성되지 않는 경우가 있습니다. 문서를 저장하거나 검색 조건을 전달할 때처럼, 서버에 데이터를 함께 보내야 하는 상황입니다. 이때 사용하는 것이 **요청 바디**(request body)입니다. Elasticsearch의 요청 바디는 JSON 형식을 사용합니다.

JSON은 키-값 쌍으로 데이터를 표현하는 텍스트 형식입니다. 중괄호({})로 감싸고, 키와 값을 콜론(:)으로 연결합니다. 예를 들어 문서를 저장하는 요청은 다음과 같습니다.

```
PUT /favorite_candy/_doc/1
{
  "first_name": "John",
  "candy": "Starburst"
}
```

첫 줄은 HTTP 메서드(PUT)와 URL 경로입니다. 그 아래 중괄호로 감싼 부분이 요청 바디입니다. "first_name"과 "candy"가 필드 이름이고, "John"과 "Starburst"가 각 필드의 값입니다. Elasticsearch는 이 JSON을 파싱하여 인덱스에 문서로 저장합니다.

검색 요청도 같은 원리입니다. 검색 조건을 JSON 바디에 담아 보냅니다.

```
POST /favorite_candy/_search
{
  "query": {
    "match": {
      "first_name": "John"
    }
  }
}
```

"query" 키 아래에 검색 조건이 중첩된 구조입니다. "match"는 특정 필드에서 값을 찾겠다는 뜻입니다. 이처럼 Elasticsearch의 요청 바디는 JSON 객체가 여러 겹 중첩되는 경우가 많습니다. 바깥 중괄호가 요청 전체를 감싸고, 안쪽 중괄호가 세부 조건을 표현합니다.

요청 바디에 JSON을 담아 보낼 때는 서버에 "이 데이터가 JSON 형식이다"라는 사실을 알려주어야 합니다. 이 역할을 하는 것이 **Content-Type 헤더**입니다. HTTP 요청에는 헤더(header)라는 메타 정보를 함께 실을 수 있는데, Content-Type 헤더는 요청 바디의 데이터 형식을 명시합니다. Elasticsearch에 JSON 바디를 보낼 때는 반드시 다음 헤더를 포함해야 합니다.

```
Content-Type: application/json
```

이 헤더가 없으면 Elasticsearch가 바디를 올바르게 해석하지 못하고 오류를 반환할 수 있습니다. curl 명령으로 요청을 보낼 때는 '-H' 옵션으로 이 헤더를 지정합니다.

```bash
curl -X PUT "http://localhost:9200/favorite_candy/_doc/1" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "candy": "Starburst"
  }'
```

'-X PUT'은 HTTP 메서드를 PUT으로 지정합니다. '-H "Content-Type: application/json"'은 앞서 설명한 헤더를 추가합니다. '-d'는 요청 바디를 직접 문자열로 전달하는 옵션입니다. 작은따옴표 안에 JSON을 넣습니다.

1.1.2에서 기동 확인에 사용한 curl 명령을 다시 떠올려 봅니다. 그때는 'curl --cacert ... -u elastic:$ELASTIC_PASSWORD https://localhost:9200'처럼 보안 옵션이 포함되어 있었습니다. 보안을 비활성화한 개발 환경에서는 이 옵션들을 생략하고 'http://localhost:9200'으로 바로 접근합니다. 핵심 구조는 동일합니다. 'curl -X {메서드} "{URL}" -H "Content-Type: application/json" -d '{JSON 바디}'' 형태가 Elasticsearch에 요청을 보내는 curl의 기본 틀입니다.

요청을 보냈으면 응답을 읽을 차례입니다. Elasticsearch의 응답에서 가장 먼저 확인해야 할 것은 **HTTP 상태 코드**입니다. 상태 코드는 세 자리 숫자로, 요청이 어떻게 처리되었는지를 알려줍니다.

**200 OK**는 요청이 정상 처리되었다는 뜻입니다. 문서 조회, 검색, 삭제가 성공했을 때 돌아옵니다.

**201 Created**는 새 자원이 생성되었다는 뜻입니다. POST로 문서를 만들면 이 코드가 돌아옵니다.

**404 Not Found**는 요청한 자원이 존재하지 않는다는 뜻입니다. 없는 문서를 조회하거나, 없는 인덱스에 접근하면 이 코드가 돌아옵니다.

**409 Conflict**는 요청이 기존 자원과 충돌했다는 뜻입니다. _create 엔드포인트로 이미 존재하는 ID에 문서를 저장하려 하면 이 코드가 돌아옵니다.

**400 Bad Request**는 요청 형식에 문제가 있다는 뜻입니다. JSON 문법이 잘못되었거나, 필수 파라미터가 빠졌을 때 발생합니다.

**500 Internal Server Error**는 서버 내부에서 오류가 발생했다는 뜻입니다. 디스크 공간 부족이나 메모리 부족 같은 서버 측 문제를 나타냅니다.

상태 코드 뒤에는 JSON 형태의 응답 본문이 따라옵니다. 예를 들어 문서를 조회하면 다음과 같은 응답이 돌아옵니다.

```json
{
  "_index": "favorite_candy",
  "_id": "1",
  "_version": 1,
  "found": true,
  "_source": {
    "first_name": "John",
    "candy": "Starburst"
  }
}
```

"_index"는 문서가 속한 인덱스 이름입니다. "_id"는 문서의 고유 식별자입니다. "_version"은 이 문서가 몇 번째 변경인지를 나타내는 숫자로, 생성 시 1에서 시작하여 수정이나 삭제 때마다 증가합니다. "found"는 문서가 실제로 존재하는지 여부입니다. "_source"는 저장된 원본 데이터가 담긴 부분입니다. 밑줄로 시작하는 필드는 Elasticsearch가 자동으로 붙이는 메타데이터이고, "_source" 안에 사용자가 저장한 실제 데이터가 들어갑니다.

그런데 터미널에서 JSON 응답을 그대로 받으면, 한 줄에 모든 내용이 이어 붙어 읽기 어렵습니다. 이때 URL 끝에 **pretty 파라미터**를 붙이면 들여쓰기가 적용된 보기 좋은 JSON을 돌려줍니다.

```
GET /favorite_candy/_doc/1?pretty
```

'?pretty'를 붙이지 않으면 '{"_index":"favorite_candy","_id":"1",...}'처럼 한 줄로 나옵니다. '?pretty'를 붙이면 앞서 본 것처럼 줄바꿈과 들여쓰기가 적용됩니다. curl로 요청할 때도 URL 끝에 '?pretty'를 추가하면 됩니다. cat API에서 사용하는 '?v' 파라미터와 비슷한 역할이지만, '?v'는 표 형식 출력에 헤더 행을 추가하는 것이고, '?pretty'는 JSON 출력을 정렬하는 것입니다.

지금까지 curl을 사용하여 요청을 보내는 방법을 살펴보았습니다. curl은 범용적이지만, 매번 메서드, 헤더, 바디를 직접 타이핑해야 하므로 반복 작업이 번거롭습니다. Elasticsearch에는 이 과정을 간소화하는 도구가 내장되어 있습니다. 바로 **Kibana Dev Tools Console**입니다.

Kibana Dev Tools Console은 Kibana 안에 내장된 API 실행 도구입니다. 1.1.2에서 Kibana를 설치하고 'http://localhost:5601'에 접속하는 방법을 다루었습니다. Kibana에 로그인한 뒤, 왼쪽 메뉴에서 'Dev Tools'(또는 '개발 도구')를 선택하면 Console 화면이 열립니다. 화면은 왼쪽 입력 영역과 오른쪽 출력 영역으로 나뉩니다.

Console의 가장 큰 장점은 curl에서 필요했던 부수적인 요소를 생략할 수 있다는 것입니다. 호스트 주소, Content-Type 헤더, 따옴표 이스케이프 같은 것을 신경 쓰지 않아도 됩니다. Console에서는 HTTP 메서드와 경로, 그리고 바디만 입력합니다.

```
PUT /favorite_candy/_doc/1
{
  "first_name": "John",
  "candy": "Starburst"
}
```

이것이 Console에 입력하는 전부입니다. curl이었다면 'curl -X PUT "http://localhost:9200/favorite_candy/_doc/1" -H "Content-Type: application/json" -d '...''처럼 길어졌을 내용이, Console에서는 메서드와 경로 한 줄, 바디 몇 줄로 끝납니다.

요청을 입력한 뒤 초록색 삼각형 버튼(실행 버튼)을 클릭하거나, 단축키 Ctrl+Enter(macOS에서는 Cmd+Enter)를 누르면 요청이 Elasticsearch로 전송됩니다. 오른쪽 영역에 응답 상태 코드와 JSON 본문이 표시됩니다. 응답은 자동으로 정렬되어 나오므로 '?pretty'를 붙일 필요도 없습니다.

Console에서는 여러 요청을 위아래로 나열해 둘 수 있습니다. 커서가 위치한 요청만 실행되므로, 자주 쓰는 요청을 모아 두고 필요할 때 골라 실행하는 식으로 활용할 수 있습니다. 자동 완성 기능도 있어서, 엔드포인트 이름이나 필드 이름을 일부만 입력해도 후보가 표시됩니다.

다음은 curl과 Kibana Dev Tools Console에서 같은 요청을 보내는 모습을 비교한 것입니다.

```
curl 방식:
curl -X GET "http://localhost:9200/favorite_candy/_doc/1?pretty" \
  -H "Content-Type: application/json"

Kibana Dev Tools Console 방식:
GET /favorite_candy/_doc/1
```

curl 방식은 호스트 주소, '?pretty', Content-Type 헤더를 모두 직접 지정해야 합니다. Console 방식은 메서드와 경로만으로 충분합니다. 학습 단계에서는 Console이 훨씬 간편하므로, 이후 단원에서 API 예시를 보여줄 때도 Console 형식을 기본으로 사용합니다.

아래 다이어그램은 요청이 전달되는 전체 흐름을 정리한 것입니다.

```
요청 흐름

사용자 입력                       Elasticsearch 처리
-----------                       ------------------

[curl / Dev Tools Console]
        |
        v
  HTTP 요청 구성
  +---------------------------+
  | 메서드: PUT               |
  | 경로: /favorite_candy     |
  |        /_doc/1            |
  | 헤더: Content-Type:       |
  |   application/json        |
  | 바디: { "first_name":     |
  |   "John", ... }           |
  +---------------------------+
        |
        v
  localhost:9200 수신
        |
        v
  +---------------------------+
  | 1. URL 경로 파싱          |
  |    -> 인덱스: favorite_   |
  |       candy               |
  |    -> 엔드포인트: _doc/1  |
  | 2. 메서드 확인 -> PUT     |
  |    -> 문서 저장 작업      |
  | 3. JSON 바디 파싱         |
  | 4. 인덱스에 문서 기록     |
  +---------------------------+
        |
        v
  HTTP 응답 반환
  +---------------------------+
  | 상태: 201 Created         |
  | 바디: { "_index":         |
  |   "favorite_candy",       |
  |   "_id": "1",             |
  |   "_version": 1,          |
  |   "result": "created" }   |
  +---------------------------+
```

사용자가 curl이나 Dev Tools Console에서 요청을 보내면, HTTP 요청이 localhost:9200으로 전달됩니다. Elasticsearch는 URL 경로에서 인덱스 이름과 엔드포인트를 파싱하고, HTTP 메서드로 수행할 작업을 결정합니다. JSON 바디가 있으면 파싱하여 작업에 반영하고, 처리 결과를 상태 코드와 JSON 응답으로 돌려줍니다.

정리하면, Elasticsearch REST API는 '/{인덱스}/{엔드포인트}' 형태의 URL과 HTTP 메서드(GET, PUT, POST, DELETE, HEAD)를 조합하여 모든 작업을 수행합니다. 요청 바디는 JSON으로 작성하며 Content-Type: application/json 헤더가 필요합니다. 응답의 상태 코드(200, 201, 404, 409 등)로 처리 결과를 판별하고, '?pretty' 파라미터로 JSON 출력을 읽기 쉽게 정렬할 수 있습니다. curl로 직접 요청을 보낼 수도 있지만, Kibana Dev Tools Console을 사용하면 호스트 주소와 헤더를 생략하고 메서드와 경로만으로 간편하게 실행할 수 있습니다.

다음 단원인 3.1.2에서는 문서 CRUD를 다룹니다.

이 단원을 마치면 Elasticsearch REST API의 URL 패턴과 HTTP 메서드 의미를 설명할 수 있고, Kibana Dev Tools Console로 API를 실행할 수 있습니다.
