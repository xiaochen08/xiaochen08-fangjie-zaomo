import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "SKILL.md"
HANDOFF = ROOT / "references" / "model-handoff.md"
BLUEPRINT = ROOT / "references" / "geometry-blueprint.md"
FIDELITY = ROOT / "references" / "fidelity-comparison.md"
REPAIR = ROOT / "references" / "auto-repair.md"


class ModelWorkshopPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.handoff = HANDOFF.read_text(encoding="utf-8")
        cls.blueprint = BLUEPRINT.read_text(encoding="utf-8")
        cls.fidelity = FIDELITY.read_text(encoding="utf-8")
        cls.repair = REPAIR.read_text(encoding="utf-8")
        cls.all_text = cls.skill + cls.handoff + cls.blueprint + cls.fidelity + cls.repair

    def test_main_only_delegation_and_result_return(self):
        for phrase in (
            "accepts work only from `$fjzm`",
            "never sends work directly to `$fjzm-texture` or `$fjzm-animation`",
            "return `model-result.json` to `$fjzm`",
        ):
            self.assertIn(phrase, self.all_text)

    def test_geometry_ownership_and_boundaries_are_explicit(self):
        for phrase in (
            "geometry",
            "base bone hierarchy",
            "origins",
            "locators",
            "placeholder UV",
            "final texture",
            "animation keyframes",
        ):
            self.assertIn(phrase, self.skill)

    def test_visual_comparison_is_bound_to_hashes_and_eight_views(self):
        for phrase in (
            "front, back, left, right, top, bottom, three-quarter, and gameplay-distance",
            "50% transparent overlay",
            "model SHA-256",
            "reference SHA-256",
            "one summary board plus eight separate high-resolution views",
        ):
            self.assertIn(phrase, self.fidelity)

    def test_balanced_fidelity_gate_is_quantified(self):
        for phrase in (
            "blocking anchors: 100%",
            "main proportion error: at most 5%",
            "key-part position error: at most 0.5 Blockbench units",
            "symmetric-part error: at most 0.25 Blockbench units",
            "rotation error: at most 3 degrees",
            "zero unintended intersections",
        ):
            self.assertIn(phrase, self.fidelity)

    def test_repair_is_bounded_and_hard_blocks_stop(self):
        for phrase in (
            "initial attempt plus at most two internal retries",
            "Never lower the approved quality target",
            "identity mismatch",
            "approval ambiguity",
            "preserve every attempt",
        ):
            self.assertIn(phrase, self.repair)


if __name__ == "__main__":
    unittest.main()
