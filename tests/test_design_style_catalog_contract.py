"""Contract tests for the researched, implementable visual-style catalog."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / ".agents/skills/web-design-guidance"
CATALOG = COMPANION / "references/style-implementation-catalog.md"
SKILL = COMPANION / "SKILL.md"
TAXONOMY = COMPANION / "references/design-taxonomy.md"

EXPECTED_STYLES = (
    "Claymorphism", "Cybercore", "Neo-brutalism", "Scrapbook",
    "Surrealism", "Y2K aesthetic", "Pixel art", "Synthwave",
    "Glassmorphism", "Neumorphism", "Bento grid", "Editorial design",
    "Swiss design", "Minimalism", "Maximalism", "Luxury typography",
    "Conceptual sketch", "Ethereal", "Bohemian", "Victorian",
    "Cyberpunk", "Wabi-sabi",
)


class DesignStyleCatalogContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = CATALOG.read_text(encoding="utf-8")
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.taxonomy = TAXONOMY.read_text(encoding="utf-8")

    def test_exactly_22_distinct_requested_styles_in_original_order(self):
        sections = re.findall(r"^### (\d{2})\. ([^\n]+)$", self.catalog, re.M)
        self.assertEqual(sections, [
            (f"{i:02}", name) for i, name in enumerate(EXPECTED_STYLES, 1)
        ])

    def test_every_style_has_distinct_reference_and_executable_guidance(self):
        blocks = re.split(r"^### \d{2}\. [^\n]+\n", self.catalog, flags=re.M)[1:]
        self.assertEqual(len(blocks), len(EXPECTED_STYLES))
        urls = []
        for name, block in zip(EXPECTED_STYLES, blocks):
            with self.subTest(style=name):
                for marker in ("**Axis:**", "**Reference:**", "**Visual grammar:**",
                               "**Implement:**", "**Acceptance:**"):
                    self.assertIn(marker, block)
                reference = re.search(
                    r"\*\*Reference:\*\* \[[^\]]+\]\((https://[^)]+)\)", block
                )
                self.assertIsNotNone(reference)
                urls.append(reference.group(1))
                self.assertGreater(len(block.split("**Implement:**")[1].split("**Acceptance:**")[0].strip()), 65)
                self.assertGreater(len(block.split("**Acceptance:**")[1].strip()), 45)
        self.assertEqual(len(set(urls)), 22, "each style needs its own relevant reference")

    def test_companion_links_and_crosswalk_are_reachable(self):
        self.assertIn("[references/style-implementation-catalog.md](references/style-implementation-catalog.md)", self.skill)
        self.assertIn("[style-implementation-catalog.md](style-implementation-catalog.md)", self.taxonomy)
        for name in EXPECTED_STYLES:
            self.assertIn(name, self.taxonomy)

    def test_surrealism_uses_actual_web_case_studies_and_asset_gate(self):
        section = self.catalog.split("### 05. Surrealism", 1)[1].split("### 06. Y2K aesthetic", 1)[0]
        self.assertIn("lynnandtonic.com/thoughts/entries/case-study-2021-refresh/", section)
        self.assertIn("hellomonday.com/work/moma-magritte", section)
        for phrase in ("Asset feasibility gate", "photographic", "SVG", "320/390/768/1440px", "rendered"):
            self.assertIn(phrase, section)

    def test_visual_style_research_requires_evidenced_implementation(self):
        research = (COMPANION / "references/reference-research-and-critique.md").read_text(encoding="utf-8")
        self.assertIn("Implementation-reference and asset-feasibility gate", research)
        self.assertIn("Inspect, do not merely locate", research)
        self.assertIn("Build and render one vertical slice", research)
        self.assertIn("Code compilation and responsive/functional tests", research)
        self.assertIn("reference-research-and-critique.md", self.skill)
        self.assertIn("before building the full page", self.skill)

    def test_not_just_palette_swaps_or_style_soup(self):
        for token in (
            "vertical slice", "real interactive control", "reduced-motion",
            "asset", "license", "rendered evidence", "320px",
            "@supports", "backdrop-filter", "image-rendering: pixelated",
            "grid-template-columns", "box-shadow", "focus-visible",
        ):
            self.assertIn(token, self.catalog)
        self.assertIn("rather than installing all 22 as a theme", self.skill)


if __name__ == "__main__":
    unittest.main()
