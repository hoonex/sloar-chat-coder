#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

BEGIN = "<!-- sloar-chat-coder:begin -->"
END = "<!-- sloar-chat-coder:end -->"
BLOCK = f"""{BEGIN}\n## Sloar Chat Coder\n\nWhen repository development is requested from a chat/agent environment, read `.agents/skills/sloar-chat-coder/SKILL.md` before repository work. Sloar governs continuity, exact state, capability escalation, failure handling, publication safety, and evidence; the repository still defines engineering method. When Apple-style web interaction/design is explicitly requested and `.agents/skills/apple-web-design/SKILL.md` exists, read that companion only after the target repository guidance; it is opt-in and never overrides the repository's product/design rules.\n{END}\n"""

BUNDLED_SKILLS = ("sloar-chat-coder", "apple-web-design")
IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc")


def skills_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def source_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        yield path


def skill_matches(source: Path, dest: Path) -> bool:
    if not dest.is_dir():
        return False
    for src in source_files(source):
        rel = src.relative_to(source)
        dst = dest / rel
        if not dst.is_file() or dst.read_bytes() != src.read_bytes():
            return False
    return True


def copy_bundled_skills(target: Path, force: bool, dry_run: bool) -> list[str]:
    root = skills_root()
    messages = []
    for name in BUNDLED_SKILLS:
        source = root / name
        if not (source / "SKILL.md").is_file():
            raise SystemExit(f"bundled skill source is missing: {source}")
        dest = target / ".agents" / "skills" / name
        if dest.exists() and not force:
            if skill_matches(source, dest):
                messages.append(f"skill already installed -> {dest}")
                continue
            raise SystemExit(f"existing {name} installation differs: {dest} (use --force to replace bundled skills)")
        if dry_run:
            messages.append(f"would copy {source} -> {dest}")
            continue
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, dest, ignore=IGNORE_PATTERNS)
        messages.append(f"installed skill -> {dest}")
    return messages


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
    parser = argparse.ArgumentParser(description="Install Sloar Chat Coder and bundled companion skills into a target repository.")
    parser.add_argument("--target", required=True, help="Target repository/workspace directory")
    parser.add_argument("--dry-run", action="store_true", help="Show intended changes without writing")
    parser.add_argument("--no-agents", action="store_true", help="Do not create/update target AGENTS.md")
    parser.add_argument("--force", action="store_true", help="Replace existing different bundled skill directories")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists() or not target.is_dir():
        raise SystemExit(f"target directory does not exist: {target}")

    for message in copy_bundled_skills(target, args.force, args.dry_run):
        print(message)
    if not args.no_agents:
        print(update_agents(target, args.dry_run))
    print("next: ask your agent to run Sloar first-run capability check before repository modification")


if __name__ == "__main__":
    main()
