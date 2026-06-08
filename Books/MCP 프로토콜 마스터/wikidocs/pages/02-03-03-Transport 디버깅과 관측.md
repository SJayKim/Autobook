# 2.3.3 Transport 디버깅과 관측

이 Phase의 마지막 단원으로, MCP transport의 문제를 진단하는 도구와 관측 방법을 정리합니다. 가장 익숙한 도구부터 시작해 점차 운영 환경에 맞는 관측 패턴까지 살펴봅니다.

가장 자주 쓰는 첫 도구는 **MCP Inspector**입니다. Anthropic이 공식 배포하는 GUI 도구로, 브라우저에서 MCP 서버와 직접 통신하며 메시지를 살펴볼 수 있습니다. 설치 없이 npx로 실행 가능합니다.

```
npx @modelcontextprotocol/inspector
```

Inspector는 두 가지 연결 모드를 지원합니다. 첫째는 stdio 모드로, 사용자가 실행할 명령어와 인자를 입력하면 Inspector가 자식 프로세스를 띄우고 연결합니다. 둘째는 Streamable HTTP 모드로, URL과 (필요하면) Authorization 헤더를 입력하면 그 서버에 붙습니다. 연결되면 좌측에 도구·자원·프롬프트 목록이 보이고, 각각을 클릭해 직접 호출해 볼 수 있습니다. 호출 결과와 그 사이에 오간 모든 메시지가 우측에 시간순으로 표시됩니다.

Inspector의 가장 큰 가치는 **호스트와 분리된 시각화**입니다. 호스트(예: Claude Desktop)와 연결된 상태에서는 모델의 결정이 함께 섞여 있어 문제의 출처가 모호해집니다. Inspector로 직접 도구를 호출해 보면 서버의 행동만 깨끗하게 관찰할 수 있습니다. "도구가 잘못 답하는 것"인지 "모델이 잘못 호출하는 것"인지를 가르는 첫 번째 진단입니다.

stdio 서버를 디버깅할 때는 **stderr 출력**이 결정적입니다. 1.3.3에서 강조했듯, 서버는 디버그 정보를 stderr로 보내야 합니다. 호스트는 보통 자식 프로세스의 stderr를 자기 로그에 합치거나 파일로 저장합니다. Claude Desktop의 경우 macOS는 `~/Library/Logs/Claude/`, Windows는 `%APPDATA%\Claude\logs\`에 로그를 둡니다. 서버 자체가 stderr에 충분히 의미 있는 메시지를 출력하도록 만들어 두면, 호스트와 연결되어 있을 때도 빠르게 원인을 좁힐 수 있습니다.

Streamable HTTP 서버는 보통 HTTP 인프라가 제공하는 관측 도구를 그대로 활용할 수 있습니다. **액세스 로그**가 첫 출발점입니다. 각 요청의 메서드, 경로, 응답 코드, 응답 시간이 기록됩니다. 여기에 `Mcp-Session-Id`를 함께 기록해 두면 세션 단위로 호출 패턴을 묶어 볼 수 있습니다. Nginx의 access log 포맷에 `$http_mcp_session_id`를 추가하는 식입니다.

```
log_format mcp '$remote_addr - $request_time '
               'session=$http_mcp_session_id '
               '"$request" $status $body_bytes_sent';
```

세 번째 도구는 **메시지 캡처**입니다. SDK가 제공하는 디버그 로깅을 켜면, JSON-RPC 객체 전체를 stderr나 파일로 덤프할 수 있습니다. Python SDK는 `MCP_LOG_LEVEL=DEBUG` 환경 변수로, TypeScript SDK는 `DEBUG=mcp:*`로 켭니다. 이 로그는 사양 위반이나 capability 불일치 같은 미묘한 문제를 찾는 데 결정적입니다. 예를 들어 호스트가 sampling을 capability에 선언하지 않았는데 서버가 sampling/createMessage를 보내는 패턴은 디버그 로그에서 한눈에 드러납니다.

네 번째 도구는 **OpenTelemetry**(OTel) 트레이스입니다. 분산 시스템에서 한 요청이 여러 서비스를 거치며 처리될 때, 그 흐름을 한 줄로 묶어 보여 주는 표준입니다. MCP에 직접 OTel을 통합한 SDK는 아직 발전 중이지만, 운영자가 직접 다음을 적용할 수 있습니다. 호스트는 모델 호출과 도구 호출에 트레이스 스팬을 만들고, 도구 호출 시 `traceparent` 헤더(W3C Trace Context)를 함께 보냅니다. 서버는 그 헤더를 받아 자기 스팬의 부모로 연결합니다. 결과적으로 모델 호출 → 도구 호출 → 외부 API 호출이 한 트레이스로 묶입니다.

OpenTelemetry의 **GenAI semantic conventions**도 함께 봐 둘 만합니다. 모델 호출과 도구 호출에 어떤 속성(예: `gen_ai.tool.name`, `gen_ai.usage.input_tokens`)을 붙여야 할지 표준이 제안되었습니다. 아직 진화 중이지만, 이 표준을 따르면 다른 도구나 대시보드와 통합이 쉬워집니다.

다섯 번째 항목은 **지표**입니다. 트레이스가 한 요청의 흐름을 보여 준다면, 지표는 전체 시스템의 상태를 보여 줍니다. MCP 서버에서 가져갈 만한 핵심 지표는 다음과 같습니다.

```
지표                                      의미
mcp_requests_total                        method별 호출 횟수
mcp_request_duration_seconds              method별 응답 시간 분포
mcp_active_sessions                       현재 활성 세션 수
mcp_sse_connections                       현재 열린 SSE 연결 수
mcp_tool_errors_total                     isError=true로 끝난 도구 호출 수
mcp_reconnects_total                      세션 만료 후 새 initialize 횟수
```

이 지표들을 Prometheus 같은 시계열 데이터베이스로 수집하고 Grafana로 시각화하면, 시스템의 건강 상태를 한눈에 볼 수 있습니다. 비정상 패턴(예: 재연결 횟수 폭증, 특정 도구의 isError 비율 급증)을 알림으로 연결해 두면 운영 자동화의 출발점이 됩니다.

전형적인 장애 유형 몇 가지를 정리합니다.

```
증상                                   가장 흔한 원인
도구를 호출했는데 응답이 없음            stdout에 print 사용, SSE buffering
호스트가 도구 목록을 보지 못함           initialized 알림 누락
초기화 후 곧장 끊김                       protocolVersion 불일치
SSE가 30초마다 끊김                       프록시 read_timeout
세션이 매번 새로 만들어짐                sticky/세션 라우팅 미설정
인증은 되는데 401 반복                   토큰 만료, audience 불일치
대용량 결과에서 502                       프록시 body 한도, upstream timeout
모델이 도구를 잘못 호출                   inputSchema description 부족
```

이런 표는 머리에 다 외울 필요는 없지만, 새 서버를 띄울 때 한 번 훑어 두면 첫 며칠의 시행착오를 줄여 줍니다.

마지막으로 **로컬에서 wire를 들여다보는 작은 트릭** 몇 가지를 적어 둡니다. 첫째, stdio 서버에 `tee` 래퍼를 두면 메시지를 파일로 저장하면서 호스트와도 그대로 주고받을 수 있습니다. 둘째, Streamable HTTP 서버 앞에 `mitmproxy`를 두면 모든 HTTP 메시지를 브라우저에서 시각적으로 볼 수 있습니다. 셋째, 의심스러운 메시지를 잘라 내어 `curl`로 재현해 보면 클라이언트 코드의 문제인지 서버의 문제인지를 빠르게 가를 수 있습니다.

정리하면, MCP transport 디버깅은 Inspector로 시작해, stderr 로그·SDK 디버그 로그·HTTP 액세스 로그를 통해 메시지 단위로 좁히고, OpenTelemetry 트레이스와 핵심 지표로 운영 단계로 확장하는 흐름을 따릅니다. 전형적인 장애 패턴을 머리에 두고 있으면 첫 진단의 속도가 크게 빨라집니다.

이 단원으로 Phase 2를 마무리합니다. 다음 Phase 3에서는 원격 MCP에서 가장 중요한 보안 모델, 곧 OAuth 2.1과 Dynamic Client Registration을 살펴봅니다. 다음 단원인 3.1.1에서는 왜 MCP에 OAuth가 필요한지를 출발점으로 삼습니다.

이 단원을 마치면 transport 단의 장애를 만났을 때 어떤 도구로 무엇을 확인할지 결정할 수 있고, 운영 환경에 맞는 관측 지표를 직접 설계할 수 있습니다.
