# Gap Analysis: LLMOps, Kafka, MLOps

## 커버리지 미달 키워드

다음 키워드는 소스 파일에서 직접 커버된 소스가 없거나 간접 언급에 그쳐 교재 작성 시 추가 조사가 필요하다.

| 키워드 | 상태 | 비고 |
|--------|------|------|
| kw_014: EDA + AI 통합 패턴 | 간접 커버 | 소스 021, 025에서 언급되지만 구체적 패턴 코드/아키텍처 부재 |
| kw_031: MLflow Model Registry 실전 | 단일 소스 | 소스 005 하나만 커버; 다른 레지스트리(W&B, SageMaker) 비교 없음 |
| kw_032: LangChain 엔터프라이즈 | 단일 소스 | 소스 105만 커버; LangGraph, LangSmith 심층 분석 없음 |
| kw_034: Confluent Platform | 단일 소스 | 소스 031만 커버; 비용 구조, 라이선스, 오픈소스 대비 분석 없음 |
| kw_050: Kafka 백프레셔 | 단일 소스 | 소스 028만 커버; Flink 백프레셔 처리와의 비교 없음 |
| kw_047: Terraform for ML | 단일 소스 | 소스 008만 커버; Pulumi, CDK 등 대안 없음; ML 특화 모듈 예시 없음 |
| kw_049: MLOps 성숙도 모델 | 단일 소스 | 소스 009(Microsoft)만 커버; Google, AWS 성숙도 모델 부재 |

---

## 추가 조사 필요 영역

### 영역 1: Kafka 보안 (완전 부재)
70개 소스 중 Kafka 보안(TLS/SSL, SASL, ACL, 암호화)을 전용으로 다룬 소스가 없다. 소스 020, 031이 일부 언급하나 설정 예시나 운영 가이드가 없다.
- **필요 소스 유형**: Kafka 공식 보안 문서, Confluent Platform 보안 가이드
- **대상 키워드**: kw_003(Kafka 보안 섹션), kw_034(Confluent ACL)

### 영역 2: Kubernetes MLOps 오케스트레이션 심층 (부분 커버)
Kubernetes 기반 배포(소스 040, 045, 046, 047, 048)는 잘 커버되었으나, Kubeflow Pipelines, KServe, Seldon Core 같은 ML 전용 Kubernetes 확장의 실전 운영 내용이 없다.
- **필요 소스 유형**: KServe 공식 문서, Kubeflow 아키텍처 문서
- **대상 키워드**: kw_019, kw_030

### 영역 3: 멀티 클라우드 및 하이브리드 ML 배포 (부재)
IaC 관련 소스 008(Terraform)은 개념을 다루나 실제 멀티 클라우드 ML 파이프라인(AWS SageMaker + GCP Vertex AI 혼용 등) 시나리오가 없다.
- **필요 소스 유형**: 멀티 클라우드 ML 아키텍처 사례 연구
- **대상 키워드**: kw_047, kw_009

### 영역 4: LLM 파인튜닝 인프라 상세 (부분 커버)
소스 120이 LoRA/QLoRA를 다루지만, 분산 훈련(DeepSpeed ZeRO, FSDP), 훈련 클러스터 설계, 체크포인팅 전략에 대한 소스가 없다.
- **필요 소스 유형**: DeepSpeed 공식 문서, Hugging Face Accelerate 가이드
- **대상 키워드**: kw_016

### 영역 5: 벡터 DB 운영 (부분 커버)
소스 102가 벡터 DB를 비교하지만, 실제 운영 관점(인덱스 업데이트 전략, 메모리 관리, 벡터 임베딩 버전 관리)이 없다.
- **필요 소스 유형**: Pinecone/Weaviate 공식 운영 가이드
- **대상 키워드**: kw_017

### 영역 6: A/B 테스트 통계 기초 (부분 커버)
소스 082가 A/B 테스트 설계를 다루지만, 통계적 검정력 계산, 샘플 크기 결정, 다중 비교 보정(Bonferroni 등) 실전 예시가 부족하다.
- **필요 소스 유형**: 통계적 A/B 테스트 실전 가이드
- **대상 키워드**: kw_027, kw_041

### 영역 7: 에이전틱 AI + MLOps (신흥 영역, 부재)
LLM 에이전트(도구 사용, 멀티 에이전트)를 MLOps 파이프라인에 통합하는 운영 패턴에 대한 소스가 없다. 소스 105(LangChain)가 간접 언급하는 수준이다.
- **필요 소스 유형**: 에이전트 오케스트레이션 + 운영 모니터링 사례
- **대상 키워드**: kw_032, kw_043

---

## 소스 품질 저하 영역

### 저품질 소스 (내용 얕음)

| 소스 번호 | 제목 요약 | 문제점 |
|-----------|-----------|--------|
| 소스 044 (NVIDIA) | 가지치기+증류 | 기술적 깊이는 있으나 실제 구현 코드/명령어 없음; 마케팅 톤 강함 |
| 소스 049 (MarkTechPost) | vLLM 비교 | 수치 인용(24× 성능 향상)의 출처 불명확; 원 논문 링크 없음 |
| 소스 062 (Estuary) | 데이터 파이프라인 | 개념 설명에 그치며 Kafka 특화 내용이 적음; ETL/ELT 정의 수준 |
| 소스 107 (Koombea) | LLM 비용 절감 | 일부 수치(87% 비용 절감) 검증 불가; 사례 기업명 미공개 |
| 소스 089 (MarkTechPost) | 배포 전략 비교 | 4개 전략을 1~2문장으로만 설명; 깊이 매우 얕음 |

### 단일 소스 의존 위험 영역

다음 토픽은 단일 소스에 의존하므로 교재 작성 시 추가 검증이 필요하다:

- **Terraform for ML** (소스 008 단독): HCL 구문 예시 풍부하나 ML 파이프라인 특화 내용 부족
- **MLOps 성숙도 모델** (소스 009 단독): Microsoft 관점만 반영; Google/Gartner 프레임워크 없음
- **프롬프트 버전 관리** (소스 100 단독): 5개 도구 소개이나 도구별 심층 기능 비교 없음
- **자동 재훈련 SEI 비판** (소스 123 단독): CMU/SEI 관점이므로 업계 반론 없음

---

## 추천 보완 방향

### 우선순위 1 (교재 필수 챕터 지원)

1. **Kafka 보안 운영 가이드** 추가 수집
   - Apache Kafka 공식 보안 문서 (kafka.apache.org/documentation/#security)
   - 실제 TLS + SASL/SCRAM 설정 예시

2. **KServe / Kubeflow Pipelines 운영** 자료 추가 수집
   - KServe GitHub 공식 예제
   - Google Vertex AI Pipelines 비교

3. **분산 LLM 훈련** (DeepSpeed, FSDP) 자료 추가 수집
   - Hugging Face Accelerate 공식 문서
   - DeepSpeed ZeRO 단계별 설명

### 우선순위 2 (내용 보강)

4. **벡터 DB 운영 심층** 자료 추가 수집
   - Weaviate 프로덕션 배포 가이드
   - 임베딩 버전 관리 전략

5. **A/B 테스트 통계** 실전 가이드 추가 수집
   - 샘플 크기 계산, 검정력 분석 예시

6. **MLflow 외 모델 레지스트리** 비교 자료 추가 수집
   - W&B Model Registry, SageMaker Model Registry, Vertex AI Model Registry

### 우선순위 3 (미래 지향)

7. **에이전틱 AI + MLOps** 통합 패턴 모니터링
   - 현재 소스에서 완전 부재; 2025–2026 신흥 영역
   - LLM 에이전트 관측 가능성 (소스 080 OTel 기반 확장)

---

## 커버리지 요약

| 하위 영역 | 소스 수 | 커버리지 평가 |
|-----------|---------|---------------|
| Apache Kafka 핵심 | 13개 | 충분 (KRaft, EOS, 파티션, Schema Registry, ksqlDB 모두 커버) |
| 스트리밍 처리 (Flink/Streams) | 5개 | 충분 (개념적 비교 포함) |
| 피처 스토어 | 4개 | 충분 (실사례 포함) |
| LLM 서빙 인프라 | 7개 | 충분 (vLLM/SGLang/TRT, K8s 배포 포함) |
| 모델 모니터링/드리프트 | 5개 | 충분 (Evidently AI 3편, OTel, Grafana) |
| RAG 파이프라인 | 4개 | 충분 (벡터DB 비교, RAGAS, 환각 감지) |
| LLM 비용 최적화 | 4개 | 충분 (토큰, 캐싱, 라우팅, 게이트웨이) |
| 모델 훈련 최적화 | 5개 | 충분 (LoRA/QLoRA, 양자화, RLHF/DPO) |
| 자동 재훈련 | 4개 | 충분 (스케줄/이벤트, SEI 비판, 314e 사례) |
| MLOps 인프라 (CI/CD, IaC) | 4개 | 보통 (Terraform 단독, K8s 미포함) |
| 실험 관리/버전 관리 | 4개 | 보통 (MLflow 중심, 타 도구 얕음) |
| Kafka 보안 | 0개 전용 | **부족** — 추가 수집 필요 |
| 분산 LLM 훈련 | 0개 전용 | **부족** — 추가 수집 필요 |
| KServe/Kubeflow 운영 | 0개 전용 | **부족** — 추가 수집 필요 |
| 에이전틱 AI + MLOps | 0개 | **없음** — 신흥 영역 모니터링 필요 |

**총 갭 건수**: 커버리지 부족 영역 7개 + 단일 소스 의존 4개 + 완전 부재 3개 = 14건
