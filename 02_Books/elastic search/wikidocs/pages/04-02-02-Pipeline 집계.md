# 4.2.2 Pipeline 집계

4.2.1에서 Bucket 집계 안에 Metric 집계를 중첩하여 그룹별 통계를 구하는 방법을 다뤘습니다. terms + avg로 카테고리별 평균 가격을 구하거나, date_histogram + sum으로 월별 매출 총액을 구하는 패턴이었습니다. 이번 단원에서는 한 단계 더 나아가, 집계 결과를 다시 입력으로 받아 재계산하는 **Pipeline 집계**를 다룹니다.

Pipeline 집계가 왜 필요한지 구체적인 상황부터 설명합니다. 월별 매출 총액을 date_histogram + sum으로 구했다고 가정합니다. 여기서 "전월 대비 매출 증감"을 알고 싶습니다. 1월 매출이 1000만 원이고 2월 매출이 1200만 원이면, 2월의 증분은 200만 원입니다. 이 계산은 개별 문서를 대상으로 하는 것이 아니라, 이미 구해 놓은 월별 합계 사이의 차이를 구하는 것입니다. 다시 말해 "집계 결과에 대한 집계"입니다. Elasticsearch에서 이런 이중 계산을 담당하는 것이 Pipeline 집계입니다.

Pipeline 집계는 문서나 필드를 직접 읽지 않습니다. 다른 집계가 산출한 결과 값을 입력으로 받아 추가 연산을 수행합니다. 이 점이 Bucket 집계나 Metric 집계와 근본적으로 다릅니다. Bucket 집계는 문서를 그룹으로 나누고, Metric 집계는 문서의 필드 값으로 수치를 계산합니다. Pipeline 집계는 이미 계산된 수치를 가져와 새로운 수치를 만들어 냅니다.

Pipeline 집계를 사용하려면 "어떤 집계의 결과를 입력으로 쓸 것인지"를 지정해야 합니다. 이때 사용하는 것이 **buckets_path** 파라미터입니다. buckets_path는 참조할 집계의 결과를 가리키는 경로 문자열입니다.

buckets_path의 문법을 설명합니다. 가장 단순한 형태는 같은 중첩 수준에 있는 형제 집계를 가리키는 것입니다. 예를 들어 date_histogram 안에 "monthly_revenue"라는 sum 집계와 "revenue_derivative"라는 Pipeline 집계가 함께 있다면, buckets_path에 "monthly_revenue"를 적으면 됩니다. 다단계 경로가 필요할 때는 ">" 기호로 집계 이름을 연결합니다. 예를 들어 "by_category>avg_price"는 by_category 버킷 안의 avg_price 집계 결과를 가리킵니다. Metric 집계가 여러 값을 반환하는 경우(stats 집계 등)에는 점(.)으로 특정 값을 지정합니다. "price_stats.avg"는 stats 집계의 avg 값을 가리킵니다.

```
buckets_path 문법 정리

형태                     의미
--------------------    -------------------------------------------
"monthly_revenue"       같은 수준의 monthly_revenue 집계 결과
"by_category>avg_price" by_category 버킷 안의 avg_price 결과
"price_stats.avg"       stats 집계의 avg 값 지정
```

이제 주요 Pipeline 집계를 하나씩 살펴봅니다.

첫 번째는 **derivative 집계**입니다. derivative는 연속된 버킷 사이의 차이, 즉 증분을 계산합니다. 앞서 예로 든 "전월 대비 매출 증감"이 바로 이 집계의 대표적인 용도입니다.

```json
{
  "size": 0,
  "aggs": {
    "monthly_sales": {
      "date_histogram": {
        "field": "order_date",
        "calendar_interval": "month"
      },
      "aggs": {
        "monthly_revenue": {
          "sum": { "field": "price" }
        },
        "revenue_change": {
          "derivative": {
            "buckets_path": "monthly_revenue"
          }
        }
      }
    }
  }
}
```

이 요청의 구조를 풀어 설명합니다. date_histogram이 월별 버킷을 만들고, 각 버킷 안에서 sum 집계가 해당 월의 매출 총액(monthly_revenue)을 계산합니다. derivative 집계인 "revenue_change"는 buckets_path로 "monthly_revenue"를 참조합니다. Elasticsearch는 각 버킷의 monthly_revenue 값에서 이전 버킷의 monthly_revenue 값을 빼서 증분을 산출합니다. 첫 번째 버킷(1월)에는 이전 버킷이 없으므로 derivative 값이 null입니다. 2월 버킷부터 값이 나타납니다. 1월 매출이 1000만 원이고 2월 매출이 1200만 원이면, 2월의 revenue_change.value는 200만 원입니다.

두 번째는 **cumulative_sum 집계**입니다. 각 버킷까지의 누적 합계를 계산합니다. 월별 매출의 연간 누적 합계를 구하는 시나리오입니다.

```json
{
  "size": 0,
  "aggs": {
    "monthly_sales": {
      "date_histogram": {
        "field": "order_date",
        "calendar_interval": "month"
      },
      "aggs": {
        "monthly_revenue": {
          "sum": { "field": "price" }
        },
        "cumulative_revenue": {
          "cumulative_sum": {
            "buckets_path": "monthly_revenue"
          }
        }
      }
    }
  }
}
```

cumulative_sum 집계인 "cumulative_revenue"는 첫 번째 버킷부터 현재 버킷까지의 monthly_revenue를 누적하여 더합니다. 1월 매출이 1000만 원이면 1월의 누적 값은 1000만 원, 2월 매출이 1200만 원이면 2월의 누적 값은 2200만 원(1000 + 1200), 3월 매출이 800만 원이면 3월의 누적 값은 3000만 원(2200 + 800)이 됩니다. 연초부터 현재까지의 총 매출 추이를 시각화할 때 유용합니다.

세 번째는 **moving_fn 집계**입니다. 이 집계는 지정한 범위(윈도우) 안의 버킷 값들에 대해 사용자 정의 함수를 적용합니다. 이전 버전의 Elasticsearch에서는 moving_avg라는 이름으로 이동 평균을 전용으로 계산했으나, 현재는 moving_fn이 이를 대체합니다. moving_fn은 이동 평균 외에도 윈도우 안에서 다양한 계산을 할 수 있습니다.

```json
{
  "size": 0,
  "aggs": {
    "monthly_sales": {
      "date_histogram": {
        "field": "order_date",
        "calendar_interval": "month"
      },
      "aggs": {
        "monthly_revenue": {
          "sum": { "field": "price" }
        },
        "moving_avg_revenue": {
          "moving_fn": {
            "buckets_path": "monthly_revenue",
            "window": 3,
            "script": "MovingFunctions.unweightedAvg(values)"
          }
        }
      }
    }
  }
}
```

"window": 3은 현재 버킷 이전의 3개 버킷을 윈도우 범위로 잡는다는 뜻입니다. "script"에서 MovingFunctions.unweightedAvg(values)를 호출하면, 윈도우 안의 값들에 대해 단순 이동 평균을 계산합니다. 3월 버킷이라면 1월, 2월, 3월이 아니라 직전 3개 버킷(12월, 1월, 2월)의 평균이 됩니다. 이동 평균은 단기 변동을 완화하여 장기 추세를 파악할 때 사용합니다. MovingFunctions에는 unweightedAvg 외에도 linearWeightedAvg, ewma(지수 가중 이동 평균), max, min, sum, stdDev 같은 함수가 내장되어 있습니다.

네 번째는 버킷 수준 Pipeline 집계입니다. 앞서 다룬 derivative, cumulative_sum, moving_fn은 각 버킷마다 값을 산출하여 해당 버킷 안에 결과를 추가합니다. 반면 **avg_bucket, sum_bucket, min_bucket, max_bucket**은 모든 버킷의 값을 모아 하나의 수치로 요약합니다.

avg_bucket을 예로 들겠습니다. 월별 매출 총액의 평균을 구하는 시나리오입니다.

```json
{
  "size": 0,
  "aggs": {
    "monthly_sales": {
      "date_histogram": {
        "field": "order_date",
        "calendar_interval": "month"
      },
      "aggs": {
        "monthly_revenue": {
          "sum": { "field": "price" }
        }
      }
    },
    "avg_monthly_revenue": {
      "avg_bucket": {
        "buckets_path": "monthly_sales>monthly_revenue"
      }
    }
  }
}
```

여기서 주목할 점은 avg_bucket 집계의 위치입니다. date_histogram 안이 아니라, date_histogram과 같은 수준에 놓여 있습니다. avg_bucket은 monthly_sales의 모든 버킷에 걸쳐 monthly_revenue 값을 모아 그 평균을 구합니다. buckets_path가 "monthly_sales>monthly_revenue"인 이유는, 다른 집계(monthly_sales) 안의 하위 집계(monthly_revenue)를 참조하기 때문입니다. 응답에서 avg_monthly_revenue.value에 12개월 매출의 평균이 하나의 수치로 담깁니다. sum_bucket, min_bucket, max_bucket도 동일한 방식이며, 집계 타입만 다릅니다. sum_bucket은 모든 버킷 값의 합, min_bucket은 최솟값, max_bucket은 최댓값을 반환합니다.

다섯 번째는 **bucket_script 집계**입니다. bucket_script는 같은 버킷 안의 여러 Metric 집계 결과를 변수로 받아 사용자 정의 수식을 적용합니다. 월별 매출과 주문 수량을 구한 뒤, 주문 건당 평균 단가를 계산하는 시나리오입니다.

```json
{
  "size": 0,
  "aggs": {
    "monthly_sales": {
      "date_histogram": {
        "field": "order_date",
        "calendar_interval": "month"
      },
      "aggs": {
        "revenue": {
          "sum": { "field": "price" }
        },
        "units": {
          "sum": { "field": "quantity" }
        },
        "avg_unit_price": {
          "bucket_script": {
            "buckets_path": {
              "rev": "revenue",
              "qty": "units"
            },
            "script": "params.rev / params.qty"
          }
        }
      }
    }
  }
}
```

이 요청의 구조를 풀어 설명합니다. date_histogram이 월별 버킷을 만들고, 각 버킷 안에서 revenue(매출 합계)와 units(수량 합계)를 구합니다. bucket_script의 buckets_path에는 변수 이름과 참조할 집계를 매핑합니다. "rev"는 revenue 집계를 가리키고, "qty"는 units 집계를 가리킵니다. script에서 params.rev / params.qty로 매출을 수량으로 나누어 건당 평균 단가를 구합니다. 각 월 버킷마다 avg_unit_price.value에 결과가 담깁니다. script 안에서 덧셈, 뺄셈, 곱셈, 나눗셈, 조건식 등 Painless 스크립트 문법을 사용할 수 있습니다.

지금까지 다룬 Pipeline 집계를 용도별로 정리합니다.

```
Pipeline 집계 요약

집계 타입          입력                  출력                 용도
-----------       ------------------   ------------------   -------------------
derivative        연속 버킷 값          버킷 간 차이          전기 대비 증감
cumulative_sum    연속 버킷 값          누적 합계            연초부터 현재까지 총합
moving_fn         윈도우 내 버킷 값     윈도우 계산 결과      이동 평균, 추세 파악
avg_bucket        모든 버킷 값          단일 평균 수치        전체 버킷의 평균
sum_bucket        모든 버킷 값          단일 합계 수치        전체 버킷의 합
min_bucket        모든 버킷 값          단일 최솟값           가장 작은 버킷
max_bucket        모든 버킷 값          단일 최댓값           가장 큰 버킷
bucket_script     같은 버킷의 여러 값   사용자 정의 수식 결과  복합 계산
```

정리하면, Pipeline 집계는 다른 집계의 결과를 입력으로 받아 재계산하는 집계입니다. buckets_path로 참조할 집계를 지정하며, derivative는 증분, cumulative_sum은 누적 합, moving_fn은 윈도우 기반 계산, avg_bucket 등은 전체 버킷의 요약, bucket_script는 사용자 정의 수식을 수행합니다. Pipeline 집계 덕분에 집계 결과에 대한 후처리를 Elasticsearch 안에서 완결할 수 있습니다.

다음 단원인 4.2.3에서는 composite 집계를 다룹니다.

이 단원을 마치면 Pipeline 집계로 집계 결과를 입력으로 재계산하는 이중 집계를 구현할 수 있습니다.
