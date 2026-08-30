from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / ".agents/skills/sloar-chat-coder/references/turn-terminalization.md"
OP = ROOT / ".agents/skills/sloar-chat-coder/references/operational-continuity.md"


class TurnTerminalizationContractTests(unittest.TestCase):
    def test_reference_exists_and_defines_bounded_corrective_cycle(self):
        text = REF.read_text(encoding="utf-8")
        self.assertIn("one failure fingerprint gets one bounded corrective cycle", text)
        self.assertIn("diagnose from concrete failure evidence", text)
        self.assertIn("make at most one corrective change", text)
        self.assertIn("re-run the affected verification once", text)

    def test_same_fingerprint_must_terminalize_instead_of_self_extend(self):
        text = REF.read_text(encoding="utf-8")
        self.assertIn("if the same failure fingerprint remains, terminalize", text)
        self.assertIn("No recursive \"one more check\"", text)
        self.assertIn("If no, terminalize the current turn", text)

    def test_red_gate_does_not_remove_turn_termination(self):
        text = REF.read_text(encoding="utf-8")
        self.assertIn(
            "A RED or unavailable required gate changes the terminal status; it does not remove the obligation to terminate the turn.",
            text,
        )
        for status in ("COMPLETED", "PARTIAL", "BLOCKED", "FAILED"):
            self.assertIn(status, text)

    def test_autonomous_mode_does_not_mean_infinite_retry(self):
        text = REF.read_text(encoding="utf-8")
        self.assertIn("Autonomous / ULW-style requests", text)
        self.assertIn("does **not** disable terminalization", text)
        self.assertIn("Do not interpret `ULW`", text)
        self.assertIn("infinite retry/wait loop", text)

    def test_long_running_ci_cannot_poll_forever(self):
        text = REF.read_text(encoding="utf-8")
        self.assertIn("Long-running CI and external waits", text)
        self.assertIn("do not poll indefinitely", text)
        self.assertIn("A check still running is not a reason to keep the visible turn open for hours or days", text)

    def test_original_scope_and_new_followups_are_separated(self):
        text = REF.read_text(encoding="utf-8")
        self.assertIn("Required gate versus optional improvement", text)
        self.assertIn("do not silently extend the current turn", text)
        self.assertIn("A direct regression introduced by the current change", text)

    def test_operational_continuity_routes_self_extension_to_terminalization_contract(self):
        text = OP.read_text(encoding="utf-8")
        self.assertIn("agent keeps extending its own work", text)
        self.assertIn("turn-terminalization.md", text)
        self.assertIn("It is not a reason to leave the turn ACTIVE indefinitely", text)


if __name__ == "__main__":
    unittest.main()
