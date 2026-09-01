import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / ".agents/skills/sloar-chat-coder/SKILL.md"
UPGRADING = ROOT / ".agents/skills/sloar-chat-coder/references/upgrading.md"
ONBOARDING = ROOT / ".agents/skills/sloar-chat-coder/references/environment-onboarding.md"
SCRIPTS = ROOT / ".agents/skills/sloar-chat-coder/scripts"
WIZARD_PATH = SCRIPTS / "wizard.py"


def load_wizard():
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location("sloar_wizard_update_test", WIZARD_PATH)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


class UpdateAwarenessContractTests(unittest.TestCase):
    def test_core_requires_bounded_read_only_awareness_before_upgrade_write(self):
        core = CORE.read_text(encoding="utf-8")
        self.assertIn('version: "0.8.2"', core)
        self.assertIn("UPDATE_AWARENESS", core)
        self.assertIn("first Sloar repository turn", core)
        self.assertIn("If they match, stay silent", core)
        self.assertIn("wait for the user's answer before any upgrade write", core)
        self.assertIn("installation is not", core)

    def test_upgrade_reference_separates_check_from_authorization(self):
        upgrading = UPGRADING.read_text(encoding="utf-8")
        self.assertIn("automatic update awareness", upgrading)
        self.assertIn("read-only awareness check", upgrading)
        self.assertIn("No upgrade write is authorized merely because a newer stable exists", upgrading)
        self.assertIn("do not re-check on every ordinary user message", upgrading.lower())
        self.assertIn("explicit authorization", upgrading)
        self.assertIn("do not retry-loop", upgrading)

    def test_onboarding_keeps_failed_update_lookup_non_blocking(self):
        onboarding = ONBOARDING.read_text(encoding="utf-8")
        self.assertIn("Version awareness during onboarding", onboarding)
        self.assertIn("read-only awareness check", onboarding)
        self.assertIn("mark update status `unknown` and continue normal work", onboarding)
        self.assertIn("local wizard remains network-free by default", onboarding.lower())
        self.assertIn("does not itself authorize", onboarding)

    def test_wizard_update_status_is_deterministic_and_never_implies_auto_write(self):
        wizard = load_wizard()
        self.assertEqual(wizard.CURRENT_SLOAR_VERSION, "0.8.2")

        current = wizard.build_update_status("0.8.2", "0.8.2")
        self.assertEqual(current["status"], "current")
        self.assertEqual(current["action"], "none")
        self.assertTrue(current["silent_when_current"])

        available = wizard.build_update_status("0.8.0", "0.8.2")
        self.assertEqual(available["status"], "update_available")
        self.assertEqual(available["action"], "ask_user_before_upgrade")
        self.assertIn("approval", available["install_policy"])

        unknown = wizard.build_update_status("0.8.2", None)
        self.assertEqual(unknown["status"], "unknown")
        self.assertEqual(unknown["action"], "resolve_stable_in_hosted_agent_when_available")

        ahead = wizard.build_update_status("0.9.0", "0.8.2")
        self.assertEqual(ahead["status"], "ahead")
        self.assertEqual(ahead["action"], "do_not_downgrade")


if __name__ == "__main__":
    unittest.main()
