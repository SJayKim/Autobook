# Agentic AI 시스템 보안체계 학습 가이드

LLM 에이전트(도구 호출, 메모리, 멀티에이전트 협업)를 실제 시스템으로 구현할 때 알아야 할
보안 개념을 "무엇을, 어떤 순서로 공부할지" 관점에서 요약한 문서입니다.
한국 공공 맥락(N2SF)과 글로벌 표준(OWASP, NIST, MCP)을 함께 다룹니다. 기준 시점: 2026년 7월.

---

## 0. 한눈에 보는 학습 지도

아래에서 위로 쌓아 올리는 순서로 공부하면 됩니다.

```
[L4] 거버넌스·규제    N2SF, AI 기본법, EU AI Act, NIST AI RMF, ISO 42001
        ▲
[L3] 운영·보증        감사 로그, 레드티밍, 런타임 모니터링, 사고 대응
        ▲
[L2] 방어 설계        샌드박스, 최소 권한, HITL 승인, 가드레일, egress 통제
        ▲
[L1] 위협 이해        OWASP LLM Top 10, Agentic Top 10(ASI), MCP 공격, Lethal Trifecta
        ▲
[L0] 기반 원칙        Zero Trust, 최소 권한 원칙, 심층 방어, 위협 모델링, 비인간 신원
```

핵심 관점 하나만 기억하면 됩니다: **에이전트는 "권한을 가진 신뢰할 수 없는 실행 주체"로 취급한다.**
전통 보안이 "외부 공격자로부터 내부를 지키는 것"이라면, agentic 보안은
"내가 배포한 에이전트 자체가 오염될 수 있다"는 전제에서 출발합니다.

---

## 1. 기반 원칙 (L0 — 선수 개념)

전통 보안 개념이지만 agentic AI에서 의미가 재해석되는 것들입니다.

- **Zero Trust Architecture** (NIST SP 800-207): "내부망이니까 신뢰"를 폐기하고 모든 요청을
  매번 검증하는 사상. N2SF도 이 사상 위에 설계되었습니다. 에이전트의 모든 도구 호출을
  "신뢰할 수 없는 요청"으로 보는 근거가 됩니다.
- **최소 권한 원칙(PoLP) → 최소 에이전시(Least Agency)**: 에이전트에게 작업에 필요한
  최소한의 도구·데이터·행동 범위만 부여. "혹시 필요할까 봐" 넓게 주는 순간 사고 반경이 커집니다.
- **심층 방어(Defense in Depth)**: 프롬프트 지시("하지 마세요")는 방어가 아닙니다.
  모델 계층 실패를 전제로 권한·네트워크·샌드박스 계층에서 다시 막는 구조가 필요합니다.
- **위협 모델링**: STRIDE 같은 고전 기법 + AI 특화 매트릭스인 **MITRE ATLAS**.
  "이 에이전트가 오염되면 최악의 경우 무엇을 할 수 있는가"를 설계 전에 묻는 습관.
- **비인간 신원(NHI, Non-Human Identity)**: 에이전트는 사람도 아니고 단순 서비스 계정도
  아닌 새로운 신원 주체. workload identity(SPIFFE/SPIRE), 단기 크리덴셜 개념이 여기 속합니다.

---

## 2. 거버넌스·규제 프레임워크 (L4)

### 2.1 국내

- **N2SF (국가 망 보안체계)**: 국가정보원이 만든 공공 네트워크 보안 프레임워크.
  20년간의 일률적 물리적 망분리를 폐기하고, 업무 정보를 **C(기밀)/S(민감)/O(공개)**
  3등급으로 분류한 뒤 **6대 보안통제 항목(권한, 인증, 분리·격리, 통제, 데이터, 정보자산)**을
  등급별로 차등 적용합니다. 도입 목적 자체가 "공공에서 생성형 AI·클라우드를 쓸 수 있게
  하되 보안을 유지"이므로, 공공 대상 에이전트 시스템을 만든다면 사실상 필수 지식입니다.
  2025년 1월 초안 → 보안가이드라인 1.0 정식판 → KISA 실증사업(생성형 AI 업무 활용 등
  6개 모델) → 2026년 국가 사이버보안 기본지침 개정과 함께 본격 시행 단계입니다.
- **AI 기본법** (인공지능 발전과 신뢰 기반 조성 등에 관한 기본법, 2026-01-22 시행):
  고영향 AI 사업자 책무, 생성형 AI 산출물 표시 의무 등. 에이전트 서비스가 "고영향"에
  해당하는지 판단하는 기준을 알아야 합니다.
- **CSAP (클라우드 보안인증제)**: 공공기관에 클라우드 서비스를 공급하려면 필요한 인증.
  상/중/하 등급제. SaaS형 에이전트를 공공에 팔려면 N2SF 등급 분류와 함께 걸리는 관문입니다.

### 2.2 해외

- **EU AI Act**: 위험 기반(risk-based) 규제의 원형. 금지 AI/고위험 AI/범용 AI(GPAI)로
  나누어 의무를 차등 부과. 2026년 8월 고위험 규제 본격 적용.
- **NIST AI RMF** + **Generative AI Profile (NIST-AI-600-1)**: 미국의 AI 위험 관리
  프레임워크. Govern/Map/Measure/Manage 4개 기능. 규제라기보다 "위험 관리 체크리스트의
  공통어"로 쓰입니다.
- **ISO/IEC 42001** (AI 경영시스템) / **ISO/IEC 27001** (정보보호 경영시스템):
  조직 차원 인증. 엔터프라이즈 고객이 에이전트 도입 시 요구하는 경우가 늘고 있습니다.

> 공부 요령: 규제는 전부 외울 필요 없이 "위험 등급 분류 → 등급별 차등 통제"라는
> 공통 패턴 하나로 묶어서 이해하면 됩니다. N2SF의 C/S/O, EU AI Act의 위험 4단계,
> CSAP의 상/중/하가 모두 같은 패턴입니다.

---

## 3. 위협 이해 (L1 — 무엇이 공격당하는가)

### 3.1 OWASP Top 10 for LLM Applications (2025)

LLM 애플리케이션 일반의 위협 목록. 에이전트 이전 단계의 기초입니다.
핵심만 추리면: **LLM01 프롬프트 인젝션**, LLM02 민감정보 유출, LLM03 공급망,
LLM04 데이터·모델 오염, LLM05 부적절한 출력 처리, **LLM06 과도한 에이전시(Excessive
Agency)**, LLM08 벡터·임베딩 취약점. LLM06이 agentic 보안으로 넘어가는 다리입니다.

### 3.2 OWASP Top 10 for Agentic Applications (2026) — 핵심 분류체계

2025년 12월 발표된 에이전트 전용 위협 Top 10. agentic 보안 공부의 중심 축으로 삼기 좋습니다.

| 코드 | 이름 | 핵심 위협 |
|------|------|----------|
| ASI01 | Agent Goal Hijack | 악성 콘텐츠가 에이전트의 목표 자체를 바꿔치기 (간접 프롬프트 인젝션 포함) |
| ASI02 | Tool Misuse & Exploitation | 정상 도구를 위험하게 사용 — 파괴적 명령, 의도치 않은 액션 |
| ASI03 | Identity & Privilege Abuse | 에이전트가 물려받은 고권한 토큰의 재사용·에스컬레이션·전파 |
| ASI04 | Agentic Supply Chain Vulnerabilities | 오염된 도구/플러그인/프롬프트 템플릿/런타임 로드 컴포넌트 |
| ASI05 | Unexpected Code Execution | 에이전트가 생성·실행하는 코드/셸 명령의 무방비 실행 |
| ASI06 | Memory & Context Poisoning | 메모리, 임베딩, RAG DB, 요약본을 오염시켜 미래 결정을 조작 |
| ASI07 | Insecure Inter-Agent Communication | 에이전트 간 메시지의 인증·암호화·의미 검증 부재 |
| ASI08 | Cascading Failures | 한 에이전트의 오류가 계획→실행→메모리→다운스트림으로 증폭 전파 |
| ASI09 | Human-Agent Trust Exploitation | 사용자의 과잉 신뢰를 악용한 의사결정 조작·정보 탈취 |
| ASI10 | Rogue Agents | 오염·미스얼라인된 에이전트가 정상인 척 지속 활동, 타 에이전트 사칭 |

### 3.3 개별 공격 기법 (반드시 손으로 이해할 것)

- **간접 프롬프트 인젝션(Indirect Prompt Injection)**: 에이전트가 읽는 웹페이지, 문서,
  이메일, 이슈 댓글에 숨긴 지시문이 실행되는 공격. agentic 보안의 1번 문제이며,
  2026년 현재도 "완전 해결책 없음"이 정설입니다. 그래서 아키텍처 방어(4~5장)가 중요합니다.
- **Lethal Trifecta** (Simon Willison): ① 민감 데이터 접근 + ② 신뢰 불가 콘텐츠 노출 +
  ③ 외부 전송 능력 — 세 가지가 한 에이전트에 모이면 데이터 유출은 시간문제라는 원칙.
  설계 검토 시 "셋 중 하나를 제거했는가"를 묻는 실용적 체크리스트로 씁니다.
- **Confused Deputy**: 낮은 권한의 요청자가 높은 권한의 에이전트를 속여 대신 일을
  시키는 고전 패턴의 재림. 멀티테넌트 에이전트 서비스에서 특히 위험합니다.
- **메모리/RAG 포이즈닝**: 한 번 오염된 문서가 벡터 DB에 들어가면 이후 모든 세션의
  컨텍스트를 오염시키는, 지속성(persistence) 있는 공격.

---

## 4. 프로토콜·도구 레이어 보안

에이전트 생태계의 "배관"에 해당하는 표준들과 그 공격면입니다.

- **MCP (Model Context Protocol) 보안**: 도구 연결 표준. 5대 공격 벡터로 정리됩니다 —
  ① Tool Poisoning(도구 설명문에 악성 지시 은닉), ② Confused Deputy,
  ③ Token Passthrough(토큰 무검증 전달), ④ SSRF(도구 커넥터 경유),
  ⑤ Rogue Server(악성 서버 등록). 대응: OAuth 2.1 기반 인증, 서버 검증·핀닝(rug pull
  방지), MCP 게이트웨이/레지스트리, 도구 설명문 정적 분석. 실무 수칙은 한 줄로:
  **"모든 MCP 서버는 검증 전까지 적대적이라고 가정한다."**
- **A2A (Agent2Agent) 프로토콜**: 에이전트 간 협업 표준(Linux Foundation).
  Agent Card(신원·능력 선언), 상호 인증이 핵심. ASI07(에이전트 간 통신)의 해법 레이어입니다.
- **AI 공급망 보안**: 모델 허브(오염 모델), 패키지 저장소(슬롭스쿼팅 — LLM이 환각한
  패키지명을 선점하는 공격), MCP 서버 배포판, 프롬프트 템플릿까지 공급망으로 취급.
  SBOM의 AI 확장(모델·데이터 출처 추적) 개념도 여기 속합니다.

---

## 5. 방어 설계 패턴 (L2 — 어떻게 막는가)

구현자가 실제로 코드/인프라로 만드는 부분입니다. 네 묶음으로 정리합니다.

### 5.1 실행 격리

- **샌드박싱**: 에이전트의 코드 실행을 컨테이너, microVM(Firecracker, gVisor),
  WASM 등에서 격리. ASI05(코드 실행)의 1차 방어선.
- **Egress 통제**: 에이전트가 접근 가능한 네트워크 목적지를 allowlist로 제한.
  Lethal Trifecta의 ③(외부 전송)을 구조적으로 제거하는 가장 확실한 방법.
- **세션 격리**: 사용자/테넌트 간 메모리·컨텍스트 완전 분리.

### 5.2 권한·신원

- **Capability 기반 권한**: 도구별·액션별 세분화된 스코프. "파일 읽기"와 "파일 쓰기"는
  다른 권한. 읽기 전용 기본값 + 명시적 승격.
- **단기(JIT) 크리덴셜 + 시크릿 볼트**: 에이전트에 장기 API 키를 심지 않고,
  작업 시점에 최소 범위 토큰을 발급. ASI03의 해법.
- **에이전트 신원**: 사람 계정 위임이 아닌 에이전트 고유 신원 발급, 행위 귀속(attribution) 보장.

### 5.3 흐름 통제

- **HITL(Human-in-the-Loop) 승인 게이트**: 고위험 액션(삭제, 송금, 외부 발송)은 사람 승인
  후 실행. 무엇이 "고위험"인지 액션 분류표를 먼저 만드는 것이 실무의 시작점입니다.
- **Dual-LLM 패턴**: 신뢰 불가 콘텐츠를 읽는 격리 LLM과 도구 권한을 가진 특권 LLM을
  분리, 둘 사이에 자연어가 아닌 구조화 데이터만 통과시키는 설계.
- **CaMeL** (Google DeepMind, "Defeating Prompt Injections by Design"): 제어 흐름과
  데이터 흐름을 분리하고 capability로 데이터 이동을 제한하는, 현재 가장 진지한
  구조적 해법. 논문 한 편은 읽어볼 가치가 있습니다.
- **Plan-then-Execute**: 신뢰 불가 데이터를 읽기 전에 실행 계획을 확정해, 읽은 내용이
  행동을 바꾸지 못하게 하는 패턴.

### 5.4 입출력·데이터

- **가드레일**: 입력 필터(인젝션 탐지 분류기), 출력 검증(스키마 강제, 민감정보 마스킹).
  단, 분류기는 우회 가능하므로 보조 수단이지 주 방어선이 아닙니다.
- **데이터 등급 분류 + DLP**: 에이전트가 접근하는 데이터에 등급표(→ N2SF의 C/S/O와
  직결)를 붙이고, 등급 간 이동을 통제. 마스킹/토크나이제이션 포함.

---

## 6. 운영·보증 (L3 — 배포 후)

- **관측성(Observability)**: 모든 도구 호출·프롬프트·응답의 감사 로그, 분산 추적
  (OpenTelemetry GenAI semantic conventions), 세션 리플레이. "에이전트가 왜 그 행동을
  했는가"를 재구성할 수 없으면 사고 대응이 불가능합니다.
- **평가·레드티밍**: 배포 전 적대적 테스트. 벤치마크로 AgentDojo(에이전트 프롬프트
  인젝션), AgentHarm(유해 작업 수행) 등. 일회성이 아니라 모델/도구 변경 때마다
  회귀 테스트처럼 돌리는 것이 핵심.
- **런타임 모니터링·이상 탐지**: 평소와 다른 도구 호출 패턴, 권한 사용, 데이터 접근을
  실시간 탐지. AI-SPM(AI Security Posture Management) 제품군이 이 영역입니다.
- **사고 대응**: kill switch(에이전트 즉시 정지), 크리덴셜 일괄 폐기, 오염된 메모리/벡터 DB
  롤백 절차를 사전에 준비.

---

## 7. N2SF × Agentic AI — 두 세계의 연결

N2SF의 6대 보안통제 항목은 위에서 공부한 agentic 보안 개념과 거의 1:1로 대응됩니다.
이 표가 이 문서 전체의 요약이기도 합니다.

| N2SF 통제 항목 | Agentic AI 구현에서의 대응 개념 |
|---------------|--------------------------------|
| 권한 | 최소 에이전시, capability 기반 도구 스코프, JIT 크리덴셜 (ASI03 대응) |
| 인증 | 에이전트 신원(NHI), OAuth 2.1, mTLS, A2A Agent Card |
| 분리·격리 | 샌드박싱, egress 통제, 세션/테넌트 격리, Dual-LLM |
| 통제 | HITL 승인 게이트, 가드레일, 정책 엔진, kill switch |
| 데이터 | C/S/O 등급 분류 → 에이전트 접근 범위 결정, DLP, RAG 오염 방지 |
| 정보자산 | 모델·MCP 서버·프롬프트 템플릿 인벤토리, AI 공급망 관리 (ASI04 대응) |

공공 도입 시나리오로 보면: 업무 정보를 C/S/O로 분류 → O등급 업무부터 외부 LLM
에이전트 허용 → S등급은 격리·통제 조건부 허용 → C등급은 차단, 이라는 구조가 되고,
KISA 실증사업의 "업무 환경에서 생성형 AI 활용" 모델이 정확히 이 흐름을 검증하는 중입니다.
역방향 연구(N2SF 보안통제 항목 도출을 멀티에이전트 LLM으로 자동화)도 나오고 있어,
"AI를 지키는 보안"과 "보안을 하는 AI"가 만나는 지점이기도 합니다.

---

## 8. 추천 학습 순서

1. **기반 다지기**: Zero Trust(NIST SP 800-207 요약본), 최소 권한, 위협 모델링 기초.
   → 검증: 임의의 에이전트 아키텍처를 보고 신뢰 경계(trust boundary)를 그릴 수 있다.
2. **LLM 보안 입문**: OWASP LLM Top 10(2025) 정독, 프롬프트 인젝션 직접 재현 실습.
   → 검증: 직접 만든 챗봇에서 간접 인젝션을 성공시켜 본다.
3. **Agentic 확장**: OWASP Agentic Top 10(ASI01~10), Lethal Trifecta, MCP 5대 공격 벡터.
   → 검증: 자기 에이전트 프로젝트에서 ASI 항목별 해당 여부 표를 만든다.
4. **방어 설계 실습**: 샌드박스 + egress allowlist + HITL 게이트를 실제로 구현.
   CaMeL 논문 읽기. → 검증: 3번에서 성공한 공격이 더 이상 통하지 않는다.
5. **규제 매핑**: N2SF 가이드라인 1.0 + KISA 실증 사례집 + AI 기본법 개요.
   → 검증: 자기 시스템을 C/S/O 등급 시나리오에 배치하고 6대 통제 항목 답안을 쓸 수 있다.

---

## 9. 핵심 자료

**국내 (N2SF)**
- [국정원 — N2SF 보안가이드라인 정식판 보도자료](https://www.nis.go.kr/CM/1_4/view.do?seq=373)
- [KISA — 국가 망 보안체계(N2SF) 실증 사례집](https://www.kisa.or.kr/20604/form?postSeq=23171&lang_type=KO&page=)
- [이글루코퍼레이션 — N2SF 시대 본격화, 국가 사이버보안 기본지침 개정](https://www.igloo.co.kr/security-information/%EB%B3%B4%EC%95%88-101-%EA%B5%AD%EA%B0%80-%EB%A7%9D-%EB%B3%B4%EC%95%88%EC%B2%B4%EA%B3%84n2sf-%EC%8B%9C%EB%8C%80-%EB%B3%B8%EA%B2%A9%ED%99%94-%EA%B5%AD%EA%B0%80-%EC%82%AC%EC%9D%B4%EB%B2%84/)
- [펜타시큐리티 — 물리적 망분리에서 맞춤형 보안으로](https://www.pentasecurity.co.kr/insight/from-physical-isolation-to-custom-security-n2sf/)

**위협 분류체계 (OWASP)**
- [OWASP Top 10 for Agentic Applications 2026 (공식)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [OWASP GenAI Security Project (LLM Top 10, Securing Agentic Applications Guide 포함)](https://genai.owasp.org/)
- [Aikido — Agentic Top 10 해설](https://www.aikido.dev/blog/owasp-top-10-agentic-applications)

**프로토콜·방어 기술**
- [MCP 공식 Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [Cloud Security Alliance — Agentic MCP Security Best Practices](https://labs.cloudsecurityalliance.org/agentic/agentic-mcp-security-best-practices-v1/)
- [Wiz Academy — MCP Security](https://www.wiz.io/academy/ai-security/model-context-protocol-security)
- [Simon Willison — The Lethal Trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)
- CaMeL 논문: "Defeating Prompt Injections by Design" (Google DeepMind, arXiv:2503.18813)

**거버넌스**
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST SP 800-207 Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [MITRE ATLAS](https://atlas.mitre.org/)
