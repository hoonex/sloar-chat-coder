import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from argparse import Namespace
from pathlib import Path

from evals.compare import compare_runs
from evals.run import run_suite


ROOT = Path(__file__).resolve().parents[1]
SLOAR = ROOT / ".agents/skills/sloar-chat-coder"
SCRIPTS = SLOAR / "scripts"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def run(*args, cwd=None, expected=0):
    proc = subprocess.run(
        [str(arg) for arg in args],
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != expected:
        raise AssertionError(
            f"exit {proc.returncode} != {expected}: {' '.join(map(str, args))}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def as_json(*args, cwd=None, expected=0):
    proc = run(*args, cwd=cwd, expected=expected)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON from {' '.join(map(str, args))}: {proc.stdout}") from exc


def git(repo: Path, *args: str, expected=0):
    return run("git", "-C", repo, *args, expected=expected)


def init_repo(root: Path, name="target") -> Path:
    repo = root / name
    repo.mkdir(parents=True)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "audit@example.com")
    git(repo, "config", "user.name", "Sloar Audit")
    git(repo, "remote", "add", "origin", f"https://github.com/example/{name}.git")
    (repo / "AGENTS.md").write_text("# Existing guidance\n", encoding="utf-8")
    (repo / "product.txt").write_text("product-v1\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "baseline")
    return repo


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FullSystemAuditTests(unittest.TestCase):
    """Cross-feature acceptance audit layered on top of the focused regression suite."""

    def test_01_every_local_entrypoint_starts_and_self_tests_pass(self):
        python_scripts = sorted(SCRIPTS.glob("*.py"))
        shell_scripts = sorted(SCRIPTS.glob("*.sh"))
        self.assertGreaterEqual(len(python_scripts), 9)
        self.assertGreaterEqual(len(shell_scripts), 2)

        for script in python_scripts:
            with self.subTest(script=script.name):
                proc = run(sys.executable, script, "--help")
                self.assertIn("usage:", proc.stdout.lower())
        for script in shell_scripts:
            with self.subTest(shell=script.name):
                run("bash", "-n", script)

        self.assertIn("sloar self-test: ok", run("bash", SCRIPTS / "preflight.sh", "--self-test").stdout)
        self.assertIn("ref cleanup: ok", run(sys.executable, SCRIPTS / "ref-cleanup.py", "--self-test").stdout)

        for path in (
            ROOT / "evals/run.py",
            ROOT / "evals/run_pair.py",
            ROOT / "evals/compare.py",
            ROOT / "evals/adapters/codex_cli.py",
        ):
            with self.subTest(eval_cli=path.name):
                self.assertIn("usage:", run(sys.executable, path, "--help").stdout.lower())

    def test_02_install_readiness_identity_and_checkpoint_chain_stays_clean(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td))
            product_before = (repo / "product.txt").read_bytes()

            run(sys.executable, SCRIPTS / "install.py", "--target", repo)
            # Exercise idempotency before committing the installation.
            run(sys.executable, SCRIPTS / "install.py", "--target", repo)
            self.assertEqual((repo / "AGENTS.md").read_text().count("sloar-chat-coder:begin"), 1)
            self.assertEqual((repo / "product.txt").read_bytes(), product_before)
            for skill in ("sloar-chat-coder", "web-design-guidance", "apple-web-design"):
                self.assertTrue((repo / f".agents/skills/{skill}/SKILL.md").is_file())

            git(repo, "add", ".")
            git(repo, "commit", "-m", "install Sloar")
            self.assertEqual(git(repo, "status", "--porcelain=v1").stdout, "")

            local_scripts = repo / ".agents/skills/sloar-chat-coder/scripts"
            doctor = as_json(sys.executable, local_scripts / "doctor.py", repo, "--json")
            wizard = as_json(
                sys.executable,
                local_scripts / "wizard.py",
                repo,
                "--stable-version",
                VERSION,
                "--json",
            )
            self.assertTrue(doctor["git"]["is_worktree"])
            self.assertTrue(doctor["sloar_installed"])
            self.assertEqual(wizard["updates"]["status"], "current")
            self.assertEqual(wizard["resilience"]["local_status"], "LOCAL_READY")
            self.assertEqual(wizard["engineering_closure"]["helper"], "ready")
            self.assertEqual(wizard["design"]["web_design_companion"], "ready")

            # Python actually creates runtime cache, but the installed Skill must hide it from Git state.
            self.assertTrue(list((repo / ".agents/skills/sloar-chat-coder").rglob("__pycache__")))
            self.assertEqual(git(repo, "status", "--porcelain=v1").stdout, "")

            head = git(repo, "rev-parse", "HEAD").stdout.strip()
            tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
            preflight = run("bash", local_scripts / "preflight.sh", repo).stdout
            self.assertIn(f"head={head}", preflight)
            self.assertIn(f"tree={tree}", preflight)
            self.assertIn("dirty=false", preflight)
            run("bash", local_scripts / "verify-state.sh", head, tree, repo)

            checkpoint = Path(td) / "checkpoint.json"
            run(
                sys.executable,
                local_scripts / "write-checkpoint.py",
                "--worktree",
                repo,
                "--repository",
                "example/target",
                "--stage",
                "VERIFY",
                "--base",
                head,
                "--output",
                checkpoint,
            )
            saved = json.loads(checkpoint.read_text(encoding="utf-8"))
            self.assertEqual(saved["head"], head)
            self.assertEqual(saved["tree"], tree)
            self.assertEqual(saved["stage"], "VERIFY")
            self.assertFalse(saved["dirty"])

    def test_03_rollover_turn_recovery_takeover_and_fencing_chain(self):
        turn_state = load_module("full_audit_turn_state", SCRIPTS / "turn-state.py")

        def ns(**overrides):
            data = dict(
                goal="finish audit",
                completed=[],
                active=["verification"],
                pending=["remote verify"],
                decision=[],
                evidence=[],
                blocker=[],
                next_action="continue",
                response_language="ko-KR",
                anchor=[],
                changed=[],
                preserved=[],
                not_changed=[],
                limitation=[],
                turn_id=None,
                epoch=None,
                status="COMPLETED",
                terminal_note=None,
                reason=None,
            )
            data.update(overrides)
            return Namespace(**data)

        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td))
            rollover = SCRIPTS / "session-rollover.py"
            handoff = as_json(
                sys.executable,
                rollover,
                "handoff",
                repo,
                "--goal",
                "finish full audit",
                "--completed",
                "install check",
                "--pending",
                "remote verify",
                "--next",
                "resume safely",
                "--response-language",
                "ko-KR",
                "--json",
            )
            self.assertEqual(handoff["checkpoint"]["context"]["response_language"], "ko-KR")
            exact = as_json(sys.executable, rollover, "resume", repo, "--json")
            self.assertEqual(exact["comparison"]["state"], "EXACT")

            old = turn_state.begin_turn(repo, ns(anchor=["verified=head-a"]))
            progressed = turn_state.progress_turn(
                repo,
                ns(turn_id=old["turn_id"], epoch=old["epoch"], evidence=["tests:green"]),
            )
            self.assertEqual(progressed["event_seq"], 2)
            self.assertTrue(turn_state.check_fence(repo, old["turn_id"], old["epoch"])["ok"])

            new = turn_state.takeover_turn(repo, ns(reason="explicit fresh-chat takeover"))
            self.assertEqual(new["epoch"], old["epoch"] + 1)
            self.assertFalse(turn_state.check_fence(repo, old["turn_id"], old["epoch"])["ok"])
            self.assertTrue(turn_state.check_fence(repo, new["turn_id"], new["epoch"])["ok"])

            terminal = turn_state.complete_turn(
                repo,
                ns(
                    turn_id=new["turn_id"],
                    epoch=new["epoch"],
                    status="PARTIAL",
                    terminal_note="provider-backed acceptance remains external",
                ),
            )
            self.assertTrue(terminal["terminal"])
            recovery = turn_state.recovery_view(repo)
            self.assertEqual(recovery["recovery_state"], "TERMINAL_REPLAY_AVAILABLE")
            self.assertEqual(recovery["comparison"]["state"], "EXACT")

            # Repository movement after the rollover snapshot must not be mistaken for exact continuity.
            (repo / "product.txt").write_text("product-v2\n", encoding="utf-8")
            git(repo, "add", "product.txt")
            git(repo, "commit", "-m", "move")
            moved = as_json(sys.executable, rollover, "resume", repo, "--json")
            self.assertEqual(moved["comparison"]["state"], "RECONCILE_REQUIRED")
            self.assertIn("head", moved["comparison"]["changed"])
            self.assertIn("tree", moved["comparison"]["changed"])

    def test_04_resilience_android_and_engineering_closure_matrix(self):
        forge = SCRIPTS / "forge-health.py"
        cleanup = SCRIPTS / "ref-cleanup.py"

        rate = as_json(sys.executable, forge, "--classify-error", "HTTP 429 secondary rate limit exceeded", "--json")
        moved = as_json(sys.executable, forge, "--classify-error", "rejected non-fast-forward; fetch first", "--json")
        permission = as_json(
            sys.executable,
            forge,
            "--classify-error",
            "refusing to allow a GitHub App to create or update workflow without workflows permission",
            "--json",
        )
        self.assertEqual(rate["classification"], "REMOTE_DEGRADED")
        self.assertEqual(moved["classification"], "REMOTE_MOVED")
        self.assertEqual(permission["classification"], "CAPABILITY_MISMATCH")
        self.assertEqual(permission["remote_state"], "REMOTE_PARTIAL")

        ready = as_json(
            sys.executable,
            cleanup,
            "--branch",
            "audit/tmp",
            "--lifecycle",
            "closed",
            "--delete-capability",
            "available",
            "--temporary",
            "--json",
        )
        blocked = as_json(
            sys.executable,
            cleanup,
            "--branch",
            "main",
            "--lifecycle",
            "merged",
            "--delete-capability",
            "available",
            "--default-branch",
            "main",
            "--json",
        )
        self.assertEqual(ready["classification"], "REF_DELETE_READY")
        self.assertEqual(blocked["classification"], "REF_DELETE_PROHIBITED")

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            android = SCRIPTS / "android-preflight.py"
            self.assertEqual(as_json(sys.executable, android, root, "--json")["state"], "EMPTY_OR_NON_ANDROID")

            app = root / "android"
            src = app / "app/src/main/java/com/example"
            src.mkdir(parents=True)
            (app / "gradlew").write_text("#!/bin/sh\n", encoding="utf-8")
            (app / "settings.gradle.kts").write_text('rootProject.name = "demo"\ninclude(":app")\n', encoding="utf-8")
            (app / "app/build.gradle.kts").write_text(
                'plugins { id("com.android.application") }\n'
                'android { namespace = "com.example.demo"; compileSdk = 36\n'
                'defaultConfig { applicationId = "com.example.demo"; minSdk = 24; targetSdk = 36 } }\n',
                encoding="utf-8",
            )
            manifest = app / "app/src/main/AndroidManifest.xml"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text('<manifest package="com.example.demo"/>\n', encoding="utf-8")
            (src / "Core.kt").write_text(
                "import android.hardware.SensorManager\n"
                "fun hot() { val mode = SensorManager.SENSOR_DELAY_FASTEST; while (true) { Thread.sleep(1) } }\n",
                encoding="utf-8",
            )
            detected = as_json(sys.executable, android, app, "--json")
            self.assertEqual(detected["state"], "EXISTING_ANDROID")
            self.assertTrue(detected["device_verification_required"])
            kinds = {row["kind"] for row in detected["risk_hints"]}
            self.assertTrue({"busy_loop_review", "high_rate_sensor", "tight_timer"} <= kinds)

            record = root / "closure.json"
            record.write_text(
                json.dumps(
                    {
                        "ownership": [{
                            "decision": "mode",
                            "authoritative_owner": "app.js",
                            "writers": ["app.js"],
                            "independent_deciders": ["app.js"],
                        }],
                        "claims": [{
                            "id": "claim",
                            "target": "head",
                            "requires": ["focused-test"],
                            "evidence": ["focused"],
                        }],
                        "evidence": [{
                            "id": "focused",
                            "target": "head",
                            "result": "pass",
                            "covers": ["focused-test"],
                        }],
                        "convergence": {
                            "required": ["source", "verified"],
                            "observed": {"source": "head", "verified": "head"},
                        },
                    }
                ),
                encoding="utf-8",
            )
            closure = as_json(sys.executable, SCRIPTS / "engineering-closure.py", record, "--json")
            self.assertEqual(closure["status"], "READY")

    def test_05_eval_runner_and_comparison_pipeline_with_valid_gate_size(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            suite = root / "suite.json"
            categories = ["bugfix", "bugfix", "feature", "feature", "refactor", "refactor"]
            suite.write_text(
                json.dumps(
                    {
                        "schema": 1,
                        "suite_id": "full-system-audit",
                        "suite_version": "1",
                        "split": "dev",
                        "tasks": [
                            {"id": f"task-{i}", "category": category, "payload": {"value": i}}
                            for i, category in enumerate(categories, 1)
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stable_policy = root / "stable-policy"
            candidate_policy = root / "candidate-policy"
            stable_policy.mkdir()
            candidate_policy.mkdir()
            (stable_policy / "SKILL.md").write_text("stable\n", encoding="utf-8")
            (candidate_policy / "SKILL.md").write_text("candidate\n", encoding="utf-8")

            adapter = root / "adapter.py"
            adapter.write_text(
                textwrap.dedent(
                    """
                    import json, os, time
                    from pathlib import Path
                    task = json.loads(Path(os.environ['SLOAR_EVAL_TASK_FILE']).read_text())
                    candidate = os.environ['SLOAR_EVAL_POLICY_ID'] == 'candidate'
                    time.sleep(0.005 if candidate else 0.03)
                    metrics = {
                        'success': 1,
                        'regression': 0,
                        'false_completion': 0,
                        'correction_distance': 0.10 if candidate else 0.20,
                        'tool_calls': 6 if candidate else 10,
                        'tokens': 600 if candidate else 1000,
                    }
                    Path(os.environ['SLOAR_EVAL_RESULT_FILE']).write_text(
                        json.dumps({'task_id': task['id'], 'metrics': metrics})
                    )
                    Path(os.environ['SLOAR_EVAL_TRAJECTORY_FILE']).write_text(
                        json.dumps({'event': 'done', 'task': task['id']}) + '\\n'
                    )
                    """
                ),
                encoding="utf-8",
            )

            common = dict(
                suite_path=suite,
                model_id="gpt-audit",
                adapter_id="mock",
                adapter_version="1",
                adapter_command=[sys.executable, str(adapter)],
                timeout_s=5,
            )
            stable = run_suite(
                **common,
                policy_id="stable",
                policy_path=stable_policy,
                output_path=root / "stable.json",
                run_id="stable-run",
            )
            candidate = run_suite(
                **common,
                policy_id="candidate",
                policy_path=candidate_policy,
                output_path=root / "candidate.json",
                run_id="candidate-run",
            )
            self.assertEqual(stable["suite_version"], candidate["suite_version"])
            self.assertNotEqual(stable["execution"]["policy_sha256"], candidate["execution"]["policy_sha256"])
            self.assertTrue(all(row["artifacts"]["trajectory_present"] for row in stable["tasks"] + candidate["tasks"]))

            result = compare_runs(stable, candidate)
            self.assertEqual(result["decision"], "EXPERIMENT_ONLY")
            self.assertTrue(result["hard_gates_passed"], result["gates"])
            self.assertGreaterEqual(result["secondary_improvements"], 2)

    def test_06_upgrade_preserves_product_custom_companion_and_backup(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td))
            old = repo / ".agents/skills/sloar-chat-coder"
            old.mkdir(parents=True)
            (old / "SKILL.md").write_text(
                '---\nname: sloar-chat-coder\nmetadata:\n  version: "0.4.0"\n---\nold\n',
                encoding="utf-8",
            )
            (old / "legacy.txt").write_text("legacy\n", encoding="utf-8")
            custom = repo / ".agents/skills/apple-web-design/SKILL.md"
            custom.parent.mkdir(parents=True)
            custom.write_text("custom companion\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "legacy Sloar")

            product_before = (repo / "product.txt").read_bytes()
            custom_before = custom.read_bytes()
            run(sys.executable, SCRIPTS / "install.py", "--target", repo, "--upgrade")
            installed = (repo / ".agents/skills/sloar-chat-coder/SKILL.md").read_text(encoding="utf-8")
            self.assertIn(f'version: "{VERSION}"', installed)
            self.assertEqual((repo / "product.txt").read_bytes(), product_before)
            self.assertEqual(custom.read_bytes(), custom_before)
            backups = list((repo / ".git/sloar-upgrade-backups").glob("*/legacy.txt"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "legacy\n")


if __name__ == "__main__":
    unittest.main()
