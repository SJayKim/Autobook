# 비전문가를 위한 기술 교재 작성법 연구 보고서

이 문서는 기술 교재를 비전문가/초보자가 쉽게 이해할 수 있도록 작성하기 위한 기법과 방법론을 종합 정리한 연구 보고서입니다.

---

## 1. 교육학적 프레임워크 (Pedagogical Frameworks)

### 1.1 파인만 기법 (Feynman Technique)

물리학자 리처드 파인만에서 유래한 학습/설명 기법으로, 기술 교재 집필에 직접 적용할 수 있습니다.

**4단계 프로세스:**
1. 개념을 선택한다
2. 초등학생(6학년 수준)에게 가르치듯 설명한다
3. 설명이 막히는 부분 = 이해가 부족한 부분을 식별한다
4. 단순화하고 비유를 사용해 다시 설명한다

**교재 집필에의 적용:**
- 모든 설명을 "해당 분야를 전혀 모르는 사람이 읽어도 이해할 수 있는가?"로 검증합니다
- 전문 용어를 사용할 때마다 일상 언어로 바꿔 설명할 수 있는지 확인합니다
- 설명이 막히는 부분이 곧 독자도 이해하기 어려운 부분입니다

> 출처: [Feynman Technique - Farnam Street](https://fs.blog/feynman-technique/)

### 1.2 스캐폴딩 (Scaffolding)과 근접 발달 영역 (ZPD)

비고츠키(Vygotsky)의 근접 발달 영역 이론에 기반한 교육 기법입니다.

**핵심 개념:**
- **근접 발달 영역(ZPD)**: 학습자가 혼자서는 할 수 없지만, 안내가 있으면 할 수 있는 영역
- **스캐폴딩**: 학습자가 새 개념을 습득할 때 임시 지지대(scaffold)를 제공하고, 숙달되면 점진적으로 제거하는 기법

**교재 집필에의 적용:**
- 각 단원은 독자가 "이미 아는 것"에서 출발해 "아직 모르는 것"으로 연결합니다
- 초반에는 상세한 설명과 예시를 제공하고, 후반으로 갈수록 독자의 자립적 이해에 맡깁니다
- 선수 지식(prerequisites)을 명확히 하여 독자가 현재 위치를 파악할 수 있게 합니다

**8가지 스캐폴딩 유형:**
1. 언어적 힌트 (verbal prompts)
2. 시각적 보조 (visual supports)
3. 모델링 (modelling) — 완성된 예시를 먼저 보여주기
4. 질문 기법 (questioning) — "왜 이렇게 될까요?"
5. 협력 학습 (collaborative learning)
6. 그래픽 조직자 (graphic organisers) — 다이어그램, 표
7. 과제 분해 (breaking tasks into steps)
8. 예시 제공 (providing examples)

> 출처: [Instructional Scaffolding - Wikipedia](https://en.wikipedia.org/wiki/Instructional_scaffolding), [Structural Learning - Scaffolding Guide](https://www.structural-learning.com/post/scaffolding-in-education-a-teachers-guide)

### 1.3 구체에서 추상으로 (Concrete-to-Abstract, CPA 접근법)

제롬 브루너(Jerome Bruner, 1966)가 제안한 연구 기반 접근법입니다.

**핵심 원리:**
- 인간의 기억은 추상적 정보보다 구체적 정보를 훨씬 잘 기억합니다
- 구체적 개념은 시각적 이미지와 언어 두 가지 경로로 인코딩되어 기억률이 높습니다
- **구체성 퇴행(Concreteness Fading)**: 처음에는 구체적 표현으로 시작하고, 점진적으로 핵심 요소를 추상적 표현으로 교체합니다

**교재 집필에의 적용:**
- 모든 새 개념은 구체적 예시/비유로 시작하고, 그 다음 정식 정의/추상적 설명으로 넘어갑니다
- "예시 먼저, 원리 나중" 순서를 기본으로 합니다
- 코드를 설명할 때: 동작하는 코드를 먼저 보여주고 → 각 부분이 무엇인지 설명 → 일반 원리를 도출합니다

> 출처: [SAGE Journals - Concrete Examples Enhance Abstract Concept Learning](https://journals.sagepub.com/doi/10.1177/00986283211058069), [Learning Scientists - Concrete Examples](https://www.learningscientists.org/blog/2016/8/25-1)

---

## 2. 인지과학 기반 접근법

### 2.1 인지 부하 이론 (Cognitive Load Theory)

존 스웰러(John Sweller)가 제안한 이론으로, 인간의 작업 기억(working memory)에는 한계가 있다는 전제에서 출발합니다.

**세 가지 인지 부하:**
| 유형 | 설명 | 전략 |
|------|------|------|
| **내재적 부하 (Intrinsic)** | 주제 자체의 복잡성. 피할 수 없음 | 청킹으로 분해 |
| **외재적 부하 (Extraneous)** | 잘못된 제시 방식에서 오는 불필요한 부하 | 제거해야 함 |
| **본유적 부하 (Germane)** | 새 지식을 기존 스키마에 통합하는 노력 | 최적화해야 함 |

**교재 집필 10대 실천 기법:**

1. **청킹(Chunking)**: 복잡한 개념을 소화 가능한 단위로 분리합니다. 하나의 단락에 하나의 개념만 담습니다.
2. **시각 요소 배치**: 다이어그램, 순서도, 표를 텍스트와 함께 배치합니다.
3. **점진적 공개(Progressive Disclosure)**: 고수준 개요 → 핵심 가이드 → 상세 스펙 → 고급 시나리오 순으로 공개합니다.
4. **여백 활용**: 짧은 단락, 목록, 넉넉한 여백으로 시각적 과부하를 줄입니다.
5. **일관된 구조**: 모든 단원이 동일한 패턴(개요-설명-예시-정리)을 따르면 독자가 예측 가능하므로 인지 부하가 줄어듭니다.
6. **기존 지식 연결**: 새 개념을 독자가 이미 아는 것에 연결합니다 ("JavaScript의 async/await는 Python의 코루틴과 유사합니다").
7. **명확한 네비게이션**: 목차, 용어집, 서술적 제목을 제공합니다.
8. **불필요한 전문 용어 최소화**: 정확성을 해치지 않는 범위에서 더 쉬운 대안을 사용합니다.
9. **예시와 비유 사용**: 추상적 개념을 친숙한 영역에 기반시킵니다.
10. **계층적 정보 설계**: 1층(핵심 개념), 2층(주요 특성), 3층(기술적 세부사항) — 독자가 자신의 수준에 맞춰 소비합니다.

> 출처: [Cognitive Load Theory in Technical Writing](https://www.hireawriter.us/technical-content/cognitive-load-theory-in-technical-writing)

### 2.2 이중 코딩 이론 (Dual Coding Theory)

앨런 파비오(Allan Paivio)의 이론으로, 인간은 언어적 정보와 비언어적(시각적) 정보를 별도의 인지 시스템으로 처리한다는 것입니다.

**핵심 원리:**
- 같은 정보를 언어와 시각 두 채널로 동시에 제공하면 기억과 이해가 향상됩니다
- 부처(Butcher, 2006)의 메타분석: 텍스트+관련 다이어그램이 텍스트만 제공할 때보다 이해도가 0.48 표준편차 향상
- 메이어(Mayer, 2009): 이중 코딩 원리를 따른 멀티미디어 교육이 텍스트 전용 대비 전이 테스트 성과 89% 향상

**교재 집필에의 적용:**
- 모든 핵심 프로세스에 순서도나 다이어그램을 함께 제공합니다
- 데이터 구조는 시각적 표현(표, 트리 그림)을 반드시 병행합니다
- 코드의 실행 흐름은 텍스트 설명 + 흐름도를 동시에 제시합니다

> 출처: [Dual Coding Theory Guide - Education Corner](https://www.educationcorner.com/dual-coding-theory/), [Frontiers in Psychology](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.834706/full)

### 2.3 메이어의 멀티미디어 학습 12원칙 (Mayer's 12 Principles)

리처드 메이어(Richard Mayer)의 연구에서 도출된, 정보 전달 효과를 극대화하는 원칙들입니다.

**교재 집필에 특히 중요한 원칙들:**

| 원칙 | 설명 | 교재 적용 |
|------|------|-----------|
| **일관성 원칙 (Coherence)** | 불필요한 단어, 그림, 소리를 배제할 때 학습 효과가 높아짐 | 흥미롭지만 무관한 이야기(seductive details)를 삽입하지 않기 |
| **신호 원칙 (Signaling)** | 핵심 내용의 조직을 강조하는 단서를 추가할 때 효과적 | 굵은 글씨, 핵심 문장 강조, 구조적 표지(transition words) 사용 |
| **중복 원칙 (Redundancy)** | 같은 정보를 여러 형식으로 동시에 제시하면 오히려 과부하 | 그림 설명과 본문 설명이 완전히 동일한 내용을 반복하지 않기 |
| **공간 인접성 (Spatial Contiguity)** | 관련된 텍스트와 그림이 가까이 배치될 때 효과적 | 코드와 그에 대한 설명을 같은 페이지/화면에 배치 |
| **시간 인접성 (Temporal Contiguity)** | 관련 내용이 시간적으로 동시에 제시될 때 효과적 | 단계별 설명에서 코드와 해설을 분리하지 않기 |
| **사전 훈련 원칙 (Pre-training)** | 핵심 개념의 이름과 특성을 미리 알려주면 효과적 | 본문 시작 전 핵심 용어/개념을 간략히 소개 |

> 출처: [Mayer's 12 Principles - Digital Learning Institute](https://www.digitallearninginstitute.com/blog/mayers-principles-multimedia-learning)

---

## 3. 기술 문서 작성 모범 사례 (Technical Writing Best Practices)

### 3.1 쉬운 언어 운동 (Plain Language Movement)

미국 연방정부의 Plain Writing Act(2010)와 국제 쉬운 언어 운동에서 확립된 원칙들입니다.

**미국 국립문서기록관리청(NARA)의 10대 원칙:**
1. 독자를 위해 쓴다 (Write for your audience)
2. 정보를 논리적으로 조직한다
3. 단어를 신중히 선택한다
4. 간결하게 쓴다
5. 필요한 정보만 담는다
6. 능동태를 사용한다
7. 짧은 문장을 사용한다
8. 표와 목록을 활용한다
9. 전문 용어를 피한다
10. 테스트한다

**쉬운 언어의 정의:**
> "해당 글의 표현, 구조, 디자인이 충분히 명확하여, 의도된 독자가 필요한 정보를 쉽게 찾고, 찾은 내용을 이해하며, 그 정보를 활용할 수 있는 것"

**구체적 실천법:**
- 전문 용어를 처음 사용할 때 반드시 설명합니다
- 능동태를 기본으로 합니다 ("함수가 값을 반환합니다" vs. "값이 함수에 의해 반환됩니다")
- 한 문장에 20단어 이내를 목표로 합니다
- 독자에게 필요한 정보만 담고, 혼란을 줄 수 있는 추가 정보는 제외합니다

> 출처: [National Archives - 10 Principles](https://www.archives.gov/open/plain-writing/10-principles.html), [Center for Plain Language](https://centerforplainlanguage.org/plain-language-advances-technical-communication/), [Digital.gov Plain Language Guide](https://digital.gov/guides/plain-language)

### 3.2 문단 구성과 가독성

**핵심 규칙:**
- **한 문단에 한 개념**: 여러 아이디어가 들어가면 분리합니다
- **주제문(Topic Sentence) 선두 배치**: 각 문단의 첫 문장이 해당 문단의 내용을 예고합니다
- **10줄 이내의 문단**: 긴 문단은 시각적으로 압도감을 주므로 짧게 유지합니다
- **전환 표현(Transitions)**: 문단 간 논리적 연결을 명시합니다 ("이를 바탕으로", "반면에", "구체적으로는")

> 출처: [Technical Writing Essentials - Readability](https://pressbooks.bccampus.ca/technicalwriting/chapter/readability/)

### 3.3 Tom Johnson의 "복잡성 단순화" 시리즈

기술 문서 전문 블로거 Tom Johnson이 정리한 11가지 전략입니다.

**특히 교재 집필에 유용한 전략들:**
1. **거시/미시 뷰 전환**: 전체 지도(커리큘럼 구조)와 현재 위치(개별 토픽)를 오갈 수 있게 합니다
2. **방대한 정보를 핵심으로 증류**: 고수준 요약과 퀵 레퍼런스를 생성합니다
3. **장르의 패턴과 스키마에 맞추기**: 독자가 기대하는 교재의 구조를 따릅니다
4. **기술 언어의 복잡성 줄이기**: 짧은 문장, 하나의 주요 아이디어, 능동태, 명확한 동사를 사용합니다
5. **제품 스토리와 사용자 스토리 정렬**: "이것이 무엇인가"보다 "이것으로 무엇을 할 수 있는가"에 초점을 맞춥니다

> 출처: [I'd Rather Be Writing - Simplifying Complexity](https://idratherbewriting.com/simplifying-complexity/)

---

## 4. 비유와 은유 기법 (Analogy & Metaphor Techniques)

### 4.1 비유가 효과적인 경우

- 낯선 개념을 친숙한 것에 매핑할 때 가장 효과적입니다
- **과학적 비유(scientific analogy)**: 구조적 유사성에 기반한 비유가 기술 문서에 적합합니다
- 예시: "REST API는 식당 메뉴와 같습니다 — 항목을 요청하면 응답을 받습니다"
- 예시: "메모리는 파일 캐비닛과 같습니다"
- 예시: "클라우드 서비스는 창고 보관함과 같습니다"

### 4.2 비유가 오해를 일으키는 경우

- **너무 문자 그대로 받아들여질 때**: 독자가 비유의 모든 측면이 원래 개념과 일치한다고 생각할 수 있습니다
- **문화적으로 특수할 때**: 특정 문화권에서만 통하는 비유는 혼란을 줍니다
- **과도하게 복잡할 때**: 비유 자체가 설명을 필요로 하면 역효과입니다
- **남용할 때**: 매 문단마다 비유를 쓰면 비유의 효과가 소멸합니다

### 4.3 비유 사용의 실천 원칙

1. **구조적 유사성을 확인합니다**: 표면적 유사성이 아니라 메커니즘의 유사성에 기반해야 합니다
2. **한계를 명시합니다**: "이 비유가 성립하지 않는 지점"을 언급합니다 ("물론 실제로는...")
3. **대상 독자에게 테스트합니다**: 동료 리뷰어에게 비유가 명확한지 확인합니다
4. **전략적으로 사용합니다**: 핵심 개념 도입 시에만 사용하고, 상세 설명에서는 정확한 기술 용어로 전환합니다

> 출처: [ClickHelp - Metaphor in Technical Writing](https://clickhelp.com/clickhelp-technical-writing-blog/metaphor-in-technical-writing/), [LinkedIn - Visual Metaphors in Technical Writing](https://www.linkedin.com/advice/0/how-do-you-use-visual-metaphors-analogies)

---

## 5. 구조적/포맷팅 기법

### 5.1 역피라미드 구조 (Inverted Pyramid)

저널리즘에서 유래한 정보 배치 기법으로, 가장 중요한 정보를 먼저 제시합니다.

**원칙:**
- 각 단원/섹션의 첫 문단이 핵심 메시지를 담습니다
- 독자가 어느 지점에서 읽기를 멈추더라도 핵심은 파악할 수 있습니다
- 모든 요소(문단, 섹션, 문서)에서 첫 문장이 가장 중요한 정보를 담습니다

**교재 적용:**
- 각 토픽 문서의 도입부에서 "이 단원에서 무엇을 다루는지"를 즉시 밝힙니다
- 각 문단의 첫 문장이 해당 문단의 핵심입니다
- 배경 설명, 역사, 부연은 핵심 뒤에 배치합니다

> 출처: [Nielsen Norman Group - Inverted Pyramid](https://www.nngroup.com/articles/inverted-pyramid/)

### 5.2 점진적 공개 (Progressive Disclosure)

**원칙:**
- 정보를 한꺼번에 쏟아붓지 않고, 필요한 시점에 필요한 만큼 제공합니다
- 고급/드문 기능은 기본 설명 뒤에 배치합니다
- 정보 과부하를 방지하고, 독자가 정보 구조를 통제된 방식으로 탐색합니다

**교재 적용:**
- 기본 개념 → 핵심 사용법 → 고급 패턴 → 엣지 케이스 순서로 배치합니다
- "더 알아보기" 섹션을 통해 심화 내용을 분리합니다
- 선수 지식 시스템(prerequisites)이 자연스러운 점진적 공개 역할을 합니다

> 출처: [Nielsen Norman Group - Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/)

---

## 6. "Made to Stick" SUCCESs 프레임워크

칩 히스(Chip Heath)와 댄 히스(Dan Heath)의 저서에서 제시된, 아이디어를 기억에 남게 만드는 6가지 원칙입니다. 기술 교재의 각 개념이 독자에게 "붙어 있도록" 만드는 데 직접 적용할 수 있습니다.

| 원칙 | 설명 | 교재 적용 |
|------|------|-----------|
| **Simple (단순)** | 핵심을 추출해 가장 본질적인 요소만 남긴다 | 각 토픽에서 "한 가지 핵심 아이디어"를 명확히 한다 |
| **Unexpected (예상 밖)** | 놀라움으로 주의를 끈다 | 흔한 오해나 "직관과 다른 동작"을 도입부에 제시한다 |
| **Concrete (구체적)** | 감각적이고 구체적으로 만든다 | 추상적 개념을 실행 가능한 코드, 실제 시나리오로 보여준다 |
| **Credible (신뢰)** | 믿을 만한 이유를 제공한다 | 동작 원리를 설명하고, 독자가 직접 검증할 수 있는 예시를 준다 |
| **Emotional (감정)** | 신경 쓸 이유를 준다 | "이것을 알면 무엇이 가능해지는지"를 먼저 보여준다 |
| **Stories (이야기)** | 시뮬레이션 역할을 한다 | 실제 문제 상황 → 해결 과정 서사를 활용한다 |

> 출처: [Made to Stick - Wikipedia](https://en.wikipedia.org/wiki/Made_to_Stick), [Stanford GSB](https://www.gsb.stanford.edu/faculty-research/books/made-stick-why-some-ideas-survive-others-die)

---

## 7. 흔한 안티패턴 (Common Anti-Patterns)

### 7.1 지식의 저주 (Curse of Knowledge)

스티븐 핑커(Steven Pinker)가 "The Sense of Style"에서 핵심적으로 다룬 문제입니다.

**정의:** 어떤 것을 알게 되면, 그것을 모르던 때의 상태를 상상할 수 없게 되는 인지적 편향

**구체적 증상:**
- 독자도 당연히 알 것이라고 가정하고 설명을 건너뜀
- 약어(acronym)를 설명 없이 사용
- 핵심 단계를 생략 (전문가에게는 "당연한" 단계)
- 추상적 전문 용어로 가득한 밀도 높은 문장

**해결 기법:**
1. **시간차 자기 편집**: 며칠 뒤에 다시 읽으면 가정(assumption)이 보입니다
2. **대상 독자에게 읽혀보기**: 지식의 저주를 극복하는 가장 확실한 방법입니다
3. **용어를 처음 사용할 때마다 설명 추가**: "알고 있을 것이다"라고 가정하지 않습니다
4. **독자의 관점을 의식적으로 채택**: 각 문단을 쓸 때 "이 배경 지식 없이 읽으면 어떨까?"를 자문합니다

> 출처: [Earthly Blog - Curse of Knowledge](https://earthly.dev/blog/curse-of-knowledge/), [Steven Pinker - The Sense of Style](https://stevenpinker.com/publications/sense-style-thinking-persons-guide-writing-21st-century)

### 7.2 기타 안티패턴

| 안티패턴 | 설명 | 해결책 |
|----------|------|--------|
| **전문 용어 과부하** | 한 문단에 새 용어가 3개 이상 등장 | 새 용어는 하나씩, 충분한 설명과 함께 도입 |
| **독자 조사 부재** | 대상 독자의 수준을 파악하지 않고 작성 | 명시적 독자 프로필(persona) 설정 |
| **공감 부재** | 필자의 선호를 독자의 필요보다 우선 | 매 섹션마다 "독자가 여기서 무엇을 궁금해할까?" 자문 |
| **핵심 단계 누락** | 전문가에게 "당연한" 중간 단계 생략 | 초보자에게 테스트하여 누락 지점 발견 |
| **정보 과부하** | 알아야 할 것 이상을 쏟아부음 | 핵심만 본문, 나머지는 부록/참고로 분리 |
| **유혹적 세부사항 (Seductive Details)** | 흥미롭지만 학습 목표와 무관한 내용 삽입 | 메이어의 일관성 원칙에 따라 제거 |

> 출처: [AJE - Overcoming Curse of Knowledge](https://www.aje.com/arc/how-to-overcome-the-curse-of-knowledge), [I'd Rather Be Writing - Reducing Technical Language Complexity](https://idratherbewriting.com/simplifying-complexity/reducing-the-complexity-of-technical-language.html)

---

## 8. 한국어 기술 문서 작성 가이드라인

### 8.1 카카오엔터프라이즈 기술문서 쉽게 쓰기 지침

한국어 기술 문서의 대표적 가이드라인입니다.

**테크니컬 라이팅 4대 원칙:**
1. **명확성 (Clarity)**: 모호함 없이 정확하게
2. **간결성 (Conciseness)**: 불필요한 수식어 제거
3. **정성 (Accuracy)**: 기술적으로 정확하게
4. **일관성 (Consistency)**: 용어와 형식을 통일

**한국어 특유의 주의점:**
- 한국어는 역사적으로 한문 투의 복잡한 문어체와 번역 투 외래 표현이 문서에 잔존합니다
- 이러한 습관적 어려운 표현이 가독성을 해칩니다
- 직관적 이해를 위해 쉬운 표현을 의식적으로 선택해야 합니다

**P.O.W.E.R. 작성 프레임워크:**
1. **Preparing (준비)**: 주제, 독자, 개요를 먼저 정합니다 — 특히 독자의 지식 수준과 정보 필요를 파악합니다
2. **Organizing (구조화)**: 논리적 흐름을 설계합니다
3. **Writing (작성)**: 초안을 작성합니다
4. **Editing (편집)**: 명확성, 간결성, 정확성을 검토합니다
5. **Reviewing (검토)**: 제3자 리뷰를 통해 이해도를 확인합니다

**국제화를 고려한 7대 특성:**
정확성, 간결성, 어휘/표현의 적절성, 명확성, 일관성, 문장 구조, 성실성

> 출처: [카카오엔터프라이즈 - 기술문서 쉽게 쓰기 지침](https://tech.kakaoenterprise.com/105), [카카오엔터프라이즈 - 기술 문서 작성 5단계](https://tech.kakaoenterprise.com/65), [카카오 개발자 스타일 가이드](https://developers.kakao.com/docs/latest/ko/documentation-guideline/document-style-open)

### 8.2 한국어 기술 교재에 특히 유의할 점

- **번역 투 지양**: "~에 의해 수행되는" → "~가 수행하는", "~하는 것이 가능하다" → "~할 수 있다"
- **명사화 남용 지양**: "처리를 수행한다" → "처리한다"
- **외래어 남발 지양**: 대체 가능한 한국어가 있으면 사용하되, 업계 표준 용어는 그대로 사용합니다
- **합니다체 통일**: 존댓말 체계를 일관되게 유지합니다
- **긴 문장 분리**: 한국어는 수식어가 앞에 오므로 문장이 길어지기 쉽습니다. 의식적으로 분리합니다

> 출처: [개발자의 글쓰기 - SK Devocean](https://devocean.sk.com/blog/techBoardDetail.do?ID=165343&boardType=techBlog), [LINE - Technical Writing Day](https://engineering.linecorp.com/ko/blog/technical-writing-day/)

---

## 9. 추천 참고 도서 및 리소스

### 핵심 도서

| 도서 | 저자 | 핵심 기여 |
|------|------|-----------|
| **The Sense of Style** | Steven Pinker (2014) | 인지과학 기반 글쓰기 원칙, "지식의 저주" 개념의 글쓰기 적용, "고전적 산문체(classic prose)" 제안 |
| **Made to Stick** | Chip & Dan Heath (2007) | SUCCESs 프레임워크 — 아이디어를 기억에 남게 만드는 6원칙 |
| **Multimedia Learning** | Richard Mayer (2009) | 멀티미디어 학습 12원칙, 인지 부하 관리의 과학적 근거 |
| **Docs for Developers** | Jared Bhatti 외 (2021) | 개발자 대상 기술 문서 작성 실무 가이드 (한국어 번역 출간) |
| **개발자의 글쓰기** | 김철수 | 한국어 기술 문서/블로그 작성법 |

### 온라인 리소스

- [I'd Rather Be Writing - Simplifying Complexity 시리즈](https://idratherbewriting.com/simplifying-complexity/) — Tom Johnson의 기술 문서 복잡성 단순화 전략
- [Plain Language Action and Information Network (PLAIN)](https://digital.gov/guides/plain-language) — 미국 정부 쉬운 언어 가이드
- [Nielsen Norman Group](https://www.nngroup.com) — UX 관점의 정보 구조화 원칙
- [카카오엔터프라이즈 테크니컬 라이팅 블로그](https://tech.kakaoenterprise.com/105) — 한국어 기술 문서 작성 지침
- [Learning Scientists](https://www.learningscientists.org) — 인지과학 기반 학습 전략

---

## 10. 종합: AutoBook 프로젝트에 적용 가능한 체크리스트

위 연구 결과를 종합하여, 각 토픽 문서 작성 시 점검할 수 있는 체크리스트입니다.

### 작성 전
- [ ] 이 토픽의 "한 가지 핵심 아이디어"가 무엇인지 한 문장으로 정의했는가?
- [ ] 선수 지식(prerequisites) 외의 개념을 끌어오지 않았는가?
- [ ] 독자가 이 토픽에 도달할 때 무엇을 이미 알고 있는지 파악했는가?

### 도입부
- [ ] 첫 문단에서 "이 단원에서 무엇을 배우는지"를 즉시 밝히는가? (역피라미드)
- [ ] 독자가 "왜 이것을 알아야 하는지" 동기부여가 되는가? (SUCCESs - Emotional)
- [ ] 새 용어를 사용하기 전에 배경부터 설명하는가? (스캐폴딩)

### 본문
- [ ] 한 문단에 한 개념만 담았는가? (청킹)
- [ ] 추상적 개념을 먼저 구체적 예시로 보여주고 원리를 설명하는가? (구체→추상)
- [ ] 새 전문 용어마다 처음 등장 시 설명을 붙였는가? (지식의 저주 방지)
- [ ] 핵심 프로세스에 시각적 보조(표, 순서도 등)가 있는가? (이중 코딩)
- [ ] 비유를 사용했다면 구조적 유사성에 기반하며, 한계를 명시했는가?
- [ ] 흥미롭지만 학습 목표와 무관한 내용을 넣지 않았는가? (일관성 원칙)
- [ ] 능동태, 짧은 문장, 합니다체를 유지하는가?
- [ ] 번역 투나 명사화 남용이 없는가?

### 마무리
- [ ] "정리하면," 요약이 포함되어 핵심을 재확인하는가?
- [ ] 다음 단원 안내가 있어 학습 경로가 보이는가? (스캐폴딩)
- [ ] learning_content의 전 항목이 본문에 반영되었는가?
- [ ] 제3자(초보자)가 읽어도 이해할 수 있는지 파인만 기법으로 점검했는가?
