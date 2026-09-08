# Codex-backed Sloar evaluation

`evals/adapters/codex_cli.py` is the first concrete Sloar Evals agent adapter. It
uses non-interactive `codex exec`, isolates each task in a fresh worktree, gives
Codex one frozen Sloar policy snapshot, then derives correctness from objective
repository checks rather than the model's self-assessment.

The adapter requires an installed/authenticated Codex CLI. It does not require a
repository-stored API key; normal Codex sign-in or an externally supplied Codex
credential can be used by the host environment.

## Fast smoke run

From a candidate Sloar branch:

```bash
python3 evals/run_pair.py evals/suites/smoke-dev.json \
  --stable-ref main \
  --candidate-ref HEAD \
  --model-id gpt-5.6-sol \
  --reasoning-effort high
```

The command archives the exact `.agents/skills` tree from both refs, exposes the
stable and candidate policy at the same path in separate sequential runs, keeps
model/harness/suite identity fixed, and writes evidence under
`.sloar-evals/latest/`.

`smoke-dev.json` is intentionally public and tiny. Its decision is
`EXPERIMENT_ONLY`; it proves the execution/evidence path works but must never be
used as promotion evidence.

## Task contract

A Codex task contains:

```json
{
  "id": "example-bug",
  "category": "bugfix",
  "prompt": "Fix the observed behavior without changing the public API.",
  "repository": {
    "url": "https://github.com/example/project.git",
    "commit": "<immutable commit sha>"
  },
  "verification": {
    "acceptance": {
      "command": ["python3", "-m", "pytest", "tests/test_bug.py", "-q"],
      "timeout_s": 120
    },
    "regression": {
      "command": ["python3", "-m", "pytest", "-q"],
      "timeout_s": 600
    }
  }
}
```

For development fixtures, `repository.fixture_path` plus an inline `seed_patch`
can replace URL/commit materialization. Public fixtures are suitable only for
smoke/dev iteration, not hidden holdout promotion.

## Metrics

The adapter emits:

- `success = 1` only when the acceptance command passes;
- `regression = 1` when the regression command fails;
- `false_completion = 1` when Codex reports `status=completed` but acceptance
  still fails;
- `wall_time_s` is measured by the outer runner.

Raw Codex JSONL, final structured message, patch, verifier logs, and command
metadata are kept as task artifacts. Adapter crashes, missing final output, and
Codex timeouts are evaluator failures rather than model-score failures.

## Promotion boundary

A real promotion suite must be private to the improver until the candidate is
frozen. Do not put hidden prompts, expected patches, or per-task holdout
trajectories in a workspace readable by the candidate-generation agent.
