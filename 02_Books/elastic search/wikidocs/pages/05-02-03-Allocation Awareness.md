# 5.2.3 Allocation Awareness

5.2.1에서 샤드 크기와 수를 결정하는 기준을 살펴보았습니다. 샤드 수를 잘 정했다 하더라도, 프라이머리 샤드와 그 레플리카가 같은 물리 서버 랙에 몰려 있다면, 그 랙 전체에 전원 장애가 발생했을 때 원본과 복제본이 동시에 사라집니다. 샤드를 '몇 개' 만들 것인지뿐 아니라, '어디에' 배치할 것인지도 중요합니다. 이 단원에서는 Elasticsearch가 샤드를 노드에 배치하는 규칙을 제어하는 Allocation Awareness 기능을 다룹니다.

Allocation Awareness를 이해하려면 먼저 **노드에 커스텀 속성을 부여하는 방법**을 알아야 합니다. Elasticsearch는 노드마다 사용자 정의 속성을 설정할 수 있습니다. `elasticsearch.yml`에 다음과 같이 지정합니다.

```yaml
node.attr.rack: rack-1
```

이 설정은 해당 노드에 "rack"이라는 속성을 부여하고, 값을 "rack-1"로 지정합니다. 다른 노드에는 "rack-2"를 지정할 수 있습니다. 속성 이름은 자유롭게 정할 수 있습니다. "zone", "region", "dc" 등 환경에 맞는 이름을 사용하면 됩니다.

이제 Elasticsearch에 이 속성을 인식시킵니다. **cluster.routing.allocation.awareness.attributes** 설정이 핵심입니다.

```yaml
cluster.routing.allocation.awareness.attributes: rack
```

이 설정을 클러스터에 적용하면, Elasticsearch는 샤드를 배치할 때 "rack" 속성 값을 고려합니다. 프라이머리 샤드가 rack-1에 있는 노드에 배치되면, 그 레플리카는 rack-2에 있는 노드에 배치하려고 시도합니다. 같은 rack 값을 가진 노드에 프라이머리와 레플리카가 함께 놓이는 것을 피하는 것입니다.

구체적인 시나리오를 들어 봅니다. 노드가 4대 있고, 2대는 rack-1, 나머지 2대는 rack-2에 속합니다. 프라이머리 샤드 2개, 레플리카 1인 인덱스를 만들면 다음과 같이 배치됩니다.

```
Allocation Awareness 배치 예시

rack-1                      rack-2
+--------+  +--------+     +--------+  +--------+
| Node-A |  | Node-B |     | Node-C |  | Node-D |
| P0     |  | P1     |     | R0     |  | R1     |
+--------+  +--------+     +--------+  +--------+

P0의 레플리카 R0는 다른 rack(rack-2)에 배치
P1의 레플리카 R1도 다른 rack(rack-2)에 배치
```

rack-1 전체가 장애를 일으켜도, rack-2에 R0와 R1이 남아 있으므로 데이터를 잃지 않습니다. R0와 R1이 각각 새 프라이머리로 승격되어 서비스가 계속됩니다.

Allocation Awareness에는 더 강력한 변형이 있습니다. **Forced Awareness**는 특정 속성 값 중 하나가 사용 불가능해도, 남은 노드에 레플리카를 강제로 몰아넣지 않는 설정입니다.

일반 Allocation Awareness에서는, rack-2의 노드가 모두 내려가면 Elasticsearch가 rack-1의 노드에 R0와 R1까지 배치하려고 시도합니다. rack-1에 프라이머리와 레플리카가 모두 모이면, rack-1 장애 시 전체 데이터가 유실됩니다. Forced Awareness는 이 상황을 방지합니다.

```yaml
cluster.routing.allocation.awareness.attributes: zone
cluster.routing.allocation.awareness.force.zone.values: zone-a, zone-b
```

첫 번째 줄은 "zone" 속성으로 Allocation Awareness를 활성화합니다. 두 번째 줄은 "zone" 속성의 가능한 값이 "zone-a"와 "zone-b"임을 선언합니다. 이 설정이 적용되면, zone-b의 노드가 모두 내려가더라도 Elasticsearch는 zone-b에 배치되어야 할 레플리카를 zone-a에 넣지 않습니다. 해당 레플리카는 미할당(unassigned) 상태로 남습니다. 클러스터 상태가 yellow로 바뀌지만, 단일 장애 영역에 원본과 복제본이 동시에 존재하는 위험은 제거됩니다.

Allocation Awareness와 별도로, 더 세밀하게 샤드 배치를 제어하는 기능이 **shard allocation filtering**입니다. 이 기능은 특정 인덱스의 샤드가 배치될 수 있는 노드를 필터 조건으로 제한합니다. 세 가지 접두사를 사용합니다.

**include**는 지정한 속성 값을 가진 노드 중 하나에 샤드를 배치합니다. 여러 값을 쉼표로 나열하면 그중 하나에 해당하면 됩니다.

```json
PUT /my-index/_settings
{
  "index.routing.allocation.include.rack": "rack-1,rack-2"
}
```

이 설정은 my-index의 샤드를 rack 속성이 rack-1 또는 rack-2인 노드에만 배치합니다.

**exclude**는 지정한 속성 값을 가진 노드를 배치 대상에서 제외합니다.

```json
PUT /my-index/_settings
{
  "index.routing.allocation.exclude.rack": "rack-3"
}
```

이 설정은 rack-3인 노드에는 my-index의 샤드를 배치하지 않습니다. 노드 퇴역(decommission) 시 해당 노드에서 샤드를 빼내는 데 유용합니다.

**require**는 지정한 속성 값을 가진 노드에만 샤드를 배치합니다. include와 비슷하지만, require는 모든 조건을 동시에 만족해야 합니다.

```json
PUT /my-index/_settings
{
  "index.routing.allocation.require.zone": "zone-a"
}
```

이 설정은 zone 속성이 정확히 zone-a인 노드에만 샤드를 배치합니다.

이 세 가지 필터는 인덱스 수준뿐 아니라 클러스터 수준에서도 설정할 수 있습니다. 클러스터 수준에서는 `cluster.routing.allocation.include.*`, `cluster.routing.allocation.exclude.*`, `cluster.routing.allocation.require.*`를 사용합니다.

**클라우드 환경에서의 multi-AZ 배치 전략**을 살펴봅니다. AWS, GCP, Azure 같은 클라우드 환경에서는 가용 영역(Availability Zone, AZ)이 물리적 데이터센터 단위의 장애 격리 영역입니다. AZ 하나가 통째로 장애를 일으킬 수 있으므로, 프라이머리와 레플리카를 서로 다른 AZ에 분산해야 합니다.

권장 구성은 3개의 AZ에 노드를 균등하게 배치하는 것입니다. 각 노드에 AZ를 속성으로 설정하고, Forced Awareness로 AZ 값을 선언합니다.

```yaml
node.attr.zone: az-1
cluster.routing.allocation.awareness.attributes: zone
cluster.routing.allocation.awareness.force.zone.values: az-1, az-2, az-3
```

레플리카를 2로 설정하면, 프라이머리가 az-1에, 레플리카 하나가 az-2에, 다른 레플리카가 az-3에 배치됩니다. 어느 AZ 하나가 완전히 장애를 일으켜도 나머지 두 AZ에 데이터가 남아 있습니다.

샤드가 왜 특정 노드에 배치되었는지, 왜 미할당 상태인지를 분석할 때는 **allocation explain API**를 사용합니다.

```
GET _cluster/allocation/explain
```

이 API는 미할당 샤드가 있을 경우, 해당 샤드가 왜 할당되지 못했는지 이유를 상세히 알려 줍니다. 예를 들어 "node does not match index setting [index.routing.allocation.require.zone] filters"라는 메시지가 나오면, 해당 노드의 zone 속성이 인덱스의 require 조건과 맞지 않아 배치가 거부되었다는 뜻입니다.

마지막으로 **리밸런싱**(rebalancing)을 짧게 짚습니다. 노드가 추가되거나 제거되면, Elasticsearch는 샤드를 노드 간에 자동으로 재분배하여 각 노드의 샤드 수가 고르게 됩니다. 이 과정을 리밸런싱이라고 합니다. 리밸런싱은 기본적으로 활성화되어 있으며, `cluster.routing.rebalance.enable` 설정으로 제어할 수 있습니다. 이 설정의 값은 "all"(기본값, 모든 샤드 리밸런싱), "primaries"(프라이머리만), "replicas"(레플리카만), "none"(비활성)입니다. 대량 데이터 적재 중에는 리밸런싱이 네트워크와 디스크 I/O를 소비하므로, 일시적으로 비활성화한 뒤 적재 완료 후 다시 활성화하는 전략이 사용됩니다.

정리하면, Allocation Awareness는 node.attr.* 속성과 cluster.routing.allocation.awareness.attributes 설정을 결합하여, 프라이머리와 레플리카를 서로 다른 물리적 영역에 분산 배치합니다. Forced Awareness는 한 영역이 내려가더라도 남은 영역에 레플리카를 강제 배치하지 않아 단일 장애 영역 격리를 보장합니다. shard allocation filtering(include/exclude/require)으로 인덱스별 배치 대상을 세밀하게 제한할 수 있으며, allocation explain API로 배치 결정의 이유를 진단합니다.

다음 단원인 5.3.1에서는 CCS(Cross-Cluster Search) 설정을 다룹니다. 하나의 클러스터를 넘어 여러 클러스터에 걸쳐 검색하는 방법을 살펴봅니다.

이 단원을 마치면 Allocation Awareness로 샤드를 특정 속성 기준으로 분산 배치할 수 있으며, Forced Awareness로 단일 장애 영역 격리를 구성할 수 있습니다.
