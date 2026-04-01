# 5.3 Cross-Cluster Search

이 섹션에서는 여러 Elasticsearch 클러스터를 연결하여 단일 쿼리로 검색하는 Cross-Cluster Search(CCS)를 다룹니다. 원격 클러스터 연결 방법, 네트워크 모드 선택, 그리고 멀티 리전 아키텍처에서의 활용 패턴을 익힙니다.

## 토픽 목록

**5.3.1 CCS 설정**
- 원격 클러스터를 등록하고 cross-cluster search 쿼리를 실행할 수 있다

원격 클러스터 등록(cluster.remote 설정), cluster_uuid와 식별, CCS 쿼리 문법({cluster}:{index}), skip_unavailable 설정, CCS 응답의 _clusters 필드 해석, CCS 권한 설정(Remote Cluster API Key), CCS와 스코어 정규화 주의를 다룹니다.

**5.3.2 Sniff 모드 vs Proxy 모드**
- Sniff 모드와 Proxy 모드의 네트워크 접근 방식 차이를 설명할 수 있다
- 방화벽 환경에서 Proxy 모드를 적용할 수 있다

Sniff 모드(노드 목록 자동 발견), Proxy 모드(고정 게이트웨이), Sniff 모드 방화벽 문제, Proxy 모드 설정(proxy_address, server_name), TLS와 CCS 연동, CCS 성능 고려사항(네트워크 레이턴시)을 다룹니다.

**5.3.3 멀티 리전 시나리오**
- 멀티 리전 데이터 아키텍처에서 CCS 활용 패턴을 설계할 수 있다

리전별 클러스터 분리 이유(레이턴시, 규제), CCS 기반 중앙 집계 패턴, CCR(Cross-Cluster Replication)과 CCS 비교, Active-Passive DR 구성, 멀티 리전 인덱싱 전략, CCS 지연 시간 SLA 고려사항을 다룹니다.
