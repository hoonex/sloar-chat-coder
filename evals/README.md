# Sloar Evals

Sloar Evals is the development-time evaluation layer for Sloar itself. It is
deliberately separate from the installed `sloar-chat-coder` Skill: target
repositories should not inherit Sloar's benchmark machinery.

It answers two separate questions:

1. can the same task suite be executed under stable and candidate Sloar policies
   with comparable execution identity and preserved trajectory evidence?
2. did the candidate become measurably better without hiding a regression behind
   an aggregate score?

`run.py` owns the first boundary. `compare.py` owns the second. Neither mutates
the stable Sloar policy automatically.

## Evaluation loop

```text
stable policy ------------------+
                                |
                                v
                         identical task suite
                                |
                                +--> evals/run.py --> baseline.json
                                |
candidate policy ---------------+--> evals/run.py --> candidate.json
                                                      |
                                                      v
                                              evals/compare.py
                                                      |
                              EXPERIMENT_ONLY | PROMOTE | NO_PROMOTION | REJECT
```

Dev data may guide changes, so it cannot by itself authorize promotion. The
default policy accepts promotion evidence only from `holdout` or `production`
splits.

## Suite manifest

A runner suite is plain JSON. Task payload is intentionally opaque to Sloar
Evals; the adapter decides how to materialize a repository, prompt an agent, run
checks, and calculate task metrics.

```json
{
  "schema": 1,
  "suite_id": "sloar-core",
  "suite_version": "2026-09-08.1",
  "split": "holdout",
  "tasks": [
    {
      "id": "bugfix-001",
      "category": "bugfix",
      "payload": {
        "repository": "example/project",
        "base_ref": "0123456789abcdef",
        "case_ref": "private-case-001"
      }
    }
  ]
}
```

The runner hashes the exact suite bytes. Do not reuse a suite version for changed
task bytes.

## Agent adapter contract

`run.py` is provider-agnostic. It launches one external adapter process per task
and passes the evaluation boundary through environment variables rather than
shell-substituting task content.

Important variables:

```text
SLOAR_EVAL_TASK_FILE
SLOAR_EVAL_TASK_ID
SLOAR_EVAL_POLICY_ID
SLOAR_EVAL_POLICY_PATH
SLOAR_EVAL_MODEL_ID
SLOAR_EVAL_OUTPUT_DIR
SLOAR_EVAL_RESULT_FILE
SLOAR_EVAL_TRAJECTORY_FILE
```

The adapter receives the complete task in `SLOAR_EVAL_TASK_FILE`. It must write
`SLOAR_EVAL_RESULT_FILE` and exit zero only when the evaluation itself completed
successfully. A model that attempts the task and fails is still a successful
*evaluation execution*: write `success: 0` and exit zero. Adapter crashes,
timeouts, missing result files, or malformed metrics are evaluation-infrastructure
failures and are never silently converted into poor model scores.

Minimum adapter result:

```json
{
  "task_id": "bugfix-001",
  "metrics": {
    "success": 1,
    "regression": 0,
    "false_completion": 0,
    "correction_distance": 0.12,
    "tool_calls": 11,
    "tokens": 9300
  }
}
```

`success`, `regression`, and `false_completion` are required rates in `[0, 1]`.
Secondary lower-is-better metrics are optional. `wall_time_s` is measured by the
runner and replaces any adapter self-report.

The adapter may also write JSONL trajectory evidence to
`SLOAR_EVAL_TRAJECTORY_FILE`. The public result bundle records artifact digests,
not the trajectory contents themselves.

## Run a suite

```bash
python3 evals/run.py evals/suites/dev.json \
  --policy-id stable-0.9 \
  --policy-path .agents/skills/sloar-chat-coder \
  --model-id gpt-5.6-sol \
  --adapter-id my-agent-harness \
  --adapter-version 1 \
  --output runs/stable.json \
  -- python3 path/to/adapter.py
```

Run the candidate with the same suite, model, adapter version, adapter command,
and timeout, changing only the Sloar policy identity/path and output location.
There is no autonomous retry loop. A failed adapter execution requires diagnosis
before another run.

## Comparable execution identity

A benchmark comparison is invalid if the candidate quietly changes more than the
policy under test. `run.py` therefore computes a comparison fingerprint from:

- the exact suite-manifest bytes;
- model ID;
- adapter ID and version;
- the exact adapter command;
- runner schema;
- per-task timeout.

The runner appends the fingerprint to the emitted `suite_version`:

```text
2026-09-08.1+ctx.8f0f... 
```

Policy bytes are deliberately **not** part of this fingerprint: stable and
candidate policies must differ while remaining comparable. Their exact policy
digests are recorded separately as `execution.policy_sha256`.

Because `compare.py` already requires exact `suite_version` equality, changing
the model/harness/suite execution context makes the pair fail comparability
instead of producing a misleading score.

This does not prove two remote model invocations were physically identical; a
provider can change hidden serving details. Record the strongest model/runtime
identity the adapter can actually observe.

## Result bundle

Runner-produced bundles contain the scorer fields plus execution identity and
artifact digests:

```json
{
  "schema": 1,
  "suite_id": "sloar-core",
  "suite_version": "2026-09-08.1+ctx.8f0f123456789abc",
  "split": "holdout",
  "run_id": "run-42",
  "policy_id": "stable-0.9",
  "execution": {
    "runner": "sloar-evals",
    "runner_schema": 1,
    "declared_suite_version": "2026-09-08.1",
    "comparison_fingerprint": "...",
    "model_id": "gpt-5.6-sol",
    "adapter_id": "my-agent-harness",
    "adapter_version": "1",
    "suite_manifest_sha256": "...",
    "policy_sha256": "..."
  },
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
      },
      "artifacts": {
        "result_sha256": "...",
        "trajectory_sha256": "...",
        "trajectory_present": true
      }
    }
  ]
}
```

`correction_distance` is evaluator-defined but must stay stable within a suite. A
common choice is normalized edit distance between the agent's final patch and
the accepted patch.

## Compare runs

```bash
python3 evals/compare.py runs/stable.json runs/candidate.json
python3 evals/compare.py runs/stable.json runs/candidate.json --json
python3 evals/compare.py runs/stable.json runs/candidate.json \
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

The exact thresholds live in `promotion-policy.json` and are intentionally plain
data rather than hidden scoring logic.

## Holdout hygiene

The improver should not receive holdout prompts, expected patches, trajectories,
or per-task failure explanations before a candidate is frozen. The suite file
and per-task artifact directory are therefore part of the evaluator trust
boundary. Keeping a holdout suite in the same readable workspace as the improver
is not hidden evaluation merely because it is named `holdout`.

Prefer an evaluator boundary that returns only the aggregate evidence needed for
a promotion decision. Preserve raw artifacts for audit, but do not automatically
feed them back into the strategy generator.

A benchmark score is not synonymous with real capability. Keep suite versions
immutable, rotate/add fresh tasks, preserve production correction signals, and
treat repeated optimization against one exposed suite as contamination risk.

## Next steps

The execution and scoring substrate now exists. The next useful layers are:

1. one real coding-agent adapter that can materialize immutable repository cases,
   run Sloar stable/candidate under the same model harness, and derive objective
   result metrics;
2. fresh/private suite generation and immutable case storage;
3. production feedback ingestion (accepted patch, user correction, rollback,
   false completion);
4. failure clustering that proposes *candidate* strategy changes without seeing
   holdout evidence;
5. versioned promotion and rollback of strategy policy, never live mutation of
   the stable core.
