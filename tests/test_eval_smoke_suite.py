import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from evals.adapters import codex_cli


class EvalSmokeSuiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.suite = json.loads((cls.root / "evals/suites/smoke-dev.json").read_text(encoding="utf-8"))

    def test_clean_fixture_is_green(self):
        fixture = self.root / "evals/fixtures/python-utils"
        completed = subprocess.run(
            ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=fixture,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

    def test_every_smoke_task_starts_red_after_seed_patch(self):
        self.assertEqual(self.suite["split"], "dev")
        self.assertGreaterEqual(len(self.suite["tasks"]), 2)
        for task in self.suite["tasks"]:
            with self.subTest(task=task["id"]), tempfile.TemporaryDirectory() as temp_name:
                output = Path(temp_name)
                worktree = codex_cli._materialize_repository(
                    task,
                    output_dir=output,
                    adapter_cwd=self.root,
                )
                acceptance, timeout_s = codex_cli._verification_spec(task, "acceptance")
                completed = subprocess.run(
                    acceptance,
                    cwd=worktree,
                    capture_output=True,
                    text=True,
                    timeout=timeout_s,
                    check=False,
                )
                self.assertNotEqual(
                    completed.returncode,
                    0,
                    f"{task['id']} seed must reproduce a failing acceptance check",
                )
                shutil.rmtree(worktree)


if __name__ == "__main__":
    unittest.main()
