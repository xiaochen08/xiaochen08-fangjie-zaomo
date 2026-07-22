import hashlib
import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_texture_handoff.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_texture_handoff.py is missing")
    spec = importlib.util.spec_from_file_location("validate_texture_handoff", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TextureHandoffValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "source").mkdir()
        (self.root / "references").mkdir()
        self.model = self.root / "source" / "cat.bbmodel"
        self.model.write_text('{"meta":{"model_format":"free"}}', encoding="utf-8")
        self.spec = self.root / "model-spec.json"
        self.spec.write_text('{"asset_id":"traveler_cat"}', encoding="utf-8")
        self.reference = self.root / "references" / "approved-cat.png"
        self.reference.write_bytes(b"approved-reference")
        self.shader = self.root / "shader-contract.json"
        self.shader.write_text('{"support_claim":"baseline_only"}', encoding="utf-8")
        self.payload = {
            "protocol_version": "1.0",
            "message_type": "handoff",
            "message_id": "msg-texture-001",
            "correlation_id": "corr-traveler-cat-001",
            "from_skill": "fjzm",
            "to_skill": "fjzm-texture",
            "stage": "texture",
            "idempotency_key": "travelers:traveler_cat:4.0.0:texture:0",
            "attempt": 0,
            "writer_lock": {"owner": "fjzm-texture", "surface": "texture", "output_version": "texture-r1"},
            "dependencies": [{"stage": "geometry", "status": "passed"}],
            "schema_version": 1,
            "project_id": "travelers",
            "asset_id": "traveler_cat",
            "asset_version": "4.0.0",
            "mode": "standalone_retexture",
            "source": {
                "model_path": "source/cat.bbmodel",
                "model_sha256": sha(self.model),
                "model_spec_path": "model-spec.json",
                "model_spec_sha256": sha(self.spec),
                "geometry_signature": "geometry-traveler-cat-v2",
                "rig_signature": "rig-traveler-cat-v2",
                "uv_signature": "uv-traveler-cat-v1",
                "source_read_only": True,
            },
            "references": [
                {"path": "references/approved-cat.png", "sha256": sha(self.reference), "approval_status": "approved"}
            ],
            "request": {
                "allowed_mutations": ["base_texture", "material_ramps", "eye_variants"],
                "protected_mutations": ["geometry", "uv_layout", "rig", "animations", "locators"],
            },
            "analysis": {
                "reference_scene_lighting_recorded": True,
                "intrinsic_material_cues_separated": True,
                "neutral_albedo": True,
                "scene_lighting_baked": False,
            },
            "texture": {
                "atlas": [128, 128],
                "texels_per_unit": 1,
                "nearest_neighbor": True,
                "antialiasing": False,
                "ao_policy": "local_opaque_contact_only",
                "edge_accent_policy": "conditional_1_2_px",
                "material_library": [
                    {
                        "id": "warm_white_fur",
                        "type": "cloth",
                        "ramp": ["#f4f0e7", "#d9d2c5", "#aaa294"],
                    },
                    {
                        "id": "tan_pack",
                        "type": "leather",
                        "ramp": ["#d0ad68", "#9a713d", "#5c3e27"],
                    },
                ],
            },
            "uv": {
                "uv_signature": "uv-traveler-cat-v1",
                "uniform_texel_density": True,
                "padding_pixels": 2,
                "seam_pairs": [{"a": "head_front:right", "b": "head_right:left"}],
                "eye_region": {
                    "mode": "atlas_frames",
                    "runtime_support": {"status": "supported", "adapter": "geckolib_texture_swap"},
                    "frames": [
                        {"state": "normal", "x": 96, "y": 0, "w": 8, "h": 8},
                        {"state": "closed", "x": 104, "y": 0, "w": 8, "h": 8},
                        {"state": "angry", "x": 112, "y": 0, "w": 8, "h": 8},
                    ],
                },
            },
            "shader": {"contract_path": "shader-contract.json", "contract_sha256": sha(self.shader)},
            "approval": {
                "analysis_plan": {"status": "approved", "evidence": "按解析方案制作"},
                "texture_production": {"status": "approved", "evidence": "制作第一版贴图"},
            },
            "ownership": {
                "writer_skill": "fjzm-texture",
                "single_writer": True,
                "write_lock_id": "traveler-cat-texture-r1",
                "output_model_path": "versions/cat__texture-r1.bbmodel",
                "output_texture_path": "textures/cat__texture-r1.png",
            },
            "integration": {"main_change_approval": {"status": "not_required", "evidence": None}},
            "return_contract_path": "texture-result.json",
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_safe_standalone_retexture(self):
        result = load_module().validate_handoff(self.payload, self.root)
        self.assertEqual(result["errors"], [])

    def test_rejects_identity_hash_mismatch_and_path_escape(self):
        payload = deepcopy(self.payload)
        payload["source"]["model_sha256"] = "0" * 64
        payload["ownership"]["output_texture_path"] = "../cat.png"
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("model_sha256 mismatch", joined)
        self.assertIn("output_texture_path", joined)

    def test_requires_geometry_uv_identity_and_read_only_source(self):
        payload = deepcopy(self.payload)
        payload["source"]["geometry_signature"] = ""
        payload["source"]["uv_signature"] = None
        payload["source"]["source_read_only"] = False
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("geometry_signature", joined)
        self.assertIn("uv_signature", joined)
        self.assertIn("source_read_only", joined)

    def test_standalone_retexture_rejects_geometry_uv_rig_or_animation_changes(self):
        payload = deepcopy(self.payload)
        payload["request"]["allowed_mutations"].extend(["geometry", "uv_layout", "animations"])
        result = load_module().validate_handoff(payload, self.root)
        self.assertTrue(any("standalone_retexture cannot allow" in error for error in result["errors"]))

    def test_uv_change_requires_delegated_mode_and_main_approval(self):
        payload = deepcopy(self.payload)
        payload["mode"] = "delegated_uv_and_texture"
        payload["request"]["allowed_mutations"].append("uv_layout")
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("main_change_approval", joined)

    def test_rejects_baked_scene_light_antialias_and_weak_material_ramps(self):
        payload = deepcopy(self.payload)
        payload["analysis"]["scene_lighting_baked"] = True
        payload["texture"]["antialiasing"] = True
        payload["texture"]["material_library"][0]["ramp"] = ["#ffffff", "#ffffff"]
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("scene_lighting_baked", joined)
        self.assertIn("antialiasing", joined)
        self.assertIn("at least 3 unique colors", joined)

    def test_eye_frames_require_supported_runtime_two_to_three_states_and_bounds(self):
        payload = deepcopy(self.payload)
        payload["uv"]["eye_region"]["runtime_support"] = {"status": "unresolved", "adapter": None}
        payload["uv"]["eye_region"]["frames"].append({"state": "hurt", "x": 126, "y": 126, "w": 8, "h": 8})
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("runtime support", joined)
        self.assertIn("2 or 3 eye frames", joined)
        self.assertIn("outside atlas bounds", joined)

    def test_requires_two_explicit_approvals_and_single_writer_versioned_output(self):
        payload = deepcopy(self.payload)
        payload["approval"]["analysis_plan"] = {"status": "proposed", "evidence": None}
        payload["approval"]["texture_production"] = {"status": "proposed", "evidence": None}
        payload["ownership"]["writer_skill"] = "fjzm"
        payload["ownership"]["single_writer"] = False
        payload["ownership"]["output_model_path"] = payload["source"]["model_path"]
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        for phrase in ("analysis_plan approval", "texture_production approval", "writer_skill", "single_writer", "must differ"):
            self.assertIn(phrase, joined)

    def test_contractflow_requires_main_route_protocol_attempt_and_passed_geometry(self):
        payload = deepcopy(self.payload)
        payload["protocol_version"] = "2.0"
        payload["from_skill"] = "fjzm-animation"
        payload["attempt"] = 3
        payload["dependencies"][0]["status"] = "failed"
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        for phrase in ("protocol_version", "central", "attempt", "geometry dependency"):
            self.assertIn(phrase, joined)

    def test_geometry_and_rig_interfaces_are_always_immutable(self):
        payload = deepcopy(self.payload)
        payload["mode"] = "delegated_uv_and_texture"
        payload["request"]["allowed_mutations"].extend(["geometry", "rig", "origins", "locators"])
        payload["integration"]["main_change_approval"] = {"status": "approved", "evidence": "only UV approved"}
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        for phrase in ("geometry", "rig", "origins", "locators"):
            self.assertIn(phrase, joined)

    def test_rig_signature_is_required_from_model_result(self):
        payload = deepcopy(self.payload)
        payload["source"]["rig_signature"] = ""
        result = load_module().validate_handoff(payload, self.root)
        self.assertIn("rig_signature", "\n".join(result["errors"]))


if __name__ == "__main__":
    unittest.main()
