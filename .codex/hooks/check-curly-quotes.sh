#!/usr/bin/env bash
# check-curly-quotes.sh — PostToolUse hook
# 교재 파일(02_Books/)에서 곡선 따옴표를 검출하여 Claude에게 알린다.
# exit 0: stdout이 Claude context에 추가됨.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | grep -oP '"file_path"\s*:\s*"([^"]*)"' | head -1 | sed 's/.*"file_path"\s*:\s*"//;s/"$//')

# 교재 파일이 아니면 무시
if ! echo "$FILE_PATH" | grep -q "02_Books/"; then
  exit 0
fi

# 파일 존재 확인
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# 곡선 따옴표 검출
CURLY=$(grep -nP "[\x{2018}\x{2019}\x{201C}\x{201D}]" "$FILE_PATH" 2>/dev/null)

if [ -n "$CURLY" ]; then
  echo "WARNING: 곡선 따옴표 발견. 직선 따옴표(' \")로 교체 필요:"
  echo "$CURLY" | head -5
  exit 0
fi

exit 0
