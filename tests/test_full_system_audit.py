import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from argparse import Namespace
from pathlib import Path

from evals.compare import compare_runs
from evals.run import run_suite


ROOT = Path(__file__).resolve().parents[1]
SLOAR = ROOT / ".agents/skills/sloar-chat-coder"
SCRIPTS = SLOAR / "scripts"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def run(*args, cwd=None, check=True):
    proc = subprocess.run(
        [str(arg) for arg in args],
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise AssertionError(
            f"command failed ({proc.returncode}): {' '.join(map(str, args))}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def git(repo: Path, *args: str, check=True):
    return run("git", "-C", repo, *args, check=check)


def init_repo(root: Path, *, name="target") -> Path:
    repo = root / name
    repo.mkdir(parents=True)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "audit@example.com")
    git(repo, "config", "user.name", "Sloar Audit")
    git(repo, "remote", "add", "origin", f"https://github.com/example/{name}.git")
    (repo / "AGENTS.md").write_text("# Existing repository guidance\n", encoding="utf-8")
    (repo / "product.txt").write_text("product-state-v1\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "baseline")
    return repo


def json_command(*args, cwd=None, expected_code=0):
    proc = run(*args, cwd=cwd, check=False)
    if proc.returncode != expected_code:
        raise AssertionError(
            f"expected exit {expected_code}, got {proc.returncode}: {' '.join(map(str, args))}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"invalid JSON from {' '.join(map(str, args))}: {proc.stdout}") from exc


def load_hyphen_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FullSystemAuditTests(unittest.TestCase):
    """Cross-feature audit on top of the focused unit/contract suite.

    These scenarios intentionally connect public entry points end-to-end. They do
    not call a paid/credentialed external model service; provider-backed agent
    execution remains a separate environment-dependent acceptance surface.
    """

    def test_01_all_local_cli_entrypoints_start_and_self_tests_pass(self):
        python_scripts = sorted(SCRIPTS.glob("*.py"))
        self.assertGreaterEqual(len(python_scripts), 9)
        for script in python_scripts:
            with self.subTest(script=script.name):
                proc = run(sys.executable, script, "--help", check=False)
                self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
                self.assertIn("usage:", proc.stdout.lower())

        for shell_script in sorted(SCRIPTS.glob("*.sh")):
            with self.subTest(shell=shell_script.name):
                self.assertEqual(run("bash", "-n", shell_script, check=False).returncode, 0)

        self.assertIn("sloar self-test: ok", run("bash", SCRIPTS / "preflight.sh", "--self-test").stdout)
        self.assertIn(
            "ref cleanup: ok",
            run(sys.executable, SCRIPTS / "ref-cleanup.py", "--self-test").stdout,
        )

        # Eval CLIs are part of 0.9.1 even though real Codex execution needs auth.
        for path in (ROOT / "evals/run.py", ROOT / "evals/run_pair.py", ROOT / "evals/compare.py", ROOT / "evals/adapters/codex_cli.py"):
            proc = run(sys.executable, path, "--help", check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
            self.assertIn("usage:", proc.stdout.lower())

    def test_02_fresh_install_doctor_wizard_preflight_checkpoint_chain(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td))
            product_before = (repo / "product.txt").read_bytes()

            install = run(sys.executable, SCRIPTS / "install.py", "--target", repo)
            self.assertEqual((repo / "product.txt").read_bytes(), product_before)
            self.assertTrue((repo / ".agents/skills/sloar-chat-coder/SKILL.md").is_file())
            self.assertTrue((repo / ".agents/skills/web-design-guidance/SKILL.md").is_file())
            self.assertTrue((repo / ".agents/skills/apple-web-design/SKILL.md").is_file())
            self.assertEqual((repo / "AGENTS.md").read_text().count("sloar-chat-coder:begin"), 1)

            # Idempotent reinstall must not duplicate the managed AGENTS block.
            run(sys.executable, SCRIPTS / "install.py", "--target", repo)
            self.assertEqual((repo / "AGENTS.md").read_text().count("sloar-chat-coder:begin"), 1)

            git(repo, "add", ".")
            git(repo, "commit", "-m", "install Sloar")
            head = git(repo, "rev-parse", "HEAD").stdout.strip()
            tree = git(repo, "rev-parse", "HEAD^{tree}").stdout.strip()

            doctor = json_command(sys.executable, repo / ".agents/skills/sloar-chat-coder/scripts/doctor.py", repo, "--json")
            self.assertEqual(doctor["schema"], 2)
            self.assertTrue(doctor["sloar_installed"])
            self.assertTrue(doctor["git"]["is_worktree"])

            wizard = json_command(
                sys.executable,
                repo / ".agents/skills/sloar-chat-coder/scripts/wizard.py",
                repo,
                "--stable-version",
                VERSION,
                "--json",
            )
            self.assertEqual(wizard["sloar_version"], VERSION)
            self.assertEqual(wizard["updates"]["status"], "current")
            self.assertEqual(wizard["resilience"]["local_status"], "LOCAL_READY")
            self.assertEqual(wizard["design"]["web_design_companion"], "ready")
            self.assertEqual(wizard["engineering_closure"]["helper"], "ready")

            preflight = run("bash", repo / ".agents/skills/sloar-chat-coder/scripts/preflight.sh", repo).stdout
            self.assertIn(f"head={head}", preflight)
            self.assertIn(f"tree={tree}", preflight)
            self.assertIn("dirty=false", preflight)

            verify = run("bash", repo / ".agents/skills/sloar-chat-coder/scripts/verify-state.sh", head, tree, repo)
            self.assertEqual(verify.returncode, 0)

            checkpoint = Path(td) / "checkpoint.json"
            run(
                sys.executable,
                repo / ".agents/skills/sloar-chat-coder/scripts/write-checkpoint.py",
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
            cp = json.loads(checkpoint.read_text())
            self.assertEqual(cp["head"], head)
            self.assertEqual(cp["stage"], "VERIFY")
            self.assertFalse(cp["dirty"])
            self.assertEqual((repo / "product.txt").read_bytes(), product_before)
            self.assertTrue(install.stdout.strip())

    def test_03_upgrade_preserves_product_custom_companion_and_backup(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = init_repo(root)
            agents = repo / "AGENTS.md"
            agents.write_text(
                "# Existing guidance\n\n<!-- sloar-chat-coder:begin -->\n"
                "## Sloar Chat Coder\nold managed block\n<!-- sloar-chat-coder:end -->\n",
                encoding="utf-8",
            )
            old = repo / ".agents/skills/sloar-chat-coder"
            old.mkdir(parents=True)
            (old / "SKILL.md").write_text(
                '---\nname: sloar-chat-coder\nmetadata:\n  version: "0.4.0"\n---\nold\n',
                encoding="utf-8",
            )
            (old / "legacy-note.txt").write_text("legacy bytes must be recoverable\n", encoding="utf-8")
            custom = repo / ".agents/skills/apple-web-design/SKILL.md"
            custom.parent.mkdir(parents=True)
            custom.write_text("custom apple companion\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "legacy Sloar")

            product_before = (repo / "product.txt").read_bytes()
            custom_before = custom.read_bytes()
            proc = run(sys.executable, SCRIPTS / "install.py", "--target", repo, "--upgrade")
            installed = (repo / ".agents/skills/sloar-chat-coder/SKILL.md").read_text(encoding="utf-8")
            self.assertIn(f'version: "{VERSION}"', installed)
            self.assertEqual((repo / "product.txt").read_bytes(), product_before)
            self.assertEqual(custom.read_bytes(), custom_before)
            self.assertEqual(agents.read_text().count("sloar-chat-coder:begin"), 1)
            backups = list((repo / ".git/sloar-upgrade-backups").glob("*/legacy-note.txt"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "legacy bytes must be recoverable\n")
            self.assertIn("preserved existing companion customization", proc.stdout)

    def test_04_rollover_handoff_resume_and_repository_movement(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td))
            script = SCRIPTS / "session-rollover.py"
            before_status = git(repo, "status", "--porcelain=v1").stdout

            handoff = json_command(
                sys.executable,
                script,
                "handoff",
                repo,
                "--goal",
                "finish system audit",
                "--completed",
                "local checks",
                "--pending",
                "remote verify",
                "--next",
                "resume safely",
                "--response-language",
                "ko-KR",
                "--json",
            )
            self.assertEqual(handoff["checkpoint"]["context"]["response_language"], "ko-KR")
            self.assertEqual(git(repo, "status", "--porcelain=v1").stdout, before_status)

            exact = json_command(sys.executable, script, "resume", repo, "--json")
            self.assertEqual(exact["comparison"]["state"], "EXACT")

            (repo / "product.txt").write_text("product-state-v2\n", encoding="utf-8")
            git(repo, "add", "product.txt")
            git(repo, "commit", "-m", "move repository")
            moved = json_command(sys.executable, script, "resume", repo, "--json")
            self.assertEqual(moved["comparison"]["state"], "RECONCILE_REQUIRED")
            self.assertIn("head", moved["comparison"]["changed"])
            self.assertIn("tree", moved["comparison"]["changed"])

    def test_05_turn_state_progress_takeover_fencing_and_terminal_recovery(self):
        turn_state = load_hyphen_module("sloar_audit_turn_state", SCRIPTS / "turn-state.py")

        def args(**overrides):
            values = dict(
                goal="audit long turn",
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
            values.update(overrides)
            return Namespace(**values)

        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td))
            old = turn_state.begin_turn(repo, args(anchor=["origin=abc"]))
            progressed = turn_state.progress_turn(
                repo,
                args(
                    turn_id=old["turn_id"],
                    epoch=old["epoch"],
                    completed=["verification"],
                    evidence=["unit:pass"],
                    changed=["audit evidence only"],
                ),
            )
            self.assertEqual(progressed["event_seq"], 2)
            self.assertTrue(turn_state.check_fence(repo, old["turn_id"], old["epoch"])["ok"])

            new = turn_state.takeover_turn(
                repo,
                args(reason="explicit fresh-chat takeover", next_action="revalidate and continue"),
            )
            self.assertEqual(new["epoch"], old["epoch"] + 1)
            self.assertFalse(turn_state.check_fence(repo, old["turn_id"], old["epoch"])["ok"])
            self.assertTrue(turn_state.check_fence(repo, new["turn_id"], new["epoch"])["ok"])

            terminal = turn_state.complete_turn(
                repo,
                args(
                    turn_id=new["turn_id"],
                    epoch=new["epoch"],
                    status="PARTIAL",
                    evidence=["audit:pass"],
                    terminal_note="external provider execution not part of this deterministic audit",
                ),
            )
            self.assertTrue(terminal["terminal"])
            view = turn_state.recovery_view(repo)
            self.assertEqual(view["recovery_state"], "TERMINAL_REPLAY_AVAILABLE")
            self.assertEqual(view["turn"]["status"], "PARTIAL")
            self.assertEqual(view["comparison"]["state"], "EXACT")

    def test_06_forge_health_and_ref_cleanup_classification_matrix(self):
        forge = SCRIPTS / "forge-health.py"
        cleanup = SCRIPTS / "ref-cleanup.py"

        rate = json_command(sys.executable, forge, "--classify-error", "HTTP 429 secondary rate limit exceeded", "--json")
        moved = json_command(sys.executable, forge, "--classify-error", "rejected non-fast-forward; fetch first", "--json")
        permission = json_command(
            sys.executable,
            forge,
            "--classify-error",
            "refusing to allow a GitHub App to create or update workflow without workflows permission",
            "--json",
        )
        self.assertEqual(rate["classification"], "REMOTE_DEGRADED")
        self.assertEqual(rate["retry"], "defer")
        self.assertEqual(moved["classification"], "REMOTE_MOVED")
        self.assertEqual(moved["retry"], "reconcile")
        self.assertEqual(permission["classification"], "CAPABILITY_MISMATCH")
        self.assertEqual(permission["remote_state"], "REMOTE_PARTIAL")

        unavailable = json_command(
            sys.executable,
            cleanup,
            "--branch",
            "audit/tmp",
            "--lifecycle",
            "merged",
            "--delete-capability",
            "unavailable",
            "--json",
        )
        ready = json_command(
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
        protected = json_command(
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
        self.assertEqual(unavailable["classification"], "REF_DELETE_UNAVAILABLE")
        self.assertEqual(unavailable["cleanup"], "CLEANUP_DEFERRED")
        self.assertEqual(ready["classification"], "REF_DELETE_READY")
        self.assertEqual(ready["cleanup"], "READY")
        self.assertEqual(protected["classification"], "REF_DELETE_PROHIBITED")
        self.assertEqual(protected["cleanup"], "PRESERVE")

    def test_07_android_preflight_and_engineering_closure_status_matrix(self):
        android = SCRIPTS / "android-preflight.py"
        closure = SCRIPTS / "engineering-closure.py"

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            empty = json_command(sys.executable, android, root, "--json")
            self.assertEqual(empty["state"], "EMPTY_OR_NON_ANDROID")

            project = root / "android"
            src = project / "app/src/main/java/com/example"
            src.mkdir(parents=True)
            (project / "gradlew").write_text("#!/bin/sh\n", encoding="utf-8")
            (project / "settings.gradle.kts").write_text('rootProject.name = "demo"\ninclude(":app")\n', encoding="utf-8")
            (project / "app/build.gradle.kts").write_text(
                'plugins { id("com.android.application") }\n'
                'android { namespace = "com.example.demo"; compileSdk = 36\n'
                'defaultConfig { applicationId = "com.example.demo"; minSdk = 24; targetSdk = 36 } }\n',
                encoding="utf-8",
            )
            manifest = project / "app/src/main/AndroidManifest.xml"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text('<manifest package="com.example.demo"/>\n', encoding="utf-8")
            (src / "Core.kt").write_text(
                "import android.hardware.SensorManager\n"
                "fun hot() { val mode = SensorManager.SENSOR_DELAY_FASTEST; while (true) { Thread.sleep(1) } }\n",
                encoding="utf-8",
            )
            detected = json_command(sys.executable, android, project, "--json")
            self.assertEqual(detected["state"], "EXISTING_ANDROID")
            self.assertTrue(detected["device_verification_required"])
            kinds = {item["kind"] for item in detected["risk_hints"]}
            self.assertTrue({"busy_loop_review", "high_rate_sensor", "tight_timer"} <= kinds)

            ready_record = root / "ready.json"
            ready_record.write_text(
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
            ready = json_command(sys.executable, closure, ready_record, "--json")
            self.assertEqual(ready["status"], "READY")

            blocked_record = root / "blocked.json"
            blocked_record.write_text(
                json.dumps(
                    {
                        "ownership": [{
                            "decision": "mode",
                            "authoritative_owner": "a.js",
                            "writers": ["a.js", "b.js"],
                            "independent_deciders": ["a.js", "b.js"],
                        }],
                        "claims": [{
                            "id": "claim",
                            "target": "new",
                            "requires": ["touch"],
                            "evidence": ["old"],
                        }],
                        "evidence": [{
                            "id": "old",
                            "target": "old",
                            "result": "pass",
                            "covers": ["touch"],
                        }],
                        "convergence": {
                            "required": ["source", "verified", "served"],
                            "observed": {"source": "new", "verified": "new"},
                        },
                    }
                ),
                encoding="utf-8",
            )
            blocked = json_command(sys.executable, closure, blocked_record, "--json", expected_code=2)
            codes = {item["code"] for item in blocked["findings"]}
            self.assertEqual(blocked["status"], "BLOCKED")
            self.assertTrue({"OWNERSHIP_SPLIT", "EVIDENCE_GAP", "CONVERGENCE_GAP"} <= codes)

    def test_08_eval_runner_artifacts_and_comparison_work_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            suite = root / "suite.json"
            suite.write_text(
                json.dumps(
                    {
                        "schema": 1,
                        "suite_id": "full-system-audit",
                        "suite_version": "1",
                        "split": "dev",
                        "tasks": [
                            {"id": "bug", "category": "bugfix", "payload": {"value": 1}},
                            {"id": "feature", "category": "feature", "payload": {"value": 2}},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stable_policy = root / "stable-policy"
            candidate_policy = root / "candidate-policy"
            stable_policy.mkdir()
            candidate_policy.mkdir()
            (stable_policy / "SKILL.md").write_text("stable policy\n", encoding="utf-8")
            (candidate_policy / "SKILL.md").write_text("candidate policy\n", encoding="utf-8")

            adapter = root / "adapter.py"
            adapter.write_text(
                textwrap.dedent(
                    """
                    import json, os
                    from pathlib import Path
                    task = json.loads(Path(os.environ['SLOAR_EVAL_TASK_FILE']).read_text())
                    candidate = os.environ['SLOAR_EVAL_POLICY_ID'] == 'candidate'
                    metrics = {
                        'success': 1,
                        'regression': 0,
                        'false_completion': 0,
                        'tool_calls': (5 if candidate else 7) + task['payload']['value'],
                        'tokens': (500 if candidate else 700) + task['payload']['value'],
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

            stable = run_suite(
                suite_path=suite,
                policy_id="stable",
                policy_path=stable_policy,
                model_id="gpt-audit",
                adapter_id="mock",
                adapter_version="1",
                adapter_command=[sys.executable, str(adapter)],
                output_path=root / "stable.json",
                run_id="stable-run",
                timeout_s=5,
            )
            candidate = run_suite(
                suite_path=suite,
                policy_id="candidate",
                policy_path=candidate_policy,
                model_id="gpt-audit",
                adapter_id="mock",
                adapter_version="1",
                adapter_command=[sys.executable, str(adapter)],
                output_path=root / "candidate.json",
                run_id="candidate-run",
                timeout_s=5,
            )
            self.assertEqual(stable["suite_version"], candidate["suite_version"])
            self.assertNotEqual(stable["execution"]["policy_sha256"], candidate["execution"]["policy_sha256"])
            self.assertTrue(all(task["artifacts"]["trajectory_present"] for task in stable["tasks"] + candidate["tasks"]))
            result = compare_runs(stable, candidate)
            self.assertEqual(result["decision"], "EXPERIMENT_ONLY")
            self.assertTrue(result["hard_gates_passed"])
            self.assertLess(result["candidate"]["means"]["tool_calls"], result["baseline"]["means"]["tool_calls"])

            # Real provider execution is deliberately not faked as proven here.
            # The adapter itself is exercised by focused tests; an authenticated
            # Codex CLI run belongs to provider/environment acceptance evidence.
            self.assertTrue((ROOT / "evals/adapters/codex_cli.py").is_file())
            self.assertIsInstance(shutil.which("codex"), (str, type(None)))


if __name__ == "__main__":
    unittest.main()
