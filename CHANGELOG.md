# Changelog

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
