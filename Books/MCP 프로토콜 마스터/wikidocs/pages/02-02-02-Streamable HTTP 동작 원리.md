# 2.2.2 Streamable HTTP 동작 원리

앞 단원 2.2.1에서 Streamable HTTP가 어떤 의도로 설계되었는지 살펴보았습니다. 이 단원에서는 실제 와이어 위에서 어떤 HTTP 메시지가 오가는지를 단계별로 추적합니다. 핵심 장면은 세 가지입니다. POST로 보내는 호스트 → 서버 메시지, 그 응답을 서버가 일반 응답 또는 SSE로 돌려주는 분기, 그리고 GET으로 시작되는 서버 → 호스트 스트림입니다.

먼저 가장 단순한 흐름인 **POST + 즉시 응답**부터 살펴봅니다. 호스트는 단일 엔드포인트(예: `https://server.example.com/mcp`)로 POST 요청을 보냅니다.

```
POST /mcp HTTP/1.1
Host: server.example.com
Content-Type: application/json
Accept: application/json, text/event-stream
Mcp-Session-Id: 9c1f...e2b
Authorization: Bearer eyJ...

{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"echo","arguments":{"message":"hi"}}}
```

서버가 결과를 짧게 돌려줄 수 있다면 그대로 일반 HTTP 응답을 보냅니다.

```
HTTP/1.1 200 OK
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"hi"}]}}
```

이 흐름은 서버리스 환경에 잘 맞습니다. 한 번의 함수 실행으로 시작과 끝이 닫히고, 다음 요청은 새 인스턴스에서 처리되어도 무방합니다.

다음은 **POST + SSE 응답**입니다. 같은 POST 요청에 대해, 서버가 결과를 곧장 돌려주지 않고 스트리밍이 필요하다고 판단하면 Content-Type을 `text/event-stream`으로 둔 응답을 만들어 SSE 이벤트를 흘립니다.

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Mcp-Session-Id: 9c1f...e2b

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"t1","progress":30}}

event: message
data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"t1","progress":70}}

event: message
data: {"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"done"}]}}
```

여러 이벤트를 한 응답 위에 흘려보낼 수 있고, 그 안에 progress 알림과 최종 응답을 함께 담을 수 있습니다. SSE의 표준 형식인 `event:`와 `data:` 줄을 활용하므로, 일반 SSE 클라이언트 라이브러리로도 디버깅이 가능합니다.

서버가 어느 모드를 고를지는 사양이 강제하지 않습니다. 클라이언트가 Accept 헤더에 두 형식을 모두 수용한다고 선언하기만 하면, 서버는 호출 특성에 따라 자유롭게 결정합니다. 단순 함수에는 일반 응답, 오래 걸리는 함수나 progress가 필요한 함수에는 SSE 응답을 고르는 것이 자연스러운 정책입니다.

다음은 **GET으로 시작하는 서버 → 호스트 스트림**입니다. 호스트가 특정 요청에 묶이지 않은 서버 알림(예: list_changed, sampling/createMessage)을 받고 싶다면, 같은 엔드포인트에 GET을 보냅니다.

```
GET /mcp HTTP/1.1
Host: server.example.com
Accept: text/event-stream
Mcp-Session-Id: 9c1f...e2b
Last-Event-ID: 42
```

서버는 SSE 응답을 열어 두고, 자발적인 메시지를 흘릴 때마다 이벤트를 보냅니다. 이 흐름은 HTTP+SSE의 전용 SSE 엔드포인트와 거의 같지만, URL이 분리되지 않았다는 점이 다릅니다.

`Last-Event-ID` 헤더는 **재전송**을 위한 장치입니다. SSE 표준이 정의해 둔 이 헤더에 클라이언트가 마지막으로 받은 이벤트 ID를 넣어 보내면, 서버는 그 이후의 이벤트만 재전송합니다. 네트워크가 일시적으로 끊겼다가 다시 붙은 경우에 같은 세션 컨텍스트를 이어 갈 수 있게 해 줍니다.

`Mcp-Session-Id` 헤더는 첫 응답에서 서버가 발급합니다. initialize 요청에 대한 응답에 이 헤더를 함께 보내고, 클라이언트는 이후 모든 요청에 같은 값을 첨부합니다. 세션 식별자가 있으면 서버는 그 세션의 상태(구독, 진행 중인 호출, 사용자 컨텍스트)를 유지할 수 있고, 재연결 시에도 같은 세션을 이어 갈 수 있습니다. 세션 관리는 다음 단원 2.2.3에서 자세히 다룹니다.

세 가지 흐름을 한 그림으로 정리합니다.

```
호스트 → 서버                       서버 → 호스트
─────────────                       ─────────────
POST /mcp + JSON-RPC 요청 ──────>  (a) 200 + application/json (일반 응답)
                                    (b) 200 + text/event-stream (스트리밍)

GET /mcp + Mcp-Session-Id ──────>  text/event-stream
                                    서버가 자발적 알림·sampling을 흘림
```

응답 코드도 사양이 의미를 부여합니다. 200은 정상이고, 404는 세션 없음, 410은 세션 만료, 401은 인증 필요(보통 WWW-Authenticate 헤더와 함께), 429는 rate limit 초과입니다. 클라이언트는 응답 코드에 따라 재인증, 재초기화, 백오프 같은 행동을 결정합니다.

이 transport의 한 가지 묘미는 **상태 모델의 자유도**입니다. 서버 구현자는 세션의 상태를 어디에 저장할지 선택할 수 있습니다. 인메모리에 두면 단일 인스턴스에서는 빠르고 단순합니다. Redis나 외부 저장소에 두면 여러 인스턴스가 같은 세션을 공유할 수 있어 로드밸런서 뒤에서도 잘 동작합니다. 완전 무상태로 만들면 모든 정보가 매 요청의 헤더와 본문에 담겨야 하지만, 그 대신 인스턴스 추가가 매우 쉬워집니다. 이 선택은 서비스 특성에 따라 달라집니다.

또 하나 주의할 점은 **헤더 케이스**입니다. HTTP 헤더 이름은 대소문자 구분이 없지만, 일부 프록시·클라이언트가 사양과 다른 케이스로 헤더를 변환할 수 있습니다. SDK들은 `Mcp-Session-Id`라는 표기를 채택하고 있으며, 직접 헤더를 다룰 때는 어떤 케이스가 와도 받아들이도록 비교를 case-insensitive하게 작성하는 편이 안전합니다.

직접 와이어를 디버깅할 때는 `curl`을 활용하면 편합니다. 예를 들어 초기화 요청을 직접 던져 볼 수 있습니다.

```
curl -N -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -X POST https://server.example.com/mcp \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{}}}'
```

`-N` 옵션은 SSE 응답을 그대로 흘려보게 해 줍니다. 응답 헤더에서 `Mcp-Session-Id`를 확인하고, 이후 요청에 그 값을 함께 보내면 됩니다.

정리하면, Streamable HTTP는 단일 엔드포인트에서 POST의 응답을 두 가지 모드(즉시 응답·SSE 응답)로 선택하고, GET으로 시작되는 SSE 스트림으로 서버 → 호스트 알림을 흘립니다. 이 세 흐름이 결합되어 양방향 통신과 스트리밍을 함께 다루며, 세션 식별자와 Last-Event-ID로 재연결까지 표준화합니다.

다음 단원인 2.2.3에서는 세션의 발급·만료·재연결·무상태 설계라는 세션 관리의 핵심 결정들을 살펴봅니다.
