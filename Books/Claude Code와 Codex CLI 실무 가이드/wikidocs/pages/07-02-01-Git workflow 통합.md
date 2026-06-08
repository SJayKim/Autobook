# 7.2.1 Git workflow 통합

코드 에이전트가 일을 잘 끝냈는지는 결국 git 기록에 남습니다. 하지만 권한이 넓은 에이전트는 main 브랜치에 바로 push하거나, force push로 동료의 작업을 덮어쓰거나, 원치 않는 파일을 함께 commit할 수 있습니다. 이 단원은 Claude Code와 Codex CLI 양쪽에서 안전한 commit·branch·PR 워크플로를 동일한 규칙으로 강제하는 방법을 정리합니다.

가장 먼저 막아야 할 것은 main 브랜치 직접 push입니다. Claude Code에서는 settings.json의 deny 매처로 명시적으로 차단합니다.

```json
{
  "permissions": {
    "deny": [
      "Bash(git push origin main*)",
      "Bash(git push origin master*)",
      "Bash(git push * --force*)",
      "Bash(git push * -f *)",
      "Bash(git commit --no-verify*)"
    ],
    "ask": [
      "Bash(git push*)"
    ]
  }
}
```

deny는 allow보다 항상 우선하므로, 와일드카드 allow를 둔 프로젝트에서도 위 다섯 줄로 가장 위험한 케이스가 차단됩니다. ask는 그 외 모든 push를 사용자 확인으로 돌려, 의도하지 않은 원격 동기화를 거릅니다.

Codex CLI에서는 동일 효과를 sandbox·approval 조합으로 냅니다. workspace-write 모드는 기본적으로 네트워크가 막혀 있어 `git push` 자체가 실패합니다. push가 필요한 작업에서는 profile을 잠시 전환하고, approval_policy를 on-request로 두어 push 직전 승인을 받습니다. 더 강한 방어가 필요하면 서버 측 보호 브랜치 규칙을 같이 켭니다. GitHub에서 main 브랜치에 push 보호와 PR 필수 리뷰를 설정하면, 클라이언트 단의 실수를 한 번 더 거릅니다.

feature 브랜치와 작은 PR 단위는 모델에게 명령으로 강제합니다. CLAUDE.md와 AGENTS.md에 동일한 한 줄을 적어 두면 두 도구가 같은 규칙을 따릅니다.

```markdown
# Git workflow
- Never commit to main. Always create feat/* or fix/* branch.
- One PR = one purpose. Keep diff under ~300 lines when possible.
- Use `gh pr create` to open PR; never push directly to remote main.
```

commit 메시지 컨벤션도 같은 방식으로 둡니다. Claude Code는 자체적으로 `Co-Authored-By` 줄을 붙이는 규칙을 따르므로, 팀 표준이 다르면 CLAUDE.md에 명시적으로 적습니다. Conventional Commits를 쓰는 팀이라면 prefix 규칙도 함께 적습니다.

```markdown
# Commit conventions
- Prefix: feat / fix / docs / refactor / test / chore
- Subject ≤ 72 chars, body explains 'why' not 'what'
- Footer: Co-Authored-By: Claude <noreply@anthropic.com>
```

PR 생성과 리뷰는 두 가지 길로 자동화합니다. 첫째는 `gh` CLI를 직접 호출하는 방식으로, 가장 빠르고 의존성이 적습니다. 둘째는 MCP github 서버를 통해 도구로 노출하는 방식으로, 권한과 토큰을 한곳에서 관리할 수 있습니다.

```bash
# Claude Code/Codex 공통: gh CLI 한 줄
gh pr create --title "feat: add login retry" \
  --body "$(cat <<'EOF'
## Summary
- Add 3-retry policy on transient 5xx
- Add unit test for backoff

## Test plan
- [x] pytest tests/auth/
- [ ] manual smoke test
EOF
)"
```

되돌리기 가능성을 마지막 안전망으로 둡니다. 에이전트가 잘못 만든 commit을 force push로 덮어쓰는 대신, 항상 `git revert`로 새 commit을 쌓도록 규칙을 둡니다. 위 deny 예시에서 force push가 막혔으므로 강제하기 쉽습니다. 작업을 잘못 시작했다면 작업 디렉토리를 `git stash`로 떨궈 두고 새 브랜치를 다시 만듭니다. 원격에 이미 푸시된 commit은 revert만 허용하고, 로컬에서만 다듬을 수 있는 commit은 amend도 허용한다는 두 줄 규칙이면 대부분의 사고를 막습니다.

정리하면, 두 도구의 Git workflow는 deny 패턴이나 sandbox로 main·force·--no-verify를 봉인하고, CLAUDE.md·AGENTS.md에 동일한 브랜치·PR·commit 규칙을 적어 두며, gh CLI 또는 MCP github 서버로 PR을 자동 생성하고, 사고가 나면 revert를 우선으로 두는 네 단계로 정리됩니다. 다음 단원에서는 긴 작업이 컨텍스트를 압박할 때 사용하는 압축·메모리 운영 패턴을 다룹니다.
