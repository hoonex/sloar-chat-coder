# Changelog

## Unreleased

No unreleased changes yet.

## 0.10.3 - 2026-09-14

Evidence-independence and domain-grounding patch.

- Added a risk-adaptive evidence-independence contract so implementation and verification that inherit the same unproven premise are treated as self-consistency evidence, not automatically as independent correctness proof.
- Added a bounded critical-assumption ledger for consequential premises whose falsity would change architecture, implementation, acceptance, safety, or performance conclusions, with `CONFIRMED / SUPPORTED / UNKNOWN` states when useful.
- Added differentiated falsifiers for common-provenance risk: authoritative contracts, conformance vectors/corpora, independently implemented references, domain-derived properties/invariants, and runtime/end-to-end observations.
- Added conditional domain grounding for standards, protocols, mathematics, hardware, compatibility, and other external contracts without turning every repository task into broad research ceremony.
- Added a dependency-ownership prior: prefer mature dependencies when they already own hard correctness/compatibility work and the product does not need that layer, while requiring enough boundary understanding to detect contract violations.
- Added regression tests and preflight presence checks for the new evidence-independence contract.
- Bumped Sloar core, First Run Wizard, readiness examples, and stable documentation to `0.10.3`.

## 0.10.2 - 2026-09-11

Full-system audit hardening patch.

- Fenced privileged `workflow_run` release publication to successful same-repository pushes on `main`, added serialized release execution, and pinned checkout to the exact `actions/checkout` v7.0.1 commit.
- Closed the release TOCTOU window with an atomic tag + no-op `main` publication guarded by `--force-with-lease`, so a release tag is rejected if `main` moves after validation instead of publishing stale source.
- Added existing-tag collision checks, exact tag-target postconditions, and idempotent GitHub Release verification so release success is tied to the verified source commit.
- Repaired companion upgrades for the exact official Sloar v0.9.1 `web-design-guidance` and unversioned `apple-web-design` bundles, including the historical equal-version `0.8.0` design bundle, while continuing to preserve any modified/custom companion bytes.
- Made `web-architecture-map.py` framework-scoped and monorepo-aware: route conventions now use the nearest declared `package.json`, Next.js routes no longer consume `.vue`/`.astro` files, and Nuxt/Astro/SvelteKit/Remix route candidates retain package-scope evidence.
- Added content-aware dirty working-tree fingerprints so distinct tracked or untracked bytes cannot reuse the same architecture snapshot identity merely because both states are labeled `dirty`.
- Expanded architecture and upgrade regression coverage for nested Next.js apps, Nuxt/Astro routing, dirty-byte invalidation, exact v0.9.1 companion migration, custom companion preservation, and release-publication fencing.
- Removed the preflight awk warning, added rendered-UI evidence presence to self-test/CI, refreshed readiness examples, and pinned validation checkout to the exact current action commit.
- Bumped Sloar core and First Run Wizard metadata to `0.10.2`.

## 0.10.1 - 2026-09-11

Rendered UI evidence-closure patch.

- Added a dedicated rendered-UI evidence contract so compile, test, instrumentation, screenshot generation, and artifact upload success cannot be mistaken for visual acceptance.
- Added exact source/run/artifact identity requirements for rendered evidence and a pre-merge HEAD reconciliation rule so accepted screenshots cannot silently refer to stale source.
- Added native system-UI boundaries covering status-bar contrast, navigation/gesture insets, cutouts, portrait/landscape, constrained viewport states, IME overlap, and action reachability when those states affect acceptance.
- Added semantic-selector guidance for UI automation: accessibility/semantics nodes, test IDs, labels, or repository-defined selectors are preferred over hard-coded coordinates that become stale after inset, density, orientation, or layout changes.
- Added failure-layer classification that separates build/package, install/runner, selector/harness, product interaction/state, and rendered visual defects before product source is changed.
- Added regression coverage for the rendered UI evidence contract.
- Bumped Sloar core and First Run Wizard metadata to `0.10.1`.

## 0.10.0 - 2026-09-11

Architecture-aware web engineering and product-craft release.

- Added an evidence-backed **web architecture capsule** so an agent can orient itself from durable repository facts before reading broad source. The capsule keeps deterministic topology separate from semantic ownership and explicitly preserves `UNKNOWN` instead of filling gaps with framework-shaped guesses.
- Added `scripts/web-architecture-map.py`, a network-free topology scanner that anchors output to Git identity when observable and reports declared frameworks, routers, state/data systems, styling systems, package scripts, source roots, entrypoint candidates, convention-based route candidates, configuration files, and token/global-style candidates.
- Added evidence levels `DECLARED / OBSERVED / CONFIRMED / INFERRED / UNKNOWN` and source-anchor/invalidation rules so a fast architecture map remains a navigation cache rather than becoming stale authority over current code.
- Added progressive, task-specific source discovery: start from repository guidance and topology, then read only the route/data/state/component/style/effect owners needed by the requested change instead of scanning the entire site for every task.
- Added structural UI engineering rules that separate `VISUAL`, `BEHAVIOR`, `STRUCTURE`, `RESILIENCE`, and `HYGIENE` claims. A clean screenshot or green build no longer stands in for coherent ownership, effect lifecycle, CSS/token integrity, or obsolete-path cleanup.
- Added source-of-truth, component-boundary, state-machine, side-effect, CSS/design-system, dependency/abstraction, blast-radius, and superseded-code audits for AI-assisted UI work so new features integrate with existing owners instead of accumulating mirrored state, synchronization effects, near-copy components, duplicate request paths, and override stacks.
- Added an Apple-inspired product-craft contract focused on hidden complexity, learnable novelty, deliberate state transitions, restrained technological novelty, and a small delight budget without allowing polish to excuse weak accessibility, performance, or architecture.
- Added a ChatGPT/GitHub connector-native workflow and integrity hardening: exact repository identity, direct checkpoint publication, conflict-rejecting remote writes, local/sidecar/product-ref separation, content-aware dirty recovery, serialized turn-state mutation, and evaluator-integrity guards.
- Kept development evaluation distinct from promotion evidence: local/Codex adapters remain development tools, policy changes and category relabeling cannot silently alter a run, and regression/cost evidence remains bound to the exact comparison identity.
- Added regression coverage for the architecture scanner, including declared-vs-observed evidence, tracked-vs-untracked topology, route bounding, and installer/self-test presence.
- Bumped Sloar core and First Run Wizard metadata to `0.10.0`.

## 0.9.1 - 2026-09-08

Evaluation-driven development and publication-reliability patch.

- Added the development-only `sloar-evals` substrate so Sloar policy changes can be compared as stable vs candidate under the same suite/model/harness identity instead of being promoted from prose intuition alone. The runner preserves trajectory/artifact evidence and the scorer gates success, regressions, false completion, category-level losses, and efficiency metrics.
- Separated exposed `dev` iteration from promotion-quality evidence. Dev suites can guide experiments but cannot authorize promotion; holdout/production evidence remains the promotion boundary, with comparison fingerprints preventing silent model/harness/suite changes from masquerading as policy improvements.
- Added a real Codex CLI evaluation adapter and one-command A/B runner. Repository tasks execute in isolated worktrees, success/regression are derived from objective repository checks, false completion is compared against verifier evidence, and adapter crashes/timeouts/malformed results remain evaluation-infrastructure failures rather than model failures.
- Added deterministic public smoke cases whose seed patches are proven RED before agent execution, providing an end-to-end check of `policy -> agent -> repository mutation -> verifier -> result bundle` without pretending the exposed smoke suite is hidden capability evidence.
- Changed the default dev A/B reasoning effort to `medium` for faster iteration while keeping both sides of every comparison on the same effort and reserving explicit `high` runs for promotion-quality validation.
- Strengthened publication safety from a generic HEAD check into an explicit **publication mutation intent / mutation envelope**. Ref movement, file-content writes, PR metadata, workflow actions, and other remote mutation families are no longer interchangeable merely because similarly named connector recipients are available.
- Added a bounded Git-object publication transaction: build against an expected head, re-resolve immediately before ref movement, stop/reconcile on movement, prefer compare-and-swap / expected-old-SHA / lease semantics when available, and verify the exact published ref/commit/tree as a postcondition. Read-then-write paths without CAS are explicitly described as retaining a residual race rather than being called atomic.
- Added operational-incident handling for wrong tool/recipient or unintended remote mutations. Sloar must inspect the durable effect, repair current state with a bounded corrective change, and must not force-rewrite shared/public history merely to hide an accidental intermediate commit.
- Distinguished GitHub Actions concurrency cancellation from code failure. A cancelled push run may be superseded by an authoritative PR run only when exact source SHA and required checks match; unexplained cancellations, different SHAs, or missing required checks cannot be coerced into GREEN evidence.
- Added regression contracts covering publication mutation intent, operation-family fencing, ref postconditions, operational incidents, and concurrency-cancellation evidence.

## 0.9.0 - 2026-09-03

Reasoning kernel and semantic-boundary verification release.

- Replaced state-machine-first reasoning with a compact default kernel: `OBSERVE -> MODEL -> ACT -> PROVE -> RECONCILE`. Detailed lifecycle references remain available as conditional guardrails when continuity, publication, remote capability, or recovery risk actually requires them.
- Added `references/reasoning-kernel.md` to keep strong models focused on authoritative facts, semantic ownership, invariants, independent acceptance claims, coherent structural fixes, relevant evidence, and final durable reconciliation without turning every task into repository archaeology.
- Strengthened async/stateful verification around **semantic phases rather than convenient implementation labels**. Requirements such as `before callback starts` must be tested at the latest valid observable boundary when that edge can change correctness, including cases where resources are already reserved or callbacks/microtasks are scheduled but user code has not run yet.
- Added transition-adjacent race derivation, end-to-end fencing checks, late-finalizer/replacement ownership checks, retry safety plus liveness, cancellation ownership separation, and public observables such as Promise results, callback invocation counts, `AbortSignal`, resource/running counts, ordering, dedupe state, events, and remote side effects.
- Added evidence-economy rules: more tests are not automatically stronger evidence. A compact adversarial basis covering distinct semantic boundaries is preferred over many repetitions of the same comfortable phase, and compound requirements must be split when separate paths or observables can fail independently.
- Reworked `verification.md`, `state-machine.md`, and the core `SKILL.md` so phase-fit, latest-valid-boundary reasoning, and risk-adaptive process selection are entry-level behavior while connector-native access, continuity, forge resilience, publication fencing, Android engineering, and design guidance remain specialized expansions.
- Preserved and integrated the earlier connector-native repository mode so blocked ordinary Git transport does not force pointless clone retries or remote-execution escalation when an exact repository connector can complete the task faithfully.
- Added regression contracts for the reasoning kernel and semantic async boundary model, including guards against generalizing queued cancellation to all pre-invocation cancellation or final-state checks to Promise/callback correctness.
- Published Sloar `0.9.0` metadata and English/Korean documentation, and removed release-version hardcoding from tests, self-test logic, wizard validation, and CI so `VERSION` is the durable release source of truth.

## 0.8.3 - 2026-09-02

Ownership and evidence intelligence release.

- Added `references/ownership-evidence-closure.md` to make **ownership before workaround** and **acceptance claim -> evidence derivation** explicit core engineering behavior instead of narrow CSS/Android advice.
- Added compact `Engineering Closure` records plus `scripts/engineering-closure.py`; the helper validates caller-provided owner/claim/evidence/convergence data but never guesses source ownership or replaces repository-defined tests.
- Expanded source-of-truth discovery across CSS/DOM/JS/data/config/runtime boundaries, temporal/input/responsive/persistence evidence dimensions, production convergence (`SOURCE -> VERIFIED -> PACKAGED -> DEPLOYED -> SERVED -> CACHED -> FIRST_FRAME`), and feature/gate lifecycle (`active / dormant / retired`).
- Added concrete rules for hot-path complexity, hit-area/input modality, persisted-state semantics, dual-path/obsolete-route detection, and separated build/instrumentation evidence from real-device runtime/performance/thermal/power evidence.
- Added adversarial, fixture-backed regression coverage for authoritative-owner discovery, stale gate detection, mobile native/system UI evidence, rollout/deploy convergence, persistence, and Sloar self-audits.
- Added per-case holdout secrecy enforcement (`validate_case_secrecy`) in the evaluator runner so hidden success criteria cannot be copied into candidate-visible fixtures by accident.
- Updated `SKILL.md`, Android, rendered-UI, verification/evidence-ledger, README/README.ko, USER_GUIDE/USER_GUIDE.ko, and public dev eval cases to use the generalized closure model without displacing repository-specific engineering rules.
- Published Sloar `0.8.3`.

## 0.8.2 - 2026-09-01

Design intelligence + anti-slop patch.

- Added multi-axis `Design DNA` (philosophy/tone, material language, composition, interaction language, motion posture, density, typography/color stance) so ordinary user language can be translated into a coherent visual direction without forcing jargon or fixed style labels.
- Added adaptive design discovery: clear requests can proceed with zero clarification, moderate ambiguity gets only the highest-value questions, high ambiguity gets a compact batch, and `you decide`/`알아서` terminates optional questioning.
- Added design-system authority rules so an existing project system beats generic taste, with an explicit redesign exception only when the user actually requests a new direction.
- Added reference-research and critique guidance that treats the model's first design idea as a hypothesis, separates inspiration from copying, and uses visual reference research only when it can change the direction.
- Added identity/logo guidance so logos are kept, transformed, or generated according to product role instead of generic placeholder behavior.
- Added a contextual Anti-AI-Slop audit covering repetitive cards, pills/chips, glow, glass, excessive rounding, purple gradients, emoji-as-icon, default fonts, bento grids, exaggerated hero copy, decorative blobs, and ornamental dashboards without turning those patterns into blanket bans.
- Added embedded-material correctness guidance: glass/frosted/liquid surfaces must actually reveal or transform underlying visual information rather than sitting over empty flat backgrounds; readability and fallback behavior remain mandatory.
- Added concrete surface recipes for liquid/glass, clay/neumorphism, paper/editorial, dark/data, dimensional/canvas, and minimal/utility interfaces.
- Added explicit rendered browser evidence to the design completion contract; code review or CSS inspection alone cannot prove visual hierarchy, text resilience, responsiveness, material legibility, or anti-slop quality.
- Added a smaller Apple-specific companion skill for cases where Apple-like or Liquid Glass work is explicitly requested, focusing on material behavior, continuity, depth, controlled motion, and contrast/accessibility instead of generic imitation.
- Added validation tests for the new design guidance and pinned the validation workflow's checkout action by exact commit SHA.
- Updated README, Korean README, user guides, first-run docs, installer wiring, and source distribution metadata for the richer design workflow.
- Published Sloar `0.8.2`.

## 0.8.1 - 2026-09-01

Chat-native continuity patch.

- Added `references/chat-native-continuity.md` with exact connector-only repository identity, direct checkpoint publication, stale sidecar protection, runtime-free handoff, and fresh-chat revalidation rules.
- Added `references/async-evidence-closure.md` and generalized async/race reasoning beyond the original remote-store example: resource ownership, task ownership, stale/later completion, cancellation generations, dedupe lifetime, cleanup ownership, ordering, and ambiguous partial-failure semantics.
- Added `scripts/session-rollover.py`, a local helper for validating and summarizing checkpoint payloads without requiring GitHub access.
- Added `scripts/turn-state.py` and operational-continuity rules for `BEGIN_TURN -> ACTIVE -> PROGRESS* -> TERMINALIZE`, terminal replay, explicit-takeover fencing, local lock/content-aware save behavior, and best-effort separation between engineering terminality and host response delivery.
- Added bounded turn terminalization: one corrective cycle per unchanged failure fingerprint by default, anti-rabbit-hole stop rules, stale-gate handling, and explicit `COMPLETED / PARTIAL / BLOCKED / FAILED` turn semantics.
- Added automatic update awareness on the first Sloar repository turn and fresh-chat resume/takeover, with one compact notice when a newer stable exists and explicit user authorization before any upgrade write.
- Added `scripts/install.py --upgrade` to back up the old core under Git metadata, replace only Sloar-owned core files, safely upgrade known official older web-design bundles, preserve customized companions, reject downgrade/same-version divergence, and continue the current task instead of restarting it.
- Replaced sample token placeholders in `eval/README.md` with `<token>` so automated secret scanners do not flag documentation examples.
- Added a minimal quarantine artifact for one previously historical-only scanner finding in a non-product evaluator simulation path; the artifact contains no credential bytes.
- Added upgrade/update-awareness tests, interrupted-turn local helper tests, async evidence-closure tests, and expanded installer/custom-companion regression coverage.
- Wired chat-native bootstrap/rollover, interrupted turns, architecture-aware async reasoning, update awareness, and safe in-session upgrades into `SKILL.md`, README/README.ko, User Guide/User Guide.ko, First Run docs, and installer AGENTS markers.
- Updated validation workflow, preflight self-test, and source-distribution config for the new files.
- Published Sloar `0.8.1`.

## 0.8.0 - 2026-08-31

First-run / onboarding release.

- Added an explicit ONBOARD readiness step before RECOVER for new Sloar sessions.
- Added `environment-onboarding.md`, `scripts/wizard.py`, `docs/FIRST_RUN.md`, `docs/CONNECTIONS.md`, `docs/CHATGPT_PLUGINS.md`, and `examples/readiness.example.json`.
- Added `scripts/doctor.py` so local readiness is machine-readable without assuming hosted plugin/app state.
- Added repo-signal-based connection recommendations for GitHub, Vercel, Supabase, Netlify, and OpenAI Platform.
- Added `web-design-guidance` as a bundled companion skill for substantial UI/design work and kept repository-specific design systems authoritative.
- Added `--force` to the installer for replacing older bundled skill directories and kept AGENTS wiring idempotent.
- Added CI/self-test coverage for onboarding docs, wizard, installer behavior, and bundled design skills.
- Added a compact first-run readiness capsule and beginner-facing documentation.
- Published Sloar `0.8.0`.

## 0.7.0 - 2026-08-31

Forge resilience release.

- Added `references/forge-resilience.md` with explicit `LOCAL_READY`, `REMOTE_HEALTHY`, `REMOTE_PARTIAL`, `REMOTE_DEGRADED`, and `PUBLICATION_BLOCKED` states.
- Added capability/capability-state distinction so policy/permission failures are not retried like service/network outages.
- Added `scripts/forge-health.py` for one-shot forge/Git capability probing and failure fingerprinting.
- Added tests for local vs remote outage behavior, permission/capability classification, update-awareness, and non-retry rules.
- Added bilingual outage/CI recovery guides.
- Added an evidence-ledger example and outage reproduction harness.
- Kept local implementation/testing active when the forge is unavailable and exact local state remains healthy.
- Published Sloar `0.7.0`.

## 0.6.0 - 2026-08-31

First public release.

- Added the core `SKILL.md`, state machine, evidence ledger, capability ladder, recovery, concurrency, Actions mission, Android engineering, and rendered UI evidence guidance.
- Added installer/preflight/doctor/verification helper scripts and CI validation.
- Added remote supply workflow for sandbox acquisition fallback.
- Added README, Korean README, first-run docs, example ledgers, fixtures, and recovery/evidence samples.
- Published Sloar `0.6.0`.
