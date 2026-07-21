---
name: build-pdf
description: 02_Books/{책이름}/ 의 curriculum.json과 토픽 .md를 묶어 Autobook Series 양식의 PDF를 생성한다. 표지·목차·들어가며·Phase/Section/Topic 본문을 자동 렌더링한다.
user-invocable: true
allowed-tools: Read, Glob, Bash
---

# 교재 PDF 빌드

## 절차

### 1단계: 책 선택

1. 인자가 주어졌으면 그 이름을 책 디렉토리로 사용한다 (예: `/build-pdf 하네스 엔지니어링`).
2. 인자가 없으면 `02_Books/` 하위 디렉토리 목록을 보여주고 사용자에게 선택 요청.
3. `02_Books/{책이름}/curriculum.json`과 `02_Books/{책이름}/wikidocs/pages/` 존재를 확인한다.
   - 없으면 안내 후 종료.

### 2단계: 표지 메타 결정

기본값: 부제·키워드는 비어 있어도 PDF는 생성된다. 사용자가 명시하지 않으면 다음을 시도한다.

1. `02_Books/{책이름}/wikidocs/pages/00-들어가며.md`의 첫 1~3 문단을 훑어 부제·키워드를 추론하고 사용자에게 확인을 요청한다.
2. 사용자가 부제/키워드를 직접 제시했으면 그 값을 사용한다.
3. 사용자가 “기본값”을 원하면 부제·키워드 없이 진행한다.

확정 사항:
- `subtitle`: 표지 부제 한 줄
- `keywords`: 점(·) 또는 공백으로 구분된 키워드 줄
- `year`: 기본 현재 연도
- `out`: 기본 `{repo_root}/{책이름}.pdf`

### 3단계: 빌드 실행

다음 Bash 명령으로 빌드한다 (Windows, bash 셸):

```
python ".Codex/skills/build-pdf/build_pdf.py" "{책이름}" \
  --subtitle "{subtitle}" \
  --keywords "{keywords}" \
  --year "{year}" \
  --out "{out}"
```

옵션 인자는 값이 비어 있으면 생략한다. `python`이 없으면 `py -3`으로 대체한다.

### 4단계: 결과 보고

빌드가 끝나면 다음을 사용자에게 알린다.

- 출력 PDF 경로와 파일 크기
- 누락된 토픽 ID 목록 (있다면) — `[INFO] missing topic md:` 라인을 그대로 인용한다
- 다음에 사용자가 할 수 있는 동작 안내 (예: PDF 열기)

## 주의

- 한글 폰트는 `C:/Windows/Fonts/malgun.ttf`, `malgunbd.ttf`, `consola.ttf`를 사용한다. 다른 OS에서는 별도 매핑이 필요하다.
- `fpdf2` 패키지가 필요하다. 미설치 시 `pip install fpdf2` 안내.
- 파일명 패턴은 `{pp}-{ss}-{tt}-*.md` (예: `01-02-03-*.md`)이며, curriculum.json의 토픽 ID `pp.ss.tt`와 1:1 매핑된다.
- `02_Books/` 하위 어떤 책이라도 동일 스크립트로 빌드된다 (책별 별도 스크립트 불필요).
