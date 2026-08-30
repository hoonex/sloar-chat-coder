# Sloar Chat Coder

Reliable repository engineering across disposable AI coding sessions.

Sloar Chat Coder is an Agent Skill for chat-based repository work where sandboxes can disappear, repository state can move concurrently, connected tools can fail, long turns can self-extend, and the host itself can stall before delivering a final response.

Current version: **0.7.0**

> Durable repository truth over reconstructed conversation memory. Evidence before completion claims.

## 10-second usage

```text
First use -> repository URL + "Use Sloar for this repository"
Normal work -> just describe the repository task
Substantial web UI -> bundled web-design-guidance applies after repository design rules
Explicit Apple-like UI -> apple-web-design may refine the general design guidance
Upgrade an old active session -> ask Sloar to upgrade while preserving current task state
Move chats -> request a handoff, then paste the returned Resume sentence in a fresh chat
Stuck response -> recover durable turn state from a fresh chat
```

## Start without learning the internals

When the current chat has an authorized durable repository path:

```text
Use Sloar for this repository:
https://github.com/OWNER/REPO

<your task>
```

The agent preserves repository guidance, resolves actual capabilities, installs or restores stable Sloar only when it can really write durable state, re-resolves repository identity, and starts the task.

### Local/manual fallback

```bash
git clone https://github.com/hoonex/sloar-chat-coder.git
cd sloar-chat-coder
python3 .agents/skills/sloar-chat-coder/scripts/install.py --target /path/to/your-project
```

First Run Wizard:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/wizard.py .
```

The installer adds only Sloar's owned marker block to `AGENTS.md`; unrelated repository guidance remains authoritative.

## 0.7: repository-aware web design guidance

0.7.0 bundles a general companion for substantial user-facing web UI work:

```text
.agents/skills/web-design-guidance/SKILL.md
```

It is not a style template and it does not make Sloar the owner of the product's visual language. Design precedence is:

```text
explicit user direction
> repository design / brand / product guidance
> shipped UI, tokens, components and assets
> bundled web-design-guidance fallback
```

A coherent existing product system is preserved instead of being replaced with whatever visual trend happens to be popular.

### Compact Design Read

For a new or materially redesigned surface, the companion may establish:

```text
surface: product | dashboard | landing | auth/onboarding | settings | content | commerce | other
primary user job:
visual tone:
density: compact | balanced | spacious
existing system to preserve:
signature decision:
responsive risk:
interaction/state risk:
```

If the user and repository already answer these questions, the agent infers the Design Read and proceeds instead of blocking on a taste questionnaire.

### What the companion checks

- existing tokens, typography, spacing, radii, shadows, icons and component primitives;
- user journey and information hierarchy before decorative styling;
- surface-specific needs for product apps, dashboards, landing pages, auth/onboarding, settings, content and commerce;
- text and responsive resilience across real content, zoom and narrow layouts;
- relevant hover/pressed/focus/selected/loading/empty/error states;
- keyboard, touch and accessibility behavior;
- motion that explains causality or continuity rather than adding arbitrary choreography;
- recurring generic generated-UI patterns before they become accidental product language.

Contextual anti-pattern checks include default split heroes, generic purple/pink AI gradients, gratuitous bento/card walls, decorative glass, fake charts, floating blobs, emoji replacing an established icon system, excessive empty hero space in dense product UI, centered-everything layouts, and animation on every element. These are not absolute bans: use them when product context or explicit direction justifies them.

### Visual evidence

For web UI:

```text
build/compile green != visually correct
DOM geometry green != balanced hierarchy
CSS property present != readable rendered material
```

When browser/screenshot capability exists, visual-success claims should be supported by rendered evidence appropriate to the changed surface and its responsive/state risks.

If rendered evidence is unavailable or blocked, report that scope as unverified or `PARTIAL` rather than keeping the chat turn alive indefinitely. Sloar's bounded terminalization rules still apply.

### Apple-specific refinement

The existing `apple-web-design` companion remains bundled, but it is not the default web language. Use it only when the user or repository explicitly wants Apple-like direct manipulation, interruptible motion, velocity-aware settling, or functional translucent materials. General repository-aware design discovery still comes first.

### Public inspirations

The 0.7 companion independently generalizes useful structures observed in these MIT-licensed projects without vendoring or requiring them at runtime:

- `nextlevelbuilder/ui-ux-pro-max-skill` — product-aware design decisions, style/color/type and anti-pattern structure;
- `superdesigndev/superdesign-skill` — persistent repository-aware design-system memory;
- `educlopez/ui-craft` — surface recipes, acceptance bars, rendered self-review and anti-generic generated-UI thinking.

See `.agents/skills/web-design-guidance/NOTICE.md` for source notes.

## Upgrade an active older Sloar session

No fresh chat is required.

```text
Upgrade this active Sloar session to the latest stable release, preserve the current task state, and continue the work.
```

The upgrade path:

```text
re-resolve repository identity
-> inspect installed version
-> resolve stable release
-> back up old Sloar core
-> upgrade Sloar core
-> install newly bundled companions only when missing
-> preserve existing divergent/customized companions
-> refresh only Sloar's owned AGENTS marker when needed
-> verify + bridge current task into latest checkpoint/turn model
-> continue original work
```

Local fallback:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

The previous Sloar core is backed up under `.git/sloar-upgrade-backups/`. Product source and unrelated repository guidance are not reset.

Exact contract: [`.agents/skills/sloar-chat-coder/references/upgrading.md`](.agents/skills/sloar-chat-coder/references/upgrading.md)

## Non-terminating chat turns

Sloar distinguishes two different failure modes.

### Agent self-extension

A turn can stay active because the agent recursively creates another check or fix whenever a required gate remains red.

For one unchanged failure fingerprint, the default corrective cycle is bounded:

```text
diagnose once from concrete evidence
-> at most one corrective change for that diagnosis
-> re-run affected verification once
```

If the same fingerprint remains, terminalize as `PARTIAL`, `BLOCKED`, or `FAILED` and return the result. `ULW`, `finish it`, or similar autonomous instructions never authorize infinite retry/search/wait/poll loops.

Contract: [`.agents/skills/sloar-chat-coder/references/turn-terminalization.md`](.agents/skills/sloar-chat-coder/references/turn-terminalization.md)

### Host/runtime stall

Sloar cannot force the ChatGPT/app/server spinner to finish or cancel server-side generation. Instead interruption-prone work can separate engineering terminality from response delivery:

```text
BEGIN_TURN -> ACTIVE -> bounded PROGRESS -> TERMINALIZE -> visible final response
```

- terminal turn -> `TERMINAL_REPLAY_AVAILABLE`
- unterminated active turn -> `ACTIVE_OR_INTERRUPTED`
- explicit fresh-chat takeover -> increment fencing epoch
- stale old session -> rejected at the next guarded durable write

User guide: [docs/INTERRUPTED_TURNS.md](docs/INTERRUPTED_TURNS.md)

Contract: [`.agents/skills/sloar-chat-coder/references/operational-continuity.md`](.agents/skills/sloar-chat-coder/references/operational-continuity.md)

## Fresh-chat rollover

Request a handoff naturally. When authorized, durable rollover metadata lives on the sidecar branch rather than a product branch:

```text
branch: sloar/rollover-state

.sloar/rollover/
  latest.json
  checkpoints/
    <checkpoint-id>.json
```

A fresh chat normally receives one control sentence:

```text
Resume the latest Sloar session for OWNER/REPO.
```

The fresh chat revalidates current repository truth before trusting checkpoint state. Remote-only sessions keep unobservable local working-tree state as `unobserved` instead of pretending it is clean. Control language and user-facing `response_language` are separate.

Contract: [`.agents/skills/sloar-chat-coder/references/chat-native-continuity.md`](.agents/skills/sloar-chat-coder/references/chat-native-continuity.md)

## Forge resilience

Git, forge APIs, Actions/CI, and identity/policy are separate failure domains.

```text
LOCAL_READY + REMOTE_DEGRADED
-> continue local IMPLEMENT/VERIFY
-> defer publication

LOCAL_READY + REMOTE_PARTIAL
-> preserve verified tree
-> change capability / identity / approval / policy path
-> do not repeat the same forbidden operation
```

Network-free local state:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py .
```

One bounded remote probe:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py . --probe
```

Classify an already-observed failure without another network request:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py \
  --classify-file /path/to/error.log --json
```

Guide: [docs/FORGE_RESILIENCE.md](docs/FORGE_RESILIENCE.md)

## Core model

Repository lifecycle:

```text
ONBOARD? -> RECOVER -> IDENTIFY -> MATERIALIZE -> BRANCH -> IMPLEMENT -> VERIFY -> PUBLISH -> REMOTE_VERIFY -> CLEANUP
```

Core invariants:

```text
repository identity = HEAD SHA + tree SHA + observable working-tree state
same failure + same inputs = change strategy
no evidence -> no completion claim
revalidate mutable remote state immediately before publication
```

When evidence exposes them, repository, verification, and serving runtime anchors may be tracked separately.

Sloar does not choose the product's framework, package manager, database, UI library, deployment provider, or visual style. The target repository defines its engineering and design method.

## Docs

- First run: [docs/FIRST_RUN.md](docs/FIRST_RUN.md)
- Connections/capabilities: [docs/CONNECTIONS.md](docs/CONNECTIONS.md)
- ChatGPT Plugin/App/Skill: [docs/CHATGPT_PLUGINS.md](docs/CHATGPT_PLUGINS.md)
- Forge resilience: [docs/FORGE_RESILIENCE.md](docs/FORGE_RESILIENCE.md)
- Interrupted turns: [docs/INTERRUPTED_TURNS.md](docs/INTERRUPTED_TURNS.md)
- General web design companion: [`.agents/skills/web-design-guidance/SKILL.md`](.agents/skills/web-design-guidance/SKILL.md)
- Apple-specific companion: [`.agents/skills/apple-web-design/SKILL.md`](.agents/skills/apple-web-design/SKILL.md)
- Korean README: [README.ko.md](README.ko.md)

## License

MIT. See [LICENSE](LICENSE).
