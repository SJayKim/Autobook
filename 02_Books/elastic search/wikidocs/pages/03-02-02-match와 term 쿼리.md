# 3.2.2 match와 term 쿼리

3.2.1에서 Elasticsearch가 쿼리를 실행할 때 query context와 filter context를 구분한다는 것을 살펴보았습니다. query context에서는 문서와 검색 조건의 관련성 점수를 계산하고, filter context에서는 조건 충족 여부만 판단합니다. 이 구분을 이해했다면 자연스럽게 다음 질문이 떠오릅니다. query context에서 실제로 어떤 쿼리를 사용하고, filter context에서는 어떤 쿼리를 사용해야 할까요. Elasticsearch에는 수십 가지 쿼리가 있지만, 가장 기본이 되는 두 가지가 있습니다. 하나는 분석기를 거쳐 전문 검색을 수행하는 match 쿼리이고, 다른 하나는 분석기를 거치지 않고 정확히 일치하는 값을 찾는 term 쿼리입니다.

이 두 쿼리의 차이를 이해하려면, 먼저 2.3.1에서 다룬 분석기의 역할을 떠올릴 필요가 있습니다. 분석기는 텍스트를 토큰으로 분리하고, 소문자 변환이나 불용어 제거 같은 가공을 수행하는 파이프라인입니다. 문서가 인덱싱될 때 text 타입 필드의 값은 분석기를 거쳐 토큰 형태로 역색인에 저장됩니다. 예를 들어 "Quick Brown Foxes!"라는 원문은 standard 분석기를 거치면 "quick", "brown", "foxes"라는 소문자 토큰으로 변환됩니다. 역색인에는 이 토큰들이 저장되고, 원문 그대로가 저장되는 것이 아닙니다. 이 사실이 match 쿼리와 term 쿼리의 차이를 이해하는 열쇠입니다.

**match 쿼리**는 검색어를 분석기에 통과시킨 뒤 검색하는 쿼리입니다. 사용자가 입력한 검색어를 먼저 해당 필드의 분석기로 토큰화하고, 만들어진 토큰들로 역색인을 조회합니다. 예를 들어 title 필드에서 "quick brown fox"를 match 쿼리로 검색하면, Elasticsearch는 이 검색어를 분석기에 넣어 "quick", "brown", "fox"라는 토큰을 만듭니다. 그런 다음 역색인에서 이 토큰 중 하나라도 포함하는 문서를 찾습니다.

match 쿼리의 기본 형태를 살펴봅니다.

```json
GET my_index/_search
{
  "query": {
    "match": {
      "title": "quick brown fox"
    }
  }
}
```

이 요청에서 "query" 안에 "match"를 지정하고, 검색할 필드 이름("title")에 검색어("quick brown fox")를 값으로 넣습니다. Elasticsearch는 이 검색어를 title 필드에 설정된 분석기로 토큰화합니다. standard 분석기가 적용된다면 "quick", "brown", "fox" 세 토큰이 만들어집니다. 기본적으로 이 세 토큰 중 하나라도 역색인에 존재하는 문서가 결과에 포함됩니다. "quick"만 있는 문서도, "brown fox"만 있는 문서도, 세 단어가 모두 있는 문서도 결과에 나옵니다.

match 쿼리가 내부적으로 수행하는 단계를 정리하면 다음과 같습니다.

```
match 쿼리 실행 흐름

1. 검색어 "quick brown fox"를 필드의 분석기에 전달
2. 분석기가 토큰화 및 정규화 수행 --> ["quick", "brown", "fox"]
3. 토큰들로 boolean 쿼리 구성 (기본: OR 조합)
4. 역색인에서 각 토큰이 포함된 문서 조회
5. BM25 알고리즘으로 각 문서의 관련성 점수 계산
6. 점수순으로 정렬하여 반환
```

3단계에서 "boolean 쿼리를 구성한다"는 점에 주목합니다. match 쿼리는 토큰화된 결과를 내부적으로 boolean 쿼리로 변환하여 실행합니다. 기본 동작은 토큰들을 OR로 연결하는 것입니다. "quick OR brown OR fox"에 해당하므로, 세 토큰 중 하나만 포함해도 결과에 들어옵니다.

이 기본 동작을 바꾸고 싶을 때 **operator** 파라미터를 사용합니다. operator를 "and"로 설정하면, 모든 토큰이 문서에 존재해야 결과에 포함됩니다.

```json
{
  "query": {
    "match": {
      "title": {
        "query": "quick brown fox",
        "operator": "and"
      }
    }
  }
}
```

이 쿼리에서 "query" 필드에 검색어를, "operator" 필드에 "and"를 지정합니다. 검색어가 단순 문자열이 아니라 객체 형태로 바뀐 점에 주의합니다. 이 설정으로 Elasticsearch는 "quick AND brown AND fox"로 검색합니다. 세 토큰이 모두 포함된 문서만 결과에 나옵니다. operator의 기본값은 "or"이므로, 별도 지정이 없으면 하나의 토큰만 매칭되어도 결과에 포함됩니다.

operator가 기본값 "or"일 때 토큰 하나만 일치해도 결과에 포함되므로, 검색 결과가 지나치게 많아질 수 있습니다. 반대로 "and"를 사용하면 모든 토큰이 일치해야 하므로 결과가 너무 적어질 수 있습니다. 이 사이에서 균형을 잡아 주는 것이 **minimum_should_match** 파라미터입니다. 이 파라미터는 토큰 중 최소 몇 개가 매칭되어야 결과에 포함할지를 지정합니다.

예를 들어 "무선 블루투스 키보드"를 match 쿼리로 검색하면 분석기가 "무선", "블루투스", "키보드" 세 토큰을 만듭니다. 기본 동작(operator: "or")에서는 "키보드"만 포함하는 문서도 결과에 나옵니다. 세 토큰 중 최소 두 개는 매칭되어야 유의미한 결과라고 판단한다면, minimum_should_match를 2로 설정합니다.

```json
{
  "query": {
    "match": {
      "title": {
        "query": "무선 블루투스 키보드",
        "minimum_should_match": 2
      }
    }
  }
}
```

이 쿼리는 "무선", "블루투스", "키보드" 중 두 개 이상의 토큰이 포함된 문서만 반환합니다. "무선 키보드"나 "블루투스 키보드"는 결과에 포함되지만, "키보드" 하나만 있는 문서는 제외됩니다.

minimum_should_match에는 정수와 백분율 두 가지 형식을 사용할 수 있습니다. 정수는 매칭해야 할 토큰의 절대 개수이고, 백분율은 전체 토큰 수 대비 비율입니다. 위 예시에서 "75%"로 지정하면 토큰 3개의 75%인 2.25를 내림하여 2개 이상 매칭을 요구합니다. 토큰 수가 적은 짧은 검색어에는 1이나 2 같은 정수가 직관적이고, 토큰 수가 많은 긴 검색어에는 "75%" 같은 백분율이 실무적으로 적합합니다.

사용자가 오타를 내는 경우에도 검색이 되도록 하려면 **fuzziness** 파라미터를 사용합니다. fuzziness는 검색어 토큰과 역색인 토큰 사이에 허용할 편집 거리(edit distance)를 지정합니다. 편집 거리란 한 문자열을 다른 문자열로 바꾸기 위해 필요한 문자 단위 변경(삽입, 삭제, 치환, 인접 문자 교환) 횟수입니다. 예를 들어 "quikc"를 "quick"으로 바꾸려면 "k"와 "c"의 위치를 교환하면 되므로 편집 거리는 1입니다.

```json
{
  "query": {
    "match": {
      "title": {
        "query": "quikc brwn fox",
        "fuzziness": "AUTO"
      }
    }
  }
}
```

fuzziness에 "AUTO"를 지정하면 Elasticsearch가 토큰 길이에 따라 허용 편집 거리를 자동으로 결정합니다. 토큰 길이가 0~2이면 편집 거리 0(정확히 일치해야 함), 3~5이면 편집 거리 1, 6 이상이면 편집 거리 2를 허용합니다. "quikc"는 5글자이므로 편집 거리 1까지 허용되어, "quick"과 매칭됩니다. "AUTO" 외에 정수 값(0, 1, 2)을 직접 지정할 수도 있습니다.

이제 match 쿼리와 근본적으로 다른 방식으로 동작하는 **term 쿼리**를 살펴봅니다. term 쿼리는 검색어를 분석기에 통과시키지 않습니다. 사용자가 입력한 값을 그대로 역색인에서 찾습니다. 대소문자, 공백, 특수문자까지 정확히 일치하는 값만 매칭됩니다.

이 차이가 실제로 어떤 결과를 만드는지, 구체적인 시나리오로 확인합니다. 인덱스에 text 타입의 title 필드가 있고, "Quick Brown Foxes!"라는 값이 저장되어 있다고 가정합니다. 인덱싱 시점에 standard 분석기가 이 값을 "quick", "brown", "foxes"로 토큰화하여 역색인에 등록합니다.

이 상황에서 term 쿼리로 "Quick Brown Foxes!"를 검색하면 어떻게 될까요. term 쿼리는 검색어를 분석하지 않으므로 "Quick Brown Foxes!"라는 문자열 그대로 역색인을 조회합니다. 역색인에는 소문자 토큰 "quick", "brown", "foxes"만 있고, "Quick Brown Foxes!"라는 문자열은 존재하지 않습니다. 결과적으로 문서가 검색되지 않습니다.

반면 match 쿼리로 같은 값을 검색하면, 검색어가 분석기를 거쳐 "quick", "brown", "foxes"로 토큰화됩니다. 역색인에 같은 토큰들이 있으므로 문서가 정상적으로 검색됩니다.

```
text 필드에 대한 term vs match 비교

원문: "Quick Brown Foxes!"
역색인 토큰: ["quick", "brown", "foxes"]

term 쿼리 "Quick Brown Foxes!"
  --> 분석 안 함 --> "Quick Brown Foxes!" 그대로 역색인 조회
  --> 일치하는 토큰 없음 --> 결과 0건

match 쿼리 "Quick Brown Foxes!"
  --> 분석기 적용 --> ["quick", "brown", "foxes"]
  --> 역색인에서 토큰 매칭 --> 결과 1건
```

이 때문에 term 쿼리는 text 타입 필드에 사용하면 기대와 다른 결과를 낳습니다. term 쿼리가 적합한 대상은 분석기를 거치지 않는 **keyword** 타입 필드입니다. keyword 타입은 2.2.1에서 살펴보았듯이 값을 분석 없이 원문 그대로 역색인에 저장합니다. "published"라는 값은 "published" 그대로 저장됩니다. 이 필드에 term 쿼리로 "published"를 검색하면 정확히 일치하므로 문서가 검색됩니다.

term 쿼리의 기본 형태를 살펴봅니다.

```json
GET my_index/_search
{
  "query": {
    "term": {
      "user.id": {
        "value": "kimchy",
        "boost": 1.0
      }
    }
  }
}
```

"term" 안에 필드 이름("user.id")을 지정하고, "value"에 정확히 찾을 값을 넣습니다. "boost"는 이 쿼리의 점수에 곱할 가중치로, 기본값은 1.0입니다. value에 넣은 문자열은 분석되지 않으므로, 대소문자와 공백까지 정확히 일치해야 합니다.

term 쿼리에는 대소문자 구분 없이 검색하는 옵션도 있습니다. **case_insensitive** 파라미터를 true로 설정하면 ASCII 범위의 대소문자를 무시하고 매칭합니다. 검색어를 직접 소문자로 변환하는 대신 이 옵션을 사용하는 것이 권장됩니다.

하나의 필드에서 여러 값 중 하나와 일치하는 문서를 찾고 싶을 때가 있습니다. 예를 들어 상태가 "published"이거나 "archived"인 문서를 한 번에 검색하려는 경우입니다. 이때 term 쿼리를 두 번 실행하는 대신 **terms 쿼리**를 사용합니다.

```json
GET my_index/_search
{
  "query": {
    "terms": {
      "status": ["published", "archived"]
    }
  }
}
```

"terms"(복수형)를 사용하고, 필드 이름에 배열로 값 목록을 전달합니다. 이 쿼리는 status가 "published"이거나 "archived"인 문서를 모두 반환합니다. 논리적으로 OR에 해당합니다. terms 쿼리 역시 입력값을 분석하지 않으므로, keyword 타입 필드에 사용하는 것이 적합합니다.

term과 terms 쿼리의 차이를 정리하면 다음과 같습니다.

```
term vs terms 쿼리

term 쿼리:  하나의 정확한 값과 매칭
  "term": { "status": { "value": "published" } }
  --> status가 정확히 "published"인 문서

terms 쿼리: 여러 값 중 하나와 매칭 (OR)
  "terms": { "status": ["published", "archived"] }
  --> status가 "published" 또는 "archived"인 문서
```

지금까지 살펴본 match 쿼리와 term 쿼리의 핵심 차이를 정리합니다. match 쿼리는 검색어를 분석기에 통과시킨 뒤 토큰 단위로 매칭하므로 text 타입 필드의 전문 검색에 적합합니다. term 쿼리는 검색어를 분석하지 않고 입력값 그대로 매칭하므로 keyword 타입 필드의 정확한 값 조회에 적합합니다. 이 차이를 무시하고 text 필드에 term 쿼리를 사용하면 의도한 결과를 얻지 못합니다.

이제 match 쿼리의 변형인 **match_phrase 쿼리**를 살펴봅니다. match 쿼리는 토큰들을 OR 또는 AND로 조합하지만, 토큰의 순서는 고려하지 않습니다. "quick brown fox"를 match 쿼리로 검색하면 "fox brown quick"이 포함된 문서도 결과에 나옵니다. 세 토큰이 모두 있기만 하면 되기 때문입니다. 그런데 "quick brown fox"라는 구문이 정확히 그 순서대로 등장하는 문서만 찾고 싶을 때가 있습니다. 이때 match_phrase 쿼리를 사용합니다.

match_phrase 쿼리는 검색어를 분석기에 통과시켜 토큰을 만든다는 점에서 match 쿼리와 같습니다. 다른 점은, 만들어진 토큰들이 문서에서 정확히 같은 순서로, 서로 인접한 위치에 나타나야 한다는 것입니다. 2.3.1에서 토크나이저가 각 토큰의 위치(position)를 기록한다고 설명한 것을 떠올려 봅니다. match_phrase 쿼리는 이 위치 정보를 활용하여 토큰의 순서와 인접성을 확인합니다.

```json
GET my_index/_search
{
  "query": {
    "match_phrase": {
      "content": "quick brown fox"
    }
  }
}
```

이 쿼리는 content 필드에서 "quick", "brown", "fox" 세 토큰이 정확히 이 순서대로, 연속으로 나타나는 문서만 반환합니다. "quick"이 위치 1에, "brown"이 위치 2에, "fox"가 위치 3에 있어야 합니다. "the quick brown fox jumps"에는 매칭되지만, "the fox is brown and quick"에는 매칭되지 않습니다. 순서가 다르기 때문입니다.

match_phrase 쿼리에는 **slop**이라는 파라미터가 있습니다. slop은 토큰 사이에 허용할 간격을 지정합니다. 기본값은 0이므로 토큰들이 정확히 인접해야 합니다. slop을 1로 설정하면 토큰 사이에 다른 토큰 하나가 끼어 있어도 매칭됩니다.

```json
{
  "query": {
    "match_phrase": {
      "content": {
        "query": "quick fox",
        "slop": 1
      }
    }
  }
}
```

이 쿼리는 "quick"과 "fox" 사이에 한 단어까지 끼어 있는 경우를 허용합니다. "quick brown fox"는 "quick"과 "fox" 사이에 "brown"이 하나 있으므로 매칭됩니다. slop을 2로 설정하면 두 단어까지 허용하고, 순서가 뒤바뀐 경우에도 위치 차이의 합이 slop 이하이면 매칭됩니다.

match 쿼리 계열의 마지막 변형으로 **match_phrase_prefix 쿼리**가 있습니다. 이 쿼리는 match_phrase와 동일하게 토큰의 순서와 인접성을 확인하되, 마지막 토큰을 접두사(prefix)로 취급합니다. 자동 완성 기능을 구현할 때 유용합니다.

```json
{
  "query": {
    "match_phrase_prefix": {
      "content": "quick bro"
    }
  }
}
```

이 쿼리는 "quick bro"를 분석하여 "quick"과 "bro" 두 토큰을 만듭니다. "quick"은 정확히 매칭하고, 마지막 토큰인 "bro"는 접두사로 취급합니다. 따라서 "quick brown", "quick broken", "quick broth" 등이 모두 매칭됩니다. 사용자가 검색어를 입력하는 도중에 실시간으로 결과를 보여 주는 자동 완성 UI에 활용할 수 있습니다.

지금까지 다룬 쿼리들의 차이를 한눈에 정리하면 다음과 같습니다.

```
쿼리 유형별 비교

쿼리               | 분석기 적용 | 토큰 순서 | 적합한 필드 타입 | 용도
-------------------|-----------|----------|----------------|------------------
match              | O         | 무관      | text           | 전문 검색
match_phrase       | O         | 순서 보장  | text           | 구문 검색
match_phrase_prefix| O         | 순서 보장  | text           | 자동 완성
term               | X         | 해당 없음  | keyword        | 정확한 값 조회
terms              | X         | 해당 없음  | keyword        | 복수 값 조회
```

정리하면, match 쿼리는 검색어를 분석기에 통과시켜 토큰 단위로 전문 검색을 수행하고, term 쿼리는 분석 없이 입력값 그대로 정확한 매칭을 수행합니다. match 쿼리는 text 필드에, term 쿼리는 keyword 필드에 사용하는 것이 원칙입니다. match 쿼리의 operator 파라미터로 AND/OR 동작을 제어하고, fuzziness로 오타를 허용할 수 있습니다. match_phrase 쿼리는 토큰의 순서와 인접성까지 보장하는 구문 검색을 수행하며, match_phrase_prefix는 마지막 토큰을 접두사로 취급하여 자동 완성에 활용됩니다.

다음 단원인 3.2.3에서는 bool 쿼리를 다룹니다.

이 단원을 마치면 match 쿼리와 term 쿼리의 분석기 적용 여부 차이를 설명할 수 있고, match_phrase로 구문 검색을 수행할 수 있습니다.

