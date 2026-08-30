import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents/skills/web-design-guidance/SKILL.md"
DISCOVERY = ROOT / ".agents/skills/web-design-guidance/references/design-discovery.md"
ADAPTIVE = ROOT / ".agents/skills/web-design-guidance/references/adaptive-design-discovery.md"
TAXONOMY = ROOT / ".agents/skills/web-design-guidance/references/design-taxonomy.md"
ANTI_SLOP = ROOT / ".agents/skills/web-design-guidance/references/anti-ai-slop.md"
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
        self.assertIn("Design DNA", discovery)

    def test_adaptive_discovery_controls_question_budget(self):
        skill = self.text(SKILL)
        adaptive = self.text(ADAPTIVE)
        for token in ("KNOWN | INFERRED | UNKNOWN", "question value", "decision impact", "rework cost", "reversibility"):
            self.assertIn(token, skill + adaptive)
        self.assertIn("Adaptive question budget", adaptive)
        self.assertIn("0 questions; proceed", adaptive)
        self.assertIn("3-5 high-value questions", adaptive)
        self.assertIn("you decide", adaptive)
        self.assertIn("Ask in user language, not taxonomy language", adaptive)

    def test_taxonomy_is_multi_axis_not_style_selector(self):
        text = self.text(TAXONOMY)
        for axis in (
            "Axis A — design philosophy / visual attitude",
            "Axis B — surface / material language",
            "Axis C — composition",
            "Axis D — interaction language",
            "Axis E — motion posture",
        ):
            self.assertIn(axis, text)
        for term in ("Minimalism", "Maximalism", "Brutalism", "neumorphism", "Glassmorphism", "Direct manipulation", "Context-aware", "Spring"):
            self.assertIn(term, text)
        self.assertIn("Anti-pattern: style soup", text)

    def test_anti_slop_contract_explains_tells_causes_and_fixes(self):
        skill = self.text(SKILL)
        anti = self.text(ANTI_SLOP)
        self.assertIn("Anti-AI-slop means replacing defaults with decisions", skill)
        for token in ("P0", "P1", "P2", "CODE-CERTAIN", "RENDER-CERTAIN", "INFERRED"):
            self.assertIn(token, anti)
        for tell in (
            "unchosen purple/indigo AI palette",
            "gradient headline text",
            "centered SaaS hero bundle",
            "three identical feature cards",
            "untouched component-library demo look",
            "generic AI/SaaS headline copy",
            "Second-order defaults",
        ):
            self.assertIn(tell, anti)
        self.assertIn("AI-authorship detector", anti)
        self.assertIn("not", anti.lower())
        self.assertIn("Do not over-design", anti)

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
        anti = self.text(ANTI_SLOP)
        self.assertIn("Visual verification is mandatory for visual claims when available", skill)
        self.assertIn("build/compile green != visually correct", visual)
        self.assertIn("Do not keep the chat turn alive indefinitely", visual)
        self.assertIn("lack of rendered evidence means visual completion remains partially unverified", anti)

    def test_installer_bundles_and_activates_general_design_companion(self):
        text = self.text(INSTALLER)
        self.assertIn('"web-design-guidance"', text)
        self.assertIn("substantial user-facing web UI/design work", text)
        self.assertIn("web-design-guidance/SKILL.md", text)
        self.assertIn("preserved existing companion customization", text)

    def test_notice_records_external_inspirations_without_runtime_dependency(self):
        text = self.text(NOTICE)
        for repo in (
            "nextlevelbuilder/ui-ux-pro-max-skill",
            "superdesigndev/superdesign-skill",
            "educlopez/ui-craft",
            "rwcod/anti-ai-slop-ui",
            "funboy322/avoid-ai-design",
        ):
            self.assertIn(repo, text)
        self.assertIn("does not vendor or require", text)
        self.assertIn("No external runtime dependency", text)


if __name__ == "__main__":
    unittest.main()
