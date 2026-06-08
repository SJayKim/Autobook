# 9.1.3 Langfuse

9.1.1에서 LLM 옵저버빌리티의 개념과 도구 생태계를 살펴보았고, 9.1.2에서 LangSmith의 트레이싱, 평가, 비용 추적 기능을 다루었습니다. LangSmith는 강력한 플랫폼이지만, 클라우드 서비스로 제공되므로 데이터가 외부 서버에 저장됩니다. 금융, 의료, 공공 분야처럼 데이터를 외부로 전송할 수 없는 환경이 있고, 비용을 직접 통제하고 싶은 조직도 있습니다. 이 단원에서는 이러한 요구를 충족하는 오픈소스 LLM 옵저버빌리티 도구인 **Langfuse**를 다룹니다.

**Langfuse**는 LLM 애플리케이션의 트레이싱, 프롬프트 관리, 비용 분석을 제공하는 오픈소스 플랫폼입니다. MIT 라이선스로 공개되어 있어 누구나 소스 코드를 열람하고 수정할 수 있습니다. Langfuse의 가장 큰 특징은 **셀프 호스팅**(self-hosting)이 가능하다는 점입니다. 셀프 호스팅이란 소프트웨어를 외부 업체의 서버가 아닌 자신의 서버에 직접 설치하여 운영하는 것을 뜻합니다. 트레이스 데이터, 프롬프트 전문, 모델 응답이 모두 자체 서버에만 저장되므로, 민감한 데이터가 조직 밖으로 나가지 않습니다. 물론 셀프 호스팅이 부담스러운 조직을 위해 Langfuse Cloud라는 관리형 서비스도 제공합니다.

Langfuse의 아키텍처는 세 부분으로 구성됩니다. 첫 번째는 **Langfuse 서버**입니다. 트레이스 데이터를 수신하고, 저장하고, 분석하며, 웹 UI를 제공하는 백엔드입니다. 두 번째는 **데이터베이스**입니다. Langfuse는 PostgreSQL을 주 데이터베이스로 사용합니다. 트레이스, 스팬, 점수, 프롬프트 등 모든 데이터가 PostgreSQL에 저장됩니다. 세 번째는 **SDK와 통합 모듈**입니다. Python SDK, JavaScript SDK를 통해 애플리케이션 코드에서 트레이스를 전송합니다. LangChain, LlamaIndex, OpenAI SDK 등과의 통합 모듈도 제공하여, 기존 코드에 최소한의 변경만으로 계측을 추가할 수 있습니다.

```
Langfuse 아키텍처

+-------------------+     +-------------------+     +-------------------+
| 애플리케이션      |     | Langfuse 서버     |     | PostgreSQL        |
|                   |     |                   |     |                   |
| Python/JS SDK     |---->| API 수신          |---->| 트레이스 저장     |
| LangChain 통합    |     | 분석 엔진         |     | 스팬 저장         |
| OpenAI 통합       |     | 웹 UI             |<----| 프롬프트 저장     |
+-------------------+     +-------------------+     +-------------------+
                                   |
                                   v
                          +-------------------+
                          | 웹 브라우저       |
                          | (대시보드,        |
                          |  트레이스 뷰어,   |
                          |  프롬프트 관리)    |
                          +-------------------+
```

Langfuse에서 데이터를 구조화하는 핵심 개념은 **트레이스**(trace)와 **스팬**(span)입니다. 이 두 개념은 9.1.1에서 다룬 옵저버빌리티의 기본 구조와 동일합니다. 하나의 트레이스가 하나의 사용자 요청 전체를 나타내고, 그 안에 여러 스팬이 계층적으로 들어갑니다. Langfuse에서는 스팬을 세 가지 유형으로 세분합니다. **span**은 일반적인 작업 단위입니다. **generation**은 LLM 호출을 나타내는 특수한 스팬으로, 모델명, 입력 토큰 수, 출력 토큰 수, 비용 등의 메타데이터가 자동으로 기록됩니다. **event**는 시간 범위가 아닌 단일 시점의 이벤트를 기록할 때 사용합니다.

트레이스를 생성하는 기본적인 코드 구조를 살펴보겠습니다.

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-...",
    secret_key="sk-...",
    host="https://your-langfuse-server.com"
)

# 트레이스 생성
trace = langfuse.trace(
    name="rag_pipeline",
    user_id="user_1234",
    session_id="session_abc"
)

# 검색 단계를 스팬으로 기록
retrieval_span = trace.span(
    name="document_retrieval",
    input={"query": "LLM 비용 최적화 방법"}
)
# ... 검색 실행 ...
retrieval_span.end(output={"documents": retrieved_docs})

# LLM 호출을 generation으로 기록
generation = trace.generation(
    name="llm_call",
    model="gpt-4o",
    input=[{"role": "user", "content": prompt}]
)
# ... 모델 호출 ...
generation.end(
    output=response_text,
    usage={"input": 1200, "output": 350}
)
```

위 코드에서 'Langfuse()' 생성자에 전달하는 'host'가 Langfuse 서버의 주소입니다. 셀프 호스팅 환경이라면 자체 서버 주소를, Langfuse Cloud를 사용한다면 'https://cloud.langfuse.com'을 지정합니다. 'langfuse.trace()'로 트레이스를 시작하고, 'trace.span()'이나 'trace.generation()'으로 하위 단계를 기록합니다. 각 단계의 '.end()' 호출에서 출력과 사용량 정보를 전달합니다. 'generation'의 'usage' 필드에 입력 토큰과 출력 토큰을 명시하면, Langfuse가 모델별 단가를 적용하여 비용을 자동으로 계산합니다.

Langfuse에서 특히 유용한 기능 중 하나가 **세션 관리와 사용자 추적**입니다. 위 코드에서 'user_id'와 'session_id'를 트레이스에 지정한 것을 볼 수 있습니다. 'user_id'는 사용자를 고유하게 식별하는 값이고, 'session_id'는 하나의 대화 세션을 식별하는 값입니다. 챗봇에서 한 사용자가 여러 턴에 걸쳐 대화를 이어가면, 각 턴이 별도의 트레이스로 기록되지만 같은 session_id를 공유합니다. Langfuse 웹 UI에서 세션 ID로 필터링하면, 한 대화의 전체 흐름을 시간순으로 볼 수 있습니다.

사용자 단위의 추적도 가능합니다. user_id로 필터링하면, 특정 사용자가 보낸 모든 요청과 그에 대한 모델 응답을 확인할 수 있습니다. 이 기능은 "특정 사용자가 불만을 제기했을 때 해당 사용자의 최근 대화 내역을 검토하는" 같은 운영 시나리오에서 유용합니다. 사용자별 토큰 사용량과 비용도 집계되므로, 어떤 사용자가 자원을 많이 소비하는지를 파악하는 데도 활용됩니다.

**프롬프트 관리** 기능은 프롬프트의 버전을 체계적으로 관리합니다. 프로덕션에서 사용하는 프롬프트를 코드에 직접 하드코딩하면, 프롬프트를 변경할 때마다 코드를 수정하고 재배포해야 합니다. Langfuse의 프롬프트 관리 기능을 사용하면, 프롬프트를 Langfuse 서버에 저장하고 애플리케이션 코드에서는 이름과 버전 번호로 프롬프트를 불러옵니다. 프롬프트를 변경하려면 Langfuse 웹 UI에서 새 버전을 등록하기만 하면 됩니다. 코드 재배포 없이 프롬프트를 교체할 수 있습니다.

프롬프트 관리에서 중요한 것은 **버전 이력**입니다. 프롬프트를 수정할 때마다 새 버전이 생기므로, 어떤 시점에 어떤 프롬프트가 사용되었는지를 추적할 수 있습니다. 프롬프트를 변경한 뒤 품질이 떨어지면, 이전 버전으로 되돌릴 수 있습니다. 또한 각 트레이스에 사용된 프롬프트 버전이 기록되므로, "버전 3으로 바꾼 이후 오류율이 올라갔다"는 분석이 가능합니다.

```
프롬프트 관리 흐름

[Langfuse 서버]
  프롬프트 이름: "customer_support"
  버전 1: "고객 질문에 간결하게 답변하세요."
  버전 2: "고객 질문에 답변하되, FAQ 링크를 포함하세요."  <-- 현재 활성
  버전 3: (준비 중)

[애플리케이션 코드]
  prompt = langfuse.get_prompt("customer_support")
  # --> 현재 활성 버전(2)의 내용을 반환

[트레이스 기록]
  트레이스 A: prompt_version=2, 점수=4.2
  트레이스 B: prompt_version=1, 점수=3.8
  --> 버전별 품질 비교 가능
```

**비용 분석 대시보드**는 토큰 사용량과 비용을 다양한 기준으로 집계하여 시각화합니다. Langfuse는 generation 스팬에 기록된 모델명과 토큰 사용량을 바탕으로 비용을 계산합니다. 주요 LLM 제공자(OpenAI, Anthropic, Google 등)의 모델별 단가가 내장되어 있어, 별도 설정 없이도 비용이 자동으로 산출됩니다. 커스텀 모델이나 셀프 호스팅 모델의 경우 단가를 직접 등록할 수 있습니다.

대시보드에서는 일별, 주별, 월별 비용 추이를 확인할 수 있습니다. 모델별로 비용을 분리하면 "GPT-4o가 전체 비용의 70%를 차지한다"는 사실을 파악할 수 있고, 사용자별로 분리하면 "상위 5%의 사용자가 전체 토큰의 40%를 소비한다"는 분석이 가능합니다. 이러한 분석 결과는 9.2.3에서 다룰 토큰 비용 최적화 전략을 수립하는 데 기초 데이터가 됩니다.

마지막으로 **셀프 호스팅 설정**을 살펴보겠습니다. Langfuse는 Docker 이미지로 배포되므로, Docker가 설치된 환경이라면 어디서든 실행할 수 있습니다. 최소 구성은 Langfuse 서버 컨테이너 하나와 PostgreSQL 데이터베이스 하나입니다. Docker Compose를 사용하면 두 컨테이너를 한 번에 실행할 수 있습니다.

```yaml
# docker-compose.yml (Langfuse 셀프 호스팅 최소 구성)
version: "3.8"
services:
  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: "postgresql://langfuse:password@db:5432/langfuse"
      NEXTAUTH_SECRET: "your-secret-key"
      NEXTAUTH_URL: "http://localhost:3000"
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: password
      POSTGRES_DB: langfuse
    volumes:
      - langfuse_data:/var/lib/postgresql/data

volumes:
  langfuse_data:
```

위 설정에서 'langfuse' 서비스가 Langfuse 서버이고, 'db' 서비스가 PostgreSQL 데이터베이스입니다. 'DATABASE_URL'은 Langfuse 서버가 데이터베이스에 접속하기 위한 연결 문자열입니다. 'NEXTAUTH_SECRET'은 사용자 인증에 사용되는 비밀 키로, 임의의 긴 문자열을 지정합니다. 'NEXTAUTH_URL'은 Langfuse 웹 UI의 접근 주소입니다. 이 파일이 있는 디렉토리에서 'docker compose up -d'를 실행하면, Langfuse 서버가 3000번 포트에서 시작됩니다. 웹 브라우저에서 'http://localhost:3000'에 접속하면 Langfuse UI가 열립니다.

프로덕션 환경에서 셀프 호스팅할 때는 몇 가지를 추가로 고려해야 합니다. PostgreSQL의 볼륨을 안정적인 스토리지에 연결하여 데이터 유실을 방지해야 합니다. HTTPS를 적용하여 전송 중인 데이터를 암호화해야 합니다. 정기적인 데이터베이스 백업을 설정해야 합니다. 트래픽이 많은 환경에서는 Langfuse 서버를 수평 확장(여러 인스턴스 실행)하고, 앞에 로드 밸런서를 둘 수 있습니다.

정리하면, Langfuse는 오픈소스이자 셀프 호스팅이 가능한 LLM 옵저버빌리티 플랫폼입니다. 트레이스, 스팬(span, generation, event)으로 LLM 파이프라인의 각 단계를 구조화하여 기록하고, 세션과 사용자 단위로 추적하여 운영 문제를 진단합니다. 프롬프트를 버전 관리하여 코드 재배포 없이 교체할 수 있으며, 비용 분석 대시보드로 모델별, 사용자별 비용을 파악합니다. Docker Compose로 셀프 호스팅 환경을 간편하게 구성할 수 있어, 데이터 주권이 중요한 조직에 적합합니다.

다음 단원인 9.1.4에서는 Arize가 개발한 Phoenix를 다룹니다. 임베딩 드리프트 탐지와 LLM 평가 통합이라는 Phoenix만의 특성을 살펴보고, LangSmith, Langfuse, Phoenix 세 도구를 비교합니다.

이 단원을 마치면 Langfuse를 활용하여 LLM 파이프라인을 모니터링하고 분석할 수 있습니다.

<!-- INCOMPLETE: Langfuse 아키텍처와 오픈소스 특성, 트레이스와 스팬 구조, 세션 관리와 사용자 추적, 프롬프트 관리, 비용 분석 대시보드, 셀프 호스팅 설정 -->
