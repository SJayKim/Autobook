# 2.3.2 Reverse proxy와 로드밸런서 구성

Streamable HTTP 서버를 운영에 올리면 곧 reverse proxy나 로드밸런서 뒤에 두게 됩니다. TLS 종단, 인증 통과, 여러 인스턴스로의 분배, 헬스체크 같은 책임이 자연스럽게 떨어지는 자리입니다. 이 단원에서는 MCP 서버를 그 뒤에 둘 때 자주 마주치는 설정 포인트를 정리합니다. Nginx와 Envoy를 예시로 들지만, 어떤 프록시든 비슷한 항목이 등장합니다.

가장 큰 함정은 **SSE buffering**입니다. 기본 설정의 reverse proxy는 응답을 일정 크기까지 모아 한 번에 전달하는 경향이 있습니다. 일반적인 HTTP 응답에는 이 동작이 효율적이지만, SSE에는 치명적입니다. 서버가 이벤트를 흘려보내도 프록시가 본문을 모아 두면, 호스트는 응답을 받지 못한 채 한참 기다리게 됩니다. 그래서 SSE 응답에 대해서는 buffering을 끄거나, 적어도 매우 작은 단위로 흘리도록 설정해야 합니다.

Nginx에서는 다음 옵션이 핵심입니다.

```
location /mcp {
    proxy_pass http://mcp_upstream;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header Connection '';
    proxy_buffering off;          # SSE를 그대로 흘려보냄
    chunked_transfer_encoding on;
    proxy_read_timeout 3600s;     # 장수명 SSE 허용
    proxy_send_timeout 3600s;
}
```

`proxy_buffering off`가 가장 중요한 한 줄입니다. 이 한 줄이 빠지면 SSE 이벤트가 호스트에 즉시 도달하지 않습니다. `Connection ''` 헤더는 Nginx가 자체적으로 `Connection: close`를 추가하지 못하게 막아 줍니다. `proxy_http_version 1.1`은 keep-alive를 활성화하여 장수명 연결을 가능하게 합니다.

`proxy_read_timeout`과 `proxy_send_timeout`도 중요합니다. 기본값(보통 60초)이 너무 짧으면 SSE 연결이 활동이 없다는 이유로 끊깁니다. MCP는 활동이 없어도 세션이 살아 있을 수 있으므로, 충분히 큰 값으로 늘리거나 서버가 주기적인 heartbeat 이벤트를 흘려보내도록 만들어야 합니다. 가장 일반적인 절충은 30분~1시간 정도의 타임아웃과 15초~30초 간격의 keep-alive 이벤트를 함께 두는 것입니다.

Envoy에서는 같은 목적이 다른 단어로 표현됩니다. `stream_idle_timeout`, `http2_protocol_options`의 `max_concurrent_streams`, `keepalive_interval` 같은 설정을 함께 다룹니다. HTTP/2를 쓰면 단일 연결 위에 여러 스트림이 흐를 수 있어 효율적이지만, SSE 응답을 한 스트림으로 묶는 동작이 잘 작동해야 합니다.

다음 항목은 **세션 라우팅**입니다. 2.2.3에서 다룬 것처럼, 인메모리 세션을 채택한 서버라면 같은 세션의 요청이 같은 인스턴스에 도달해야 합니다. 두 가지 흔한 방법이 있습니다.

첫째는 **sticky session**입니다. 로드밸런서가 첫 응답에서 쿠키나 헤더를 보고 클라이언트를 한 인스턴스에 고정합니다. AWS ALB의 `lb_cookie`, Nginx Plus의 `sticky cookie`, Envoy의 `stateful_session` 필터가 이에 해당합니다. 단순하지만 한 인스턴스가 죽으면 그 세션도 잃습니다.

둘째는 **세션 식별자 기반 라우팅**입니다. Mcp-Session-Id 헤더를 해시해 일관성 있는 라우팅(consistent hashing)을 적용합니다. 같은 식별자는 항상 같은 인스턴스로 갑니다. 한 인스턴스가 죽으면 다른 인스턴스로 옮겨지면서 그 세션은 재시작됩니다. 이 방식은 가시적이라는 장점이 있습니다. 어떤 헤더가 라우팅을 결정하는지 명확합니다.

```
upstream mcp_upstream {
    hash $http_mcp_session_id consistent;
    server mcp-1:8000;
    server mcp-2:8000;
    server mcp-3:8000;
}
```

세 번째 항목은 **TLS termination**입니다. 보통 TLS는 reverse proxy에서 종단되고, MCP 서버는 평문 HTTP로 받습니다. 이 모델은 인증서 관리를 중앙화한다는 장점이 있지만, 서버가 클라이언트 IP나 원본 호스트를 알아야 한다면 `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host` 같은 헤더를 프록시에서 설정해 주어야 합니다. 인증 토큰을 검증할 때 원본 IP 기반 정책이 있다면 이 헤더가 필수입니다.

네 번째 항목은 **헬스체크 엔드포인트**입니다. MCP 사양은 헬스체크를 정의하지 않습니다. 운영을 위해 서버에 `/healthz` 같은 별도 엔드포인트를 추가해 두고, 그 엔드포인트는 인증 없이 200을 돌려주도록 만드는 것이 편합니다. 로드밸런서는 이 엔드포인트로 인스턴스 상태를 확인하고, 응답이 없으면 트래픽에서 제외합니다. MCP 본 엔드포인트 자체로 헬스를 확인하려 하면 인증·세션이 얽혀 복잡해집니다.

다섯 번째 항목은 **CORS**입니다. 브라우저 기반 호스트가 다른 도메인의 MCP 서버에 접근하면 CORS preflight가 발생합니다. 프록시에서 `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`(특히 `Mcp-Session-Id`, `Authorization`을 포함)를 적절히 설정해야 합니다. 그렇지 않으면 호스트가 응답을 받아도 브라우저가 차단합니다.

여섯 번째 항목은 **요청 크기 한도**입니다. 큰 파일을 리소스로 노출하거나 큰 결과를 돌려주는 도구라면 프록시의 기본 본문 크기 한도에 걸릴 수 있습니다. Nginx의 `client_max_body_size`, Envoy의 `max_request_bytes` 같은 옵션을 늘려야 합니다.

일곱 번째 항목은 **idle 연결 정리**입니다. 호스트가 깔끔하지 않게 종료되면 SSE 연결만 살아 있다가 결국 timeout으로 정리됩니다. 프록시는 그 동안 자원을 잡고 있으므로, 동시 연결 수가 늘어나면 서비스 자원이 빨리 소진됩니다. 동시 연결 한도와 idle timeout을 함께 조절해 자원 사용을 통제합니다.

여덟 번째 항목은 **로깅과 관측**입니다. 프록시 액세스 로그에 `Mcp-Session-Id`나 `Trace-Id` 같은 헤더를 포함시켜 두면, 후속 디버깅이 매우 쉬워집니다. 어떤 세션에서 어떤 호출이 얼마나 걸렸는지를 한눈에 볼 수 있습니다. 자세한 관측 패턴은 2.3.3에서 다룹니다.

마지막으로, 클라우드 사업자가 제공하는 매니지드 LB는 SSE 지원에 차이가 있습니다. AWS ALB는 일반 HTTP/HTTP2 위에서 SSE를 잘 지원하지만 기본 idle timeout(60초)이 짧아 조정이 필요합니다. CloudFront 같은 CDN을 앞에 두면 SSE가 캐시되거나 잘못 처리될 수 있어, MCP 트래픽은 CDN을 우회시키는 편이 안전합니다. GCP Load Balancer, Azure Application Gateway도 비슷한 주의점을 가집니다. 신규 서비스를 배포하기 전에 작은 실험으로 SSE 흐름을 확인하는 것이 좋습니다.

자주 마주치는 증상과 의심해야 할 설정을 한 표로 정리합니다.

```
증상                                    의심할 설정
SSE 이벤트가 한참 뒤에야 도착           proxy_buffering, gzip, CDN 캐시
30~60초마다 SSE가 끊김                  read/write timeout, idle timeout
같은 세션이 매번 새로 만들어짐           sticky session, consistent hashing
큰 도구 결과에서 502                     proxy body size, upstream timeout
브라우저에서만 CORS 오류                allow-origin/headers, preflight 처리
인증은 통과하는데 사용자 IP가 0.0.0.0   X-Forwarded-For 미설정
```

정리하면, Streamable HTTP 서버를 reverse proxy 뒤에 둘 때 가장 먼저 살필 항목은 SSE buffering 비활성화, 충분한 timeout, 세션 라우팅 정책입니다. 여기에 TLS 종단, 헬스체크, CORS, 본문 크기, 로깅을 더하면 운영의 골격이 갖춰집니다.

다음 단원인 2.3.3에서는 운영 중인 MCP 통신을 어떻게 관측하고 디버깅할지를 살펴봅니다.
