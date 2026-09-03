import unittest
from pathlib import Path


class AsyncEvidenceClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        refs = root / ".agents/skills/sloar-chat-coder/references"
        cls.async_ref = (refs / "async-evidence-closure.md").read_text(encoding="utf-8")
        cls.verification = (refs / "verification.md").read_text(encoding="utf-8")

    def test_async_reference_is_connected_to_verification(self):
        self.assertIn("async-evidence-closure.md", self.verification)
        self.assertIn("independently observable claims", self.verification)

    def test_await_boundary_and_observable_result_are_required(self):
        self.assertIn("Await-boundary state-transition analysis", self.async_ref)
        self.assertIn("Observable-result invariant", self.async_ref)
        self.assertIn("Promise resolution", self.async_ref)

    def test_lifecycle_pairs_and_end_to_end_fencing_are_required(self):
        self.assertIn("Lifecycle-pair derivation", self.async_ref)
        self.assertIn("Fencing must be end-to-end", self.async_ref)
        self.assertIn("Sequential tests are not evidence for an interleaving race", self.async_ref)

    def test_claims_do_not_generalize_across_distinct_paths(self):
        self.assertIn("logout test to all invalidation paths", self.async_ref)
        self.assertIn("final-state test to Promise return value", self.async_ref)
        self.assertIn("PARTIAL or EVIDENCE_GAP", self.async_ref)


if __name__ == "__main__":
    unittest.main()
