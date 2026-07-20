import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_shader_contract.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_shader_contract.py is missing")
    spec = importlib.util.spec_from_file_location("validate_shader_contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def complete_contract():
    return {
        "schema_version": 1,
        "project_id": "energy_defense",
        "asset_id": "crystal_tower",
        "asset_version": "1.2.0",
        "edition": "java",
        "compatibility_tier": "vanilla_baseline",
        "support_claim": "baseline_only",
        "baseline_required": True,
        "target_stack": {
            "minecraft_version_status": "locked",
            "minecraft_version": "1.21.1",
            "shader_loader_status": "not_applicable",
            "shader_loader": None,
            "shader_loader_version": None,
            "shader_packs": [],
            "material_standard": "none",
            "material_standard_version": None,
        },
        "materials": {
            "base_texture": "textures/crystal_tower.png",
            "emissive_mask": None,
            "normal_map": None,
            "specular_map": None,
            "roughness_map": None,
            "metalness_map": None,
            "translucency": "opaque",
            "render_layer": "solid",
            "painted_lighting_policy": "neutral_only",
        },
        "emissive": {
            "visual_emissive": False,
            "world_light": "none",
            "world_light_runtime_owner": None,
            "bloom_dependency": "none",
        },
        "fallback": {
            "no_shader_supported": True,
            "missing_optional_maps": "base_texture_only",
            "fallback_verified": False,
        },
        "test_matrix": [
            {"case_id": "no_shader_daylight", "required": True, "status": "not_run", "evidence": []},
            {"case_id": "no_shader_dark", "required": True, "status": "not_run", "evidence": []},
            {"case_id": "side_lighting", "required": True, "status": "not_run", "evidence": []},
        ],
        "qualification_status": "unverified",
    }


class ShaderContractValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_module()

    def test_accepts_complete_vanilla_baseline_contract(self):
        result = self.validator.validate_contract(complete_contract())
        self.assertEqual(result["errors"], [])

    def test_named_shader_target_requires_locked_loader_pack_version_and_source(self):
        payload = complete_contract()
        payload["compatibility_tier"] = "specified_shader_pack"
        payload["support_claim"] = "named_targets_only"
        payload["target_stack"].update({
            "shader_loader_status": "unresolved",
            "shader_loader": "iris",
            "shader_loader_version": None,
            "shader_packs": [{"name": "Example", "version": None, "status": "provisional", "source_url": None, "checked_at": None}],
        })
        result = self.validator.validate_contract(payload)
        joined = "\n".join(result["errors"])
        self.assertIn("locked shader loader", joined)
        self.assertIn("locked exact shader pack", joined)

    def test_pbr_target_requires_locked_standard_version_and_maps(self):
        payload = complete_contract()
        payload["compatibility_tier"] = "pbr_targeted"
        payload["support_claim"] = "named_targets_only"
        payload["target_stack"].update({
            "shader_loader_status": "locked",
            "shader_loader": "iris",
            "shader_loader_version": "1.8.8",
            "shader_packs": [{"name": "Example", "version": "1.0", "status": "locked", "source_url": "https://example.invalid", "checked_at": "2026-07-20"}],
            "material_standard": "none",
            "material_standard_version": None,
        })
        result = self.validator.validate_contract(payload)
        self.assertTrue(any("PBR material standard" in error for error in result["errors"]))
        self.assertTrue(any("normal/specular or roughness/metalness maps" in error for error in result["errors"]))

    def test_emissive_mask_and_world_light_runtime_owner_are_enforced(self):
        payload = complete_contract()
        payload["emissive"].update({"visual_emissive": True, "world_light": "dynamic_light_integration", "world_light_runtime_owner": None})
        payload["emissive"]["bloom_dependency"] = "optional"
        result = self.validator.validate_contract(payload)
        self.assertTrue(any("emissive_mask" in error for error in result["errors"]))
        self.assertTrue(any("world_light_runtime_owner" in error for error in result["errors"]))

    def test_translucency_requires_render_layer_and_overlap_test(self):
        payload = complete_contract()
        payload["materials"].update({"translucency": "translucent", "render_layer": None})
        result = self.validator.validate_contract(payload)
        joined = "\n".join(result["errors"])
        self.assertIn("render_layer", joined)
        self.assertIn("transparency_overlap", joined)

    def test_named_shader_target_requires_target_and_bloom_cases(self):
        payload = complete_contract()
        payload["compatibility_tier"] = "specified_shader_pack"
        payload["support_claim"] = "named_targets_only"
        payload["target_stack"].update({
            "shader_loader_status": "locked", "shader_loader": "iris", "shader_loader_version": "1.8.8",
            "shader_packs": [{"name": "Example", "version": "1.0", "status": "locked", "source_url": "https://example.invalid", "checked_at": "2026-07-20"}],
        })
        payload["emissive"]["bloom_dependency"] = "optional"
        result = self.validator.validate_contract(payload)
        joined = "\n".join(result["errors"])
        self.assertIn("target_shader_daylight", joined)
        self.assertIn("target_shader_dark", joined)
        self.assertIn("bloom_stress", joined)

    def test_universal_shader_support_claim_is_rejected(self):
        payload = complete_contract()
        payload["support_claim"] = "all_shader_packs"
        result = self.validator.validate_contract(payload)
        self.assertTrue(any("support_claim" in error for error in result["errors"]))

    def test_verified_status_requires_all_required_cases_passed_with_evidence(self):
        payload = complete_contract()
        payload["qualification_status"] = "verified"
        payload["test_matrix"][0]["status"] = "passed"
        result = self.validator.validate_contract(payload)
        joined = "\n".join(result["errors"])
        self.assertIn("required test cases must be passed", joined)
        self.assertIn("evidence", joined)


if __name__ == "__main__":
    unittest.main()
