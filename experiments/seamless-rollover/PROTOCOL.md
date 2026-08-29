# Seamless Rollover Demo — Agent Protocol

This experiment targets one chat-native problem only: **a fresh chat must be able to continue repository work without the user reconstructing the previous conversation.** It does not attempt multi-agent coordination yet.

## User-facing intent

Accept natural-language rollover requests in the user's language. Examples include "새 채팅으로 넘겨줘", "새 채팅에서 이어서 하게 해줘", "prepare a handoff", and equivalent wording.

Do not require the user to memorize a slash command.

## Internal agent contract

Agent-facing instructions SHOULD be concise English even when the user-facing conversation is not English.

### PREPARE_ROLLOVER

When the user asks to move to a fresh chat:

1. Re-resolve the current repository identity and mutable remote state needed for the task.
2. Compact only durable task state: goal, completed work, active work, pending work, durable decisions, verification evidence, blockers, and one next action.
3. Exclude conversational narration, obsolete plans, hidden reasoning, duplicated facts, and unverified success claims.
4. Build a Sloar rollover checkpoint.
5. Persist it through the strongest authorized durable path that does not modify the product branch unnecessarily.
6. Prefer a repository sidecar branch named `sloar/rollover-state` when GitHub write is available. Store `latest.json` and immutable checkpoint JSON there. Product branches remain untouched.
7. If remote state persistence is unavailable, preserve a local checkpoint and explicitly report that it is not cross-chat durable; fall back to a copyable compact checkpoint only when necessary.
8. Return a short user-facing confirmation plus exactly one fresh-chat resume sentence.

Recommended resume sentence:

```text
Resume the latest Sloar rollover for OWNER/REPO.
```

### RESUME_ROLLOVER

When a fresh chat receives the resume sentence:

1. Resolve the repository independently; do not assume the checkpoint is current truth.
2. Load the latest authorized rollover checkpoint from `sloar/rollover-state` or the strongest available durable fallback.
3. Re-resolve current HEAD, tree, branch/PR state, working state when available, relevant remote refs, and required capabilities.
4. Compare current durable reality with the checkpoint.
5. If unchanged, reconstruct a compact context capsule and continue from the recorded next action.
6. If changed, mark `RECONCILE_REQUIRED`, reconcile against current durable repository state, invalidate stale checkpoint facts, and rerun only verification affected by the change.
7. Never ask the user to restate information already recoverable from repository state or the checkpoint.
8. Keep the visible resume report short; repository work should start immediately after recovery.

## Sidecar branch layout

```text
branch: sloar/rollover-state

.sloar/rollover/
  latest.json
  checkpoints/
    <checkpoint-id>.json
```

`latest.json` is only a pointer. Immutable checkpoint files contain compact recovery metadata. The sidecar branch is metadata transport, not product source.

## Checkpoint schema

```json
{
  "schema": 1,
  "kind": "sloar-seamless-rollover",
  "checkpoint_id": "...",
  "created_at": "...",
  "repository": "OWNER/REPO",
  "identity": {
    "head": "...",
    "tree": "...",
    "branch": "...",
    "dirty": false,
    "status_sha256": "..."
  },
  "context": {
    "goal": "...",
    "completed": [],
    "active": [],
    "pending": [],
    "decisions": [],
    "evidence": [],
    "blockers": [],
    "next_action": "..."
  }
}
```

The checkpoint MUST state that it is recovery metadata and never outranks freshly re-resolved repository state.

## User-visible response contract

Old chat, successful durable handoff:

```text
Sloar handoff saved.
Repository: OWNER/REPO
Checkpoint: <id>

새 채팅에서 이것만 보내면 된다:
Resume the latest Sloar rollover for OWNER/REPO.
```

Fresh chat, unchanged repository:

```text
Sloar restored.
Recovered: <goal>
Current state: <short stage/status>
Next: <next action>

이어서 진행한다.
```

Fresh chat, repository moved:

```text
Sloar restored, but the repository changed after the handoff.
Checkpoint: <old head>
Current: <new head>
Reconciliation required; current repository state takes priority.
```

Then reconcile and continue without asking the user to reconstruct the old chat.
