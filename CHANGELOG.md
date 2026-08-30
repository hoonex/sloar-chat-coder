# Changelog

## Unreleased

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
