import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evals.adapters import codex_cli


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / ".agents/skills/sloar-chat-coder/scripts/install.py"


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
        raise AssertionError(proc.stderr or proc.stdout)
    return proc


class RuntimeCacheIsolationTests(unittest.TestCase):
    def test_eval_fixture_materialization_excludes_python_runtime_cache(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fixture = root / "fixture"
            fixture.mkdir()
            (fixture / "utils.py").write_text("value = 1\n", encoding="utf-8")
            cache = fixture / "__pycache__"
            cache.mkdir()
            (cache / "utils.cpython-313.pyc").write_bytes(b"stale-bytecode")
            task = {
                "id": "cache-test",
                "repository": {"fixture_path": str(fixture)},
            }
            output = root / "output"
            output.mkdir()
            worktree = codex_cli._materialize_repository(task, output_dir=output, adapter_cwd=root)
            self.assertTrue((worktree / "utils.py").is_file())
            self.assertFalse((worktree / "__pycache__").exists())
            self.assertFalse(any(worktree.rglob("*.pyc")))

    def test_installed_helpers_do_not_dirty_target_with_python_cache(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run("git", "-C", repo, "init", "-b", "main")
            run("git", "-C", repo, "config", "user.email", "audit@example.com")
            run("git", "-C", repo, "config", "user.name", "Audit")
            run("git", "-C", repo, "remote", "add", "origin", "https://github.com/example/demo.git")
            (repo / "README.md").write_text("demo\n", encoding="utf-8")
            run("git", "-C", repo, "add", ".")
            run("git", "-C", repo, "commit", "-m", "baseline")

            run(sys.executable, INSTALLER, "--target", repo)
            run("git", "-C", repo, "add", ".")
            run("git", "-C", repo, "commit", "-m", "install Sloar")
            before = run("git", "-C", repo, "status", "--porcelain=v1").stdout
            self.assertEqual(before, "")

            skill_scripts = repo / ".agents/skills/sloar-chat-coder/scripts"
            run(sys.executable, skill_scripts / "doctor.py", repo, "--json")
            run(sys.executable, skill_scripts / "wizard.py", repo, "--json")

            cache_dirs = list((repo / ".agents/skills/sloar-chat-coder").rglob("__pycache__"))
            self.assertTrue(cache_dirs, "test must actually exercise Python bytecode cache creation")
            after = run("git", "-C", repo, "status", "--porcelain=v1").stdout
            self.assertEqual(after, "", after)
            self.assertTrue((repo / ".agents/skills/sloar-chat-coder/.gitignore").is_file())


if __name__ == "__main__":
    unittest.main()
