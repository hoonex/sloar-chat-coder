# State machine

Sloar models repository engineering as explicit states. The states are procedural guardrails, not a requirement to narrate every step.

## RECOVER

Enter when prior work may exist or state continuity is uncertain.

Must establish:
- surviving sandbox workspace status;
- known durable branch/PR/commit/artifact state;
- ownership of unfamiliar temporary resources before deleting them.

Exit when the candidate task state is known well enough to identify the intended source.

## IDENTIFY

Resolve mutable names to immutable identity.

Minimum evidence:
- repository identity;
- intended branch/PR/ref;
- resolved commit SHA;
- resolved tree SHA when available.

Exit when the exact source target is immutable.

## MATERIALIZE

Create a complete working tree for the identified source.

Must verify:
- checked-out HEAD equals expected commit SHA;
- tree identity equals expected tree when known;
- unexpected dirty state is absent or explicitly preserved and understood.

A collection of individually fetched source snippets is not a complete materialized working tree for repository-wide engineering.

## BRANCH

Use the target repository's branch policy. When isolated task branches are required, create from the verified immutable base, not from a stale mutable name.

Exit when the write target and base identity are known.

## IMPLEMENT

Make the smallest coherent change that satisfies the task. Preserve unrelated work. Use repository-native formatting, architecture, and dependency rules.

## VERIFY

Choose checks based on change risk and repository declarations. Verification failures must be classified before source is changed.

Exit when required checks pass or a concrete blocker is recorded in the evidence ledger.

## PUBLISH

Before writing remote state:
1. re-resolve mutable base/head refs;
2. compare them to expected identities;
3. stop if reconciliation is required;
4. publish exact verified bytes/objects;
5. verify the resulting remote head/diff.

## REMOTE_VERIFY

Run or inspect relevant CI, deployment, integration, production, or remote checks required by the repository/task. Do not treat a green unrelated check as evidence for the changed behavior.

## CLEANUP

Remove only task-owned temporary resources after terminal state is known. Do not delete unfamiliar workflows, branches, artifacts, or files merely because their names look temporary.
