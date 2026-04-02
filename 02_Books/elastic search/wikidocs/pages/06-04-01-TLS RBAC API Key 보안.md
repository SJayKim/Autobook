# 6.4.1 TLS/RBAC/API Key 보안

Elasticsearch 클러스터를 프로덕션에 배포하면, 네트워크를 통해 누구나 접근할 수 있는 상태가 됩니다. 보안 설정이 없으면 아무 사용자나 데이터를 읽고, 수정하고, 삭제할 수 있습니다. 노드 간 통신도 평문으로 이루어져 네트워크 도청에 취약합니다. 프로덕션 환경에서는 통신 암호화, 사용자 인증, 권한 관리가 필수입니다.

Elasticsearch 8.0부터는 보안 기능이 기본적으로 활성화됩니다. 이전 버전에서는 수동으로 활성화해야 합니다. elasticsearch.yml에 다음 설정을 추가합니다.

```yaml
xpack.security.enabled: true
```

이 설정을 켜고 Elasticsearch를 재시작하면, 모든 요청에 인증이 필요해집니다. 인증 없이는 어떤 API도 호출할 수 없습니다.

보안의 첫 단계는 통신 암호화입니다. Elasticsearch에서 TLS를 적용해야 하는 통신 경로는 두 가지입니다.

**Transport 통신**은 노드와 노드 사이의 내부 통신입니다. 샤드 복제, 클러스터 상태 전파, 분산 검색 등 클러스터 내부에서 발생하는 모든 트래픽이 여기에 해당합니다. Transport TLS는 xpack.security.enabled가 true이면 반드시 설정해야 합니다. 설정하지 않으면 노드가 시작되지 않습니다.

**HTTP 통신**은 클라이언트(애플리케이션, Kibana, curl 등)와 Elasticsearch 사이의 통신입니다. REST API 요청과 응답이 이 경로를 통해 오갑니다.

TLS 설정에 필요한 인증서를 생성하는 도구가 **elasticsearch-certutil**입니다. 이 도구는 Elasticsearch 배포판에 포함되어 있습니다. 인증서 생성 과정은 다음과 같습니다.

먼저 CA(인증 기관) 인증서를 만듭니다.

```bash
bin/elasticsearch-certutil ca
```

이 명령은 elastic-stack-ca.p12 파일을 생성합니다. 이 파일이 클러스터의 루트 인증 기관 역할을 합니다.

다음으로 CA 인증서를 사용하여 노드 인증서를 생성합니다.

```bash
bin/elasticsearch-certutil cert --ca elastic-stack-ca.p12
```

생성된 인증서를 elasticsearch.yml에서 참조하여 Transport TLS를 설정합니다.

```yaml
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.keystore.path: elastic-certificates.p12
xpack.security.transport.ssl.truststore.path: elastic-certificates.p12
```

transport.ssl.enabled는 Transport 계층의 TLS를 활성화합니다. verification_mode는 인증서 검증 수준을 설정합니다. certificate는 인증서의 유효성을 확인하되 호스트 이름 검증은 건너뜁니다. keystore.path와 truststore.path는 노드 인증서 파일 경로입니다.

HTTP TLS도 유사하게 설정합니다.

```yaml
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: http.p12
```

HTTP 인증서는 elasticsearch-certutil http 명령으로 별도 생성합니다. HTTP TLS가 활성화되면 클라이언트는 https 프로토콜로 접속해야 합니다.

보안 기능을 활성화하면 Elasticsearch의 **내장 사용자** 계정에 비밀번호를 설정해야 합니다. elastic 계정은 슈퍼유저 권한을 가진 관리자 계정이고, kibana_system 계정은 Kibana가 Elasticsearch에 접속할 때 사용하는 계정입니다. elasticsearch-setup-passwords 도구로 비밀번호를 설정합니다.

비밀번호 설정 후에는 **RBAC(Role-Based Access Control)**으로 사용자 권한을 세분화합니다. RBAC는 역할(role)을 먼저 정의하고, 그 역할을 사용자에게 할당하는 방식입니다.

역할을 정의하는 예를 보겠습니다.

```json
POST _security/role/log_reader
{
  "cluster": ["monitor"],
  "indices": [
    {
      "names": ["logs-*"],
      "privileges": ["read", "view_index_metadata"]
    }
  ]
}
```

이 역할은 클러스터 수준에서 monitor 권한(클러스터 상태 조회)을 갖고, logs-로 시작하는 인덱스에 대해 read와 view_index_metadata 권한을 갖습니다. 이 역할이 할당된 사용자는 로그 인덱스를 검색할 수 있지만, 데이터를 수정하거나 다른 인덱스에 접근할 수 없습니다.

RBAC는 네 가지 수준에서 접근을 제어합니다. **클러스터 수준**은 클러스터 상태 조회, 스냅샷 관리 등 클러스터 전체에 대한 권한입니다. **인덱스 수준**은 특정 인덱스의 읽기, 쓰기, 삭제 권한입니다. **도큐먼트 수준 보안(DLS)**은 같은 인덱스 안에서 특정 조건에 맞는 문서만 볼 수 있도록 제한합니다. **필드 수준 보안(FLS)**은 같은 문서 안에서 특정 필드만 볼 수 있도록 제한합니다.

DLS와 FLS를 함께 사용하는 역할 정의 예입니다.

```json
POST _security/role/restricted_reader
{
  "indices": [
    {
      "names": ["customer-*"],
      "privileges": ["read"],
      "field_security": {
        "grant": ["name", "email", "order_count"]
      },
      "query": {
        "term": { "region": "asia" }
      }
    }
  ]
}
```

field_security.grant는 사용자가 볼 수 있는 필드를 제한합니다. 이 역할은 name, email, order_count 필드만 반환하고 나머지 필드는 숨깁니다. query 절은 DLS로, region이 asia인 문서만 검색 결과에 포함됩니다.

역할을 정의한 뒤에는 사용자를 생성하고 역할을 할당합니다. Kibana의 보안 관리 화면이나 API를 통해 수행할 수 있습니다. LDAP이나 Active Directory와 연동하는 경우에는 **역할 매핑(role mapping)**을 설정하여 외부 그룹과 Elasticsearch 역할을 연결합니다.

사람이 아닌 애플리케이션이 Elasticsearch에 접근할 때는 **API Key**를 사용하는 것이 적합합니다. API Key는 사용자 비밀번호를 애플리케이션에 직접 저장하지 않아도 되게 해 줍니다.

```json
POST _security/api_key
{
  "name": "my-app-key",
  "expiration": "30d",
  "role_descriptors": {
    "app_role": {
      "cluster": ["monitor"],
      "indices": [
        {
          "names": ["app-data-*"],
          "privileges": ["read", "write"]
        }
      ]
    }
  }
}
```

name은 API Key를 식별하는 이름입니다. expiration은 만료 기간으로, 30d는 30일 후 자동 만료됩니다. role_descriptors 안에 이 키가 가질 권한을 정의합니다. 응답으로 반환되는 id와 api_key 값을 Base64로 인코딩하여 요청 헤더에 포함하면 인증이 완료됩니다.

```
Authorization: ApiKey <base64(id:api_key)>
```

API Key는 생성한 사용자의 권한 범위 내에서만 동작합니다. 즉, API Key에 슈퍼유저 권한을 부여하더라도, 생성자의 권한보다 넓은 권한을 가질 수 없습니다. 보안 모범 사례로, API Key의 권한은 필요한 최소한으로 제한하고, 정기적으로 갱신하는 것이 좋습니다.

정리하면, Elasticsearch 보안은 TLS 통신 암호화, RBAC 권한 관리, API Key 인증의 세 축으로 구성됩니다. Transport TLS와 HTTP TLS로 네트워크 통신을 암호화하고, elasticsearch-certutil로 인증서를 생성합니다. RBAC로 클러스터, 인덱스, 도큐먼트, 필드 수준까지 접근을 제어하며, API Key로 애플리케이션 인증을 구현합니다.

다음 단원인 6.4.2에서는 스냅샷과 복구를 다룹니다. 클러스터 데이터를 백업하고 복원하는 절차와 자동 스냅샷 스케줄링 방법을 알아봅니다.

이 단원을 마치면 Transport/HTTP TLS를 활성화하고 RBAC으로 사용자 권한을 관리할 수 있으며, API Key를 생성하고 애플리케이션 인증에 적용할 수 있습니다.
