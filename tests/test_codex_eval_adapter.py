import json
import os
import stat
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.adapters import codex_cli


class CodexEvalAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = self.root / "fixture"
        self.fixture.mkdir()
        (self.fixture / "calc.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
        tests = self.fixture / "tests"
        tests.mkdir()
        (tests / "test_calc.py").write_text(
            "import unittest\n"
            "from calc import add\n\n"
            "class CalcTests(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n",
            encoding="utf-8",
        )
        self.policy = self.root / "policy"
        self.policy.mkdir()
        (self.policy / "SKILL.md").write_text("# Test Sloar policy\n", encoding="utf-8")
        self.output = self.root / "output"
        self.output.mkdir()
        self.task = {
            "id": "bugfix-add",
            "prompt": "Fix add() so ordinary addition works.",
            "repository": {"fixture_path": str(self.fixture)},
            "verification": {
                "acceptance": {"command": ["python3", "-m", "unittest", "tests.test_calc", "-v"]},
                "regression": {"command": ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"]},
            },
        }
        self.task_file = self.output / "task.json"
        self.task_file.write_text(json.dumps(self.task), encoding="utf-8")
        self.fake_codex = self.root / "fake-codex"
        self._write_fake_codex(fix=True)
        self.env = {
            "SLOAR_EVAL_TASK_ID": "bugfix-add",
            "SLOAR_EVAL_TASK_FILE": str(self.task_file),
            "SLOAR_EVAL_POLICY_PATH": str(self.policy),
            "SLOAR_EVAL_MODEL_ID": "gpt-5.6-sol",
            "SLOAR_EVAL_OUTPUT_DIR": str(self.output),
            "SLOAR_EVAL_RESULT_FILE": str(self.output / "result.json"),
            "SLOAR_EVAL_TRAJECTORY_FILE": str(self.output / "trajectory.jsonl"),
        }

    def tearDown(self):
        self.temp.cleanup()

    def _write_fake_codex(self, *, fix: bool) -> None:
        change = "(worktree / 'calc.py').write_text('def add(a, b):\\n    return a + b\\n')" if fix else "pass"
        self.fake_codex.write_text(
            textwrap.dedent(
                f"""\
                #!/usr/bin/env python3
                import json
                import pathlib
                import sys

                args = sys.argv[1:]
                worktree = pathlib.Path(args[args.index('--cd') + 1])
                output = pathlib.Path(args[args.index('--output-last-message') + 1])
                {change}
                output.write_text(json.dumps({{'status': 'completed', 'summary': 'done'}}))
                print(json.dumps({{'type': 'turn.completed'}}))
                """
            ),
            encoding="utf-8",
        )
        self.fake_codex.chmod(self.fake_codex.stat().st_mode | stat.S_IXUSR)

    def test_objective_verification_marks_success(self):
        with patch.dict(os.environ, self.env, clear=False):
            result = codex_cli.evaluate_task(
                codex_bin=str(self.fake_codex),
                reasoning_effort="high",
                codex_timeout_s=30,
                adapter_cwd=self.root,
            )

        self.assertEqual(result["metrics"], {"success": 1.0, "regression": 0.0, "false_completion": 0.0})
        self.assertTrue((self.output / "patch.diff").is_file())
        self.assertTrue((self.output / "trajectory.jsonl").is_file())

    def test_completed_claim_with_failed_acceptance_is_false_completion(self):
        self._write_fake_codex(fix=False)
        with patch.dict(os.environ, self.env, clear=False):
            result = codex_cli.evaluate_task(
                codex_bin=str(self.fake_codex),
                reasoning_effort="high",
                codex_timeout_s=30,
                adapter_cwd=self.root,
            )

        self.assertEqual(result["metrics"]["success"], 0.0)
        self.assertEqual(result["metrics"]["regression"], 1.0)
        self.assertEqual(result["metrics"]["false_completion"], 1.0)

    def test_codex_command_pins_model_sandbox_and_noninteractive_policy(self):
        command = codex_cli.build_codex_command(
            codex_bin="codex",
            model_id="gpt-5.6-sol",
            worktree=Path("/worktree"),
            policy_path=Path("/policy"),
            schema_file=Path("/schema.json"),
            last_message_file=Path("/last.json"),
            reasoning_effort="high",
        )

        self.assertEqual(command[:4], ["codex", "exec", "--json", "--model"])
        self.assertIn("gpt-5.6-sol", command)
        self.assertIn("workspace-write", command)
        self.assertIn('approval_policy="never"', command)
        self.assertIn('web_search="disabled"', command)
        self.assertIn("sandbox_workspace_write.network_access=false", command)
        self.assertNotIn("--add-dir", command)

    def _evaluate(self):
        with patch.dict(os.environ, self.env, clear=False):
            return codex_cli.evaluate_task(codex_bin=str(self.fake_codex), reasoning_effort="medium", codex_timeout_s=30, adapter_cwd=self.root)

    def test_weakening_tests_cannot_earn_success(self):
        self._write_fake_codex(fix=False)
        script = self.fake_codex.read_text().replace(
            "output.write_text(",
            "(worktree / 'tests/test_calc.py').write_text('import unittest\\nclass CalcTests(unittest.TestCase):\\n def test_add(self): pass\\n')\noutput.write_text(",
        )
        self.fake_codex.write_text(script)
        result = self._evaluate()
        self.assertIn("changed", result["verification_integrity_error"])
        self.assertEqual(result["metrics"], {"success": 0.0, "regression": 1.0, "false_completion": 1.0})
        self.assertIn("return a - b", (self.output / "worktree/calc.py").read_text())
        self.assertFalse(json.loads((self.output / "verify-acceptance.json").read_text())["executed"])

    def test_patch_includes_agent_commits_and_new_files(self):
        script = self.fake_codex.read_text().replace(
            "output.write_text(",
            "import subprocess\nsubprocess.run(['git', '-C', str(worktree), 'commit', '-am', 'fix'], check=True, capture_output=True)\n(worktree / 'new_module.py').write_text('VALUE = 42\\n')\noutput.write_text(",
        )
        self.fake_codex.write_text(script)
        result = self._evaluate()
        artifact = (self.output / "patch.diff").read_text()
        self.assertIn("+    return a + b", artifact)
        self.assertIn("+VALUE = 42", artifact)
        self.assertNotEqual(result["repository"]["base_commit"], result["repository"]["final_commit"])

    def test_regression_failure_also_invalidates_completion_claim(self):
        self.task["verification"]["acceptance"]["command"] = ["python3", "-m", "unittest", "tests.test_calc.CalcTests.test_add"]
        self.task_file.write_text(json.dumps(self.task))
        with (self.fixture / "tests/test_calc.py").open("a") as handle:
            handle.write("\n    def test_unrelated_failure(self):\n        self.fail('existing required gate')\n")
        result = self._evaluate()
        self.assertEqual(result["metrics"], {"success": 1.0, "regression": 1.0, "false_completion": 1.0})

    def test_local_adapter_cannot_claim_hidden_holdout_evidence(self):
        with patch.dict(os.environ, {**self.env, "SLOAR_EVAL_SPLIT": "holdout"}):
            with self.assertRaisesRegex(codex_cli.AdapterError, "isolated evaluator"):
                codex_cli.evaluate_task(codex_bin=str(self.fake_codex), reasoning_effort="high", codex_timeout_s=30)

    def test_mutable_repository_ref_is_rejected_before_clone(self):
        self.task["repository"] = {"url": "https://github.com/example/project", "commit": "release-branch"}
        with self.assertRaisesRegex(codex_cli.AdapterError, "immutable commit SHA"):
            codex_cli._materialize_repository(self.task, output_dir=self.output, adapter_cwd=self.root)


if __name__ == "__main__":
    unittest.main()
