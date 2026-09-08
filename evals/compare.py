#!/usr/bin/env python3
"""Compare two completed Sloar evaluation runs.

The scorer is intentionally model- and harness-agnostic. It does not execute an
agent or inspect task prompts. A runner produces paired result bundles; this
module checks comparability, summarizes objective signals, applies hard
regression gates, and decides whether the candidate has enough holdout or
production evidence to promote.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


REQUIRED_METRICS = ("success", "regression", "false_completion")
SECONDARY_METRICS = (
    "correction_distance",
    "tool_calls",
    "tokens",
    "wall_time_s",
)

DEFAULT_POLICY: dict[str, Any] = {
    "schema": 1,
    "min_tasks": 5,
    "allowed_promotion_splits": ["holdout", "production"],
    "min_success_gain": 0.02,
    "max_success_drop": 0.0,
    "max_regression_rate_delta": 0.0,
    "max_false_completion_rate_delta": 0.0,
    "max_secondary_worsening_ratio": 1.15,
    "min_secondary_improvement_ratio": 0.05,
    "min_secondary_improvements": 2,
    "min_category_tasks": 2,
    "max_category_success_drop": 0.05,
}


class EvalFormatError(ValueError):
    """Raised when a run cannot be compared safely."""


def _number(value: Any, *, name: str) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    raise EvalFormatError(f"{name} must be a finite number")


def _rate(value: Any, *, name: str) -> float:
    number = _number(value, name=name)
    if not 0.0 <= number <= 1.0:
        raise EvalFormatError(f"{name} must be in [0, 1]")
    return number


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvalFormatError(f"{path}: root must be an object")
    return value


def _validate_run(run: dict[str, Any], *, label: str) -> dict[str, dict[str, Any]]:
    for key in ("schema", "suite_id", "suite_version", "split", "run_id", "policy_id", "tasks"):
        if key not in run:
            raise EvalFormatError(f"{label}: missing {key}")
    if run["schema"] != 1:
        raise EvalFormatError(f"{label}: unsupported schema {run['schema']!r}")
    if not isinstance(run["tasks"], list) or not run["tasks"]:
        raise EvalFormatError(f"{label}: tasks must be a non-empty array")

    by_id: dict[str, dict[str, Any]] = {}
    for index, task in enumerate(run["tasks"]):
        if not isinstance(task, dict):
            raise EvalFormatError(f"{label}: tasks[{index}] must be an object")
        task_id = str(task.get("id") or "").strip()
        if not task_id:
            raise EvalFormatError(f"{label}: tasks[{index}] missing id")
        if task_id in by_id:
            raise EvalFormatError(f"{label}: duplicate task id {task_id}")
        metrics = task.get("metrics")
        if not isinstance(metrics, dict):
            raise EvalFormatError(f"{label}: {task_id} metrics must be an object")
        for metric in REQUIRED_METRICS:
            _rate(metrics.get(metric), name=f"{label}.{task_id}.{metric}")
        for metric in SECONDARY_METRICS:
            if metric in metrics and metrics[metric] is not None:
                value = _number(metrics[metric], name=f"{label}.{task_id}.{metric}")
                if value < 0:
                    raise EvalFormatError(f"{label}.{task_id}.{metric} must be >= 0")
        by_id[task_id] = task
    return by_id


def _mean(values: Iterable[float]) -> float:
    rows = list(values)
    if not rows:
        raise EvalFormatError("cannot average empty values")
    return sum(rows) / len(rows)


def _summary(tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ordered = list(tasks.values())
    result: dict[str, Any] = {
        "tasks": len(ordered),
        "success_rate": _mean(_rate(t["metrics"]["success"], name="success") for t in ordered),
        "regression_rate": _mean(_rate(t["metrics"]["regression"], name="regression") for t in ordered),
        "false_completion_rate": _mean(
            _rate(t["metrics"]["false_completion"], name="false_completion") for t in ordered
        ),
    }
    for metric in SECONDARY_METRICS:
        if all(metric in t["metrics"] and t["metrics"][metric] is not None for t in ordered):
            result[metric] = _mean(_number(t["metrics"][metric], name=metric) for t in ordered)

    categories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in ordered:
        category = str(task.get("category") or "uncategorized")
        categories[category].append(task)
    result["categories"] = {
        category: {
            "tasks": len(rows),
            "success_rate": _mean(
                _rate(t["metrics"]["success"], name=f"{category}.success") for t in rows
            ),
        }
        for category, rows in sorted(categories.items())
    }
    return result


def _lower_is_better_change(baseline: float, candidate: float) -> dict[str, Any]:
    if baseline == 0:
        if candidate == 0:
            return {"ratio": 1.0, "relative_improvement": 0.0}
        return {"ratio": math.inf, "relative_improvement": -math.inf}
    ratio = candidate / baseline
    return {"ratio": ratio, "relative_improvement": (baseline - candidate) / baseline}


def compare_runs(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    effective = dict(DEFAULT_POLICY)
    if policy:
        if policy.get("schema", 1) != 1:
            raise EvalFormatError("policy: unsupported schema")
        effective.update(policy)

    baseline_tasks = _validate_run(baseline, label="baseline")
    candidate_tasks = _validate_run(candidate, label="candidate")

    for key in ("suite_id", "suite_version", "split"):
        if baseline[key] != candidate[key]:
            raise EvalFormatError(
                f"runs are not comparable: {key} differs "
                f"({baseline[key]!r} != {candidate[key]!r})"
            )
    if set(baseline_tasks) != set(candidate_tasks):
        missing = sorted(set(baseline_tasks) - set(candidate_tasks))
        extra = sorted(set(candidate_tasks) - set(baseline_tasks))
        raise EvalFormatError(
            f"runs are not paired over identical task ids; missing={missing}, extra={extra}"
        )

    for task_id, base_task in baseline_tasks.items():
        if (base_task.get("category") or "uncategorized") != (candidate_tasks[task_id].get("category") or "uncategorized"):
            raise EvalFormatError(f"{task_id}: category changed between paired runs")
    for metric in SECONDARY_METRICS:
        base_coverage = {key for key, task in baseline_tasks.items() if task["metrics"].get(metric) is not None}
        cand_coverage = {key for key, task in candidate_tasks.items() if task["metrics"].get(metric) is not None}
        if base_coverage != cand_coverage or (base_coverage and base_coverage != set(baseline_tasks)):
            raise EvalFormatError(f"{metric}: incomplete or mismatched coverage cannot silently disable a regression gate")

    base = _summary(baseline_tasks)
    cand = _summary(candidate_tasks)
    success_delta = cand["success_rate"] - base["success_rate"]
    regression_delta = cand["regression_rate"] - base["regression_rate"]
    false_completion_delta = cand["false_completion_rate"] - base["false_completion_rate"]

    gates: list[dict[str, Any]] = []

    def gate(name: str, passed: bool, detail: str) -> None:
        gates.append({"name": name, "passed": bool(passed), "detail": detail})

    gate(
        "minimum_task_count",
        base["tasks"] >= int(effective["min_tasks"]),
        f"{base['tasks']} >= {int(effective['min_tasks'])}",
    )
    gate(
        "success_non_regression",
        success_delta >= -float(effective["max_success_drop"]),
        f"delta={success_delta:+.4f}",
    )
    gate(
        "regression_rate_non_regression",
        regression_delta <= float(effective["max_regression_rate_delta"]),
        f"delta={regression_delta:+.4f}",
    )
    gate(
        "false_completion_non_regression",
        false_completion_delta <= float(effective["max_false_completion_rate_delta"]),
        f"delta={false_completion_delta:+.4f}",
    )

    secondary: dict[str, Any] = {}
    secondary_improvements = 0
    for metric in SECONDARY_METRICS:
        if metric not in base or metric not in cand:
            continue
        change = _lower_is_better_change(float(base[metric]), float(cand[metric]))
        secondary[metric] = {
            "baseline": base[metric],
            "candidate": cand[metric],
            **change,
        }
        ratio = change["ratio"]
        gate(
            f"{metric}_worsening_bound",
            ratio <= float(effective["max_secondary_worsening_ratio"]),
            f"candidate/baseline={ratio:.4f}" if math.isfinite(ratio) else "candidate/baseline=inf",
        )
        if change["relative_improvement"] >= float(effective["min_secondary_improvement_ratio"]):
            secondary_improvements += 1

    category_findings: list[dict[str, Any]] = []
    for category, base_row in base["categories"].items():
        cand_row = cand["categories"].get(category)
        if cand_row is None:
            continue
        if base_row["tasks"] < int(effective["min_category_tasks"]):
            continue
        delta = cand_row["success_rate"] - base_row["success_rate"]
        passed = delta >= -float(effective["max_category_success_drop"])
        category_findings.append(
            {
                "category": category,
                "tasks": base_row["tasks"],
                "success_delta": delta,
                "passed": passed,
            }
        )
        gate(
            f"category:{category}:success_non_regression",
            passed,
            f"delta={delta:+.4f}",
        )

    hard_gates_passed = all(row["passed"] for row in gates)
    allowed_split = str(baseline["split"]) in set(effective["allowed_promotion_splits"])

    material_success_gain = success_delta >= float(effective["min_success_gain"])
    efficiency_gain = (
        success_delta >= -float(effective["max_success_drop"])
        and secondary_improvements >= int(effective["min_secondary_improvements"])
    )
    positive_evidence = material_success_gain or efficiency_gain

    if not allowed_split:
        decision = "EXPERIMENT_ONLY"
        reason = (
            f"split {baseline['split']!r} is not promotion evidence; "
            "use a holdout or production split"
        )
    elif not hard_gates_passed:
        decision = "REJECT"
        failed = [row["name"] for row in gates if not row["passed"]]
        reason = "hard regression gate failed: " + ", ".join(failed)
    elif not positive_evidence:
        decision = "NO_PROMOTION"
        reason = "candidate is non-regressing but lacks the configured material improvement"
    else:
        decision = "PROMOTE"
        if material_success_gain:
            reason = f"success rate improved by {success_delta:+.4f} with all hard gates green"
        else:
            reason = (
                f"success held while {secondary_improvements} secondary metrics improved "
                "materially with all hard gates green"
            )

    return {
        "schema": 1,
        "suite": {
            "id": baseline["suite_id"],
            "version": baseline["suite_version"],
            "split": baseline["split"],
            "tasks": base["tasks"],
        },
        "runs": {
            "baseline": {"run_id": baseline["run_id"], "policy_id": baseline["policy_id"]},
            "candidate": {"run_id": candidate["run_id"], "policy_id": candidate["policy_id"]},
        },
        "decision": decision,
        "reason": reason,
        "hard_gates_passed": hard_gates_passed,
        "deltas": {
            "success_rate": success_delta,
            "regression_rate": regression_delta,
            "false_completion_rate": false_completion_delta,
        },
        "secondary": secondary,
        "secondary_improvements": secondary_improvements,
        "categories": category_findings,
        "gates": gates,
        "baseline": base,
        "candidate": cand,
        "policy": effective,
    }


def _human(result: dict[str, Any]) -> str:
    delta = result["deltas"]
    lines = [
        f"Sloar eval decision: {result['decision']}",
        (
            f"Suite: {result['suite']['id']}@{result['suite']['version']} "
            f"split={result['suite']['split']} tasks={result['suite']['tasks']}"
        ),
        (
            "Delta: "
            f"success={delta['success_rate']:+.3f} "
            f"regression={delta['regression_rate']:+.3f} "
            f"false_completion={delta['false_completion_rate']:+.3f}"
        ),
        f"Reason: {result['reason']}",
    ]
    failed = [row["name"] for row in result["gates"] if not row["passed"]]
    if failed:
        lines.append("Failed gates: " + ", ".join(failed))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--require-promote",
        action="store_true",
        help="return exit code 2 unless the decision is PROMOTE",
    )
    args = parser.parse_args()

    try:
        baseline = _load(args.baseline)
        candidate = _load(args.candidate)
        policy = _load(args.policy) if args.policy else None
        result = compare_runs(baseline, candidate, policy)
    except (OSError, json.JSONDecodeError, EvalFormatError) as exc:
        if args.json:
            print(json.dumps({"schema": 1, "decision": "INVALID", "error": str(exc)}, indent=2))
        else:
            print(f"Sloar eval: INVALID: {exc}")
        return 2

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(_human(result))
    if args.require_promote and result["decision"] != "PROMOTE":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
