import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "SKILL.md"
AGENT = ROOT / "agents" / "openai.yaml"
HANDOFF = ROOT / "references" / "animation-handoff.md"
REVISION = ROOT / "references" / "animation-revision.md"
BLENDER = ROOT / "references" / "blender-epicfight-backend.md"
COMBAT = ROOT / "references" / "combat-behavior-orchestration.md"
VALIDATOR = ROOT / "scripts" / "validate_animation_handoff.py"
COMBAT_VALIDATOR = ROOT / "scripts" / "validate_combat_behavior.py"


class AnimationSkillPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.agent = AGENT.read_text(encoding="utf-8")
        cls.handoff = HANDOFF.read_text(encoding="utf-8") if HANDOFF.exists() else ""
        cls.revision = REVISION.read_text(encoding="utf-8") if REVISION.exists() else ""
        cls.blender = BLENDER.read_text(encoding="utf-8") if BLENDER.exists() else ""
        cls.combat = COMBAT.read_text(encoding="utf-8") if COMBAT.exists() else ""

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

    def test_direct_conversation_asks_one_plain_numbered_question(self):
        for phrase in (
            "Ask exactly one user-facing question per turn",
            "Use plain Chinese and an internet-friendly conversational tone",
            "Offer 2 or 3 numbered choices",
            "Keep the remaining question queue internal",
            "回复序号就行，也可以直接说你的想法。",
        ):
            self.assertIn(phrase, self.skill)

    def test_actual_blockbench_and_interpolated_evidence_are_required(self):
        self.assertIn("actual Blockbench", self.skill)
        self.assertIn("0.05 seconds", self.skill)
        self.assertIn("loop seam", self.skill)

    def test_animation_workshop_contains_two_internal_backends(self):
        self.assertIn("Blockbench backend", self.skill)
        self.assertIn("Blender / Epic Fight backend", self.skill)
        self.assertIn("Do not create a separate user-facing Blender skill", self.skill)
        self.assertIn("animation_backend", self.skill)

    def test_blender_backend_is_loaded_only_when_selected(self):
        self.assertTrue(BLENDER.exists())
        self.assertIn("Read [blender-epicfight-backend.md](references/blender-epicfight-backend.md)", self.skill)
        for phrase in (
            "Blender Python",
            "Epic Fight",
            "rig-map.json",
            "action-library.json",
            "actual Blender",
            "actual target runtime",
        ):
            self.assertIn(phrase, self.skill + self.blender)

    def test_blender_route_locks_versions_and_ascii_export_ids(self):
        for phrase in (
            "minecraft_version",
            "loader_version",
            "animation_runtime_version",
            "blender_version",
            "exporter_version",
            "official source",
            "ASCII",
        ):
            self.assertIn(phrase, self.blender)

    def test_blender_route_never_claims_runtime_from_authoring_preview(self):
        self.assertIn("Blender preview is not runtime proof", self.blender)
        self.assertIn("runtime_review: required", self.blender)

    def test_machine_validator_and_return_contract_are_required(self):
        self.assertTrue(VALIDATOR.exists())
        self.assertIn("validate_animation_handoff.py", self.skill)
        for phrase in ("animation-system.json", "animation-events.json", "animation-result.json"):
            self.assertIn(phrase, self.skill)

    def test_contractflow_main_only_routing_and_model_immutability_are_explicit(self):
        for phrase in (
            "ContractFlow v1",
            "accepts production only from `$fjzm`",
            "never sends work directly to `$fjzm-model` or `$fjzm-texture`",
            "geometry, UV, base bone hierarchy, bone names, origins, and locators are immutable",
        ):
            self.assertIn(phrase, self.skill)

    def test_combat_motion_loads_the_behavior_orchestration_contract(self):
        self.assertTrue(COMBAT.exists())
        self.assertTrue(COMBAT_VALIDATOR.exists())
        self.assertIn("motion_domain", self.skill)
        self.assertIn("Read [combat-behavior-orchestration.md](references/combat-behavior-orchestration.md)", self.skill)
        self.assertIn("validate_combat_behavior.py", self.skill)
        self.assertIn("combat-behavior-system.json", self.skill)

    def test_combat_orchestration_covers_observable_high_quality_patterns(self):
        for phrase in (
            "weapon category and style",
            "distance and eye-height",
            "weighted selection",
            "repetition penalty",
            "hit and whiff",
            "interrupt",
            "long combo",
            "play_speed",
            "phase transition",
            "runtime evidence",
        ):
            self.assertIn(phrase, self.combat)

    def test_combat_reference_forbids_copying_third_party_animation_assets(self):
        for phrase in (
            "Do not copy",
            "third-party animation files",
            "original key poses",
            "original timing",
        ):
            self.assertIn(phrase, self.combat)

    def test_animation_workshop_authors_contract_but_main_owns_runtime_ai(self):
        self.assertIn("`$fjzm` owns runtime AI", self.combat)
        self.assertIn("does not write gameplay AI", self.combat)


if __name__ == "__main__":
    unittest.main()
