import hashlib
import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_animation_handoff.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_animation_handoff.py is missing")
    spec = importlib.util.spec_from_file_location("validate_animation_handoff", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AnimationHandoffValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.model = self.root / "source" / "tower.bbmodel"
        self.model.parent.mkdir()
        self.model.write_text('{"meta":{"model_format":"free"}}', encoding="utf-8")
        self.spec = self.root / "model-spec.json"
        self.spec.write_text('{"asset_id":"crystal_tower"}', encoding="utf-8")
        self.payload = {
            "protocol_version": "1.0",
            "message_type": "handoff",
            "message_id": "msg-animation-001",
            "correlation_id": "corr-crystal-tower-001",
            "from_skill": "fjzm",
            "to_skill": "fjzm-animation",
            "stage": "animation",
            "idempotency_key": "energy_defense:crystal_tower:3.0.0:animation:0",
            "attempt": 0,
            "writer_lock": {"owner": "fjzm-animation", "surface": "animation", "output_version": "animation-r1"},
            "dependencies": [{"stage": "geometry", "status": "passed"}],
            "schema_version": 2,
            "project_id": "energy_defense",
            "asset_id": "crystal_tower",
            "asset_version": "3.0.0",
            "mode": "standalone_revision",
            "animation_backend": "blockbench",
            "motion_domain": "mechanism",
            "source": {
                "model_path": "source/tower.bbmodel",
                "model_sha256": sha(self.model),
                "model_spec_path": "model-spec.json",
                "model_spec_sha256": sha(self.spec),
                "rig_signature": "rig-crystal-tower-v1",
                "geometry_signature": "geometry-crystal-tower-v1",
                "uv_signature": "uv-crystal-tower-v1",
                "locator_signature": "locators-crystal-tower-v1",
                "source_read_only": True,
            },
            "request": {
                "animation_ids": ["animation.tower.attack"],
                "issue_report": "orbit is stiff and clips during cooldown",
                "allowed_mutations": ["keyframes", "timing", "interpolation", "event_timing"],
                "protected_mutations": ["geometry", "uv", "textures", "bone_names", "bone_hierarchy", "locators"],
            },
            "approval": {"status": "approved", "evidence": "优化攻击动画，不改模型造型"},
            "ownership": {
                "writer_skill": "fjzm-animation",
                "single_writer": True,
                "write_lock_id": "crystal_tower-animation-revision-001",
                "output_project_path": "versions/tower__animation-r1.bbmodel",
            },
            "integration": {
                "dependent_rebind_required": False,
                "main_change_approval": {"status": "not_required", "evidence": None},
            },
            "return_contract_path": "animation-result.json",
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_safe_standalone_revision(self):
        result = load_module().validate_handoff(self.payload, self.root)
        self.assertEqual(result["errors"], [])

    def test_rejects_hash_mismatch_and_path_escape(self):
        payload = deepcopy(self.payload)
        payload["source"]["model_sha256"] = "0" * 64
        payload["ownership"]["output_project_path"] = "../other.bbmodel"
        result = load_module().validate_handoff(payload, self.root)
        self.assertTrue(any("model_sha256 mismatch" in error for error in result["errors"]))
        self.assertTrue(any("output_project_path" in error for error in result["errors"]))

    def test_requires_identity_rig_and_animation_scope(self):
        payload = deepcopy(self.payload)
        payload["asset_id"] = ""
        payload["source"]["rig_signature"] = None
        payload["request"]["animation_ids"] = []
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("asset_id", joined)
        self.assertIn("rig_signature", joined)
        self.assertIn("animation_ids", joined)

    def test_requires_read_only_source_versioned_output_and_single_writer(self):
        payload = deepcopy(self.payload)
        payload["source"]["source_read_only"] = False
        payload["ownership"]["output_project_path"] = payload["source"]["model_path"]
        payload["ownership"]["single_writer"] = False
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("source_read_only", joined)
        self.assertIn("must differ", joined)
        self.assertIn("single_writer", joined)

    def test_requires_an_explicit_supported_backend(self):
        payload = deepcopy(self.payload)
        payload.pop("animation_backend")
        result = load_module().validate_handoff(payload, self.root)
        self.assertTrue(any("animation_backend" in error for error in result["errors"]))

    def test_requires_an_explicit_supported_motion_domain(self):
        payload = deepcopy(self.payload)
        payload.pop("motion_domain")
        result = load_module().validate_handoff(payload, self.root)
        self.assertTrue(any("motion_domain" in error for error in result["errors"]))

        payload["motion_domain"] = "cinematic_unknown"
        result = load_module().validate_handoff(payload, self.root)
        self.assertTrue(any("motion_domain" in error for error in result["errors"]))

    def test_combat_domain_requires_a_behavior_contract_output(self):
        payload = deepcopy(self.payload)
        payload["motion_domain"] = "combat"
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("combat_behavior_required", joined)
        self.assertIn("combat_behavior_path", joined)

        payload["request"]["combat_behavior_required"] = True
        payload["ownership"]["combat_behavior_path"] = "contracts/combat-behavior-system-animation-r1.json"
        result = load_module().validate_handoff(payload, self.root)
        self.assertEqual(result["errors"], [])

        payload["animation_backend"] = "unknown"
        result = load_module().validate_handoff(payload, self.root)
        self.assertTrue(any("animation_backend" in error for error in result["errors"]))

    def test_accepts_version_locked_blender_epicfight_backend(self):
        payload = deepcopy(self.payload)
        payload["animation_backend"] = "blender_epicfight"
        payload["backend_contract"] = {
            "target": {
                "edition": "java",
                "minecraft_version": "1.20.1",
                "loader": "forge",
                "loader_version": "47.2.20",
                "animation_runtime": "epicfight",
                "animation_runtime_version": "20.10.3",
            },
            "toolchain": {
                "blender_version": "4.2.0",
                "exporter_name": "epic-fight-blender-exporter",
                "exporter_version": "1.0.0",
                "exporter_source_url": "https://github.com/Epic-Fight/epicfightmod",
                "checked_at": "2026-07-22",
            },
            "rig_bridge": {
                "source_rig_signature": "rig-crystal-tower-v1",
                "target_armature": "epicfight:entity/biped",
                "coordinate_system": {"up": "+Y", "forward": "-Z"},
                "unit_scale": 1.0,
                "mapping_policy": "create_versioned_map",
            },
            "control": {
                "authoring_mode": "blender_python",
                "visual_review": "interactive_blender",
                "runtime_review": "required",
            },
        }
        payload["ownership"]["output_project_path"] = "versions/tower__animation-r1.blend"
        payload["ownership"]["output_runtime_directory"] = "exports/epicfight/tower/animation-r1"
        payload["ownership"]["rig_map_path"] = "contracts/rig-map-animation-r1.json"
        payload["ownership"]["action_library_path"] = "contracts/action-library-animation-r1.json"
        result = load_module().validate_handoff(payload, self.root)
        self.assertEqual(result["errors"], [])

    def test_blender_backend_rejects_unlocked_runtime_exporter_and_rig_bridge(self):
        payload = deepcopy(self.payload)
        payload["animation_backend"] = "blender_epicfight"
        payload["backend_contract"] = {
            "target": {"edition": "java", "minecraft_version": "1.20.1", "loader": "forge"},
            "toolchain": {"blender_version": "", "exporter_source_url": "not-official"},
            "rig_bridge": {"source_rig_signature": "wrong-rig"},
            "control": {"authoring_mode": "mouse_only", "runtime_review": "optional"},
        }
        payload["ownership"]["output_project_path"] = "versions/tower__animation-r1.bbmodel"
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        for phrase in (
            "animation_runtime_version",
            "blender_version",
            "exporter_version",
            "official HTTPS",
            "source_rig_signature",
            "authoring_mode",
            "runtime_review",
            ".blend",
            "output_runtime_directory",
            "rig_map_path",
            "action_library_path",
        ):
            self.assertIn(phrase, joined)

    def test_export_identifiers_must_be_ascii_safe(self):
        payload = deepcopy(self.payload)
        payload["request"]["animation_ids"] = ["动画.塔.攻击"]
        payload["ownership"]["output_project_path"] = "versions/塔__animation-r1.bbmodel"
        result = load_module().validate_handoff(payload, self.root)
        self.assertTrue(any("ASCII" in error for error in result["errors"]))

    def test_standalone_revision_rejects_geometry_or_bone_topology_mutation(self):
        payload = deepcopy(self.payload)
        payload["request"]["allowed_mutations"].extend(["geometry", "bone_topology"])
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("standalone_revision cannot allow", joined)

    def test_rig_topology_change_requires_delegated_mode_main_approval_and_rebind(self):
        payload = deepcopy(self.payload)
        payload["mode"] = "delegated_rig_and_animation"
        payload["request"]["allowed_mutations"].append("bone_topology")
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("main_change_approval", joined)
        self.assertIn("dependent_rebind_required", joined)

    def test_requires_explicit_approval_and_writer_identity(self):
        payload = deepcopy(self.payload)
        payload["approval"] = {"status": "proposed", "evidence": None}
        payload["ownership"]["writer_skill"] = "fjzm"
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("approval", joined)
        self.assertIn("writer_skill", joined)

    def test_contractflow_requires_main_route_protocol_attempt_and_passed_geometry(self):
        payload = deepcopy(self.payload)
        payload["protocol_version"] = "2.0"
        payload["from_skill"] = "fjzm-texture"
        payload["attempt"] = 3
        payload["dependencies"][0]["status"] = "failed"
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        for phrase in ("protocol_version", "central", "attempt", "geometry dependency"):
            self.assertIn(phrase, joined)

    def test_all_upstream_model_interfaces_are_required(self):
        payload = deepcopy(self.payload)
        for key in ("geometry_signature", "uv_signature", "locator_signature"):
            payload["source"][key] = ""
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        for phrase in ("geometry_signature", "uv_signature", "locator_signature"):
            self.assertIn(phrase, joined)

    def test_animation_can_never_mutate_model_owned_interfaces(self):
        payload = deepcopy(self.payload)
        payload["mode"] = "delegated_rig_and_animation"
        payload["request"]["allowed_mutations"].extend(["geometry", "bone_hierarchy", "origins", "locators"])
        payload["integration"]["main_change_approval"] = {"status": "approved", "evidence": "requested"}
        payload["integration"]["dependent_rebind_required"] = True
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        for phrase in ("geometry", "bone_hierarchy", "origins", "locators"):
            self.assertIn(phrase, joined)


if __name__ == "__main__":
    unittest.main()
