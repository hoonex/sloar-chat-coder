import copy
import unittest

from evals.compare import EvalFormatError, compare_runs


def make_run(run_id="base", policy_id="stable", split="holdout"):
    categories = ["bugfix", "bugfix", "feature", "feature", "refactor", "refactor"]
    metrics = [
        dict(success=1, regression=0, false_completion=0, correction_distance=.20, tool_calls=12, tokens=12000, wall_time_s=120),
        dict(success=0, regression=0, false_completion=0, correction_distance=.40, tool_calls=14, tokens=14000, wall_time_s=140),
        dict(success=1, regression=0, false_completion=0, correction_distance=.25, tool_calls=13, tokens=13000, wall_time_s=130),
        dict(success=0, regression=0, false_completion=1, correction_distance=.50, tool_calls=16, tokens=16000, wall_time_s=160),
        dict(success=1, regression=0, false_completion=0, correction_distance=.15, tool_calls=10, tokens=10000, wall_time_s=100),
        dict(success=1, regression=0, false_completion=0, correction_distance=.20, tool_calls=11, tokens=11000, wall_time_s=110),
    ]
    return {
        "schema": 1,
        "suite_id": "sloar-core",
        "suite_version": "2026-09-08.1",
        "split": split,
        "run_id": run_id,
        "policy_id": policy_id,
        "tasks": [
            {"id": f"task-{index}", "category": category, "metrics": row}
            for index, (category, row) in enumerate(zip(categories, metrics), 1)
        ],
    }


class SloarEvalTests(unittest.TestCase):
    def test_holdout_candidate_can_promote_on_material_success_gain(self):
        baseline = make_run()
        candidate = copy.deepcopy(baseline)
        candidate["run_id"] = "candidate"
        candidate["policy_id"] = "candidate-policy"
        candidate["tasks"][1]["metrics"]["success"] = 1
        candidate["tasks"][3]["metrics"]["success"] = 1
        candidate["tasks"][3]["metrics"]["false_completion"] = 0
        for task in candidate["tasks"]:
            task["metrics"]["tool_calls"] *= .9
            task["metrics"]["tokens"] *= .9
            task["metrics"]["wall_time_s"] *= .9

        result = compare_runs(baseline, candidate)

        self.assertEqual(result["decision"], "PROMOTE")
        self.assertTrue(result["hard_gates_passed"])
        self.assertGreater(result["deltas"]["success_rate"], 0)

    def test_dev_split_never_becomes_promotion_evidence(self):
        baseline = make_run(split="dev")
        candidate = copy.deepcopy(baseline)
        candidate["policy_id"] = "candidate-policy"
        candidate["tasks"][1]["metrics"]["success"] = 1
        candidate["tasks"][3]["metrics"]["success"] = 1
        candidate["tasks"][3]["metrics"]["false_completion"] = 0

        result = compare_runs(baseline, candidate)

        self.assertEqual(result["decision"], "EXPERIMENT_ONLY")

    def test_hard_gate_rejects_regression_even_when_success_improves(self):
        baseline = make_run()
        candidate = copy.deepcopy(baseline)
        candidate["policy_id"] = "candidate-policy"
        candidate["tasks"][1]["metrics"]["success"] = 1
        candidate["tasks"][0]["metrics"]["regression"] = 1

        result = compare_runs(baseline, candidate)

        self.assertEqual(result["decision"], "REJECT")
        self.assertIn(
            "regression_rate_non_regression",
            {row["name"] for row in result["gates"] if not row["passed"]},
        )

    def test_category_gate_catches_hidden_subgroup_regression(self):
        baseline = make_run()
        candidate = copy.deepcopy(baseline)
        candidate["policy_id"] = "candidate-policy"
        # Overall success is held: lose one bugfix, gain one feature.
        candidate["tasks"][0]["metrics"]["success"] = 0
        candidate["tasks"][3]["metrics"]["success"] = 1
        candidate["tasks"][3]["metrics"]["false_completion"] = 0

        result = compare_runs(baseline, candidate)

        self.assertEqual(result["decision"], "REJECT")
        self.assertIn(
            "category:bugfix:success_non_regression",
            {row["name"] for row in result["gates"] if not row["passed"]},
        )

    def test_non_regressing_candidate_without_material_gain_does_not_promote(self):
        baseline = make_run()
        candidate = copy.deepcopy(baseline)
        candidate["policy_id"] = "candidate-policy"

        result = compare_runs(baseline, candidate)

        self.assertEqual(result["decision"], "NO_PROMOTION")
        self.assertTrue(result["hard_gates_passed"])

    def test_mismatched_task_ids_are_invalid(self):
        baseline = make_run()
        candidate = copy.deepcopy(baseline)
        candidate["tasks"].pop()

        with self.assertRaises(EvalFormatError):
            compare_runs(baseline, candidate)

    def test_mismatched_suite_version_is_invalid(self):
        baseline = make_run()
        candidate = copy.deepcopy(baseline)
        candidate["suite_version"] = "different"

        with self.assertRaises(EvalFormatError):
            compare_runs(baseline, candidate)


if __name__ == "__main__":
    unittest.main()
