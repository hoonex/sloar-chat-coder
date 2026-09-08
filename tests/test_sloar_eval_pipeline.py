import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from evals.compare import EvalFormatError, compare_runs
from evals.run import run_suite


class EvalPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.suite = self.root / "suite.json"
        self.suite.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "suite_id": "pipeline-test",
                    "suite_version": "1",
                    "split": "dev",
                    "tasks": [
                        {"id": "a", "category": "bugfix", "payload": {}},
                        {"id": "b", "category": "bugfix", "payload": {}},
                        {"id": "c", "category": "feature", "payload": {}},
                        {"id": "d", "category": "feature", "payload": {}},
                        {"id": "e", "category": "refactor", "payload": {}},
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.adapter = self.root / "adapter.py"
        self.adapter.write_text(
            textwrap.dedent(
                """
                import json, os
                from pathlib import Path
                task = json.loads(Path(os.environ['SLOAR_EVAL_TASK_FILE']).read_text())
                Path(os.environ['SLOAR_EVAL_RESULT_FILE']).write_text(json.dumps({
                    'task_id': task['id'],
                    'metrics': {
                        'success': 1,
                        'regression': 0,
                        'false_completion': 0,
                        'tool_calls': 5,
                        'tokens': 100,
                    },
                }))
                """
            ),
            encoding="utf-8",
        )
        self.stable = self.root / "stable"
        self.candidate = self.root / "candidate"
        self.stable.mkdir()
        self.candidate.mkdir()
        (self.stable / "SKILL.md").write_text("stable\n", encoding="utf-8")
        (self.candidate / "SKILL.md").write_text("candidate\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, policy_id, policy_path, model_id, output):
        return run_suite(
            suite_path=self.suite,
            policy_id=policy_id,
            policy_path=policy_path,
            model_id=model_id,
            adapter_id="mock",
            adapter_version="1",
            adapter_command=[sys.executable, str(self.adapter)],
            output_path=self.root / output,
            timeout_s=5,
        )

    def test_policy_only_difference_remains_comparable(self):
        baseline = self._run("stable", self.stable, "same-model", "baseline.json")
        candidate = self._run("candidate", self.candidate, "same-model", "candidate.json")

        result = compare_runs(baseline, candidate)

        self.assertEqual(baseline["suite_version"], candidate["suite_version"])
        self.assertNotEqual(
            baseline["execution"]["policy_sha256"],
            candidate["execution"]["policy_sha256"],
        )
        self.assertEqual(result["decision"], "EXPERIMENT_ONLY")

    def test_model_change_is_rejected_as_noncomparable(self):
        baseline = self._run("stable", self.stable, "model-a", "baseline.json")
        candidate = self._run("candidate", self.candidate, "model-b", "candidate.json")

        with self.assertRaises(EvalFormatError):
            compare_runs(baseline, candidate)


if __name__ == "__main__":
    unittest.main()
