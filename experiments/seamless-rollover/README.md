# Sloar Seamless Rollover Demo

Experimental, isolated prototype for reducing the biggest chat-based coding continuity cost: moving to a fresh chat after context becomes crowded.

This demo is **not part of Sloar 0.4.0** and does not change the stable skill contract.

## Goal

Turn this:

```text
old chat gets long
→ user asks for a giant handoff prompt
→ user copies several thousand characters
→ new chat re-learns the project
```

into this:

```text
old chat: "새 채팅으로 넘겨줘"
→ durable compact checkpoint
→ new chat: "Resume the latest Sloar rollover for OWNER/REPO."
→ repository revalidation
→ compact context reconstruction
→ continue
```

The success criterion is simple: **the user should not need to restate previous task context in the new chat.**

## Why a sidecar branch

The preferred chat-native backend is a GitHub branch named `sloar/rollover-state`.

- It survives disposable chat/sandbox sessions.
- A fresh ChatGPT session with repository read access can recover it.
- It does not add runtime checkpoint files to the product branch.
- It keeps the repository itself as the durable coordination surface.

The checkpoint is never treated as current truth. On resume, current repository/remote state is re-resolved first and compared with the checkpoint.

## Local helper

`rollover.py` demonstrates checkpoint generation and context reconstruction without requiring network access or GitHub credentials. Local helper state defaults to `.git/sloar-rollover/`, so creating a handoff does not dirty the product worktree. Durable cross-chat publication remains the agent's job through the sidecar branch.

```bash
python3 rollover.py handoff /path/to/repo \
  --goal "Finish university settings" \
  --completed "state model implemented" \
  --active "desktop settings UI" \
  --pending "mobile landscape regression" \
  --decision "preserve existing school behavior" \
  --evidence "typecheck: pass" \
  --next "run visual regression"
```

It prints a fresh-chat instruction:

```text
Resume the latest Sloar rollover for OWNER/REPO.
```

Resume locally:

```bash
python3 rollover.py resume /path/to/repo
```

If HEAD/tree/branch/working state changed, the capsule reports `RECONCILE_REQUIRED` rather than silently trusting stale state.

## Chat behavior

The user can ask for rollover naturally in any language. The agent-facing protocol is kept in concise English for unambiguous Git/tool terminology. See `PROTOCOL.md`.

The intended user-visible flow is intentionally tiny:

```text
User: 새 채팅으로 넘겨줘.

Assistant:
Sloar handoff saved.
Repository: OWNER/REPO
Checkpoint: <id>

새 채팅에서 이것만 보내면 된다:
Resume the latest Sloar rollover for OWNER/REPO.
```

A fresh chat should then recover, revalidate, and continue without asking the user to explain the previous work again.

## Scope deliberately excluded

- parallel-chat orchestration;
- learned memory or RL policies;
- automatic context-limit prediction;
- replacing Git/PR/CI as source of truth;
- modifying the stable Sloar skill.

Those can be evaluated only after rollover itself proves useful.

## Test

```bash
python3 -m unittest discover -s tests -v
```

The test suite checks exact recovery, dirty-state detection, repository movement detection, and compact capsule rendering.
