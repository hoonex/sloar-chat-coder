# Sloar Chat-Native Continuity Demo

Experimental, isolated prototype for making Sloar usable from the **first chat** and cheap to continue in a **fresh chat** when context gets crowded.

This demo is **not part of Sloar 0.4.0** and does not change the stable skill contract.

## Goal

Turn first use from this:

```text
find Sloar repo
→ clone it
→ run install.py
→ run wizard.py
→ explain setup to the chat
→ start coding
```

into this when the current chat has enough authorized capability:

```text
User:
이 저장소 Sloar로 개발해.
https://github.com/OWNER/REPO

<request>

→ agent checks capabilities
→ installs/restores Sloar safely when possible
→ resolves exact repository state
→ starts the requested work
```

Then turn context rollover from this:

```text
old chat gets long
→ giant handoff prompt
→ several thousand characters copied into a new chat
→ new chat re-learns the project
```

into this:

```text
old chat: "새 채팅으로 넘겨줘"
→ durable compact checkpoint
→ new chat: "Resume the latest Sloar session for OWNER/REPO."
→ repository revalidation
→ response-language restoration
→ compact context reconstruction
→ continue
```

The intended lifecycle is:

```text
BOOTSTRAP_SESSION? -> NORMAL_WORK -> PREPARE_ROLLOVER -> RESUME_SESSION -> NORMAL_WORK
```

The success criteria are simple:

1. **A first-time user should not need to understand Sloar installation mechanics when the chat can bootstrap it safely.**
2. **A fresh chat should not require the user to restate previous task context.**
3. **An English resume control sentence must not silently switch the user's conversation language.**

See [`FIRST_USE.md`](FIRST_USE.md) for the beginner flow and [`PROTOCOL.md`](PROTOCOL.md) for the agent-facing contract.

## Preferred user experience

### First chat

```text
이 저장소 Sloar로 개발해.
https://github.com/OWNER/REPO

로그인 화면 만들어줘.
```

The agent checks whether Sloar already exists, what repository/GitHub/execution capabilities are actually available, bootstraps only through authorized safe paths, resolves repository identity, preserves the established user-facing response language, and starts the requested work.

If durable write is unavailable, the agent must not claim that Sloar was installed. It can still use the protocol ephemerally when possible and clearly mark rollover durability as unavailable. Only then should it show the smallest fallback, such as the existing local installer.

### Normal work

The user talks normally. No Sloar prefix is required for every request.

```text
모바일 레이아웃도 고쳐줘.
테스트까지 해줘.
```

### Move to a fresh chat

```text
새 채팅으로 넘겨줘.
```

Expected response:

```text
Sloar handoff saved.
Repository: OWNER/REPO
Checkpoint: <id>

새 채팅에서 이것만 보내면 된다:
Resume the latest Sloar session for OWNER/REPO.
```

The English resume line is a **control phrase only**. It is not a request to change the visible conversation to English. The checkpoint stores the established user-facing `response_language` when known.

### Fresh chat

```text
Resume the latest Sloar session for OWNER/REPO.
```

The new chat restores `response_language` before its first visible reply, re-resolves repository reality, loads the checkpoint, reconciles movement if needed, reconstructs only compact working context, and continues.

A remote-only chat may be able to prove HEAD/tree/branch and PR/CI state without seeing any local worktree. In that case Sloar records the working state as **unobserved** rather than inventing a clean/dirty value. Matching observable identity may still be `EXACT`, but that label must not be presented as proof that an unobserved worktree is clean.

## Durable rollover backend

The preferred chat-native backend remains a GitHub sidecar branch named `sloar/rollover-state`.

- It survives disposable chat/sandbox sessions.
- A fresh session with repository read access can recover it.
- It does not add runtime checkpoint files to product branches.
- It keeps the repository as the durable coordination surface.

The checkpoint is never current truth. Fresh repository state always wins.

```text
branch: sloar/rollover-state

.sloar/rollover/
  latest.json
  checkpoints/
    <checkpoint-id>.json
```

## Language continuity

Sloar now treats these as separate channels:

```text
agent/control language  !=  user-facing response language
```

Agent protocol text and the one-line resume command may remain concise English. The user's established response language is stored independently in checkpoint context, for example:

```json
{
  "context": {
    "response_language": "ko-KR"
  }
}
```

A later explicit user request to change languages still takes priority.

## Local helper

`rollover.py` exists to test checkpoint generation and context reconstruction without network access. It is a development/fallback helper, **not the intended first-user UX**.

Local helper state defaults to `.git/sloar-rollover/`, so handoff generation does not dirty the product worktree.

```bash
python3 rollover.py handoff /path/to/repo \
  --goal "Finish university settings" \
  --completed "state model implemented" \
  --active "desktop settings UI" \
  --pending "mobile landscape regression" \
  --decision "preserve existing school behavior" \
  --evidence "typecheck: pass" \
  --response-language "ko-KR" \
  --next "run visual regression"
```

Resume locally:

```bash
python3 rollover.py resume /path/to/repo
```

For local captures, a changed HEAD/tree/branch/dirty/status identity reports `RECONCILE_REQUIRED`. The comparison helper also accepts a mapping from remote-only agents; unavailable working-tree fields are surfaced as unobserved and do not create a false reconciliation by themselves. When `response_language` is present, the capsule surfaces it for the fresh agent.

## Scope deliberately excluded

- parallel-chat orchestration;
- learned memory or RL policies;
- automatic context-limit prediction;
- replacing Git/PR/CI as source of truth;
- modifying the stable Sloar skill.

Those should be evaluated only after first-use bootstrap and rollover prove useful in real chat sessions.

## Test

```bash
python3 -m unittest discover -s tests -v
```

The tests cover local exact recovery, dirty-state detection, repository movement detection, remote-only exact/reconcile behavior, compact capsule rendering, the one-line session resume instruction, response-language persistence, and compatibility when older checkpoints omit the language field.
