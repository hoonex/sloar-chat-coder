# Sloar Chat Coder repository guidance

This repository maintains the `sloar-chat-coder` Agent Skill.

When modifying the skill itself:

1. Read `.agents/skills/sloar-chat-coder/SKILL.md` first.
2. Preserve the public contract: Sloar governs continuity, exact state, escalation, failure handling, publication safety, and evidence. It must not override a target repository's engineering method.
3. Keep `SKILL.md` concise. Put detailed procedures in one-level `references/` files and executable helpers in `scripts/`.
4. Prefer normative, testable rules over motivational prose.
5. New fallback mechanisms must have explicit entry conditions, exit conditions, and terminal cleanup behavior.
6. Do not introduce retry loops. Every retry rule must name the evidence that makes the retry different from the previous attempt.
7. If a rule can cause writes to GitHub or remote execution, require a fresh immutable source identity and a publication/concurrency guard.
8. First-run guidance must distinguish Plugin, App, Skill, local execution, and authorization without assuming product capabilities.
9. Run `bash .agents/skills/sloar-chat-coder/scripts/preflight.sh --self-test`, Python helper tests, and `bash -n` on shell scripts before publishing changes.
