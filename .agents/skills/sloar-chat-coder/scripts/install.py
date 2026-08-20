#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

BEGIN = "<!-- sloar-chat-coder:begin -->"
END = "<!-- sloar-chat-coder:end -->"
BLOCK = f"""{BEGIN}\n## Sloar Chat Coder\n\nWhen repository development is requested from a chat/agent environment, read `.agents/skills/sloar-chat-coder/SKILL.md` before repository work. Sloar governs continuity, exact state, capability escalation, failure handling, publication safety, and evidence; the repository still defines engineering method.\n{END}\n"""


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def copy_skill(target: Path, force: bool, dry_run: bool) -> str:
    source = skill_root()
    dest = target / ".agents" / "skills" / "sloar-chat-coder"
    if dest.exists() and not force:
        if (dest / "SKILL.md").exists() and (dest / "SKILL.md").read_bytes() == (source / "SKILL.md").read_bytes():
            return "skill already installed"
        raise SystemExit(f"existing Sloar installation differs: {dest} (use --force to replace)")
    if dry_run:
        return f"would copy {source} -> {dest}"
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, dest)
    return f"installed skill -> {dest}"


def update_agents(target: Path, dry_run: bool) -> str:
    path = target / "AGENTS.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if BEGIN in existing and END in existing:
        return "AGENTS.md already wired"
    if BEGIN in existing or END in existing:
        raise SystemExit("AGENTS.md contains an incomplete Sloar marker block; fix it manually before installing")
    updated = existing.rstrip()
    if updated:
        updated += "\n\n"
    updated += BLOCK
    if dry_run:
        return f"would add Sloar block -> {path}"
    path.write_text(updated, encoding="utf-8")
    return f"wired -> {path}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Sloar Chat Coder into a target repository.")
    parser.add_argument("--target", required=True, help="Target repository/workspace directory")
    parser.add_argument("--dry-run", action="store_true", help="Show intended changes without writing")
    parser.add_argument("--no-agents", action="store_true", help="Do not create/update target AGENTS.md")
    parser.add_argument("--force", action="store_true", help="Replace an existing different Sloar skill directory")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists() or not target.is_dir():
        raise SystemExit(f"target directory does not exist: {target}")

    print(copy_skill(target, args.force, args.dry_run))
    if not args.no_agents:
        print(update_agents(target, args.dry_run))
    print("next: ask your agent to run Sloar first-run capability check before repository modification")


if __name__ == "__main__":
    main()
