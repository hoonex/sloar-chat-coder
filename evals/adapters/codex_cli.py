#!/usr/bin/env python3
"""Codex CLI adapter for Sloar Evals.

Each invocation evaluates exactly one task. The outer ``evals/run.py`` process
supplies task/policy/model identity through SLOAR_EVAL_* environment variables.
This adapter materializes an isolated repository, runs ``codex exec`` once, then
runs objective acceptance and regression checks and writes ``result.json``.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence


class AdapterError(RuntimeError):
    pass


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise AdapterError(f"missing required environment variable {name}")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise AdapterError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise AdapterError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AdapterError(f"{path}: root must be an object")
    return value


def _command(value: Any, *, name: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise AdapterError(f"{name}.command must be a non-empty string array")
    return list(value)


def _run_checked(command: Sequence[str], *, cwd: Path | None = None, timeout_s: float = 120.0) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AdapterError(f"command timed out after {timeout_s:g}s: {shlex.join(command)}") from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        suffix = f": {detail[:1000]}" if detail else ""
        raise AdapterError(f"command failed ({completed.returncode}): {shlex.join(command)}{suffix}")
    return completed


def _git(worktree: Path, *args: str, timeout_s: float = 120.0) -> str:
    return _run_checked(["git", "-C", str(worktree), *args], timeout_s=timeout_s).stdout.strip()


def _resolve_fixture(path_value: str, adapter_cwd: Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = adapter_cwd / path
    path = path.resolve()
    if not path.is_dir():
        raise AdapterError(f"fixture_path is not a directory: {path}")
    return path


def _materialize_repository(task: dict[str, Any], *, output_dir: Path, adapter_cwd: Path) -> Path:
    repository = task.get("repository")
    if not isinstance(repository, dict):
        raise AdapterError("task.repository must be an object")

    worktree = output_dir / "worktree"
    if worktree.exists():
        if any(worktree.iterdir()):
            raise AdapterError(f"worktree already exists and is not empty: {worktree}")
    else:
        worktree.mkdir(parents=True)

    if repository.get("fixture_path"):
        fixture = _resolve_fixture(str(repository["fixture_path"]), adapter_cwd)
        shutil.copytree(
            fixture,
            worktree,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )
        seed_patch = task.get("seed_patch")
        if seed_patch:
            if not isinstance(seed_patch, str):
                raise AdapterError("task.seed_patch must be a string")
            patch_file = output_dir / "seed.patch"
            patch_file.write_text(seed_patch, encoding="utf-8")
            _run_checked(["git", "apply", "--whitespace=nowarn", str(patch_file)], cwd=worktree)
        _run_checked(["git", "init", "-q"], cwd=worktree)
        _run_checked(["git", "config", "user.email", "sloar-eval@example.invalid"], cwd=worktree)
        _run_checked(["git", "config", "user.name", "Sloar Eval"], cwd=worktree)
        _run_checked(["git", "add", "-A"], cwd=worktree)
        _run_checked(["git", "commit", "-qm", "eval baseline"], cwd=worktree)
        return worktree

    source = repository.get("url") or repository.get("path")
    commit = str(repository.get("commit") or "").strip()
    if not source or not commit:
        raise AdapterError("repository requires fixture_path or source url/path plus exact commit")
    if len(commit) < 7:
        raise AdapterError("repository.commit must be an immutable commit id")
    source_value = str(source)
    if repository.get("path"):
        local = Path(source_value)
        if not local.is_absolute():
            local = adapter_cwd / local
        source_value = str(local.resolve())
    shutil.rmtree(worktree)
    _run_checked(["git", "clone", "-q", "--no-checkout", source_value, str(worktree)], timeout_s=300)
    _git(worktree, "checkout", "-q", "--detach", commit, timeout_s=120)
    observed = _git(worktree, "rev-parse", "HEAD")
    expected = _run_checked(["git", "-C", str(worktree), "rev-parse", f"{commit}^{{commit}}"], timeout_s=120).stdout.strip()
    if observed != expected:
        raise AdapterError(f"repository identity mismatch: expected {expected}, got {observed}")
    return worktree


def _resolve_policy_entrypoint(policy_path: Path) -> Path:
    if policy_path.is_file():
        return policy_path
    candidates = [
        policy_path / "SKILL.md",
        policy_path / "sloar-chat-coder" / "SKILL.md",
        policy_path / ".agents" / "skills" / "sloar-chat-coder" / "SKILL.md",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise AdapterError(f"cannot locate Sloar SKILL.md under policy path: {policy_path}")


def _final_schema(path: Path) -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["status", "summary"],
        "properties": {
            "status": {"type": "string", "enum": ["completed", "blocked", "failed"]},
            "summary": {"type": "string"},
        },
    }
    path.write_text(json.dumps(schema, indent=2), encoding="utf-8")


def _build_prompt(task: dict[str, Any], *, policy_entrypoint: Path) -> str:
    prompt = str(task.get("prompt") or "").strip()
    if not prompt:
        raise AdapterError("task.prompt must be a non-empty string")
    return (
        "You are running one controlled Sloar coding evaluation.\n"
        f"Before changing the repository, read and follow the supplied Sloar policy snapshot at {policy_entrypoint}.\n"
        "Treat that snapshot as the Sloar authority for this run. Do not search for or compare against other Sloar policy versions.\n"
        "Work only in the provided repository worktree. Use repository-defined validation where useful.\n"
        "At the end, set status=completed only if you believe the requested task is actually complete; otherwise use blocked or failed.\n\n"
        "Task:\n"
        f"{prompt}\n"
    )


def build_codex_command(
    *,
    codex_bin: str,
    model_id: str,
    worktree: Path,
    policy_path: Path,
    schema_file: Path,
    last_message_file: Path,
    reasoning_effort: str,
) -> list[str]:
    return [
        codex_bin,
        "exec",
        "--json",
        "--model",
        model_id,
        "--sandbox",
        "workspace-write",
        "--cd",
        str(worktree),
        "--add-dir",
        str(policy_path),
        "--output-schema",
        str(schema_file),
        "--output-last-message",
        str(last_message_file),
        "--config",
        f'model_reasoning_effort="{reasoning_effort}"',
        "--config",
        'approval_policy="never"',
        "--config",
        'web_search="disabled"',
        "--config",
        "sandbox_workspace_write.network_access=false",
    ]


def _terminate_process(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    except ProcessLookupError:
        pass


def _run_codex(command: Sequence[str], *, prompt: str, trajectory_file: Path, stderr_file: Path, timeout_s: float) -> None:
    kwargs: dict[str, Any] = {
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }
    if os.name == "posix":
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(list(command), **kwargs)
    try:
        stdout, stderr = proc.communicate(prompt, timeout=timeout_s)
    except subprocess.TimeoutExpired as exc:
        _terminate_process(proc)
        stdout, stderr = proc.communicate()
        trajectory_file.write_text(stdout or "", encoding="utf-8")
        stderr_file.write_text(stderr or "", encoding="utf-8")
        raise AdapterError(f"codex exec timed out after {timeout_s:g}s") from exc
    trajectory_file.write_text(stdout or "", encoding="utf-8")
    stderr_file.write_text(stderr or "", encoding="utf-8")
    if proc.returncode != 0:
        detail = (stderr or stdout or "").strip()
        raise AdapterError(f"codex exec failed ({proc.returncode}): {detail[-1500:]}")


def _verification_spec(task: dict[str, Any], name: str) -> tuple[list[str], float]:
    verification = task.get("verification")
    if not isinstance(verification, dict):
        raise AdapterError("task.verification must be an object")
    spec = verification.get(name)
    if not isinstance(spec, dict):
        raise AdapterError(f"task.verification.{name} must be an object")
    command = _command(spec.get("command"), name=f"verification.{name}")
    timeout_s = float(spec.get("timeout_s", 300))
    if timeout_s <= 0:
        raise AdapterError(f"verification.{name}.timeout_s must be > 0")
    return command, timeout_s


def _run_verifier(task: dict[str, Any], name: str, *, worktree: Path, output_dir: Path) -> bool:
    command, timeout_s = _verification_spec(task, name)
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command,
            cwd=str(worktree),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        completed = None
        timed_out = True
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode(errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode(errors="replace")
    else:
        stdout = completed.stdout
        stderr = completed.stderr
    elapsed = time.perf_counter() - started
    (output_dir / f"verify-{name}.stdout.log").write_text(stdout or "", encoding="utf-8")
    (output_dir / f"verify-{name}.stderr.log").write_text(stderr or "", encoding="utf-8")
    (output_dir / f"verify-{name}.json").write_text(
        json.dumps(
            {
                "command": command,
                "timeout_s": timeout_s,
                "elapsed_s": elapsed,
                "timed_out": timed_out,
                "returncode": None if completed is None else completed.returncode,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return bool(completed is not None and completed.returncode == 0)


def evaluate_task(*, codex_bin: str, reasoning_effort: str, codex_timeout_s: float, adapter_cwd: Path | None = None) -> dict[str, Any]:
    task_id = _required_env("SLOAR_EVAL_TASK_ID")
    task_file = Path(_required_env("SLOAR_EVAL_TASK_FILE")).resolve()
    policy_path = Path(_required_env("SLOAR_EVAL_POLICY_PATH")).resolve()
    model_id = _required_env("SLOAR_EVAL_MODEL_ID")
    output_dir = Path(_required_env("SLOAR_EVAL_OUTPUT_DIR")).resolve()
    result_file = Path(_required_env("SLOAR_EVAL_RESULT_FILE")).resolve()
    trajectory_file = Path(_required_env("SLOAR_EVAL_TRAJECTORY_FILE")).resolve()
    adapter_cwd = (adapter_cwd or Path.cwd()).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    task = _load_json(task_file)
    if str(task.get("id") or "") != task_id:
        raise AdapterError(f"task id mismatch: env={task_id!r} file={task.get('id')!r}")
    if codex_timeout_s <= 0:
        raise AdapterError("codex timeout must be > 0")

    worktree = _materialize_repository(task, output_dir=output_dir, adapter_cwd=adapter_cwd)
    policy_entrypoint = _resolve_policy_entrypoint(policy_path)
    schema_file = output_dir / "final.schema.json"
    last_message_file = output_dir / "final.json"
    codex_stderr_file = output_dir / "codex.stderr.log"
    _final_schema(schema_file)
    prompt = _build_prompt(task, policy_entrypoint=policy_entrypoint)
    (output_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    command = build_codex_command(
        codex_bin=codex_bin,
        model_id=model_id,
        worktree=worktree,
        policy_path=policy_path,
        schema_file=schema_file,
        last_message_file=last_message_file,
        reasoning_effort=reasoning_effort,
    )
    (output_dir / "codex-command.json").write_text(json.dumps(command, indent=2), encoding="utf-8")
    _run_codex(command, prompt=prompt, trajectory_file=trajectory_file, stderr_file=codex_stderr_file, timeout_s=codex_timeout_s)

    final = _load_json(last_message_file)
    status = str(final.get("status") or "")
    if status not in {"completed", "blocked", "failed"}:
        raise AdapterError(f"invalid final status: {status!r}")
    if not isinstance(final.get("summary"), str):
        raise AdapterError("final summary must be a string")

    acceptance_pass = _run_verifier(task, "acceptance", worktree=worktree, output_dir=output_dir)
    regression_pass = _run_verifier(task, "regression", worktree=worktree, output_dir=output_dir)
    patch = _run_checked(["git", "diff", "--binary", "HEAD"], cwd=worktree).stdout
    (output_dir / "patch.diff").write_text(patch, encoding="utf-8")

    metrics = {
        "success": 1.0 if acceptance_pass else 0.0,
        "regression": 0.0 if regression_pass else 1.0,
        "false_completion": 1.0 if status == "completed" and not acceptance_pass else 0.0,
    }
    result = {
        "schema": 1,
        "task_id": task_id,
        "metrics": metrics,
        "agent": {
            "status": status,
            "summary": final["summary"],
            "model_id": model_id,
            "reasoning_effort": reasoning_effort,
        },
    }
    result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-bin", default=os.environ.get("CODEX_BIN", "codex"))
    parser.add_argument("--reasoning-effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--codex-timeout-s", type=float, default=1500.0)
    args = parser.parse_args()
    try:
        result = evaluate_task(
            codex_bin=args.codex_bin,
            reasoning_effort=args.reasoning_effort,
            codex_timeout_s=args.codex_timeout_s,
        )
    except (AdapterError, OSError, ValueError) as exc:
        print(f"Sloar Codex eval adapter: FAILED: {exc}", file=sys.stderr)
        return 2
    print(f"Sloar Codex eval task complete: {result['task_id']} success={result['metrics']['success']:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())