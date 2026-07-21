#!/usr/bin/env bash
# on-compact.sh — context 압축 후 핵심 상태를 재주입한다.
# subagent에서도 실행될 수 있으므로, 규칙 리마인더만 공통 출력하고
# 루프 상태 복원은 orchestrator(메인 프로세스)에서만 출력한다.

# 1. 핵심 규칙 리마인더 (공통 — orchestrator/subagent 모두 유용)
echo "=== AutoBook 핵심 규칙 리마인더 ==="
echo "- 합니다체 통일, 직선 따옴표만(' \"), ## 이하 헤더 금지"
echo "- Rules/ 폴더 수정 금지"
echo "- 한 문단 한 개념, 새 굵은 용어 3개/문단 이하"
echo "- 번역 투/명사화 남용 금지, 80자 초과 문장 분리"

# 2. subagent 판별 — CLAUDE_AGENT_NAME이 설정되어 있으면 subagent
# subagent는 규칙 리마인더만 받고, 루프 상태/계속 지시는 받지 않는다.
if [ -n "$CLAUDE_AGENT_NAME" ]; then
  echo ""
  echo "(subagent: $CLAUDE_AGENT_NAME — 할당된 단일 작업만 완료하라)"
  exit 0
fi

# 3. orchestrator 전용: 현재 autobook 루프 상태 복원
CURRICULUM=$(find 02_Books/ -maxdepth 2 -name "curriculum.json" 2>/dev/null | head -1)
if [ -n "$CURRICULUM" ]; then
  BOOK_NAME=$(echo "$CURRICULUM" | sed 's|02_Books/||;s|/curriculum.json||')
  echo ""
  echo "=== AutoBook 루프 상태 ==="
  echo "책이름: $BOOK_NAME"
  echo "curriculum: $CURRICULUM"

  # 브랜치
  BRANCH=$(git branch --show-current 2>/dev/null)
  echo "브랜치: $BRANCH"

  # 완료/전체 토픽 수
  PAGES_DIR="02_Books/${BOOK_NAME}/wikidocs/pages"
  if [ -d "$PAGES_DIR" ]; then
    DONE=$(find "$PAGES_DIR" -name "[0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.md" 2>/dev/null | wc -l)
    echo "작성 완료 토픽: ${DONE}개"
  fi

  echo ""
  echo ">>> /autobook 루프 중이었다면: 멈추지 말고 다음 미작성 토픽부터 계속 진행하라. <<<"
fi
