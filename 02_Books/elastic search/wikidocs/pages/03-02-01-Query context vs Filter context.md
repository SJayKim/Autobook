# 3.2.1 Query context vs Filter context

1.1.3에서 _search API와 match 쿼리를 사용해 문서를 검색하는 방법을 다뤘습니다. 그때 검색 결과에는 각 문서마다 _score라는 관련성 점수가 붙어 있었고, 점수가 높은 문서가 상위에 노출되었습니다. 그런데 실무에서 검색 조건을 구성하다 보면, 모든 조건이 관련성 점수를 필요로 하지는 않는다는 사실을 깨닫게 됩니다. 예를 들어 "Elasticsearch 튜토리얼"이라는 키워드로 글을 검색할 때, 키워드와 본문의 유사도에 따라 순위를 매기는 것은 의미가 있습니다. 하지만 "상태가 published인 글만 보여 달라"는 조건은 점수를 매길 필요가 없습니다. published이면 포함하고, 아니면 제외하면 그뿐입니다. Elasticsearch는 이 두 가지 상황을 명확히 구분합니다. 하나는 "이 문서가 검색어와 얼마나 잘 맞는가"를 계산하는 상황이고, 다른 하나는 "이 문서가 조건을 만족하는가, 아닌가"만 판단하는 상황입니다.

Elasticsearch는 이 구분을 **query context**와 **filter context**라는 두 가지 실행 맥락으로 나눕니다.

query context는 "이 문서가 검색 조건과 얼마나 관련이 있는가"에 답합니다. query context에서 실행되는 쿼리 절은 매칭 여부뿐 아니라, 각 문서에 대해 관련성 점수인 _score를 계산합니다. 1.1.3에서 match 쿼리로 "검색"이라는 단어를 찾았을 때, 각 문서마다 1.4712, 0.8319 같은 점수가 매겨졌던 것이 바로 query context에서의 동작입니다. Elasticsearch는 검색어를 분석기로 토큰화하고, 역색인에서 매칭되는 문서를 찾은 뒤, BM25 알고리즘으로 각 문서가 검색어와 얼마나 관련 있는지를 수치로 산출합니다.

**filter context**는 이와 다릅니다. filter context는 "이 문서가 조건에 맞는가, 아닌가"라는 이진 판단만 수행합니다. 맞으면 결과에 포함하고, 맞지 않으면 제외합니다. 점수를 계산하지 않으므로, _score에 기여하는 값은 0입니다. "status가 published인가", "날짜가 2024년 1월 1일 이후인가", "카테고리가 draft가 아닌가"처럼 예/아니오로 판단할 수 있는 조건이 filter context에 적합합니다.

filter context가 점수를 계산하지 않는다는 점은 단순히 결과 형태의 차이에 그치지 않습니다. 점수 계산을 건너뛴다는 것은 곧 성능 이점으로 이어집니다. Elasticsearch는 filter context에서 실행된 쿼리의 결과를 **bitset cache**에 저장합니다. bitset은 인덱스의 모든 문서를 대상으로 "이 문서가 조건에 맞으면 1, 아니면 0"을 표시하는 비트 배열입니다. 예를 들어 인덱스에 문서가 다섯 건 있고, 그중 첫 번째와 세 번째 문서만 "status가 published"라면, bitset은 [1, 0, 1, 0, 0]이 됩니다.

이 bitset이 캐시에 올라가면, 동일한 조건의 필터가 다시 실행될 때 Elasticsearch는 역색인을 다시 조회하지 않습니다. 캐시에 저장된 bitset을 그대로 가져와 적용하기만 하면 됩니다. "status가 published인 문서만 보여 달라"는 조건은 여러 사용자가 반복적으로 보내는 경우가 많으므로, 캐시의 효과가 큽니다. 반면 query context의 쿼리는 검색어가 달라질 때마다 점수를 새로 계산해야 하므로, 이런 캐싱이 적용되지 않습니다.

bitset cache의 동작을 단계별로 정리하면 다음과 같습니다.

```
filter context 캐싱 흐름

1. 클라이언트 → filter 조건 전송 (예: "status": "published")
2. Elasticsearch → 캐시에 해당 조건의 bitset이 있는지 확인
   ├─ 캐시 적중 → 저장된 bitset 반환 (역색인 조회 생략)
   └─ 캐시 미스 → 역색인 조회 → bitset 생성 → 캐시에 저장
3. bitset을 다른 쿼리 결과와 조합하여 최종 결과 산출
```

그렇다면 query context와 filter context를 실제로 어떻게 지정할까요. Elasticsearch에서 이 두 맥락을 가장 자연스럽게 나누어 쓸 수 있는 도구가 **bool 쿼리**입니다. bool 쿼리는 여러 쿼리 절을 하나로 묶는 복합 쿼리로, 네 가지 절을 제공합니다. 이 네 가지 절 중 어디에 쿼리를 배치하느냐에 따라 query context로 실행될지, filter context로 실행될지가 결정됩니다.

bool 쿼리의 네 가지 절은 **must**, **filter**, **should**, **must_not**입니다. 각 절의 역할을 하나씩 설명합니다.

must 절에 배치된 쿼리는 query context에서 실행됩니다. 문서가 결과에 포함되려면 must 절의 모든 쿼리를 만족해야 합니다. 동시에 각 쿼리가 계산한 점수가 최종 _score에 합산됩니다. 논리적으로 AND에 해당합니다.

filter 절에 배치된 쿼리는 filter context에서 실행됩니다. 문서가 결과에 포함되려면 filter 절의 모든 쿼리를 만족해야 한다는 점은 must와 같습니다. 그러나 점수를 계산하지 않으며, 결과가 bitset cache에 캐싱됩니다.

should 절에 배치된 쿼리는 query context에서 실행됩니다. should 절의 쿼리를 만족하는 문서는 추가 점수를 받아 상위에 노출됩니다. 논리적으로 OR에 해당하며, bool 쿼리에 must나 filter 절이 함께 있으면 should를 하나도 만족하지 않아도 결과에서 제외되지 않습니다. 다만 must나 filter 없이 should만 있는 경우에는 최소 하나의 should 절을 만족해야 합니다.

must_not 절에 배치된 쿼리는 filter context에서 실행됩니다. 이 절의 쿼리를 만족하는 문서는 결과에서 제외됩니다. 점수에 기여하지 않으며, 역시 캐싱 대상입니다. 논리적으로 NOT에 해당합니다.

네 절의 차이를 정리하면 다음과 같습니다.

```
bool 쿼리 절 비교

절         | 실행 맥락       | 점수 기여 | 캐싱 | 논리 연산
-----------|----------------|----------|------|----------
must       | query context  | O        | X    | AND
filter     | filter context | X        | O    | AND
should     | query context  | O        | X    | OR
must_not   | filter context | X        | O    | NOT
```

구체적인 예를 하나 들어 봅니다. 블로그 글을 검색하는 상황을 가정합니다. "title 필드에 Elasticsearch가 포함된 글을 찾되, 상태가 published이고, 작성일이 2024년 1월 1일 이후인 것만 보여 주고, 카테고리가 draft인 것은 제외하라. 태그에 tutorial이 있으면 우선 노출하라."

이 요구사항을 bool 쿼리로 표현하면 다음과 같습니다.

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "Elasticsearch" } }
      ],
      "filter": [
        { "term": { "status": "published" } },
        { "range": { "date": { "gte": "2024-01-01" } } }
      ],
      "should": [
        { "match": { "tags": "tutorial" } }
      ],
      "must_not": [
        { "term": { "category": "draft" } }
      ]
    }
  }
}
```

이 쿼리의 각 절이 어떻게 동작하는지 풀어 봅니다.

must 절의 match 쿼리는 title 필드에서 "Elasticsearch"를 검색합니다. query context에서 실행되므로, 각 문서에 대해 title과 "Elasticsearch"의 관련성 점수를 계산합니다. 이 점수가 최종 _score의 기반이 됩니다.

filter 절에는 두 조건이 있습니다. term 쿼리는 status 필드가 정확히 "published"인 문서만 통과시킵니다. range 쿼리는 date 필드가 2024-01-01 이후인 문서만 통과시킵니다. 두 조건 모두 filter context에서 실행되므로 점수를 계산하지 않고, 결과가 bitset cache에 저장됩니다. 같은 조건의 요청이 반복되면 캐시에서 바로 결과를 가져옵니다.

should 절의 match 쿼리는 tags 필드에서 "tutorial"을 검색합니다. must 절이 이미 존재하므로, should를 만족하지 않아도 결과에서 빠지지는 않습니다. 다만 tags에 "tutorial"이 있는 문서는 추가 점수를 받아 상위에 노출됩니다.

must_not 절의 term 쿼리는 category가 "draft"인 문서를 제외합니다. filter context에서 실행되므로 점수에 영향을 주지 않습니다.

이 쿼리가 실행되는 흐름을 단계별로 나타내면 다음과 같습니다.

```
bool 쿼리 실행 흐름

1. filter 절 실행
   - status = "published" → bitset A 생성 (또는 캐시에서 로드)
   - date >= "2024-01-01" → bitset B 생성 (또는 캐시에서 로드)
   - bitset A AND bitset B → 후보 문서 집합 확정

2. must_not 절 실행
   - category = "draft" → bitset C 생성
   - 후보 문서 집합에서 bitset C에 해당하는 문서 제외

3. must 절 실행
   - 남은 후보 문서에 대해 title "Elasticsearch" match 쿼리 실행
   - 각 문서의 관련성 점수 계산

4. should 절 실행
   - tags "tutorial" match 쿼리 실행
   - 매칭되는 문서에 추가 점수 부여

5. must 점수 + should 점수 = 최종 _score
6. _score 순으로 정렬하여 반환
```

이 흐름에서 주목할 점은 filter와 must_not이 먼저 실행되어 후보 문서의 범위를 줄인다는 것입니다. 점수 계산이 필요한 must와 should는 이미 줄어든 문서 집합에 대해서만 실행됩니다. 점수 계산은 비용이 큰 연산이므로, filter로 후보를 먼저 좁히면 전체 검색 성능이 향상됩니다.

이제 어떤 조건을 query context에 두고 어떤 조건을 filter context에 둘지, 선택 기준을 정리합니다.

텍스트 유사도가 중요한 조건은 query context에 둡니다. "이 문서가 검색어와 얼마나 관련 있는가"라는 질문에 답해야 하는 경우입니다. 전문 검색(full-text search)이 대표적입니다. 사용자가 입력한 검색어와 문서 본문의 유사도를 BM25로 계산해야 하므로, must나 should 절에 배치합니다.

예/아니오로 판단 가능한 조건은 filter context에 둡니다. 날짜 범위, 카테고리, 상태 값, 숫자 범위처럼 문서가 조건을 만족하는지 여부만 따지면 되는 경우입니다. 이런 조건에 점수를 매기는 것은 불필요한 연산이며, filter 절에 두면 캐싱 혜택까지 얻습니다.

구체적으로 나열하면 다음과 같습니다. filter에 적합한 조건의 예로는 날짜 범위("2024년 1월 1일 이후 글"), 상태 필드("status가 published"), 카테고리 분류("category가 tutorial"), 숫자 범위("가격이 10000 이상 50000 이하"), 존재 여부("thumbnail 필드가 있는 문서")가 있습니다. query에 적합한 조건의 예로는 제목이나 본문의 키워드 검색("Elasticsearch 튜토리얼"), 태그나 설명 필드의 유사도 검색이 있습니다.

실무에서 검색 요청 하나에 여러 조건이 섞이는 경우가 대부분입니다. 이때 모든 조건을 must에 넣는 실수를 자주 합니다. 예를 들어 상태 필터까지 must에 넣으면, Elasticsearch는 "status가 published"라는 조건에 대해서도 점수를 계산합니다. status는 정확히 일치하거나 일치하지 않거나 둘 중 하나이므로, 점수 계산은 의미 없는 연산입니다. 게다가 캐시도 되지 않습니다. 이 조건을 filter로 옮기면 불필요한 점수 계산을 피하고, 동일 조건의 반복 요청에서 캐시가 작동하여 응답 속도가 빨라집니다.

정리하면, Elasticsearch의 query context는 문서와 검색 조건의 관련성 점수를 계산하는 맥락이고, filter context는 조건의 충족 여부만 이진으로 판단하는 맥락입니다. filter context는 점수 계산을 건너뛰므로 빠르고, 결과를 bitset cache에 저장하여 반복 요청에서 더 큰 성능 이점을 줍니다. bool 쿼리의 네 절 중 must와 should는 query context, filter와 must_not은 filter context에서 실행됩니다. 성능 최적화의 핵심은 점수가 필요 없는 조건을 filter 절로 옮기는 것입니다.

다음 단원인 3.2.2에서는 match와 term 쿼리를 다룹니다.

이 단원을 마치면 query context와 filter context의 차이를 설명하고 적절히 선택할 수 있으며, filter context의 bitset 캐싱이 검색 성능을 어떻게 향상시키는지 설명할 수 있습니다.
