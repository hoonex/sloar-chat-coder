import unittest

from utils import clamp, parse_bool


class UtilsTests(unittest.TestCase):
    def test_clamp_bounds(self):
        self.assertEqual(clamp(-5, 0, 10), 0)
        self.assertEqual(clamp(15, 0, 10), 10)
        self.assertEqual(clamp(4, 0, 10), 4)

    def test_clamp_rejects_inverted_range(self):
        with self.assertRaises(ValueError):
            clamp(2, 3, 1)

    def test_parse_bool_false_values(self):
        for value in ("0", "false", "NO", " off "):
            with self.subTest(value=value):
                self.assertIs(parse_bool(value), False)

    def test_parse_bool_true_values(self):
        for value in ("1", "true", "YES", " on "):
            with self.subTest(value=value):
                self.assertIs(parse_bool(value), True)

    def test_parse_bool_rejects_unknown(self):
        with self.assertRaises(ValueError):
            parse_bool("maybe")


if __name__ == "__main__":
    unittest.main()
