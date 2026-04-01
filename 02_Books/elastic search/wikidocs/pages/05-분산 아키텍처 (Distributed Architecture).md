# Phase 5. 분산 아키텍처 (Distributed Architecture)

이 Phase를 마치면 클러스터 노드 역할을 설계하고, 샤드 전략을 수립하며, Cross-Cluster Search 환경을 구성할 수 있게 됩니다.

Elasticsearch의 진가는 분산 환경에서 발휘됩니다. 수십 개의 노드가 협력하여 수십 테라바이트의 데이터를 처리하고, 노드 장애가 발생해도 서비스를 중단 없이 유지합니다. Phase 5에서는 클러스터를 구성하는 노드의 역할, 마스터 선출과 분산 읽기/쓰기 흐름, 샤드 전략 설계, 여러 클러스터를 연결하는 Cross-Cluster Search까지 다룹니다.

첫 번째 섹션에서는 노드 역할 유형, 클러스터 아키텍처와 마스터 선출, 분산 읽기/쓰기 흐름을 다룹니다. 두 번째 섹션에서는 샤드 크기와 수 결정, Rollover/Shrink/Split/Clone API, Allocation Awareness를 다룹니다. 세 번째 섹션에서는 Cross-Cluster Search 설정과 멀티 리전 시나리오를 다룹니다.

## 이 Phase의 섹션 구성

**5.1 클러스터와 노드**
노드 역할(master-eligible, data, ingest, coordinating 등), 마스터 선출과 split-brain 방지, 분산 읽기/쓰기 흐름을 다룹니다.
- 5.1.1 노드 역할
- 5.1.2 클러스터 아키텍처
- 5.1.3 분산 읽기/쓰기 흐름

**5.2 샤드 전략**
샤드 크기와 수 결정 기준, Rollover/Shrink/Split/Clone API, Allocation Awareness와 랙 인식 분산을 다룹니다.
- 5.2.1 샤드 크기와 수 결정
- 5.2.2 Rollover, Shrink, Split, Clone
- 5.2.3 Allocation Awareness

**5.3 Cross-Cluster Search**
원격 클러스터 등록과 CCS 쿼리 실행, Sniff 모드 vs Proxy 모드, 멀티 리전 데이터 아키텍처 설계를 다룹니다.
- 5.3.1 CCS 설정
- 5.3.2 Sniff 모드 vs Proxy 모드
- 5.3.3 멀티 리전 시나리오
