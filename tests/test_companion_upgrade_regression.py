import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / ".agents/skills/sloar-chat-coder/scripts/install.py"
OFFICIAL_0_9_1_COMMIT = "743be629c217e5c0ebad894f8ecd5b07a2c1fcf3"


def git(repo: Path, *args: str, check: bool = True):
    return subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


class CompanionUpgradeRegressionTests(unittest.TestCase):
    def make_target(self, root: Path) -> Path:
        target = root / "target"; target.mkdir(); git(target, "init", "-q"); git(target, "config", "user.email", "test@example.com"); git(target, "config", "user.name", "test")
        (target / "AGENTS.md").write_text("# Existing guidance\n", encoding="utf-8")
        core = target / ".agents/skills/sloar-chat-coder"; core.mkdir(parents=True)
        (core / "SKILL.md").write_text('---\nname: sloar-chat-coder\nmetadata:\n  version: "0.10.0"\n---\nold core\n', encoding="utf-8")
        (target / "product.txt").write_text("product state\n", encoding="utf-8")
        return target

    def copy_historical_skill(self, target: Path, skill: str) -> Path:
        prefix = f".agents/skills/{skill}/"
        if git(ROOT, "cat-file", "-e", f"{OFFICIAL_0_9_1_COMMIT}^{{commit}}", check=False).returncode != 0:
            self.skipTest("v0.9.1 history unavailable in this checkout")
        listing = git(ROOT, "ls-tree", "-r", "--name-only", OFFICIAL_0_9_1_COMMIT, prefix)
        paths = [raw.decode("utf-8") for raw in listing.stdout.splitlines() if raw.decode("utf-8").startswith(prefix)]
        self.assertTrue(paths, skill)
        dest = target / ".agents/skills" / skill
        for repo_path in paths:
            shown = git(ROOT, "show", f"{OFFICIAL_0_9_1_COMMIT}:{repo_path}")
            path = dest / repo_path[len(prefix):]; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(shown.stdout)
        return dest

    def run_upgrade(self, target: Path):
        return subprocess.run(["python3", str(INSTALLER), "--target", str(target), "--upgrade"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

    def test_v0_9_1_official_companions_refresh_even_with_equal_or_missing_local_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_target(Path(temporary)); design = self.copy_historical_skill(target, "web-design-guidance"); apple = self.copy_historical_skill(target, "apple-web-design")
            self.assertIn('version: "0.8.0"', (design / "SKILL.md").read_text(encoding="utf-8")); self.assertNotIn("Product-craft contract", (apple / "SKILL.md").read_text(encoding="utf-8"))
            git(target, "add", "."); git(target, "commit", "-qm", "v0.9.1 install")
            proc = self.run_upgrade(target); self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue((design / "references/structural-ui-engineering.md").is_file()); self.assertIn("Product-craft contract", (apple / "SKILL.md").read_text(encoding="utf-8"))
            self.assertIn("refreshed official companion web-design-guidance 0.8.0 -> 0.8.0", proc.stdout)
            self.assertIn("refreshed official companion apple-web-design unversioned -> current bundle", proc.stdout)
            self.assertEqual(len(list((target / ".git/sloar-upgrade-backups/companions/web-design-guidance").glob("*/SKILL.md"))), 1)
            self.assertEqual(len(list((target / ".git/sloar-upgrade-backups/companions/apple-web-design").glob("*/SKILL.md"))), 1)

    def test_modified_v0_9_1_same_version_companion_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = self.make_target(Path(temporary)); design = self.copy_historical_skill(target, "web-design-guidance"); apple = self.copy_historical_skill(target, "apple-web-design")
            discovery = design / "references/design-discovery.md"; discovery.write_text(discovery.read_text(encoding="utf-8") + "\n# local customization\n", encoding="utf-8")
            git(target, "add", "."); git(target, "commit", "-qm", "customized v0.9.1 install")
            before = discovery.read_text(encoding="utf-8"); proc = self.run_upgrade(target); self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(discovery.read_text(encoding="utf-8"), before); self.assertFalse((design / "references/structural-ui-engineering.md").exists())
            self.assertIn("preserved existing companion customization", proc.stdout); self.assertIn("Product-craft contract", (apple / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
