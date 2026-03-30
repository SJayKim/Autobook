# 2.1.3 Kafka Connect

2.1.2에서 스키마 레지스트리가 프로듀서와 컨슈머 사이의 메시지 형식을 중앙에서 관리하는 방법을 살펴보았습니다. 프로듀서와 컨슈머를 직접 작성하면 Kafka 토픽에 데이터를 넣고 꺼낼 수 있습니다. 그런데 실제 시스템에서는 데이터베이스, 검색 엔진, 클라우드 스토리지처럼 Kafka 밖에 있는 시스템과 데이터를 주고받아야 하는 상황이 빈번합니다.

이때 떠오르는 가장 단순한 방법은 애플리케이션 코드 안에서 프로듀서나 컨슈머를 직접 만들어 외부 시스템과 Kafka를 연결하는 것입니다. 예를 들어 데이터베이스의 변경 사항을 Kafka에 보내려면, 프로듀서 코드를 작성하고 데이터베이스 변경을 감지하는 로직을 직접 구현해야 합니다. 오프셋을 어디까지 읽었는지 추적하는 코드도 필요합니다. 장애가 발생했을 때 중복 없이 재시작하는 로직도 만들어야 합니다. 이런 코드를 외부 시스템마다 새로 작성하면 비슷한 구조가 반복됩니다. 오프셋 관리, 직렬화, 장애 복구처럼 공통되는 부분을 매번 구현하는 것은 비효율적입니다.

**Kafka Connect**는 이 공통 부분을 프레임워크로 묶어 놓은 것입니다. Apache Kafka가 제공하는 네 가지 핵심 API 중 하나인 Connector API를 기반으로 동작합니다. 개발자는 데이터를 읽거나 쓰는 로직만 구현하면 됩니다. 오프셋 관리, 직렬화와 역직렬화, 장애 복구, REST API 서버 기능은 프레임워크가 자동으로 제공합니다. 이미 만들어진 커넥터가 100개 이상 존재하므로, 많은 경우 코드를 작성하지 않고 설정만으로 외부 시스템과 Kafka를 연결할 수 있습니다.

Kafka Connect의 데이터 흐름은 두 가지 방향으로 나뉩니다. 외부 시스템에서 Kafka로 데이터를 가져오는 방향과, Kafka에서 외부 시스템으로 데이터를 내보내는 방향입니다. 전자를 담당하는 것이 Source Connector이고, 후자를 담당하는 것이 Sink Connector입니다.

**Source Connector**는 외부 시스템에서 데이터를 읽어 Kafka 토픽에 게시하는 역할을 합니다. 데이터베이스의 테이블 변경 사항을 읽거나, 로그 파일의 새 줄을 감지하거나, REST API의 응답을 주기적으로 수집하는 것이 대표적인 사용 사례입니다.

Source Connector의 내부 동작을 좀 더 구체적으로 봅니다. Source Connector는 두 개의 클래스로 구성됩니다. SourceConnector 클래스는 커넥터의 설정을 정의하고, 데이터를 몇 개의 단위로 분할할지 결정합니다. 실제 데이터 읽기는 SourceTask 클래스가 담당합니다. SourceTask는 poll()이라는 메서드를 반복 호출하여 SourceRecord 목록을 반환합니다. 각 SourceRecord에는 데이터와 함께 오프셋 정보가 포함됩니다. 프레임워크는 이 오프셋을 주기적으로 저장합니다. 장애가 발생하여 재시작하면, 마지막으로 저장된 오프셋부터 이어서 읽습니다. 개발자가 오프셋 저장 로직을 직접 작성할 필요가 없습니다.

다음은 로컬 파일을 읽어 Kafka 토픽으로 스트리밍하는 가장 간단한 Source Connector 설정 예시입니다.

```
name=local-file-source
connector.class=FileStreamSource
tasks.max=1
file=test.txt
topic=connect-test
```

name은 이 커넥터의 고유 식별자입니다. connector.class는 사용할 커넥터 구현체를 지정합니다. FileStreamSource는 Kafka에 기본 포함된 파일 읽기 커넥터입니다. tasks.max는 병렬로 실행할 최대 Task 수이며, 여기서는 파일이 하나이므로 1로 지정합니다. file은 읽을 파일 경로, topic은 데이터를 보낼 Kafka 토픽 이름입니다.

**Sink Connector**는 Source Connector의 반대 방향입니다. Kafka 토픽의 메시지를 읽어 외부 시스템에 저장합니다. Elasticsearch에 검색 인덱스를 구축하거나, HDFS나 S3에 분석용 데이터를 적재하거나, Redis 캐시를 갱신하는 것이 대표적인 사용 사례입니다.

Sink Connector도 두 개의 클래스로 구성됩니다. SinkConnector 클래스가 설정을 정의하고, SinkTask 클래스가 실제 쓰기를 담당합니다. SinkTask는 put()이라는 메서드에서 Kafka 토픽에서 읽은 레코드를 받아 외부 시스템에 기록합니다. 구독할 토픽은 topics 속성에 쉼표로 구분하여 지정하거나, topics.regex로 패턴을 사용할 수 있습니다. Sink Connector는 Kafka의 Consumer Group 기반으로 동작하므로, 2.1.2에서 다룬 컨슈머 그룹의 오프셋 관리와 리밸런싱 메커니즘을 그대로 활용합니다.

Source Connector와 Sink Connector의 데이터 흐름을 정리하면 다음과 같습니다.

```
  외부 시스템                  Kafka 클러스터                외부 시스템
  (DB, 파일,        Source       토픽        Sink        (ES, S3,
   API 등)      --> Connector --> [|||] --> Connector -->  HDFS 등)
                    poll()                   put()
```

왼쪽에서 Source Connector가 외부 시스템의 데이터를 읽어 Kafka 토픽에 넣고, 오른쪽에서 Sink Connector가 토픽의 데이터를 꺼내 다른 외부 시스템에 저장합니다.

이제 커넥터를 실행하는 런타임 환경을 살펴봅니다. Kafka Connect에서 커넥터와 Task를 실제로 구동하는 프로세스를 **Worker**라 부릅니다. Worker는 JVM 프로세스 하나에 해당합니다. Worker는 자신에게 할당된 커넥터와 Task를 실행하면서, 동시에 REST API 서버 역할도 합니다. 기본 포트는 8083입니다. 이 REST API를 통해 커넥터를 등록하고, 상태를 조회하고, 설정을 변경할 수 있습니다.

Worker 안에서 실제 데이터를 옮기는 단위가 **Task**입니다. 하나의 커넥터는 여러 개의 Task로 분할될 수 있습니다. tasks.max 설정값이 이 최대 분할 수를 결정합니다. 예를 들어 데이터베이스의 테이블 10개를 읽는 Source Connector에 tasks.max=5를 지정하면, 최대 5개의 Task가 테이블을 나누어 병렬로 읽습니다. 실제 Task 수는 소스 데이터의 분할 가능 단위와 tasks.max 중 작은 값으로 결정됩니다. 테이블이 3개뿐이라면 tasks.max를 5로 지정해도 Task는 3개만 생성됩니다.

Task는 Worker 내부의 스레드로 실행됩니다. Source Connector의 Task는 SourceTask이며 poll()을 반복 호출합니다. Sink Connector의 Task는 SinkTask이며 put()을 호출합니다. Worker, 커넥터, Task의 관계를 정리하면 다음과 같습니다.

```
  Worker (JVM 프로세스, REST API :8083)
  +--------------------------------------+
  |  Connector A                         |
  |    +-- Task A-1 (스레드)             |
  |    +-- Task A-2 (스레드)             |
  |                                      |
  |  Connector B                         |
  |    +-- Task B-1 (스레드)             |
  +--------------------------------------+
```

하나의 Worker 안에 여러 커넥터가 존재할 수 있고, 각 커넥터는 하나 이상의 Task를 가집니다.

Kafka Connect를 기동하는 방식에는 두 가지 모드가 있습니다. **단독 모드**와 **분산 모드**입니다. 두 모드의 핵심 차이는 Worker가 한 대인지 여러 대인지, 그리고 상태를 어디에 저장하는지입니다.

단독 모드(standalone mode)는 connect-standalone.sh 스크립트로 기동합니다. Worker 프로세스가 한 대만 실행됩니다. 오프셋 상태를 로컬 파일에 저장합니다. 설정이 단순하고 디버깅이 쉬워서 개발이나 테스트 환경에 적합합니다. 단일 서버에서 웹 서버 로그를 Kafka로 전송하는 것처럼 경량 사용 사례에도 쓸 수 있습니다. 다만 Worker가 한 대이므로 해당 프로세스가 중단되면 데이터 이동도 멈춥니다. 수평 확장도 불가능합니다. 이런 이유로 프로덕션 환경에는 권장되지 않습니다.

단독 모드의 필수 설정 항목은 세 가지입니다. bootstrap.servers는 Kafka 클러스터의 연결 주소입니다. key.converter와 value.converter는 메시지의 키와 값을 직렬화하는 형식을 지정합니다. 2.1.2에서 다룬 Avro, Protobuf, JSON 등을 사용할 수 있습니다. offset.storage.file.filename은 오프셋을 저장할 로컬 파일 경로입니다. 같은 호스트에서 여러 Worker를 실행한다면 이 경로를 각각 다르게 지정해야 합니다.

분산 모드(distributed mode)는 connect-distributed.sh 스크립트로 기동합니다. 여러 Worker 프로세스가 동일한 group.id를 공유하여 클러스터를 형성합니다. 단독 모드와의 가장 큰 차이는 상태 저장 방식입니다. 단독 모드가 로컬 파일에 오프셋을 저장하는 반면, 분산 모드는 Kafka 내부 토픽에 저장합니다. 커넥터 설정, 오프셋, 커넥터와 Task의 상태를 각각 별도의 Kafka 토픽에 기록합니다. Worker가 재시작되거나 다른 노드로 교체되어도 Kafka 토픽에 상태가 남아 있으므로 이어서 동작할 수 있습니다.

분산 모드에서 Worker를 추가하거나 기존 Worker가 장애로 이탈하면, 남은 Worker들이 커넥터와 Task를 자동으로 재분배합니다. 이 과정을 리밸런싱이라 합니다. Kafka의 Consumer Group 프로토콜을 활용하므로, 2.1.2에서 다룬 컨슈머 리밸런싱과 원리가 같습니다. 프로덕션 환경에서는 이 장애 허용성과 수평 확장 때문에 분산 모드를 사용합니다.

분산 모드의 필수 설정 항목을 정리합니다. bootstrap.servers는 단독 모드와 같습니다. group.id는 클러스터를 식별하는 이름으로, 같은 group.id를 가진 Worker들이 하나의 클러스터를 형성합니다. 일반 Consumer Group ID와 충돌하지 않도록 주의해야 합니다. config.storage.topic은 커넥터 설정을 저장하는 Kafka 토픽입니다. 단일 파티션에 compaction 정책을 적용하는 것이 권장됩니다. offset.storage.topic은 오프셋을 저장하는 토픽이며, 다수의 파티션을 두어 처리량을 높입니다. status.storage.topic은 커넥터와 Task의 실행 상태를 저장하는 토픽입니다.

두 모드의 차이를 정리하면 다음과 같습니다.

```
항목              단독 모드                    분산 모드
-----------      -----------------------     -------------------------
기동 스크립트     connect-standalone.sh        connect-distributed.sh
Worker 수        1대                          여러 대 (클러스터)
상태 저장         로컬 파일                    Kafka 내부 토픽
장애 허용         불가 (Worker 중단 시 멈춤)    자동 리밸런싱
수평 확장         불가                         Worker 추가로 확장
적합 환경         개발, 테스트, 경량 수집       프로덕션
```

이제 커넥터를 실제로 등록하고 관리하는 방법인 커넥터 설정을 다룹니다. 커넥터 설정을 전달하는 방식은 두 가지입니다. 첫째, Properties 파일 방식입니다. 단독 모드에서 주로 사용하며, 기동 시 파일 경로를 명령줄 인자로 전달합니다. 둘째, REST API 방식입니다. 분산 모드에서 주로 사용하며, JSON 본문으로 커넥터를 동적으로 등록하고 변경합니다. 분산 모드에서는 Worker가 실행 중인 상태에서 REST API로 커넥터를 추가하거나 삭제할 수 있습니다. 클러스터를 재시작할 필요가 없습니다.

모든 커넥터에 공통으로 필요한 설정 항목이 있습니다. name은 커넥터의 고유 식별자입니다. connector.class는 사용할 커넥터 구현 클래스의 전체 경로이거나 축약명입니다. tasks.max는 최대 Task 수입니다. key.converter와 value.converter는 메시지 키와 값의 직렬화 형식입니다. 이 외에 각 커넥터 구현체가 요구하는 고유 설정(데이터베이스 연결 정보, 파일 경로, 토픽 이름 등)을 추가합니다.

REST API의 주요 엔드포인트를 살펴봅니다. Worker의 REST API는 기본적으로 8083 포트에서 동작합니다.

```
POST   /connectors              커넥터 신규 등록
GET    /connectors/{name}       커넥터 정보 조회
PUT    /connectors/{name}/config 설정 변경
DELETE /connectors/{name}       커넥터 삭제
PUT    /connectors/{name}/pause  일시 중지 (리소스 유지)
PUT    /connectors/{name}/stop   중지 (리소스 해제)
```

POST /connectors로 새 커넥터를 등록할 때는 JSON 본문에 name, config 객체를 포함합니다. config 안에 connector.class, tasks.max, 커넥터 고유 설정을 넣습니다. GET으로 상태를 조회하고, PUT으로 설정을 변경하며, DELETE로 커넥터를 제거합니다. pause는 Task를 멈추지만 리소스를 유지하여 빠르게 재개할 수 있고, stop은 리소스까지 해제합니다.

Kafka Connect는 커넥터 레벨에서 메시지를 변환하는 기능도 제공합니다. SMT(Single Message Transformation)라 부르는 이 기능은 메시지 하나 단위로 경량 변환을 적용합니다. 필드를 추가하거나 제거하고, 토픽 이름을 변경하고, 타임스탬프를 삽입하는 등의 작업을 커넥터 설정만으로 처리할 수 있습니다. 별도의 스트림 처리 애플리케이션을 작성하지 않아도 되므로, 단순한 변환이 필요할 때 유용합니다.

정리하면, Kafka Connect는 외부 시스템과 Kafka 사이의 데이터 이동을 표준화하는 프레임워크입니다. Source Connector가 외부에서 Kafka로, Sink Connector가 Kafka에서 외부로 데이터를 옮깁니다. Worker가 커넥터와 Task를 실행하는 런타임 프로세스이며, Task가 실제 데이터 이동의 병렬 실행 단위입니다. 단독 모드는 개발과 테스트에, 분산 모드는 장애 허용과 수평 확장이 필요한 프로덕션 환경에 적합합니다. 커넥터 설정은 Properties 파일이나 REST API로 전달하며, 분산 모드에서는 실행 중에 동적으로 커넥터를 추가하거나 제거할 수 있습니다.

다음 단원인 2.1.4에서는 CDC와 Debezium을 다룹니다. Source Connector의 대표적인 구현체인 Debezium이 데이터베이스의 변경 사항을 실시간으로 Kafka에 전달하는 방식을 살펴봅니다.

이 단원을 마치면 Kafka Connect의 Source/Sink 커넥터 구조와 설정 방법을 설명할 수 있습니다.
