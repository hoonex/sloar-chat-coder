# Forge resilience

Sloar 0.4 separates **your local Git repository** from the **hosted forge platform** around it.

A GitHub incident can affect pull requests, APIs, Actions, search, checks, webhooks, or artifacts while your local commit/tree remains perfectly valid. Sloar should not throw away good local work or start retrying every remote operation just because one hosted layer is failing.

## Quick rule

If local source is exact and local verification still works:

```text
LOCAL_READY + REMOTE_DEGRADED = keep working locally, defer publication
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

`--probe` checks Git transport once. For a GitHub origin, it also checks the GitHub repository API once when an authenticated `gh` CLI is available. Sloar deliberately does not loop until the service recovers.

## What to do during an outage

1. Keep the exact local HEAD/tree and working-tree evidence.
2. Continue implementation and local verification when repository rules permit it.
3. Save a checkpoint before a disposable workspace can disappear.
4. Mark publication/remote verification as pending.
5. Avoid identical retries when the same forge-layer failure fingerprint repeats.
6. When the forge recovers, resolve the remote base again before publishing.

## Mirrors

A mirror is optional. Sloar never silently creates a GitLab/Forgejo/GitHub mirror or publishes private source to another provider simply because the primary forge is down.

If the user/repository already authorizes a mirror, verify its exact commit identity before using it, and reconcile deliberately when the primary forge returns.

For the full protocol, read `.agents/skills/sloar-chat-coder/references/forge-resilience.md`.
