import importlib.util
import subprocess
import sys
import tempfile
import unittest
import json
from unittest.mock import patch
from argparse import Namespace
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / ".agents/skills/sloar-chat-coder/scripts/turn-state.py"
spec = importlib.util.spec_from_file_location("turn_state", MODULE_PATH)
turn_state = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = turn_state
spec.loader.exec_module(turn_state)


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return proc.stdout.strip()


def args(**overrides):
    values = dict(
        goal="Finish repository task",
        completed=[],
        active=["implementation"],
        pending=["remote verify"],
        decision=[],
        evidence=[],
        blocker=[],
        next_action="run verification",
        response_language="ko-KR",
        anchor=[],
        changed=[],
        preserved=[],
        not_changed=[],
        limitation=[],
        turn_id=None,
        epoch=None,
        status="COMPLETED",
        terminal_note=None,
        reason=None,
    )
    values.update(overrides)
    return Namespace(**values)


class TurnStateTests(unittest.TestCase):
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

    def test_begin_turn_is_active_and_does_not_dirty_worktree(self):
        before = turn_state.capture_identity(self.repo)
        state = turn_state.begin_turn(self.repo, args())
        after = turn_state.capture_identity(self.repo)
        self.assertEqual(state["status"], "ACTIVE")
        self.assertFalse(state["terminal"])
        self.assertEqual(state["epoch"], 1)
        self.assertEqual(before.head, after.head)
        self.assertEqual(before.status_sha256, after.status_sha256)
        pointer = turn_state.load_pointer(self.repo)
        self.assertEqual(pointer["turn_id"], state["turn_id"])
        self.assertEqual(pointer["response_language"], "ko-KR")

    def test_overlapping_active_turn_is_refused(self):
        turn_state.begin_turn(self.repo, args())
        with self.assertRaises(turn_state.TurnStateError):
            turn_state.begin_turn(self.repo, args(goal="second"))

    def test_progress_appends_hot_state_anchors_and_change_boundary(self):
        state = turn_state.begin_turn(
            self.repo,
            args(anchor=["verified_commit=abc123"], preserved=["existing API contract"]),
        )
        progress_args = args(
            turn_id=state["turn_id"],
            epoch=state["epoch"],
            completed=["implementation"],
            evidence=["unit:pass"],
            anchor=["production_commit=def456"],
            changed=["settings UI"],
            not_changed=["authentication"],
            limitation=["live provider not checked"],
            next_action="run browser audit",
        )
        updated = turn_state.progress_turn(self.repo, progress_args)
        self.assertEqual(updated["event_seq"], 2)
        self.assertIn("implementation", updated["context"]["completed"])
        self.assertEqual(updated["context"]["anchors"]["verified_commit"], "abc123")
        self.assertEqual(updated["context"]["anchors"]["production_commit"], "def456")
        boundary = updated["context"]["change_boundary"]
        self.assertIn("settings UI", boundary["changed"])
        self.assertIn("existing API contract", boundary["preserved"])
        self.assertIn("authentication", boundary["deliberately_not_changed"])
        self.assertIn("live provider not checked", boundary["limitations"])

    def test_terminal_snapshot_is_recoverable_before_visible_final_reply(self):
        state = turn_state.begin_turn(self.repo, args())
        completed = turn_state.complete_turn(
            self.repo,
            args(
                turn_id=state["turn_id"],
                epoch=state["epoch"],
                status="COMPLETED",
                evidence=["ci:green"],
                terminal_note="Engineering work finished; visible final response may still fail at the host layer.",
            ),
        )
        self.assertTrue(completed["terminal"])
        self.assertEqual(completed["status"], "COMPLETED")
        view = turn_state.recovery_view(self.repo)
        self.assertEqual(view["recovery_state"], "TERMINAL_REPLAY_AVAILABLE")
        self.assertEqual(view["comparison"]["state"], "EXACT")
        self.assertFalse(view["takeover_allowed_only_with_explicit_user_intent"])

    def test_active_turn_is_not_auto_declared_dead_by_time(self):
        state = turn_state.begin_turn(self.repo, args())
        state["updated_at"] = "2000-01-01T00:00:00Z"
        turn_state._write_state(self.repo, turn_state.DEFAULT_STATE_DIR, state)
        view = turn_state.recovery_view(self.repo)
        self.assertEqual(view["recovery_state"], "ACTIVE_OR_INTERRUPTED")
        self.assertFalse(view["automatic_timeout_takeover"])

    def test_explicit_takeover_increments_epoch_and_fences_old_turn(self):
        old = turn_state.begin_turn(self.repo, args())
        self.assertTrue(turn_state.check_fence(self.repo, old["turn_id"], old["epoch"])["ok"])
        new = turn_state.takeover_turn(
            self.repo,
            args(reason="user opened a fresh chat because previous response is stuck", next_action="revalidate and continue"),
        )
        self.assertEqual(new["epoch"], old["epoch"] + 1)
        self.assertEqual(new["predecessor_turn_id"], old["turn_id"])
        self.assertFalse(turn_state.check_fence(self.repo, old["turn_id"], old["epoch"])["ok"])
        self.assertTrue(turn_state.check_fence(self.repo, new["turn_id"], new["epoch"])["ok"])

    def test_takeover_of_terminal_turn_is_refused(self):
        state = turn_state.begin_turn(self.repo, args())
        turn_state.complete_turn(
            self.repo,
            args(turn_id=state["turn_id"], epoch=state["epoch"], status="COMPLETED"),
        )
        with self.assertRaises(turn_state.TurnStateError):
            turn_state.takeover_turn(self.repo, args(reason="should not redo terminal work"))

    def test_repository_move_after_snapshot_requires_reconcile(self):
        turn_state.begin_turn(self.repo, args())
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "move")
        view = turn_state.recovery_view(self.repo)
        self.assertEqual(view["comparison"]["state"], "RECONCILE_REQUIRED")
        self.assertIn("head", view["comparison"]["changed"])
        self.assertIn("tree", view["comparison"]["changed"])

    def test_progress_requires_current_fence(self):
        state = turn_state.begin_turn(self.repo, args())
        with self.assertRaises(turn_state.TurnStateError):
            turn_state.progress_turn(
                self.repo,
                args(turn_id=state["turn_id"], epoch=state["epoch"] + 1),
            )

    def test_anchor_syntax_rejects_ambiguous_values(self):
        with self.assertRaises(turn_state.TurnStateError):
            turn_state.begin_turn(self.repo, args(anchor=["broken-anchor"]))

    def test_takeover_cannot_interleave_with_progress_commit(self):
        old = turn_state.begin_turn(self.repo, args())
        original = turn_state.capture_identity
        observed = []

        def during_capture(repo):
            # A separate process tries takeover after progress has checked its
            # fence but before it publishes. It must fail fast, not overwrite.
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), "takeover", str(repo),
                 "--reason", "explicit test takeover", "--json"],
                capture_output=True, text=True, timeout=10,
            )
            observed.append(result.returncode)
            return original(repo)

        with patch.object(turn_state, "capture_identity", side_effect=during_capture):
            turn_state.progress_turn(self.repo, args(turn_id=old["turn_id"], epoch=old["epoch"]))
        self.assertEqual(observed, [2])
        new = turn_state.takeover_turn(self.repo, args(reason="explicit test takeover"))
        self.assertEqual(new["epoch"], 2)
        for operation in (turn_state.progress_turn, turn_state.complete_turn):
            with self.assertRaises(turn_state.TurnStateError):
                operation(self.repo, args(turn_id=old["turn_id"], epoch=old["epoch"]))
        self.assertTrue(turn_state.check_fence(self.repo, new["turn_id"], new["epoch"])["ok"])

    def test_failed_pointer_write_preserves_previous_snapshot(self):
        old = turn_state.begin_turn(self.repo, args())
        # Simulate a pre-0.9.1 pointer targeting mutable turn/latest.json.
        base = self.repo / turn_state.DEFAULT_STATE_DIR
        legacy = base / "turns" / old["turn_id"] / "latest.json"
        legacy.write_text(json.dumps(old))
        pointer = turn_state.load_pointer(self.repo)
        pointer["turn_file"] = legacy.relative_to(self.repo).as_posix()
        (base / "latest.json").write_text(json.dumps(pointer))
        write = turn_state._atomic_write

        def fail_pointer(path, text):
            if path == self.repo / turn_state.DEFAULT_STATE_DIR / "latest.json":
                raise OSError("simulated interruption before pointer publication")
            write(path, text)

        with patch.object(turn_state, "_atomic_write", side_effect=fail_pointer):
            with self.assertRaises(OSError):
                turn_state.complete_turn(self.repo, args(turn_id=old["turn_id"], epoch=old["epoch"]))
        recovered = turn_state.load_latest_turn(self.repo)
        self.assertEqual(recovered["status"], "ACTIVE")
        self.assertEqual(recovered["event_seq"], 1)
        # The failed attempt leaves immutable evidence, not a corrupt pointer.
        completed = turn_state.complete_turn(self.repo, args(turn_id=old["turn_id"], epoch=old["epoch"]))
        self.assertTrue(completed["terminal"])

    def test_invalid_pointer_does_not_reset_fencing_epoch(self):
        turn_state.begin_turn(self.repo, args())
        pointer = self.repo / turn_state.DEFAULT_STATE_DIR / "latest.json"
        pointer.write_text(json.dumps({"schema": 99, "epoch": 12}))
        with self.assertRaises(turn_state.TurnStateError):
            turn_state.begin_turn(self.repo, args())
        self.assertEqual(json.loads(pointer.read_text())["epoch"], 12)

    def test_detached_and_linked_worktree_turn_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            linked = Path(temporary) / "linked"
            git(self.repo, "worktree", "add", "--detach", str(linked), "HEAD")
            self.assertTrue((linked / ".git").is_file())
            state = turn_state.begin_turn(linked, args())
            self.assertEqual(state["identity"]["branch"], "DETACHED")
            self.assertEqual(turn_state.recovery_view(linked)["comparison"]["state"], "EXACT")
            self.assertEqual(git(linked, "status", "--porcelain"), "")

    def test_dirty_content_change_requires_reconcile(self):
        path = self.repo / "README.md"
        path.write_text("first dirty edit")
        turn_state.begin_turn(self.repo, args())
        path.write_text("different dirty edit")
        view = turn_state.recovery_view(self.repo)
        self.assertEqual(view["comparison"]["state"], "RECONCILE_REQUIRED")
        self.assertIn("working_content_sha256", view["comparison"]["changed"])

    def test_recovery_capsule_exposes_claim_relevant_anchors(self):
        state = turn_state.begin_turn(
            self.repo,
            args(anchor=["verified_commit=abc123", "deployment=dpl_42"]),
        )
        turn_state.complete_turn(
            self.repo,
            args(turn_id=state["turn_id"], epoch=state["epoch"], status="PARTIAL"),
        )
        capsule = turn_state.render_recovery(turn_state.recovery_view(self.repo))
        self.assertIn("TERMINAL_REPLAY_AVAILABLE", capsule)
        self.assertIn("verified_commit=abc123", capsule)
        self.assertIn("deployment=dpl_42", capsule)
        self.assertIn("Response language: ko-KR", capsule)


if __name__ == "__main__":
    unittest.main()
