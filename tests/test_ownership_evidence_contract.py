from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/sloar-chat-coder/SKILL.md"
REFERENCE = ROOT / ".agents/skills/sloar-chat-coder/references/ownership-evidence-closure.md"
VERIFICATION = ROOT / ".agents/skills/sloar-chat-coder/references/verification.md"
LEDGER = ROOT / ".agents/skills/sloar-chat-coder/references/evidence-ledger.md"
VERSION = ROOT / "VERSION"


class OwnershipEvidenceContractTests(unittest.TestCase):
    def test_core_wires_ownership_before_workaround_and_claim_closure(self):
        text = SKILL.read_text(encoding="utf-8")
        version = VERSION.read_text(encoding="utf-8").strip()
        self.assertIn(f'version: "{version}"', text)
        self.assertIn("Ownership before workaround", text)
        self.assertIn("ownership-evidence-closure.md", text)
        self.assertIn("engineering-closure.py", text)
        self.assertIn("real touch", text.lower())
        self.assertIn("SOURCE -> VERIFIED -> PACKAGED -> DEPLOYED -> SERVED -> CACHED -> FIRST_FRAME", text)
        self.assertIn("STALE_GATE_SUSPECTED", text)

    def test_reference_defines_root_failure_classes_and_rediscovery(self):
        text = REFERENCE.read_text(encoding="utf-8")
        for token in (
            "OWNER_CONFIRMED",
            "OWNER_UNKNOWN",
            "OWNERSHIP_SPLIT",
            "EVIDENCE_GAP",
            "STALE_GATE_SUSPECTED",
            "CONVERGENCE_GAP",
        ):
            self.assertIn(token, text)
        self.assertIn("Ownership rediscovery after a failed corrective cycle", text)
        self.assertIn("real-touch", text)
        self.assertIn("first frame", text.lower())
        self.assertIn("Absence is not a value", text)
        self.assertIn("Time provenance", text)

    def test_verification_starts_from_claim_and_owner_not_existing_green_tests(self):
        text = VERIFICATION.read_text(encoding="utf-8")
        self.assertIn("Verification begins from the acceptance claim and authoritative semantic owner", text)
        self.assertIn("Mouse input does not prove real-touch behavior", text)
        self.assertIn("Feature lifecycle and gate relevance", text)
        self.assertIn("same fingerprint remains", text)

    def test_ledger_records_claim_dimensions_lifecycle_and_convergence(self):
        text = LEDGER.read_text(encoding="utf-8")
        self.assertIn("ownership:", text)
        self.assertIn("claims:", text)
        self.assertIn("covers:", text)
        self.assertIn("features:", text)
        self.assertIn("gates:", text)
        self.assertIn("convergence:", text)
        self.assertIn("SOURCE -> VERIFIED -> PACKAGED -> DEPLOYED -> SERVED -> CACHED -> FIRST_FRAME", text)


if __name__ == "__main__":
    unittest.main()
