# Contributing

Contributions are welcome when they make Sloar more deterministic, portable, recoverable, or evidence-driven.

Before opening a change:

1. Keep runtime policy host-neutral unless a host-specific behavior is explicitly scoped.
2. Do not add repository-specific framework rules to the core skill.
3. Add a reference document when a procedure would make `SKILL.md` materially longer.
4. For new escalation paths, define capability prerequisites, exact inputs, outputs, failure handling, and cleanup.
5. For new retry behavior, define a failure fingerprint and the evidence required before another attempt.
6. Run the repository validation workflow or the local checks documented in `AGENTS.md`.

Please explain the failure mode your change prevents, not only the new rule it adds.
