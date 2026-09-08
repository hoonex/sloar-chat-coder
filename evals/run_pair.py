#!/usr/bin/env python3
"""Run one Sloar policy A/B evaluation through the Codex CLI adapter."""
from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.compare import EvalFormatError, compare_runs
from evals.run import RunnerError, run_suite


class PairError(RuntimeError):
    pass


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise PairError((completed.stderr or completed.stdout).strip())
    return completed.stdout.strip()


def _policy_archive(repo: Path, ref: str, destination: Path) -> tuple[str, Path]:
    commit = _git(repo, "rev-parse", f"{ref}^{{commit}}")
    completed = subprocess.run(
        ["git", "-C", str(repo), "archive", "--format=tar", commit, ".agents/skills"],
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise PairError(completed.stderr.decode(errors="replace").strip())
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(completed.stdout), mode="r:") as archive:
        for member in archive.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise PairError(f"unsafe path in git archive: {member.name}")
        archive.extractall(destination)
    policy = destination / ".agents" / "skills"
    if not (policy / "sloar-chat-coder" / "SKILL.md").is_file():
        raise PairError(f"{ref}: archived policy has no sloar-chat-coder/SKILL.md")
    return commit, policy


def _replace_policy(source: Path, shared: Path) -> None:
    if shared.exists():
        shutil.rmtree(shared)
    shutil.copytree(source, shared)


def run_pair(
    *,
    repo_root: Path,
    suite: Path,
    stable_ref: str,
    candidate_ref: str,
    model_id: str,
    reasoning_effort: str,
    codex_bin: str,
    output_dir: Path,
    task_timeout_s: float,
    codex_timeout_s: float,
) -> dict:
    repo_root = repo_root.resolve()
    suite = suite.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    adapter = (repo_root / "evals" / "adapters" / "codex_cli.py").resolve()
    if not adapter.is_file():
        raise PairError(f"missing Codex eval adapter: {adapter}")

    with tempfile.TemporaryDirectory(prefix="sloar-eval-policy-") as temp_name:
        temp = Path(temp_name)
        stable_commit, stable_policy = _policy_archive(repo_root, stable_ref, temp / "stable")
        candidate_commit, candidate_policy = _policy_archive(repo_root, candidate_ref, temp / "candidate")
        shared_policy = output_dir / ".active-policy"

        adapter_command = [
            sys.executable,
            str(adapter),
            "--codex-bin",
            codex_bin,
            "--reasoning-effort",
            reasoning_effort,
            "--codex-timeout-s",
            str(codex_timeout_s),
        ]

        _replace_policy(stable_policy, shared_policy)
        baseline = run_suite(
            suite_path=suite,
            policy_id=f"git:{stable_commit}",
            policy_path=shared_policy,
            model_id=model_id,
            adapter_id="codex-cli",
            adapter_version="1",
            adapter_command=adapter_command,
            output_path=output_dir / "baseline.json",
            artifacts_dir=output_dir / "baseline-artifacts",
            timeout_s=task_timeout_s,
            cwd=repo_root,
        )

        _replace_policy(candidate_policy, shared_policy)
        candidate = run_suite(
            suite_path=suite,
            policy_id=f"git:{candidate_commit}",
            policy_path=shared_policy,
            model_id=model_id,
            adapter_id="codex-cli",
            adapter_version="1",
            adapter_command=adapter_command,
            output_path=output_dir / "candidate.json",
            artifacts_dir=output_dir / "candidate-artifacts",
            timeout_s=task_timeout_s,
            cwd=repo_root,
        )
        shutil.rmtree(shared_policy, ignore_errors=True)

    comparison = compare_runs(baseline, candidate)
    result = {
        "schema": 1,
        "stable_ref": stable_ref,
        "stable_commit": stable_commit,
        "candidate_ref": candidate_ref,
        "candidate_commit": candidate_commit,
        "model_id": model_id,
        "reasoning_effort": reasoning_effort,
        "comparison": comparison,
    }
    (output_dir / "comparison.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--stable-ref", default="main")
    parser.add_argument("--candidate-ref", default="HEAD")
    parser.add_argument("--model-id", default="gpt-5.6-sol")
    parser.add_argument(
        "--reasoning-effort",
        default="medium",
        choices=["low", "medium", "high", "xhigh", "max"],
        help="reasoning used for both sides of the A/B run; medium is the fast dev default, use high for promotion evidence",
    )
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--output-dir", type=Path, default=Path(".sloar-evals/latest"))
    parser.add_argument("--task-timeout-s", type=float, default=1800.0)
    parser.add_argument("--codex-timeout-s", type=float, default=1500.0)
    parser.add_argument("--require-promote", action="store_true")
    args = parser.parse_args()
    try:
        result = run_pair(
            repo_root=args.repo_root,
            suite=args.suite,
            stable_ref=args.stable_ref,
            candidate_ref=args.candidate_ref,
            model_id=args.model_id,
            reasoning_effort=args.reasoning_effort,
            codex_bin=args.codex_bin,
            output_dir=args.output_dir,
            task_timeout_s=args.task_timeout_s,
            codex_timeout_s=args.codex_timeout_s,
        )
    except (PairError, RunnerError, EvalFormatError, OSError, ValueError) as exc:
        print(f"Sloar Codex A/B eval: FAILED: {exc}", file=sys.stderr)
        return 2

    comparison = result["comparison"]
    delta = comparison["deltas"]
    print(
        f"Sloar Codex A/B eval: {comparison['decision']} "
        f"success={delta['success_rate']:+.3f} "
        f"regression={delta['regression_rate']:+.3f} "
        f"false_completion={delta['false_completion_rate']:+.3f}"
    )
    print(f"Evidence: {(args.output_dir / 'comparison.json').resolve()}")
    if args.require_promote and comparison["decision"] != "PROMOTE":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
