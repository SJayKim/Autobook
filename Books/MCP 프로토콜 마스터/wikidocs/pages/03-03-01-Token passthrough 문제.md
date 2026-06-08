# 3.3.1 Token passthrough 문제

OAuth 2.1과 DCR이 갖춰지면 인증의 골격이 단단해집니다. 그런데 MCP 서버가 자기 일을 하기 위해 다른 API에 접근해야 하는 경우, 미묘한 함정이 등장합니다. **Token passthrough**입니다. 이 단원에서는 그 함정의 정체와 완화책을 정리합니다.

상황을 단순한 예로 그려 봅시다. 사내 위키 MCP 서버가 있고, 그 서버는 사용자의 위키 콘텐츠를 가져오기 위해 회사의 위키 API를 호출합니다. 위키 API도 OAuth로 보호받는다고 합시다. 사용자가 MCP 서버에 보낸 access token으로 위키 API를 그대로 호출하면 어떻게 될까요. 같은 사용자의 토큰이므로 권한 측면에서는 문제가 없어 보입니다. 그러나 이 패턴이 바로 token passthrough이며, 사양과 보안 권고가 모두 금지하는 행위입니다.

이유는 **audience의 의미**에 있습니다. OAuth에서 access token은 특정 자원 서버(audience)를 위해 발급됩니다. AS가 이 토큰을 발급할 때 audience를 위키 MCP 서버로 두었다면, 그 토큰은 위키 MCP 서버에서만 사용되어야 합니다. 같은 사용자의 토큰이라도 위키 API라는 별도 자원 서버에는 사용되어선 안 됩니다.

이 약속이 깨지면 두 가지 위험이 생깁니다.

첫째, **권한 상승**입니다. 사용자가 MCP 서버에 동의한 scope와 위키 API에 부여한 scope는 다를 수 있습니다. MCP 서버 토큰을 위키 API에 그대로 보내면, MCP 서버에서 허용된 scope가 위키 API의 다른 영역에 적용될 위험이 있습니다. 위키 API가 audience 검증을 제대로 한다면 토큰을 거부하지만, 검증이 느슨하면 통과해 버립니다.

둘째, **신뢰 경계의 모호화**입니다. 만약 MCP 서버가 손상되면, 그 서버가 보유한 사용자 토큰은 이론적으로 audience 범위 안에서만 위험합니다. 그런데 그 토큰이 다른 API에도 통한다면, 한 곳의 침해가 여러 자원으로 번집니다. 토큰은 audience라는 경계를 따라 폭발 반경이 좁혀져야 합니다.

해결책은 두 가지 방향에서 옵니다. 호출하는 쪽(MCP 서버)과 받는 쪽(위키 API) 모두 자기 책임을 가집니다.

**받는 쪽의 책임**은 audience 검증입니다. 자원 서버는 토큰을 받으면 그 audience 클레임이 자기 자신을 가리키는지 반드시 확인해야 합니다. 일치하지 않으면 401로 거부합니다. 이 검증이 빠진 자원 서버는 token passthrough의 1차 피해자가 됩니다. RFC 9728의 protected resource metadata에 `resource` 필드를 두는 이유도 이 검증의 기준 값을 명확히 하기 위함입니다.

**호출하는 쪽의 책임**은 자기 audience용 토큰만 사용하는 것입니다. MCP 서버는 자기가 받은 토큰을 다른 자원 서버에 그대로 보내지 말아야 합니다. 그 대신 다음 두 가지 방법 중 하나를 사용합니다.

첫째, **별도 토큰 획득**입니다. MCP 서버가 위키 API에 호출하기 위해 자기 자신을 클라이언트로 삼아 별도의 OAuth 흐름을 거쳐 토큰을 받습니다. 사용자의 동의가 필요한 경우라면 처음 MCP 서버에 합류할 때 두 자원 서버 모두에 대한 scope를 함께 받는 식이 됩니다. 사용자에게는 한 번의 동의 흐름이지만, 내부적으로는 두 audience용 토큰이 발급됩니다. AS가 이를 자연스럽게 지원하지 않으면 MCP 서버가 두 번의 authorize 흐름을 묶어야 합니다.

둘째, **토큰 교환**(RFC 8693)입니다. MCP 서버가 받은 토큰을 AS에 다시 보내, 다른 audience로 좁힌 새 토큰을 받습니다. 표준화된 token exchange 흐름은 이 시나리오를 정확히 다룹니다.

```
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:token-exchange
&subject_token=eyJ...   (사용자가 보낸 토큰)
&subject_token_type=urn:ietf:params:oauth:token-type:access_token
&audience=https://wiki-api.example.com
&scope=read:notes

HTTP/1.1 200 OK
{
  "access_token": "new_eyJ...",
  "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
  "token_type": "Bearer",
  "expires_in": 300
}
```

새 토큰은 다음 두 가지가 다릅니다. audience가 위키 API를 가리키고, scope가 위키 API에 필요한 만큼으로 좁혀집니다. 원래 토큰이 보유한 다른 권한은 새 토큰에 들어오지 않습니다. 이 흐름이 잘 동작하려면 AS가 RFC 8693을 지원해야 하고, MCP 서버가 token exchange를 위한 클라이언트로 사전 등록되거나 DCR로 등록되어 있어야 합니다.

이 두 가지 외에 단순한 **서비스 계정**(client credentials)도 가능합니다. MCP 서버가 자기 식별으로 위키 API를 호출하고, 사용자별 권한 검증은 별도의 메커니즘(사용자 식별자를 헤더로 전달 + 위키 API가 그 사용자에 대해 권한 확인)으로 처리합니다. 이 모델은 MCP 서버가 매우 신뢰받는 내부 구성요소일 때만 적절합니다. 그렇지 않으면 MCP 서버가 사용자의 권한을 마음대로 사칭할 수 있게 됩니다.

MCP 사양은 token passthrough를 **명시적으로 금지**합니다. 2025-06-18 사양의 보안 섹션은 "MCP 서버는 자신이 audience가 아닌 토큰을 받아들이거나, 받은 토큰을 다른 자원 서버에 그대로 사용하지 말아야 한다"고 권고합니다. 이 권고는 도구 구현자와 게이트웨이 운영자 모두에게 적용됩니다.

운영 관점에서 token passthrough를 막기 위한 점검 항목은 다음과 같습니다.

```
점검 항목                                          위치
audience(aud) 클레임 검증                          MCP 서버(자원 서버 역할)
다른 API 호출 시 별도 토큰 사용                    MCP 서버 내부 코드
사용자 토큰을 DB·로그에 평문 보관 금지             MCP 서버 운영
토큰 교환 흐름 지원 여부 확인                      AS 설정
사용자 동의 시 필요한 모든 scope 선요청            호스트·MCP 서버 협력
```

여기서 실제 자주 마주치는 한 가지 함정은 **편의를 위한 passthrough**입니다. 처음 MCP 서버를 만들 때 "사용자 토큰을 그대로 위키 API에 넘기면 되지 않나?"라는 유혹이 큽니다. AS 설정이 단순해지고, 토큰 교환 비용도 없습니다. 그러나 이 단순함은 audience 검증을 약화시키며, 결국 외부 감사·보안 검토 단계에서 큰 부채가 됩니다. 처음부터 audience를 분리해 두는 편이 길게 보면 훨씬 안전합니다.

또 한 가지 함정은 **로그에 토큰 그대로 기록**입니다. 디버깅 편의를 위해 access token 전체를 로그에 남기는 경우가 흔한데, 그 자체로 token passthrough의 잠재 위험을 키웁니다. 로그를 보는 누구라도 그 토큰의 audience 안에서 사용자를 사칭할 수 있게 되기 때문입니다. 로그에는 토큰의 짧은 프리픽스나 jti(JWT ID)만 남기고, 전체 토큰은 절대 보관하지 않는 것이 표준입니다.

마지막으로, token passthrough를 정면으로 다루는 가장 강력한 도구는 **token binding** 또는 **DPoP**입니다. 토큰을 사용할 때 클라이언트가 자기 키로 서명한 작은 JWT(`DPoP-Proof`)를 함께 보내야 자원 서버가 받아들이는 모델입니다. 누군가 토큰만 가로채도 그 키 없이는 사용할 수 없습니다. 사양은 DPoP를 필수로 강제하지 않지만, 자원 서버가 옵션으로 요구할 수 있는 길을 열어 둡니다. 보안 요구가 높은 환경에서는 채택을 고려할 만합니다.

정리하면, token passthrough는 받은 토큰을 다른 자원에 그대로 사용해서 발생하는 위험이며, audience 검증·별도 토큰 획득·RFC 8693 token exchange가 그 표준 답입니다. 호출하는 쪽과 받는 쪽이 모두 자기 책임을 다해야 폭발 반경이 토큰 단위로 좁혀집니다.

다음 단원인 3.3.2에서는 비슷한 결의 위협이지만 게이트웨이가 끼어들 때 변형되는 confused deputy 공격을 살펴봅니다.
