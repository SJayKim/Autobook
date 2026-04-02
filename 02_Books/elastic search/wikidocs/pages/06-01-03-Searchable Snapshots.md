# 6.1.3 Searchable Snapshots

6.1.2에서 다룬 Data Stream과 ILM 정책을 통해 인덱스는 Hot에서 Warm, Cold로 자동 전환됩니다. 그런데 Cold 티어 이후에도 데이터를 삭제하지 않고 보관해야 하는 경우가 있습니다. 규정상 몇 년치 로그를 유지해야 하거나, 드물지만 과거 데이터를 검색해야 하는 상황입니다. 이런 데이터를 모두 로컬 디스크에 두면 스토리지 비용이 크게 늘어납니다.

**Searchable Snapshot**은 스냅샷 형태로 외부 저장소에 보관된 데이터를 삭제하지 않고 직접 검색할 수 있게 해 주는 기능입니다. 일반적인 스냅샷은 백업 목적이므로, 검색하려면 먼저 클러스터에 복구(restore)해야 합니다. Searchable Snapshot은 복구 없이 스냅샷 데이터를 바로 검색합니다. 데이터 원본이 외부 저장소(S3, GCS, Azure Blob 등)에 있으므로, 로컬 디스크 사용량을 크게 줄일 수 있습니다.

Searchable Snapshot은 주로 Cold 티어와 Frozen 티어에서 사용합니다. 두 티어의 차이를 이해하는 것이 중요합니다.

**Cold 티어**에서는 전체 마운트(full mount) 방식을 사용합니다. 스냅샷 데이터의 전체 사본을 로컬 노드에 캐싱합니다. 첫 번째 검색 시 외부 저장소에서 데이터를 가져와 로컬에 저장하고, 이후 검색은 로컬 캐시에서 처리합니다. 레플리카가 필요 없습니다. 장애가 발생해도 외부 저장소의 스냅샷에서 다시 복원할 수 있기 때문입니다. 레플리카를 제거하는 것만으로도 스토리지 사용량이 절반으로 줄어듭니다.

**Frozen 티어**에서는 부분 마운트(partial mount) 방식을 사용합니다. 로컬 노드에 전체 데이터를 저장하지 않고, 검색에 필요한 부분만 외부 저장소에서 가져옵니다. 로컬에는 최근 접근한 데이터의 캐시만 유지합니다. 디스크 사용량이 극히 적은 대신, 검색 속도는 Cold 티어보다 느립니다. 거의 조회하지 않는 아카이브 데이터에 적합합니다.

```
┌─────────────────────────────────────────────────────────┐
│                    외부 스냅샷 저장소                      │
│                  (S3, GCS, Azure Blob)                   │
└───────────────┬──────────────────────┬──────────────────┘
                │                      │
     전체 사본 캐싱               필요한 부분만 요청
                │                      │
        ┌───────▼────────┐     ┌───────▼────────┐
        │   Cold 티어     │     │  Frozen 티어    │
        │  (full mount)  │     │ (partial mount) │
        │  로컬 전체 캐시  │     │  로컬 일부 캐시  │
        │  레플리카 불필요  │     │  최소 디스크     │
        └────────────────┘     └────────────────┘
```

Searchable Snapshot을 사용하려면 먼저 스냅샷 저장소를 등록해야 합니다. 저장소는 S3, Google Cloud Storage(GCS), Azure Blob Storage, 또는 공유 파일시스템 중 하나를 사용할 수 있습니다. 예를 들어 S3 저장소를 등록하는 방법은 다음과 같습니다.

```json
PUT _snapshot/my_s3_repository
{
  "type": "s3",
  "settings": {
    "bucket": "my-es-snapshots",
    "region": "ap-northeast-2"
  }
}
```

type은 저장소 종류를 지정합니다. bucket은 S3 버킷 이름이고, region은 버킷이 위치한 리전입니다. S3 인증 정보는 Elasticsearch 키스토어에 미리 등록해 두어야 합니다.

저장소가 등록되면 스냅샷을 생성하고, 해당 스냅샷을 Searchable Snapshot으로 마운트할 수 있습니다. mount API를 사용합니다.

```json
POST _snapshot/my_s3_repository/my_snapshot/_mount
{
  "index": "logs-2023.01",
  "renamed_index": "restored-logs-2023.01",
  "index_settings": {
    "index.number_of_replicas": 0
  }
}
```

이 요청은 my_snapshot 스냅샷 안의 logs-2023.01 인덱스를 restored-logs-2023.01이라는 이름으로 마운트합니다. 기본적으로 전체 마운트(Cold 티어용)가 됩니다. 부분 마운트를 사용하려면 storage 파라미터를 추가합니다.

```json
POST _snapshot/my_s3_repository/my_snapshot/_mount?storage=shared_cache
{
  "index": "logs-2023.01"
}
```

storage=shared_cache를 지정하면 Frozen 티어의 부분 마운트 방식으로 동작합니다. 이 경우 노드의 로컬 캐시 크기를 설정해야 합니다. elasticsearch.yml에서 xpack.searchable.snapshot.shared_cache.size 값을 지정합니다. 일반적으로 노드 디스크 용량의 일부를 캐시로 할당합니다.

수동으로 mount API를 호출하는 대신, ILM 정책의 cold 또는 frozen 페이즈에 searchable_snapshot 액션을 설정하면 자동화할 수 있습니다. 6.1.1에서 만든 ILM 정책에 다음과 같이 추가합니다.

```json
"cold": {
  "min_age": "90d",
  "actions": {
    "searchable_snapshot": {
      "snapshot_repository": "my_s3_repository"
    }
  }
},
"frozen": {
  "min_age": "180d",
  "actions": {
    "searchable_snapshot": {
      "snapshot_repository": "my_s3_repository"
    }
  }
}
```

cold 페이즈에서는 전체 마운트가 적용되고, frozen 페이즈에서는 부분 마운트가 자동으로 적용됩니다. ILM이 각 페이즈 전환 시 자동으로 스냅샷을 생성하고 마운트하므로, 관리자가 개입하지 않아도 됩니다.

정리하면, Searchable Snapshot은 외부 저장소의 스냅샷 데이터를 복구 없이 직접 검색할 수 있게 해 주는 기능입니다. Cold 티어에서는 전체 마운트로 로컬에 데이터를 캐싱하고, Frozen 티어에서는 부분 마운트로 필요한 데이터만 가져옵니다. ILM 정책에 searchable_snapshot 액션을 설정하면 데이터 티어링이 자동화되어, 검색 가능성을 유지하면서도 스토리지 비용을 크게 절감할 수 있습니다.

다음 단원인 6.2.1에서는 Logstash를 다룹니다. Elasticsearch로 데이터를 보내기 전에 수집과 변환을 담당하는 파이프라인 도구를 알아봅니다.

이 단원을 마치면 Searchable Snapshot으로 Cold/Frozen 티어를 구성하여 스토리지 비용을 절감할 수 있습니다.
