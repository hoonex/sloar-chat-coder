import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / ".agents/skills/sloar-chat-coder/scripts/install.py"
SOURCE_SKILL = ROOT / ".agents/skills/sloar-chat-coder/SKILL.md"
LEGACY_DESIGN_COMMIT = "371d8def796378f2fb59f61ea73019b397b75f9c"
LEGACY_DESIGN_FILES = (
    "NOTICE.md",
    "SKILL.md",
    "references/design-discovery.md",
    "references/surface-recipes.md",
    "references/visual-verification.md",
)


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

    def install_official_legacy_design(self, target: Path) -> Path:
        probe = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{LEGACY_DESIGN_COMMIT}^{{commit}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if probe.returncode != 0:
            self.skipTest("legacy 0.7.0 commit unavailable in this shallow/local checkout")
        design = target / ".agents/skills/web-design-guidance"
        for rel in LEGACY_DESIGN_FILES:
            proc = subprocess.run(
                ["git", "-C", str(ROOT), "show", f"{LEGACY_DESIGN_COMMIT}:.agents/skills/web-design-guidance/{rel}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr.decode(errors="replace"))
            path = design / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(proc.stdout)
        return design

    def run_upgrade(self, target: Path):
        return subprocess.run(
            ["python3", str(INSTALLER), "--target", str(target), "--upgrade"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_upgrade_replaces_sloar_installs_missing_design_companion_and_preserves_custom_companion(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            before_product = (target / "product.txt").read_text(encoding="utf-8")
            before_companion = (target / ".agents/skills/apple-web-design/SKILL.md").read_text(encoding="utf-8")

            proc = self.run_upgrade(target)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            installed = (target / ".agents/skills/sloar-chat-coder/SKILL.md").read_text(encoding="utf-8")
            self.assertIn(f'version: "{source_version()}"', installed)
            design = target / ".agents/skills/web-design-guidance"
            self.assertTrue((design / "SKILL.md").is_file())
            for rel in (
                "references/adaptive-design-discovery.md",
                "references/design-taxonomy.md",
                "references/anti-ai-slop.md",
            ):
                self.assertTrue((design / rel).is_file(), rel)
            self.assertEqual((target / "product.txt").read_text(encoding="utf-8"), before_product)
            self.assertEqual((target / ".agents/skills/apple-web-design/SKILL.md").read_text(encoding="utf-8"), before_companion)
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("web-design-guidance/SKILL.md", agents)
            self.assertEqual(agents.count("<!-- sloar-chat-coder:begin -->"), 1)
            backups = list((target / ".git/sloar-upgrade-backups").glob("*/custom-old-file.txt"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "preserve in backup\n")

    def test_upgrade_replaces_exact_official_0_7_design_companion(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            design = self.install_official_legacy_design(target)
            subprocess.run(["git", "-C", str(target), "add", "."], check=True)
            subprocess.run(["git", "-C", str(target), "commit", "-qm", "official 0.7 design companion"], check=True)

            before = (design / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn('version: "0.7.0"', before)
            proc = self.run_upgrade(target)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            after = (design / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn('version: "0.8.0"', after)
            self.assertTrue((design / "references/adaptive-design-discovery.md").is_file())
            self.assertTrue((design / "references/design-taxonomy.md").is_file())
            self.assertTrue((design / "references/anti-ai-slop.md").is_file())
            self.assertIn("upgraded official companion web-design-guidance 0.7.0 -> 0.8.0", proc.stdout)
            backups = list((target / ".git/sloar-upgrade-backups/companions/web-design-guidance").glob("*/SKILL.md"))
            self.assertEqual(len(backups), 1)
            self.assertIn('version: "0.7.0"', backups[0].read_text(encoding="utf-8"))

    def test_upgrade_preserves_modified_0_7_design_companion(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            design = self.install_official_legacy_design(target)
            discovery = design / "references/design-discovery.md"
            discovery.write_text(discovery.read_text(encoding="utf-8") + "\n# local customization\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(target), "add", "."], check=True)
            subprocess.run(["git", "-C", str(target), "commit", "-qm", "customized 0.7 design companion"], check=True)

            before = discovery.read_text(encoding="utf-8")
            proc = self.run_upgrade(target)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(discovery.read_text(encoding="utf-8"), before)
            self.assertIn('version: "0.7.0"', (design / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse((design / "references/adaptive-design-discovery.md").exists())
            self.assertIn("preserved existing companion customization", proc.stdout)

    def test_upgrade_preserves_existing_custom_design_companion_without_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            design = target / ".agents/skills/web-design-guidance"
            design.mkdir(parents=True)
            (design / "SKILL.md").write_text("custom web design companion\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(target), "add", "."], check=True)
            subprocess.run(["git", "-C", str(target), "commit", "-qm", "custom design companion"], check=True)
            before = (design / "SKILL.md").read_text(encoding="utf-8")

            proc = self.run_upgrade(target)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual((design / "SKILL.md").read_text(encoding="utf-8"), before)
            self.assertIn("preserved existing companion customization", proc.stdout)

    def test_upgrade_does_not_dirty_unrelated_product_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            proc = self.run_upgrade(target)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            status = subprocess.run(
                ["git", "-C", str(target), "status", "--porcelain=v1"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.splitlines()
            self.assertTrue(status)
            allowed = (
                "AGENTS.md",
                ".agents/skills/sloar-chat-coder/",
                ".agents/skills/web-design-guidance/",
            )
            unexpected = [line for line in status if not any(path in line for path in allowed)]
            self.assertEqual(unexpected, [], status)
            self.assertEqual((target / "product.txt").read_text(encoding="utf-8"), "product state\n")

    def test_same_version_different_install_requires_explicit_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            skill = target / ".agents/skills/sloar-chat-coder/SKILL.md"
            skill.write_text(f'---\nname: sloar-chat-coder\nmetadata:\n  version: "{source_version()}"\n---\nmodified\n', encoding="utf-8")
            proc = self.run_upgrade(target)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("differs from this release", proc.stderr)

    def test_upgrade_refuses_downgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            skill = target / ".agents/skills/sloar-chat-coder/SKILL.md"
            skill.write_text('---\nname: sloar-chat-coder\nmetadata:\n  version: "99.0.0"\n---\nfuture\n', encoding="utf-8")
            proc = self.run_upgrade(target)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("refusing Sloar downgrade", proc.stderr)


if __name__ == "__main__":
    unittest.main()
