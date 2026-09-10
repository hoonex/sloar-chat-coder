import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "benchmarks" / "forge_sloar" / "score.py"
SPEC = importlib.util.spec_from_file_location("forge_sloar_score", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ForgeSloarBenchmarkTests(unittest.TestCase):
    def test_negative_clamps_to_zero(self):
        self.assertEqual(MODULE.normalize_score(-7), 0)

    def test_midrange_is_preserved(self):
        self.assertEqual(MODULE.normalize_score(42), 42)

    def test_above_max_clamps_to_hundred(self):
        self.assertEqual(MODULE.normalize_score(101), 100)


if __name__ == "__main__":
    unittest.main()
