#!/usr/bin/env python3
"""Run a Sloar evaluation suite through an external agent adapter.

The runner is intentionally provider-agnostic. It executes one adapter process per
suite task, passes task/policy identity through environment variables, preserves
artifacts, and emits the result bundle consumed by ``evals.compare``.

A non-zero adapter exit, timeout, malformed result, or missing result is an
infrastructure/evaluator failure. The runner does not convert those failures into
model failures and does not retry automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Sequence


REQUIRED_METRICS = ("success", "regression", "false_completion")
SECONDARY_METRICS = ("correction_distance", "tool_calls", "tokens", "wall_time_s")


class RunnerError(RuntimeError):
    """Raised when an evaluation run cannot produce trustworthy evidence."""


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RunnerError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RunnerError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RunnerError(f"{path}: root must be an object")
    return value


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def hash_policy_path(path: Path) -> str:
    """Return a deterministic digest for one policy file or directory tree."""
    path = path.resolve()
    if path.is_file():
        return _sha256_bytes(b"file\0" + path.name.encode() + b"\0" + path.read_bytes())
    if not path.is_dir():
        raise RunnerError(f"policy path does not exist: {path}")

    hasher = hashlib.sha256()
    hasher.update(b"directory\0")
    files = sorted(row for row in path.rglob("*") if row.is_file()
                   and "__pycache__" not in row.parts and row.suffix != ".pyc")
    if not files:
        raise RunnerError(f"policy directory is empty: {path}")
    for file_path in files:
        relative = file_path.relative_to(path).as_posix()
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(_sha256_file(file_path).encode("ascii"))
        hasher.update(b"\0")
    return hasher.hexdigest()


def _finite_number(value: Any, *, name: str) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        number = float(value)
        if number == number and abs(number) != float("inf"):
            return number
    raise RunnerError(f"{name} must be a finite number")


def _validate_metrics(metrics: Any, *, task_id: str) -> dict[str, float]:
    if not isinstance(metrics, dict):
        raise RunnerError(f"{task_id}: result metrics must be an object")
    normalized: dict[str, float] = {}
    for metric in REQUIRED_METRICS:
        number = _finite_number(metrics.get(metric), name=f"{task_id}.{metric}")
        if not 0.0 <= number <= 1.0:
            raise RunnerError(f"{task_id}.{metric} must be in [0, 1]")
        normalized[metric] = number
    for metric in SECONDARY_METRICS:
        if metric not in metrics or metrics[metric] is None:
            continue
        number = _finite_number(metrics[metric], name=f"{task_id}.{metric}")
        if number < 0:
            raise RunnerError(f"{task_id}.{metric} must be >= 0")
        normalized[metric] = number
    return normalized


def _validate_suite(suite: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("schema", "suite_id", "suite_version", "split", "tasks"):
        if key not in suite:
            raise RunnerError(f"suite missing {key}")
    if suite["schema"] != 1:
        raise RunnerError(f"unsupported suite schema {suite['schema']!r}")
    if not isinstance(suite["tasks"], list) or not suite["tasks"]:
        raise RunnerError("suite tasks must be a non-empty array")

    seen: set[str] = set()
    tasks: list[dict[str, Any]] = []
    for index, task in enumerate(suite["tasks"]):
        if not isinstance(task, dict):
            raise RunnerError(f"suite.tasks[{index}] must be an object")
        task_id = str(task.get("id") or "").strip()
        if not task_id:
            raise RunnerError(f"suite.tasks[{index}] missing id")
        if task_id in seen:
            raise RunnerError(f"duplicate suite task id {task_id}")
        seen.add(task_id)
        tasks.append(task)
    return tasks


def _safe_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return (cleaned or "task")[:80]


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _artifact_digest(path: Path) -> str | None:
    return _sha256_file(path) if path.is_file() else None


def _comparison_fingerprint(
    *,
    suite_digest: str,
    model_id: str,
    adapter_id: str,
    adapter_version: str,
    adapter_command: Sequence[str],
    timeout_s: float,
) -> str:
    payload = {
        "runner_schema": 1,
        "suite_manifest_sha256": suite_digest,
        "model_id": model_id,
        "adapter_id": adapter_id,
        "adapter_version": adapter_version,
        "adapter_command": list(adapter_command),
        "task_timeout_s": timeout_s,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _sha256_bytes(encoded)


def run_suite(
    *,
    suite_path: Path,
    policy_id: str,
    policy_path: Path,
    model_id: str,
    adapter_id: str,
    adapter_version: str,
    adapter_command: Sequence[str],
    output_path: Path,
    artifacts_dir: Path | None = None,
    run_id: str | None = None,
    timeout_s: float = 1800.0,
    cwd: Path | None = None,
) -> dict[str, Any]:
    if not adapter_command:
        raise RunnerError("adapter command is empty")
    if timeout_s <= 0:
        raise RunnerError("timeout_s must be > 0")

    suite_path = suite_path.resolve()
    policy_path = policy_path.resolve()
    suite = _json_object(suite_path)
    tasks = _validate_suite(suite)
    suite_digest = _sha256_file(suite_path)
    policy_digest = hash_policy_path(policy_path)
    comparison_fingerprint = _comparison_fingerprint(
        suite_digest=suite_digest,
        model_id=model_id,
        adapter_id=adapter_id,
        adapter_version=adapter_version,
        adapter_command=adapter_command,
        timeout_s=timeout_s,
    )
    declared_suite_version = str(suite["suite_version"])
    effective_suite_version = f"{declared_suite_version}+ctx.{comparison_fingerprint[:16]}"
    run_id = run_id or f"run-{uuid.uuid4().hex[:12]}"

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if artifacts_dir is None:
        artifacts_dir = output_path.parent / f"{output_path.stem}.artifacts"
    artifacts_dir = artifacts_dir.resolve()
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    bundle_tasks: list[dict[str, Any]] = []
    run_started = time.time()

    for index, task in enumerate(tasks, start=1):
        task_id = str(task["id"])
        category = str(task.get("category") or "uncategorized")
        task_dir = artifacts_dir / f"{index:04d}-{_safe_component(task_id)}"
        if task_dir.exists() and any(task_dir.iterdir()):
            raise RunnerError(f"artifact directory is not empty: {task_dir}")
        task_dir.mkdir(parents=True, exist_ok=True)

        task_file = task_dir / "task.json"
        result_file = task_dir / "result.json"
        trajectory_file = task_dir / "trajectory.jsonl"
        stdout_file = task_dir / "stdout.log"
        stderr_file = task_dir / "stderr.log"
        task_file.write_text(json.dumps(task, indent=2, ensure_ascii=False), encoding="utf-8")

        env = os.environ.copy()
        env.update(
            {
                "SLOAR_EVAL_SCHEMA": "1",
                "SLOAR_EVAL_SUITE_ID": str(suite["suite_id"]),
                "SLOAR_EVAL_SUITE_VERSION": effective_suite_version,
                "SLOAR_EVAL_DECLARED_SUITE_VERSION": declared_suite_version,
                "SLOAR_EVAL_SPLIT": str(suite["split"]),
                "SLOAR_EVAL_RUN_ID": run_id,
                "SLOAR_EVAL_TASK_ID": task_id,
                "SLOAR_EVAL_TASK_FILE": str(task_file),
                "SLOAR_EVAL_POLICY_ID": policy_id,
                "SLOAR_EVAL_POLICY_PATH": str(policy_path),
                "SLOAR_EVAL_MODEL_ID": model_id,
                "SLOAR_EVAL_OUTPUT_DIR": str(task_dir),
                "SLOAR_EVAL_RESULT_FILE": str(result_file),
                "SLOAR_EVAL_TRAJECTORY_FILE": str(trajectory_file),
            }
        )

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                list(adapter_command),
                cwd=str(cwd.resolve()) if cwd else None,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            if exc.stdout:
                _write_text(stdout_file, exc.stdout if isinstance(exc.stdout, str) else exc.stdout.decode(errors="replace"))
            if exc.stderr:
                _write_text(stderr_file, exc.stderr if isinstance(exc.stderr, str) else exc.stderr.decode(errors="replace"))
            raise RunnerError(f"{task_id}: adapter timed out after {timeout_s:g}s") from exc
        elapsed = time.perf_counter() - started
        _write_text(stdout_file, completed.stdout)
        _write_text(stderr_file, completed.stderr)

        if hash_policy_path(policy_path) != policy_digest:
            raise RunnerError(f"{task_id}: policy bytes changed during evaluation; run is invalid")

        if completed.returncode != 0:
            raise RunnerError(
                f"{task_id}: adapter exited {completed.returncode}; "
                f"inspect {stderr_file} and {stdout_file}"
            )
        if not result_file.is_file():
            raise RunnerError(f"{task_id}: adapter did not produce {result_file}")

        result = _json_object(result_file)
        result_task_id = str(result.get("task_id") or task_id)
        if result_task_id != task_id:
            raise RunnerError(f"{task_id}: result task_id mismatch ({result_task_id!r})")
        metrics = _validate_metrics(result.get("metrics"), task_id=task_id)
        # Wall time comes from the runner boundary, not self-reported adapter telemetry.
        metrics["wall_time_s"] = elapsed

        bundle_tasks.append(
            {
                "id": task_id,
                "category": category,
                "metrics": metrics,
                "artifacts": {
                    "result_sha256": _artifact_digest(result_file),
                    "trajectory_sha256": _artifact_digest(trajectory_file),
                    "trajectory_present": trajectory_file.is_file(),
                    "stdout_sha256": _artifact_digest(stdout_file),
                    "stderr_sha256": _artifact_digest(stderr_file),
                },
            }
        )

    run_finished = time.time()
    bundle = {
        "schema": 1,
        "suite_id": suite["suite_id"],
        "suite_version": effective_suite_version,
        "split": suite["split"],
        "run_id": run_id,
        "policy_id": policy_id,
        "execution": {
            "runner": "sloar-evals",
            "runner_schema": 1,
            "declared_suite_version": declared_suite_version,
            "comparison_fingerprint": comparison_fingerprint,
            "model_id": model_id,
            "adapter_id": adapter_id,
            "adapter_version": adapter_version,
            "suite_manifest_sha256": suite_digest,
            "policy_sha256": policy_digest,
            "task_timeout_s": timeout_s,
            "started_unix_s": run_started,
            "finished_unix_s": run_finished,
        },
        "tasks": bundle_tasks,
    }
    output_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", type=Path)
    parser.add_argument("--policy-id", required=True)
    parser.add_argument("--policy-path", type=Path, required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--adapter-id", required=True)
    parser.add_argument("--adapter-version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifacts-dir", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--timeout-s", type=float, default=1800.0)
    parser.add_argument("--cwd", type=Path)
    parser.add_argument(
        "adapter_command",
        nargs=argparse.REMAINDER,
        help="adapter executable and arguments, usually after --",
    )
    args = parser.parse_args()
    command = list(args.adapter_command)
    if command and command[0] == "--":
        command = command[1:]

    try:
        result = run_suite(
            suite_path=args.suite,
            policy_id=args.policy_id,
            policy_path=args.policy_path,
            model_id=args.model_id,
            adapter_id=args.adapter_id,
            adapter_version=args.adapter_version,
            adapter_command=command,
            output_path=args.output,
            artifacts_dir=args.artifacts_dir,
            run_id=args.run_id,
            timeout_s=args.timeout_s,
            cwd=args.cwd,
        )
    except RunnerError as exc:
        print(f"Sloar eval runner: FAILED: {exc}", file=sys.stderr)
        return 2

    print(
        f"Sloar eval run complete: {result['run_id']} "
        f"tasks={len(result['tasks'])} output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
