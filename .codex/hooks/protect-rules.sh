#!/usr/bin/env bash
# protect-rules.sh
# PreToolUse 훅: Rules/ 폴더 내 파일 수정을 차단한다.
# $TOOL_INPUT에 file_path가 포함되어 있으면 검사.

INPUT="$1"

# file_path 값을 추출 (JSON 형태로 전달됨)
FILE_PATH=$(echo "$INPUT" | grep -oP '"file_path"\s*:\s*"([^"]*)"' | head -1 | sed 's/.*"file_path"\s*:\s*"//;s/"$//')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Rules/ 경로 포함 여부 확인
if echo "$FILE_PATH" | grep -qiE '(^|/)Rules/'; then
  echo "BLOCKED: Rules/ 폴더의 파일은 수정할 수 없습니다. 이 폴더는 불변 규칙입니다."
  exit 2
fi

# curriculum.schema.json도 보호
if echo "$FILE_PATH" | grep -qE 'curriculum\.schema\.json$'; then
  echo "BLOCKED: curriculum.schema.json은 수정할 수 없습니다."
  exit 2
fi

exit 0
