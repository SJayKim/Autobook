# 3.3.1 multi_match와 cross-field 검색

3.2.2에서 match 쿼리가 하나의 필드에서 검색어를 분석기에 통과시킨 뒤 토큰 단위로 매칭하는 과정을 살펴보았습니다. match 쿼리는 검색 대상 필드를 하나만 지정합니다. 그런데 실제 서비스에서는 하나의 검색어로 여러 필드를 동시에 조회해야 하는 상황이 자주 발생합니다. 예를 들어 상품 검색에서 사용자가 "무선 키보드"를 입력하면, 상품명(title) 필드뿐 아니라 설명(description) 필드와 카테고리(category) 필드까지 함께 살펴보아야 원하는 상품을 빠짐없이 찾을 수 있습니다. 이때 match 쿼리를 필드마다 따로 작성하고 bool 쿼리로 감싸는 방법도 있지만, Elasticsearch는 이 패턴을 간결하게 표현하는 전용 쿼리를 제공합니다. 그것이 **multi_match 쿼리**입니다.

multi_match 쿼리는 하나의 검색어를 여러 필드에 동시에 전달하여 검색하는 쿼리입니다. 내부적으로는 지정된 각 필드에 match 쿼리(또는 그 변형)를 실행하고, 필드별 점수를 조합하여 최종 관련성 점수를 산출합니다. 기본 형태를 살펴봅니다.

```json
{
  "query": {
    "multi_match": {
      "query": "무선 키보드",
      "fields": ["title", "description", "category"]
    }
  }
}
```

"multi_match" 안에 "query"로 검색어를, "fields"로 검색할 필드 목록을 배열로 지정합니다. 이 쿼리는 "무선 키보드"를 title, description, category 세 필드에서 각각 검색합니다. 각 필드의 분석기가 검색어를 토큰화하고, 토큰 단위로 역색인을 조회하는 과정은 3.2.2에서 다룬 match 쿼리와 동일합니다. 차이는 한 번의 쿼리로 여러 필드를 동시에 대상으로 한다는 점입니다.

multi_match 쿼리에서 핵심적인 설정이 **type** 파라미터입니다. type은 여러 필드의 점수를 어떻게 조합할지를 결정합니다. type에 따라 multi_match 쿼리의 동작 방식이 근본적으로 달라지므로, 각 type의 특성을 이해하는 것이 multi_match를 올바르게 사용하는 열쇠입니다. type을 별도로 지정하지 않으면 기본값인 best_fields가 적용됩니다.

multi_match 쿼리가 지원하는 type은 다섯 가지입니다. best_fields, most_fields, cross_fields, phrase, phrase_prefix입니다. 각 type이 어떤 상황에서 적합한지 하나씩 살펴봅니다.

**best_fields**는 multi_match 쿼리의 기본 type입니다. 이 type은 각 필드에 match 쿼리를 실행한 뒤, 가장 높은 점수를 받은 필드 하나의 점수를 최종 점수로 사용합니다. "여러 필드 중 가장 잘 맞는 필드의 점수를 대표로 삼는다"는 뜻입니다.

구체적인 시나리오로 설명합니다. 블로그 검색 서비스에서 "Elasticsearch 성능 튜닝"이라는 검색어를 title과 body 두 필드에서 검색한다고 가정합니다. 어떤 문서의 title이 "Elasticsearch 성능 튜닝 가이드"이고, body에는 "Elasticsearch"라는 단어가 한 번 언급되어 있습니다. title 필드에서의 점수가 8.5, body 필드에서의 점수가 2.1이라면, best_fields type은 더 높은 8.5를 최종 점수로 채택합니다. 검색어와 가장 관련도가 높은 필드 하나가 문서의 대표 점수를 결정하는 것입니다.

best_fields type은 검색어 전체가 하나의 필드에 집중적으로 나타날 때 적합합니다. 제목에 핵심 키워드가 몰려 있는 문서, 상품명에 검색어가 정확히 들어 있는 상품 등이 이에 해당합니다.

best_fields의 동작을 이해했다면, 한 가지 의문이 생깁니다. 가장 높은 점수만 사용하면 나머지 필드의 점수는 완전히 무시되는 것일까요. 여기서 **tie_breaker** 파라미터가 등장합니다. tie_breaker는 0.0에서 1.0 사이의 값을 받으며, 기본값은 0.0입니다. 최종 점수 계산 방식은 다음과 같습니다.

```
최종 점수 = (가장 높은 필드 점수) + tie_breaker * (나머지 필드 점수들의 합)
```

tie_breaker가 기본값 0.0이면 나머지 필드의 점수가 전혀 반영되지 않습니다. 앞선 예시에서 title 점수 8.5, body 점수 2.1일 때, tie_breaker가 0.0이면 최종 점수는 8.5입니다. tie_breaker를 0.3으로 설정하면 최종 점수는 8.5 + 0.3 * 2.1 = 9.13이 됩니다.

```json
{
  "query": {
    "multi_match": {
      "query": "Elasticsearch 성능 튜닝",
      "fields": ["title", "body"],
      "type": "best_fields",
      "tie_breaker": 0.3
    }
  }
}
```

이 설정에서 "type"을 "best_fields"로, "tie_breaker"를 0.3으로 지정합니다. tie_breaker를 0.0보다 크게 설정하면, 여러 필드에서 고르게 매칭되는 문서가 한 필드에서만 매칭되는 문서보다 약간 더 높은 점수를 받습니다. 검색어가 여러 필드에 걸쳐 나타나는 것을 보너스로 반영하되, 가장 잘 맞는 필드의 점수가 주도권을 유지하도록 하는 균형 장치입니다. tie_breaker를 1.0으로 설정하면 모든 필드의 점수를 동등하게 합산하게 되어, 사실상 most_fields type과 같은 동작이 됩니다. 즉 tie_breaker는 best_fields(최고 점수 필드만 사용)와 most_fields(모든 필드 점수 합산) 사이의 균형을 조절하는 파라미터입니다. 실무에서는 0.3 전후의 값을 시작점으로 삼아, 검색 결과를 확인하면서 값을 조정하는 방식이 일반적입니다.

다음은 **most_fields** type입니다. most_fields는 best_fields와 반대되는 접근입니다. 각 필드에 match 쿼리를 실행하는 것까지는 같지만, 최종 점수 계산 방식이 다릅니다. most_fields는 모든 필드의 점수를 합산합니다. 가장 높은 점수 하나만 취하는 best_fields와 달리, 더 많은 필드에서 매칭될수록 점수가 높아집니다.

most_fields가 적합한 상황을 구체적으로 살펴봅니다. 동일한 텍스트를 서로 다른 분석기로 분석하여 여러 필드에 저장하는 경우가 있습니다. 예를 들어 영문 상품명을 title 필드에는 standard 분석기로, title.english 필드에는 english 분석기로 저장합니다. english 분석기는 어간 추출(stemming)을 수행하므로 "running"을 "run"으로 변환합니다. "running shoes"를 검색하면 title 필드에서는 "running"이 정확히 매칭되고, title.english 필드에서는 "run"으로 어간이 일치하는 문서도 매칭됩니다. most_fields type은 두 필드의 점수를 합산하므로, 정확한 형태와 어간 모두에서 매칭되는 문서가 더 높은 점수를 받습니다.

```json
{
  "query": {
    "multi_match": {
      "query": "running shoes",
      "fields": ["title", "title.english"],
      "type": "most_fields"
    }
  }
}
```

이 쿼리에서 "type"을 "most_fields"로 지정합니다. title과 title.english 두 필드에서 매칭되는 점수가 합산되어 최종 점수가 됩니다.

이제 multi_match의 type 중에서 가장 독특한 동작을 하는 **cross_fields** type을 살펴봅니다. best_fields와 most_fields는 각 필드에 독립적으로 match 쿼리를 실행한 뒤 점수를 조합합니다. 반면 cross_fields는 여러 필드를 마치 하나의 커다란 필드처럼 취급합니다.

cross_fields가 왜 필요한지, 구체적인 시나리오로 설명합니다. 인물 정보를 저장하는 인덱스에 first_name 필드와 last_name 필드가 있다고 가정합니다. 사용자가 "홍 길동"을 검색합니다. 이 검색어를 분석기에 통과시키면 "홍"과 "길동" 두 토큰이 만들어집니다.

best_fields type으로 검색하면 어떻게 될까요. first_name 필드에서 "홍"과 "길동"을 찾고, last_name 필드에서도 "홍"과 "길동"을 찾습니다. 그런데 first_name에는 "길동"만 있고 last_name에는 "홍"만 있습니다. 각 필드에서는 검색 토큰 두 개 중 하나만 매칭되므로, 기대보다 낮은 점수가 나옵니다. 검색어의 토큰들이 서로 다른 필드에 분산되어 있기 때문입니다.

cross_fields type은 이 문제를 해결합니다. 이 type은 토큰별로 "이 토큰이 지정된 필드 중 어디에라도 존재하는지"를 확인합니다. "홍"이라는 토큰은 last_name에 있고, "길동"이라는 토큰은 first_name에 있습니다. 두 토큰 모두 필드 어딘가에 존재하므로 높은 점수를 받습니다.

이 과정을 단계별로 정리하면 다음과 같습니다.

```
cross_fields 동작 흐름 (검색어: "홍 길동")

1. 검색어를 분석기에 통과 --> 토큰: ["홍", "길동"]
2. 토큰 "홍"을 모든 대상 필드에서 탐색
   - first_name: 없음
   - last_name:  있음 (점수 3.2)
   --> "홍" 토큰의 대표 점수 = 3.2 (가장 높은 점수)
3. 토큰 "길동"을 모든 대상 필드에서 탐색
   - first_name: 있음 (점수 4.1)
   - last_name:  없음
   --> "길동" 토큰의 대표 점수 = 4.1
4. 모든 토큰의 대표 점수를 조합 --> 최종 점수
```

best_fields가 "필드 단위"로 점수를 매긴 뒤 필드 간 비교를 하는 반면, cross_fields는 "토큰 단위"로 필드를 횡단합니다. 여러 필드에 흩어져 있는 정보를 하나의 논리적 필드로 묶어 검색하는 셈입니다.

```json
{
  "query": {
    "multi_match": {
      "query": "홍 길동",
      "fields": ["first_name", "last_name"],
      "type": "cross_fields"
    }
  }
}
```

cross_fields는 이름 외에도 주소(시, 구, 동이 별도 필드), 상품 사양(브랜드, 모델명, 부제목이 별도 필드) 등 하나의 개념이 여러 필드에 나뉘어 저장된 경우에 적합합니다. 주의할 점은 cross_fields type을 사용하려면 대상 필드들이 동일한 분석기를 사용해야 한다는 것입니다. 분석기가 다르면 같은 검색어에서 서로 다른 토큰이 생성되어 필드 횡단 비교가 성립하지 않기 때문입니다.

**phrase** type은 각 필드에 match 쿼리 대신 match_phrase 쿼리를 실행합니다. 3.2.2에서 살펴본 match_phrase 쿼리는 토큰의 순서와 인접성을 보장하는 구문 검색을 수행합니다. phrase type의 multi_match는 이 구문 검색을 여러 필드에 동시에 적용합니다. 점수 조합 방식은 best_fields와 동일하여, 가장 높은 점수를 받은 필드 하나의 점수가 최종 점수가 됩니다. 정확한 구문 일치가 필요한 상황, 예를 들어 "machine learning"이라는 표현이 반드시 이 어순 그대로 포함된 문서를 여러 필드에서 찾아야 할 때 phrase type을 사용합니다. 단어가 흩어져 나타나는 문서는 제외하고, 구문이 정확히 연속으로 등장하는 문서만 결과에 포함한다는 점에서 best_fields와 구별됩니다.

```json
{
  "query": {
    "multi_match": {
      "query": "quick brown fox",
      "fields": ["title", "body"],
      "type": "phrase"
    }
  }
}
```

이 쿼리는 title과 body 필드 각각에서 "quick brown fox"가 정확히 그 순서대로 연속으로 나타나는 문서를 찾습니다. 어느 필드에서든 구문이 매칭되면 결과에 포함되고, 더 높은 점수를 받은 필드의 점수가 최종 점수가 됩니다.

**phrase_prefix** type은 각 필드에 match_phrase_prefix 쿼리를 실행합니다. 3.2.2에서 다룬 match_phrase_prefix는 마지막 토큰을 접두사로 취급하여 자동 완성에 활용하는 쿼리입니다. phrase_prefix type의 multi_match는 이 자동 완성 검색을 여러 필드에 동시에 적용합니다. 마지막 토큰을 접두어로 처리하기 때문에, 사용자가 검색어를 입력하는 도중에도 실시간으로 후보 문서를 보여줄 수 있습니다. 이때 max_expansions 파라미터로 접두어에서 확장할 후보 토큰 수를 제한할 수 있습니다. 기본값은 50이며, 값을 낮추면 성능이 개선되지만 매칭 범위가 좁아집니다.

```json
{
  "query": {
    "multi_match": {
      "query": "quick bro",
      "fields": ["title", "body"],
      "type": "phrase_prefix",
      "max_expansions": 10
    }
  }
}
```

이 쿼리는 title과 body 필드에서 "quick"을 정확히 매칭하고, 마지막 토큰 "bro"는 접두사로 취급합니다. "quick brown", "quick broken" 등이 매칭됩니다. "max_expansions"를 10으로 설정했으므로, "bro"로 시작하는 토큰 중 최대 10개까지만 확장 후보로 사용합니다. 자동완성 기능에서 응답 속도가 중요할 때 이 값을 낮게 설정하면 불필요한 후보 확장을 줄여 성능을 확보할 수 있습니다.

다섯 가지 type의 차이를 정리합니다.

```
multi_match type별 비교

type           | 필드별 실행 쿼리       | 점수 조합 방식          | 적합한 상황
---------------|----------------------|----------------------|---------------------------
best_fields    | match                | 최고 점수 필드 대표     | 핵심 키워드가 한 필드에 집중
most_fields    | match                | 모든 필드 점수 합산     | 같은 텍스트를 다른 분석기로 저장
cross_fields   | (토큰별 필드 횡단)     | 토큰별 최고 점수 조합   | 하나의 개념이 여러 필드에 분산
phrase         | match_phrase         | 최고 점수 필드 대표     | 구문 순서가 중요한 다중 필드 검색
phrase_prefix  | match_phrase_prefix  | 최고 점수 필드 대표     | 여러 필드 대상 자동 완성
```

multi_match 쿼리에는 type과 tie_breaker 외에도 유용한 설정이 있습니다. 필드마다 중요도가 다를 때 **필드별 boost**를 지정할 수 있습니다. 필드 이름 뒤에 캐럿 기호(^)와 숫자를 붙이면, 해당 필드의 점수에 그 숫자만큼 가중치가 곱해집니다.

```json
{
  "query": {
    "multi_match": {
      "query": "full text search",
      "fields": ["title^3", "body", "summary^2"]
    }
  }
}
```

이 쿼리에서 "title^3"은 title 필드의 점수에 3을 곱하고, "summary^2"는 summary 필드의 점수에 2를 곱합니다. 가중치를 지정하지 않은 body 필드는 기본 가중치 1이 적용됩니다. title에서 매칭된 문서가 body에서만 매칭된 문서보다 3배 높은 점수를 받게 됩니다. 상품 검색에서 상품명 매칭을 상세 설명 매칭보다 중시하거나, 뉴스 검색에서 헤드라인 매칭을 본문 매칭보다 우선하는 등의 상황에서 활용합니다.

boost 값은 소수도 가능합니다. "title^1.5"처럼 지정하면 1.5배 가중치가 적용됩니다. boost 값은 절대적인 점수가 아니라 필드 간 상대적 중요도를 나타내므로, 값 자체보다 필드 간 비율이 중요합니다. "title^3", "body^1"과 "title^6", "body^2"는 비율이 동일하므로 결과 순위에 같은 영향을 줍니다.

multi_match 쿼리로 검색할 필드 수가 많아지면 성능에 영향을 줄 수 있습니다. 각 필드에 개별적으로 쿼리를 실행하고 점수를 계산해야 하기 때문입니다. 이런 경우 인덱싱 시점에 여러 필드의 값을 하나의 필드로 합치는 copy_to 설정을 활용하면, 하나의 필드에 match 쿼리를 실행하는 것으로 대체할 수 있어 성능이 개선됩니다.

정리하면, multi_match 쿼리는 하나의 검색어를 여러 필드에 동시에 전달하여 검색하는 쿼리입니다. type 파라미터로 점수 조합 방식을 결정하며, 기본값인 best_fields는 가장 높은 점수의 필드를 대표로 삼고, most_fields는 모든 필드의 점수를 합산하며, cross_fields는 토큰 단위로 필드를 횡단하여 여러 필드에 분산된 키워드를 효과적으로 검색합니다. tie_breaker 파라미터로 best_fields의 점수 조합을 미세 조정할 수 있고, 캐럿 기호(^)로 필드별 가중치를 설정하여 중요한 필드의 매칭을 우선할 수 있습니다.

다음 단원인 3.3.2에서는 자동완성 구현을 다룹니다.

이 단원을 마치면 multi_match 쿼리의 type 옵션을 비교하여 적합한 방식을 선택할 수 있고, cross_fields 타입으로 여러 필드에 분산된 키워드를 효과적으로 검색할 수 있습니다.

