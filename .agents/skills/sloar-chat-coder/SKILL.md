---
name: sloar-chat-coder
description: Keep repository development exact and recoverable across disposable chat coding sessions, including when a hosted forge, API, CI system, or remote publication path is degraded. Use for repository implementation, debugging, testing, publication, outage handling, or recovery when sandbox state, GitHub/GitLab state, connected tools, CI, or concurrent actors can change during the task.
license: MIT
compatibility: Requires a repository source of truth and a code-execution environment for full engineering workflows. Forge-specific fallback rules apply only when equivalent authorized remote capabilities exist.
metadata:
  version: "0.4.0"
---

# Sloar Chat Coder

Sloar is a repository-engineering continuity protocol for chat-based coding. It does not choose the target repository's engineering method. It makes the work exact, recoverable, escalation-aware, concurrency-safe, evidence-bounded, outage-tolerant, and understandable on first use.

## First-run onboarding

When the user/session is new to Sloar or required capabilities are uncertain, run a compact **ONBOARD** check before repository modification. Inspect the capabilities actually exposed in the current session; do not assume a plugin, app, sandbox, GitHub write path, browser, or CI runner exists because another session had one.

For ChatGPT/Codex, distinguish **Plugin** (workflow package), **App** (authenticated external data/actions), and **Skill** (reusable instructions). Installing Sloar does not itself authorize GitHub. Conversely, missing GitHub integration does not block local engineering when a lower capability path is sufficient.

Read [references/environment-onboarding.md](references/environment-onboarding.md) when setup is unknown or the user asks how to start. If local execution is available, `scripts/wizard.py` can produce a machine-readable local readiness report. Hosted capabilities must still be resolved from the current agent/tool inventory.

When ONBOARD is shown to the user, prefer a compact readiness capsule:

```text
Sloar readiness
Repository: ready | missing | unknown
Execution: ready | missing | unknown
GitHub read/write: ready | partial | missing | unknown
CI/browser: ready | partial | missing | unknown
Next: one concrete action, or "ready to work"
```

Do not turn a healthy first run into a long setup tutorial. Keep onboarding brief once the environment is established.

## Seven invariants

1. **Durable truth beats reconstructed chat memory.** Resolve repository facts from durable state whenever it exists.
2. **Identity before modification.** Establish the intended commit SHA, tree SHA, and working-tree state before editing.
3. **Sandbox before remote execution.** Use the sandbox work container as the default workstation once exact source is materialized.
4. **Lowest sufficient capability wins.** Escalate only when the current level cannot faithfully complete the required operation.
5. **Diagnose before retry.** A retry must be justified by new evidence or changed inputs.
6. **Evidence bounds claims.** Never report a check, deployment, merge, or behavior as successful without relevant evidence.
7. **Revalidate before publication.** Resolve mutable remote refs again immediately before a write that depends on them.

## Task state machine

Repository work follows this lifecycle:

```text
ONBOARD? -> RECOVER -> IDENTIFY -> MATERIALIZE -> BRANCH -> IMPLEMENT -> VERIFY -> PUBLISH -> REMOTE_VERIFY -> CLEANUP
```

Do not skip a state whose exit condition is required by the task. Read [references/state-machine.md](references/state-machine.md) for state contracts.

Forge health is a separate overlay on this lifecycle. A task may be `LOCAL_READY` while the hosted forge is `REMOTE_DEGRADED`; in that case IMPLEMENT/VERIFY can continue locally while publication remains deferred. Read [references/forge-resilience.md](references/forge-resilience.md).

## Repository identity contract

Treat repository identity as:

```text
HEAD commit SHA + HEAD tree SHA + working-tree state
```

A matching commit SHA with unexpected local modifications is not the same engineering state. Preserve unfamiliar surviving work until ownership is known.

## Capability selection

Use the lowest level that can perform the operation exactly:

```text
L0 sandbox native
L1 sandbox acquisition
L2 connected repository transport
L3 supply mission
L4 bounded remote execution
L5 blocked
```

Read [references/capability-ladder.md](references/capability-ladder.md) before escalating beyond ordinary sandbox work.

## Forge resilience

Git and the hosted forge are different failure domains. A working `git fetch` does not prove PR/API/Actions health, and a hosted API outage does not invalidate an exact local worktree.

When remote behavior is suspect, classify evidence by layer instead of repeatedly retrying the same operation:

```text
LOCAL_READY
REMOTE_HEALTHY | REMOTE_DEGRADED
PUBLICATION_BLOCKED | ready
```

If local source and execution remain valid, continue local implementation and verification while preserving an outage checkpoint. Never claim PUBLISH or REMOTE_VERIFY success while the required remote layer is unproven. When the forge recovers, re-resolve the remote base before publication because it may have moved during the outage.

`scripts/forge-health.py` is an optional local classifier. Its default mode is network-free; `--probe` performs one bounded Git transport probe and, when supported/authenticated, one forge API probe. It never retries automatically.

## Failure handling

Create a mental or written failure fingerprint from the operation, relevant inputs, failing phase, exit/status code, normalized error, and—when remote infrastructure is involved—the affected forge layer. Inspect logs or returned error details before changing source.

```text
same fingerprint + same inputs != useful retry
same fingerprint + changed evidence/input = possible bounded retry
```

Do not create autonomous retry loops. Repeated platform-layer failures should transition to `REMOTE_DEGRADED` / `PUBLICATION_BLOCKED`, not a retry storm. Read [references/recovery.md](references/recovery.md) when execution, transport, or chat state is lost or ambiguous.

## Concurrent actors and publication guard

Assume branches, PRs, workflows, deployments, and artifacts may move while the task is active. Capture the expected base identity before substantial work, then resolve it again before publication.

If the remote identity changed, stop publication, inspect the new durable state, deliberately reconcile, and rerun affected verification. After a forge outage, always perform this revalidation even if the original base was known exactly before the outage. Read [references/concurrency.md](references/concurrency.md).

## Verification and evidence

Verification should be change-aware and repository-defined. Source changes are not complete merely because the files were written.

Maintain an evidence ledger containing the checks that actually ran, their target state, result, and blocker when applicable. No evidence means no success claim. During a remote outage, local green checks can support `LOCAL_READY` but cannot substitute for required REMOTE_VERIFY evidence. Read [references/verification.md](references/verification.md) and [references/evidence-ledger.md](references/evidence-ledger.md).

## Actions and remote missions

Remote execution is a fallback, not the default development workstation. If a bounded Actions mission is necessary, define exact source identity, mission type, inputs, allowed effects, outputs, integrity checks, terminal status, and cleanup before dispatch.

Use supply missions for acquisition/transport gaps when the sandbox can still perform the engineering loop. Use remote execution only when the sandbox cannot faithfully execute the required capability. If Actions itself is the degraded forge layer, do not create more Actions runs as a workaround for that same incident. Read [references/actions-missions.md](references/actions-missions.md) first.

## Recovery checkpoint

For expensive or interruption-prone tasks, persist a machine-readable checkpoint containing at least repository, base identity, task branch/head, current state-machine stage, verified evidence IDs, pending checks, and owned temporary resources. A checkpoint is a recovery aid, not a source-of-truth replacement.

When publication is deferred by a forge incident, also record local/remote status and the remote checks still pending. If the local workspace is disposable, preserve an exact repository-approved artifact, bundle, or patch with integrity evidence before the workspace can disappear.

## Completion report

At completion, report only:

- the exact durable state changed or published;
- the checks that actually ran and their results;
- any blocked check and its concrete blocker;
- any reconciliation caused by concurrent remote movement or forge recovery;
- any temporary remote resource that could not be cleaned up.

If remote publication is blocked, say so explicitly rather than presenting `LOCAL_READY` as task completion. Do not expose Sloar mechanics when the normal path is healthy unless they materially explain a limitation or result.
