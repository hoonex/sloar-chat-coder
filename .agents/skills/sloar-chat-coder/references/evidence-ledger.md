# Evidence ledger

The evidence ledger is the boundary between what happened and what the agent merely intended.

It may live in memory for short tasks or in a checkpoint/artifact for interruption-prone work.

Recommended record shape:

```yaml
source:
  repository: owner/repo
  expected_commit: abc123
  actual_commit: abc123
  tree: def456
  dirty: false

changes:
  branch: feat/example
  files:
    - path/to/file

checks:
  - id: syntax-js
    target_commit: 789abc
    command: node --check path/to/file.js
    result: pass
  - id: browser-mobile
    target_commit: 789abc
    result: blocked
    blocker: sandbox browser policy returned ERR_BLOCKED_BY_ADMINISTRATOR

remote:
  ci:
    commit: 789abc
    result: pass
```

## Rules

- Record the state a check ran against. A passing test on an older commit is not evidence for a newer commit.
- Preserve blocked checks as blocked; do not silently downgrade them to pass.
- Separate product failures from infrastructure, external integration, transport, and permission failures.
- Screenshots are behavioral evidence only when they depict the state relevant to the assertion.
- A successful write API response is not proof that the published bytes match the verified bytes; inspect resulting identity/diff when publication integrity matters.
