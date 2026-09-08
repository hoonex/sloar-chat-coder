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
  --reasoning-effort medium
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
    "commit": "<full 40- or 64-character commit SHA>"
  },
  "verification": {
    "protected_paths": ["tests", "conftest.py", "pyproject.toml"],
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
  or regression verification fails;
- `wall_time_s` is measured by the outer runner.

Raw Codex JSONL, final structured message, patch, verifier logs, and command
metadata are kept as task artifacts. Adapter crashes, missing final output, and
Codex timeouts are evaluator failures rather than model-score failures.

## Promotion boundary

A real promotion suite must be private to the improver until the candidate is
frozen. Do not put hidden prompts, expected patches, or per-task holdout
trajectories in a workspace readable by the candidate-generation agent.

## Integrity and environment limits

This adapter accepts `dev` only. A fresh worktree and prompt instructions do not
isolate hidden evaluator data from an agent running under the same OS identity.
Holdout/production evaluation needs a separate trusted execution boundary; simply
renaming the split is rejected. This CLI harness does not reproduce the ChatGPT
chat + GitHub connector environment or establish gains in that environment.

The evaluator snapshots protected tests/configuration before the agent runs. Any
change, deletion, addition under a protected directory, or symlink substitution
fails the task without executing the modified checks. Declare all verifier entry
points and relevant configuration in `verification.protected_paths`; defaults
cover `tests`, `conftest.py`, `pytest.ini`, `pyproject.toml`, and `setup.cfg`.
This detects verifier modification, not every possible attempt by arbitrary
candidate code to interfere with its interpreter. Raw logs and patches remain
audit evidence, not a secure evaluator boundary.

Patch evidence is relative to the original materialized commit and includes new
non-ignored files and commits made by the agent. Both required checks count when
assessing a completion claim. The outer runner invalidates a run if policy source
bytes change during it. The harness version is 2 because these grading semantics
must not be compared with version 1 results.

The adapter currently emits correctness metrics plus runner-measured wall time.
It does not yet extract tokens, tool calls, or correction distance. Do not claim
those costs improved merely because a run became faster. Use an explicit fresh
`--output-dir` for another run; existing artifact directories are preserved.
