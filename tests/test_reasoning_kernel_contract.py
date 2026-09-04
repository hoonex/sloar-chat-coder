import re
import unittest
from pathlib import Path


class ReasoningKernelContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.root = root
        skill_root = root / ".agents/skills/sloar-chat-coder"
        refs = skill_root / "references"
        cls.skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        cls.kernel = (refs / "reasoning-kernel.md").read_text(encoding="utf-8")
        cls.design_taste = (refs / "design-taste-priors.md").read_text(encoding="utf-8")
        cls.engineering_choice = (refs / "engineering-choice-priors.md").read_text(encoding="utf-8")
        cls.state_machine = (refs / "state-machine.md").read_text(encoding="utf-8")
        cls.verification = (refs / "verification.md").read_text(encoding="utf-8")
        cls.readme = (root / "README.md").read_text(encoding="utf-8")
        cls.version = (root / "VERSION").read_text(encoding="utf-8").strip()

    def test_five_move_kernel_is_primary_entry_point(self):
        loop = "OBSERVE -> MODEL -> ACT -> PROVE -> RECONCILE"
        self.assertIn(loop, self.skill)
        self.assertIn(loop, self.kernel)
        self.assertIn("default reasoning algorithm", self.skill)
        self.assertIn("Do not turn the union of all Sloar references into ceremony", self.skill)

    def test_state_machine_is_risk_adaptive_not_mandatory_choreography(self):
        self.assertIn("risk-adaptive guardrails", self.skill)
        self.assertIn("not the default reasoning algorithm", self.state_machine)
        self.assertIn("Small exact tasks may collapse", self.skill)
        self.assertIn("do not spend tool calls", self.state_machine.lower())

    def test_phase_fit_and_latest_boundary_are_entry_level_rules(self):
        self.assertIn("latest valid observable", self.skill)
        self.assertIn("Phase-fit rule", self.verification)
        self.assertIn("latest valid observable boundary", self.verification)
        self.assertIn("More tests do not compensate for missing the critical phase", self.skill)

    def test_evidence_economy_is_explicit(self):
        self.assertIn("Evidence economy", self.kernel)
        self.assertIn("More tests are not automatically stronger evidence", self.kernel)
        self.assertIn("Evidence quality is not test count", self.verification)

    def test_public_contract_preservation_is_entry_level_rule(self):
        self.assertIn("Public contract preservation", self.kernel)
        self.assertIn("simplest pre-existing behavior", self.kernel)
        self.assertIn("control/sentinel values", self.kernel)
        self.assertIn("compatibility probe", self.kernel)

    def test_origin_checkpoint_and_final_anchors_are_distinct(self):
        self.assertIn("origin anchor != checkpoint anchor != final anchor", self.kernel)
        self.assertIn("Do not redefine the origin from a later checkpoint", self.kernel)
        self.assertIn("branch ref that has not advanced", self.kernel)

    def test_visible_ui_routes_to_soft_design_taste_prior(self):
        self.assertIn("substantial visible UI/product design -> `design-taste-priors.md`", self.kernel)
        self.assertIn("soft priors, not a style preset and not a ban list", self.design_taste)
        self.assertIn("Treat defaults as hypotheses, not answers", self.design_taste)
        self.assertIn("Identity test", self.design_taste)
        self.assertIn("Grounding test", self.design_taste)
        self.assertIn("product-specific decisions beat generic polish", self.design_taste)

    def test_representation_choice_prefers_structural_correctness(self):
        self.assertIn("Representation choice", self.kernel)
        self.assertIn("engineering-choice-priors.md", self.kernel)
        self.assertIn("Representation before machinery", self.engineering_choice)
        self.assertIn("fewest lifecycle edges", self.engineering_choice)
        self.assertIn("removes failure classes", self.engineering_choice)
        self.assertIn("internal decision aid, not a user-facing questionnaire", self.engineering_choice)

    def test_discovered_material_defects_must_close_against_final_bytes(self):
        self.assertIn("Discovered-defect closure", self.kernel)
        self.assertIn("final durable bytes", self.kernel)
        self.assertIn("green checkpoint plus separate local fixes is not a green final result", self.kernel.lower())

    def test_stable_version_contract_is_consistent(self):
        self.assertEqual(self.version, "0.9.0")
        self.assertRegex(self.skill, r'version:\s*"0\.9\.0"')
        self.assertIn("Current stable: **0.9.0**", self.readme)
        self.assertIn("stable-0.9.0", self.readme)


if __name__ == "__main__":
    unittest.main()
