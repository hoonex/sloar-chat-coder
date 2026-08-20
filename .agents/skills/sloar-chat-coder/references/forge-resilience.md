# Forge resilience

A Git repository and a hosted forge are different failure domains. Git can be healthy while GitHub, GitLab, Actions, PR APIs, search, webhooks, or artifact services are degraded.

Sloar therefore treats forge health as an overlay on the normal repository state machine rather than as permission to abandon exact local work.

## Status model

Use evidence to classify the current task into one of these statuses:

- `LOCAL_READY` — exact source is materialized and local implementation/verification can continue.
- `REMOTE_HEALTHY` — the required remote Git/forge capabilities are responding normally.
- `REMOTE_DEGRADED` — one or more required hosted capabilities are failing or timing out, but local work remains intact.
- `PUBLICATION_BLOCKED` — implementation/verification may be complete, but required remote publication or verification cannot currently be proven.
- `BLOCKED` — the task cannot continue faithfully with the capabilities or durable source currently available.

Statuses may coexist. `LOCAL_READY + REMOTE_DEGRADED` is a normal degraded-mode state.

## Separate Git transport from forge platform health

Do not infer that the whole forge is healthy because `git fetch` works. Conversely, an API/Actions outage does not imply local Git state is damaged.

When relevant, collect distinct evidence for:

1. local Git identity — HEAD, tree, dirty state;
2. Git transport — fetch/ls-remote/push path;
3. forge API — repository/PR/status API path;
4. CI/Actions — queue/start/log/artifact path;
5. deployment/integration — only if required by the task.

A failure in one layer should not automatically escalate work into another layer.

## Degraded-mode rules

When a forge layer is degraded:

1. Preserve the exact local checkpoint and evidence ledger.
2. Continue IMPLEMENT/VERIFY locally if the repository rules and available execution allow it.
3. Do not claim PUBLISH or REMOTE_VERIFY success without remote evidence.
4. Mark publication as deferred rather than repeatedly retrying the same request.
5. Re-probe only when evidence changes, a bounded retry window is justified, or the user explicitly asks.
6. Before eventual publication, re-resolve the remote base because it may have moved during the outage.

## Retry budget

Platform incidents are particularly prone to retry storms. Use the normal Sloar failure fingerprint plus the affected forge layer.

Example fingerprint:

```text
layer=forge-api
operation=create-pr
base=abc123
status=502
error=upstream unavailable
```

The same fingerprint with unchanged inputs is not evidence for another immediate retry. One bounded retry can be reasonable for an isolated transient failure. Repeated failures should switch the task to `REMOTE_DEGRADED` / `PUBLICATION_BLOCKED` until new evidence appears.

## Durable outage checkpoint

When publication is deferred, the checkpoint should include:

```json
{
  "stage": "PUBLISH",
  "local_status": "LOCAL_READY",
  "remote_status": "REMOTE_DEGRADED",
  "publication": "PUBLICATION_BLOCKED",
  "base": "<expected base sha>",
  "head": "<verified local head sha>",
  "tree": "<verified local tree sha>",
  "verified": ["syntax", "focused-test"],
  "pending": ["remote-base-recheck", "publish", "ci"]
}
```

If the local worktree itself is disposable, also preserve a bundle, patch, artifact, or other repository-approved exact transport with checksum/provenance.

## Optional mirror/fallback

A secondary forge or mirror is optional, not a default requirement. Use it only when the repository/user has authorized it and when it genuinely improves durability or delivery.

Never silently publish proprietary/private source to a new provider merely because the primary forge is down. Never create a mirror as a workaround for missing permission.

If a mirror already exists, verify its exact commit identity before using it as source or publication transport. Reconciliation back to the primary forge remains a deliberate publication step.

## Recovery after the forge returns

When remote health recovers:

1. resolve current remote base/head again;
2. compare with the outage checkpoint;
3. inspect intervening commits/PR movement;
4. reconcile deliberately;
5. rerun checks affected by reconciliation;
6. publish exact verified state;
7. complete normal REMOTE_VERIFY and CLEANUP.

Do not assume the pre-outage base is still publishable merely because the service is reachable again.
