# Sloar Evals

Sloar Evals is the development-time evaluation layer for Sloar itself. It is
deliberately separate from the installed `sloar-chat-coder` Skill: target
repositories should not inherit Sloar's benchmark machinery.

The first version answers one question:

> Did a candidate Sloar policy become measurably better on paired tasks without
> hiding a regression behind an aggregate score?

It does **not** launch a model, mutate Sloar automatically, or treat one
benchmark as ground truth. A runner produces completed result bundles; the
scorer compares them.

## Evaluation loop

```text
stable policy
    |
    +---- run on dev tasks --------> inspect failures / propose candidate
    |
candidate policy
    |
    +---- run on the same dev tasks -> EXPERIMENT_ONLY
    |
    +---- run on hidden holdout ----> PROMOTE | NO_PROMOTION | REJECT
    |
    +---- production evidence ------> later confirmation / rollback signal
```

Dev data may guide changes, so it cannot by itself authorize promotion. The
default policy accepts promotion evidence only from `holdout` or `production`
splits.

## Result bundle

Baseline and candidate runs must use the same `suite_id`, `suite_version`,
`split`, and exact task IDs.

```json
{
  "schema": 1,
  "suite_id": "sloar-core",
  "suite_version": "2026-09-08.1",
  "split": "holdout",
  "run_id": "run-42",
  "policy_id": "stable-0.9",
  "tasks": [
    {
      "id": "bugfix-001",
      "category": "bugfix",
      "metrics": {
        "success": 1,
        "regression": 0,
        "false_completion": 0,
        "correction_distance": 0.12,
        "tool_calls": 11,
        "tokens": 9300,
        "wall_time_s": 88
      }
    }
  ]
}
```

Required metrics are `success`, `regression`, and `false_completion`, each in
`[0, 1]`. Secondary lower-is-better metrics are optional, but when present for
every paired task they can support an efficiency promotion.

`correction_distance` is runner-defined but should be stable within a suite. A
common choice is normalized edit distance between the agent's final patch and
the accepted patch.

## Compare runs

```bash
python3 evals/compare.py baseline.json candidate.json
python3 evals/compare.py baseline.json candidate.json --json
python3 evals/compare.py baseline.json candidate.json \
  --policy evals/promotion-policy.json \
  --require-promote
```

`--require-promote` exits non-zero unless the decision is `PROMOTE`; without it,
a valid comparison exits successfully even when the candidate is rejected.

Possible decisions:

- `PROMOTE`: holdout/production evidence shows material improvement and every
  hard gate passes.
- `NO_PROMOTION`: no hard regression, but improvement is too small.
- `REJECT`: at least one hard regression gate failed.
- `EXPERIMENT_ONLY`: the split is useful for iteration but not for promotion.
- `INVALID`: runs are not safely comparable.

## Default promotion discipline

The default policy rejects a candidate when any of these happen:

- task coverage differs between baseline and candidate;
- overall success drops;
- regression rate increases;
- false-completion rate increases;
- a sufficiently represented task category loses more than the configured
  success tolerance;
- a reported secondary metric worsens beyond the configured ratio.

A candidate then needs either a material success-rate gain or several material
secondary improvements while success is held.

The exact thresholds live in `promotion-policy.json` and are intentionally
plain data rather than hidden scoring logic.

## Holdout hygiene

The improver should not receive holdout prompts, expected patches, or
per-task failure explanations before a candidate is frozen. Prefer an evaluator
boundary that returns only the evidence needed for a promotion decision.

A benchmark score is not synonymous with real capability. Keep suite versions
immutable, rotate/add fresh tasks, preserve production correction signals, and
treat repeated optimization against one exposed suite as contamination risk.

## Next steps

This MVP is a scorer, not yet an autonomous improvement engine. The next useful
layers are:

1. a task runner that records identical structured trajectories for baseline
   and candidate policies;
2. fresh/hidden suite generation and immutable suite versioning;
3. production feedback ingestion (accepted patch, user correction, rollback,
   false completion);
4. failure clustering that proposes *candidate* strategy changes;
5. versioned promotion and rollback of strategy policy, never live mutation of
   the stable core.
