# 5.2.5 Metadata filtering과 Citation

검색이 의미만 본다면 같은 의미의 청크가 잔뜩 잡힐 뿐이고, 그 청크가 권한 밖 문서이거나 1년 전 폐기된 정책이라면 시스템은 그럴듯한 잘못된 답을 내놓습니다. 답이 어느 문서 어느 페이지에 기반했는지도 표시되지 않으면 사용자는 그 답을 검증할 수 없습니다. 이 단원은 검색 단계에 메타데이터 필터를 더해 범위를 좁히고, 생성 단계에서 인용을 강제해 hallucination을 줄이는 방법을 다룹니다.

먼저 **메타데이터 스키마**부터 짚겠습니다. 청크와 함께 저장해 두면 운영에 가장 자주 쓰이는 필드는 다음과 같습니다. 출처 식별을 위한 doc_id, page, section_path, 권한 통제를 위한 acl, 신선도 통제를 위한 created_at, updated_at, valid_from, valid_until, 분류와 검색 보조를 위한 doc_type, tags, language, 그리고 운영을 위한 embedding_model, embedding_version입니다. 이 필드들은 청크를 인덱싱할 때 한 번 채워 두면 검색에서 자유롭게 조합해 쓸 수 있고, 빠뜨리면 나중에 보강하기 위해 다시 인덱싱해야 합니다.

| 필드 | 예시 | 쓰임 |
|---|---|---|
| doc_id | "policy-2024-12" | 출처 표시, 중복 제거 |
| page | 17 | citation에 표기 |
| section_path | "환불/디지털상품" | reranker 보조, citation |
| acl | ["team:finance"] | 권한 필터 |
| valid_from~until | 2024-01-01~2025-12-31 | 신선도 필터 |
| doc_type | "policy", "code" | 도메인별 필터 |
| tags | ["refund","digital"] | 사용자 facet |

메타데이터를 검색에 끼우는 시점은 두 가지입니다. **Pre-filter**는 벡터 검색 전에 메타데이터 조건을 먼저 적용해 후보 집합을 좁히고 그 안에서 유사도를 잽니다. **Post-filter**는 벡터 검색 결과에서 조건 미충족 청크를 떨어냅니다. 후자는 단순하지만 조건이 강하면 top-k가 거의 비는 사고가 잦아, 권한이 들어간 RAG는 사실상 pre-filter가 강제 선택입니다. Qdrant·Weaviate·Milvus가 payload 인덱스 위 pre-filter를 지원하고, pgvector는 SQL WHERE로 자연스럽게 구현됩니다.

```python
# Qdrant pre-filter 예시
res = qclient.query_points(
    collection_name="docs",
    query=q_vec,
    query_filter=Filter(
        must=[
            FieldCondition(key="acl", match=MatchAny(any=user_groups)),
            FieldCondition(key="valid_until", range=Range(gte=today)),
        ]
    ),
    limit=50,
)
```

작은 사례로 보면, 한 사내 RAG가 인사팀과 영업팀 정책을 한 인덱스에 함께 두었더니 영업팀 사용자가 'A고객사 환불 절차'를 물었을 때 인사팀 휴가 환불 청크가 top-3에 섞여 답이 엉뚱한 방향으로 흘렀습니다. acl을 pre-filter로 강제한 뒤 답이 영업 정책으로 수렴했습니다. 신선도도 같은 양상이라, valid_until >= today를 항상 거는 운영이 폐기 정책 노출을 막아 줍니다.

이제 **citation**으로 넘어가겠습니다. Citation은 답변 안에 어떤 청크를 근거로 썼는지 표시하는 단계입니다. 단순히 마지막에 출처 목록을 늘어놓는 것이 아니라, 답의 각 주장에 출처 번호를 매기는 형태가 가장 강력합니다. 다음 예시가 표준 모양입니다.

```
A: 디지털 상품은 다운로드 이후 환불이 불가합니다 [1].
   단, 결제 후 24시간 안에 다운로드 이력이 없으면 전액 환불됩니다 [2].

[1] policy-2024-12, p.17 (환불/디지털상품)
[2] policy-2024-12, p.18 (환불/디지털상품)
```

이 표시를 강제하는 길은 두 가지입니다. 하나는 **프롬프트 강제**로, 각 청크를 [1], [2]처럼 번호와 함께 모델에 넣고 '근거가 되는 청크 번호를 답안 안에 표기하라'를 시스템 메시지로 줍니다. 다른 하나는 **structured output 강제**로, 답변을 {answer, citations: [{n, doc_id, page}]}처럼 JSON 스키마로 받아 구조적 무결성을 검증합니다. 두 방식 모두 100%는 아니지만, structured output 쪽이 후처리에서 자동 검증과 차단이 가능해 운영에 적합합니다.

Citation이 hallucination을 줄이는 원리는 단순합니다. 모델이 답의 각 문장 옆에 출처 번호를 붙여야 한다고 강제하면, 자기가 만든 정보를 함부로 적기 어려워집니다. 출처 번호가 없는 문장은 사실상 hallucination 후보이고, 후처리에서 그 부분을 잘라내거나 '근거 부족'으로 표시할 수 있습니다.

여기에 한 단계 더 강한 장치가 있습니다. **저신뢰 답변 거부**입니다. Reranker의 top-1 점수가 일정 임계값(예: BGE-reranker-v2-m3에서 -2.0) 아래로 떨어지면 답을 만들지 않고 'I don't know'를 반환하는 흐름입니다. 검색이 정답 청크를 못 찾았을 때 모델이 억지로 답을 만드는 가장 흔한 hallucination 경로를 차단합니다.

전체 흐름을 한 그림으로 모으면 다음과 같습니다.

```
질문 + 사용자 정보(acl, 시점)
        |
        v
[Hybrid 검색 + Pre-filter]
   (acl, valid_until, doc_type 같은 조건을 인덱스에 함께 건다)
        |
        v
[Reranker]
   - top-1 점수가 임계값 미만? -> "근거 부족" 응답으로 종료
        |
        v
[Generator]
   - 청크에 [1], [2] 번호 부여
   - structured output으로 {answer, citations} 강제
        |
        v
[Post-validation]
   - citations의 doc_id가 실제 후보에 있는가
   - answer의 각 문장에 citation이 붙어 있는가
        |
        v
사용자에게 답 + 출처 링크
```

마지막 후처리 단계에서 자주 빠뜨리는 것이 **출처 진위 검증**입니다. 모델이 [1] 번호를 붙여도 실제로 그 청크가 답을 뒷받침하지 않을 수 있어, 정답 문장과 인용 청크의 의미 유사도를 다시 재거나 LLM-as-judge로 '각 주장이 [n]으로 뒷받침되는가'를 채점합니다. 한 팀이 citation 강제 전후의 hallucination을 LLM-as-judge로 측정해 18%에서 7%로 떨어진 사례가 있는데, 같은 모델·같은 검색 설정에서 답안 형식만 바꾼 결과였습니다.

정리하면, 메타데이터는 청크와 함께 권한·신선도·분류 정보를 저장해 두는 자리이고, pre-filter로 검색 범위를 좁히면 권한 누수와 폐기 정책 노출을 한 번에 막을 수 있습니다. Citation은 답에 출처 번호를 강제로 붙이는 장치로, structured output과 결합하면 자동 검증이 가능하고 hallucination을 큰 폭으로 줄입니다. Reranker의 점수 임계값으로 저신뢰 응답을 거부하면 마지막 안전망이 추가됩니다.

다음 단원인 5.3.1에서는 청크와 메타데이터만으로는 다루기 어려운 관계 데이터를 위한 GraphRAG와 KG-RAG의 기본 개념으로 들어갑니다.
