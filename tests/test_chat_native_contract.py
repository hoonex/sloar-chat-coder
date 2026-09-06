import unittest
from pathlib import Path


class ChatNativeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.reference = (root / ".agents/skills/sloar-chat-coder/references/chat-native-continuity.md").read_text(encoding="utf-8")

    def test_pre_response_blocker_has_entry_and_exit_conditions(self):
        text = self.reference
        self.assertIn("PRE_RESPONSE_READ_BLOCKED", text)
        self.assertIn("Entry condition:", text)
        self.assertIn("Exit condition:", text)
        self.assertIn("do not repeat an unchanged live validation", text)

    def test_checkpoint_never_outranks_repository(self):
        self.assertIn("never outranks freshly resolved repository state", self.reference)

    def test_sidecar_is_not_product_truth(self):
        self.assertIn("`latest.json` is a pointer, not repository truth", self.reference)

    def test_sloar_name_alone_is_not_activation_evidence(self):
        text = self.reference
        self.assertIn("is **not** by itself evidence that Sloar is active", text)
        self.assertIn("host-exposed Sloar Skill was actually loaded/read", text)
        self.assertIn("installed contract was actually read", text)
        self.assertIn("canonical Sloar source ephemerally", text)

    def test_remote_activation_is_sha_pinned_and_bounded(self):
        text = self.reference
        self.assertIn("exact immutable source commit SHA", text)
        self.assertIn("same source SHA", text)
        self.assertIn("fetch only references that can materially affect the current task", text)
        self.assertIn("SLOAR_UNAVAILABLE", text)
        self.assertIn("Do **not** silently continue as an ordinary/Bare workflow", text)


if __name__ == "__main__":
    unittest.main()
