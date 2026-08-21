# Changelog

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
