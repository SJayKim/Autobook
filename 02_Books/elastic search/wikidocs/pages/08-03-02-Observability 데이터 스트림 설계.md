# 8.3.2 Observability 데이터 스트림 설계

8.3.1에서 Logs, Metrics, APM 세 가지 데이터를 하나의 Elasticsearch 클러스터에 통합하는 방법을 다뤘습니다. 통합이 완료되면 곧바로 현실적인 문제가 드러납니다. 로그는 하루에 수십 기가바이트씩 쌓이고, 메트릭은 10초 간격으로 수백 개 서버에서 수집되며, APM 트레이스는 요청 하나마다 여러 스팬을 생성합니다. 이 데이터를 아무런 설계 없이 저장하면, 디스크가 빠르게 소진되고 검색 성능이 떨어집니다. 3개월 전 로그를 7일 전 로그와 같은 빠른 디스크에 두는 것은 비용 낭비이고, 1초 간격 메트릭을 수년간 원본 해상도로 보관하는 것은 저장 공간을 불필요하게 차지합니다.

이 단원에서는 Observability 데이터를 효율적으로 관리하기 위해, Data Stream 네이밍 규칙, 보존 정책, 티어별 배치, 대용량 메트릭 다운샘플링, 그리고 Kibana Observability Overview 대시보드를 설계하는 방법을 다룹니다.

6.1.2에서 Data Stream의 개념과 backing index 구조를 다뤘습니다. Data Stream은 하나의 이름 아래 여러 backing index를 자동으로 관리하는 추상 계층이며, @timestamp 필드가 필수이고, 인덱스 템플릿에 data_stream 옵션을 설정하여 생성한다는 점을 배웠습니다. 이 단원에서는 그 Data Stream을 Observability 워크로드에 맞게 이름을 짓고, ILM 정책을 연결하여 데이터의 전체 수명주기를 자동화하는 데 초점을 둡니다.

Elastic Observability에서 Data Stream의 이름은 단순한 식별자가 아닙니다. 이름 자체가 데이터의 종류, 출처, 소속을 나타내는 구조화된 정보입니다. Elastic은 **ECS(Elastic Common Schema)** 기반의 네이밍 규칙을 사용합니다. ECS는 Elastic이 정의한 공통 필드 규격으로, 서로 다른 소스에서 온 데이터를 동일한 필드 이름으로 정규화하여 통합 검색과 분석을 가능하게 합니다. Data Stream 네이밍에서도 이 규격을 따라, 이름만 보고 데이터의 성격을 판단할 수 있도록 설계되어 있습니다.

네이밍 규칙은 세 부분으로 구성됩니다.

```
{type}-{dataset}-{namespace}
```

**type**은 데이터의 종류를 나타냅니다. Observability에서 사용하는 주요 type은 세 가지입니다. logs는 로그 데이터, metrics는 수치 지표, traces는 APM 분산 추적 데이터입니다. **dataset**은 데이터의 구체적인 출처를 나타냅니다. 예를 들어 nginx, system.cpu, apm.transaction 같은 값이 들어갑니다. **namespace**는 데이터가 속한 환경이나 팀을 구분합니다. production, staging, team-backend 같은 값을 사용합니다.

이 규칙에 따라 만들어지는 Data Stream 이름의 예를 보겠습니다.

```
logs-nginx-production          (프로덕션 환경의 Nginx 로그)
logs-nginx-staging             (스테이징 환경의 Nginx 로그)
metrics-system.cpu-production  (프로덕션 서버의 CPU 메트릭)
traces-apm-production          (프로덕션 APM 트레이스)
```

같은 Nginx 로그라도 production과 staging을 namespace로 분리하면, 환경별로 독립된 ILM 정책을 적용할 수 있습니다. 프로덕션 로그는 90일 보관하고 스테이징 로그는 14일만 보관하는 식의 차등 관리가 가능합니다.

Elastic Observability의 기본 제공 인덱스 템플릿은 이 네이밍 규칙을 따르는 패턴으로 구성되어 있습니다. Filebeat, Metricbeat, APM 에이전트가 데이터를 전송할 때 자동으로 이 패턴에 맞는 Data Stream을 생성합니다. 대표적인 인덱스 패턴은 다음과 같습니다.

```
logs-*       (모든 로그 Data Stream에 매칭)
metrics-*    (모든 메트릭 Data Stream에 매칭)
traces-*     (모든 트레이스 Data Stream에 매칭)
```

Kibana에서 이 패턴을 데이터 뷰(data view)로 등록하면, logs-nginx-production, logs-apache-production, logs-application-staging 등 서로 다른 Data Stream의 로그를 한 화면에서 통합 검색할 수 있습니다. type 수준에서 묶이기 때문에, 출처와 환경이 다른 데이터도 같은 종류끼리 자연스럽게 합쳐집니다.

이제 이 Data Stream에 적용할 보존 정책을 설계합니다. Observability 데이터는 시간이 지날수록 분석 가치가 낮아집니다. 장애가 발생하면 최근 몇 시간의 로그를 집중적으로 분석하고, 일주일 전 로그는 가끔 참조하며, 3개월 전 로그는 감사 목적으로만 보관하는 것이 일반적입니다. 이 특성을 반영하여 데이터의 나이에 따라 저장 티어를 옮기고, 일정 기간이 지나면 삭제하는 것이 보존 정책의 핵심입니다.

6.1.1에서 다룬 ILM은 backing index를 Hot, Warm, Cold, Delete 페이즈로 자동 전환합니다. 8.3.1에서 다룬 Observability 데이터에 이 ILM을 적용하려면, 데이터 종류별로 보존 요구사항이 다르다는 점을 고려해야 합니다.

로그 데이터는 가장 많은 저장 공간을 차지합니다. 하루에 수십 기가바이트가 쌓이는 환경에서는, 전체 기간의 로그를 빠른 디스크에 두는 것이 현실적으로 불가능합니다. 메트릭 데이터는 로그보다 개별 문서 크기가 작지만, 수집 주기가 짧아 문서 수가 매우 많습니다. 10초 간격으로 100대의 서버에서 CPU, 메모리, 디스크, 네트워크 지표를 수집하면 하루에 수백만 건이 쌓입니다. APM 트레이스는 요청량에 비례하여 증가하며, 분산 추적 데이터는 스팬 수가 많아 개별 트레이스의 크기가 클 수 있습니다.

이 차이를 반영한 보존 정책의 예를 표로 정리하겠습니다.

```
데이터 종류  | Hot    | Warm   | Cold   | 삭제
-------------|--------|--------|--------|--------
logs         | 7일    | 30일   | 90일   | 90일 후
metrics      | 3일    | 14일   | 60일   | 60일 후
traces       | 3일    | 7일    | 30일   | 30일 후
```

Hot 티어에는 SSD 같은 빠른 디스크를 배치합니다. 가장 최근 데이터가 여기에 저장되어 빠른 검색과 인덱싱을 처리합니다. Warm 티어에는 상대적으로 느리지만 용량 대비 비용이 낮은 디스크를 사용합니다. 검색은 가능하지만 인덱싱은 하지 않습니다. Cold 티어에는 가장 저렴한 스토리지를 사용하며, 가끔 발생하는 검색 요청만 처리합니다.

이 정책을 ILM으로 구현하는 과정을 살펴봅니다. 로그용 ILM 정책을 예로 들겠습니다.

```json
PUT _ilm/policy/observability-logs-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "1d"
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": {
            "number_of_shards": 1
          },
          "forcemerge": {
            "max_num_segments": 1
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "allocate": {
            "require": {
              "data": "cold"
            }
          }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

이 정책의 각 페이즈를 설명합니다. hot 페이즈에서는 backing index가 50GB에 도달하거나 1일이 경과하면 롤오버합니다. 롤오버란 새 backing index를 생성하여 쓰기 대상을 전환하는 것입니다(6.1.2). warm 페이즈는 7일이 경과한 backing index에 적용됩니다. shrink로 샤드 수를 1로 줄여 리소스를 절약하고, forcemerge로 세그먼트를 하나로 병합하여 검색 효율을 높입니다. cold 페이즈는 30일 경과 후 적용되며, cold 노드로 데이터를 이동합니다. delete 페이즈는 90일 경과 후 backing index를 삭제합니다.

이 ILM 정책을 인덱스 템플릿에 연결하면, logs-*로 시작하는 모든 Data Stream의 backing index가 이 정책을 자동으로 따릅니다.

```json
PUT _index_template/observability-logs
{
  "index_patterns": ["logs-*"],
  "data_stream": {},
  "template": {
    "settings": {
      "index.lifecycle.name": "observability-logs-policy",
      "index.lifecycle.rollover_alias": "logs"
    }
  },
  "priority": 200
}
```

메트릭과 트레이스도 같은 방식으로 별도의 ILM 정책을 만들어 각각 metrics-*, traces-* 패턴의 인덱스 템플릿에 연결합니다. 데이터 종류별로 보존 기간과 롤오버 조건을 다르게 설정할 수 있는 것은, type-dataset-namespace 네이밍 규칙 덕분에 인덱스 패턴으로 깔끔하게 분리되기 때문입니다.

롤오버 주기와 보존 크기를 결정할 때는 일일 데이터 생성량을 기준으로 계산합니다. 하루에 로그가 100GB씩 쌓이는 환경에서 Hot 티어에 7일치를 보관하려면 최소 700GB의 SSD 공간이 필요합니다. 여기에 레플리카를 1개 두면 1.4TB가 됩니다. Warm 티어에 23일치(7일 이후부터 30일까지)를 보관하면 2.3TB의 HDD 공간이 필요합니다. 이런 계산을 데이터 종류별로 수행하여 각 티어의 노드 수와 디스크 용량을 산정합니다.

```
일일 로그 100GB 기준 용량 산정

Hot 티어 (7일, 레플리카 1):
  100GB x 7일 x 2(레플리카) = 1,400GB

Warm 티어 (8일~30일, 레플리카 0):
  100GB x 23일 x 1 = 2,300GB

Cold 티어 (31일~90일, 레플리카 0):
  100GB x 60일 x 1 = 6,000GB

합계: 약 9.7TB
```

Warm 이후에는 새 데이터가 들어오지 않으므로 레플리카를 줄이거나 제거하여 공간을 절약합니다. Cold 티어에서는 Searchable Snapshot을 활용하면 원본 인덱스를 삭제하고 스냅샷만 유지하여 저장 공간을 더 절약할 수 있습니다.

Observability 메트릭에서 특히 유용한 기능이 **다운샘플링(downsampling)**입니다. 다운샘플링은 고해상도 시계열 데이터를 낮은 해상도로 변환하여 저장 공간을 줄이는 기법입니다.

다운샘플링이 필요한 상황을 구체적으로 살펴봅니다. 10초 간격으로 수집한 CPU 사용률 메트릭이 있다고 합시다. 최근 3일간의 데이터는 10초 단위로 보며 순간적인 스파이크를 분석합니다. 하지만 30일 전 데이터에서 10초 단위의 변동을 볼 일은 거의 없습니다. 시간 단위 평균으로 충분합니다. 90일 전 데이터는 일 단위 추이만 확인하면 됩니다.

다운샘플링은 이 차이를 반영합니다. 일정 기간이 지난 메트릭 데이터를 지정한 간격(예: 1시간, 1일)으로 집계하여 새로운 인덱스를 생성합니다. 원본 10초 간격 데이터에서 1시간 간격으로 다운샘플링하면, 360개의 데이터 포인트가 1개로 줄어듭니다. 저장 공간이 최대 70%까지 감소할 수 있습니다.

다운샘플링은 **Time Series Data Stream(TSDS)**에서 사용합니다. TSDS는 6.1.2에서 다룬 일반 Data Stream의 특수한 형태로, 시계열 메트릭에 최적화된 구조입니다. TSDS를 사용하려면 인덱스 템플릿에서 index.mode를 time_series로 설정하고, 라우팅 차원(dimension) 필드를 지정합니다. 라우팅 차원이란 시계열 데이터를 그룹으로 분류하는 기준입니다. 예를 들어 host.name과 metricset.name을 차원으로 지정하면, 같은 서버의 같은 종류의 메트릭이 하나의 시계열로 묶입니다.

ILM 정책에 다운샘플링 액션을 추가하면, 페이즈 전환 시 자동으로 다운샘플링이 실행됩니다.

```json
PUT _ilm/policy/observability-metrics-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "1d"
          }
        }
      },
      "warm": {
        "min_age": "3d",
        "actions": {
          "downsample": {
            "fixed_interval": "1h"
          },
          "shrink": {
            "number_of_shards": 1
          }
        }
      },
      "cold": {
        "min_age": "14d",
        "actions": {
          "downsample": {
            "fixed_interval": "1d"
          }
        }
      },
      "delete": {
        "min_age": "60d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

warm 페이즈에서 fixed_interval을 1h로 설정하면, 10초 간격이었던 원본 데이터가 1시간 간격 집계로 변환됩니다. cold 페이즈에서는 다시 1d 간격으로 집계합니다. 각 단계에서 평균, 최솟값, 최댓값, 합계 같은 통계값이 보존되므로, 해상도는 낮아지지만 추이 분석은 여전히 가능합니다.

다운샘플링의 효과를 수치로 살펴봅니다. 100대 서버에서 10초 간격으로 CPU, 메모리, 디스크, 네트워크 4종의 메트릭을 수집한다고 합시다. 하루에 생성되는 문서 수는 100대 x 4종 x 8,640(하루 10초 간격 횟수) = 약 3,456,000건입니다. 1시간 간격으로 다운샘플링하면 100대 x 4종 x 24 = 9,600건으로 줄어듭니다. 문서 수 기준으로 99.7% 감소입니다.

모든 설계를 마친 뒤, 실제 운영 현황을 한눈에 확인하는 도구가 **Kibana Observability Overview 대시보드**입니다. 이 대시보드는 Kibana의 Observability 메뉴에서 접근할 수 있으며, logs-*, metrics-*, traces-* 패턴의 Data Stream에서 데이터를 자동으로 수집하여 표시합니다.

Observability Overview 대시보드에는 핵심 지표가 통합되어 있습니다. 로그 영역에서는 최근 로그 발생량 추이와 에러 로그 비율을 보여 줍니다. 메트릭 영역에서는 호스트별 CPU, 메모리 사용률 현황을 보여 줍니다. APM 영역에서는 서비스별 응답 시간과 에러율을 보여 줍니다. 이 세 영역이 같은 시간축 위에 배치되어 있어, 특정 시간대에 로그 에러가 급증하면서 동시에 CPU 사용률이 치솟고 APM 응답 시간이 늘어난 상황을 한 화면에서 파악할 수 있습니다.

대시보드가 정상적으로 동작하려면, Data Stream의 네이밍이 ECS 규칙을 따라야 합니다. logs-*, metrics-*, traces-* 패턴에 맞지 않는 이름을 사용하면 대시보드에서 데이터가 표시되지 않습니다. 앞서 설계한 type-dataset-namespace 네이밍 규칙을 일관되게 적용하는 것이 중요한 이유가 여기에도 있습니다.

전체 설계 흐름을 정리합니다.

```
1. 네이밍 규칙 수립
   {type}-{dataset}-{namespace}
         |
         v
2. 데이터 종류별 ILM 정책 생성
   logs: Hot 7일 -> Warm 30일 -> Cold 90일 -> 삭제
   metrics: Hot 3일 -> Warm(다운샘플 1h) 14일 -> Cold(다운샘플 1d) 60일 -> 삭제
   traces: Hot 3일 -> Warm 7일 -> Cold 30일 -> 삭제
         |
         v
3. 인덱스 템플릿에 ILM 정책 연결
   logs-* -> observability-logs-policy
   metrics-* -> observability-metrics-policy
   traces-* -> observability-traces-policy
         |
         v
4. Kibana Observability Overview 대시보드에서 통합 모니터링
   logs-* + metrics-* + traces-* -> 단일 대시보드
```

정리하면, Observability 데이터 스트림 설계는 ECS 기반의 type-dataset-namespace 네이밍 규칙으로 시작합니다. 이 규칙 덕분에 logs-*, metrics-*, traces-* 패턴으로 데이터를 종류별로 분리하고, 각각에 맞는 ILM 정책을 적용할 수 있습니다. Hot-Warm-Cold 티어를 활용하여 데이터의 나이에 따라 저장 비용을 최적화하고, 메트릭 데이터에는 다운샘플링을 적용하여 장기 보존 시 저장 공간을 대폭 절약합니다. Kibana Observability Overview 대시보드에서 세 종류의 데이터를 하나의 시간축 위에 통합하여 모니터링합니다.

이 단원은 이 책의 마지막 단원입니다. 1장에서 Elasticsearch의 기본 개념과 역인덱스 구조를 이해하는 것으로 시작하여, 인덱스 설계, 매핑, 쿼리, 집계를 거치고, 클러스터 운영과 수명주기 관리를 익힌 뒤, 최종적으로 Observability라는 실전 워크로드에 이 모든 지식을 적용하는 데까지 다뤘습니다. Elasticsearch를 더 깊이 활용하려면, 공식 문서에서 Security(인증, 권한, TLS 설정), Machine Learning(이상 탐지, 예측 분석), Cross-Cluster Search(다중 클러스터 간 검색) 같은 주제를 추가로 학습하는 것을 권장합니다. 이 책에서 다룬 인덱스 구조, 쿼리 메커니즘, 클러스터 운영, 수명주기 관리의 기초가 갖춰져 있다면, 어떤 고급 주제를 만나더라도 동작 원리를 이해하고 적용하는 데 어려움이 없을 것입니다.

이 단원을 마치면 Observability 워크로드를 위한 Data Stream 네이밍 규칙과 ILM 정책을 설계할 수 있습니다.
