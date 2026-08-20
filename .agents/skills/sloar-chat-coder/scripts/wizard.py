#!/usr/bin/env python3
"""Beginner-facing Sloar local readiness wizard.

This script intentionally limits itself to evidence visible from the local
filesystem/terminal. ChatGPT/Codex plugin/app/tool availability must be
resolved by the agent from its actual current tool inventory.
"""
import argparse
import json
from pathlib import Path

from doctor import inspect as inspect_local


def state(value: bool, *, missing="missing"):
    return "ready" if value else missing


def build(repo: Path):
    local = inspect_local(repo)
    git_ok = bool(local["git"].get("is_worktree"))
    installed = bool(local.get("sloar_installed"))
    execution = bool(local["tools"]["python3"]["available"])
    dirty = bool(local["git"].get("dirty")) if git_ok else None

    recommendations = []
    if not git_ok:
        recommendations.append("Open or initialize the target Git repository before repository engineering.")
    if not installed:
        recommendations.append("Install Sloar into this repository with install.py before using the protocol.")
    if not execution:
        recommendations.append("Use an agent/surface with code execution for implementation and verification claims.")
    if not recommendations:
        recommendations.append("Local side is ready. Ask the agent to resolve hosted GitHub/CI/browser capabilities from the current session and begin RECOVER.")

    return {
        "schema": 1,
        "sloar_version": "0.3.0",
        "repository": {
            "state": state(git_ok),
            "installed": installed,
            "dirty": dirty,
            "head": local["git"].get("head"),
            "tree": local["git"].get("tree"),
            "branch": local["git"].get("branch"),
            "origin": local["git"].get("origin"),
        },
        "execution": {"state": state(execution), "python3": local["tools"]["python3"]["available"]},
        "hosted": {
            "state": "unknown",
            "repository_read": "unknown",
            "repository_write": "unknown",
            "ci": "unknown",
            "browser": "unknown",
            "plugin_or_app_state": "unknown",
            "reason": "not-detectable-locally; agent must inspect its current tool inventory",
        },
        "next": recommendations[0],
        "recommendations": recommendations,
    }


def render(data):
    repo = data["repository"]
    hosted = data["hosted"]
    lines = [
        "Sloar readiness",
        f"Repository: {repo['state']}" + (f" ({repo['branch']})" if repo.get("branch") else ""),
        f"Sloar skill: {'ready' if repo['installed'] else 'missing'}",
        f"Execution: {data['execution']['state']}",
        "GitHub read/write: unknown (agent check)",
        "CI/browser: unknown (agent check)",
        f"Next: {data['next']}",
    ]
    if repo.get("dirty"):
        lines.insert(2, "Working tree: dirty (preserve/identify changes before modification)")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Show beginner-friendly Sloar local readiness and next action.")
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="Emit the full machine-readable readiness report")
    parser.add_argument("--output", help="Also write the JSON readiness report to this path")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"directory does not exist: {repo}")
    data = build(repo)
    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2) if args.json else render(data))


if __name__ == "__main__":
    main()
