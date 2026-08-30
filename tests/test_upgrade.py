import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / ".agents/skills/sloar-chat-coder/scripts/install.py"
SOURCE_SKILL = ROOT / ".agents/skills/sloar-chat-coder/SKILL.md"


def source_version() -> str:
    for line in SOURCE_SKILL.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("version:"):
            return line.split(":", 1)[1].strip().strip('"\'')
    raise AssertionError("source version missing")


class UpgradeTests(unittest.TestCase):
    def make_target(self, root: Path) -> Path:
        target = root / "target"
        target.mkdir()
        subprocess.run(["git", "-C", str(target), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(target), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(target), "config", "user.name", "test"], check=True)
        (target / "AGENTS.md").write_text("# Existing guidance\n\n<!-- sloar-chat-coder:begin -->\n## Sloar Chat Coder\nold block\n<!-- sloar-chat-coder:end -->\n", encoding="utf-8")
        old = target / ".agents/skills/sloar-chat-coder"
        old.mkdir(parents=True)
        (old / "SKILL.md").write_text('---\nname: sloar-chat-coder\nmetadata:\n  version: "0.4.0"\n---\nold\n', encoding="utf-8")
        (old / "custom-old-file.txt").write_text("preserve in backup\n", encoding="utf-8")
        companion = target / ".agents/skills/apple-web-design"
        companion.mkdir(parents=True)
        (companion / "SKILL.md").write_text("custom companion must stay\n", encoding="utf-8")
        (target / "product.txt").write_text("product state\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(target), "add", "."], check=True)
        subprocess.run(["git", "-C", str(target), "commit", "-qm", "baseline"], check=True)
        return target

    def test_upgrade_replaces_only_sloar_and_preserves_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            before_product = (target / "product.txt").read_text(encoding="utf-8")
            before_companion = (target / ".agents/skills/apple-web-design/SKILL.md").read_text(encoding="utf-8")

            proc = subprocess.run(
                ["python3", str(INSTALLER), "--target", str(target), "--upgrade"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            installed = (target / ".agents/skills/sloar-chat-coder/SKILL.md").read_text(encoding="utf-8")
            self.assertIn(f'version: "{source_version()}"', installed)
            self.assertEqual((target / "product.txt").read_text(encoding="utf-8"), before_product)
            self.assertEqual((target / ".agents/skills/apple-web-design/SKILL.md").read_text(encoding="utf-8"), before_companion)
            backups = list((target / ".git/sloar-upgrade-backups").glob("*/custom-old-file.txt"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "preserve in backup\n")

    def test_upgrade_does_not_dirty_product_files_beyond_sloar_owned_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            subprocess.run(["python3", str(INSTALLER), "--target", str(target), "--upgrade"], check=True, stdout=subprocess.PIPE, text=True)
            status = subprocess.run(
                ["git", "-C", str(target), "status", "--porcelain=v1"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.splitlines()
            self.assertTrue(status)
            self.assertTrue(all(".agents/skills/sloar-chat-coder/" in line for line in status), status)

    def test_same_version_different_install_requires_explicit_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            skill = target / ".agents/skills/sloar-chat-coder/SKILL.md"
            skill.write_text(f'---\nname: sloar-chat-coder\nmetadata:\n  version: "{source_version()}"\n---\nmodified\n', encoding="utf-8")
            proc = subprocess.run(
                ["python3", str(INSTALLER), "--target", str(target), "--upgrade"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("differs from this release", proc.stderr)

    def test_upgrade_refuses_downgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            skill = target / ".agents/skills/sloar-chat-coder/SKILL.md"
            skill.write_text('---\nname: sloar-chat-coder\nmetadata:\n  version: "99.0.0"\n---\nfuture\n', encoding="utf-8")
            proc = subprocess.run(
                ["python3", str(INSTALLER), "--target", str(target), "--upgrade"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("refusing Sloar downgrade", proc.stderr)


if __name__ == "__main__":
    unittest.main()
