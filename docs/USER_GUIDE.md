# Sloar Chat Coder User Guide

This guide is for users who want to go from **first use -> normal development -> upgrade -> fresh-chat handoff -> stuck-response recovery** without learning Sloar internals first.

Current stable: **0.8.1**

## 1. First use

Open a fresh ChatGPT/Codex chat and paste this. Replace only `OWNER/REPO` and the task.

```text
Use the following Sloar Chat Coder to develop this repository.
Sloar: https://github.com/hoonex/sloar-chat-coder

Target repository:
https://github.com/OWNER/REPO

Task:
<what you want to build or change>

Read the current Sloar usage guidance and current repository state before proceeding.
```

Including the Sloar source URL lets a fresh chat resolve the current project instead of guessing what the name means.

### If Sloar is already installed

A shorter request is enough:

```text
Use Sloar for this repository.
https://github.com/OWNER/REPO

<task>
```

## 2. Normal work

After Sloar is installed and the session has resolved the repository, you do not need to repeat the Sloar URL for every request.

Examples:

```text
Fix the mobile layout on the login screen.
```

```text
Find the cause of this error, fix it, and run the relevant tests.
```

```text
Implement this feature and prepare the PR.
```

Sloar treats durable repository state as more authoritative than reconstructed chat memory.

## 3. Vague web-design requests are okay

Users do not need to know design vocabulary.

Example:

```text
I want a web app where friends can plan a trip together.
It should feel polished and work well on mobile, but I do not know the design style.
```

If the request is already clear enough, the agent proceeds. If a wrong assumption would cause expensive redesign, it asks only the high-value questions needed to choose the direction.

If the user says:

```text
You decide what fits best.
```

optional design clarification stops and the agent chooses from product/repository evidence.

Design details:
- [web-design-guidance](../.agents/skills/web-design-guidance/SKILL.md)
- [Adaptive discovery](../.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)
- [Design taxonomy](../.agents/skills/web-design-guidance/references/design-taxonomy.md)
- [Anti-AI-Slop](../.agents/skills/web-design-guidance/references/anti-ai-slop.md)

## 4. Upgrade Sloar without restarting the task

Since 0.8.1 the default UX is **automatic update awareness, followed by an upgrade only after user approval**.

On the first Sloar repository turn in a chat, and after an intentional fresh-chat resume/takeover, Sloar compares the installed version with the canonical stable once when that stable source is reachable.

```text
installed == stable
-> stay silent and continue work

new stable discovered
-> Sloar update available: 0.8.0 -> 0.8.1. Upgrade now?
-> user approves
-> run the safe UPGRADE_SESSION automatically

stable lookup fails/is unavailable
-> update status = unknown
-> continue normal repository work on the installed release
```

Discovering a newer stable does not itself authorize a repository write. Sloar must not modify its core or companions until the user approves the notice or explicitly requests an upgrade.

After approval, the normal flow is:

```text
re-resolve repository identity
-> re-read installed Sloar version
-> confirm the approved stable identity
-> back up the old Sloar core
-> upgrade Sloar-owned files only
-> migrate only known-official companion bundles safely
-> preserve custom/unrecognized companions
-> run available validation
-> bridge the active checkpoint
-> continue the same task
```

To start the same flow manually at any time, say:

```text
Upgrade this active Sloar session to the latest stable release, preserve the current task state, and continue the work.
```

Local fallback:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

The local Wizard does not secretly fetch a stable version from the network. If a caller has already resolved stable, pass it explicitly:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py . \
  --stable-version 0.8.1 --json
```

`updates.status` is one of `current`, `update_available`, `ahead`, `unknown`, or `not_installed`.

Contract: [upgrading.md](../.agents/skills/sloar-chat-coder/references/upgrading.md)

## 5. Move to a fresh chat

In the current chat:

```text
Move this Sloar session to a fresh chat.
```

When durable rollover is available, Sloar preserves the current goal, completed/active/pending work, important decisions, evidence, repository identity, and one next action.

Paste the returned Resume sentence in the fresh chat. The default form is:

```text
Resume the latest Sloar session for OWNER/REPO.
```

The new chat revalidates the current repository before trusting the checkpoint. If the canonical stable source is available, the resumed session also performs one update-awareness check.

Contract: [chat-native-continuity.md](../.agents/skills/sloar-chat-coder/references/chat-native-continuity.md)

## 6. If a response stays stuck in `answering`

Sloar distinguishes two cases.

### A. The agent keeps extending the task

For one unchanged failure fingerprint, Sloar uses a bounded corrective cycle instead of repeating `one more check` forever.

If the same failure remains, the turn should finish as `PARTIAL`, `BLOCKED`, or `FAILED` with the exact remaining gate.

Contract: [turn-terminalization.md](../.agents/skills/sloar-chat-coder/references/turn-terminalization.md)

### B. The host/app/server itself stalls

Sloar cannot force the ChatGPT/app spinner to stop.

In a fresh chat, use:

```text
The previous Sloar task appears to have stalled while answering. Check the saved turn state and the current repository, then continue safely.
```

A terminal prior turn can be replayed after revalidation. An interrupted active turn can be reconciled and explicitly taken over.

Guide: [INTERRUPTED_TURNS.md](INTERRUPTED_TURNS.md)

## 7. How Sloar works overall

The internal repository lifecycle is roughly:

```text
ONBOARD?
-> RECOVER
-> IDENTIFY
-> MATERIALIZE
-> BRANCH
-> IMPLEMENT
-> VERIFY
-> PUBLISH
-> REMOTE_VERIFY
-> CLEANUP
```

Core rules:

```text
current durable repository truth > reconstructed chat memory
resolve exact source identity before modification
same failure + same inputs != useful retry
no relevant evidence -> no success claim
```

## 8. Manual/local installation fallback

If the current ChatGPT/Codex environment cannot write the repository or execute code, Sloar must not pretend installation succeeded.

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

Readiness wizard:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

Connections/capabilities: [CONNECTIONS.md](CONNECTIONS.md)

## 9. Copy-paste cheat sheet

```text
# First use
Use the following Sloar Chat Coder to develop this repository.
Sloar: https://github.com/hoonex/sloar-chat-coder
Target repository: https://github.com/OWNER/REPO
Task: <task>
Read the current Sloar usage guidance and current repository state before proceeding.

# Already installed
Use Sloar for this repository.
https://github.com/OWNER/REPO
<task>

# Start an upgrade manually
Upgrade this active Sloar session to the latest stable release, preserve the current task state, and continue the work.

# Fresh chat
Move this Sloar session to a fresh chat.

# Recover a stuck response
The previous Sloar task appears to have stalled while answering. Check the saved turn state and the current repository, then continue safely.
```

## More documentation

- [FIRST_RUN.md](FIRST_RUN.md)
- [CONNECTIONS.md](CONNECTIONS.md)
- [CHATGPT_PLUGINS.md](CHATGPT_PLUGINS.md)
- [FORGE_RESILIENCE.md](FORGE_RESILIENCE.md)
- [INTERRUPTED_TURNS.md](INTERRUPTED_TURNS.md)
