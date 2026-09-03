import unittest
from pathlib import Path


class ConnectorNativeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        base = root / ".agents/skills/sloar-chat-coder/references"
        cls.ladder = (base / "capability-ladder.md").read_text(encoding="utf-8")
        cls.state = (base / "state-machine.md").read_text(encoding="utf-8")

    def test_l2_allows_connector_native_workspace(self):
        self.assertIn("connector-native workspace", self.ladder)
        self.assertIn("Do not retry clone merely to obtain a local copy", self.ladder)

    def test_materialize_has_local_and_connector_native_modes(self):
        self.assertIn("`LOCAL_WORKTREE`", self.state)
        self.assertIn("`CONNECTOR_NATIVE`", self.state)
        self.assertIn("does not require a local clone", self.state)

    def test_local_execution_promotes_only_when_required(self):
        self.assertIn("Promote to `LOCAL_WORKTREE` only when", self.state)
        self.assertIn("A failed `git clone` by itself is not a reason to escalate", self.state)


if __name__ == "__main__":
    unittest.main()
