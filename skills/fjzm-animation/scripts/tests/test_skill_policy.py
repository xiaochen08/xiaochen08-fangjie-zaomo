import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "SKILL.md"
AGENT = ROOT / "agents" / "openai.yaml"
HANDOFF = ROOT / "references" / "animation-handoff.md"
REVISION = ROOT / "references" / "animation-revision.md"
VALIDATOR = ROOT / "scripts" / "validate_animation_handoff.py"


class AnimationSkillPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.agent = AGENT.read_text(encoding="utf-8")
        cls.handoff = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
        cls.revision = REVISION.read_text(encoding="utf-8") if REVISION.exists() else ""

    def test_official_identity_and_call_name(self):
        self.assertIn("name: fjzm-animation", self.skill)
        self.assertIn("# 方界造模·动画工坊", self.skill)
        self.assertIn("$fjzm-animation", self.agent)

    def test_supports_main_delegation_and_direct_revision(self):
        self.assertIn("delegated production", self.skill)
        self.assertIn("standalone revision", self.skill)

    def test_reads_contracts_before_any_edit(self):
        self.assertIn("Read [animation-handoff.md](references/animation-handoff.md) before editing", self.skill)
        self.assertIn("Read [animation-revision.md](references/animation-revision.md)", self.skill)

    def test_identity_model_hash_and_rig_are_locked(self):
        for phrase in ("project_id", "asset_id", "asset_version", "model_sha256", "rig_signature"):
            self.assertIn(phrase, self.handoff)

    def test_source_is_read_only_and_output_is_versioned(self):
        self.assertIn("Never overwrite the source `.bbmodel`", self.skill)
        self.assertIn("versioned output copy", self.skill)
        self.assertIn("single writer", self.handoff)

    def test_scope_boundary_escalates_geometry_and_rig_topology(self):
        for phrase in ("geometry", "UV", "texture", "bone topology", "return to `$fjzm`"):
            self.assertIn(phrase, self.skill + self.handoff)

    def test_revision_diagnoses_before_changing_animation(self):
        for phrase in ("timing", "key pose", "interpolation", "pivot", "clearance", "model-geometry issue"):
            self.assertIn(phrase, self.revision)

    def test_user_approval_is_required_for_revision_plan(self):
        self.assertIn("explicit revision approval", self.skill)
        self.assertIn("Silence is not approval", self.skill)

    def test_actual_blockbench_and_interpolated_evidence_are_required(self):
        self.assertIn("actual Blockbench", self.skill)
        self.assertIn("0.05 seconds", self.skill)
        self.assertIn("loop seam", self.skill)

    def test_machine_validator_and_return_contract_are_required(self):
        self.assertTrue(VALIDATOR.exists())
        self.assertIn("validate_animation_handoff.py", self.skill)
        for phrase in ("animation-system.json", "animation-events.json", "animation-result.json"):
            self.assertIn(phrase, self.skill)


if __name__ == "__main__":
    unittest.main()
