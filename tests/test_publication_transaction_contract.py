from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONCURRENCY = ROOT / ".agents/skills/sloar-chat-coder/references/concurrency.md"
SKILL = ROOT / ".agents/skills/sloar-chat-coder/SKILL.md"


class PublicationTransactionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.concurrency = CONCURRENCY.read_text(encoding="utf-8")
        cls.skill = SKILL.read_text(encoding="utf-8")

    def test_skill_routes_publication_safety_to_concurrency_reference(self):
        self.assertIn("references/concurrency.md", self.skill)
        self.assertIn("Concurrent actors and publication guard", self.skill)

    def test_publication_requires_explicit_mutation_intent(self):
        for phrase in (
            "Publication mutation intent",
            "mutation_kind = ref_move | file_content | pr_metadata | workflow_action | other",
            "Tool or recipient name similarity never authorizes substitution",
            "mutation envelope",
        ):
            self.assertIn(phrase, self.concurrency)

    def test_ref_publication_has_identity_guard_and_postcondition(self):
        for phrase in (
            "build blob/tree/commit with parent = expected_head",
            "if current_head != expected_head: reconcile; do not move the ref",
            "compare-and-swap",
            "Publication postconditions",
            "final ref SHA is the intended commit",
        ):
            self.assertIn(phrase, self.concurrency)

    def test_wrong_remote_write_becomes_operational_incident(self):
        self.assertIn("wrong tool/recipient", self.concurrency)
        self.assertIn("operational incident", self.concurrency)
        self.assertIn("Do not force-rewrite shared or already-public history merely to hide", self.concurrency)

    def test_concurrency_cancellation_is_not_silently_green_or_red(self):
        self.assertIn("CI concurrency cancellation", self.concurrency)
        self.assertIn("Workflow cancellation is not automatically a code failure", self.concurrency)
        self.assertIn("exact source SHA", self.concurrency)
        self.assertIn("Never convert an unexplained cancellation", self.concurrency)


if __name__ == "__main__":
    unittest.main()
