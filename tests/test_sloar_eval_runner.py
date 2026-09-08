import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from evals.run import RunnerError, hash_policy_path, run_suite


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.suite = self.root / "suite.json"
        self.policy = self.root / "policy"
        self.policy.mkdir()
        (self.policy / "SKILL.md").write_text("policy-v1\n", encoding="utf-8")
        self.suite.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "suite_id": "runner-test",
                    "suite_version": "1",
                    "split": "dev",
                    "tasks": [
                        {"id": "task-a", "category": "bugfix", "payload": {"value": 1}},
                        {"id": "task-b", "category": "feature", "payload": {"value": 2}},
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
                out = Path(os.environ['SLOAR_EVAL_RESULT_FILE'])
                trajectory = Path(os.environ['SLOAR_EVAL_TRAJECTORY_FILE'])
                metrics = {
                    'success': 1,
                    'regression': 0,
                    'false_completion': 0,
                    'tool_calls': task['payload']['value'] + 3,
                    'tokens': 100 + task['payload']['value'],
                    'wall_time_s': 9999,
                }
                out.write_text(json.dumps({'task_id': task['id'], 'metrics': metrics}))
                trajectory.write_text(json.dumps({'event': 'done', 'task': task['id']}) + '\\n')
                """
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *, policy_path=None, model_id="gpt-test", output="run.json", run_id="run-fixed"):
        return run_suite(
            suite_path=self.suite,
            policy_id="stable",
            policy_path=policy_path or self.policy,
            model_id=model_id,
            adapter_id="mock",
            adapter_version="1",
            adapter_command=[sys.executable, str(self.adapter)],
            output_path=self.root / output,
            run_id=run_id,
            timeout_s=5,
        )

    def test_runner_emits_bundle_identity_and_artifact_digests(self):
        output = self.root / "run.json"
        bundle = self._run()

        self.assertEqual(bundle["run_id"], "run-fixed")
        self.assertEqual(bundle["execution"]["policy_sha256"], hash_policy_path(self.policy))
        self.assertEqual(bundle["execution"]["model_id"], "gpt-test")
        self.assertTrue(bundle["suite_version"].startswith("1+ctx."))
        self.assertEqual(bundle["execution"]["declared_suite_version"], "1")
        self.assertEqual([row["id"] for row in bundle["tasks"]], ["task-a", "task-b"])
        self.assertTrue(all(row["artifacts"]["trajectory_present"] for row in bundle["tasks"]))
        self.assertTrue(all(row["metrics"]["wall_time_s"] < 5 for row in bundle["tasks"]))
        self.assertEqual(json.loads(output.read_text())["execution"]["adapter_id"], "mock")

    def test_comparison_identity_changes_with_model_but_not_policy(self):
        first = self._run(output="first.json", run_id="first")
        other_policy = self.root / "other-policy"
        other_policy.mkdir()
        (other_policy / "SKILL.md").write_text("candidate\n", encoding="utf-8")
        second = self._run(policy_path=other_policy, output="second.json", run_id="second")
        third = self._run(
            policy_path=other_policy,
            model_id="different-model",
            output="third.json",
            run_id="third",
        )

        self.assertEqual(first["suite_version"], second["suite_version"])
        self.assertNotEqual(first["execution"]["policy_sha256"], second["execution"]["policy_sha256"])
        self.assertNotEqual(first["suite_version"], third["suite_version"])

    def test_policy_digest_changes_when_policy_bytes_change(self):
        before = hash_policy_path(self.policy)
        (self.policy / "SKILL.md").write_text("policy-v2\n", encoding="utf-8")
        after = hash_policy_path(self.policy)
        self.assertNotEqual(before, after)

    def test_policy_mutation_invalidates_run(self):
        with self.adapter.open("a") as handle:
            handle.write("\n(Path(os.environ['SLOAR_EVAL_POLICY_PATH']) / 'SKILL.md').write_text('changed')\n")
        with self.assertRaisesRegex(RunnerError, "policy bytes changed"):
            self._run()
        self.assertFalse((self.root / "run.json").exists())

    def test_nonzero_adapter_is_infrastructure_failure_not_model_failure(self):
        bad = self.root / "bad.py"
        bad.write_text("raise SystemExit(7)\n", encoding="utf-8")
        with self.assertRaises(RunnerError):
            run_suite(
                suite_path=self.suite,
                policy_id="candidate",
                policy_path=self.policy,
                model_id="gpt-test",
                adapter_id="bad",
                adapter_version="1",
                adapter_command=[sys.executable, str(bad)],
                output_path=self.root / "bad-run.json",
                timeout_s=5,
            )

    def test_missing_result_is_runner_failure(self):
        noop = self.root / "noop.py"
        noop.write_text("print('nothing')\n", encoding="utf-8")
        with self.assertRaises(RunnerError):
            run_suite(
                suite_path=self.suite,
                policy_id="candidate",
                policy_path=self.policy,
                model_id="gpt-test",
                adapter_id="noop",
                adapter_version="1",
                adapter_command=[sys.executable, str(noop)],
                output_path=self.root / "noop-run.json",
                timeout_s=5,
            )


if __name__ == "__main__":
    unittest.main()
