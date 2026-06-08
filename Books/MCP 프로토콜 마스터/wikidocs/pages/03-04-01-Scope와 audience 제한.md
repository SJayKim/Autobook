# 3.4.1 Scope와 audience 제한

지금까지의 위협들을 막는 가장 기초적인 도구가 토큰의 **scope**와 **audience**입니다. 잘 설계된 scope·audience는 그 자체로 token passthrough·confused deputy·일부 prompt injection까지 한 번에 줄여 줍니다. 이 단원에서는 MCP 환경에 적용할 만한 scope 설계 패턴과 audience 묶음을 정리합니다.

먼저 둘의 책임을 다시 정리합니다. **Audience**는 "이 토큰을 누가 받아 처리할 것인가"를 답합니다. 토큰의 aud 클레임은 한두 개의 자원 서버 식별자입니다. **Scope**는 "그 자원 서버 안에서 어떤 범위를 허용하는가"를 답합니다. scope는 보통 공백으로 구분된 문자열 목록(`read:notes write:notes`)으로 표현됩니다. 둘은 직교합니다. 같은 audience라도 scope에 따라 허용 범위가 달라지고, 같은 scope를 표현해도 audience가 다르면 다른 자원에 적용됩니다.

**Scope 설계의 기본 패턴**은 세 가지입니다.

첫째, **자원 단위 scope**입니다. 위키의 페이지·DB의 테이블·이메일의 인박스처럼, 자원 종류 단위로 scope를 정의합니다. 예: `read:pages`, `write:pages`, `read:databases`.

둘째, **동작 단위 scope**입니다. 자원 종류는 묶어 두고 동작(read·write·delete)으로 나누는 방식입니다. 예: `read`, `write`, `admin`. 단순하지만 권한 폭이 거칠어집니다.

셋째, **도구 단위 scope**입니다. MCP에 특화된 형태로, 도구별로 scope를 만듭니다. 예: `tool:send_email`, `tool:list_drafts`. 사용자 동의 화면에 도구 이름이 그대로 나와 직관적이지만, 도구 수가 많으면 scope 수도 비대해집니다.

실전에서는 보통 첫째와 셋째를 결합합니다. 자원 단위로 큰 scope를 두고, 위험한 도구에는 별도 scope를 추가하는 식입니다. 예를 들어 위키 MCP 서버의 scope는 다음처럼 구성할 수 있습니다.

```
read:notes        — 모든 페이지 읽기
write:notes       — 페이지 작성·수정
admin:notes       — 페이지 삭제·권한 변경
tool:share_email  — 페이지를 외부에 메일로 공유 (위험)
```

`share_email`은 일반적인 write scope보다 더 위험하므로 별도 scope로 분리합니다. 사용자가 일반 작성을 동의했더라도 외부 공유는 따로 확인합니다.

scope 설계의 좋은 신호 몇 가지를 짚어 두면 다음과 같습니다.

```
좋은 신호                                       반대 신호
사용자가 동의 화면에서 의미를 읽을 수 있다       모호한 단어("access", "all")만 사용
scope 하나당 한 가지 의도                       하나의 scope가 너무 많은 일을 포함
이름이 자원·동작 또는 도구를 명확히 가리킴      이름이 내부 구현을 노출
새 기능 추가 시 새 scope를 깔끔히 만들 수 있음 새 기능마다 기존 scope에 의미를 덧붙임
```

다음은 **audience 설계**입니다. audience는 토큰이 사용될 자원 서버를 가리키는 URI입니다. RFC 8707의 resource indicator를 활용하면 authorize·token 요청에 `resource=https://mcp.example.com` 같은 파라미터를 함께 보내, 발급된 토큰의 audience를 그 자원으로 한정할 수 있습니다.

audience 설계의 핵심은 한 토큰이 가능한 한 좁은 audience를 가지도록 만드는 것입니다. 다음 두 원칙을 따릅니다.

첫째, **자원 서버 단위로 audience를 분리**합니다. 한 회사가 위키·이메일·캘린더 세 MCP 서버를 운영한다면, audience도 셋입니다. 한 토큰이 세 서버를 모두 가리키는 것은 피합니다.

둘째, **하위 도메인이나 경로 단위로 더 좁힐 수 있다**면 좁힙니다. 예를 들어 한 MCP 서버가 여러 테넌트를 서비스한다면, audience를 테넌트별로 분리(`https://mcp.example.com/tenant/A`)할 수 있습니다. 자원 서버는 토큰의 audience가 호출 경로의 테넌트와 일치하는지 확인합니다.

**down-scoping**도 자주 등장하는 패턴입니다. 큰 scope의 토큰을 한 번 받은 다음, 도구별 호출 직전에 그 도구가 필요로 하는 좁은 scope의 새 토큰을 token exchange로 받는 모델입니다. 도구 호출 결과가 다른 도구 호출의 인자로 흐를 때 점진적으로 권한이 커지는 것을 막을 수 있습니다.

```
1. 사용자가 위키 서버에 read:notes + write:notes 동의
2. 사용자가 "이 페이지를 이메일로 공유" 도구 호출
3. 게이트웨이가 token exchange로 audience=mail, scope=send:share 토큰 발급
4. 이메일 도구에 좁은 토큰만 전달
```

여기서 중요한 것은 게이트웨이나 도구 구현이 항상 **가장 좁은 권한**을 골라 사용한다는 원칙입니다. 편의를 위해 admin scope를 들고 다니면, 한 도구가 손상되었을 때 모든 권한이 함께 노출됩니다.

scope·audience 설계를 사용자 동의 흐름과 맞물려 보면 다음과 같은 그림이 나옵니다.

```
사용자 처음 합류
   ↓ 동의 화면: read:notes (이 동의는 위키 서버 audience만)
   ↓
사용자가 share_email 도구 시도
   ↓ 호스트가 추가 scope 필요함을 감지 → 재인증
   ↓ 동의 화면: tool:share_email 추가 (위키 서버 audience)
   ↓
호스트가 share_email을 위해 audience=mail 토큰 교환
   ↓ token exchange → 이메일 audience, scope=send:share
   ↓
이메일 도구 호출 성공
```

이 흐름이 보여 주는 점은 사용자 동의는 점진적이며, 토큰은 사용 시점에 좁아진다는 사실입니다. 처음부터 모든 scope를 한 번에 요구하면 사용자가 거부할 가능성이 높고, 손상 시 폭발 반경도 커집니다. 필요할 때마다 새 scope를 요청하고, 사용 직전에 audience를 좁히는 패턴이 보안과 사용성 모두에 유리합니다.

다음은 **자원 서버의 audience 검증** 체크리스트입니다.

```
1. 토큰의 aud 클레임이 자기 자원 서버 식별자를 포함하는가
2. 식별자 비교가 정확한 문자열 매칭인가(prefix 매칭 금지)
3. 한 토큰이 여러 audience를 가지면 정책상 허용되는 조합인가
4. 토큰의 iss(issuer)가 자기가 신뢰하는 AS인가
5. 토큰의 scope가 호출하려는 도구·자원에 충분한가
6. scope 부족 시 403, 토큰 자체가 잘못이면 401 분리 응답
```

이 검증은 SDK가 보통 자동 처리해 주지만, 자체 미들웨어를 만들 때는 빠뜨리지 않도록 반드시 점검해야 합니다.

scope·audience를 운영에 풀어 두는 보조 도구도 정리해 둡니다.

첫째, **잘 적힌 동의 화면**입니다. 사용자에게 보여 주는 화면이 scope의 의미를 풍부히 설명해 줘야 합니다. AS의 동의 화면을 커스터마이즈할 수 있다면, 각 scope에 사람 친화적 설명을 매핑해 둡니다.

둘째, **scope 인벤토리 문서**입니다. 어떤 scope가 어떤 도구·자원과 매핑되는지 한 문서에 정리해 두면, 새 도구를 만들 때 어떤 scope를 요구할지 결정하기 쉽고, 감사 시점에도 빠르게 답할 수 있습니다.

셋째, **테스트 시나리오**입니다. scope가 부족하거나 audience가 어긋난 토큰을 일부러 보내, 자원 서버가 정확히 401·403으로 응답하는지 확인합니다. 자동화된 보안 테스트에 이 시나리오를 두면 변경에 따른 회귀를 빠르게 감지할 수 있습니다.

정리하면, scope는 자원 서버 안의 권한 폭을 좁히고, audience는 토큰이 사용될 자원 서버를 좁힙니다. 두 도구가 함께 적용되어야 최소 권한 원칙이 실제로 동작합니다. 자원 단위·도구 단위 scope 조합과 RFC 8707 resource indicator, token exchange를 통한 down-scoping이 MCP의 표준 도구함입니다.

다음 단원인 3.4.2에서는 토큰·비밀의 회전과 그에 따른 감사 흐름을 살펴봅니다.
