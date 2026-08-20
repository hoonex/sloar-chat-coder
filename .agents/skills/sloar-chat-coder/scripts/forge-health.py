#!/usr/bin/env python3
"""Classify local Git vs hosted-forge health without retry loops.

Default mode is local-only and makes no network requests. Use --probe when a
bounded remote health check is useful. A probe runs each relevant remote layer
at most once.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def run(cmd, cwd: Path, timeout=8):
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except OSError as exc:
        return 127, "", str(exc)


def origin_host(origin: str | None):
    if not origin:
        return None
    text = origin.strip()
    if text.startswith("git@") and ":" in text:
        return text.split("@", 1)[1].split(":", 1)[0].lower()
    if "://" in text:
        return (urlparse(text).hostname or "").lower() or None
    return None


def github_slug(origin: str | None):
    if not origin or origin_host(origin) != "github.com":
        return None
    text = origin.strip()
    if text.startswith("git@github.com:"):
        path = text.split(":", 1)[1]
    else:
        path = urlparse(text).path.lstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = [p for p in path.split("/") if p]
    return "/".join(parts[:2]) if len(parts) >= 2 else None


def inspect(repo: Path, probe=False):
    git = shutil.which("git")
    if not git:
        return {
            "schema": 1,
            "local": {"state": "BLOCKED", "reason": "git missing"},
            "remote": {"state": "unknown"},
            "publication": "BLOCKED",
        }

    rc, _, _ = run([git, "rev-parse", "--is-inside-work-tree"], repo)
    if rc != 0:
        return {
            "schema": 1,
            "local": {"state": "BLOCKED", "reason": "not a git worktree"},
            "remote": {"state": "unknown"},
            "publication": "BLOCKED",
        }

    _, head, _ = run([git, "rev-parse", "HEAD"], repo)
    _, tree, _ = run([git, "rev-parse", "HEAD^{tree}"], repo)
    _, status, _ = run([git, "status", "--porcelain"], repo)
    _, origin, _ = run([git, "remote", "get-url", "origin"], repo)
    host = origin_host(origin)

    data = {
        "schema": 1,
        "local": {
            "state": "LOCAL_READY" if head and tree else "BLOCKED",
            "head": head or None,
            "tree": tree or None,
            "dirty": bool(status),
        },
        "remote": {
            "state": "unknown" if not probe else "REMOTE_HEALTHY",
            "origin": origin or None,
            "host": host,
            "git_transport": "unknown",
            "forge_api": "unknown" if host else "not_applicable",
            "evidence": [],
        },
        "publication": "unknown" if not probe else "ready",
    }

    if not probe:
        return data

    if not origin:
        data["remote"].update({"state": "REMOTE_DEGRADED", "git_transport": "missing", "forge_api": "not_applicable"})
        data["remote"]["evidence"].append("origin remote missing")
        data["publication"] = "PUBLICATION_BLOCKED"
        return data

    rc, out, err = run([git, "ls-remote", "--exit-code", origin, "HEAD"], repo)
    if rc == 0:
        data["remote"]["git_transport"] = "healthy"
        data["remote"]["evidence"].append("git ls-remote origin HEAD: success")
    else:
        data["remote"]["git_transport"] = "degraded"
        data["remote"]["state"] = "REMOTE_DEGRADED"
        data["publication"] = "PUBLICATION_BLOCKED"
        data["remote"]["evidence"].append(f"git ls-remote origin HEAD: rc={rc} {err or out}".strip())

    slug = github_slug(origin)
    gh = shutil.which("gh")
    if slug and gh:
        auth_rc, _, _ = run([gh, "auth", "status"], repo)
        if auth_rc == 0:
            api_rc, _, api_err = run([gh, "api", f"repos/{slug}", "--silent"], repo)
            if api_rc == 0:
                data["remote"]["forge_api"] = "healthy"
                data["remote"]["evidence"].append("GitHub API repository probe: success")
            else:
                data["remote"]["forge_api"] = "degraded"
                data["remote"]["state"] = "REMOTE_DEGRADED"
                data["publication"] = "PUBLICATION_BLOCKED"
                data["remote"]["evidence"].append(f"GitHub API repository probe: rc={api_rc} {api_err}".strip())
        else:
            data["remote"]["forge_api"] = "unknown"
            data["remote"]["evidence"].append("GitHub CLI is not authenticated; API layer not probed")
    elif slug:
        data["remote"]["forge_api"] = "unknown"
        data["remote"]["evidence"].append("GitHub CLI unavailable; API layer not probed")
    elif host:
        data["remote"]["forge_api"] = "unknown"
        data["remote"]["evidence"].append("generic forge API probe is not configured")

    if data["remote"]["state"] == "REMOTE_HEALTHY" and data["remote"]["git_transport"] != "healthy":
        data["remote"]["state"] = "REMOTE_DEGRADED"
        data["publication"] = "PUBLICATION_BLOCKED"
    return data


def render(data):
    local = data["local"]
    remote = data["remote"]
    lines = [
        "Sloar forge health",
        f"Local: {local['state']}",
        f"Git transport: {remote.get('git_transport', 'unknown')}",
        f"Forge API: {remote.get('forge_api', 'unknown')}",
        f"Remote: {remote.get('state', 'unknown')}",
        f"Publication: {data['publication']}",
    ]
    if remote.get("evidence"):
        lines.append("Evidence:")
        lines.extend(f"- {item}" for item in remote["evidence"])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Separate local Git readiness from hosted-forge health.")
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--probe", action="store_true", help="Run one bounded Git transport / supported forge API probe. No retries.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        raise SystemExit(f"directory does not exist: {repo}")
    data = inspect(repo, probe=args.probe)
    print(json.dumps(data, indent=2) if args.json else render(data))


if __name__ == "__main__":
    main()
