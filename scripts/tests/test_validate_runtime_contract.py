import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_runtime_contract.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_runtime_contract.py is missing")
    spec = importlib.util.spec_from_file_location("validate_runtime_contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def complete_high_risk_contract():
    return {
        "schema_version": 1,
        "project_id": "energy_defense",
        "asset_id": "crystal_tower",
        "asset_version": "1.1.0",
        "edition": "java",
        "route_choice": "model_first",
        "project_status": "runtime_deferred",
        "asset_role": "block_entity",
        "runtime_risk": "high",
        "runtime_features": [
            "animation", "particles", "audio", "projectile", "targeting",
            "damage", "networking", "emissive",
        ],
        "target_profile": {
            "minecraft_version_status": "provisional",
            "minecraft_version": "1.21.x",
            "loader_status": "unresolved",
            "loader": None,
            "mappings_status": "unresolved",
            "mappings": None,
            "animation_runtime_status": "provisional",
            "animation_runtime": "geckolib_or_equivalent",
            "render_path_status": "locked",
            "render_path": "block_entity_renderer",
            "multiplayer_required": True,
        },
        "stable_contract": {
            "rig_signature": "rig-crystal-tower-v1",
            "animation_ids": ["animation.crystal_tower.idle", "animation.crystal_tower.attack"],
            "event_ids": ["energy_defense:crystal_tower.fire"],
            "locator_ids": ["projectile_spawn", "core_energy_emitter"],
            "texture_ids": ["crystal_tower", "crystal_tower_emissive"],
        },
        "mod_first_recommendation": {
            "required": True,
            "status": "declined",
            "evidence": "用户确认暂不创建 Mod，并要求先制作运行时中立模型源",
        },
        "production_gate": {
            "allowed_stage": "runtime_neutral_source",
            "blockers": ["actual Mod project inspection", "platform-specific export"],
        },
        "risk_acceptance": {
            "required": True,
            "status": "approved",
            "evidence": "用户接受后续接入时可能需要调整适配层",
            "accepted_consequences": [
                "runtime exports deferred",
                "integration rework may be required",
                "no game-ready claim",
            ],
        },
        "integration_handoff": {
            "source_format": "bbmodel",
            "export_status": "deferred",
            "adapter_status": "not_started",
            "project_path": None,
        },
        "qualification_status": "unverified",
    }


class RuntimeContractValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_module()
        self.complete = complete_high_risk_contract()

    def test_accepts_complete_high_risk_model_first_contract(self):
        result = self.validator.validate_contract(self.complete)
        self.assertEqual(result["errors"], [])

    def test_rejects_high_risk_without_decline_and_risk_evidence(self):
        contract = deepcopy(self.complete)
        contract["mod_first_recommendation"] = {"required": True, "status": "presented", "evidence": ""}
        contract["risk_acceptance"] = {"required": True, "status": "pending", "evidence": "", "accepted_consequences": []}
        result = self.validator.validate_contract(contract)
        self.assertTrue(any("verbatim decline evidence" in error for error in result["errors"]))
        self.assertTrue(any("explicit risk acceptance" in error for error in result["errors"]))

    def test_unresolved_critical_render_or_animation_fields_force_graybox(self):
        contract = deepcopy(self.complete)
        contract["target_profile"]["render_path_status"] = "unresolved"
        contract["target_profile"]["render_path"] = None
        contract["production_gate"]["allowed_stage"] = "runtime_neutral_source"
        result = self.validator.validate_contract(contract)
        self.assertTrue(any("unresolved critical runtime fields require graybox_only" in error for error in result["errors"]))

        contract["production_gate"]["allowed_stage"] = "graybox_only"
        result = self.validator.validate_contract(contract)
        self.assertFalse(any("unresolved critical runtime fields require graybox_only" in error for error in result["errors"]))

    def test_model_first_never_allows_platform_export_or_verified_claim(self):
        contract = deepcopy(self.complete)
        contract["production_gate"]["allowed_stage"] = "platform_export"
        contract["integration_handoff"]["export_status"] = "exported"
        contract["qualification_status"] = "verified"
        result = self.validator.validate_contract(contract)
        self.assertTrue(any("platform-specific export requires an inspected project" in error for error in result["errors"]))
        self.assertTrue(any("runtime_deferred cannot be verified" in error for error in result["errors"]))

    def test_dynamic_or_runtime_heavy_asset_cannot_be_low_risk(self):
        contract = deepcopy(self.complete)
        contract["runtime_risk"] = "low"
        result = self.validator.validate_contract(contract)
        self.assertTrue(any("dynamic or runtime-heavy assets cannot be classified low risk" in error for error in result["errors"]))

    def test_requires_stable_unique_ids_and_projectile_locator(self):
        contract = deepcopy(self.complete)
        contract["stable_contract"]["event_ids"] = ["Bad Event", "Bad Event"]
        contract["stable_contract"]["locator_ids"] = ["core_energy_emitter"]
        result = self.validator.validate_contract(contract)
        self.assertTrue(any("stable lowercase IDs" in error for error in result["errors"]))
        self.assertTrue(any("projectile_spawn" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
