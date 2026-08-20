# Recovery and failure fingerprints

## Recovery priority

Use durable state in this order:

```text
verified task commit / PR head
  > immutable Git or CI artifact
  > surviving sandbox working tree
  > checkpoint
  > conversation reconstruction
```

A checkpoint helps locate state; it does not outrank exact repository objects.

## Failure fingerprint

Normalize a failure into fields such as:

```text
operation
input identity
execution level
failing phase
status / exit code
normalized error signature
external endpoint or dependency when relevant
```

Example:

```text
operation: npm install
input: package-lock sha256:...
level: L1
phase: dependency acquisition
exit: 1
error: EAI_AGAIN registry.npmjs.org
```

Repeating that operation unchanged is not progress.

## Recovery procedure

1. Inspect surviving sandbox state before deleting or recreating it.
2. Resolve the latest durable task branch/PR/commit.
3. Compare surviving local identity with durable identity.
4. Preserve unfamiliar dirty changes until ownership is understood.
5. Restore the most exact state available.
6. Re-run only verification invalidated by the recovery.
7. Update the checkpoint/evidence ledger.

## Checkpoint minimum fields

- schema version;
- repository;
- expected base commit/tree;
- task branch/head;
- state-machine stage;
- verified evidence IDs and target commits;
- pending checks;
- known failure fingerprints;
- task-owned temporary resources.
