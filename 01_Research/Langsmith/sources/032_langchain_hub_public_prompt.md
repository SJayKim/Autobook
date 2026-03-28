---
source_id: 032
title: "LangChain Hub — 공개 프롬프트 허브, pull/push, fork, 커뮤니티 공유"
url: "https://blog.langchain.com/langchain-prompt-hub/"
type: blog
scraped_at: 2026-03-27
keywords: ["LangChain Hub"]
content_length: 1640
---

# LangChain Hub — 공개 프롬프트 허브, pull/push, fork, 커뮤니티 공유

## 설계 목적

LangChain Hub는 프롬프트 라이브러리가 모범 사례(best practice)를 인코딩하여 누구나 사용할 수 있도록 하는 공간이다. 개발자들이 새로운 활용 사례와 정제된 프롬프트를 발견하도록 돕는 것이 핵심 목표다.

## 구축 배경

세 가지 인사이트가 Hub 재구축을 이끌었다:

1. **모델 다양성**: Claude, Llama2 등 다양한 모델이 등장하면서 각 모델에 최적화된 프롬프트가 필요해졌다.
2. **투명성**: 프롬프트를 숨기지 않고 내부 작동 원리를 누구나 볼 수 있도록 공개한다.
3. **협업**: 기술팀과 비기술팀이 함께 프롬프트를 편집하고 개선할 수 있도록 지원한다.

## Pull / Push 워크플로우

```python
from langchain import hub

# 공개 프롬프트 다운로드 (handle/prompt-name 형식)
prompt = hub.pull("hwchase17/eli5-solar-system")

# 프롬프트 업로드 (자신의 handle 사용)
hub.push("<handle>/topic-joke", prompt)
```

## 탐색 기능

공개 Hub에서 프롬프트를 탐색하는 기준:

- **정렬**: 최신순, 즐겨찾기순, 조회순, 다운로드순
- **필터**: 사용 사례(use case), 모델(model), 언어(language)별 필터링

## 버전 관리

각 커밋은 새 버전으로 저장되며 이전 버전 복원이 가능하다. 커밋 해시를 통해 특정 버전을 코드에서 고정 참조할 수 있다.

## 커뮤니티 지향 설계

사용자들이 다른 사람의 작업을 기반으로 발전시킬 수 있도록 설계되었다:

- **포크(Fork)**: 공개 프롬프트를 개인 조직으로 복제하여 수정
- **플레이그라운드**: 브라우저에서 직접 프롬프트 테스트
- **공유**: 창의적이고 유용한 프롬프트를 커뮤니티와 공유
