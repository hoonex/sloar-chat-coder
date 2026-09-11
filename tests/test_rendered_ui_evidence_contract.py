import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/sloar-chat-coder"


class RenderedUiEvidenceContractTest(unittest.TestCase):
    def test_rendered_ui_reference_is_wired_from_core_skill(self):
        reference = SKILL / "references/rendered-ui-evidence.md"
        self.assertTrue(reference.is_file())

        core = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("rendered-ui-evidence.md", core)

    def test_visual_acceptance_is_independent_from_automation(self):
        text = (SKILL / "references/rendered-ui-evidence.md").read_text(encoding="utf-8")
        self.assertIn("AUTOMATION_GREEN != VISUAL_ACCEPTED", text)
        self.assertIn("actual rendered artifact", text)
        self.assertIn("visual gate is RED even when CI is GREEN", text)
        self.assertIn("source_sha", text)
        self.assertIn("artifact_or_run_id", text)
        self.assertIn("re-resolve the branch HEAD", text)

    def test_native_geometry_and_selector_failures_are_not_conflated_with_product_defects(self):
        text = (SKILL / "references/rendered-ui-evidence.md").read_text(encoding="utf-8")
        self.assertIn("status bar/icon contrast", text)
        self.assertIn("navigation bar or gesture inset separation", text)
        self.assertIn("portrait and landscape", text)
        self.assertIn("Hard-coded screen coordinates", text)
        self.assertIn("semantic targets", text)
        self.assertIn("test-harness/selector failure", text)
        self.assertIn("rendered visual defect", text)


if __name__ == "__main__":
    unittest.main()
