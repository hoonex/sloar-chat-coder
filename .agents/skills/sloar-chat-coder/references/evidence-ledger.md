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

anchors:
  verified_commit: 789abc
  production_commit: 789abc
  deployment: dpl_example

changes:
  branch: feat/example
  files:
    - path/to/file
  boundary:
    changed:
      - settings UI
    preserved:
      - existing authentication contract
    deliberately_not_changed:
      - billing
    limitations:
      - live provider not available in this environment

checks:
  - id: syntax-js
    kind: compile
    supports_claims:
      - source parses
    target_commit: 789abc
    command: node --check path/to/file.js
    result: pass
  - id: browser-mobile
    kind: rendered-ui
    supports_claims:
      - mobile layout is visually usable
    target_commit: 789abc
    result: blocked
    blocker: sandbox browser policy returned ERR_BLOCKED_BY_ADMINISTRATOR

remote:
  ci:
    commit: 789abc
    result: pass
```

## Claim/evidence matching

A passing check supports only claims inside that check's real scope.

Examples:

```text
compile/build pass
  -> can support a compile/build claim
  -> does not by itself prove rendered UI quality or production health

browser/visual evidence
  -> can support the depicted UI/interaction claim
  -> does not prove unrelated backend/runtime behavior

integration/live probe
  -> can support the bounded external integration behavior that was actually exercised

merge/deploy success
  -> proves publication/deployment transition only to the extent the provider reports it
  -> does not substitute for route/runtime health when that health is separately observable
```

Repository-defined acceptance gates remain authoritative. When a required evidence type cannot be collected, report the claim as unverified/blocked instead of silently substituting a weaker check.

## Rules

- Record the state a check ran against. A passing test on an older commit is not evidence for a newer commit.
- Preserve blocked checks as blocked; do not silently downgrade them to pass.
- Separate product failures from infrastructure, external integration, transport, and permission failures.
- Screenshots are behavioral evidence only when they depict the state relevant to the assertion.
- A successful write API response is not proof that the published bytes match the verified bytes; inspect resulting identity/diff when publication integrity matters.
- Keep repository, verification, and runtime anchors separate when they can legitimately differ.
- Do not call a turn complete merely because a final chat response was attempted. For interruption-prone work, a durable terminal turn snapshot can prove engineering terminality even if response delivery later fails.
