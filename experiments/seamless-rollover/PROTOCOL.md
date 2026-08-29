# Sloar Chat-Native Continuity Demo — Agent Protocol

This experiment targets two chat-native continuity problems:

1. a first-time user should be able to start from a repository URL without understanding Sloar installation mechanics when the current chat can bootstrap safely;
2. a fresh chat must be able to continue repository work without the user reconstructing the previous conversation.

It does not attempt multi-agent coordination yet.

## User-facing intent

Accept natural-language first-use and rollover requests in the user's language.

First-use examples:

- `이 저장소 Sloar로 개발해. https://github.com/OWNER/REPO`
- `Sloar로 이 프로젝트 작업 시작해.`
- `Use Sloar for https://github.com/OWNER/REPO and continue with my request.`

Rollover examples:

- `새 채팅으로 넘겨줘`
- `새 채팅에서 이어서 하게 해줘`
- `prepare a handoff`

Do not require the user to memorize a slash command. Agent-facing protocol text SHOULD remain concise English even when the user-facing conversation is not English.

## BOOTSTRAP_SESSION

Enter this state only when the user explicitly asks to use Sloar for a repository or when an already-Sloar-enabled repository instructs the agent to do so. Never silently install Sloar merely because a GitHub URL was mentioned.

1. Resolve the target repository independently from the user's URL/name and inspect the capabilities actually exposed in the current chat.
2. Read repository guidance before mutation, especially existing `AGENTS.md`, and check for `.agents/skills/sloar-chat-coder/SKILL.md`.
3. If Sloar is already present, do not reinstall blindly. Read the installed contract, resolve current repository identity, and continue through normal recovery.
4. If Sloar is absent, determine whether a safe authorized durable installation path exists.
5. When a safe write path exists, obtain the documented stable Sloar core, preserve unrelated repository guidance, install only the required Sloar files, and verify the resulting durable state before claiming bootstrap success.
6. Do not assume `latest main` equals the stable release merely because the Sloar source repository is reachable. Resolve the documented stable contract/version deliberately.
7. If repository write is unavailable but local/sandbox execution is available, Sloar may be used ephemerally for the current engineering loop. Do not claim durable installation or cross-chat rollover persistence.
8. If neither a durable write path nor a usable local repository source exists, ask only for the smallest missing capability/source needed to proceed. Do not dump a full setup tutorial by default.
9. After bootstrap/restoration, resolve exact repository identity, relevant mutable remote state, and task-required capabilities.
10. Begin the user's actual requested work immediately. A healthy first run should not become an onboarding ceremony.

### Bootstrap success claim

A durable bootstrap claim requires evidence that the target repository now contains the intended Sloar installation through an authorized path. Repository read access alone is not proof of installation capability.

Recommended visible response:

```text
Sloar ready.
Repository: OWNER/REPO
State: <short current state>

<start the requested work>
```

If Sloar already existed:

```text
Sloar restored.
Repository: OWNER/REPO
State: <short current state>

<continue the requested work>
```

If durable bootstrap is unavailable:

```text
Sloar can be used for this chat, but durable setup is unavailable with the current repository permissions.
Cross-chat rollover will not be claimed as durable.
```

Then continue through the strongest valid lower-capability path when possible.

## NORMAL_WORK

After bootstrap, the user should not need to mention Sloar on every turn.

During ordinary work:

- repository reality outranks conversational memory;
- maintain only the durable task facts needed for recovery;
- do not expose Sloar mechanics when the path is healthy unless they explain a material limitation;
- preserve evidence for claims that will matter at rollover or publication.

## PREPARE_ROLLOVER

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
Resume the latest Sloar session for OWNER/REPO.
```

## RESUME_SESSION

Enter this state when a fresh chat receives the resume sentence or an unambiguous equivalent.

1. Resolve the repository independently; do not assume the checkpoint is current truth.
2. Determine whether Sloar is installed/accessible and load the latest authorized rollover checkpoint from `sloar/rollover-state` or the strongest available durable fallback.
3. Re-resolve current HEAD, tree, branch/PR state, working state when available, relevant remote refs, and required capabilities. Record working-tree observability explicitly rather than inventing a clean/dirty value.
4. Compare current durable reality with the checkpoint.
5. If no observable identity field contradicts the checkpoint, classify the resume as `EXACT`, reconstruct a compact context capsule, explicitly surface any unobserved identity fields, and continue from the recorded next action.
6. If an observable identity field changed, mark `RECONCILE_REQUIRED`, reconcile against current durable repository state, invalidate stale checkpoint facts, and rerun only verification affected by the change.
7. Never ask the user to restate information already recoverable from repository state or the checkpoint.
8. Keep the visible resume report short; repository work should start immediately after recovery.

`EXACT` means exact for the identity fields the current session can actually observe. It MUST NOT be phrased as proof that an unobserved working tree is clean. A remote-only chat can therefore resume `EXACT` when HEAD/tree/branch and other observable durable state match while reporting `working_state` as unobserved.

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
    "working_state_observed": false,
    "dirty": null,
    "status_sha256": null
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

When a local worktree is available, set `working_state_observed` to `true` and record the actual boolean `dirty` value plus the status digest. When it is unavailable, set `working_state_observed` to `false` and keep `dirty` / `status_sha256` null. Unknown working state is not a reconciliation event by itself; a contradictory observable field is.

The checkpoint MUST state that it is recovery metadata and never outranks freshly re-resolved repository state.

## User-visible response contract

Old chat, successful durable handoff:

```text
Sloar handoff saved.
Repository: OWNER/REPO
Checkpoint: <id>

새 채팅에서 이것만 보내면 된다:
Resume the latest Sloar session for OWNER/REPO.
```

Fresh chat, unchanged observable repository state:

```text
Sloar restored.
Recovered: <goal>
Current state: <short stage/status>
Next: <next action>

이어서 진행한다.
```

If working-tree state is unavailable, append a compact qualification such as `Working tree: unobserved` rather than implying it is clean.

Fresh chat, repository moved:

```text
Sloar restored, but the repository changed after the handoff.
Checkpoint: <old head>
Current: <new head>
Reconciliation required; current repository state takes priority.
```

Then reconcile and continue without asking the user to reconstruct the old chat.

## Lifecycle summary

```text
BOOTSTRAP_SESSION? -> NORMAL_WORK -> PREPARE_ROLLOVER -> RESUME_SESSION -> NORMAL_WORK
```

The lifecycle is intentionally small. Parallel-chat coordination, learned memory, and automatic context-limit prediction remain outside this experiment until the basic first-use and rollover UX is proven.
