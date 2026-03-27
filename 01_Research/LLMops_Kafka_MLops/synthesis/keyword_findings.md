# Keyword Findings: LLMOps, Kafka, MLOps

---

## kw_001: LLMOps

**정의/핵심:**
- Large Language Model Operations. LLM을 실제 프로덕션 환경에서 관리·확장·최적화하는 신흥 분야. MLOps 원칙을 LLM의 고유한 특성에 맞게 확장한 것.
- 핵심 특성: 프롬프트 기반 반복, API-first 추론, 토큰 단위 비용 구조, 할루시네이션 모니터링.

**소스별 관점:**
- 001 (Redis): LLMOps의 핵심은 비용 제어와 신뢰성. 시맨틱 캐싱(캐시 히트율 60-85%), 지능형 모델 라우팅, 배치 최적화로 비용 68.8% 절감 가능. 레이턴시 96.9% 감소(1.67s → 0.052s per cache hit).
- 002 (TrueFoundry): MLOps와의 차이점을 표 형식으로 정리. LLMOps 개선은 "프롬프트 재작성, 검색 콘텐츠 업데이트, 출력 재랭킹"이 핵심.
- 010 (ZenML): 빌드 루프가 훨씬 빠르고 동적. 프롬프트 엔지니어링, 모델 선택, RAG, 인간 루프 평가, 비용 관리, 안전 모니터링이 추가 요소. 완전 재훈련은 최후 수단.

**소스 간 합의:**
- LLMOps는 MLOps의 대체가 아닌 확장. 추론 비용이 가장 큰 비용 드라이버. 프롬프트/임베딩/벡터스토어/가드레일이 새로운 버전 관리 대상.

**소스 간 불일치:**
- 없음 (세 소스 모두 동일한 방향성).

---

## kw_002: MLOps

**정의/핵심:**
- Machine Learning Operations. 데이터 과학자·ML 엔지니어·DevOps 팀이 협업해 모델의 빌드-배포-모니터링-유지보수를 자동화하는 관행 및 도구 집합.
- 자동화 3단계: 수동 프로세스 → ML 파이프라인 자동화 → CI/CD 파이프라인 자동화.

**소스별 관점:**
- 002 (TrueFoundry): 구조화 데이터의 분류·예측·추천에 적합. 훈련 비용이 지배적, 추론 비용 낮음.
- 003 (LakeFS): 4가지 파이프라인 유형(데이터, 모델, 실험, 프로덕션). 핵심 컴포넌트: 데이터 관리, 실험 추적, 모델 레지스트리, CI/CD, 모니터링.
- 009 (Microsoft): MLOps 성숙도 모델 5단계(Level 0~4). Level 4: 드리프트가 자동 재훈련을 트리거, 정책 기반 모델 프로모션.
- 010 (ZenML): 클래식 오프라인 훈련 루프. 특성 엔지니어링과 훈련 개선에 집중.

**소스 간 합의:**
- MLOps의 핵심 가치: 재현성, 자동화, 모니터링, 협업.

**소스 간 불일치:**
- 없음.

---

## kw_003: Apache Kafka

**정의/핵심:**
- 분산 이벤트 스트리밍 플랫폼. 4개 API(Producer, Consumer, Streams, Connector). 초당 수백만 메시지 처리 가능. 커밋 로그 기반 영속 저장.
- 구성: Broker, Topic, Partition, Consumer Group, KRaft(메타데이터 관리, ZooKeeper 대체).

**소스별 관점:**
- 020 (Instaclustr): 핵심 아키텍처 설명. KRaft가 기본 메타데이터 메커니즘으로 자리잡음. Tiered Storage(KIP-405)로 오래된 세그먼트를 S3/GCS로 오프로드.
- 021 (GoPubby): AI/ML 관점에서 Kafka의 역할: 특성 신선도, 저지연 예측, 이벤트 재생(디버깅/복구), 지리적 복제.
- 068 (Estuary): Fortune 500의 80%가 사용. 3가지 CDC 방식(Query-Based, Log-Based). Debezium은 Log-Based 방식 사용.
- 060 (Wix): Wix에서 하루 700억 이벤트, 5만 Kafka 토픽 처리.

**소스 간 합의:**
- Kafka는 ML 파이프라인의 중앙 데이터 버스. 실시간 특성 스토어, 스트리밍 추론, CDC의 핵심 인프라.

**소스 간 불일치:**
- 없음.

---

## kw_004: LLM inference serving

**정의/핵심:**
- 훈련된 LLM을 프로덕션에 배포해 실시간 추론을 제공하는 인프라. 핵심 메트릭: TTFT(Time To First Token), 처리량(tokens/sec), KV 캐시 활용률.
- 주요 엔진: vLLM(PagedAttention), TensorRT-LLM(NVIDIA 최적화), TGI(유지보수 모드), SGLang(RadixAttention).

**소스별 관점:**
- 049 (MarkTechPost): vLLM이 고동시성에서 TGI 대비 24배 처리량. TGI는 2025년 12월 유지보수 모드 전환. Stripe: vLLM 도입 후 추론 비용 73% 절감.
- 045 (PremAI): Kubernetes에서 vLLM(단일 노드), Ray Serve + vLLM(멀티 노드), llm-d(대규모 분리 서빙) 비교. CPU/메모리 메트릭 대신 큐 깊이·KV 캐시 활용률로 오토스케일링 필요.
- 040 (Civo): 8개 기둥: GPU 클러스터 프로비저닝, 재현 가능한 컨테이너, 오토스케일링, 옵저버빌리티, 보안, 비용 예측, MLOps 워크플로, 모델 시작 시간.
- 025 (Kai Waehner): 원격 추론(API 기반) vs 임베디드 추론(스트림 처리 내 모델 내장) 트레이드오프.

**소스 간 합의:**
- vLLM + Kubernetes가 2025년 프로덕션 표준. GPU 메트릭 기반 오토스케일링 필수.

**소스 간 불일치:**
- 049는 TGI를 단계적 폐기 대상으로 봄. 025는 여전히 원격 추론 아키텍처 유효성을 논함.

---

## kw_005: feature store

**정의/핵심:**
- ML 파이프라인 전반에서 특성(feature)의 생성·변환·저장·서빙을 중앙화하는 플랫폼. 훈련과 추론 간 일관성 보장. 온라인 스토어(저지연)와 오프라인 스토어(배치 훈련)의 이중 구조.

**소스별 관점:**
- 060 (Wix/Kai Waehner): Kafka + Flink로 구축한 실시간 특성 스토어. 하루 70억 이벤트 처리, 3,000개 이상 특성 지원. Aerospike를 온라인 스토어로 사용. Kappa 아키텍처(모든 데이터를 스트림으로 처리).
- 061 (MLOps Community): 다양한 아키텍처 비교: Feast(Redis+gRPC로 최고 성능), Wix DIY(활성 사용자만 온라인 스토어에 보관해 write/read 비율 최적화), Tecton(Redis Enterprise가 DynamoDB 대비 3배 빠르고 14배 저렴), Qwak(오프라인 스토어가 아닌 원본 데이터에서 직접 온라인 스토어로 물질화해 훈련-서빙 스큐 감소).

**소스 간 합의:**
- 실시간 AI/ML에 온라인 특성 스토어 필수. Redis가 온라인 스토어의 사실상 표준. Kafka + Flink가 실시간 특성 계산 스택으로 확립.

**소스 간 불일치:**
- 물질화(materialization) 전략: Feast·Tecton은 오프라인 → 온라인 순차 물질화. Qwak은 원본에서 직접 물질화. 각각 훈련-서빙 스큐 처리 방식이 다름.

---

## kw_006: model monitoring

**정의/핵심:**
- 프로덕션 ML 모델의 예측 품질·데이터 특성·시스템 건강 상태를 지속적으로 추적·평가하는 관행. 76%의 모델이 6개월 내 성능 저하 경험(Evidently AI).
- 모니터링 계층: 모델 품질 메트릭, 데이터 품질, 데이터 드리프트, 예측 드리프트.

**소스별 관점:**
- 086 (Evidently AI): 포괄적 가이드. 지연된 Ground Truth 문제 → 드리프트를 프록시 지표로 활용. ML 모니터링 아키텍처 5계층(수집→저장→계산→알림→시각화). 주요 도구: Evidently AI(오픈소스, 100+ 메트릭), WhyLabs, Arize AI, NannyML.
- 083 (Grafana): LLM 관찰가능성에 OpenTelemetry + Grafana Cloud 활용. 추적(traces), 메트릭(request volume, duration, cost/token) 모두 수집.
- 080 (OpenTelemetry): LLM 전용 신호: Temperature, top_p, 토큰 수, 비용, 응답 품질. OpenLIT 라이브러리로 자동 계측.

**소스 간 합의:**
- LLM 모니터링은 전통 ML 모니터링을 포함하며, 할루시네이션·비용·토큰 추적이 추가됨. OpenTelemetry가 벤더 중립 표준으로 부상.

**소스 간 불일치:**
- 없음.

---

## kw_007: data pipeline

**정의/핵심:**
- 데이터를 소스에서 추출·변환·목적지에 로드하는 프로세스 집합. ETL(변환 후 로드) vs ELT(로드 후 변환). 배치 vs 실시간 처리.

**소스별 관점:**
- 062 (Estuary): 5가지 설계 고려사항: 비용 최적화, 암호화·보안, 컴플라이언스, 확장성·성능, 유지보수성. Zero-ETL 트렌드(AWS Aurora, Snowflake no-copy sharing).
- 063 (Astronomer/Airflow): Airflow가 MLOps 파이프라인 오케스트레이션의 사실상 표준. LLMOps 세 기법(프롬프트 엔지니어링, RAG, 파인튜닝) 모두 Airflow로 조율 가능.
- 060 (Wix): Kafka+Flink 기반 실시간 파이프라인이 배치 ETL보다 AI 요구사항에 적합.
- 068 (Estuary/CDC): Log-Based CDC가 스트리밍 데이터 파이프라인의 핵심 패턴.

**소스 간 합의:**
- 실시간 데이터 파이프라인이 AI/ML 요구사항(특성 신선도, 즉시 예측)에 더 적합. 하이브리드(실시간 수집 + 배치 변환) 아키텍처가 현실적.

**소스 간 불일치:**
- 없음.

---

## kw_008: event-driven architecture

**정의/핵심:**
- 이벤트(불변 발생 기록)를 중심으로 서비스가 느슨하게 결합되는 아키텍처. 이벤트 브로커(Kafka)를 중심으로 pub/sub 패턴 사용.

**소스별 관점:**
- 021 (GoPubby): 전통 배치 ML과 이벤트 드리븐 ML 파이프라인 비교. 이벤트 드리븐: 저지연, 지속 학습, 특성 신선도, 독립 확장. 주식 예측 시스템 사례: 5분 대기 → 1초 응답.
- 121 (InfoQ/Chip Huyen): 요청 기반 아키텍처(REST) vs 이벤트 기반 아키텍처. 이벤트 기반은 서비스 간 직접 통신 불필요, 데이터 변환 이력을 스트림에서 직접 조회 가능.

**소스 간 합의:**
- ML 시스템에서 이벤트 드리븐 아키텍처가 지속 학습(continual learning)에 필수.

**소스 간 불일치:**
- 없음.

---

## kw_009: CI/CD for ML

**정의/핵심:**
- ML 모델 코드·데이터·파이프라인 컴포넌트의 자동화된 빌드·테스트·배포. 특정 이벤트(새 데이터, 성능 저하)에 의해 트리거.

**소스별 관점:**
- 004 (MadeWithML): GitHub Actions 기반 구현. workloads(PR 시 학습/검증), serve(main 병합 시 배포), documentation 워크플로 분리. Continual Learning 패턴: 코드 변경 → PR → 학습 → 성능 확인 → 병합 → 배포.
- 003 (LakeFS): CI/CD 자동화 단계: Pipeline CI(소스 코드·테스트→패키지·실행파일), Pipeline CD(아티팩트 배포→trained model in registry). 생산 환경에서 스케줄 또는 트리거로 자동 실행.

**소스 간 합의:**
- ML CI/CD는 코드뿐 아니라 데이터·모델 아티팩트·환경 버전 관리를 포함해야 함.

**소스 간 불일치:**
- 없음.

---

## kw_010: model registry

**정의/핵심:**
- ML 모델의 버전·메타데이터·계보(lineage)를 중앙에서 관리하는 저장소. 실험→스테이징→프로덕션 단계 전환 지원.

**소스별 관점:**
- 005 (MLflow): 개념 설명: Registered Model, Version, Alias(@champion), Tags. URI 형식: models:/MyModel@champion. Databricks Unity Catalog 통합으로 거버넌스 강화.
- 007 (apxml): 포괄적 버전 관리 전략: 코드(Git), 데이터(DVC/Pachyderm), 모델 아티팩트, 환경(Docker). Lineage를 DAG로 표현. 재현성·디버깅·규정 준수에 필수.

**소스 간 합의:**
- 모델 레지스트리는 MLOps의 중추. 코드 SHA, 데이터 해시, Docker 이미지 다이제스트, 하이퍼파라미터를 모두 연결해야 진정한 재현성 달성.

**소스 간 불일치:**
- 없음.

---

## kw_011: prompt management

**정의/핵심:**
- LLM 애플리케이션에서 프롬프트 템플릿의 버전 관리·A/B 테스트·모니터링·팀 협업을 다루는 LLMOps 실천 영역.

**소스별 관점:**
- 100 (PromptLayer): 주요 도구 5가지 비교: PromptLayer(비기술 팀원 친화, 협업 중심), Mirascope(파이썬 네이티브, 프로덕션급), LangSmith(LangChain 통합, 디버깅 강점), Agenta(프롬프트 엔지니어링+평가+관찰가능성 통합), Helicone(시맨틱 캐싱, 비용 추적).

**소스 간 합의:**
- 프롬프트 버전 관리는 코드 버전 관리와 동등한 중요성. A/B 테스트와 비용 추적이 핵심 기능.

**소스 간 불일치:**
- 없음.

---

## kw_012: RAG pipeline

**정의/핵심:**
- 검색 증강 생성(Retrieval-Augmented Generation): 외부 지식 베이스에서 관련 문서를 검색해 LLM에 컨텍스트로 제공. 벡터 검색 + 생성 결합.

**소스별 관점:**
- 101 (Coralogix): 프로덕션 RAG의 과제: 쿼리 다양성, 검색 정확도, 레이턴시(Google: 300ms 이하), 콘텐츠 신선도. 배포 레시피: 벡터 DB 샤딩/복제, Kafka 기반 비동기 문서 처리, HNSW/IVF-PQ 색인, Redis 캐싱.
- 025 (Kai Waehner): RAG용 벡터 DB + 의미 검색으로 LLM 할루시네이션 방지. 데이터 스트리밍으로 LLM에 최신 정보 공급.

**소스 간 합의:**
- 프로덕션 RAG는 단순 프로토타입과 달리 지속적인 인덱스 업데이트, 모니터링, 스케일 처리가 필요.

**소스 간 불일치:**
- 없음.

---

## kw_013: Kafka Streams

**정의/핵심:**
- Apache Kafka에 내장된 스트림 처리 클라이언트 라이브러리. 별도 클러스터 없이 표준 Java/Scala 앱에 임베드. KStream, KTable 추상화 제공. Exactly-once 지원.

**소스별 관점:**
- 032 (Confluent): 로컬 상태 스토어(RocksDB), 고수준 DSL(필터링·맵핑·집계·조인·윈도잉). 낮은 진입 장벽.
- 022 (Confluent): Flink vs Kafka Streams 비교. Kafka Streams: 임베드 가능 라이브러리, Kafka 브로커가 코디네이션 담당, 제품팀 소유에 적합. Flink: 클러스터 프레임워크, 데이터 인프라팀 소유에 적합. 상호 보완적 시스템.
- 067 (Confluent/CDC): Debezium + Kafka Streams로 MongoDB CDC 처리: KStream(변경 이벤트) + KTable(최신 상태 유지) 결합.

**소스 간 합의:**
- Kafka Streams는 마이크로서비스 내 임베드 스트림 처리에 최적. Flink는 대규모 독립 클러스터 처리에 적합.

**소스 간 불일치:**
- 없음.

---

## kw_014: stream processing

**정의/핵심:**
- 연속적(unbounded) 데이터 스트림을 실시간으로 처리하는 패러다임. 배치 처리의 특수한 경우로도 볼 수 있음(스트리밍 우선 인프라).

**소스별 관점:**
- 022 (Confluent): Apache Flink: 클러스터 기반, 수천만 이벤트/초, 서브초 지연. Kafka Streams: 앱 내 라이브러리, Kafka와 밀착 통합.
- 025 (Kai Waehner): 원격 추론(Kafka + Flink + OpenAI API) vs 임베디드 추론(TensorFlow 모델 Flink 앱 내 직접 탑재) 패턴.
- 121 (InfoQ/Chip Huyen): 배치 처리는 스트리밍의 특수 케이스. 스트리밍 우선 인프라로 훈련·추론 파이프라인 통합 권장. Weibo: 10분 주기 모델 업데이트.

**소스 간 합의:**
- 스트리밍 처리가 ML 특성 신선도와 지속 학습의 핵심 인프라.

**소스 간 불일치:**
- 없음.

---

## kw_015: experiment tracking

**정의/핵심:**
- ML 실험의 하이퍼파라미터, 메트릭, 아티팩트, 코드·데이터 버전을 체계적으로 기록·비교하는 도구와 관행.

**소스별 관점:**
- 006 (DagsHub): 주요 도구 비교: MLflow(오픈소스, 언어 무관, 대규모 커뮤니티), DVC(Git 연동, 데이터·코드·아티팩트 버전 관리), ClearML(자동 로깅, GPU/CPU 추적), W&B(시각화 강점, 하이퍼파라미터 최적화 내장), Comet(실시간 차트, 협업 기능).
- 120 (Introl): LLM 파인튜닝 실험 추적: Axolotl(YAML 설정), LLaMA-Factory, HuggingFace PEFT. W&B 또는 MLflow로 재현성 확보.

**소스 간 합의:**
- MLflow가 가장 널리 채택된 오픈소스 표준. W&B는 시각화와 협업에서 강점.

**소스 간 불일치:**
- 없음.

---

## kw_016: LLM fine-tuning

**정의/핵심:**
- 사전 훈련된 LLM을 특정 도메인·태스크에 맞게 추가 학습. PEFT(Parameter-Efficient Fine-Tuning) 방법론으로 비용 10-20배 절감.
- 주요 기법: LoRA(저랭크 적응), QLoRA(4비트 양자화 + LoRA), Adapters, Prefix Tuning.

**소스별 관점:**
- 120 (Introl): LoRA: 7B 모델 파인튜닝에 24-32GB VRAM, 풀 파인튜닝 품질의 90-95%. QLoRA: 12-20GB VRAM으로 가능, 80-90% 품질. 최소 유효 데이터셋: 1,000-5,000개 고품질 예시. 어댑터 병합으로 추론 오버헤드 제거.
- 125 (SuperAnnotate): RLHF 3단계(선호도 데이터셋 → 보상 모델 → PPO 기반 파인튜닝). DPO가 PPO 대비 단순하고 성능 동등. 2025년 기업의 70%가 RLHF 또는 DPO 채택.

**소스 간 합의:**
- PEFT(특히 LoRA/QLoRA)가 LLM 파인튜닝의 사실상 표준. 완전 재훈련은 대부분 불필요.

**소스 간 불일치:**
- 없음.

---

## kw_017: vector database

**정의/핵심:**
- 벡터 임베딩을 저장하고 근사 최근접 이웃(ANN) 검색을 수행하는 특화 데이터베이스. RAG, 시맨틱 검색의 핵심 인프라.

**소스별 관점:**
- 102 (LiquidMetal): 2025년 주요 솔루션 비교: Pinecone(완전 관리형, 대규모 확장성), Weaviate(지식 그래프, 다중 모달), Qdrant(Rust 기반 고성능, 메타데이터 필터링), FAISS(연구용, 최고 성능), Milvus(클라우드 네이티브, 대규모), Chroma(RAG 프로토타이핑 최적).
- 101 (Coralogix): RAG 배포에서 벡터 DB: HNSW/IVF-PQ 색인, Redis 인메모리 캐싱, 제로 다운타임 재색인 필요.

**소스 간 합의:**
- Qdrant가 비용 대비 성능 최적. Pinecone은 관리형 엔터프라이즈에 적합. Chroma는 빠른 프로토타이핑에 적합.

**소스 간 불일치:**
- 없음.

---

## kw_018: Kafka Connect

**정의/핵심:**
- Apache Kafka의 데이터 통합 프레임워크. Source 커넥터(외부→Kafka)와 Sink 커넥터(Kafka→외부)로 이루어짐. 내결함성·확장성 제공.

**소스별 관점:**
- 023 (Debezium): Debezium이 Kafka Connect 기반 CDC 커넥터. MySQL(binlog), PostgreSQL(논리 복제), MongoDB 등 지원. 테이블당 하나의 Kafka 토픽으로 매핑. 폴트 톨러런트 스토리지, 확장성, Elasticsearch/데이터 웨어하우스 싱크 지원.
- 068 (Estuary): Kafka Connect = Source 커넥터 + Sink 커넥터. Debezium이 Log-Based CDC 커넥터. 폴트 톨러런스: 커넥터 충돌 시 Kafka Connect가 재스케줄.

**소스 간 합의:**
- Kafka Connect + Debezium = 엔터프라이즈 CDC의 표준 조합.

**소스 간 불일치:**
- 없음.

---

## kw_019: model deployment

**정의/핵심:**
- 훈련된 모델을 프로덕션 환경에서 예측 요청을 처리할 수 있는 상태로 배포하는 과정. 전략: 블루-그린, 카나리, 섀도우, A/B 테스트.

**소스별 관점:**
- 046 (OneUptime): 블루-그린(리소스 2배 사용, 즉각 롤백)과 카나리(1.1배 리소스, 단계적 노출) 비교. Argo Rollouts로 자동화: AnalysisTemplate으로 Prometheus 메트릭 기반 자동 프로모션/롤백.
- 089 (MarkTechPost): 4가지 전략 비교(A/B, 카나리, 인터리빙, 섀도우). 사용자 안전 최우선 → 섀도우 후 카나리. 통계적 엄밀성 → A/B.
- 040 (Civo): Kubernetes LLM 배포: GPU 클러스터, 재현 가능 컨테이너, HPA, 옵저버빌리티, 보안, 비용.
- 045 (PremAI): vLLM(단일 노드), Ray Serve(멀티 노드, 멀티 모델), llm-d(대규모 분리 서빙).

**소스 간 합의:**
- 카나리 배포가 리스크/리소스 균형에서 가장 널리 추천. Argo Rollouts이 메트릭 기반 자동 롤아웃 표준.

**소스 간 불일치:**
- 없음.

---

## kw_020: data drift

**정의/핵심:**
- 프로덕션 입력 데이터의 통계적 분포가 훈련 데이터와 달라지는 현상. 데이터 드리프트(P(X) 변화) vs 개념 드리프트(P(Y|X) 변화) 구분 중요.

**소스별 관점:**
- 087 (Evidently AI): 데이터 드리프트 vs 개념 드리프트 vs 훈련-서빙 스큐 세분화. 감지 방법: KS 테스트(소규모 데이터), PSI(대규모, 임계값 명확), 와서스타인 거리(균형적), KL 발산, JS 발산.
- 088 (Evidently AI): 5가지 방법 대규모 데이터 비교 실험. KS는 100K 이상에서 과민반응. PSI는 10% 이상 드리프트만 탐지. WD가 KS와 PSI의 균형점.
- 122 (Enhanced MLOps): 드리프트 감지 후 대응: 예약 재훈련 vs 이벤트 기반 재훈련. 두 전략 결합 권장.

**소스 간 합의:**
- 단일 드리프트 감지 방법은 없음. 데이터셋 크기와 허용 가능한 드리프트 크기에 따라 방법 선택.

**소스 간 불일치:**
- 없음.

---

## kw_021: ksqlDB

**정의/핵심:**
- 모션 데이터(스트리밍 데이터)를 위해 특화된 데이터베이스. SQL 문법으로 스트리밍 앱 구축. Kafka Streams 위에서 구동. 스트림(KStream)과 테이블(KTable) 지원.

**소스별 관점:**
- 024 (Confluent): Push 쿼리(EMIT CHANGES로 연속 스트림 반환) vs Pull 쿼리(현재 상태 반환). 집계(COUNT, SUM 등)→테이블 생성. 스트림·테이블 병합·분할 가능. 내부적으로 Kafka Connect 커넥터 직접 실행.

**소스 간 합의:**
- ksqlDB는 ML 특성 계산을 SQL로 수행할 수 있는 저진입 스트리밍 데이터베이스.

**소스 간 불일치:**
- 없음.

---

## kw_022: LLM evaluation

**정의/핵심:**
- LLM 출력의 품질(관련성, 신실성, 안전성)을 자동화된 방법으로 평가. LLM-as-a-judge, RAGAS, DeepEval 등 프레임워크 활용.

**소스별 관점:**
- 103 (GoCodEo): 5대 프레임워크: RAGAS(RAG 파이프라인 평가, 레퍼런스 없이 평가 가능, Context Precision/Recall/Faithfulness/Answer Relevance), RAGXplain(설명 가능성 강점), ARES(맞춤 평가 스키마), RAGEval(도메인 특화 테스트 스위트), DeepEval(Pytest 스타일, CI/CD 통합).
- 104 (Datadog): 할루시네이션 감지: LLM-as-a-judge 방식. 루브릭 기반 접근법(모순 + 미지원 주장 탐지). 구조화 출력(FSM)으로 유효 JSON 강제. HaluBench F1: 0.844, RAGTruth F1: 0.810.
- 010 (ZenML): LLMOps 테스트: 황금 데이터셋(15-20개 고신호 테스트), LLM-as-judge + 인간 피드백 혼합.

**소스 간 합의:**
- LLM 평가는 비결정론적이므로 자동 메트릭과 인간/LLM 판단을 결합해야 함.

**소스 간 불일치:**
- 없음.

---

## kw_023: Apache Flink

**정의/핵심:**
- 자체 클러스터에서 동작하는 분산 스트림 처리 프레임워크. 수천만 이벤트/초 처리, 서브초 레이턴시, 정확히 한 번(exactly-once) 보장.

**소스별 관점:**
- 022 (Confluent): Flink: 클러스터 프레임워크(YARN, Mesos, K8s), 배치+스트리밍 모두 지원, 세이브포인트, FlinkML, Flink SQL/Table API. Kafka Streams와 상호 보완.
- 025 (Kai Waehner): Flink + Kafka 조합으로 예측 AI와 생성 AI 모두 지원. Flink SQL UDF로 OpenAI API 호출(원격 추론). TensorFlow 모델 Flink 앱 내 임베딩(임베디드 추론).
- 060 (Wix): Confluent Cloud 서버리스 Flink, FlinkSQL, 상태 저장 처리로 실시간 특성 스토어 구현.

**소스 간 합의:**
- Flink가 대규모 실시간 ML 특성 계산 및 추론 파이프라인의 사실상 표준.

**소스 간 불일치:**
- 없음.

---

## kw_024: model versioning

**정의/핵심:**
- 모델 아티팩트·코드·데이터·환경을 체계적으로 버전 관리해 재현성·감사·롤백을 가능하게 하는 관행. Lineage: 코드→데이터→모델 간 DAG 연결.

**소스별 관점:**
- 007 (apxml): 포괄적 버전 관리 4요소: 코드(Git 커밋 SHA), 데이터(DVC/Pachyderm 또는 불변 스냅샷), 모델 아티팩트(MLflow/SageMaker 저장), 환경(Docker 이미지 다이제스트). Lineage를 DAG로 표현. 과제: 확장성, 세분화 수준, 도구 통합, 규율.

**소스 간 합의:**
- Git 커밋 해시만으로는 불충분. 데이터 버전·환경·실험 런을 모두 연결해야 진정한 재현성 달성.

**소스 간 불일치:**
- 없음.

---

## kw_025: online learning

**정의/핵심:**
- 새 데이터가 도착할 때마다 모델을 점진적으로 업데이트하는 학습 방식. 미니배치(500-1000개) 기반 업데이트가 현실적.

**소스별 관점:**
- 121 (InfoQ/Chip Huyen): 지속 학습(continual learning)의 실제 구현: 프로덕션 모델 직접 업데이트 대신 복제본 업데이트 후 평가 통과 시 배포. 이벤트 드리븐 마이크로서비스 아키텍처가 적합. Weibo: 10분 주기. TikTok: 세션 내 사용자 선호도 적응.
- 126 (Future Generation CS): Kafka-ML 프레임워크: Kafka 위에서 ML 파이프라인 관리. 온라인 학습 확장: 성능 개선 시 자동으로 개선된 모델 버전 배포. 중앙화·분산 모델 구성 모두 지원.

**소스 간 합의:**
- 온라인 학습은 이벤트 드리븐 아키텍처 + 스트리밍 인프라(Kafka) 위에서 가장 효과적으로 구현.

**소스 간 불일치:**
- 없음.

---

## kw_026: Kafka consumer group

**정의/핵심:**
- 동일 태스크를 공유하는 소비자 집합. 파티션이 소비자에 배타적으로 할당되어 병렬 처리 구현. 오프셋 관리로 at-least-once/exactly-once 구현.

**소스별 관점:**
- 029 (Confluent): 오프셋 = 파티션 내 메시지 위치. __consumer_offsets 토픽에 저장. Leader Epoch를 함께 커밋해야 zombie leader 문제 방지. KIP-1094(Kafka 4.0): nextOffsets API로 정확한 오프셋 커밋 지원.
- 028 (OneUptime): 백프레셔 발생 시 partition pausing API 활용. 핵심 설정: max.poll.records=100, max.poll.interval.ms=300000, enable.auto.commit=false.
- 020 (Instaclustr): 소비자 수 > 파티션 수이면 일부 소비자 비활성. CooperativeStickyAssignor로 리밸런싱 시 다운타임 최소화.

**소스 간 합의:**
- 소비자 그룹 = Kafka 기반 ML 추론 수평 확장의 핵심 메커니즘.

**소스 간 불일치:**
- 없음.

---

## kw_027: A/B testing ML

**정의/핵심:**
- 두 모델 변형에 프로덕션 트래픽을 무작위 분할해 실제 성능 비교. Champion(현 모델) vs Challenger(신 모델) 패턴.

**소스별 관점:**
- 082 (MLOps Community): OEC(Overall Evaluation Criterion) 사전 정의, delta(최소 탐지 효과 크기), alpha(유의수준), beta(검정력), n(최소 샘플 크기) 결정이 핵심. 멀티암드 밴딧: 탐색-착취 균형.
- 084 (DataRobot): 챔피언/챌린저 패턴: DataRobot은 챔피언이 100% 트래픽 서빙, 챌린저는 같은 요청 재생으로 분석(A/B와 다름). 엄격한 승인 워크플로.
- 089 (MarkTechPost): 4가지 전략 비교. 사용자 메트릭 필요 → A/B 또는 인터리빙. 랭킹 시스템 → 인터리빙. 안전 최우선 → 섀도우.

**소스 간 합의:**
- A/B 테스트는 통계적 엄밀성 필요 시. 섀도우 배포는 사용자 영향 없이 검증 시. 카나리는 점진적 안전 배포 시.

**소스 간 불일치:**
- DataRobot의 챔피언/챌린저는 순수 트래픽 분할 A/B가 아닌 재생(replay) 방식.

---

## kw_028: observability

**정의/핵심:**
- 시스템의 내부 상태를 외부 출력(로그, 메트릭, 트레이스)으로 추론하는 능력. LLM 관찰가능성은 전통 APM에 더해 토큰 비용·할루시네이션·프롬프트 효과를 포함.

**소스별 관점:**
- 080 (OpenTelemetry): OpenTelemetry가 LLM 관찰가능성의 벤더 중립 표준. 추적(traces): Temperature, top_p, 모델 버전, 프롬프트 세부사항. 메트릭: 요청 볼륨, 레이턴시, 비용/토큰.
- 083 (Grafana): OpenLIT SDK로 자동 계측 → Grafana Cloud 시각화. 환경 변수 OTEL_EXPORTER_OTLP_ENDPOINT로 설정.
- 086 (Evidently AI): 모니터링 vs 관찰가능성 구분: 모니터링은 사전 정의된 메트릭 추적, 관찰가능성은 임의 질의로 시스템 동작 이해.

**소스 간 합의:**
- OpenTelemetry + Prometheus/Grafana 스택이 ML/LLM 관찰가능성의 표준으로 확립.

**소스 간 불일치:**
- 없음.

---

## kw_029: schema registry (Kafka 데이터 직렬화 형식)

**정의/핵심:**
- Kafka 메시지의 데이터 스키마를 중앙 관리하는 레지스트리. 생산자-소비자 간 스키마 계약(contract) 역할. 버전 호환성 규칙 강제.
- 주요 형식: Avro(유연한 스키마 진화, 빅데이터 생태계), Protobuf(최고 성능, gRPC), JSON Schema(인간 가독성).

**소스별 관점:**
- 030 (AutoMQ): Avro vs JSON Schema vs Protobuf 상세 비교. Binary 형식(Avro, Protobuf)은 JSON 대비 50-80% 작은 메시지, 빠른 직렬화. Avro: 동적 타이핑 지원, 후방/전방 호환성 우수. Protobuf: 5% 더 높은 처리량, 필드 번호로 이진 데이터 관리, gRPC 시스템에 최적.
- 031 (Confluent): Confluent Schema Registry가 Avro, JSON Schema, Protobuf 지원. 버전 추적, 호환성 설정 강제.

**소스 간 합의:**
- 프로덕션 Kafka에는 Schema Registry + 이진 형식(Avro/Protobuf) 사용이 표준.

**소스 간 불일치:**
- 없음.

---

## kw_030: Kubernetes for ML/LLM

**정의/핵심:**
- LLM/ML 워크로드를 위한 컨테이너 오케스트레이션. GPU 스케줄링, 오토스케일링, 다중 테넌시, 보안이 핵심 과제.

**소스별 관점:**
- 040 (Civo): 8가지 배포 기둥. GPU 노드: NVIDIA A100/H100, MIG로 소형 모델 병렬 실행, 노드 어피니티/테인트로 GPU/CPU 분리.
- 045 (PremAI): NVIDIA GPU Operator(v25.10.1): GPU 자동 발견, MIG 파티셔닝, DCGM 익스포터. Gateway API Inference Extension(2026년 2월 GA): 모델 인식 라우팅, KV 캐시 인식 스케줄링.
- 047 (debugg.ai): Kueue(기업 멀티 테넌트 큐·할당량), Volcano(HPC급 배치 학습), MIG(하드웨어 격리 추론), MPS(레이턴시 허용 처리량 최대화). 권장: 프로덕션 추론에 MIG, 개발/실험에 MPS.
- 048 (RedHat): OpenShift AI + Ray Data + vLLM + CodeFlare SDK로 배치 추론 구현.

**소스 간 합의:**
- Kubernetes + NVIDIA GPU Operator가 2025년 LLM 프로덕션 배포 표준.

**소스 간 불일치:**
- 없음.

---

## kw_031: MLflow

**정의/핵심:**
- ML 수명 주기 전반(실험 추적, 프로젝트 패키징, 모델 저장, 레지스트리)을 관리하는 오픈소스 플랫폼.

**소스별 관점:**
- 005 (MLflow 공식): 4대 컴포넌트: Tracking(실험·런 로깅), Projects(재현 가능 패키징), Models(표준화 형식), Model Registry(버전 관리·별칭). Databricks Unity Catalog 통합으로 거버넌스 강화.
- 006 (DagsHub): 강점: 언어·프레임워크 무관, 자동 로깅, 웹 UI, 로컬/원격 서버 모두 지원. 약점: 관리형 서비스 없음, 보안 기능 기본 제공 미흡.

**소스 간 합의:**
- MLflow는 오픈소스 ML 실험 관리·모델 레지스트리의 사실상 표준.

**소스 간 불일치:**
- 없음.

---

## kw_032: LangChain

**정의/핵심:**
- LLM 기반 애플리케이션 구축을 위한 오픈소스 오케스트레이션 프레임워크. RAG, 에이전트, 멀티스텝 추론, 도구 호출 지원.

**소스별 관점:**
- 105 (NexaStack): 엔터프라이즈 배포 4단계(전략 평가→솔루션 개발→엔터프라이즈 통합→제어 배포). 사례: 제조업체 정보 검색 시간 45분→30초, 금융사 대출 처리 2일→2시간, 소매업체 LLM 비용 $50K→$12K/월.
- 063 (Astronomer): LangChain RAG 파이프라인을 Airflow로 오케스트레이션 가능.

**소스 간 합의:**
- LangChain은 엔터프라이즈 LLM 앱 프로덕션화의 핵심 프레임워크. 거버넌스·보안·감사 로그가 엔터프라이즈 배포의 필수 요소.

**소스 간 불일치:**
- 없음.

---

## kw_033: automated retraining

**정의/핵심:**
- 성능 저하·드리프트 감지 시 모델을 수동 개입 없이 자동으로 재훈련하는 MLOps 파이프라인 구성요소.

**소스별 관점:**
- 122 (Enhanced MLOps): 예약 재훈련(단순, 예측 가능) vs 이벤트 기반 재훈련(효율, 적시) 비교. 혼합 전략 권장. 도구: MLflow, Kubeflow Pipelines, Airflow, SageMaker.
- 123 (SEI/CMU): 현행 MLOps 한계: 단순히 새 데이터로 기존 모델 재피팅. 분석 없는 재훈련은 미래 예측 오차 증가. SEI의 model operational analysis module: analyze→audit→select 자동화.
- 124 (314e): 자기 개선 ML 시스템 청사진(Dexit): 사용자 수정 캡처 → 성능 저하 감지 → 스마트 데이터셋 생성(계층화 샘플링) → 재훈련 → V1 vs V2 평가 → 배포. 적응형 임계값: V2 기준 성능으로 재훈련 임계값 업데이트.
- 126 (Future Gen CS): Kafka-ML: 스트림을 통한 온라인 학습. 성능 개선 시 자동 모델 버전 배포.

**소스 간 합의:**
- 단순 재피팅이 아닌 드리프트 분석 기반 지능형 재훈련이 권장. 인간 감독은 여전히 필요.

**소스 간 불일치:**
- 123(SEI)은 현행 MLOps의 단순 재피팅 접근법에 비판적. 다른 소스들은 현행 방식의 점진적 개선을 논함.

---

## kw_034: Confluent Platform

**정의/핵심:**
- Apache Kafka 원작자들이 만든 엔터프라이즈급 스트리밍 플랫폼. Kafka 핵심 + Schema Registry, Kafka Connect, ksqlDB, Flink, REST Proxy 포함.

**소스별 관점:**
- 031 (Confluent): 주요 추가 기능: Schema Registry(Avro/JSON/Protobuf 관리), Cluster Linking(클러스터 직접 연결), 100+ 사전 빌드 커넥터, ksqlDB, Tiered Storage, Self-Balancing Clusters(자동 부하 분산). 보안: RBAC, SSO, 감사 로그.

**소스 간 합의:**
- Confluent Platform은 오픈소스 Kafka의 엔터프라이즈 확장판.

**소스 간 불일치:**
- 없음.

---

## kw_035: batch inference

**정의/핵심:**
- 대량 데이터셋에 대해 일괄로 모델 예측을 수행. 레이턴시보다 전체 완료 시간과 처리량이 중요. 온라인 추론과 대비.

**소스별 관점:**
- 041 (Anyscale): Ray Data vs Spark vs SageMaker 배치 추론 비교. Ray Data: SageMaker 대비 17배, Spark 대비 2배 빠른 처리량. GPU+CPU 하이브리드 워크로드에서 Ray의 독립 스케일링이 핵심 차별점. 10TB 데이터, 10K GPU 이상에서 선형 확장.
- 048 (RedHat): OpenShift AI + CodeFlare SDK + Ray Data + vLLM 조합. vLLMEngineProcessorConfig: concurrency=GPU 수, batch_size, tensor_parallel_size 설정.

**소스 간 합의:**
- Ray Data가 현재 배치 추론 성능과 사용성에서 최우수.

**소스 간 불일치:**
- 없음.

---

## kw_036: LLM optimization (inference speedup)

**정의/핵심:**
- LLM 추론의 속도·메모리·비용을 최적화하는 기술. 양자화(quantization), 가지치기(pruning), 지식 증류(distillation), 투기적 디코딩(speculative decoding).

**소스별 관점:**
- 042 (Introl): 투기적 디코딩: 소형 드래프트 모델이 5-8토큰 제안 → 대형 모델이 병렬 검증. 2-3배 속도 향상. EAGLE 방법: 80% 수용률, 2.5-2.8배 가속. TensorRT-LLM+FP8: 3.6배 처리량.
- 043 (CAST AI): 양자화 방법: GPTQ(4비트, Hessian 기반), SmoothQuant(W8A8, 배치 처리에 적합), AWQ(W4A16, 4비트에서 최고 정확도), GGUF(CPU/엣지 배포용 파일 형식). INT8은 FP32 대비 에너지 효율 30배.
- 044 (NVIDIA): 가지치기(구조적): 깊이 가지치기(레이어 제거)와 너비 가지치기(뉴런/어텐션 헤드 제거). 지식 증류로 Qwen3 8B → 6B: MMLU 72.5(원본 70.0 초과), 추론 속도 30% 향상.

**소스 간 합의:**
- AWQ가 GPU 프로덕션 4비트 서빙의 SOTA. 투기적 디코딩이 인터랙티브 채팅 지연 최소화에 효과적.

**소스 간 불일치:**
- 없음.

---

## kw_037: pipeline orchestration

**정의/핵심:**
- ML/데이터 파이프라인의 태스크 의존성, 스케줄링, 모니터링, 오류 처리를 자동화하는 도구.

**소스별 관점:**
- 063 (Astronomer): Airflow의 MLOps 강점: Python 네이티브, 확장 가능, 플러그인 생태계(1,000+ 오퍼레이터), 데이터 기반 스케줄링(Airflow Datasets), 동적 태스크 매핑.
- 064 (ZenML): Airflow vs Dagster vs Prefect 비교. Airflow: 가장 큰 커뮤니티(37K 스타), 배치 검증 확장성. Dagster: 소프트웨어 정의 에셋(SDA), 데이터 리니지, 테스트 우수. Prefect: Pythonic, 동적 워크플로, 빠른 시작.
- 066 (Bixtech): Great Expectations와 Airflow 통합: 각 스테이지 완료 시 체크포인트 실행.

**소스 간 합의:**
- Airflow가 가장 널리 사용. MLOps에서는 Dagster의 에셋 중심 접근이 데이터 리니지 측면에서 유리.

**소스 간 불일치:**
- 없음.

---

## kw_038: LLM guardrails

**정의/핵심:**
- LLM 출력의 안전성·정확성·규정 준수를 보장하는 통제 메커니즘. 입력 가드레일(프롬프트 인젝션 방지)과 출력 가드레일(할루시네이션 감지, PII 마스킹).

**소스별 관점:**
- 110 (Medium): 주요 프레임워크: NeMo Guardrails(NVIDIA, Colang DSL, 대화형 AI에 최적), Llama Guard(Meta, 멀티 카테고리 안전 분류, 낮은 지연), Guardrails AI(오픈소스, 구조화 출력 검증). 77%의 기업이 GenAI 침해 경험(IBM 2025).
- 002 (TrueFoundry): LLMOps의 보안 위험: 프롬프트 인젝션, 유해 콘텐츠 생성, 데이터 유출.
- 010 (ZenML): 가드레일이 LLMOps 배포 전 필수 안전 필터.

**소스 간 합의:**
- 다층 가드레일(입력+대화+출력) 접근이 권장. 안전성과 사용자 경험 균형 필요.

**소스 간 불일치:**
- 없음.

---

## kw_039: LLM cost optimization

**정의/핵심:**
- LLM 추론 비용을 최소화하면서 품질을 유지하는 전략. 토큰 최적화, 모델 라우팅, 캐싱, 양자화, 배치 처리 조합.

**소스별 관점:**
- 106 (Glukhov): 프롬프트 효율화로 70% 토큰 절감 가능. 컨텍스트 캐싱(OpenAI/Anthropic): 캐시 비용 50-90% 절감. 모델 라우팅(80% GPT-3.5, 20% GPT-4): 비용 75% 절감. 실사례: $4,200/월 → $780/월(81% 절감).
- 107 (Koombea): 80% 비용 절감 가능. 폭포식 모델 선택(Mistral 7B → GPT-4), LLMLingua로 20배 압축, 증류·양자화, 자체 호스팅(월 100만 쿼리 이상 시 비용 효과). RAG로 컨텍스트 크기 축소(15K → 4.5K 토큰).

**소스 간 합의:**
- 아웃풋 토큰이 인풋 대비 2-5배 비쌈. 모델 라우팅이 가장 큰 비용 절감 레버. 시맨틱 캐싱이 반복 워크로드에 효과적.

**소스 간 불일치:**
- 없음.

---

## kw_040: data quality

**정의/핵심:**
- 데이터 파이프라인 내 데이터의 정확성·완전성·일관성·신선도를 자동으로 검증하고 문서화하는 관행. ML에서 "쓰레기 입력 → 쓰레기 출력" 방지.

**소스별 관점:**
- 065 (Great Expectations): 데이터 품질은 ML Ops의 적 #1. 훈련·서빙 양쪽에서 나쁜 데이터가 두 배로 나쁜 결과를 초래.
- 066 (Bixtech): Great Expectations(GX): 기대치(expectations) 정의 → 검증 → Data Docs 자동 생성. 테이블 레벨(행 수, 신선도), 스키마 레벨, 컬럼 레벨, 비즈니스 규칙 레벨 검증. mostly 파라미터로 허용 오차 설정.

**소스 간 합의:**
- 데이터 검증이 ML 파이프라인의 모든 단계(수집→훈련→프로덕션)에서 필수.

**소스 간 불일치:**
- 없음.

---

## kw_041: shadow deployment

**정의/핵심:**
- 프로덕션 트래픽을 신규 모델에 미러링하여 사용자에게 노출 없이 실제 환경에서 테스트하는 배포 전략.

**소스별 관점:**
- 081 (Microsoft): 섀도우 테스팅 = "트래픽 미러링". V-Current에서 V-Next로 동일 트래픽 복제. V-Next 응답은 수집만 하고 사용자에게 반환 안 함. 인프라 스케일링 테스트에 적합. Diffy 도구: Twitter, Airbnb, Baidu에서 사용.
- 085 (Deepchecks): 섀도우 vs 카나리 명확 구분. 섀도우: 사용자 영향 없음, 리소스 2배. 카나리: 실제 사용자 일부에게 점진적 노출.
- 089 (MarkTechPost): 섀도우의 한계: 사용자 인터랙션 메트릭(클릭률) 측정 불가. 부작용(DB 쓰기, 알림) 방지 필수.

**소스 간 합의:**
- 섀도우 배포가 가장 안전한 ML 모델 검증 방법. 단, 리소스 2배와 사용자 메트릭 불가 트레이드오프.

**소스 간 불일치:**
- 없음.

---

## kw_042: CDC (Change Data Capture)

**정의/핵심:**
- 데이터베이스의 삽입·수정·삭제 변경을 실시간으로 캡처해 다운스트림 시스템에 전파하는 기술. Log-Based CDC가 성능·비침투성 측면에서 우수.

**소스별 관점:**
- 067 (Confluent): Debezium + Kafka Streams로 MongoDB CDC 처리. 스트림(변경 이벤트)과 테이블(현재 상태)의 이중 추상화. 병합 함수: create/read(after 문서 사용), delete(null 반환), update(패치 적용).
- 068 (Estuary): CDC 2가지: Query-Based(DB 쿼리), Log-Based(트랜잭션 로그 읽기). Debezium: Log-Based, MySQL binlog/PostgreSQL 논리 복제 사용. 배포 3가지: 독립 서버, 앱 내 임베드, Kafka Connect 서비스(엔터프라이즈 권장).

**소스 간 합의:**
- CDC + Kafka는 레거시 DB를 ML 실시간 데이터 소스로 전환하는 표준 패턴.

**소스 간 불일치:**
- 없음.

---

## kw_043: LLM gateway

**정의/핵심:**
- 애플리케이션과 LLM 제공자 사이의 지능형 게이트웨이. 통합 인터페이스, 장애 조치, 비용 추적, 로드밸런싱, 캐싱 제공.

**소스별 관점:**
- 108 (Helicone): 5대 LLM 게이트웨이 비교: Helicone(Rust, 8ms P50 레이턴시, 40% 레이턴시 감소), OpenRouter(빠른 설정, 5% 마크업), Portkey(엔터프라이즈 보안), LiteLLM(오픈소스, +50ms 지연), Unify(단순 라우팅).
- 109 (Kong): 벤치마크: Kong이 Portkey 대비 228% 빠름, LiteLLM 대비 859% 빠름. Kong이 65% 낮은 레이턴시.

**소스 간 합의:**
- LLM 게이트웨이가 멀티 LLM 프로덕션 운영의 필수 인프라. 성능 차이가 크므로 벤치마크 기반 선택 필요.

**소스 간 불일치:**
- 없음.

---

## kw_044: RLHF

**정의/핵심:**
- 인간 피드백을 통한 강화학습. 선호도 데이터 → 보상 모델 → PPO 파인튜닝 3단계. LLM을 인간 가치·선호도에 정렬하는 핵심 기법.

**소스별 관점:**
- 125 (SuperAnnotate): RLHF 3단계 상세 설명. 대안: DPO(분류 손실만 사용, PPO 대비 단순하고 성능 동등), RLAIF(LLM이 인간 주석자 대체), ReST(오프라인 샘플링), 세분화 RLHF(문장 단위 밀집 보상).
- 124 (314e): 실제 사용 피드백(사용자 수정)을 고품질 RLHF 신호로 활용해 자동 재훈련 트리거.

**소스 간 합의:**
- DPO가 2025년 RLHF를 대체하는 주류 기법으로 자리잡음. 2025년 기업 70%가 RLHF 또는 DPO 채택.

**소스 간 불일치:**
- 없음.

---

## kw_045: Kafka exactly-once semantics

**정의/핵심:**
- 재시도가 있더라도 메시지가 정확히 한 번만 전달·처리되는 보장. 멱등성 생산자 + 트랜잭션 API + 정확히 한 번 스트림 처리로 구성.

**소스별 관점:**
- 026 (Confluent/Neha Narkhede): 정확히 한 번 구현 3요소: 1) 멱등성(enable.idempotence=true, 시퀀스 번호 기반 중복 제거), 2) 트랜잭션(여러 파티션에 원자적 쓰기, read_committed/read_uncommitted 격리 수준), 3) Kafka Streams(processing.guarantee=exactly_once). 성능: 트랜잭션 생산자는 at-least-once 대비 3% 처리량 감소.
- 029 (Confluent): EOS에서 오프셋을 트랜잭션 내 원자적으로 커밋(sendOffsetsToTransaction). Leader Epoch를 함께 저장해 zombie leader 시나리오 방지.

**소스 간 합의:**
- Kafka의 정확히 한 번 보장은 ML 파이프라인의 데이터 정확성에 필수.

**소스 간 불일치:**
- 없음.

---

## kw_046: model compression

**정의/핵심:**
- LLM 모델 크기·메모리·레이턴시를 줄이는 기술군: 양자화(quantization), 가지치기(pruning), 지식 증류(knowledge distillation).

**소스별 관점:**
- 043 (CAST AI): 양자화 역사와 LLM별 방법 심층 설명. GGUF는 직렬화 형식이지 양자화 방법이 아님. i-quants(IQ3_S 등)이 최신 GGML 권장.
- 044 (NVIDIA TensorRT Model Optimizer): 깊이 가지치기(레이어 제거, 레이턴시 감소 효과적)와 너비 가지치기(뉴런 제거, 정확도 유지 효과적). 응답 기반 증류(soft labels, KL divergence), 특성 기반 증류(중간 표현 정렬).

**소스 간 합의:**
- 양자화+가지치기+증류 결합이 최대 효율 달성. AWQ가 GPU 서빙 4비트 SOTA, GGUF가 CPU/엣지 표준.

**소스 간 불일치:**
- 없음.

---

## kw_047: Infrastructure as Code (IaC)

**정의/핵심:**
- 인프라를 코드로 정의·버전 관리하는 방법론. 선언적 접근으로 동일 환경 반복 생성 보장. GitOps 실천의 핵심.

**소스별 관점:**
- 008 (Medium): Terraform 핵심: HCL 선언적 설정, 다중 클라우드 지원, 상태 파일(terraform.tfstate). 워크플로: init → validate → plan → apply → destroy. ML 프로젝트 예시: GCS 버킷, 노트북 인스턴스, GKE 클러스터, 서비스 계정 프로비저닝.

**소스 간 합의:**
- IaC(특히 Terraform)가 MLOps 인프라 관리의 표준. 재현 가능 ML 환경 구축에 필수.

**소스 간 불일치:**
- 없음.

---

## kw_048: Kafka topic/partition

**정의/핵심:**
- 토픽: Kafka 데이터 스트림의 논리적 채널. 파티션: 토픽의 병렬 처리 단위, 순서 보장의 기본 단위.

**소스별 관점:**
- 027 (New Relic): 파티셔닝 전략: 무작위(균등 부하), 집계 키 기반(순서 보장, hot spot 위험), 리소스 병목 해소, 스토리지 효율화. New Relic 사례: 상위 1.5% 쿼리가 90% 이벤트 → hot spot → 2단계 집계로 해결.
- 020 (Instaclustr): 파티션 = 순차적 디스크 읽기로 고성능. 오프셋으로 소비자 위치 추적. ISR(In-Sync Replica)이 리더 장애 시 자동 승계.

**소스 간 합의:**
- 파티션 설계가 Kafka 성능의 핵심. 키 기반 파티셔닝 시 hot spot에 주의.

**소스 간 불일치:**
- 없음.

---

## kw_049: MLOps maturity model

**정의/핵심:**
- 조직의 MLOps 역량을 Level 0~4로 평가하는 프레임워크. 사람·프로세스·기술 세 차원을 평가.

**소스별 관점:**
- 009 (Microsoft Azure): 5단계: Level 0(수동, 추적 없음), Level 1(DevOps but no MLOps, 빌드 자동화만), Level 2(훈련 자동화, 특성 스토어 관리), Level 3(배포 자동화, CI/CD 파이프라인), Level 4(완전 자동화, 드리프트→자동 재훈련, 정책 기반 프로모션).

**소스 간 합의:**
- 성숙도 모델은 현재 상태 진단과 목표 설정 도구로 활용.

**소스 간 불일치:**
- 없음.

---

## kw_050: Kafka backpressure

**정의/핵심:**
- 소비자가 생산자 속도를 따라가지 못할 때 발생하는 처리 지연. 소비자 지연(lag) 증가, 메모리 압박, 리밸런싱 유발.

**소스별 관점:**
- 028 (OneUptime): 증상: 증가하는 lag, OOM 에러, 리밸런싱, 타임아웃. 흐름 제어: partition pausing API(백로그 임계값 초과 시 일시 정지, 해소 시 재개). 핵심 설정: max.poll.records=100, enable.auto.commit=false(수동 커밋).

**소스 간 합의:**
- Kafka 소비자 백프레셔 처리는 실시간 ML 파이프라인의 안정성에 직결.

**소스 간 불일치:**
- 없음.
