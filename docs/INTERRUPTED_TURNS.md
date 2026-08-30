# When a chat response never finishes

A chat host can occasionally remain visibly "answering" without ever delivering a final response during a long repository task.

Sloar cannot force the ChatGPT/app/server host to cancel, finish, or revive that generation. Sloar 0.6 instead makes long engineering turns durable so another chat can recover the exact repository state even when the previous visible response never terminates.

## Durable turn flow

```text
begin work
  -> persist ACTIVE turn
  -> persist bounded progress snapshots when durable facts materially change
  -> persist a terminal snapshot before the final visible completion report
  -> send the final chat response
```

This separates engineering terminality from response-delivery terminality. If the code/PR/CI work finished but the final response stalled, a fresh chat can revalidate the repository and replay the terminal result without redoing completed work.

## Fresh-chat recovery

A latest terminal turn is classified as:

```text
TERMINAL_REPLAY_AVAILABLE
```

A latest unterminated turn is classified as:

```text
ACTIVE_OR_INTERRUPTED
```

Elapsed time alone never proves the previous host process is dead. Revalidate repository truth first.

## Explicit takeover and fencing

When the user explicitly chooses to continue from another chat, an unterminated turn can be taken over. Takeover creates a new turn ID and increments a monotonic fencing epoch.

Before later durable writes/publication, an ACTIVE turn checks that its `turn_id + epoch` still owns the durable pointer. This makes an old apparently-stuck session stop on its next guarded write if it later resumes after a fresh chat has taken over.

Sloar cannot retroactively cancel a write that was already in flight before the epoch changed.

## What Sloar does not claim to solve

Sloar does not control:

- the host UI spinner;
- server-side generation cancellation/restart;
- delivery of the final assistant message;
- already-in-flight external writes.

It provides loss-resistant recovery, duplicate-work reduction, stale-session fencing, and exact reconstruction of terminal engineering state.

See `.agents/skills/sloar-chat-coder/references/operational-continuity.md` for the normative contract.
