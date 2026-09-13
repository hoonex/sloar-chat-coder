import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents/skills/sloar-chat-coder"


class EvidenceIndependenceContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (SKILL_ROOT / relative).read_text(encoding="utf-8")

    def test_reference_exists_and_names_common_provenance_risk(self):
        text = self.read("references/evidence-independence.md")
        self.assertIn("Common-provenance trap", text)
        self.assertIn("failure provenance", text)
        self.assertIn("Critical-assumption ledger", text)
        self.assertIn("Differentiated falsifiers", text)
        self.assertIn("EVIDENCE_GAP", text)

    def test_reasoning_kernel_links_model_and_prove_to_independent_evidence(self):
        text = self.read("references/reasoning-kernel.md")
        self.assertIn("### Critical assumptions", text)
        self.assertIn("### Evidence provenance", text)
        self.assertIn("evidence-independence.md", text)
        self.assertIn("CONFIRMED", text)
        self.assertIn("SUPPORTED", text)
        self.assertIn("UNKNOWN", text)
        self.assertIn("differentiated falsifier", text)

    def test_dependency_prior_rejects_from_scratch_as_default(self):
        text = self.read("references/engineering-choice-priors.md")
        self.assertIn("## Dependency ownership boundary", text)
        self.assertIn("Prefer reuse", text)
        self.assertIn("Reimplement when", text)
        self.assertIn("from scratch", text)
        self.assertIn("evidence-independence.md", text)

    def test_contract_stays_conditional_not_universal_research_ceremony(self):
        text = self.read("references/evidence-independence.md")
        self.assertIn("risk-adaptive", text)
        self.assertIn("Do not perform broad research", text)
        self.assertIn("Skip this reference when", text)


if __name__ == "__main__":
    unittest.main()
