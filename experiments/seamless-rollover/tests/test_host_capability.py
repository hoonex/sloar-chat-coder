import unittest
from pathlib import Path


PROTOCOL_PATH = Path(__file__).resolve().parents[1] / "PROTOCOL.md"


class HostCapabilityContractTests(unittest.TestCase):
    def test_pre_response_host_capability_blocker_is_explicit(self):
        protocol = PROTOCOL_PATH.read_text(encoding="utf-8")
        self.assertIn("#### Host capability boundary", protocol)
        self.assertIn("PRE_RESPONSE_READ_BLOCKED", protocol)
        self.assertIn(
            "do not repeat the same fresh-chat validation under unchanged host conditions",
            protocol,
        )
        self.assertIn(
            "Exit `PRE_RESPONSE_READ_BLOCKED` only when the host either permits a silent durable read before visible output or provides an authenticated early `response_language` hint before visible output.",
            protocol,
        )


if __name__ == "__main__":
    unittest.main()
