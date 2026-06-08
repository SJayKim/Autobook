# 3.2.3 PKCE와 redirect 처리

앞 단원 3.2.2에서 DCR 전체 흐름을 살펴보았습니다. 그 흐름의 가장 중요한 보호 장치 두 가지가 PKCE와 redirect 처리입니다. 둘은 짝을 이루는 장치로, 함께 작동해야 의도한 보호 효과가 납니다. 이 단원에서 두 장치를 자세히 살펴보고, MCP 호스트 구현 시 마주치는 실전 함정들을 정리합니다.

먼저 **PKCE**(Proof Key for Code Exchange)입니다. PKCE는 OAuth 2.0 시기에 모바일·SPA 같은 퍼블릭 클라이언트를 보호하기 위해 만들어진 확장입니다. 핵심 아이디어는 단순합니다. 클라이언트가 authorize 요청 시 "이 코드를 토큰으로 바꿀 사람은 이 비밀을 알아야 한다"는 약속을 함께 보냅니다.

```
1. code_verifier = 무작위 문자열 (43~128자, URL-safe)
2. code_challenge = BASE64URL(SHA-256(code_verifier))
3. authorize 요청에 code_challenge + code_challenge_method=S256 첨부
4. token 교환 시 code_verifier를 함께 전송
5. AS는 verifier의 해시가 등록된 challenge와 일치하는지 확인
```

이 메커니즘의 가치는 누군가가 authorization code를 가로채도 token으로 바꿀 수 없다는 점에 있습니다. code_verifier는 클라이언트 메모리에만 잠시 머무르고, authorize 요청이나 redirect 응답에는 들어가지 않기 때문입니다.

S256은 SHA-256 해시를 사용한다는 표시입니다. OAuth 2.1은 평문(plain) 방식의 PKCE를 더 이상 권장하지 않습니다. 모든 흐름이 S256을 쓰도록 강제하는 것이 안전합니다.

```python
import secrets, hashlib, base64

verifier = secrets.token_urlsafe(64)  # 43~128자
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b'=').decode()
```

이 짧은 코드가 호스트가 매 authorize마다 수행할 작업입니다. 결과로 얻은 verifier는 콜백을 기다리는 동안 호스트 메모리에 보관되고, 토큰 교환 시점에 함께 보내집니다.

PKCE는 confidential 클라이언트에도 적용됩니다. OAuth 2.1은 모든 흐름에서 PKCE를 권장하므로, 클라이언트 비밀이 있다 하더라도 PKCE를 함께 쓰는 것이 일반적입니다.

다음은 **redirect 처리**입니다. authorize가 끝나면 AS는 사용자를 등록된 redirect_uri로 보내면서 authorization code를 쿼리스트링에 담아 줍니다. 이 코드를 호스트가 받아야 다음 단계로 갈 수 있습니다. 문제는 호스트의 종류가 다양하다는 점입니다. 데스크톱 앱, IDE 플러그인, 웹 SPA, 모바일 앱이 각각 다른 방식으로 콜백을 받습니다.

MCP 사양과 OAuth 2.1 BCP는 다음 패턴을 권장합니다.

**Loopback redirect URI**. 데스크톱·CLI·IDE 같은 네이티브 앱은 `http://127.0.0.1:포트/callback` 형태의 loopback 주소를 사용합니다. 앱이 임의의 비특권 포트(예: 43253)에서 잠시 HTTP 서버를 띄우고, AS의 redirect를 받습니다. 포트는 매번 무작위로 골라야 합니다. 그래야 같은 머신의 다른 앱이 그 포트를 가로챌 수 없습니다.

```python
import http.server, socket, threading, secrets

def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

port = free_port()
redirect_uri = f"http://127.0.0.1:{port}/callback"
state = secrets.token_urlsafe(32)

# httpd를 띄워 callback을 처리한 뒤 종료
```

loopback에는 한 가지 미묘한 사양이 있습니다. AS는 등록된 loopback URI의 호스트(`127.0.0.1` 또는 `::1`)만 매칭하고, 포트는 자유롭게 허용하는 것이 표준 권고입니다. 그래야 호스트가 매번 다른 포트를 써도 등록을 갱신할 필요가 없습니다. AS가 포트 정확 매칭을 요구하면 매번 등록을 갱신해야 하고, 사용성이 떨어집니다.

**Custom URI scheme**(예: `myapp://callback`)도 한때 흔히 쓰였습니다. 모바일 앱이 자기 도메인 대신 자체 스킴으로 콜백을 받는 방식입니다. 이 방법은 보안상 위험합니다. 같은 머신의 다른 앱이 동일 스킴을 등록하면 가로챌 수 있습니다. 사양은 가능한 한 loopback 또는 **claimed HTTPS scheme**(iOS Universal Link, Android App Link 같은 OS 검증된 HTTPS 콜백)을 권장합니다.

**Open redirect 방지**도 중요합니다. AS는 redirect_uri를 등록된 값과 정확히 비교해야 합니다. 단순한 substring 비교나 prefix 비교는 우회를 허용합니다. 예를 들어 `https://app.example.com/callback`을 등록했는데 `https://app.example.com.attacker.com/callback`을 받아들이면, 공격자가 사용자의 동의를 가로챌 수 있습니다. 정확한 문자열 비교(또는 loopback의 경우 호스트 매칭 + 포트 자유)가 표준 권고입니다.

콜백에서 호스트가 해야 할 검증도 잊지 말아야 합니다.

```
1. state 값이 자기가 보낸 값과 일치하는가 → CSRF 방어
2. iss(issuer)가 기대한 AS인가 → 잘못된 AS 응답 방어
3. error 파라미터가 없는가 → 사용자가 거부했거나 AS 측 오류
4. code 파라미터가 있는가 → 정상 응답
```

`iss` 검증(RFC 9207)은 비교적 최근에 권장된 보호 장치입니다. 응답에 issuer 식별자가 함께 들어오면, 호스트는 자기가 보냈던 authorize 요청의 AS와 일치하는지 확인합니다. 일치하지 않으면 다른 AS의 응답이 잘못 라우팅된 것이므로 거부합니다.

이제 두 보호 장치가 함께 어떻게 동작하는지를 그림으로 정리합니다.

```
호스트                             AS
  |                                 |
  | verifier = rand;                |
  | challenge = SHA256(verifier);   |
  |                                 |
  |--- authorize?                  |
  |    code_challenge=challenge --->|
  |                                 |  사용자 로그인·동의
  |<-- redirect with code, state ---|
  |                                 |
  | state 검증, iss 검증           |
  |                                 |
  |--- token?                       |
  |    code, code_verifier=verifier|
  |--- ----------------------> ---->|
  |                                 |  challenge ?= SHA256(verifier)
  |<-- access token -----------------|
```

두 장치가 함께 막아 주는 위협은 다음과 같습니다.

```
위협                                             완화
authorization code 가로채기 (브라우저 히스토리)   PKCE로 토큰 교환 차단
authorize redirect로 사용자 동의 가로채기         정확한 redirect_uri 매칭
재실행 공격(reply attack)                         code 일회용 + verifier 결합
다른 AS의 응답 잘못 받기                          iss 검증
타 사용자에게 redirect 결과를 향하게 만들기       state 검증(CSRF)
```

MCP 사양은 이 보호 장치들을 단계별로 통합해 왔습니다. 2025-03-26에서 PKCE 필수가 되었고, 2025-06-18에서 resource indicator(RFC 8707)와 audience 검증, iss 검증 같은 보호가 더 강하게 명시되었습니다. 새 호스트를 만들 때 이 표준 권고를 따르면, 사양이 다시 한 차례 강화되어도 거의 손볼 일이 없습니다.

마지막으로 호스트 개발에서 자주 마주치는 함정 몇 가지입니다.

```
함정                                       완화
verifier를 디스크에 저장                   메모리에만 두고 콜백 직후 폐기
같은 verifier를 여러 인가에 재사용         매 흐름마다 새로 생성
redirect URI에 의미 있는 쿼리 파라미터     state·code 외에 다른 값을 두지 않음
콜백 페이지에서 자동 로그아웃 링크 노출    공격자 유도 위험, 폐쇄형 페이지 사용
포트 충돌로 다른 앱이 받음                 매번 free port를 골라 등록 또는 매칭
```

정리하면, PKCE는 코드 가로채기를 무력화하는 비밀의 약속이고, 정확한 redirect 매칭과 state·iss 검증은 동의 흐름이 엉뚱한 곳으로 새지 않게 잡아 줍니다. 두 장치는 함께 적용해야 의도한 보호 효과가 나며, MCP 호스트는 매 흐름마다 무작위 값을 새로 생성해 사용하는 습관을 들여야 합니다.

다음 단원인 3.3.1에서는 보호 장치를 갖춰도 여전히 남는 새 위협, 곧 token passthrough 문제를 살펴봅니다.
