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
            "schema_version": 1,
            "project_id": "energy_defense",
            "asset_id": "crystal_tower",
            "asset_version": "3.0.0",
            "mode": "standalone_revision",
            "source": {
                "model_path": "source/tower.bbmodel",
                "model_sha256": sha(self.model),
                "model_spec_path": "model-spec.json",
                "model_spec_sha256": sha(self.spec),
                "rig_signature": "rig-crystal-tower-v1",
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
                "output_model_path": "versions/tower__animation-r1.bbmodel",
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
        payload["ownership"]["output_model_path"] = "../other.bbmodel"
        result = load_module().validate_handoff(payload, self.root)
        self.assertTrue(any("model_sha256 mismatch" in error for error in result["errors"]))
        self.assertTrue(any("output_model_path" in error for error in result["errors"]))

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
        payload["ownership"]["output_model_path"] = payload["source"]["model_path"]
        payload["ownership"]["single_writer"] = False
        result = load_module().validate_handoff(payload, self.root)
        joined = "\n".join(result["errors"])
        self.assertIn("source_read_only", joined)
        self.assertIn("must differ", joined)
        self.assertIn("single_writer", joined)

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


if __name__ == "__main__":
    unittest.main()
