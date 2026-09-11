# Sloar Chat Coder

Reliable repository engineering across disposable AI coding sessions.

Sloar Chat Coder is an Agent Skill for chat-based repository work where sandboxes can disappear, repository state can move concurrently, tools can fail, long turns can self-extend, and the host can stall before delivering a final response.

Current stable: **0.10.0**

<p align="center">
  <a href="VERSION"><img src="https://img.shields.io/badge/stable-0.10.0-2563eb?style=flat-square" alt="stable 0.10.0"></a>
  <a href="https://github.com/hoonex/sloar-chat-coder/actions/workflows/validate.yml"><img src="https://github.com/hoonex/sloar-chat-coder/actions/workflows/validate.yml/badge.svg?branch=main" alt="Validate Sloar"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-16a34a?style=flat-square" alt="MIT License"></a>
</p>

<p align="center">
  <a href="#first-time-paste-this-first"><b>Quick Start</b></a> ·
  <a href="docs/USER_GUIDE.md"><b>User Guide</b></a> ·
  <a href="#upgrade-without-restarting-the-task"><b>Upgrade</b></a> ·
  <a href="#move-to-a-fresh-chat"><b>Fresh Chat</b></a> ·
  <a href="#web-development-includes-architecture-and-design-reasoning"><b>Web Architecture + Design</b></a> ·
  <a href="README.ko.md">한국어</a>
</p>

> Durable repository truth over reconstructed conversation memory. Evidence before completion claims.

## Using ChatGPT chat with a GitHub plugin/app

Sloar is read and applied by the assistant in the current chat. The GitHub
connector supplies the repository operations actually exposed to that session.
Using Sloar this way does not require Codex CLI, an API key, or local Python.

- Instructions and repository edits can operate through exact connector reads/writes.
- Python helpers run only when a code runtime is available; they are optional.
- Tests require an actual runtime or applicable repository CI. Saved code is not a test pass.
- Codex CLI A/B evaluation is separate development tooling, not a measurement of this chat.
- Cross-chat state must actually be saved remotely. Local locks do not lock GitHub.
- Existing vendored copies need their own authorized upgrade; canonical changes do not update them automatically.

See [the chat/GitHub workflow](.agents/skills/sloar-chat-coder/references/chat-github-workflow.md)
for capability selection, conflict-rejecting publication, and runtime-free handoff.

## First time? Paste this first

Open a fresh ChatGPT/Codex chat and replace only `OWNER/REPO` and the task.

```text
Use the canonical Sloar Chat Coder from:
https://github.com/hoonex/sloar-chat-coder

Before modifying the target repository, actually load Sloar in this session:
- resolve the current canonical Sloar source to an exact commit SHA;
- read .agents/skills/sloar-chat-coder/SKILL.md from that exact SHA;
- read only task-relevant Sloar references from the same SHA.
If canonical Sloar cannot actually be read, report SLOAR_UNAVAILABLE and do not silently continue without Sloar.

Target repository:
https://github.com/OWNER/REPO

Task:
<what you want to build or change>

Read the current repository state before proceeding.
```

**For a fresh chat that has never seen Sloar, include the Sloar source URL and require real activation as above.** Merely writing `Use Sloar Chat Coder` is not activation evidence. If Sloar is already installed in the target repository, a shorter request is enough because the session can read the installed contract directly:

```text
Use Sloar for this repository.
https://github.com/OWNER/REPO

<task>
```

Full user guide: **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)**

한국어: [README.ko.md](README.ko.md)

## Common actions

| Situation | What the user needs to say |
| --- | --- |
| First use | Paste the `Sloar:` source URL + target repository + task into a fresh chat |
| Normal development | Just describe the repository task |
| Green CI missed the real bug | Report the real-device/production symptom; Sloar re-checks semantic ownership and whether the existing evidence actually covers the acceptance claim |
| Unfamiliar or AI-grown web repository | Just describe the feature; Sloar can build a bounded architecture topology first and inspect only the task-relevant owners |
| Vague web UI request | No design vocabulary required; Sloar asks only high-value questions when needed |
| Delegate design | `You decide what fits best.` |
| Upgrade | On the first Sloar repository turn/fresh-chat recovery, Sloar checks stable once when possible. If a newer stable exists, it asks once; after approval, the safe upgrade process is automated |
| Move chats | Ask for a fresh-chat handoff, then paste the returned Resume sentence |
| Stuck response | In a fresh chat, ask Sloar to inspect saved turn state and current repository before continuing |

## How Sloar works

0.10 keeps the compact reasoning kernel introduced in 0.9 and adds evidence-backed architecture discovery for substantial web work:

```text
OBSERVE
-> MODEL
-> ACT
-> PROVE
-> RECONCILE
```

The detailed repository lifecycle still exists, but it expands only when continuity, publication, remote capability, or recovery risk makes those distinctions useful.

Core safeguards:

```text
current durable repository truth > reconstructed chat memory
resolve exact source identity before identity-dependent modification
identify the authoritative semantic owner before stacking a workaround
same failure + same inputs != useful retry
no relevant verification evidence -> no success claim
revalidate mutable remote state immediately before publication-dependent writes
```

The MODEL/PROVE steps treat user-visible semantics as stronger than convenient implementation labels. For example, `queued` does not automatically prove a requirement phrased as `before callback starts`; Sloar tests the latest valid observable boundary when that edge can change correctness.

For asynchronous/stateful work, Sloar also checks Promise/callback/event results, resource ownership, late finalizers, cancellation ownership, retry safety/liveness, and transition-adjacent races instead of validating only final store state.

Details:
- [Reasoning kernel](.agents/skills/sloar-chat-coder/references/reasoning-kernel.md)
- [Async evidence closure](.agents/skills/sloar-chat-coder/references/async-evidence-closure.md)
- [State machine](.agents/skills/sloar-chat-coder/references/state-machine.md)
- [Verification](.agents/skills/sloar-chat-coder/references/verification.md)

The central continuity idea remains the same: re-resolve Git/repository/checkpoint/CI truth instead of reconstructing a long development session from memory alone.

## Web development includes architecture and design reasoning

### Fast, evidence-backed architecture orientation

0.10 adds a two-layer **web architecture capsule** for unfamiliar repositories and codebases that have accumulated repeated AI edits.

```text
DURABLE SOURCE
-> deterministic topology snapshot
-> evidence-backed semantic owner map
-> task-specific read set
```

When execution is available, Sloar can first run:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/web-architecture-map.py . --json
```

The helper reports bounded facts such as Git identity, declared framework/router/state/data/styling systems, package scripts, source roots, entrypoint candidates, convention-based route files, configs, and token/global-style candidates. It deliberately does **not** guess business ownership or runtime data flow from folder names.

The agent then reads the smallest source path needed for the actual task and distinguishes:

```text
DECLARED  package/config says it
OBSERVED  repository path/content shows it
CONFIRMED semantic ownership is directly established by source
INFERRED  durable evidence supports it but does not fully establish it
UNKNOWN   not resolved
```

That makes architecture discovery faster without turning a generated map into a second, stale source of truth. The normal owner path is:

```text
route/page
-> data/cache
-> domain/application state
-> component/rendering
-> styling/tokens
-> async/interaction lifecycle
-> persistence/navigation/external side effects
```

Details:
- [Web architecture capsule](.agents/skills/sloar-chat-coder/references/web-architecture-capsule.md)
- [Structural UI engineering](.agents/skills/web-design-guidance/references/structural-ui-engineering.md)

### Design reasoning and product craft

Since 0.8.0, the bundled `web-design-guidance` assumes users may know the experience they want without knowing words such as `glassmorphism`, `neumorphism`, or `brutalism`.

Example:

```text
I want a web app where friends can plan a trip together.
It should feel polished and work well on mobile, but I do not know the design style.
```

If the request is clear enough, the agent proceeds. If a wrong assumption would cause expensive redesign, it asks only the high-value questions needed to choose the direction.

Clarification depth is adaptive rather than fixed:

```text
nearly clear -> 0 questions
moderate ambiguity -> roughly 1-3 high-value questions as needed
high ambiguity -> a compact batch around purpose/users/platform/tone
"you decide" -> stop optional clarification
```

Ordinary language can then be translated into multi-axis **Design DNA**:

```text
philosophy / tone
material language
composition
interaction language
motion posture
density
typography / color stance
```

The companion also reviews common generated/default UI convergence through **Anti-AI-Slop** guidance. The goal is not to ban purple, glass, bento, Inter, or any particular style. The goal is to replace unchosen defaults with product-specific decisions.

0.10 also treats internal architecture as UI quality. `VISUAL`, `BEHAVIOR`, `STRUCTURE`, `RESILIENCE`, and `HYGIENE` are separate claims: a beautiful screenshot does not prove coherent ownership, safe effect lifecycles, token integrity, or removal of obsolete paths.

For explicitly Apple-like interaction work, the specialized companion adds product-craft rules around hidden complexity, learnable novelty, transition continuity, restrained new technology, and a small delight budget. Polish never excuses weak accessibility, performance, or architecture.

Details:
- [web-design-guidance](.agents/skills/web-design-guidance/SKILL.md)
- [Adaptive discovery](.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)
- [Design taxonomy](.agents/skills/web-design-guidance/references/design-taxonomy.md)
- [Anti-AI-Slop](.agents/skills/web-design-guidance/references/anti-ai-slop.md)
- [Structural UI engineering](.agents/skills/web-design-guidance/references/structural-ui-engineering.md)
- [Apple-specific companion](.agents/skills/apple-web-design/SKILL.md)

## Upgrade without restarting the task

**Update awareness is automatic; installation starts only after user approval.**

On the first Sloar repository turn in a chat, and after an intentional fresh-chat resume/takeover, Sloar checks the canonical stable source once when that source is reachable.

```text
installed == stable
-> stay silent and continue work

new stable exists
-> Sloar update available: 0.9.1 -> 0.10.0. Upgrade now?
-> user approves
-> automated safe upgrade while preserving current task state

stable lookup unavailable
-> update status = unknown
-> continue ordinary repository work
```

Sloar does not silently rewrite the repository merely because a newer stable exists. After approval, it can automate backup, Sloar-owned file replacement, known-official companion migration, custom companion preservation, validation, and the active-session checkpoint bridge.

To start the same flow manually at any time, say in the active chat:

```text
Upgrade this active Sloar session to the latest stable release,
preserve the current task state, and continue the work.
```

A normal upgrade re-resolves repository identity, backs up the old Sloar core, updates Sloar-owned files, verifies bundled companions and available checks, then continues the same task.

Customized companions are not replaced merely because their reported version is older.

Local fallback:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

The local Wizard never performs a hidden stable-version network lookup. A caller that already resolved stable may pass it explicitly:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py . \
  --stable-version 0.10.0 --json
```

Contract: [upgrading.md](.agents/skills/sloar-chat-coder/references/upgrading.md)

## Move to a fresh chat

In the current chat, request a fresh-chat handoff.

When durable rollover is available, Sloar preserves the current goal, completed/active/pending work, important decisions, evidence, repository identity, and one next action outside the product branch.

Paste the returned Resume sentence in the fresh chat. The default form is:

```text
Resume the latest Sloar session for OWNER/REPO.
```

The fresh chat revalidates the current repository before trusting the checkpoint. When the canonical stable source is reachable, this resumed session also performs one bounded update-awareness check.

Contract: [chat-native-continuity.md](.agents/skills/sloar-chat-coder/references/chat-native-continuity.md)

## If the response never finishes

Sloar distinguishes two failure modes.

### The agent keeps extending with `one more check`

For one unchanged failure fingerprint, the default corrective cycle is bounded:

```text
diagnose
-> at most one corrective change for that diagnosis
-> rerun affected verification
```

If the same failure remains, Sloar does not stack another symptom patch. It re-checks the authoritative ownership boundary; without differentiated evidence for a structurally different fix, the turn finishes as `PARTIAL`, `BLOCKED`, or `FAILED` with the exact remaining gate. Autonomous instructions such as `finish it` do not authorize infinite retry/search/wait/poll loops.

### The ChatGPT/app/server host itself stalls

Sloar cannot force the host spinner to stop.

In a fresh chat, use:

```text
The previous Sloar task appears to have stalled while answering.
Check the saved turn state and the current repository, then continue safely.
```

Guide: [docs/INTERRUPTED_TURNS.md](docs/INTERRUPTED_TURNS.md)

## Manual/local installation fallback

The current ChatGPT/Codex session may not expose repository write or code-execution capability. Sloar must not claim installation succeeded when it cannot actually write durable state.

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/project
```

Readiness wizard:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

## Documentation

**For users**
- [User guide](docs/USER_GUIDE.md) — first use, normal work, upgrades, fresh chats, stuck-response recovery
- [First run](docs/FIRST_RUN.md)
- [Connections/capabilities](docs/CONNECTIONS.md)
- [ChatGPT Plugin/App/Skill](docs/CHATGPT_PLUGINS.md)
- [Interrupted turns](docs/INTERRUPTED_TURNS.md)
- [Forge/CI resilience](docs/FORGE_RESILIENCE.md)

**Engineering/design protocol**
- [Reasoning kernel](.agents/skills/sloar-chat-coder/references/reasoning-kernel.md)
- [Async evidence closure](.agents/skills/sloar-chat-coder/references/async-evidence-closure.md)
- [Ownership and evidence closure](.agents/skills/sloar-chat-coder/references/ownership-evidence-closure.md)
- [Web architecture capsule](.agents/skills/sloar-chat-coder/references/web-architecture-capsule.md)
- [Evidence ledger](.agents/skills/sloar-chat-coder/references/evidence-ledger.md)
- [General web-design companion](.agents/skills/web-design-guidance/SKILL.md)
- [Structural UI engineering](.agents/skills/web-design-guidance/references/structural-ui-engineering.md)
- [Adaptive discovery](.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)
- [Design taxonomy](.agents/skills/web-design-guidance/references/design-taxonomy.md)
- [Anti-AI-Slop](.agents/skills/web-design-guidance/references/anti-ai-slop.md)
- [Sloar core Skill](.agents/skills/sloar-chat-coder/SKILL.md)

## License

MIT. See [LICENSE](LICENSE).