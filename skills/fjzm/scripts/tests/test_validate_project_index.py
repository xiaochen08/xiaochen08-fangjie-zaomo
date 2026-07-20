import hashlib
import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_project_index.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_project_index.py is missing")
    spec = importlib.util.spec_from_file_location("validate_project_index", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_asset(root: Path, asset_id: str, *, shared_event=None):
    folder = root / "assets" / asset_id
    folder.mkdir(parents=True)
    identity = {"project_id": "energy_defense", "asset_id": asset_id, "asset_version": "1.0.0"}
    rig = f"rig-{asset_id}-v1"
    event_id = shared_event or f"mymod:{asset_id}.fire"
    mapping = {"event_id": event_id, "output_file": f"sounds/{asset_id}/fire.ogg"}
    if shared_event:
        mapping.update({"shared_audio_library": "mechanical_common", "shared_audio_approved": True})
    payloads = {
        "model-spec.json": {**identity, "animation_system": {"rig_signature": rig}},
        "animation-system.json": {**identity, "rig_signature": rig, "clips": [{"animation_id": f"animation.{asset_id}.attack"}]},
        "audio-manifest.json": {**identity, "mappings": [mapping]},
        "particle-contracts.json": {**identity, "contracts": [{"effect_id": f"{asset_id}_muzzle"}]},
    }
    for name, payload in payloads.items():
        (folder / name).write_text(json.dumps(payload), encoding="utf-8")
    bundle = {
        "schema_version": 1,
        **identity,
        "rig_signature": rig,
        "resources": [
            {"kind": name.removesuffix(".json"), "path": name, "sha256": sha(folder / name)}
            for name in payloads
        ],
        "workflow_evidence": [{
            "step": "asset_identity_locked", "timestamp": "2026-07-17T12:00:00Z", "status": "verified",
            "input_hashes": [], "output_hashes": [sha(folder / "model-spec.json")],
            "approval_evidence": "用户确认", "tool_version": "skill-v13-rc",
        }],
    }
    bundle_path = folder / "asset-bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return {
        "asset_id": asset_id,
        "asset_version": "1.0.0",
        "rig_signature": rig,
        "bundle_path": bundle_path.relative_to(root).as_posix(),
        "bundle_sha256": sha(bundle_path),
    }


class ProjectIndexValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.tower = create_asset(self.root, "crystal_tower")
        self.wolf = create_asset(self.root, "three_headed_wolf")
        self.index = {"schema_version": 1, "project_id": "energy_defense", "assets": [self.tower, self.wolf]}

    def tearDown(self):
        self.temp.cleanup()

    def refresh_bundle_hash(self, entry):
        entry["bundle_sha256"] = sha(self.root / entry["bundle_path"])

    def test_accepts_two_identity_isolated_asset_bundles(self):
        result = self.validator.validate_project_index(self.index, self.root)
        self.assertEqual(result["errors"], [])

    def test_rejects_duplicate_asset_identity_and_bundle_path_escape(self):
        index = deepcopy(self.index)
        index["assets"][1]["asset_id"] = "crystal_tower"
        index["assets"][0]["bundle_path"] = "../outside/asset-bundle.json"
        result = self.validator.validate_project_index(index, self.root)
        self.assertTrue(any("duplicate asset_id" in error for error in result["errors"]))
        self.assertTrue(any("outside project root" in error for error in result["errors"]))

    def test_rejects_embedded_cross_model_identity(self):
        path = self.root / "assets/three_headed_wolf/animation-system.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["asset_id"] = "crystal_tower"
        path.write_text(json.dumps(payload), encoding="utf-8")
        bundle_path = self.root / self.wolf["bundle_path"]
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        next(item for item in bundle["resources"] if item["path"] == "animation-system.json")["sha256"] = sha(path)
        bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
        self.refresh_bundle_hash(self.wolf)
        result = self.validator.validate_project_index(self.index, self.root)
        self.assertTrue(any("cross-model identity" in error for error in result["errors"]))

    def test_rejects_cross_asset_animation_event_particle_and_output_collisions(self):
        wolf_folder = self.root / "assets/three_headed_wolf"
        replacements = {
            "animation-system.json": ("animation_id", "animation.crystal_tower.attack"),
            "audio-manifest.json": ("event_id", "mymod:crystal_tower.fire"),
            "particle-contracts.json": ("effect_id", "crystal_tower_muzzle"),
        }
        for name, (field, value) in replacements.items():
            path = wolf_folder / name
            payload = json.loads(path.read_text(encoding="utf-8"))
            target = payload["clips"][0] if name.startswith("animation") else payload["mappings"][0] if name.startswith("audio") else payload["contracts"][0]
            target[field] = value
            if name == "audio-manifest.json":
                target["output_file"] = "sounds/crystal_tower/fire.ogg"
            path.write_text(json.dumps(payload), encoding="utf-8")
        bundle_path = wolf_folder / "asset-bundle.json"
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        for resource in bundle["resources"]:
            resource["sha256"] = sha(wolf_folder / resource["path"])
        bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
        self.refresh_bundle_hash(self.wolf)
        result = self.validator.validate_project_index(self.index, self.root)
        for phrase in ("animation_id collision", "event_id collision", "effect_id collision", "output_file collision"):
            self.assertTrue(any(phrase in error for error in result["errors"]), phrase)

    def test_allows_only_mutually_approved_same_shared_audio_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = create_asset(root, "crystal_tower", shared_event="mymod:shared.metal_hit")
            second = create_asset(root, "three_headed_wolf", shared_event="mymod:shared.metal_hit")
            index = {"schema_version": 1, "project_id": "energy_defense", "assets": [first, second]}
            result = self.validator.validate_project_index(index, root)
            self.assertEqual(result["errors"], [])
            audio_path = root / "assets/three_headed_wolf/audio-manifest.json"
            audio = json.loads(audio_path.read_text(encoding="utf-8"))
            audio["mappings"][0]["shared_audio_approved"] = False
            audio_path.write_text(json.dumps(audio), encoding="utf-8")
            bundle_path = root / second["bundle_path"]
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            next(item for item in bundle["resources"] if item["path"] == "audio-manifest.json")["sha256"] = sha(audio_path)
            bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
            second["bundle_sha256"] = sha(bundle_path)
            result = self.validator.validate_project_index(index, root)
            self.assertTrue(any("event_id collision" in error for error in result["errors"]))

    def test_rejects_unique_identifiers_scoped_to_another_asset(self):
        wolf_folder = self.root / "assets/three_headed_wolf"
        values = {
            "animation-system.json": ("clips", "animation_id", "animation.crystal_tower.wolf_unique"),
            "audio-manifest.json": ("mappings", "event_id", "mymod:crystal_tower.wolf_unique"),
            "particle-contracts.json": ("contracts", "effect_id", "crystal_tower_wolf_unique"),
        }
        for name, (collection, field, value) in values.items():
            path = wolf_folder / name
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload[collection][0][field] = value
            if name == "audio-manifest.json":
                payload[collection][0]["output_file"] = "sounds/crystal_tower/wolf_unique.ogg"
            path.write_text(json.dumps(payload), encoding="utf-8")
        bundle_path = wolf_folder / "asset-bundle.json"
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        for resource in bundle["resources"]:
            resource["sha256"] = sha(wolf_folder / resource["path"])
        bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
        self.refresh_bundle_hash(self.wolf)
        result = self.validator.validate_project_index(self.index, self.root)
        for field in ("animation_id", "event_id", "effect_id", "output_file"):
            self.assertTrue(
                any(f"{field} is scoped to another asset" in error for error in result["errors"]),
                field,
            )


if __name__ == "__main__":
    unittest.main()
