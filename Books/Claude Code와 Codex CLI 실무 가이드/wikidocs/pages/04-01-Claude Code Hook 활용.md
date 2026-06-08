# 4.1 Claude Code Hook 활용

이 섹션의 토픽과 학습 목표는 다음과 같습니다.

- **4.1.1 Hook 6종 개요와 동작 순서** — PreToolUse, PostToolUse, UserPromptSubmit, Stop, SessionStart, Notification, PreCompact의 트리거 시점과 데이터 흐름을 설명할 수 있다
- **4.1.2 PreToolUse로 위험 작업 차단** — PreToolUse hook으로 도구 인자를 검사해 위험 명령을 차단하는 스크립트를 작성할 수 있다
- **4.1.3 PostToolUse로 포맷·린트 자동화** — PostToolUse hook으로 파일 편집 직후 포맷·린트·테스트를 자동 실행할 수 있다
- **4.1.4 UserPromptSubmit으로 정책 주입** — UserPromptSubmit hook으로 모든 사용자 메시지 앞에 정책 문구를 자동 첨부할 수 있다
- **4.1.5 SessionStart로 환경 점검** — SessionStart hook으로 세션 시작 시 git 상태·환경 변수·외부 의존성을 점검할 수 있다
