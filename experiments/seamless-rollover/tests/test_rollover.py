import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "rollover.py"
PROTOCOL_PATH = Path(__file__).resolve().parents[1] / "PROTOCOL.md"
spec = importlib.util.spec_from_file_location("rollover", MODULE_PATH)
rollover = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rollover
spec.loader.exec_module(rollover)


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return proc.stdout.strip()


class RolloverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-b", "main")
        git(self.repo, "config", "user.email", "demo@example.com")
        git(self.repo, "config", "user.name", "Demo")
        git(self.repo, "remote", "add", "origin", "https://github.com/example/demo.git")
        (self.repo / "README.md").write_text("demo\n", encoding="utf-8")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "init")

    def tearDown(self):
        self.tmp.cleanup()

    def _args(self):
        return Namespace(
            goal="Continue UI work",
            completed=["typecheck pass"],
            active=["settings UI"],
            pending=["mobile regression"],
            decision=["preserve school behavior"],
            evidence=["unit: pass"],
            blocker=[],
            next_action="run browser regression",
            response_language="ko-KR",
        )

    def test_checkpoint_round_trip_exact(self):
        identity = rollover.capture_identity(self.repo)
        checkpoint = rollover.build_checkpoint(identity, self._args())
        rollover.write_checkpoint(self.repo, checkpoint, rollover.DEFAULT_STATE_DIR)
        loaded = rollover.load_checkpoint(self.repo, rollover.DEFAULT_STATE_DIR, None)
        comparison = rollover.compare_identity(loaded, rollover.capture_identity(self.repo))
        self.assertEqual(comparison["state"], "EXACT")
        self.assertEqual(comparison["unobserved"], [])
        self.assertEqual(loaded["context"]["response_language"], "ko-KR")

    def test_rollover_pointer_copies_response_language_hint(self):
        identity = rollover.capture_identity(self.repo)
        checkpoint = rollover.build_checkpoint(identity, self._args())
        _, latest_path = rollover.write_checkpoint(self.repo, checkpoint, rollover.DEFAULT_STATE_DIR)
        pointer = json.loads(latest_path.read_text(encoding="utf-8"))
        self.assertEqual(pointer["response_language"], "ko-KR")
        self.assertEqual(pointer["checkpoint_id"], checkpoint["checkpoint_id"])

    def test_custom_worktree_state_dir_is_detected(self):
        identity = rollover.capture_identity(self.repo)
        checkpoint = rollover.build_checkpoint(identity, self._args())
        rollover.write_checkpoint(self.repo, checkpoint, ".sloar/rollover")
        comparison = rollover.compare_identity(checkpoint, rollover.capture_identity(self.repo))
        self.assertEqual(comparison["state"], "RECONCILE_REQUIRED")
        self.assertIn("dirty", comparison["changed"])
        self.assertIn("status_sha256", comparison["changed"])

    def test_repository_move_requires_reconcile(self):
        checkpoint = rollover.build_checkpoint(rollover.capture_identity(self.repo), self._args())
        rollover.write_checkpoint(self.repo, checkpoint, rollover.DEFAULT_STATE_DIR)
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "move")
        comparison = rollover.compare_identity(checkpoint, rollover.capture_identity(self.repo))
        self.assertEqual(comparison["state"], "RECONCILE_REQUIRED")
        self.assertIn("head", comparison["changed"])
        self.assertIn("tree", comparison["changed"])

    def test_remote_only_identity_can_be_exact_for_observable_state(self):
        identity = rollover.capture_identity(self.repo)
        checkpoint = rollover.build_checkpoint(identity, self._args())
        checkpoint["identity"].update(
            {
                "working_state_observed": False,
                "dirty": None,
                "status_sha256": None,
            }
        )
        current = dict(checkpoint["identity"])
        comparison = rollover.compare_identity(checkpoint, current)
        self.assertEqual(comparison["state"], "EXACT")
        self.assertEqual(comparison["changed"], [])
        self.assertEqual(comparison["unobserved"], ["working_state"])

    def test_remote_only_repository_move_still_requires_reconcile(self):
        identity = rollover.capture_identity(self.repo)
        checkpoint = rollover.build_checkpoint(identity, self._args())
        checkpoint["identity"].update(
            {
                "working_state_observed": False,
                "dirty": None,
                "status_sha256": None,
            }
        )
        current = dict(checkpoint["identity"])
        current["head"] = "f" * 40
        comparison = rollover.compare_identity(checkpoint, current)
        self.assertEqual(comparison["state"], "RECONCILE_REQUIRED")
        self.assertIn("head", comparison["changed"])
        self.assertEqual(comparison["unobserved"], ["working_state"])

    def test_capsule_omits_chat_noise(self):
        checkpoint = rollover.build_checkpoint(rollover.capture_identity(self.repo), self._args())
        comparison = rollover.compare_identity(checkpoint, rollover.capture_identity(self.repo))
        capsule = rollover.render_capsule(checkpoint, comparison)
        self.assertIn("SLOAR SESSION CAPSULE v1", capsule)
        self.assertIn("Response language: ko-KR", capsule)
        self.assertIn("Goal: Continue UI work", capsule)
        self.assertIn("Next action: run browser regression", capsule)
        self.assertNotIn("conversation", capsule.lower())

    def test_capsule_marks_unobserved_working_state(self):
        identity = rollover.capture_identity(self.repo)
        checkpoint = rollover.build_checkpoint(identity, self._args())
        checkpoint["identity"].update(
            {
                "working_state_observed": False,
                "dirty": None,
                "status_sha256": None,
            }
        )
        comparison = rollover.compare_identity(checkpoint, dict(checkpoint["identity"]))
        capsule = rollover.render_capsule(checkpoint, comparison)
        self.assertIn("Resume state: EXACT", capsule)
        self.assertIn("Unobserved identity fields: working_state", capsule)

    def test_response_language_can_be_omitted_for_legacy_checkpoint_creation(self):
        args = self._args()
        delattr(args, "response_language")
        checkpoint = rollover.build_checkpoint(rollover.capture_identity(self.repo), args)
        self.assertEqual(checkpoint["context"]["response_language"], "")

    def test_protocol_requires_silent_pre_response_recovery(self):
        protocol = PROTOCOL_PATH.read_text(encoding="utf-8")
        self.assertIn("### Pre-response recovery gate", protocol)
        self.assertIn(
            "Do not emit any user-visible acknowledgement, progress update, or status message until `response_language` is restored",
            protocol,
        )
        self.assertIn("silent control-plane preflight", protocol)

    def test_resume_instruction_is_one_line_and_repository_specific(self):
        instruction = rollover.resume_instruction("example/demo")
        self.assertEqual(instruction, "Resume the latest Sloar session for example/demo.")
        self.assertNotIn("\n", instruction)
        self.assertNotIn("rollover", instruction.lower())


if __name__ == "__main__":
    unittest.main()
