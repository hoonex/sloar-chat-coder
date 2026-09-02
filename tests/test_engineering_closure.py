import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/sloar-chat-coder/scripts/engineering-closure.py"


class EngineeringClosureTest(unittest.TestCase):
    def run_closure(self, record: dict, expected_code: int = 0) -> dict:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "record.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--json"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, expected_code, proc.stderr or proc.stdout)
            return json.loads(proc.stdout)

    def test_ready_when_claims_owners_and_convergence_close(self):
        data = self.run_closure({
            "ownership": [{
                "decision": "responsive-mode",
                "authoritative_owner": "shell.css",
                "writers": ["shell.css"],
                "independent_deciders": ["shell.css"],
            }],
            "claims": [{
                "id": "mobile-flick",
                "target": "abc",
                "requires": ["real-touch", "post-release", "final-snap"],
                "evidence": ["touch-audit"],
            }],
            "evidence": [{
                "id": "touch-audit",
                "target": "abc",
                "result": "pass",
                "covers": ["real-touch", "post-release", "final-snap"],
            }],
            "convergence": {
                "required": ["source", "verified", "packaged", "deployed", "served"],
                "observed": {
                    "source": "abc",
                    "verified": "abc",
                    "packaged": "abc",
                    "deployed": "dep1",
                    "served": "abc",
                },
            },
        })
        self.assertEqual(data["status"], "READY")
        self.assertEqual(data["summary"]["claims_closed"], 1)
        self.assertFalse(data["findings"])

    def test_blocks_split_ownership_stale_evidence_and_convergence_gap(self):
        data = self.run_closure({
            "ownership": [{
                "decision": "responsive-mode",
                "authoritative_owner": "shell.css",
                "writers": ["shell.css", "v2.css"],
                "independent_deciders": ["shell.css", "v2.css"],
            }],
            "claims": [{
                "id": "mobile-flick",
                "target": "new",
                "requires": ["real-touch", "post-release"],
                "evidence": ["old-touch"],
            }],
            "evidence": [{
                "id": "old-touch",
                "target": "old",
                "result": "pass",
                "covers": ["real-touch", "post-release"],
            }],
            "features": [{"id": "transit", "status": "retired"}],
            "gates": [{
                "id": "transit-live",
                "feature": "transit",
                "result": "red",
                "task_affects_feature": False,
            }],
            "convergence": {
                "required": ["source", "verified", "served"],
                "observed": {"source": "new", "verified": "new"},
            },
        }, expected_code=2)
        codes = {item["code"] for item in data["findings"]}
        self.assertEqual(data["status"], "BLOCKED")
        self.assertIn("OWNERSHIP_SPLIT", codes)
        self.assertIn("EVIDENCE_GAP", codes)
        self.assertIn("STALE_GATE_SUSPECTED", codes)
        self.assertIn("CONVERGENCE_GAP", codes)
        claim = data["claims"][0]
        self.assertEqual(claim["status"], "open")
        self.assertEqual(claim["stale_evidence"], ["old-touch"])

    def test_retired_gate_is_review_not_product_failure(self):
        data = self.run_closure({
            "features": [{"id": "legacy", "status": "dormant"}],
            "gates": [{
                "id": "legacy-ci",
                "feature": "legacy",
                "result": "failed",
                "task_affects_feature": False,
            }],
        }, expected_code=2)
        self.assertEqual(data["status"], "REVIEW")
        self.assertEqual(data["summary"]["p0"], 0)
        self.assertEqual(data["summary"]["p1"], 1)
        self.assertEqual(data["findings"][0]["code"], "STALE_GATE_SUSPECTED")


if __name__ == "__main__":
    unittest.main()
