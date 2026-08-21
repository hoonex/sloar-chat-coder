# Forge resilience

Sloar 0.4 separates **your local Git repository** from the **hosted forge platform** around it.

A GitHub incident can affect pull requests, APIs, Actions, search, checks, webhooks, or artifacts while your local commit/tree remains perfectly valid. A different failure can happen when GitHub itself is healthy but your current App/token simply lacks one operation-specific permission. Sloar treats those cases differently.

## Quick rules

If local source is exact and a remote service is unhealthy:

```text
LOCAL_READY + REMOTE_DEGRADED = keep working locally, defer publication
```

If the forge is reachable but the current identity/policy cannot perform the required operation:

```text
LOCAL_READY + REMOTE_PARTIAL = preserve the verified tree, change capability/policy path instead of retrying
```

Do not claim that a PR was created, CI passed, or a deployment succeeded until those remote operations are evidenced.

## Check local vs remote health

Local-only, no network requests:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py .
```

One bounded remote probe, with no automatic retry:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py . --probe
```

Use `--json` when another agent/tool should consume the result.

`--probe` checks Git transport once. For a GitHub origin, it also checks the GitHub repository API once when an authenticated `gh` CLI is available. It does not prove every write permission; operation-specific failures must be classified from actual evidence.

## Classify an observed failure

No network request is made:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py \
  --classify-file /path/to/error.log --json
```

or:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py \
  --classify-error 'rejected non-fast-forward; fetch first'
```

The classifier separates cases such as:

- GitHub App cannot update workflow files → `CAPABILITY_MISMATCH / REMOTE_PARTIAL`
- CI needs approval / `action_required` → `REMOTE_ACTION_REQUIRED / REMOTE_PARTIAL`
- branch protection/ruleset rejection → `POLICY_BLOCKED / REMOTE_PARTIAL`
- non-fast-forward / stale lease → `REMOTE_MOVED`, re-resolve the remote base
- 429 / rate limit → `REMOTE_DEGRADED`, defer rather than storm-retry
- 5xx / DNS / timeout → `REMOTE_DEGRADED`

The result includes a SHA-256 failure fingerprint but does not echo the raw error text.

## What to do during an outage

1. Keep the exact local HEAD/tree and working-tree evidence.
2. Continue implementation and local verification when repository rules permit it.
3. Save a checkpoint before a disposable workspace can disappear.
4. Mark publication/remote verification as pending.
5. Avoid identical retries when the same forge-layer failure fingerprint repeats.
6. When the forge recovers, resolve the remote base again before publishing.

## What to do for missing permission or policy

1. Keep the exact verified tree; do not rewrite product code just because one authenticated path is forbidden.
2. Do not retry with the same identity and unchanged permission set.
3. Use another transport only when it is already authorized or explicitly authorized by the user/repository.
4. Split the blocked operation when possible—for example, product publication can be separate from a workflow-file mutation.
5. Re-resolve the remote base before the eventual write because it may have moved while publication was blocked.

## Mirrors

A mirror is optional. Sloar never silently creates a GitLab/Forgejo/GitHub mirror or publishes private source to another provider simply because the primary forge is down or a permission is missing.

If the user/repository already authorizes a mirror, verify its exact commit identity before using it, and reconcile deliberately when the primary forge returns.

For the full protocol, read `.agents/skills/sloar-chat-coder/references/forge-resilience.md`.
