# 5.1.3 LlamaIndex 핵심 구조

5.1.1에서 LLM 오케스트레이션이 무엇인지, 단순 API 호출만으로는 왜 한계가 있는지를 살펴보았습니다. 오케스트레이션 프레임워크는 LLM 호출 전후의 데이터 흐름을 체계적으로 관리하여, 외부 문서 검색, 응답 후처리, 대화 맥락 유지 같은 복잡한 작업을 하나의 파이프라인으로 엮어 줍니다. 5.1.2에서 다룬 LangChain이 범용적인 체인 구성에 초점을 맞춘다면, 이 단원에서 다루는 **LlamaIndex**는 "외부 데이터를 LLM이 활용할 수 있는 형태로 구조화하고 검색하는 것"에 특화된 프레임워크입니다. 사내 문서, PDF, 데이터베이스 같은 비정형 데이터를 LLM에 연결해야 하는 상황이라면, LlamaIndex가 제공하는 추상화가 그 과정을 크게 단순화합니다.

LlamaIndex가 해결하려는 문제를 먼저 짚어 보겠습니다. LLM은 사전훈련 시점까지의 지식만 갖고 있습니다. 조직 내부 문서나 최신 데이터에 대해서는 답할 수 없고, 질문을 받으면 사실과 다른 내용을 생성하는 환각이 발생하기 쉽습니다. 이 문제를 해결하는 대표적인 방법이 4단원에서 다룬 RAG(Retrieval-Augmented Generation)입니다. RAG의 핵심은 사용자 질문과 관련된 문서 조각을 먼저 검색하고, 그 조각을 프롬프트에 첨부하여 LLM이 근거 있는 답변을 생성하도록 유도하는 것입니다. LlamaIndex는 바로 이 RAG 파이프라인을 구축하는 데 필요한 도구를 한데 묶어 제공합니다. 문서를 읽어 들이고, 적절한 크기로 나누고, 임베딩하여 인덱스에 저장하고, 질문이 들어오면 관련 조각을 검색하여 LLM에 전달하는 전 과정을 일관된 인터페이스로 처리합니다.

LlamaIndex의 전체 아키텍처는 크게 다섯 단계로 나뉩니다. 데이터 로딩, 데이터 변환, 인덱싱, 검색, 질의 응답입니다. 각 단계에는 전용 추상화 객체가 있어서, 개발자는 단계별로 필요한 부분만 교체하거나 확장할 수 있습니다. 아래 다이어그램은 이 흐름을 보여줍니다.

```
LlamaIndex 데이터 파이프라인 전체 흐름

원본 데이터        데이터 변환           인덱싱             질의
(PDF, DB 등)
     |                |                  |                 |
     v                v                  v                 v
+---------+    +------------+    +---------------+    +------------+
| Reader  | -> | Document   | -> | Index         | -> | Query      |
| (로더)  |    | -> Node    |    | (벡터, 요약,  |    | Engine     |
|         |    |   분할/변환 |    |  지식그래프)  |    |            |
+---------+    +------------+    +---------------+    +------------+
                                       |                    |
                                       v                    v
                                 +-----------+        +-----------+
                                 | Retriever |   ->   | LLM 호출  |
                                 | (검색기)  |        | + 응답생성 |
                                 +-----------+        +-----------+
```

첫 번째 단계는 데이터 로딩입니다. LlamaIndex는 다양한 데이터 소스에서 문서를 읽어 들이는 Reader(로더)를 제공합니다. PDF 파일, 웹 페이지, 데이터베이스, Notion, Slack, Google Drive 등 수십 종의 데이터 소스를 지원하며, 커뮤니티에서 제공하는 로더까지 합치면 수백 가지에 이릅니다. 로더가 원본 데이터를 읽어 들이면 그 결과물은 **Document** 객체가 됩니다.

**Document**는 LlamaIndex에서 하나의 문서를 표현하는 기본 단위입니다. 텍스트 본문을 담는 text 필드와, 문서에 대한 부가 정보를 담는 metadata 필드로 구성됩니다. 예를 들어 PDF 파일 하나를 로더로 읽으면, 해당 파일의 전체 텍스트가 text에 들어가고, 파일 이름, 페이지 수, 생성 날짜 같은 정보가 metadata에 저장됩니다. 아래는 Document 객체를 직접 만드는 예입니다.

```python
from llama_index.core import Document

doc = Document(
    text="LlamaIndex는 데이터와 LLM을 연결하는 프레임워크입니다.",
    metadata={"source": "internal_wiki", "page": 1}
)
```

text 필드에는 문서의 본문 텍스트가, metadata 필드에는 소스 이름과 페이지 번호가 들어 있습니다. metadata는 이후 검색 시 필터링 조건으로 활용할 수 있습니다. 예를 들어 "internal_wiki 출처의 문서만 검색하라"는 조건을 걸 수 있습니다.

하나의 Document는 보통 수천 자에서 수만 자에 이르는 긴 텍스트를 담고 있습니다. LLM의 컨텍스트 윈도우에는 한 번에 넣을 수 있는 토큰 수에 제한이 있으므로, 긴 문서를 통째로 프롬프트에 넣는 것은 비효율적이거나 불가능합니다. 또한 검색의 정밀도를 높이려면 문서를 의미 단위로 나누어야 합니다. 이때 등장하는 것이 **Node**입니다.

**Node**는 Document를 더 작은 단위로 나눈 것입니다. LlamaIndex의 실질적인 처리 단위는 Document가 아니라 Node입니다. 하나의 Document에서 여러 개의 Node가 생성되며, 각 Node는 원본 Document에 대한 참조를 유지합니다. Node에도 text와 metadata가 있고, 추가로 어떤 Document에서 나왔는지를 가리키는 관계 정보가 포함됩니다.

Document를 Node로 나누는 작업은 **NodeParser**(또는 TextSplitter)가 담당합니다. 가장 기본적인 방식은 고정된 크기(예: 1024자)로 텍스트를 자르되, 앞뒤 Node가 약간씩 겹치도록 하는 것입니다. 이 겹침을 overlap이라 부르며, 문장이 잘리면서 문맥이 끊기는 것을 방지합니다. 문장 단위로 나누는 SentenceSplitter, 마크다운의 헤더를 기준으로 나누는 MarkdownNodeParser 등 다양한 파서가 있어서, 문서의 성격에 맞는 분할 전략을 선택할 수 있습니다.

```python
from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = splitter.get_nodes_from_documents([doc])
```

이 코드는 Document를 512자 단위로, 50자씩 겹치게 나눕니다. SentenceSplitter는 단순히 글자 수로 자르는 것이 아니라, 문장 경계를 인식하여 문장 중간에서 끊기지 않도록 합니다. 결과로 나온 nodes 리스트에는 여러 개의 Node 객체가 들어 있습니다.

Document와 Node의 관계를 정리하면, Document는 원본 데이터의 논리적 단위이고, Node는 인덱싱과 검색을 위한 물리적 단위입니다. 로더가 원본 데이터를 Document로 변환하고, 파서가 Document를 Node로 분할하며, 이후의 인덱싱과 검색은 모두 Node를 기준으로 이루어집니다.

```
Document와 Node의 관계

+---------------------------+
|        Document           |
|  text: "긴 문서 전체..."  |
|  metadata: {source: ...}  |
+---------------------------+
          |
    NodeParser 분할
          |
    +-----+-----+-----+
    |     |     |     |
    v     v     v     v
 +-----+ +-----+ +-----+ +-----+
 |Node | |Node | |Node | |Node |
 | #1  | | #2  | | #3  | | #4  |
 +-----+ +-----+ +-----+ +-----+
  각 Node는 원본 Document 참조를 유지
```

Node가 준비되면 다음 단계는 **인덱싱**입니다. 인덱스란 Node들을 특정 구조로 정리하여, 나중에 질문이 들어왔을 때 관련 Node를 빠르게 찾을 수 있도록 하는 데이터 구조입니다. LlamaIndex는 용도에 따라 여러 종류의 인덱스를 제공합니다. 대표적인 세 가지가 **VectorStoreIndex**, **SummaryIndex**, **KnowledgeGraphIndex**입니다.

**VectorStoreIndex**는 가장 널리 쓰이는 인덱스 유형입니다. 각 Node의 텍스트를 임베딩 모델을 통해 벡터로 변환하고, 이 벡터들을 벡터 저장소에 저장합니다. 임베딩이란 텍스트의 의미를 고차원 숫자 배열로 표현하는 것으로, 3단원에서 자세히 다루었습니다. 질문이 들어오면 질문 텍스트도 같은 방식으로 벡터로 변환한 뒤, 저장된 벡터들 중 가장 유사한 것을 찾습니다. 유사도는 보통 코사인 유사도로 측정합니다. 이 방식은 의미적으로 관련된 내용을 찾는 데 효과적이며, RAG 파이프라인에서 가장 흔히 사용됩니다.

```python
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents([doc])
```

이 한 줄의 코드가 내부적으로 수행하는 작업은 세 단계입니다. 첫째, Document를 Node로 분할합니다. 둘째, 각 Node의 텍스트를 임베딩 모델에 보내 벡터를 생성합니다. 셋째, 생성된 벡터와 Node를 벡터 저장소에 저장합니다. 기본 설정에서는 OpenAI의 임베딩 모델을 사용하고, 벡터는 메모리에 저장됩니다. 운영 환경에서는 Pinecone, Weaviate, Chroma 같은 외부 벡터 데이터베이스를 연결하여 영속적으로 저장할 수 있습니다.

**SummaryIndex**는 벡터 유사도 검색 대신, 모든 Node를 순회하면서 LLM에게 "이 Node가 질문과 관련이 있는가"를 판단하게 하는 방식입니다. 벡터 검색이 의미적 유사성에 의존하는 반면, SummaryIndex는 LLM의 언어 이해 능력을 활용하여 관련성을 판단합니다. 이 방식은 문서 전체를 종합적으로 요약해야 하는 경우에 유용합니다. 예를 들어 "이 보고서의 핵심 결론은 무엇인가"라는 질문은 특정 문단 하나가 아니라 문서 전체의 맥락을 파악해야 답할 수 있는데, SummaryIndex가 이런 질문에 적합합니다. 다만 모든 Node에 대해 LLM 호출이 발생하므로, Node 수가 많으면 비용과 지연 시간이 증가합니다.

**KnowledgeGraphIndex**는 Node에서 엔티티(개체)와 관계를 추출하여 지식 그래프 형태로 저장하는 인덱스입니다. 지식 그래프란 "A는 B와 어떤 관계에 있다"라는 트리플(주어-관계-목적어)의 모음입니다. 예를 들어 "LlamaIndex는 LLM 프레임워크이다"라는 문장에서 "LlamaIndex"가 주어, "이다"가 관계, "LLM 프레임워크"가 목적어가 됩니다. 질문이 들어오면 질문에서 엔티티를 추출하고, 그 엔티티와 연결된 트리플을 그래프에서 탐색하여 관련 정보를 가져옵니다. 이 방식은 "A와 B의 관계는 무엇인가"처럼 엔티티 간 관계를 묻는 질문에 효과적입니다.

세 인덱스의 특성을 비교하면 다음과 같습니다.

```
인덱스 유형별 비교

+--------------------+------------------+------------------+---------------------+
| 구분               | VectorStoreIndex | SummaryIndex     | KnowledgeGraphIndex |
+--------------------+------------------+------------------+---------------------+
| 검색 방식          | 벡터 유사도      | LLM 판단         | 그래프 탐색         |
+--------------------+------------------+------------------+---------------------+
| 적합한 질문        | 특정 내용 검색   | 전체 요약        | 엔티티 관계 질문    |
+--------------------+------------------+------------------+---------------------+
| 속도               | 빠름             | Node 수에 비례   | 그래프 크기에 비례  |
+--------------------+------------------+------------------+---------------------+
| LLM 호출(검색 시)  | 없음             | Node마다 발생    | 엔티티 추출 시 발생 |
+--------------------+------------------+------------------+---------------------+
| 주 용도            | RAG 파이프라인   | 문서 요약        | 관계 기반 QA        |
+--------------------+------------------+------------------+---------------------+
```

인덱스가 구축되면, 사용자의 질문에 답하는 데 두 가지 엔진을 사용할 수 있습니다. **QueryEngine**과 **ChatEngine**입니다.

**QueryEngine**은 단발성 질문-응답에 사용합니다. 사용자가 질문을 보내면, QueryEngine은 인덱스에서 관련 Node를 검색하고, 검색된 Node의 텍스트를 프롬프트에 포함하여 LLM에 전달합니다. LLM은 제공된 맥락을 바탕으로 응답을 생성합니다. 이 과정에서 이전 대화 이력은 고려하지 않습니다. 매 질문이 독립적인 요청으로 처리됩니다.

```python
query_engine = index.as_query_engine()
response = query_engine.query("LlamaIndex의 주요 기능은 무엇인가요?")
print(response)
```

as_query_engine() 메서드는 인덱스로부터 QueryEngine을 생성합니다. query() 메서드에 질문 문자열을 전달하면, 내부적으로 세 단계가 일어납니다. 첫째, 질문을 벡터로 변환하여 인덱스에서 유사한 Node를 검색합니다. 둘째, 검색된 Node의 텍스트와 질문을 결합하여 프롬프트를 구성합니다. 셋째, 구성된 프롬프트를 LLM에 보내 응답을 받습니다.

**ChatEngine**은 대화형 상호작용에 사용합니다. QueryEngine과 달리 이전 대화 이력을 유지하여, 후속 질문에서 "그것"이나 "아까 말한 것"처럼 맥락에 의존하는 표현을 이해할 수 있습니다. ChatEngine은 내부적으로 대화 이력을 메모리에 보관하고, 새 질문이 들어올 때마다 이전 대화 맥락과 함께 처리합니다.

```python
chat_engine = index.as_chat_engine()
response1 = chat_engine.chat("LlamaIndex가 무엇인가요?")
response2 = chat_engine.chat("그것의 주요 인덱스 유형은 무엇인가요?")
```

두 번째 질문에서 "그것"은 첫 번째 질문의 "LlamaIndex"를 가리킵니다. ChatEngine은 대화 이력을 참조하여 "그것"이 무엇인지 파악한 뒤, "LlamaIndex의 주요 인덱스 유형"에 대한 검색과 응답을 수행합니다. QueryEngine으로 같은 질문을 보내면, 대화 이력이 없으므로 "그것"이 무엇을 가리키는지 알 수 없어 엉뚱한 답을 생성할 수 있습니다.

QueryEngine과 ChatEngine의 내부에서 인덱스로부터 Node를 실제로 찾아오는 역할은 **Retriever**가 담당합니다. Retriever는 질문을 받아 인덱스에서 관련 Node를 반환하는 컴포넌트입니다. 기본 Retriever는 인덱스 유형에 따라 자동으로 결정됩니다. VectorStoreIndex에서는 벡터 유사도 기반 Retriever가, SummaryIndex에서는 전체 순회 기반 Retriever가 사용됩니다.

기본 Retriever의 동작이 요구 사항에 맞지 않을 때는 커스터마이징할 수 있습니다. 가장 흔한 조정은 검색 결과 개수(top_k)를 바꾸는 것입니다. 기본값은 보통 2개인데, 질문의 복잡도에 따라 더 많은 Node를 가져와야 정확한 답변이 가능한 경우가 있습니다.

```python
retriever = index.as_retriever(similarity_top_k=5)
nodes = retriever.retrieve("벡터 인덱스의 장점은?")
```

similarity_top_k=5는 가장 유사한 Node 5개를 반환하라는 설정입니다. 반환된 nodes 리스트에는 유사도 점수와 함께 Node 객체가 들어 있어, 어떤 문서 조각이 얼마나 관련성이 높은지를 확인할 수 있습니다.

검색 결과 개수 외에도 메타데이터 필터를 추가할 수 있습니다. 예를 들어 "2024년 이후 문서에서만 검색하라"거나 "특정 부서의 문서만 대상으로 하라"는 조건을 설정할 수 있습니다. 또한 여러 인덱스의 Retriever를 조합하여 하나의 질문에 대해 벡터 검색과 키워드 검색을 동시에 수행하는 하이브리드 검색도 구성할 수 있습니다. 이런 커스터마이징은 검색 정밀도와 재현율 사이의 균형을 맞추는 데 중요합니다.

Retriever를 직접 정의하여 QueryEngine에 연결하는 흐름은 다음과 같습니다.

```python
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine

retriever = index.as_retriever(similarity_top_k=5)
synthesizer = get_response_synthesizer()
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=synthesizer
)
response = query_engine.query("검색 품질을 높이려면?")
```

이 코드에서 RetrieverQueryEngine은 Retriever와 ResponseSynthesizer를 조합하여 만든 QueryEngine입니다. Retriever가 관련 Node를 찾아오면, ResponseSynthesizer가 그 Node들의 텍스트를 LLM 프롬프트로 합성하여 최종 응답을 생성합니다. 이처럼 LlamaIndex는 각 컴포넌트를 독립적으로 교체할 수 있는 구조로 설계되어 있어, 특정 단계만 바꿔 끼우는 것이 가능합니다.

마지막으로, 5.1.2에서 다룬 LangChain과 LlamaIndex의 차이를 짚어 보겠습니다. 두 프레임워크가 해결하려는 문제의 범위가 다릅니다. LangChain은 LLM을 활용한 애플리케이션 전반의 흐름을 구성하는 데 초점을 맞춥니다. 프롬프트 템플릿, 출력 파서, 체인 구성, 에이전트, 도구 호출 등 다양한 기능을 폭넓게 제공합니다. 반면 LlamaIndex는 외부 데이터를 인덱싱하고 검색하여 LLM에 전달하는 과정, 즉 데이터 중심의 파이프라인에 집중합니다. Document, Node, Index, Retriever라는 추상화가 이 목적에 맞게 설계되어 있습니다.

실무에서는 두 프레임워크를 경쟁 관계로 보기보다 상호 보완적으로 사용하는 경우가 많습니다. 예를 들어 LlamaIndex로 문서 인덱싱과 검색 파이프라인을 구축하고, 그 결과를 LangChain의 체인에 통합하여 더 복잡한 워크플로를 만들 수 있습니다. LlamaIndex 자체도 LangChain과의 연동을 위한 도구를 제공합니다. 어떤 프레임워크를 선택할지는 프로젝트의 주된 요구 사항이 "데이터 검색과 인덱싱"인지, "전반적인 LLM 워크플로 구성"인지에 따라 달라집니다.

정리하면, LlamaIndex는 외부 데이터를 LLM이 활용할 수 있도록 구조화하는 프레임워크입니다. 원본 데이터를 Document로 읽어 들이고, Node로 분할한 뒤, VectorStoreIndex, SummaryIndex, KnowledgeGraphIndex 같은 인덱스로 정리합니다. QueryEngine은 단발성 질문에, ChatEngine은 대화형 상호작용에 사용하며, Retriever를 커스터마이징하여 검색 정밀도를 조정할 수 있습니다. LangChain이 범용적인 LLM 워크플로 구성에 강점을 가진다면, LlamaIndex는 데이터 인덱싱과 검색이라는 특정 영역에서 더 세밀한 제어를 제공합니다.

다음 단원인 5.1.4에서는 체인과 파이프라인 구성을 다룹니다. 이 단원에서 살펴본 LlamaIndex의 컴포넌트들과 5.1.2에서 다룬 LangChain의 체인을 조합하여, 순차 실행, 분기, 라우팅, 스트리밍 같은 복잡한 워크플로를 구성하는 방법을 살펴봅니다.

이 단원을 마치면 LlamaIndex의 핵심 추상화인 Document, Node, Index, QueryEngine, ChatEngine, Retriever의 역할을 설명하고, 기본적인 인덱스를 구축하여 질의 응답 파이프라인을 만들 수 있습니다.

<!-- INCOMPLETE: LlamaIndex 아키텍처 개요, Document와 Node 추상화, 인덱스 유형 (VectorStoreIndex, SummaryIndex, KnowledgeGraphIndex), QueryEngine과 ChatEngine, Retriever 커스터마이징, LangChain과의 비교 -->
