from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/sloar-chat-coder/SKILL.md"
OP = ROOT / ".agents/skills/sloar-chat-coder/references/operational-continuity.md"


class LongRunningExecutionContractTests(unittest.TestCase):
    def test_skill_routes_execution_bound_work_to_managed_orchestrator(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("genuinely execution-bound", text)
        self.assertIn("one bounded managed orchestrator", text)
        self.assertIn("terminal acceptance criteria before launch", text)
        self.assertIn("poll the existing managed process", text)
        self.assertIn("independent terminal audit", text)

    def test_internal_runtime_markers_are_diagnostic_only(self):
        text = SKILL.read_text(encoding="utf-8")
        for marker in (
            "conversation-turn-*",
            "wfr_*",
            "SAServer async execution",
            "temporal conversation turn",
            "stream handoff",
        ):
            self.assertIn(marker, text)
        self.assertIn("diagnostic hints only", text)
        self.assertIn("must never be fabricated", text)
        self.assertIn("treated as proof", text)

    def test_operational_contract_prevents_duplicate_or_fake_duration(self):
        text = OP.read_text(encoding="utf-8")
        self.assertIn("start the orchestrator exactly once", text)
        self.assertIn("never restart or duplicate a healthy calculation", text)
        self.assertIn("do not create shell `sleep` loops", text)
        self.assertIn("do not add fake duration", text)
        self.assertIn("Do not keep the turn alive after terminality", text)

    def test_safety_blocks_are_separate_and_not_bypassed(self):
        text = OP.read_text(encoding="utf-8")
        self.assertIn("classify host/tool safety blocks separately", text)
        self.assertIn("do not rephrase commands solely to evade the safety decision", text)

    def test_progress_and_terminal_audit_are_durable(self):
        text = OP.read_text(encoding="utf-8")
        self.assertIn("write progress atomically", text)
        self.assertIn("orchestrator_state = RUNNING | COMPLETED | PARTIAL | BLOCKED | FAILED", text)
        self.assertIn("perform a short independent audit", text)
        self.assertIn("no Sloar-owned child process remains unintentionally active", text)


if __name__ == "__main__":
    unittest.main()
