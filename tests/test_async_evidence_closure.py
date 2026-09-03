import unittest
from pathlib import Path


class AsyncEvidenceClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        refs = root / ".agents/skills/sloar-chat-coder/references"
        cls.async_ref = (refs / "async-evidence-closure.md").read_text(encoding="utf-8")
        cls.verification = (refs / "verification.md").read_text(encoding="utf-8")
        cls.kernel = (refs / "reasoning-kernel.md").read_text(encoding="utf-8")

    def test_async_reference_is_connected_to_verification_and_kernel(self):
        self.assertIn("async-evidence-closure.md", self.verification)
        self.assertIn("reasoning-kernel.md", self.async_ref)
        self.assertIn("independently observable claims", self.verification)

    def test_semantic_phase_is_not_collapsed_into_implementation_state(self):
        self.assertIn("Semantic phase before implementation state", self.async_ref)
        self.assertIn("Latest-valid-boundary rule", self.async_ref)
        self.assertIn("reserved", self.async_ref)
        self.assertIn("scheduled", self.async_ref)
        self.assertIn("runner not invoked yet", self.async_ref)

    def test_transition_adjacent_testing_is_required(self):
        self.assertIn("transition-adjacent testing", self.async_ref.lower())
        self.assertIn("immediately before user callback invocation", self.async_ref)
        self.assertIn("late finalizer", self.async_ref)
        self.assertIn("Sequential tests are not evidence for an interleaving race", self.async_ref)

    def test_observable_result_and_resource_ownership_are_required(self):
        self.assertIn("Observable-result invariant", self.async_ref)
        self.assertIn("Promise resolution/rejection", self.async_ref)
        self.assertIn("callback invocation count", self.async_ref)
        self.assertIn("resource/running count", self.async_ref)

    def test_lifecycle_pairs_and_end_to_end_fencing_are_required(self):
        self.assertIn("Lifecycle-pair derivation", self.async_ref)
        self.assertIn("Fencing must be end-to-end", self.async_ref)
        self.assertIn("old finalizer x replacement execution", self.async_ref)
        self.assertIn("retry x concurrency slot", self.async_ref)

    def test_claims_do_not_generalize_across_distinct_paths_or_phases(self):
        self.assertIn("logout test -> all invalidation paths", self.async_ref)
        self.assertIn("queued cancellation -> all pre-invocation cancellation", self.async_ref)
        self.assertIn("final-state test -> Promise/callback observable", self.async_ref)
        self.assertIn("PARTIAL or EVIDENCE_GAP", self.async_ref)

    def test_caller_visible_cancellation_is_separate_from_underlying_lifetime(self):
        self.assertIn("Caller-visible cancellation must not inherit unrelated operation latency", self.async_ref)
        self.assertIn("caller settlement", self.async_ref)
        self.assertIn("underlying operation termination", self.async_ref)
        self.assertIn("caller-visible latency/settlement", self.async_ref)
        self.assertIn("underlying closure", self.async_ref)
        self.assertIn("not a requirement to use `Promise.race`", self.async_ref)

    def test_evidence_economy_prefers_boundary_coverage_over_volume(self):
        self.assertIn("Evidence economy", self.async_ref)
        self.assertIn("not inflate test count", self.async_ref)
        self.assertIn("More tests are not automatically stronger evidence", self.kernel)


if __name__ == "__main__":
    unittest.main()
