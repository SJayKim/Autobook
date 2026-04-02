# 6.2.1 Logstash

Elasticsearch에 데이터를 저장하려면, 원천 시스템에서 데이터를 가져와 적절한 형태로 변환한 뒤 전송해야 합니다. 웹 서버 로그는 한 줄짜리 텍스트이고, 데이터베이스 레코드는 테이블 형태이며, 메시지 큐의 이벤트는 JSON 포맷일 수 있습니다. 이렇게 서로 다른 형태의 데이터를 수집하고, 파싱하고, 가공하여 Elasticsearch로 전달하는 작업을 수작업으로 처리하면 코드가 복잡해지고 유지보수가 어렵습니다.

**Logstash**는 이 문제를 해결하는 데이터 처리 파이프라인 도구입니다. Elastic Stack의 구성 요소 중 하나로, 다양한 소스에서 데이터를 수집하고, 변환하고, 원하는 목적지로 전송합니다. Logstash 파이프라인은 세 가지 단계로 구성됩니다.

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Input   │ ──▶ │  Filter  │ ──▶ │  Output  │
│  (수집)   │     │  (변환)   │     │  (전송)   │
└──────────┘     └──────────┘     └──────────┘
```

**Input** 단계는 데이터가 파이프라인으로 들어오는 진입점입니다. Logstash는 다양한 input 플러그인을 제공하여 여러 소스에서 데이터를 받을 수 있습니다.

beats 플러그인은 Filebeat, Metricbeat 등 경량 에이전트로부터 이벤트를 수신합니다. 지정한 포트에서 대기하다가 Beat가 보내는 데이터를 받아들입니다.

```
input {
    beats {
        port => "5044"
    }
}
```

port 값은 Beat 에이전트가 데이터를 보낼 포트 번호입니다. Logstash가 이 포트에서 수신 대기합니다.

file 플러그인은 로컬 파일 시스템의 파일을 직접 읽습니다. kafka 플러그인은 Apache Kafka 토픽에서 메시지를 소비합니다. jdbc 플러그인은 관계형 데이터베이스에서 데이터를 가져옵니다. 이 외에도 syslog, http, s3 등 다양한 플러그인을 상황에 맞게 선택할 수 있습니다.

**Filter** 단계는 수집된 데이터를 파싱하고 변환하는 핵심 단계입니다. 원시 데이터를 구조화된 필드로 분해하고, 값을 변경하거나, 새로운 정보를 추가합니다.

가장 많이 사용하는 필터 플러그인은 **grok**입니다. grok은 비정형 텍스트에서 패턴을 인식하여 구조화된 필드를 추출합니다. 웹 서버 로그처럼 정해진 형식이 있지만 JSON이 아닌 텍스트 데이터를 파싱할 때 유용합니다.

```
filter {
    grok {
        match => { "message" => "%{COMBINEDAPACHELOG}" }
    }
}
```

%{COMBINEDAPACHELOG}는 Logstash가 내장하고 있는 **Grok 패턴**입니다. Apache 웹 서버의 combined 로그 형식을 인식하여, IP 주소(clientip), HTTP 메서드(verb), 요청 경로(request), 응답 코드(response), 전송 바이트(bytes) 등의 필드로 자동 분리합니다.

Grok 패턴의 문법은 %{패턴이름:필드이름} 형태입니다. 패턴이름은 Logstash가 미리 정의한 정규식 별칭이고, 필드이름은 추출된 값이 저장될 필드 이름입니다. 예를 들어 %{IP:client_ip}는 IP 주소 패턴을 인식하여 client_ip 필드에 저장합니다. Logstash는 120개 이상의 내장 패턴을 제공하며, 커스텀 패턴도 정의할 수 있습니다.

**mutate** 필터는 필드의 이름을 바꾸거나, 값의 타입을 변환하거나, 불필요한 필드를 제거합니다.

```
filter {
    mutate {
        rename => { "host" => "hostname" }
        convert => { "bytes" => "integer" }
        remove_field => ["internal_field"]
    }
}
```

rename은 host 필드 이름을 hostname으로 변경합니다. convert는 bytes 필드 값을 문자열에서 정수형으로 변환합니다. remove_field는 지정한 필드를 이벤트에서 삭제합니다.

**date** 필터는 텍스트 형태의 날짜 문자열을 파싱하여 @timestamp 필드로 변환합니다. Elasticsearch에서 시계열 검색을 정확히 수행하려면 @timestamp가 올바른 날짜 형식이어야 하므로, 원본 로그의 타임스탬프를 date 필터로 파싱하는 과정이 중요합니다.

```
filter {
    date {
        match => ["timestamp", "dd/MMM/yyyy:HH:mm:ss Z"]
    }
}
```

match 배열의 첫 번째 요소는 원본 필드 이름이고, 두 번째 요소는 해당 필드에 담긴 날짜 문자열의 형식입니다. 이 필터는 timestamp 필드의 값을 파싱하여 @timestamp에 덮어씁니다.

**geoip** 필터는 IP 주소에서 지리 정보를 추출합니다. 도시, 국가, 위도, 경도 등의 정보를 자동으로 추가합니다. 네트워크 트래픽 분석이나 접속 지역 시각화에 활용됩니다.

**Output** 단계는 변환이 완료된 데이터를 최종 목적지로 전송합니다. 가장 흔한 출력 대상은 Elasticsearch입니다.

```
output {
    elasticsearch {
        hosts => [ "localhost:9200" ]
        index => "logs-%{+YYYY.MM.dd}"
    }
}
```

hosts는 Elasticsearch 클러스터의 주소입니다. index는 데이터가 저장될 인덱스 이름이며, %{+YYYY.MM.dd}는 이벤트의 타임스탬프를 기반으로 날짜별 인덱스를 생성합니다.

stdout 플러그인은 파이프라인을 개발하거나 디버깅할 때 유용합니다. 콘솔에 이벤트 내용을 출력하여 변환 결과를 즉시 확인할 수 있습니다.

파이프라인 전체를 하나의 .conf 파일에 작성한 예를 보겠습니다.

```
input {
    beats {
        port => "5044"
    }
}

filter {
    grok {
        match => { "message" => "%{COMBINEDAPACHELOG}" }
    }
    geoip {
        source => "clientip"
    }
    date {
        match => ["timestamp", "dd/MMM/yyyy:HH:mm:ss Z"]
    }
}

output {
    elasticsearch {
        hosts => [ "localhost:9200" ]
        index => "apache-logs-%{+YYYY.MM.dd}"
    }
}
```

이 파이프라인은 Beat로부터 Apache 로그를 수신하고, grok으로 필드를 분리하고, geoip로 지리 정보를 추가하고, date로 타임스탬프를 파싱한 뒤, Elasticsearch의 날짜별 인덱스에 저장합니다.

파이프라인을 처리하다가 특정 이벤트에서 오류가 발생할 수 있습니다. 예를 들어 grok 패턴이 일부 로그 형식과 맞지 않거나, 필드 변환에 실패하는 경우입니다. 이런 이벤트를 버리지 않고 보관하는 장치가 **Dead Letter Queue(DLQ)**입니다. DLQ가 활성화되면, 처리에 실패한 이벤트가 별도 큐에 저장됩니다. 관리자는 나중에 DLQ의 이벤트를 확인하고, 원인을 파악한 뒤 재처리할 수 있습니다.

Logstash는 하나의 프로세스에서 여러 파이프라인을 동시에 실행할 수 있습니다. **pipelines.yml** 파일에 각 파이프라인의 ID와 설정 파일 경로를 정의합니다.

```yaml
- pipeline.id: main
  path.config: "/etc/logstash/conf.d/main.conf"
- pipeline.id: secondary
  path.config: "/etc/logstash/conf.d/secondary.conf"
  pipeline.workers: 2
```

pipeline.id는 파이프라인을 식별하는 이름입니다. path.config는 해당 파이프라인의 설정 파일 경로입니다. pipeline.workers는 이벤트를 병렬 처리하는 워커 스레드 수를 지정합니다. 서로 다른 소스의 데이터를 독립적으로 처리하거나, 처리 로직을 분리하고 싶을 때 파이프라인 다중화를 사용합니다.

Logstash 프로세스가 갑자기 종료되면 메모리에 있던 처리 중 이벤트가 유실될 수 있습니다. **Persistent Queue**는 이벤트를 메모리 대신 디스크에 기록하여, 프로세스가 재시작되더라도 미처리 이벤트를 복원할 수 있게 합니다. logstash.yml에서 queue.type을 persisted로 설정하면 활성화됩니다.

정리하면, Logstash는 input, filter, output 세 단계로 구성된 데이터 처리 파이프라인입니다. input 플러그인으로 다양한 소스에서 데이터를 수집하고, filter 플러그인(grok, mutate, date, geoip 등)으로 데이터를 파싱하고 변환하며, output 플러그인으로 Elasticsearch 등 목적지에 전송합니다. Dead Letter Queue로 실패 이벤트를 보관하고, Persistent Queue로 데이터 유실을 방지하며, pipelines.yml로 여러 파이프라인을 동시에 운영할 수 있습니다.

다음 단원인 6.2.2에서는 Beats를 다룹니다. Logstash보다 가벼운 경량 에이전트로 데이터를 수집하는 방법을 알아봅니다.

이 단원을 마치면 Logstash 파이프라인의 input, filter, output 구조를 설명할 수 있으며, Grok 필터로 비정형 로그를 파싱할 수 있습니다.
