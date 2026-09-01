# Changelog

## Unreleased


## 0.8.2 - 2026-09-02

Android engineering and distribution release.

- Added `references/android-engineering.md` as a durable Android production playbook covering existing-project discovery, empty-repository bootstrap, Gradle/build commands, Compose/UI resilience, permissions/security, signing identity, update compatibility, APK/AAB distribution, and CI/CD evidence.
- Added `scripts/android-preflight.py` to classify repositories as `EXISTING_ANDROID`, `PARTIAL_ANDROID`, or `EMPTY_OR_NON_ANDROID`, discover package/SDK/build facts, and surface static review hints for high-rate sensors, tight timers, unbounded loops, wake locks, listener lifecycle, continuous networking, and hot-path logging.
- Separated Android compile/test/artifact success from `UI`, `DEVICE_RUNTIME`, `PERF`, `THERMAL`, and `POWER` evidence so a green CI build cannot be reported as proof of real-device heat, battery, touch, sensor, or OEM behavior.
- Added real-device performance/thermal/power verification guidance, including bounded soak-test expectations for continuous sensor, game, navigation, camera, Bluetooth, media, and network workloads.
- Wired Android activation into the Sloar engineering lifecycle and core Skill so installed repositories use their local bundled Android guidance instead of depending on the canonical Sloar repository for ordinary Android work.
- Added regression coverage proving Android guidance and preflight tooling ship in fresh Sloar installations and remain connected to the core workflow.
- Added validated release automation: release commits publish only after `Validate Sloar` succeeds, with an annotated version tag and GitHub Release tied to the exact source commit.

## 0.8.1 - 2026-08-30

Automatic update-awareness patch.

- Added bounded `UPDATE_AWARENESS` at the first Sloar repository turn in a chat and after intentional fresh-chat resume/takeover when the canonical stable source is reachable.
- Separated automatic version discovery from upgrade authorization: current installs stay silent, newer stable releases produce one compact notice, and no Sloar write occurs until the user explicitly approves or independently requests an upgrade.
- Made stable-version lookup failure non-blocking. Unavailable, degraded, rate-limited, or unauthorized lookup becomes update status `unknown`; Sloar continues ordinary repository work and does not poll indefinitely.
- Preserved the existing automated `UPGRADE_SESSION` after approval, including repository identity revalidation, Git-metadata backup, Sloar-owned file replacement, known-official companion migration, custom companion preservation, validation, checkpoint bridging, and continuation of the active task.
- Extended the local First Run Wizard with deterministic `--stable-version` comparison while keeping the Wizard network-free. It now reports `current`, `update_available`, `ahead`, `unknown`, or `not_installed` and never treats update availability as write authorization.
- Added regression and CI coverage proving current stable is silent, a newer stable asks for approval, ahead-of-stable installs are not downgraded, and unavailable stable resolution remains non-blocking.
- Updated Korean/English README and user guides plus the readiness example so the public UX clearly states: update checking is automatic when possible; installation is automated only after user approval.

## 0.8.0 - 2026-08-30

Adaptive design discovery and Anti-AI-Slop release.

- Reworked substantial web-design discovery around `KNOWN / INFERRED / UNKNOWN` facts instead of a fixed taste questionnaire.
- Added an adaptive clarification budget: ask only questions whose answers have meaningful decision impact, uncertainty, rework cost, and low reversibility; well-specified work may ask zero questions while very vague work may ask a compact batch of several high-value questions.
- Required design questions to use ordinary experiential language rather than expecting users to know terms such as neumorphism, glassmorphism, brutalism, direct manipulation, or spring motion. `You decide` / `알아서` stops optional questioning and delegates the choice to product/repository evidence.
- Added 2-3 candidate-direction guidance when recognition is easier than description, while prohibiting superficial color-only A/B/C choices.
- Added a multi-axis Design DNA taxonomy separating design philosophy/tone, material language, composition, interaction language, motion posture, density, typography, and color. The taxonomy covers functional/minimal/maximal/editorial/brutalist/refined/playful/technical/organic/retro/futuristic directions; flat/tactile/neumorphic/glass/clay/paper/hard-surface materials; grid/asymmetric/bento/spatial compositions; and microinteractive/direct-manipulation/context-aware/gesture/scroll interaction modes.
- Added explicit style-soup prevention: a style label is not a feature checklist and multiple fashionable influences must not be combined without one coherent product reason.
- Added `anti-ai-slop.md` as an evidence-aware design audit rather than an authorship detector. Findings are classified as `P0 / P1 / P2` and `CODE-CERTAIN / RENDER-CERTAIN / INFERRED` so source heuristics cannot masquerade as rendered visual evidence.
- Cataloged common unchosen generated/default tells across palette/material, typography, layout/information architecture, component styling fingerprints, interaction/state, motion, copy/product evidence, imagery/fake data, and second-order defaults.
- Added remedies for high-signal patterns such as generic purple/indigo AI palettes, gradient headlines, decorative glass/glow, default centered SaaS hero bundles, equal feature cards, unjustified bento, untouched component-library demos, pill/rounded-card repetition, fake social proof/charts/data, generic `Transform/Elevate/Unlock` copy, universal hover/scroll animation, and happy-path-only states.
- Added a second-order-default check so de-slopping cannot simply become another universal rescue style such as always swapping Inter for the same trendy font or purple glass for the same warm-paper/brutalist aesthetic.
- Strengthened rendered visual re-audit around five questions: are major choices justified, coherent, product-specific, state/responsive complete, and not merely another default? Lack of rendered capability remains an evidence limitation, not a reason to keep the turn open indefinitely.
- Expanded source notes with public anti-slop/design-agent projects including `rwcod/anti-ai-slop-ui`, `funboy322/avoid-ai-design`, and `imMamdouhaboammar/unslop-preflight`, while preserving independent Sloar wording and no external runtime dependency.
- Improved `--upgrade` safety for the bundled design companion. Sloar 0.8 records the exact official 0.7.0 file fingerprint, automatically migrates only an untouched known bundle after backing it up under Git metadata, and preserves modified/custom/unrecognized companion content. A lower version number alone never authorizes replacement.
- Added regression coverage for exact official 0.7 -> 0.8 companion migration, modified-0.7 preservation, adaptive question budgeting, multi-axis taxonomy, Anti-AI-Slop severity/evidence contracts, installer/wizard readiness, and existing continuity/terminalization behavior.

## 0.7.0 - 2026-08-30

Repository-aware web design guidance release.

- Added the bundled `web-design-guidance` companion for substantial user-facing web UI work while preserving Sloar's separation between repository engineering continuity and project-specific design decisions.
- Defined design precedence as explicit user direction > repository design/brand rules > shipped UI/tokens/components > bundled fallback guidance, preventing generic style catalogs from overriding an established product language.
- Added compact design discovery and a working `Design Read` covering surface type, primary user job, visual tone, density, existing system, one intentional signature decision, and responsive/interaction risks.
- Added fallback recipes for product applications, dashboards, landing pages, auth/onboarding, settings, content/docs, and commerce without turning them into rigid templates.
- Added contextual anti-generic-generated-UI heuristics for repetitive split heroes, generic AI gradients, gratuitous bento/card layouts, decorative glass, fake charts, meaningless floating effects, and one-style-fits-all component rhythm; these are decision checks, not absolute style bans.
- Added text/responsive resilience, interactive state, accessibility, motion, and visual-evidence contracts. Build/compile/DOM checks no longer count as proof of visual correctness when rendered browser/screenshot evidence is available.
- Added a bounded visual-verification policy that can return `PARTIAL` when rendered evidence is unavailable or blocked rather than keeping the chat turn open indefinitely.
- Generalized useful structures from the MIT-licensed `nextlevelbuilder/ui-ux-pro-max-skill`, `superdesigndev/superdesign-skill`, and `educlopez/ui-craft` projects without vendoring or requiring them at runtime; source notes are recorded in the companion `NOTICE.md`.
- Kept the existing `apple-web-design` companion as a specialized opt-in refinement for explicitly Apple-like interaction/material requests rather than making Apple styling the default web language.
- Updated the installer so fresh installs bundle both general and specialized design companions. `--upgrade` installs newly missing bundled companions, preserves divergent/customized existing companions, and refreshes only Sloar's owned `AGENTS.md` marker block.
- Added upgrade and contract regression tests plus First Run Wizard/CI coverage for design companion readiness and activation safety.

## 0.6.1 - 2026-08-30

Bounded turn terminalization patch.

- Distinguished host/runtime stalls from agent self-extension where a RED or pending gate causes recursive `one more check` / `one more fix` work and the visible response never reaches a terminal report.
- Added `references/turn-terminalization.md` with a default bounded corrective cycle for one unchanged failure fingerprint: diagnose from concrete evidence, make at most one corrective change for that diagnosis, then re-run the affected verification once.
- Required `PARTIAL`, `BLOCKED`, or `FAILED` terminalization when a required gate remains RED, pending, or externally blocked after its allowed bounded cycle instead of leaving the turn indefinitely ACTIVE.
- Added explicit anti-rabbit-hole rules for optional follow-up scope, long-running CI/external waits, recursive polling, and autonomous/ULW-style requests.
- Clarified that `ULW`, `finish it`, and similar autonomous instructions permit deeper work but never authorize infinite retry, search, wait, or polling loops.
- Added regression tests that lock the terminalization contract and installer/CI checks that ensure the new reference ships with Sloar.
- Updated the First Run Wizard continuity report to expose bounded turn terminalization separately from host-level stuck-response recovery.

## 0.6.0 - 2026-08-30

Operational continuity release.

- Added durable interrupted-turn recovery for long repository tasks when a chat host stalls or remains visibly "answering" without delivering a final response.
- Explicitly separates engineering terminality from response-delivery terminality; Sloar does not claim to control the host spinner, cancel server-side generation, or revive a stuck host process.
- Added `scripts/turn-state.py` with ACTIVE/progress/terminal turn snapshots, terminal replay, explicit user-authorized takeover, monotonic fencing epochs, and pre-write fence checks.
- Added `ACTIVE_OR_INTERRUPTED` and `TERMINAL_REPLAY_AVAILABLE` recovery states without time-based automatic takeover.
- Added a stale-session fencing contract so an old apparently-stuck chat can be rejected on later guarded writes after a fresh chat has taken over; already-in-flight writes remain outside that guarantee.
- Added repository/verification/runtime anchors for projects where current HEAD, last verified product state, and serving production state legitimately differ.
- Added hot-state vs cold-history guidance for long-lived repositories while preserving repository-owned current-status/history/ADR conventions instead of imposing Sloar-specific project docs.
- Strengthened the evidence ledger so evidence type/scope must match the completion claim; compile, rendered UI, live integration, merge/deploy, and production-health evidence are not interchangeable.
- Added a compact change-boundary contract: `changed / preserved / deliberately_not_changed / limitations`.
- Added durable failed-experiment guidance to prevent repeated structural mistakes without promoting speculative diagnoses into facts.
- Added English/Korean stuck-response recovery guides and CI coverage for terminal snapshots, repository movement, explicit takeover, stale-fence rejection, anchors, and no-timeout semantics.

## 0.5.1 - 2026-08-30

Active-session upgrade release.

- Added `UPGRADE_SESSION` so a repository already using an older Sloar release can upgrade without starting a fresh chat or reconstructing the current task.
- Added `references/upgrading.md` with explicit upgrade entry/exit conditions, publication/revalidation requirements, and the bridge from an older active session into the 0.5+ rollover checkpoint model.
- Added `install.py --upgrade` as the recommended local upgrade fallback. It upgrades only `sloar-chat-coder`, leaves unrelated companion skills alone, refuses downgrades and ambiguous same-version replacements, and preserves the previous installed skill under `.git/sloar-upgrade-backups/` before replacement.
- Added regression tests proving product files and companion skills are preserved, old Sloar files are recoverable from the Git metadata backup, same-version divergence is not silently overwritten, and downgrades are rejected.
- Added a beginner-facing Korean quick path for upgrading an active 0.4.x session with one natural-language request and continuing the same task.

## 0.5.0 - 2026-08-30

Chat-native continuity release.

- Added explicit `BOOTSTRAP_SESSION -> NORMAL_WORK -> PREPARE_ROLLOVER -> RESUME_SESSION` continuity semantics for first-use and fresh-chat recovery.
- Added capability-aware first-use bootstrap so a user can begin from a repository URL when the current session has an authorized durable path, while keeping the local installer/wizard as fallback rather than mandatory ceremony.
- Added the preferred `sloar/rollover-state` sidecar branch for durable cross-chat checkpoint transport without polluting product branches with runtime metadata.
- Added compact rollover state for goal/completed/active/pending/decisions/evidence/blockers/next action and user-facing `response_language`.
- Added partial identity observability: remote-only sessions can mark working-tree state as unobserved instead of coercing unknown state to clean/dirty.
- Defined `EXACT` as no contradiction among mutually observable identity fields and `RECONCILE_REQUIRED` when an observable identity field moved.
- Added response-language continuity that separates English control/protocol text from the established user-facing response language.
- Added `PRE_RESPONSE_READ_BLOCKED` for hosts that require visible output before durable checkpoint reads; the contract forbids unsupported first-response language claims and unchanged retry loops under that host condition.
- Added `scripts/session-rollover.py`, a transport-agnostic local checkpoint/capsule helper that defaults state to `.git/sloar-rollover/` so handoff generation does not dirty the product worktree.
- Added regression coverage for local/remote identity comparison, repository movement, pointer/checkpoint language metadata, legacy checkpoints, compact capsules, and the host capability boundary.
- Updated CI to run the chat-native continuity suite and verify the new helper/reference are installed with the Skill.
- Added the optional `apple-web-design` companion skill, adapted from Emil Kowalski's MIT-licensed `apple-design` skill with upstream attribution preserved.
- Distilled Apple-style web interaction guidance into testable contracts for immediate feedback, 1:1 direct manipulation, presentation-state interruption, velocity projection, rubber-banding, restrained materials, typography, and accessibility.
- Updated the installer to bundle the companion without making it a default engineering method; target repository guidance remains authoritative.
- Added installer idempotency across all bundled skills while ignoring generated Python cache files.

## 0.4.0 - 2026-08-21

Forge resilience release.

- Added an explicit forge overlay separating local Git readiness from hosted platform health and operation-specific capability.
- Added `LOCAL_READY`, `REMOTE_HEALTHY`, `REMOTE_PARTIAL`, `REMOTE_DEGRADED`, `PUBLICATION_BLOCKED`, and `BLOCKED` semantics.
- Added `forge-health.py` with a network-free default and a single bounded `--probe` mode; it never creates retry loops.
- Added deterministic `--classify-file` / `--classify-error` handling for already-observed forge failures without making a network request.
- Added explicit classification for GitHub workflow permission mismatch, integration permission denial, CI approval/`action_required`, branch policy, non-fast-forward/stale remote state, 429, 5xx, DNS, and timeout failures.
- Failure classification returns a normalized class/layer/retry strategy/next action and SHA-256 fingerprint without echoing the raw error text.
- Added guidance for continuing local IMPLEMENT/VERIFY work while GitHub/GitLab/CI/API layers are degraded or partially authorized, without claiming publication success.
- Added a rule that correct verified product source must not be rewritten merely because the publishing identity lacks a specific permission.
- Added forge-layer failure fingerprints and retry-storm prevention rules; permission/policy failures require changed capability/policy evidence before retry.
- Added outage/capability checkpoints, optional mirror safeguards, and mandatory remote-base revalidation after recovery, approval, or delayed publication.
- Added a repository-aware Connection Advisor in the First Run Wizard for GitHub, Vercel, Supabase, Netlify, and OpenAI Platform.
- Added English/Korean connection guides that keep authentication user-controlled, recommend least-privilege scopes, and never treat repository detection as proof of an installed/authorized ChatGPT connection.
- Added explicit ref-cleanup capability handling: missing delete-ref tools are `REMOTE_PARTIAL`, completed publication/verification stays intact, and only `CLEANUP` is deferred as `REF_DELETE_UNAVAILABLE`.
- Added non-mutating `ref-cleanup.py` to prevent unsafe deletion substitutes such as moving a branch ref to another commit.
- Kept mirrors opt-in and prohibited silently publishing private source to a new forge merely because the primary provider is unavailable or a permission is missing.
- Updated English/Korean README and Forge Resilience guides so first-time users can discover the 0.4 workflow directly.

## 0.3.0 - 2026-08-20

Beginner First Run Wizard release.

- Added `wizard.py` with a compact human view and full JSON readiness report.
- Added a stable readiness capsule contract: Repository, Execution, GitHub read/write, CI/browser, and one next action.
- Upgraded `doctor.py` to schema 2 with origin and safe `gh auth` status while keeping ChatGPT account/plugin state explicitly unknown locally.
- Added dedicated English/Korean ChatGPT Plugin/App/Skill guides based on the current Plugin Directory model.
- Added zero-to-first-run clone/install/wizard commands so new users do not need prior Agent Skills knowledge.
- Clarified that Sloar is currently an Agent Skill repository and does not claim a Plugin Directory listing.
- Expanded CI to verify wizard behavior and the stricter local-vs-hosted capability boundary.

## 0.2.0 - 2026-08-20

First-run onboarding release.

- Added an ONBOARD capability-discovery pre-state for unknown/new environments.
- Added explicit ChatGPT Plugin vs App vs Skill guidance and GitHub connection boundaries.
- Added an idempotent installer for copying Sloar into a target repository and wiring `AGENTS.md`.
- Added a local `doctor.py` capability/worktree diagnostic with JSON output.
- Added English/Korean first-run guides and ready-to-paste starter prompts.
- Expanded validation to test installer idempotency and doctor output.
- Kept hosted integrations optional: missing GitHub app access degrades capability instead of falsely blocking local work.

## 0.1.0 - 2026-08-20

Initial public release.

- Added explicit repository-task state machine.
- Added repository identity contract using commit, tree, and working-tree state.
- Added six-level capability ladder.
- Added failure fingerprint and bounded retry policy.
- Added evidence ledger and claim-bound reporting rules.
- Added optimistic concurrency publication guard.
- Added bounded Actions mission contract.
- Added recovery checkpoint format and helper scripts.