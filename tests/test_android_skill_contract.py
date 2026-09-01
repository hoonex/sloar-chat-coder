import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/sloar-chat-coder"
INSTALLER = SKILL / "scripts/install.py"


class AndroidSkillContractTest(unittest.TestCase):
    def test_android_reference_and_preflight_are_bundled_and_wired(self):
        reference = SKILL / "references/android-engineering.md"
        preflight = SKILL / "scripts/android-preflight.py"
        state_machine = SKILL / "references/state-machine.md"

        self.assertTrue(reference.is_file())
        self.assertTrue(preflight.is_file())
        text = state_machine.read_text(encoding="utf-8")
        core_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("android-engineering.md", core_text)
        self.assertIn("android-preflight.py", core_text)
        self.assertIn("android-engineering.md", text)
        self.assertIn("android-preflight.py", text)
        self.assertIn("THERMAL", reference.read_text(encoding="utf-8"))
        self.assertIn("EMPTY_OR_NON_ANDROID", reference.read_text(encoding="utf-8"))

    def test_fresh_install_copies_android_capability_into_target_repository(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            subprocess.run(["git", "init", "-q", str(target)], check=True)
            subprocess.run(
                [sys.executable, str(INSTALLER), "--target", str(target)],
                check=True,
                capture_output=True,
                text=True,
            )

            installed = target / ".agents/skills/sloar-chat-coder"
            self.assertTrue((installed / "references/android-engineering.md").is_file())
            self.assertTrue((installed / "scripts/android-preflight.py").is_file())
            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("sloar-chat-coder/SKILL.md", agents)


if __name__ == "__main__":
    unittest.main()
