import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "SKILL.md"
AGENT = ROOT / "agents" / "openai.yaml"
ANALYSIS = ROOT / "references" / "texture-analysis.md"
UV_EYES = ROOT / "references" / "uv-and-eye-system.md"
QUALITY = ROOT / "references" / "texture-quality.md"
VALIDATOR = ROOT / "scripts" / "validate_texture_handoff.py"


class TextureSkillPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.agent = AGENT.read_text(encoding="utf-8")
        cls.analysis = ANALYSIS.read_text(encoding="utf-8") if ANALYSIS.exists() else ""
        cls.uv_eyes = UV_EYES.read_text(encoding="utf-8") if UV_EYES.exists() else ""
        cls.quality = QUALITY.read_text(encoding="utf-8") if QUALITY.exists() else ""
        cls.all_text = cls.skill + cls.analysis + cls.uv_eyes + cls.quality

    def test_official_identity_and_call_name(self):
        self.assertIn("name: fjzm-texture", self.skill)
        self.assertIn("# 方界造模·纹理工坊", self.skill)
        self.assertIn("$fjzm-texture", self.agent)

    def test_supports_delegation_retexture_and_approved_uv_mode(self):
        for phrase in ("delegated production", "standalone retexture", "delegated_uv_and_texture"):
            self.assertIn(phrase, self.skill)

    def test_reads_contracts_before_editing(self):
        self.assertIn("Read [texture-analysis.md](references/texture-analysis.md) before editing", self.skill)
        self.assertIn("Read [uv-and-eye-system.md](references/uv-and-eye-system.md)", self.skill)
        self.assertIn("Read [texture-quality.md](references/texture-quality.md)", self.skill)

    def test_preserves_the_four_step_workflow(self):
        for phrase in (
            "Step 1: reference decomposition",
            "Step 2: UV and spatial planning",
            "Step 3: high-fidelity pixel texturing",
            "Step 4: eyes and animation adaptation",
        ):
            self.assertIn(phrase, self.all_text)

    def test_scene_light_is_analyzed_but_not_baked_into_albedo(self):
        for phrase in (
            "reference scene lighting",
            "intrinsic material cues",
            "neutral albedo",
            "Never bake directional scene light",
            "double lighting",
        ):
            self.assertIn(phrase, self.all_text)

    def test_high_quality_pixel_material_rules_are_explicit(self):
        for phrase in (
            "3-5 color ramp",
            "hue shift",
            "nearest-neighbor",
            "no antialiasing blur",
            "metal",
            "cloth",
            "skin",
        ):
            self.assertIn(phrase, self.all_text)

    def test_ao_and_edge_accents_are_controlled(self):
        for phrase in (
            "local contact AO",
            "opaque pixel colors",
            "conditional 1-2 pixel edge accents",
            "pillow shading",
            "not every edge",
        ):
            self.assertIn(phrase, self.all_text)

    def test_uv_seams_and_eye_states_are_contractual(self):
        for phrase in (
            "uniform texel density",
            "padding and bleed",
            "seam-pair validation",
            "normal",
            "closed",
            "angry",
            "runtime support",
            "frame coordinates",
        ):
            self.assertIn(phrase, self.uv_eyes)

    def test_source_identity_and_writer_are_locked(self):
        for phrase in (
            "texture-handoff.json",
            "project_id",
            "asset_id",
            "asset_version",
            "model_sha256",
            "geometry_signature",
            "uv_signature",
            "single writer",
            "Never overwrite the source `.bbmodel`",
            "versioned output copy",
        ):
            self.assertIn(phrase, self.skill + self.analysis)

    def test_two_user_approvals_are_required(self):
        self.assertIn("explicit analysis-plan approval", self.skill)
        self.assertIn("explicit texture-preview approval", self.skill)
        self.assertIn("Silence is not approval", self.skill)

    def test_direct_conversation_asks_one_plain_numbered_question(self):
        for phrase in (
            "Ask exactly one user-facing question per turn",
            "Use plain Chinese and an internet-friendly conversational tone",
            "Offer 2 or 3 numbered choices",
            "Keep the remaining question queue internal",
            "回复序号就行，也可以直接说你的想法。",
        ):
            self.assertIn(phrase, self.skill)

    def test_actual_blockbench_evidence_is_required(self):
        for phrase in ("actual Blockbench", "front", "side", "back", "three-quarter", "gameplay distance"):
            self.assertIn(phrase, self.skill + self.quality)

    def test_machine_validator_and_outputs_are_required(self):
        self.assertTrue(VALIDATOR.exists())
        self.assertIn("validate_texture_handoff.py", self.skill)
        for phrase in (
            "texture-spec.json",
            "texture-atlas.png",
            "reference-fidelity-report.json",
            "texture-result.json",
        ):
            self.assertIn(phrase, self.skill)

    def test_contractflow_and_main_only_routing_are_explicit(self):
        for phrase in (
            "ContractFlow v1",
            "accepts production only from `$fjzm`",
            "never sends work directly to `$fjzm-model` or `$fjzm-animation`",
            "geometry, base bone hierarchy, origins, and locators remain immutable",
        ):
            self.assertIn(phrase, self.skill)


if __name__ == "__main__":
    unittest.main()
