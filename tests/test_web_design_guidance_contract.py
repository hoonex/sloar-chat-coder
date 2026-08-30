import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/web-design-guidance/SKILL.md"
DISCOVERY = ROOT / ".agents/skills/web-design-guidance/references/design-discovery.md"
RECIPES = ROOT / ".agents/skills/web-design-guidance/references/surface-recipes.md"
VISUAL = ROOT / ".agents/skills/web-design-guidance/references/visual-verification.md"
NOTICE = ROOT / ".agents/skills/web-design-guidance/NOTICE.md"
INSTALLER = ROOT / ".agents/skills/sloar-chat-coder/scripts/install.py"


class WebDesignGuidanceContractTests(unittest.TestCase):
    def text(self, path: Path) -> str:
        self.assertTrue(path.is_file(), path)
        return path.read_text(encoding="utf-8")

    def test_skill_precedence_keeps_user_and_repository_authoritative(self):
        text = self.text(SKILL)
        self.assertIn("explicit user direction", text)
        self.assertIn("repository design rules", text)
        self.assertIn("shipped UI patterns", text)
        self.assertLess(text.index("explicit user direction"), text.index("repository design rules"))
        self.assertLess(text.index("repository design rules"), text.index("shipped UI patterns"))
        self.assertIn("Never replace a coherent existing design system", text)

    def test_discovery_does_not_force_new_design_document(self):
        skill = self.text(SKILL)
        discovery = self.text(DISCOVERY)
        self.assertIn("Do not create a new persistent design-system document by default", skill)
        self.assertIn("Do not add another competing design-memory file", discovery)
        self.assertIn("Design Read", discovery)

    def test_anti_generic_rules_are_contextual_not_style_bans(self):
        text = self.text(SKILL)
        self.assertIn("Anti-generic-AI rules", text)
        self.assertIn("purple/pink glow gradients", text)
        self.assertIn("defaulting every landing page", text)
        self.assertIn("The solution is not to ban a style", text)

    def test_surface_recipes_cover_common_web_surfaces(self):
        text = self.text(RECIPES)
        for heading in (
            "Product application",
            "Dashboard / analytics",
            "Landing / marketing",
            "Auth / onboarding",
            "Settings / configuration",
            "Content / docs / editorial",
            "Commerce",
        ):
            self.assertIn(f"## {heading}", text)

    def test_visual_claims_require_rendered_evidence_when_available(self):
        skill = self.text(SKILL)
        visual = self.text(VISUAL)
        self.assertIn("Visual verification is mandatory for visual claims when available", skill)
        self.assertIn("build/compile green != visually correct", visual)
        self.assertIn("Do not keep the chat turn alive indefinitely", visual)

    def test_installer_bundles_and_activates_general_design_companion(self):
        text = self.text(INSTALLER)
        self.assertRegex(text, r'BUNDLED_SKILLS\s*=.*"web-design-guidance"')
        self.assertIn("substantial user-facing web UI/design work", text)
        self.assertIn("web-design-guidance/SKILL.md", text)
        self.assertIn("preserved existing companion customization", text)

    def test_notice_records_external_inspirations_without_runtime_dependency(self):
        text = self.text(NOTICE)
        for repo in (
            "nextlevelbuilder/ui-ux-pro-max-skill",
            "superdesigndev/superdesign-skill",
            "educlopez/ui-craft",
        ):
            self.assertIn(repo, text)
        self.assertIn("does not vendor or require", text)


if __name__ == "__main__":
    unittest.main()
