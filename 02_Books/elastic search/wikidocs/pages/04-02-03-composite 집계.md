# 4.2.3 composite 집계

4.2.1에서 다룬 중첩 집계로 다차원 분석이 가능해졌습니다. terms 집계를 여러 단계로 중첩하면 국가별, 카테고리별, 브랜드별처럼 여러 기준의 조합을 구할 수 있습니다. 그런데 이 방식에는 실무적인 한계가 있습니다. 이번 단원에서는 그 한계가 무엇인지 살펴보고, 이를 해결하는 **composite 집계**를 다룹니다.

terms 집계의 한계를 구체적으로 설명합니다. 4.1.2에서 다뤘듯이 terms 집계는 size 파라미터로 반환할 버킷 수를 제한합니다. 기본값은 10이고, 늘릴 수는 있지만 무한정 늘릴 수 없습니다. 카테고리가 10개이고 브랜드가 5개라면 최대 50개의 조합이므로 크게 문제되지 않습니다. 하지만 상품 ID처럼 고유 값이 수십만 개인 필드를 기준으로 집계하면, terms 집계의 size를 아무리 키워도 전체를 한 번에 가져올 수 없습니다. size를 지나치게 크게 설정하면 메모리 사용량이 급증하고 응답 시간이 느려집니다.

composite 집계는 이 문제를 **페이지네이션**으로 해결합니다. 전체 결과를 한 번에 가져오는 대신, 정해진 개수만큼 나누어 여러 번에 걸쳐 가져옵니다. 데이터베이스의 커서 기반 페이징과 비슷한 방식입니다. 한 번 요청할 때마다 일정량의 버킷을 반환하고, 다음 요청에서 이어서 가져올 수 있는 키를 함께 제공합니다.

composite 집계의 기본 구조를 살펴봅니다.

```json
{
  "size": 0,
  "aggs": {
    "my_composite": {
      "composite": {
        "size": 100,
        "sources": [
          {
            "category_source": {
              "terms": { "field": "category" }
            }
          },
          {
            "brand_source": {
              "terms": { "field": "brand" }
            }
          }
        ]
      }
    }
  }
}
```

이 요청의 각 부분을 풀어 설명합니다. "composite"가 집계 타입입니다. "size": 100은 한 번에 반환할 버킷 수입니다. terms 집계의 size와 이름은 같지만 역할이 다릅니다. terms 집계에서 size는 "상위 N개"를 의미하지만, composite 집계에서 size는 "한 페이지에 담을 개수"를 의미합니다. **sources** 배열이 composite 집계의 핵심입니다. 이 배열에 나열한 기준들의 모든 조합을 버킷으로 만듭니다. 위 예시에서는 category와 brand의 모든 조합이 각각 하나의 버킷이 됩니다.

sources 배열의 각 요소는 이름과 집계 타입의 쌍입니다. "category_source"가 이름이고, "terms"가 소스 타입입니다. sources에 사용할 수 있는 소스 타입은 네 가지입니다.

**terms 소스**는 keyword, 숫자, IP 등 필드의 고유 값을 기준으로 합니다. 4.1.2에서 다룬 terms 집계와 동일한 원리이지만, composite 안에서는 페이지네이션의 한 축을 담당합니다.

**date_histogram 소스**는 날짜 필드를 시간 간격으로 나눕니다. 4.1.2에서 다룬 date_histogram 집계의 calendar_interval이나 fixed_interval을 그대로 사용합니다.

```json
{
  "date_source": {
    "date_histogram": {
      "field": "order_date",
      "calendar_interval": "month"
    }
  }
}
```

**histogram 소스**는 숫자 필드를 고정 간격으로 나눕니다. 4.1.2에서 다룬 histogram 집계의 interval을 그대로 사용합니다.

**geotile_grid 소스**는 지리 좌표를 타일 격자로 나눕니다. geo_point 필드를 대상으로 하며, precision 파라미터로 격자의 세밀함을 조정합니다. 지도 시각화에서 영역별 집계가 필요할 때 사용합니다.

이제 composite 집계의 핵심인 페이지네이션 방법을 설명합니다. 첫 번째 요청의 응답에는 버킷 목록과 함께 **after_key**가 포함됩니다.

```json
{
  "aggregations": {
    "my_composite": {
      "after_key": {
        "category_source": "의류",
        "brand_source": "B사"
      },
      "buckets": [
        {
          "key": {
            "category_source": "가전",
            "brand_source": "A사"
          },
          "doc_count": 42
        },
        {
          "key": {
            "category_source": "의류",
            "brand_source": "B사"
          },
          "doc_count": 37
        }
      ]
    }
  }
}
```

after_key는 이번 페이지의 마지막 버킷 키를 나타냅니다. 다음 페이지를 가져오려면 이 after_key를 그대로 다음 요청의 "after" 파라미터에 넣습니다.

```json
{
  "size": 0,
  "aggs": {
    "my_composite": {
      "composite": {
        "size": 100,
        "sources": [
          {
            "category_source": {
              "terms": { "field": "category" }
            }
          },
          {
            "brand_source": {
              "terms": { "field": "brand" }
            }
          }
        ],
        "after": {
          "category_source": "의류",
          "brand_source": "B사"
        }
      }
    }
  }
}
```

"after"에 이전 응답의 after_key 값을 그대로 넣으면, Elasticsearch는 그 키 다음부터 이어서 버킷을 반환합니다. 응답의 buckets 배열이 비어 있으면 더 이상 가져올 데이터가 없다는 뜻입니다. 이 과정을 반복하면 전체 조합을 빠짐없이 순회할 수 있습니다.

```
composite 집계 페이지네이션 흐름

1. 첫 번째 요청 (after 없음)
   -> 버킷 100개 반환 + after_key

2. 두 번째 요청 (after: 첫 번째의 after_key)
   -> 다음 버킷 100개 반환 + after_key

3. 세 번째 요청 (after: 두 번째의 after_key)
   -> 다음 버킷 100개 반환 + after_key

4. ... 반복 ...

5. N번째 요청
   -> buckets 배열이 비어 있음 -> 종료
```

composite 집계와 terms 집계의 차이를 정리합니다. terms 집계는 문서 수 기준으로 상위 N개의 버킷만 반환합니다. 전체 값을 순회하는 것이 목적이 아니라, 가장 빈도가 높은 값들을 빠르게 확인하는 것이 목적입니다. composite 집계는 모든 조합을 빠짐없이 순회하는 것이 목적입니다. 문서 수 기준 정렬 대신, 키 값의 자연 순서(알파벳, 숫자, 날짜 순)로 정렬하여 페이지네이션합니다. 한 번에 메모리에 올리는 버킷 수가 size로 제한되므로, 고카디널리티 필드에서도 안정적으로 작동합니다.

```
terms 집계 vs composite 집계

                    terms 집계              composite 집계
------------------  --------------------   ----------------------
반환 방식           상위 N개 한 번에        페이지 단위 순차 반환
정렬 기준           doc_count 내림차순      키 값의 자연 순서
고카디널리티 대응    size 제한 필요          after_key로 순회 가능
다차원 조합         중첩으로 구현           sources 배열로 flat 구현
메모리 사용         size 비례              페이지 size 비례
```

composite 집계는 Kibana의 대시보드에서 내부적으로 많이 사용됩니다. 대시보드의 시각화 패널이 날짜와 카테고리 등 여러 차원의 집계를 필요로 할 때, Kibana는 composite 집계를 통해 결과를 페이지 단위로 가져옵니다. 특히 대량의 데이터를 다루는 대시보드에서 terms 집계의 size 한계에 부딪히지 않고 전체 데이터를 안정적으로 집계할 수 있습니다.

composite 집계 안에도 하위 집계를 넣을 수 있습니다. 4.2.1에서 다룬 중첩 집계와 같은 방식입니다.

```json
{
  "size": 0,
  "aggs": {
    "my_composite": {
      "composite": {
        "size": 100,
        "sources": [
          {
            "category_source": {
              "terms": { "field": "category" }
            }
          }
        ]
      },
      "aggs": {
        "avg_price": {
          "avg": { "field": "price" }
        }
      }
    }
  }
}
```

이 요청은 카테고리별 평균 가격을 composite 집계로 구합니다. 각 버킷마다 avg_price.value가 포함됩니다. 페이지네이션을 하면서 동시에 그룹별 통계를 산출할 수 있습니다.

정리하면, composite 집계는 여러 소스의 조합을 페이지네이션하며 순회하는 집계입니다. sources 배열에 terms, date_histogram, histogram, geotile_grid 소스를 나열하고, after_key를 이용하여 다음 페이지를 가져옵니다. 한 번에 메모리에 올리는 양이 제한되므로 고카디널리티 필드에서도 안정적이며, Kibana 대시보드에서 내부적으로 활용됩니다.

다음 단원인 4.2.4에서는 집계 성능 최적화를 다룹니다.

이 단원을 마치면 composite 집계로 대용량 다차원 집계를 페이지네이션하며 처리할 수 있습니다.
