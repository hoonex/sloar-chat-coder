import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/sloar-chat-coder/scripts/android-preflight.py"


class AndroidPreflightTest(unittest.TestCase):
    def run_preflight(self, target: Path) -> dict:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(target), "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(proc.stdout)

    def test_empty_repository_is_bootstrap_state(self):
        with tempfile.TemporaryDirectory() as td:
            data = self.run_preflight(Path(td))
            self.assertEqual(data["schema"], 1)
            self.assertEqual(data["state"], "EMPTY_OR_NON_ANDROID")
            self.assertFalse(data["project"]["gradle_wrapper"])
            self.assertFalse(data["device_verification_required"])
            self.assertEqual(data["evidence_defaults"]["thermal"], "UNVERIFIED")
            self.assertTrue(any("applicationId" in item for item in data["next_actions"]))

    def test_android_project_detects_identity_and_device_risks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "gradlew").write_text("#!/bin/sh\n", encoding="utf-8")
            (root / "settings.gradle.kts").write_text('rootProject.name = "demo"\ninclude(":app")\n', encoding="utf-8")
            app = root / "app"
            src = app / "src/main/java/com/example"
            src.mkdir(parents=True)
            (app / "build.gradle.kts").write_text(
                '''plugins { id("com.android.application") }\n'''
                '''android { namespace = "com.example.demo"; compileSdk = 36\n'''
                '''defaultConfig { applicationId = "com.example.demo"; minSdk = 24; targetSdk = 36 } }\n''',
                encoding="utf-8",
            )
            manifest = app / "src/main/AndroidManifest.xml"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text("<manifest package=\"com.example.demo\"/>\n", encoding="utf-8")
            (src / "Core.kt").write_text(
                '''import android.hardware.SensorManager\n'''
                '''fun hot() { val mode = SensorManager.SENSOR_DELAY_FASTEST; while (true) { Thread.sleep(1) } }\n''',
                encoding="utf-8",
            )

            data = self.run_preflight(root)
            self.assertEqual(data["state"], "EXISTING_ANDROID")
            self.assertEqual(data["project"]["application_id"], "com.example.demo")
            self.assertTrue(data["project"]["placeholder_identity"])
            self.assertTrue(data["project"]["gradle_wrapper"])
            self.assertTrue(data["device_verification_required"])
            kinds = {item["kind"] for item in data["risk_hints"]}
            self.assertIn("busy_loop_review", kinds)
            self.assertIn("high_rate_sensor", kinds)
            self.assertIn("tight_timer", kinds)
            self.assertTrue(any("thermal" in item.lower() for item in data["next_actions"]))


if __name__ == "__main__":
    unittest.main()
