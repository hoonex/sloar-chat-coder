import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/sloar-chat-coder/scripts/web-architecture-map.py"
INSTALLER = ROOT / ".agents/skills/sloar-chat-coder/scripts/install.py"


def load_module():
    spec = importlib.util.spec_from_file_location("web_architecture_map", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str):
    subprocess.run(["git", "-C", str(repo), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class WebArchitectureMapTests(unittest.TestCase):
    def make_repo(self):
        tmp = tempfile.TemporaryDirectory()
        repo = Path(tmp.name)
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "test@example.com")
        git(repo, "config", "user.name", "test")
        (repo / "package.json").write_text(json.dumps({"packageManager": "pnpm@10.0.0", "scripts": {"dev": "next dev", "build": "next build"}, "dependencies": {"next": "16.0.0", "react": "19.0.0", "zustand": "5.0.0", "@tanstack/react-query": "5.0.0", "tailwindcss": "4.0.0"}}) + "\n", encoding="utf-8")
        (repo / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")
        (repo / "app" / "settings").mkdir(parents=True)
        (repo / "app" / "settings" / "page.tsx").write_text("export default function Page(){return null}\n", encoding="utf-8")
        (repo / "app" / "layout.tsx").write_text("export default function Layout({children}){return children}\n", encoding="utf-8")
        (repo / "src" / "styles").mkdir(parents=True)
        (repo / "src" / "styles" / "tokens.css").write_text(":root { --space-1: 4px; }\n", encoding="utf-8")
        (repo / "app" / "globals.css").write_text("body{}\n", encoding="utf-8")
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "init")
        return tmp, repo

    def test_declared_and_observed_topology_are_separate_from_semantics(self):
        module = load_module(); tmp, repo = self.make_repo(); self.addCleanup(tmp.cleanup)
        data = module.build(repo)
        self.assertEqual(data["schema"], 1)
        self.assertEqual(data["kind"], "sloar-web-topology-snapshot")
        self.assertEqual(data["repository"]["source_identity"]["working_tree"], "clean")
        self.assertIsNone(data["repository"]["source_identity"]["working_tree_fingerprint"])
        self.assertEqual(data["package_manager"]["name"], "pnpm@10.0.0")
        framework_names = {item["name"] for item in data["frameworks"]}
        self.assertIn("Next.js", framework_names); self.assertIn("React", framework_names)
        state_names = {item["name"] for item in data["state_data_systems"]}
        self.assertIn("Zustand", state_names); self.assertIn("TanStack Query", state_names)
        self.assertIn("Tailwind CSS", {item["name"] for item in data["styling_systems"]})
        settings = next(item for item in data["routes"] if item["path"] == "app/settings/page.tsx")
        self.assertEqual(settings["route"], "/settings"); self.assertEqual(settings["kind"], "next-app-page")
        self.assertEqual(settings["framework"], "Next.js"); self.assertEqual(settings["package_root"], ".")
        self.assertIn("src/styles/tokens.css", data["styling_candidates"]["token_theme_candidates"])
        self.assertIn("app/globals.css", data["styling_candidates"]["global_style_candidates"])
        self.assertTrue(any("Semantic ownership is intentionally not inferred" in item for item in data["limits"]))

    def test_untracked_files_are_excluded_unless_requested(self):
        module = load_module(); tmp, repo = self.make_repo(); self.addCleanup(tmp.cleanup)
        (repo / "app" / "preview").mkdir(parents=True)
        preview = repo / "app" / "preview" / "page.tsx"
        preview.write_text("export default function Page(){return null}\n", encoding="utf-8")
        durable = module.build(repo); first = durable["repository"]["source_identity"]["working_tree_fingerprint"]
        preview.write_text("export default function Page(){return <div/>}\n", encoding="utf-8")
        changed = module.build(repo); working = module.build(repo, include_untracked=True)
        self.assertFalse(any(item["path"] == "app/preview/page.tsx" for item in durable["routes"]))
        self.assertTrue(any(item["path"] == "app/preview/page.tsx" for item in working["routes"]))
        self.assertEqual(durable["repository"]["source_identity"]["working_tree"], "dirty")
        self.assertTrue(first); self.assertNotEqual(first, changed["repository"]["source_identity"]["working_tree_fingerprint"])

    def test_tracked_dirty_bytes_change_fingerprint(self):
        module = load_module(); tmp, repo = self.make_repo(); self.addCleanup(tmp.cleanup)
        package = repo / "package.json"
        package.write_text(package.read_text(encoding="utf-8").replace("16.0.0", "16.0.1"), encoding="utf-8")
        first = module.build(repo)["repository"]["source_identity"]["working_tree_fingerprint"]
        package.write_text(package.read_text(encoding="utf-8").replace("16.0.1", "16.0.2"), encoding="utf-8")
        second = module.build(repo)["repository"]["source_identity"]["working_tree_fingerprint"]
        self.assertTrue(first); self.assertTrue(second); self.assertNotEqual(first, second)

    def test_nuxt_and_astro_routes_are_framework_scoped(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary); git(repo, "init", "-q"); git(repo, "config", "user.email", "test@example.com"); git(repo, "config", "user.name", "test")
            (repo / "package.json").write_text('{"private":true,"workspaces":["apps/*"]}\n', encoding="utf-8")
            nuxt = repo / "apps" / "nuxt"; (nuxt / "pages").mkdir(parents=True)
            (nuxt / "package.json").write_text('{"dependencies":{"nuxt":"4.0.0","vue":"3.0.0"}}\n', encoding="utf-8")
            (nuxt / "pages" / "about.vue").write_text("<template>About</template>\n", encoding="utf-8")
            astro = repo / "apps" / "docs"; (astro / "src" / "pages").mkdir(parents=True)
            (astro / "package.json").write_text('{"dependencies":{"astro":"6.0.0"}}\n', encoding="utf-8")
            (astro / "src" / "pages" / "index.astro").write_text("<html></html>\n", encoding="utf-8")
            git(repo, "add", "."); git(repo, "commit", "-qm", "monorepo")
            data = module.build(repo); by_path = {item["path"]: item for item in data["routes"]}
            self.assertEqual(by_path["apps/nuxt/pages/about.vue"]["kind"], "nuxt-file-route")
            self.assertEqual(by_path["apps/nuxt/pages/about.vue"]["route"], "/about")
            self.assertEqual(by_path["apps/docs/src/pages/index.astro"]["kind"], "astro-file-route")
            self.assertEqual(by_path["apps/docs/src/pages/index.astro"]["route"], "/")
            self.assertFalse(any(item["kind"].startswith("next-") for item in data["routes"]))

    def test_monorepo_uses_nearest_package_declarations(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary); git(repo, "init", "-q"); git(repo, "config", "user.email", "test@example.com"); git(repo, "config", "user.name", "test")
            (repo / "package.json").write_text('{"private":true,"packageManager":"pnpm@10.0.0"}\n', encoding="utf-8")
            web = repo / "apps" / "web"; (web / "app" / "settings").mkdir(parents=True)
            (web / "package.json").write_text('{"dependencies":{"next":"16.0.0","react":"19.0.0"}}\n', encoding="utf-8")
            (web / "app" / "settings" / "page.tsx").write_text("export default function Page(){return null}\n", encoding="utf-8")
            git(repo, "add", "."); git(repo, "commit", "-qm", "nested next")
            data = module.build(repo); route = next(item for item in data["routes"] if item["path"] == "apps/web/app/settings/page.tsx")
            self.assertEqual(route["route"], "/settings"); self.assertEqual(route["kind"], "next-app-page"); self.assertEqual(route["package_root"], "apps/web")
            next_decl = next(item for item in data["frameworks"] if item["name"] == "Next.js")
            self.assertIn("apps/web/package.json:next", next_decl["evidence"])
            self.assertIn("apps/web/app/", {item["path"] for item in data["source_roots"]})

    def test_route_output_is_bounded(self):
        module = load_module(); tmp, repo = self.make_repo(); self.addCleanup(tmp.cleanup)
        for index in range(4):
            path = repo / "app" / f"r{index}"; path.mkdir(parents=True); (path / "page.tsx").write_text("export default function Page(){return null}\n", encoding="utf-8")
        git(repo, "add", "."); git(repo, "commit", "-qm", "routes")
        data = module.build(repo, max_routes=2)
        self.assertEqual(len(data["routes"]), 2); self.assertTrue(any("Route candidate output truncated at 2" in item for item in data["limits"]))

    def test_installer_bundles_architecture_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            subprocess.run([sys.executable, str(INSTALLER), "--target", str(target)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            core = target / ".agents/skills/sloar-chat-coder"
            self.assertTrue((core / "references/web-architecture-capsule.md").is_file())
            self.assertTrue((core / "scripts/web-architecture-map.py").is_file())
            self.assertIn("references/web-architecture-capsule.md", (core / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
