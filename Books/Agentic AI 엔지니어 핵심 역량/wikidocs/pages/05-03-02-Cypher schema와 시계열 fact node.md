# 5.3.2 Cypher schema와 시계열 fact node

KG의 가치를 결정하는 것은 스키마입니다. 단순한 두 점 사이의 관계만으로는 시간에 따라 변하는 사실을 담을 수 없고, 사실이 충돌하거나 갱신될 때 KG가 빠르게 어지러워집니다. 이 단원은 Neo4j와 Cypher의 기본 모양, **fact node** 패턴, 그리고 갱신 충돌을 다루는 운영 원칙을 정리합니다.

먼저 **Cypher**의 기본 형태를 보겠습니다. Cypher는 Neo4j의 질의 언어로, 그래프를 그림 그리듯이 패턴을 쓰는 방식입니다. 노드는 괄호 안에 라벨로, 관계는 대괄호 안에 타입으로 표현합니다.

```cypher
CREATE (a:Company {id:"A"})-[:ACQUIRED {year:2023}]->(b:Company {id:"B"})

MATCH (a:Company)-[r:ACQUIRED]->(b:Company)
WHERE r.year >= 2023
RETURN a.name, b.name, r.year
```

라벨(Company)은 노드의 종류, 타입(ACQUIRED)은 관계의 종류, 양쪽에 속성(property)을 자유롭게 붙일 수 있습니다. SQL로 같은 일을 하려면 두 테이블을 조인해야 하지만, Cypher는 패턴을 늘려 두 단계, 세 단계 관계 추적까지 자연스럽게 표현합니다.

KG 설계의 세 축은 **Entity, Relationship, Property**입니다. Entity는 실세계의 사물을 표현하는 노드, Relationship은 두 엔티티 사이의 엣지, Property는 노드나 엣지에 붙는 속성입니다. 일반적인 권고는 **변하지 않는 정보는 property로, 시간에 따라 변하거나 여러 번 일어나는 사건은 별도 노드로** 두는 것입니다. 이 권고가 fact node 패턴의 출발점입니다.

'직원이 부서에 근무한다'를 단순 엣지 `(e:Employee)-[:WORKS_AT]->(d:Department)`로 두면 처음에는 깔끔합니다. 그러나 사람은 부서를 옮깁니다. 옮길 때마다 엣지를 지우면 과거 근무 이력이 사라지고, 그대로 두면 한 사람이 두 부서에 동시에 근무하는 모순이 생깁니다. 시작과 종료 시각을 엣지 속성에 박아도 한 엣지에 여러 기간이 들어가는 일을 표현하기 어렵습니다.

해법이 **fact node**입니다. 사실 자체를 노드로 승격시키고, 관련 엔티티들과 시간 정보를 그 노드의 엣지·속성으로 연결합니다.

```cypher
(e:Employee)-[:HAS_ROLE]->(r:Role {
    title:"Manager",
    valid_from:"2023-01-01",
    valid_until:"2024-06-30",
    source_chunk:"hr-2023-q1#42"
})-[:IN]->(d:Department)
```

`Role`이라는 fact node가 직원과 부서 사이의 '근무 사실'을 한 단위로 표현합니다. 부서를 옮기면 새 Role 노드를 만들고, 현재 사실은 valid_until이 비어 있거나 미래 시점인 노드로 식별합니다.

같은 발상을 회사 인수, 가격 변경, 정책 개정 같은 **시간에 의존하는 모든 사실**로 일반화할 수 있습니다. fact node의 표준 속성은 다음과 같습니다.

| 속성 | 의미 | 예 |
|---|---|---|
| valid_from | 사실의 시작 | "2023-01-01" |
| valid_until | 사실의 종료(없으면 현재 진행) | "2024-06-30" |
| asserted_at | KG에 기록된 시각 | "2024-07-02T10:00" |
| source_chunk | 근거 청크 id | "policy-2024#17" |
| confidence | 추출 신뢰도 | 0.92 |

`valid_from~until`은 사실의 시간 범위, `asserted_at`은 KG가 이 사실을 알게 된 시각입니다. 두 시간 축을 함께 두는 모양을 **bitemporal**이라 부르며, 사실이 잘못 기록되었다가 수정된 경우에도 이력이 보존됩니다.

'2023년 1분기에 김 매니저가 어디서 일했는가'를 묻는 시계열 질의는 다음과 같이 씁니다.

```cypher
MATCH (e:Employee {name:"김지은"})-[:HAS_ROLE]->(r:Role)-[:IN]->(d:Department)
WHERE r.valid_from <= date("2023-03-31")
  AND (r.valid_until IS NULL OR r.valid_until >= date("2023-01-01"))
RETURN d.name, r.title
```

valid_from·until 범위 비교가 모든 시계열 질의의 핵심 패턴이고, 한 번 익히면 fact 종류에 관계없이 재사용할 수 있습니다.

설계 전체를 한 그림으로 모으면 다음과 같습니다.

```
[Entity] -> [Fact (valid_from, valid_until, source_chunk)] -> [Entity]
                         ^
                         |
            시간 인덱스 (valid_from / valid_until)
```

시간 인덱스는 운영에서 매우 중요합니다. valid_from과 valid_until에 인덱스를 걸어 두지 않으면 시계열 범위 질의가 전체 fact를 다 훑게 되어, 노드 100만 단위에서 응답이 초 단위로 떨어집니다.

```cypher
CREATE INDEX fact_valid_from FOR (r:Role) ON (r.valid_from);
CREATE INDEX fact_valid_until FOR (r:Role) ON (r.valid_until);
```

KG 운영에서 가장 자주 만나는 함정이 **업데이트 충돌**입니다. 새 문서가 'A 회사가 2023년 B 회사를 인수했다'고 적었는데, 한 달 뒤 다른 문서가 '실은 2022년에 인수됐다'고 적습니다. 권고는 출처별로 fact 노드를 따로 만들고 status를 부여하는 것입니다. 두 fact 노드가 같은 두 엔티티를 잇되, 하나는 status:"superseded", 다른 하나는 status:"current"가 되고, 시계열 질의는 status 필터를 함께 겁니다. 우선순위는 confidence가 높은 노드 또는 doc_type이 'primary'인 노드를 current로 두는 식으로 정합니다.

운영 흐름을 정리하면 다음과 같습니다.

```
새 문서 -> 청크화 + 엔티티/관계 추출 (LLM)
       -> 기존 엔티티와 동일성 해소 (alias, embedding)
       -> 신규 fact 노드 생성 (valid_*, confidence, source_chunk)
       -> 같은 엔티티 쌍의 기존 fact 조회
            충돌 없음 -> 추가
            충돌 있음 -> confidence·valid 범위로 status 갱신
       -> 인덱스 업데이트, community summary 재계산 예약
```

가장 자주 실수하는 자리는 동일성 해소 단계입니다. 같은 회사를 'Acme', 'Acme Corp.', '에이크미'로 다르게 적었을 때 셋 모두 별 노드로 생기면 KG가 무너집니다. 노드 생성 직전에 임베딩 유사도 + 별칭 규칙을 거치는 후처리를 두는 편이 안전합니다.

fact node 패턴은 청크 RAG와도 자연스럽게 이어집니다. fact 노드의 source_chunk 속성이 근거 청크를 가리키므로, KG로 사실을 찾은 뒤 그 청크를 citation으로 그대로 끌어 쓸 수 있습니다. 사용자에게는 'A 회사가 2023년 B 회사를 인수했습니다 [doc:report-2023-q4 p.12]'처럼 KG의 정확한 사실과 청크의 원문이 함께 제시되어, KG가 정확성을 보장하고 청크가 표현 근거를 보충합니다.

정리하면, Cypher는 노드·관계·속성 세 축으로 그래프를 그리고 질의하는 언어이며, 시간에 따라 변하는 사실은 단순 엣지가 아니라 fact node로 승격시켜야 합니다. fact node에는 valid_from·valid_until·asserted_at·source_chunk·confidence를 두고 시간 인덱스로 시계열 질의를 빠르게 만들며, 충돌은 status와 출처 우선순위로 다루고 동일성 해소를 거쳐 KG가 무너지지 않게 합니다. source_chunk 포인터가 GraphRAG와 청크 RAG의 citation을 자연스럽게 잇습니다.

이 단원으로 Phase 5가 마무리됩니다. 다음 Phase에서는 RAG가 도구·계획·메모리를 거느린 에이전트 아키텍처로 확장되는 길을 다룹니다.
