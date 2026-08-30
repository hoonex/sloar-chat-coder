# Sloar Chat Coder

Reliable repository engineering across disposable AI coding sessions.

Sloar Chat Coder is an Agent Skill for chat-based repository work where sandboxes can disappear, repository state can move concurrently, connected tools can fail, long turns can self-extend, and the host itself can stall before delivering a final response.

Current version: **0.8.0**

> Durable repository truth over reconstructed conversation memory. Evidence before completion claims.

## 10-second usage

```text
First use -> repository URL + "Use Sloar for this repository"
Normal work -> just describe the repository task
Vague web UI request -> ask only the high-value questions justified by ambiguity
No design vocabulary -> translate ordinary language into multi-axis Design DNA
"You decide" -> stop optional design questions and choose from product/repository evidence
After material UI work -> responsive/state/visual + Anti-AI-Slop re-audit
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

The installer adds or refreshes only Sloar's owned marker block in `AGENTS.md`; unrelated repository guidance remains authoritative.

## 0.8: adaptive web-design discovery

The bundled general web-design companion assumes users often know the experience they want without knowing terms such as `neumorphism`, `glassmorphism`, `brutalism`, `direct manipulation`, or `spring motion`.

For a vague request such as:

```text
Build a school timetable web app.
```

it should neither jump straight to a generic dashboard nor force a fixed questionnaire.

It first classifies consequential design/product facts as:

```text
KNOWN     explicitly established
INFERRED  reasonably supported by repository/product evidence
UNKNOWN   materially different directions remain plausible
```

Questions are asked only when the answer can change the design substantially and guessing wrong would be costly to reverse.

```text
question value
≈ decision impact × uncertainty × rework cost
  ÷ reversibility
```

This is a reasoning heuristic, not a numeric API.

Soft defaults for clarification depth:

```text
very clear request -> 0 questions
one consequential fork -> 0-1 question
moderate ambiguity -> 1-3 questions
high ambiguity -> 2-4 questions
"make a cool website" -> roughly 3-5 high-value questions, preferably in one batch
```

The agent asks in language ordinary users can answer:

```text
Is fast information scanning more important, or is a strong first impression more important?
Should it feel calm/refined, friendly/soft, or bold/experimental?
Should controls feel tactile and physically responsive, or should motion stay minimal?
Is mobile the primary environment, or should desktop be equally first-class?
```

It normally does not ask users to choose jargon such as `neumorphism vs glassmorphism` unless they already use those terms.

If the user says `you decide`, optional clarification stops. The agent chooses from product/repository evidence and proceeds.

When recognition is easier than description, it may offer 2-3 materially different candidate directions such as `Calm Utility`, `Soft Tactile`, and `Editorial Bold` instead of asking many token-level questions.

Contract: [adaptive-design-discovery.md](.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)

## Design is multi-axis, not one style name

`Minimalism`, `Glassmorphism`, `Bento`, `Interactive`, and `Spring` describe different design axes.

Sloar 0.8 can translate intent into a compact **Design DNA**:

```text
philosophy / tone
material language
composition
interaction language
motion posture
density
typography / color stance
```

Example:

```text
philosophy: soft minimal + functional
material: restrained translucency
composition: asymmetric compact grid
interaction: tactile + context-aware
motion: short spring
density: compact-balanced
```

The taxonomy covers useful vocabularies such as:

```text
philosophy
-> Functional, Minimalism, Maximalism, Editorial,
   Brutalism/Neo-brutalism, Refined/Luxury,
   Playful, Industrial/Technical, Organic, Retro, Futuristic/Spatial

material
-> Flat, Skeuomorphic/Tactile, Soft UI/Neumorphism,
   Glassmorphism/Translucent, Clay/Soft-3D, Paper, Hard-surface

composition
-> Grid, Asymmetric, Split, Full-bleed, Command center,
   Editorial, Bento, Timeline, Spatial layers, Single-focus

interaction
-> Static, Microinteractive, Tactile, Direct manipulation,
   Gesture-driven, Scroll-driven, Context-aware/State-driven, Spatial

motion
-> None, Restrained, Spring, Physics-based,
   Morphing, Cinematic, Parallax/Depth
```

The goal is not to combine everything. Choose only the axes that serve the same product intent and avoid style soup.

Taxonomy: [design-taxonomy.md](.agents/skills/web-design-guidance/references/design-taxonomy.md)

## 0.8: Anti-AI-Slop design audit

`Looks AI-generated` is not proof that AI authored a UI. Sloar's Anti-AI-Slop pass audits whether unrelated products are converging on the same **unchosen generated/default patterns**.

The governing principle is:

> Replace reflexes with decisions.

Purple, Inter, glass, bento, Lucide, or centered composition can all be correct when product/brand/function evidence justifies them.

### Tell categories

```text
1. Palette / Material
2. Typography
3. Layout / Information Architecture
4. Components / Styling fingerprints
5. Interaction / State
6. Motion
7. Copy / Product evidence
8. Imagery / Fake data
9. Second-order defaults
```

Representative tells include:

- unchosen purple/indigo AI palettes, purple-to-blue gradients, gradient headlines;
- decorative glass, neon glow, aurora/blob effects without a spatial/product reason;
- untouched Inter/Geist/Roboto/system type as the entire product identity;
- replacing those with the same small cluster of `tasteful` fonts on every project;
- the `pill badge -> centered H1 -> generic subtitle -> two CTAs -> three equal feature cards` SaaS bundle;
- bento grids unrelated to information hierarchy;
- `rounded-2xl shadow-lg`-style equal cards everywhere;
- identical icons inside tinted rounded-square chips;
- untouched shadcn/MUI/Bootstrap-style demo appearance;
- fake user counts, uptime, testimonials, logos, charts, feeds, or activity data;
- vague `Transform / Elevate / Unlock / Supercharge` product copy;
- hover-lift on every card and scroll-reveal on every section;
- happy-path screenshots with no real loading/empty/error/focus/pressed/selected states;
- **second-order defaults** where the agent always uses the same rescue aesthetic after removing the first cliché.

### P0 / P1 / P2 and evidence confidence

Findings may be classified as:

```text
P0 — high-signal generic/generated tell visible to ordinary users
P1 — designer/developer-level template smell
P2 — craft/polish gap
```

Evidence is kept separate:

```text
CODE-CERTAIN
RENDER-CERTAIN
INFERRED
```

A literal class/import and a rendered judgment about palette balance, hierarchy, spacing, or motion are not the same evidence type.

### Fix the cause, not the token

Weak de-slop:

```text
indigo -> teal
Inter -> Fraunces
rounded-2xl -> rounded-md
```

Stronger correction:

```text
re-establish product purpose + user + Design DNA
-> align composition/type/color/material/interaction with that direction
-> remove high-signal defaults that conflict with it
-> inspect the rendered result again
```

An `anti-AI style` that becomes another universal template is also a failure.

Catalog and remedies: [anti-ai-slop.md](.agents/skills/web-design-guidance/references/anti-ai-slop.md)

## Visual evidence

For web UI:

```text
build/compile green != visually correct
DOM geometry green != balanced hierarchy
anti-slop lint green != product-specific design
CSS property present != readable rendered material
```

When browser/screenshot capability exists, visual-success claims should be supported by rendered evidence appropriate to the changed surface and responsive/state risks. Material P0/P1 anti-slop findings should also be re-audited on the rendered result.

If rendered evidence is unavailable or blocked, report that scope as unverified or `PARTIAL` rather than keeping the chat turn alive indefinitely. Sloar's bounded terminalization rules still apply.

## Apple-specific refinement

The existing `apple-web-design` companion remains bundled, but it is not the default web language. Use it only when the user or repository explicitly wants Apple-like direct manipulation, interruptible motion, velocity-aware settling, or functional translucent materials. General repository-aware adaptive design discovery still comes first.

## Public inspirations

The 0.8 design guidance independently generalizes useful structures observed in public design-agent/anti-slop projects without vendoring or requiring them at runtime:

- `nextlevelbuilder/ui-ux-pro-max-skill` — product-aware style/color/type and anti-pattern structure;
- `superdesigndev/superdesign-skill` — repository-aware design-system memory;
- `educlopez/ui-craft` — surface recipes, acceptance bars and rendered self-review;
- `rwcod/anti-ai-slop-ui` — product-specific direction plus generated/default UI audits;
- `funboy322/avoid-ai-design` — P0/P1/P2, code-vs-render evidence and second-order defaults;
- `imMamdouhaboammar/unslop-preflight` — vague-request preflight and specification-readiness thinking.

Original repositories and licenses remain authoritative for their work. See `.agents/skills/web-design-guidance/NOTICE.md` for source notes.

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
-> back up + upgrade Sloar core
-> install missing bundled companions
-> exact-known official older companion: fingerprint -> backup -> migrate
-> modified/custom companion: preserve
-> refresh only Sloar's owned AGENTS marker when needed
-> verify + bridge current task into latest checkpoint/turn model
-> continue original work
```

For 0.8 specifically, Sloar knows the exact official `web-design-guidance 0.7.0` fingerprint:

```text
untouched official 0.7.0 -> safely migrate to 0.8.0
modified 0.7.0 -> preserve customization
```

A lower version number alone never authorizes companion replacement.

Local fallback:

```bash
python3 .agents/skills/sloar-chat-coder/scripts/install.py \
  --target /path/to/project \
  --upgrade
```

The previous core and known companions migrated automatically are backed up under `.git/sloar-upgrade-backups/`. Product source and unrelated repository guidance are not reset.

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
- Adaptive design discovery: [adaptive-design-discovery.md](.agents/skills/web-design-guidance/references/adaptive-design-discovery.md)
- Design taxonomy: [design-taxonomy.md](.agents/skills/web-design-guidance/references/design-taxonomy.md)
- Anti-AI-Slop: [anti-ai-slop.md](.agents/skills/web-design-guidance/references/anti-ai-slop.md)
- Apple-specific companion: [`.agents/skills/apple-web-design/SKILL.md`](.agents/skills/apple-web-design/SKILL.md)
- Korean README: [README.ko.md](README.ko.md)

## License

MIT. See [LICENSE](LICENSE).
