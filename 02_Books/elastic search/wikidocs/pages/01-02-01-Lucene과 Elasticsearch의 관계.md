# 1.2.1 Lucene과 Elasticsearch의 관계

1.1.1에서 Elasticsearch는 Apache Lucene을 기반으로 만들어진 분산형 검색 엔진이라고 소개했습니다. "Lucene 기반"이라는 표현이 구체적으로 무엇을 뜻하는지, Lucene이 어디까지 담당하고 Elasticsearch가 어디부터 시작하는지를 이해하면 Elasticsearch 내부 동작을 파악하는 데 훨씬 수월해집니다. 이 단원에서는 Lucene이라는 라이브러리의 정체, Elasticsearch가 그 위에 쌓은 기능 계층, 그리고 두 프로젝트의 버전이 어떻게 맞물리는지를 살펴봅니다.

**Apache Lucene**은 Java로 작성된 오픈소스 전문 검색(full-text search) 라이브러리입니다. 여기서 '라이브러리'라는 점이 중요합니다. Lucene은 독립적으로 실행할 수 있는 서버가 아닙니다. 다른 애플리케이션이 Lucene의 Java 클래스를 호출해야 비로소 검색 기능이 작동합니다. 다시 말해, Lucene은 검색 엔진 그 자체가 아니라 검색 기능을 만들기 위한 부품 상자에 해당합니다.

이 부품 상자 안에는 검색에 필요한 핵심 기능이 모두 들어 있습니다. 1.1.1에서 책 뒤의 찾아보기에 비유했던 **역색인**(Inverted Index)이 대표적입니다. 역색인은 단어를 키로, 그 단어가 등장하는 문서 ID 목록을 값으로 저장하는 자료구조입니다.

Lucene의 역색인은 내부적으로 두 가지 핵심 구성 요소로 나뉩니다. 첫째는 **Term Dictionary**입니다. 인덱싱된 모든 고유 단어를 정렬하여 보관하며, FST(Finite State Transducer)라는 자료구조를 사용해 메모리를 절약하면서도 빠른 조회를 가능하게 합니다.

둘째는 **Posting List**입니다. 각 단어에 대해 그 단어가 등장하는 문서 ID, 등장 횟수(Term Frequency), 위치 정보, 오프셋 등을 기록합니다. Posting List는 델타 인코딩(delta encoding)으로 압축하여 디스크와 메모리 사용량을 줄이고, 스킵 리스트(skip list)를 활용하여 여러 Posting List 간의 교집합과 합집합 연산을 빠르게 처리합니다.

역색인 외에도 Lucene은 **쿼리 파서**(Query Parser)를 제공합니다. 사용자가 입력한 텍스트 형태의 검색어를 분석하여 내부 Query 객체로 변환하는 역할입니다. 예를 들어 "무선 키보드"라는 검색어가 들어오면, Lucene의 쿼리 파서는 이를 TermQuery나 BooleanQuery 같은 내부 객체로 바꿉니다. Elasticsearch의 Query DSL은 이 과정을 JSON 형태의 API로 감싼 것입니다. 즉 사용자가 JSON으로 작성한 쿼리는 최종적으로 Lucene의 Query 객체로 변환되어 실행됩니다.

검색 결과의 순서를 정하는 **스코어링**(Scoring)도 Lucene이 담당합니다. Lucene은 기본 알고리즘으로 **BM25**(Best Match 25)를 사용합니다. BM25는 두 가지 요소를 핵심으로 삼습니다. 하나는 검색 단어가 해당 문서에 얼마나 자주 등장하는지(Term Frequency)이고, 다른 하나는 그 단어가 전체 문서 집합에서 얼마나 드문지(Inverse Document Frequency)입니다. 자주 등장하되 흔하지 않은 단어일수록 높은 점수를 받습니다. BM25 이전에는 TF-IDF라는 알고리즘이 기본값이었는데, TF-IDF는 단어 빈도가 높아질수록 점수가 한계 없이 증가하는 문제가 있었습니다. BM25는 단어 빈도에 포화 곡선을 적용하여 일정 횟수 이상 반복되어도 점수 증가가 둔화되도록 개선했습니다. 또한 문서 길이를 정규화하여 짧은 문서가 부당하게 높은 점수를 받는 것을 방지합니다. Elasticsearch 5.0부터 BM25가 기본 스코어링 알고리즘이 되었습니다.

Lucene은 역색인, 쿼리 파서, 스코어링 외에도 여러 보조 자료구조를 제공합니다. 정렬이나 집계에 사용하는 컬럼 지향 저장소인 Doc Values, 원본 문서 내용을 보관하는 Stored Fields, 숫자나 날짜, 지리 좌표의 범위 검색을 빠르게 처리하는 BKD Tree 등이 대표적입니다. 이처럼 Lucene 하나만으로도 텍스트 색인, 검색, 점수 산출, 정렬에 필요한 기능은 거의 갖추고 있습니다.

그렇다면 Lucene만으로 충분한데 Elasticsearch는 왜 필요할까요. Lucene에는 근본적인 한계가 하나 있습니다. Lucene은 단일 머신에서 동작하는 라이브러리라는 점입니다. 데이터가 한 대의 서버 디스크에 다 담길 수 있고, 처리량도 한 대의 CPU로 충당할 수 있다면 Lucene만으로 문제가 없습니다. 그러나 데이터가 수십 테라바이트 규모로 커지거나, 초당 수천 건의 검색 요청을 감당해야 하는 상황에서는 여러 서버에 데이터를 나누어 저장하고 검색을 동시에 수행해야 합니다. Lucene 자체에는 이러한 분산 처리 기능이 없습니다.

Elasticsearch는 Lucene 위에 분산 처리 계층을 올려 이 한계를 해결합니다. 여러 노드에 걸쳐 데이터를 자동으로 분산 배치하고, 복제본(레플리카)을 관리하며, 검색 요청이 들어오면 관련된 모든 노드에 쿼리를 보내 결과를 합칩니다. 이 과정은 두 단계로 나뉩니다. 먼저 Query Phase에서 각 샤드가 자신의 데이터를 검색하여 상위 문서 ID와 점수를 반환합니다. 이어서 Fetch Phase에서 선별된 문서의 전체 내용을 가져옵니다. 쓰기 작업도 분산됩니다. 문서를 인덱싱하면 요청을 받은 Coordinating Node가 해당 문서가 속할 Primary Shard를 결정하고, Primary Shard에 기록한 뒤 Replica Shard로 복제합니다.

```
검색 요청 처리 흐름 (2단계)

1. Query Phase
   클라이언트 --> Coordinating Node --> 각 Shard에 쿼리 전송
                                        각 Shard: Lucene 검색 실행
                                        각 Shard --> Coordinating Node로 (문서ID, 점수) 반환

2. Fetch Phase
   Coordinating Node: 점수 기준 상위 문서 선별
   Coordinating Node --> 해당 Shard에 문서 본문 요청
                         해당 Shard --> 문서 본문 반환
   Coordinating Node --> 클라이언트에 최종 결과 전달
```

Lucene은 Java 라이브러리이므로 Java 코드에서만 호출할 수 있습니다. Elasticsearch는 HTTP 기반의 **REST API**를 추가하여 프로그래밍 언어에 상관없이 JSON으로 요청을 주고받을 수 있게 했습니다. 1.1.1에서 살펴본 PUT, GET, POST, DELETE 요청이 바로 이 REST API입니다. Query DSL도 마찬가지입니다. Lucene의 Query 객체를 직접 다루는 대신, JSON 형태로 쿼리를 작성하면 Elasticsearch가 이를 Lucene Query 객체로 변환하여 실행합니다. 이 덕분에 사용자는 Lucene의 Java API를 알지 못해도 검색 기능을 활용할 수 있습니다.

클러스터 운영에 필요한 관리 기능도 Elasticsearch가 추가한 영역입니다. 여러 노드 중에서 클러스터 전체 상태를 관리할 마스터 노드를 선출하고, 새로운 노드가 합류하거나 기존 노드가 이탈할 때 샤드를 재배치합니다. 노드를 역할별로 분리하는 것도 가능합니다. 마스터 역할만 수행하는 노드, 데이터를 저장하는 노드, 인덱싱 전에 데이터를 가공하는 인제스트 노드, 요청을 분배하는 코디네이팅 노드 등으로 나눌 수 있습니다. 클러스터 상태 모니터링을 위한 _cluster/health API, 무중단 버전 업그레이드를 위한 롤링 업그레이드 절차 등 운영에 필요한 기능도 Elasticsearch 계층에서 제공합니다.

**집계**(Aggregation)도 Elasticsearch가 Lucene 위에 구현한 대표적인 기능입니다. Lucene에는 집계라는 개념 자체가 없습니다. Lucene이 할 수 있는 것은 조건에 맞는 문서를 찾아 점수를 매기는 것까지입니다. 그 결과를 그룹별로 묶고, 합산하고, 평균을 내는 작업은 Elasticsearch가 Lucene의 검색 결과 위에서 수행합니다.

Lucene과 Elasticsearch의 역할 분담을 정리하면 다음과 같습니다.

```
+-------------------------------------------------------+
|                  Elasticsearch 계층                     |
|                                                       |
|   분산 처리 (샤딩, 레플리케이션, 쿼리 팬아웃)            |
|   REST API (HTTP + JSON)                              |
|   Query DSL (JSON -> Lucene Query 변환)               |
|   클러스터 관리 (마스터 선출, 샤드 할당, 모니터링)        |
|   집계 (Aggregation)                                   |
|   인제스트 파이프라인                                    |
+-------------------------------------------------------+
|                   Lucene 계층                           |
|                                                       |
|   역색인 (Term Dictionary + Posting List)              |
|   쿼리 파서 (텍스트 -> Query 객체)                      |
|   스코어링 (BM25)                                      |
|   보조 자료구조 (Doc Values, Stored Fields, BKD Tree)  |
|   세그먼트 관리 (불변 세그먼트 생성, 병합)               |
+-------------------------------------------------------+
```

아래쪽 Lucene 계층이 한 대의 머신에서 텍스트를 색인하고 검색하고 점수를 매기는 역할을 맡고, 위쪽 Elasticsearch 계층이 이를 여러 대의 머신으로 확장하고 외부에서 접근할 수 있는 API를 제공하는 역할을 맡습니다.

이 구조에서 핵심 연결 고리가 **샤드**(Shard)입니다. 1.1.1에서 샤드를 인덱스를 나누는 단위로 소개했는데, 내부를 들여다보면 하나의 샤드는 곧 하나의 완전한 Lucene 인덱스 인스턴스입니다. 여기서 혼동하기 쉬운 점이 있습니다. Elasticsearch에서 말하는 '인덱스'와 Lucene에서 말하는 '인덱스'는 서로 다른 층위의 개념입니다. Elasticsearch 인덱스는 논리적인 이름 공간(예: 'products')이고, Lucene 인덱스는 역색인과 세그먼트 파일을 실제로 보유한 물리적인 검색 단위입니다. Elasticsearch 인덱스 하나는 여러 샤드로 구성되고, 각 샤드가 독립적인 Lucene 인덱스 하나와 1:1로 대응합니다.

```
Elasticsearch Index "products" (논리적 이름 공간)
  |
  +-- Shard 0  =  Lucene Index 인스턴스 (IndexWriter + IndexSearcher)
  |                 +-- Segment 0 (불변)
  |                 +-- Segment 1 (불변)
  |                 +-- ...
  |
  +-- Shard 1  =  Lucene Index 인스턴스
  |                 +-- Segment 0
  |                 +-- ...
  |
  +-- Shard 2  =  Lucene Index 인스턴스
                    +-- Segment 0
                    +-- ...
```

각 샤드, 즉 각 Lucene 인덱스 인스턴스는 자체적으로 **IndexWriter**와 **IndexSearcher**를 보유합니다. IndexWriter는 문서를 받아 역색인을 생성하고 세그먼트 파일을 기록하는 역할을 합니다. IndexSearcher는 세그먼트를 열어 쿼리를 실행하고 결과를 반환하는 역할을 합니다. 이 두 객체가 있으므로 각 샤드는 다른 샤드의 도움 없이 독립적으로 인덱싱과 검색을 수행할 수 있습니다. Elasticsearch가 하나의 논리 인덱스를 여러 샤드로 나누는 이유는 단일 Lucene 인스턴스가 가진 제약, 즉 한 대 서버의 디스크 용량과 CPU 처리량을 분산으로 넘어서기 위해서입니다.

Lucene 인덱스 안에는 하나 이상의 **세그먼트**(Segment)가 존재합니다. 세그먼트는 역색인, Doc Values, Stored Fields, BKD Tree 등이 기록된 불변(immutable) 파일 집합입니다. 한 번 기록된 세그먼트는 수정되지 않습니다. 새 문서가 들어오면 기존 세그먼트를 고치는 것이 아니라 새로운 세그먼트가 만들어집니다. 시간이 지나면 작은 세그먼트 여러 개가 하나의 큰 세그먼트로 병합(merge)됩니다. 1.1.1에서 설명한 refresh 주기마다 메모리 버퍼의 내용이 새 세그먼트로 기록되는 것이 바로 이 과정입니다.

마지막으로, Lucene과 Elasticsearch의 버전 관계를 살펴봅니다. Elasticsearch의 주요(major) 버전은 특정 Lucene 주요 버전과 짝을 이룹니다.

| Elasticsearch 버전 | Lucene 버전 |
|--------------------|-------------|
| ES 1.x             | Lucene 4.x  |
| ES 2.x             | Lucene 5.x  |
| ES 5.x             | Lucene 6.x  |
| ES 6.x             | Lucene 7.x  |
| ES 7.x             | Lucene 8.x  |
| ES 8.x             | Lucene 9.x  |
| ES 9.x             | Lucene 10.x |

이 대응이 중요한 이유는 Lucene 버전이 올라가면 인덱스 파일의 저장 형식(코덱)이 바뀔 수 있기 때문입니다. 예를 들어 ES 6.x에서 작성한 인덱스 파일은 Lucene 7.x 코덱으로 기록되어 있으므로, Lucene 9.x 코덱을 사용하는 ES 8.x에서는 이 파일을 직접 읽을 수 없습니다. 따라서 ES 메이저 버전 업그레이드 시에는 반드시 한 단계씩 거쳐야 합니다. ES 6.x에서 곧바로 8.x로 건너뛸 수 없고, 6.x에서 7.x로 먼저 업그레이드한 뒤 7.x에서 8.x로 진행해야 합니다. 경우에 따라 인덱스를 새로운 코덱으로 다시 색인(재색인)하는 작업이 필요하기도 합니다.

정리하면, Lucene은 역색인, 쿼리 파서, BM25 스코어링 등 검색의 핵심 기능을 제공하는 단일 머신용 Java 라이브러리이고, Elasticsearch는 이 Lucene을 분산 환경에서 운용할 수 있도록 분산 처리, REST API, 클러스터 관리, 집계 기능을 추가한 시스템입니다. 양자의 물리적 연결 지점이 샤드이며, 하나의 ES 샤드는 정확히 하나의 Lucene 인덱스 인스턴스와 1:1로 대응합니다.

다음 단원인 1.2.2에서는 역색인 동작 원리를 다룹니다.

이 단원을 마치면 Lucene이 Elasticsearch의 핵심 검색 엔진임을 설명할 수 있고, Elasticsearch가 Lucene 위에 추가한 기능 계층을 열거할 수 있습니다.
