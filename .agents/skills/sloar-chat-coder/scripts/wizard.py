#!/usr/bin/env python3
"""Beginner-facing Sloar local readiness wizard.

This script intentionally limits itself to evidence visible from the local
filesystem/terminal. ChatGPT/Codex plugin/app/tool availability and hosted
forge health must be resolved by the agent from its actual current tool
inventory unless the user explicitly runs a bounded forge probe or classifies
an already-observed remote failure.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from doctor import inspect as inspect_local


def state(value: bool, *, missing="missing"):
    return "ready" if value else missing


def read_small_text(path: Path, limit=200_000):
    try:
        if path.is_file() and path.stat().st_size <= limit:
            return path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        pass
    return ""


def origin_host(origin: str | None):
    if not origin:
        return ""
    text = origin.strip()
    if text.startswith("git@") and ":" in text:
        return text.split("@", 1)[1].split(":", 1)[0].lower()
    if "://" in text:
        return (urlparse(text).hostname or "").lower()
    return ""


def detect_connections(repo: Path, origin: str | None):
    """Recommend connections from durable repository signals only.

    Detection never means the connection is installed, authenticated, or
    sufficiently authorized in the current ChatGPT/Codex session.
    """
    package = read_small_text(repo / "package.json")
    pyproject = read_small_text(repo / "pyproject.toml")
    requirements = read_small_text(repo / "requirements.txt")
    host = origin_host(origin)
    rows = []

    def add(id_, name, level, why, evidence):
        rows.append({
            "id": id_,
            "name": name,
            "level": level,
            "status": "unknown",
            "connect_by_user": True,
            "why": why,
            "evidence": evidence,
        })

    if host == "github.com":
        add(
            "github",
            "GitHub",
            "baseline_for_remote_workflow",
            "Recommended when the user wants ChatGPT/Codex to read/write the remote repository, create PRs, inspect CI, or publish through GitHub.",
            ["origin host: github.com"],
        )

    vercel_evidence = []
    if (repo / "vercel.json").is_file(): vercel_evidence.append("vercel.json")
    if (repo / ".vercel" / "project.json").is_file(): vercel_evidence.append(".vercel/project.json")
    if '"vercel"' in package or "@vercel/" in package: vercel_evidence.append("package.json")
    if vercel_evidence:
        add("vercel", "Vercel", "recommended", "Recommended for deployment/project inspection when this repository is deployed on Vercel.", vercel_evidence)

    supabase_evidence = []
    if (repo / "supabase").is_dir(): supabase_evidence.append("supabase/")
    if "@supabase/" in package or '"supabase"' in package: supabase_evidence.append("package.json")
    if "supabase" in pyproject or "supabase" in requirements: supabase_evidence.append("Python dependency metadata")
    if supabase_evidence:
        add("supabase", "Supabase", "recommended", "Recommended for database, Auth, Edge Functions, migrations, and project-state work when Supabase is part of the repository.", supabase_evidence)

    netlify_evidence = []
    if (repo / "netlify.toml").is_file(): netlify_evidence.append("netlify.toml")
    if (repo / ".netlify").is_dir(): netlify_evidence.append(".netlify/")
    if '"netlify"' in package or "@netlify/" in package: netlify_evidence.append("package.json")
    if netlify_evidence:
        add("netlify", "Netlify", "recommended", "Recommended for deploy/build/project operations when this repository uses Netlify.", netlify_evidence)

    openai_evidence = []
    if '"openai"' in package or "@openai/" in package: openai_evidence.append("package.json")
    if "openai" in pyproject or "openai" in requirements: openai_evidence.append("Python dependency metadata")
    if openai_evidence:
        add("openai-platform", "OpenAI Platform", "recommended_when_api_work_is_requested", "Recommended when the task needs OpenAI API keys, project configuration, or OpenAI-backed runtime setup.", openai_evidence)

    return rows


def build(repo: Path):
    local = inspect_local(repo)
    git_ok = bool(local["git"].get("is_worktree"))
    installed = bool(local.get("sloar_installed"))
    execution = bool(local["tools"]["python3"]["available"])
    dirty = bool(local["git"].get("dirty")) if git_ok else None
    origin = local["git"].get("origin")
    connections = detect_connections(repo, origin)

    recommendations = []
    if not git_ok:
        recommendations.append("Open or initialize the target Git repository before repository engineering.")
    if not installed:
        recommendations.append("Install Sloar into this repository with install.py before using the protocol.")
    if not execution:
        recommendations.append("Use an agent/surface with code execution for implementation and verification claims.")
    if not recommendations:
        recommendations.append("Local side is ready. Review the suggested connections, connect only the services you want the agent to operate, then let the agent verify actual capabilities and begin RECOVER.")

    return {
        "schema": 2,
        "sloar_version": "0.6.1",
        "repository": {
            "state": state(git_ok),
            "installed": installed,
            "dirty": dirty,
            "head": local["git"].get("head"),
            "tree": local["git"].get("tree"),
            "branch": local["git"].get("branch"),
            "origin": origin,
        },
        "execution": {"state": state(execution), "python3": local["tools"]["python3"]["available"]},
        "hosted": {
            "state": "unknown",
            "repository_read": "unknown",
            "repository_write": "unknown",
            "ci": "unknown",
            "browser": "unknown",
            "plugin_or_app_state": "unknown",
            "forge_health": "unknown",
            "reason": "not-detectable-locally; user connects external services explicitly and the agent must verify the capabilities exposed in the current session",
        },
        "connections": {
            "policy": "recommend from repository signals; user connects manually; never infer installed/authenticated from detection",
            "items": connections,
        },
        "resilience": {
            "local_status": "LOCAL_READY" if git_ok and execution else "BLOCKED",
            "remote_status": "unknown",
            "remote_status_values": ["REMOTE_HEALTHY", "REMOTE_PARTIAL", "REMOTE_DEGRADED", "unknown"],
            "publication": "unknown",
            "probe_command": "python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py . --probe --json",
            "classify_command": "python3 .agents/skills/sloar-chat-coder/scripts/forge-health.py --classify-file /path/to/error.log --json",
        },
        "continuity": {
            "turn_state_helper": ".agents/skills/sloar-chat-coder/scripts/turn-state.py",
            "stuck_response_recovery": "host-dependent; Sloar preserves terminal/interrupted engineering state but cannot control the chat host spinner",
            "turn_terminalization": "bounded; a RED/pending required gate changes terminal status instead of allowing indefinite self-extension",
        },
        "next": recommendations[0],
        "recommendations": recommendations,
    }


def render(data):
    repo = data["repository"]
    connections = data.get("connections", {}).get("items", [])
    connection_text = ", ".join(f"{item['name']} ({item['level']})" for item in connections) or "none detected from repository signals"
    lines = [
        "Sloar readiness",
        f"Repository: {repo['state']}" + (f" ({repo['branch']})" if repo.get("branch") else ""),
        f"Sloar skill: {'ready' if repo['installed'] else 'missing'}",
        f"Execution: {data['execution']['state']}",
        "Hosted connections: unknown until the user connects them and the agent verifies actual tools",
        f"Suggested connections: {connection_text}",
        "Forge health/capability: unknown (probe or classify observed failure only when needed)",
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
