# 1.2 핵심 원리: Lucene과 역색인

이 섹션에서는 Elasticsearch 검색 성능의 근간이 되는 Apache Lucene과 역색인 구조를 다룹니다. 이 원리를 이해하면 매핑 설계, 성능 최적화, 장애 진단 등 이후의 모든 주제가 훨씬 명확하게 연결됩니다.

## 토픽 목록

**1.2.1 Lucene과 Elasticsearch의 관계**
- Lucene이 Elasticsearch의 핵심 검색 엔진임을 설명할 수 있다
- Elasticsearch가 Lucene 위에 추가한 기능 계층을 열거할 수 있다

Apache Lucene 라이브러리의 역할, Lucene 인덱스와 ES 샤드의 1:1 관계, Lucene이 제공하는 역색인·쿼리 파서·스코어링 기능, Elasticsearch가 추가한 분산 처리·REST API·클러스터 관리 기능을 다룹니다.

**1.2.2 역색인 동작 원리**
- 역색인(inverted index)의 구조와 구축 과정을 다이어그램으로 설명할 수 있다
- 전방 색인과 역색인의 차이를 비교할 수 있다

전방 색인과 역색인의 차이, 토큰화(tokenization) 과정, 텀 딕셔너리(term dictionary)와 포스팅 리스트(posting list), 문서 빈도(DF)와 텀 빈도(TF), 역색인의 불변성(immutability)을 다룹니다.

**1.2.3 세그먼트 계층 구조**
- 세그먼트가 생성되고 병합되는 과정을 설명할 수 있다
- 세그먼트 수가 검색 성능에 미치는 영향을 설명할 수 있다

Lucene 세그먼트의 개념, 세그먼트 불변성, 세그먼트 병합(merge) 정책, 삭제 마킹과 .del 파일, force merge API, 세그먼트 수와 검색 성능 트레이드오프, 인메모리 버퍼와 디스크 플러시를 다룹니다.

**1.2.4 NRT 검색과 Translog**
- Near Real-Time 검색의 동작 원리를 설명할 수 있다
- Translog의 역할과 내구성 보장 방식을 설명할 수 있다

NRT(Near Real-Time) 개념, refresh 주기(index.refresh_interval), 인메모리 세그먼트와 파일시스템 캐시, Translog와 WAL(Write-Ahead Log), flush와 fsync, Translog 크기와 복구 시간 트레이드오프를 다룹니다.
