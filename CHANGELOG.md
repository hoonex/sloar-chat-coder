# Changelog

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
