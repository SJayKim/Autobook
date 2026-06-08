# 1.3.2 Capability negotiation

앞 단원 1.3.1에서 호스트·클라이언트·서버의 3계층을 살펴보았습니다. 그런데 한 가지 의문이 남습니다. 서로 다른 시점에 만들어진 호스트와 서버가 처음 만났을 때 어떻게 서로의 기능을 맞춰 갈까요. 호스트는 sampling을 지원하지만 서버는 이 기능을 쓰고 싶지 않을 수 있고, 서버는 resource subscription을 제공하지만 호스트가 구독을 처리할 준비가 안 되어 있을 수도 있습니다. 이 차이를 매끄럽게 다루기 위해 MCP는 초기화 단계의 **capability negotiation**을 정의합니다.

협상은 호스트와 서버가 처음 연결되는 순간에 단 한 번 일어납니다. 호스트가 서버에게 보내는 첫 메시지가 **initialize** 요청입니다. 이 요청에는 세 가지 정보가 담깁니다.

```json
{
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "sampling": {},
      "roots": {"listChanged": true}
    },
    "clientInfo": {"name": "ClaudeDesktop", "version": "1.4.0"}
  }
}
```

첫째, **protocolVersion**은 호스트가 사용하고자 하는 사양 버전입니다. MCP 사양은 짧은 기간에 여러 차례 갱신되었고(2024-11-05, 2025-03-26, 2025-06-18), 각 버전은 메시지 형식과 기능에 차이가 있습니다. 호스트는 자신이 선호하는 버전을 알리고, 서버는 응답에서 자신이 동의하는 버전을 돌려줍니다. 둘 사이에 호환되는 버전이 있다면 그 버전으로 통신하고, 없다면 연결을 종료합니다.

둘째, **capabilities**는 호스트가 자신이 지원하는 능력을 선언합니다. 예시에서는 sampling을 처리할 수 있다는 점, 그리고 roots의 list_changed 알림을 보낼 수 있다는 점을 알립니다. 서버는 이 정보를 보고 그 능력을 활용할지 결정합니다. 예를 들어 호스트가 sampling을 지원하지 않는다고 응답하면, 서버는 sampling 요청을 보내지 않습니다.

셋째, **clientInfo**는 호스트 자체의 식별 정보입니다. 이름과 버전을 알려 주어 서버가 호스트별로 로깅하거나 호환성을 판단할 때 사용할 수 있게 합니다.

서버는 같은 형태로 응답합니다.

```json
{
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {"subscribe": true, "listChanged": true},
      "prompts": {"listChanged": true},
      "logging": {}
    },
    "serverInfo": {"name": "FilesystemServer", "version": "0.5.0"}
  }
}
```

서버의 응답에는 자신이 노출하는 프리미티브와 그에 따라붙는 부가 능력이 담깁니다. tools와 prompts는 list_changed 알림을 보낼 수 있고, resources는 subscribe도 처리할 수 있다고 알립니다. 이로써 호스트는 어떤 메시지를 보낼 수 있는지 파악합니다. 예를 들어 resources/subscribe를 보내려면 서버가 그 능력을 선언해야 하고, 서버의 list_changed 알림을 처리하려면 호스트가 듣고 있다가 다시 list 메서드를 호출해야 합니다.

협상이 끝나면 호스트는 **notifications/initialized** 알림을 보냅니다. 이 알림은 응답이 필요 없는 단방향 메시지로, "이제 운영 단계로 넘어가겠다"는 신호 역할을 합니다. 이 알림이 도착하기 전까지 서버는 호스트에게 자발적인 메시지를 보내지 않는 것이 권고됩니다. 그래야 호스트가 초기 상태를 깨끗하게 준비할 수 있습니다.

```
호스트                                          서버
  |                                              |
  |--- initialize (version, capabilities) ----->|
  |                                              |
  |<-- result (version, capabilities) -----------|
  |                                              |
  |--- notifications/initialized --------------->|
  |                                              |
  |     이후 운영 단계 (tools/list, ...)         |
```

protocolVersion이 다른 경우의 처리도 흥미롭습니다. 사양은 보통 하위 호환을 유지하지만, 큰 변화가 있는 경우 두 버전을 모두 지원하는 호스트·서버를 권장합니다. 예를 들어 2025-03-26 사양으로 작성된 서버에 2024-11-05만 지원하는 호스트가 접속하면, 서버는 가능한 한 옛 사양으로 응답해 주는 것이 바람직합니다. 클라이언트 SDK들은 보통 여러 버전을 동시에 지원하도록 구현되어 있어서, 사용자는 이 협상을 신경 쓸 일이 거의 없습니다.

capability를 무시하고 메시지를 보내면 어떻게 될까요. 호스트가 sampling을 지원한다고 선언하지 않았는데도 서버가 sampling/createMessage를 보내면, 호스트는 method not found 오류로 응답할 가능성이 큽니다. 이런 식의 잘못된 호출은 사양 위반이며, 잘 만든 서버라면 capability를 검사한 뒤에만 그 메서드를 사용합니다.

capability 협상의 또 다른 가치는 **선택적 기능의 매끄러운 도입**입니다. 새 사양에 새 기능이 추가되어도, 그 기능을 지원하지 않는 호스트·서버는 그저 capability에서 빠뜨리면 그만입니다. 통신은 그대로 작동하고, 새 기능을 쓰는 쪽만 그 능력을 활용합니다. 이는 사양이 빠르게 진화하는 동안 생태계 전체가 깨지지 않게 해 주는 중요한 장치입니다.

설계 측면에서 capability를 살펴보면 두 가지 패턴이 보입니다. 첫째는 **존재 자체가 신호**인 capability입니다. sampling이나 roots처럼, 객체가 존재하면 지원, 없으면 미지원입니다. 둘째는 **세부 옵션을 가진** capability입니다. resources의 subscribe·listChanged처럼 능력 안에 더 세분된 플래그가 들어갑니다. 이 두 패턴이 섞여 있으므로, SDK가 제공하는 헬퍼를 활용해 정확히 검사하는 편이 안전합니다.

정리하면, capability negotiation은 호스트와 서버가 만나는 순간에 protocolVersion·capabilities·info를 교환해 서로 무엇을 할 수 있는지 합의하는 절차입니다. 이 합의 위에서만 이후 운영 단계의 메시지가 의미를 가집니다.

다음 단원인 1.3.3에서는 지금까지의 개념을 묶어 실제로 동작하는 첫 MCP 서버를 만들어 봅니다.
