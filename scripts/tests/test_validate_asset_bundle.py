import hashlib
import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_asset_bundle.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_asset_bundle.py is missing")
    spec = importlib.util.spec_from_file_location("validate_asset_bundle", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AssetBundleValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        identity = {"project_id": "energy_defense", "asset_id": "crystal_tower", "asset_version": "1.0.0"}
        files = {
            "model-spec.json": {**identity, "animation_system": {"rig_signature": "rig-tower-v1"}},
            "animation-system.json": {**identity, "rig_signature": "rig-tower-v1"},
            "animation-events.json": {**identity, "events": [{"sound_event": "mymod:crystal_tower.fire", "particle_contract_id": "tower_muzzle"}]},
            "particle-contracts.json": {**identity, "contracts": [{"effect_id": "tower_muzzle"}]},
            "audio-manifest.json": {**identity, "mappings": [{"event_id": "mymod:crystal_tower.fire"}]},
        }
        for name, payload in files.items():
            (self.base / name).write_text(json.dumps(payload), encoding="utf-8")
        (self.base / "model.bbmodel").write_text('{"meta":{"model_format":"free"}}', encoding="utf-8")
        (self.base / "texture.png").write_bytes(b"png-placeholder")
        self.manifest = {
            "schema_version": 1,
            **identity,
            "rig_signature": "rig-tower-v1",
            "resources": [
                {"kind": name.split(".")[0], "path": name, "sha256": sha(self.base / name)}
                for name in [
                    "model-spec.json", "model.bbmodel", "texture.png", "animation-system.json",
                    "animation-events.json", "particle-contracts.json", "audio-manifest.json",
                ]
            ],
            "workflow_evidence": [
                {
                    "step": "asset_identity_locked",
                    "timestamp": "2026-07-17T12:00:00Z",
                    "status": "verified",
                    "input_hashes": [],
                    "output_hashes": [sha(self.base / "model-spec.json")],
                    "approval_evidence": "用户确认目标模型",
                    "tool_version": "skill-v11-rc",
                },
                {
                    "step": "attachments_inventoried",
                    "timestamp": "2026-07-17T12:01:00Z",
                    "status": "verified",
                    "input_hashes": [],
                    "output_hashes": [],
                    "approval_evidence": None,
                    "tool_version": "skill-v11-rc",
                },
            ],
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_consistent_identity_scoped_bundle(self):
        result = self.validator.validate_bundle(self.manifest, self.base)
        self.assertEqual(result["errors"], [])

    def test_rejects_hash_mismatch_and_path_escape(self):
        manifest = deepcopy(self.manifest)
        manifest["resources"][0]["sha256"] = "0" * 64
        manifest["resources"][1]["path"] = "../other/model.bbmodel"
        result = self.validator.validate_bundle(manifest, self.base)
        self.assertTrue(any("SHA-256 mismatch" in error for error in result["errors"]))
        self.assertTrue(any("outside bundle root" in error for error in result["errors"]))

    def test_rejects_embedded_cross_model_identity_and_rig(self):
        payload = json.loads((self.base / "animation-system.json").read_text(encoding="utf-8"))
        payload["asset_id"] = "three_headed_wolf"
        payload["rig_signature"] = "rig-wolf-v1"
        (self.base / "animation-system.json").write_text(json.dumps(payload), encoding="utf-8")
        manifest = deepcopy(self.manifest)
        for resource in manifest["resources"]:
            if resource["path"] == "animation-system.json":
                resource["sha256"] = sha(self.base / "animation-system.json")
        result = self.validator.validate_bundle(manifest, self.base)
        self.assertTrue(any("cross-model identity" in error for error in result["errors"]))
        self.assertTrue(any("rig signature mismatch" in error for error in result["errors"]))

    def test_rejects_missing_sound_or_particle_event_targets(self):
        (self.base / "audio-manifest.json").write_text(json.dumps({"project_id":"energy_defense","asset_id":"crystal_tower","asset_version":"1.0.0","mappings":[]}), encoding="utf-8")
        (self.base / "particle-contracts.json").write_text(json.dumps({"project_id":"energy_defense","asset_id":"crystal_tower","asset_version":"1.0.0","contracts":[]}), encoding="utf-8")
        manifest = deepcopy(self.manifest)
        for resource in manifest["resources"]:
            if resource["path"] in {"audio-manifest.json", "particle-contracts.json"}:
                resource["sha256"] = sha(self.base / resource["path"])
        result = self.validator.validate_bundle(manifest, self.base)
        self.assertTrue(any("unresolved sound_event" in error for error in result["errors"]))
        self.assertTrue(any("unresolved particle_contract_id" in error for error in result["errors"]))

    def test_rejects_out_of_order_or_unverifiable_evidence(self):
        manifest = deepcopy(self.manifest)
        manifest["workflow_evidence"][1]["step"] = "mapping_approved"
        manifest["workflow_evidence"][1].pop("tool_version")
        result = self.validator.validate_bundle(manifest, self.base)
        self.assertTrue(any("evidence steps are out of order" in error for error in result["errors"]))
        self.assertTrue(any("tool_version" in error for error in result["errors"]))

    def test_model_first_bundle_requires_runtime_contract_resource(self):
        model_spec = json.loads((self.base / "model-spec.json").read_text(encoding="utf-8"))
        model_spec["mod_project"] = {"route_choice": "model_first", "project_status": "runtime_deferred"}
        (self.base / "model-spec.json").write_text(json.dumps(model_spec), encoding="utf-8")
        manifest = deepcopy(self.manifest)
        for resource in manifest["resources"]:
            if resource["path"] == "model-spec.json":
                resource["sha256"] = sha(self.base / "model-spec.json")
        result = self.validator.validate_bundle(manifest, self.base)
        self.assertTrue(any("model_first bundle requires runtime-contract.json" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
