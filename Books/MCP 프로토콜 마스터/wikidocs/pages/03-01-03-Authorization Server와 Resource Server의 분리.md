# 3.1.3 Authorization Server와 Resource Server의 분리

앞 단원에서 OAuth 2.1의 핵심 개념을 살펴보았습니다. 한 가지 더 짚어 둘 골격이 있습니다. **Authorization Server**(AS)와 **Resource Server**(RS)의 분리입니다. 이 분리가 어떻게 동작하는지, MCP가 그 위에서 어떤 메타데이터 발견 흐름을 정의하는지를 정리합니다.

OAuth는 두 서버를 개념적으로 구분합니다. **Authorization Server**는 사용자 로그인, 동의 화면, 토큰 발급을 담당합니다. 사용자의 정체성(누가 로그인했는가)과 권한(어떤 scope에 동의했는가)을 확인하고, 그 결과를 access token으로 발급합니다. **Resource Server**는 발급된 토큰을 받아 API 호출을 처리합니다. 토큰을 검증한 뒤, 토큰이 표현하는 권한 범위 안에서만 자원을 노출합니다.

MCP에서는 이 두 서버가 보통 다른 인스턴스입니다. AS는 회사가 이미 가지고 있는 IdP(예: Okta, Auth0, Azure AD, Keycloak)일 가능성이 높고, RS는 우리가 새로 만든 MCP 서버입니다. 이 분리에서 자연스럽게 두 가지 질문이 나옵니다. 첫째, MCP 클라이언트는 어떤 AS와 이야기해야 하는지 어떻게 알까요. 둘째, 사용자가 인증된 사실을 RS는 어떻게 신뢰할까요.

첫째 질문의 답이 **protected resource metadata**(RFC 9728)입니다. MCP 서버는 자기 도메인의 `/.well-known/oauth-protected-resource` 경로에 자기 메타데이터를 노출합니다.

```
GET /.well-known/oauth-protected-resource HTTP/1.1
Host: mcp.example.com

HTTP/1.1 200 OK
Content-Type: application/json

{
  "resource": "https://mcp.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "bearer_methods_supported": ["header"],
  "scopes_supported": ["read:notes", "write:notes"]
}
```

핵심 필드는 두 가지입니다. `resource`는 이 자원 서버의 정식 식별자입니다. AS가 발급한 토큰의 audience 클레임은 이 값과 일치해야 합니다. `authorization_servers`는 이 자원 서버가 신뢰하는 AS 목록입니다. 클라이언트는 이 목록 중 하나를 골라 그 AS의 메타데이터로 다시 이동합니다.

```
GET /.well-known/oauth-authorization-server HTTP/1.1
Host: auth.example.com

HTTP/1.1 200 OK
Content-Type: application/json

{
  "issuer": "https://auth.example.com",
  "authorization_endpoint": "https://auth.example.com/authorize",
  "token_endpoint": "https://auth.example.com/token",
  "registration_endpoint": "https://auth.example.com/register",
  "scopes_supported": ["read:notes", "write:notes"],
  "code_challenge_methods_supported": ["S256"],
  "response_types_supported": ["code"]
}
```

이것이 **authorization server metadata**(RFC 8414)입니다. 클라이언트는 이 메타데이터를 보고 사용할 엔드포인트를 결정합니다. authorize 엔드포인트로 사용자를 보내고, token 엔드포인트에서 코드를 교환하고, 필요하다면 registration 엔드포인트로 동적 등록을 합니다.

이 두 메타데이터의 조합으로 클라이언트는 **사전 지식 없이도** 인증 흐름을 시작할 수 있습니다. 사용자가 새 MCP 서버 주소를 입력하면, 호스트는 그 서버의 protected resource metadata를 읽고, 그 안의 AS 메타데이터를 다시 읽어, 어디로 사용자를 인도할지를 결정합니다. 이 흐름이 가능해야 새 서버가 등장할 때마다 호스트를 손볼 필요가 없어집니다.

여기서 한 가지 미묘한 안전 장치가 있습니다. **WWW-Authenticate 헤더**를 통한 도약입니다. 호스트가 토큰 없이 또는 만료된 토큰으로 MCP 호출을 보내면, 자원 서버는 401 응답에 다음과 같은 헤더를 함께 보냅니다.

```
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource="https://mcp.example.com",
                  resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource"
```

호스트는 이 헤더를 보고 곧장 메타데이터 발견 흐름을 시작합니다. 헤더에 메타데이터 URL이 있으므로 추측에 의존하지 않습니다. 이 패턴이 표준화되어 있다는 점이 중요합니다. 호스트는 어떤 MCP 서버를 만나든 같은 헤더를 기대할 수 있고, 그 결과 사용자 입장에서는 "처음 본 서버"라도 익숙한 로그인 흐름을 마주하게 됩니다.

둘째 질문, 즉 자원 서버가 토큰을 신뢰하는 방법은 두 가지가 있습니다. 첫째는 **자체 검증**(local validation)입니다. AS가 JWT를 발급하고 서명 키를 공개 키 형태로 노출하면(JWKS 엔드포인트), RS는 그 키로 JWT 서명을 직접 검증할 수 있습니다. 외부 호출 없이 빠릅니다. 둘째는 **인트로스펙션**(introspection)입니다. RS가 AS의 introspection 엔드포인트에 토큰을 보내 유효성을 확인합니다. 토큰을 폐기했을 때 즉시 반영된다는 장점이 있지만, 호출마다 외부 통신이 필요합니다. 두 방식을 함께 쓰는 하이브리드도 가능합니다. JWT 검증을 기본으로 하되, 민감한 호출 전에는 인트로스펙션으로 한 번 더 확인하는 식입니다.

RS는 다음 항목을 반드시 확인해야 합니다.

```
검증 항목                       의미
서명                            토큰이 AS가 발급한 것이 맞는가
만료(exp)                       토큰이 유효 기간 안에 있는가
audience(aud)                   토큰이 우리 자원 서버용인가
issuer(iss)                     토큰이 신뢰하는 AS에서 왔는가
scope                           이 호출에 필요한 권한을 가지고 있는가
선택: sub(주체)                  로그인한 사용자가 누구인가
```

audience 검증의 중요성은 3.3.1에서 따로 자세히 다룹니다. 한 AS가 여러 자원 서버를 인증해 주는 상황에서, audience가 우리 RS를 가리키지 않는 토큰이 들어오면 거부해야 합니다. 그렇지 않으면 token passthrough 같은 공격에 노출됩니다.

이 모델의 가장 큰 가치는 **분리에서 오는 운영 이점**입니다. AS는 회사의 신원 시스템 한 곳에 모이고, RS는 각 도메인별로 자유롭게 만들 수 있습니다. 새 MCP 서버가 등장해도 AS는 손볼 필요가 없습니다. 새 인증 방식(MFA, SSO)이 도입되어도 RS는 영향을 받지 않습니다. 사용자 입장에서는 사내 다른 서비스와 같은 로그인 흐름을 다시 만나게 됩니다.

분리의 부수 효과로 **여러 RS에 한 번 로그인**도 가능합니다. 사용자가 같은 AS를 신뢰하는 두 MCP 서버를 동시에 쓰면, 첫 서버에서 받은 sso 세션이 두 번째 서버의 인증에도 사용됩니다. 사용자는 한 번만 로그인하고 두 서버 모두에 접근할 수 있습니다(scope가 다르면 추가 동의가 필요할 수 있습니다).

물론 분리에는 비용도 있습니다. 두 서버를 운영해야 하고, 둘 사이의 신뢰 관계(공개 키, 메타데이터 발견)를 명확히 설계해야 합니다. 작은 단일 서비스라면 AS와 RS가 같은 인스턴스에 합쳐져 있어도 됩니다. 사양은 두 역할이 같은 인스턴스에 합쳐지는 것을 막지 않습니다. 다만 사용자가 늘고 여러 도메인의 자원이 등장하면 분리를 권장합니다.

정리하면, OAuth의 AS·RS 분리는 인증과 자원을 깨끗하게 나누는 골격이며, RFC 9728의 protected resource metadata와 RFC 8414의 authorization server metadata, 그리고 WWW-Authenticate 헤더의 조합으로 새 클라이언트가 어떤 사전 지식도 없이 인증 흐름을 시작할 수 있게 해 줍니다.

다음 단원인 3.2.1에서는 클라이언트 측의 또 다른 도전, 곧 무수히 많은 호스트를 어떻게 동적으로 등록할 것인지를 다룹니다.
