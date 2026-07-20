import hashlib
import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_release_evidence.py"
CASES = [
    "actual_blockbench",
    "single_player",
    "dedicated_server_two_clients",
    "two_models_one_project",
    "interrupt_and_unload",
    "projectile_collision",
]


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_release_evidence.py is missing")
    spec = importlib.util.spec_from_file_location("validate_release_evidence", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReleaseEvidenceValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        identity = {
            "project_id": "energy_defense",
            "asset_id": "crystal_tower",
            "asset_version": "1.0.0",
            "rig_signature": "rig-crystal-tower-v1",
        }
        (self.root / "model-spec.json").write_text(
            json.dumps({
                "project_id": identity["project_id"],
                "asset_id": identity["asset_id"],
                "asset_version": identity["asset_version"],
                "animation_system": {"rig_signature": identity["rig_signature"]},
            }),
            encoding="utf-8",
        )
        bundle = {
            "schema_version": 1,
            **identity,
            "resources": [
                {"kind": "model-spec", "path": "model-spec.json", "sha256": sha(self.root / "model-spec.json")}
            ],
            "workflow_evidence": [{
                "step": "asset_identity_locked",
                "timestamp": "2026-07-17T14:00:00Z",
                "status": "verified",
                "input_hashes": [],
                "output_hashes": [sha(self.root / "model-spec.json")],
                "approval_evidence": "用户确认目标模型",
                "tool_version": "skill-v12-rc",
            }],
        }
        (self.root / "asset-bundle.json").write_text(json.dumps(bundle), encoding="utf-8")
        (self.root / "model.bbmodel").write_bytes(b"exact-bbmodel")
        (self.root / "runtime-project").mkdir()
        (self.root / "build").mkdir()
        (self.root / "build" / "mymod.jar").write_bytes(b"compiled-runtime")
        (self.root / "evidence").mkdir()
        (self.root / "evidence" / "blockbench.png").write_bytes(b"viewport")
        for case_id in CASES:
            (self.root / "evidence" / f"{case_id}.log").write_text("passed", encoding="utf-8")

        self.complete = {
            "schema_version": 1,
            **identity,
            "asset_bundle": {"path": "asset-bundle.json", "sha256": sha(self.root / "asset-bundle.json")},
            "support_tier": "verified",
            "qualification_status": "verified",
            "target": {
                "edition": "java",
                "minecraft_version": "1.21.1",
                "integration_type": "fabric",
                "integration_version": "0.16.10",
                "animation_runtime": "geckolib",
                "animation_runtime_version": "5.1.0",
                "project_path": "runtime-project",
                "project_commit": "0123456789abcdef",
                "build": {
                    "command": ["gradlew.bat", "build"],
                    "exit_code": 0,
                    "artifact_path": "build/mymod.jar",
                    "artifact_sha256": sha(self.root / "build" / "mymod.jar"),
                    "built_at": "2026-07-17T15:00:00Z",
                },
            },
            "blockbench_evidence": {
                "model_path": "model.bbmodel",
                "saved_sha256": sha(self.root / "model.bbmodel"),
                "reopened_sha256": sha(self.root / "model.bbmodel"),
                "validator_exit_code": 0,
                "animations_expected": ["idle", "attack"],
                "animations_played": ["idle", "attack"],
                "viewport_captures": [
                    {"path": "evidence/blockbench.png", "sha256": sha(self.root / "evidence" / "blockbench.png")}
                ],
            },
            "test_matrix": [
                {
                    "case_id": case_id,
                    "status": "passed",
                    "timestamp": "2026-07-17T15:10:00Z",
                    "tester": "tester-1",
                    "steps": ["execute the named case"],
                    "expected": "no cross-binding or lifecycle leak",
                    "actual": "passed as expected",
                    "evidence": [{"path": f"evidence/{case_id}.log", "sha256": sha(self.root / "evidence" / f"{case_id}.log")}],
                }
                for case_id in CASES
            ],
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_complete_verified_real_project_evidence(self):
        result = self.validator.validate_release_evidence(self.complete, self.root)
        self.assertEqual(result["errors"], [])

    def test_verified_requires_exact_project_versions_and_successful_build(self):
        manifest = deepcopy(self.complete)
        manifest["target"]["project_path"] = ""
        manifest["target"].pop("integration_version")
        manifest["target"]["build"]["exit_code"] = 1
        result = self.validator.validate_release_evidence(manifest, self.root)
        self.assertTrue(any("verified support requires an authorized project" in error for error in result["errors"]))
        self.assertTrue(any("integration_version" in error for error in result["errors"]))
        self.assertTrue(any("successful build" in error for error in result["errors"]))

    def test_verified_rejects_asset_bundle_that_fails_unified_validation(self):
        bundle = json.loads((self.root / "asset-bundle.json").read_text(encoding="utf-8"))
        bundle["resources"] = []
        (self.root / "asset-bundle.json").write_text(json.dumps(bundle), encoding="utf-8")
        manifest = deepcopy(self.complete)
        manifest["asset_bundle"]["sha256"] = sha(self.root / "asset-bundle.json")
        result = self.validator.validate_release_evidence(manifest, self.root)
        self.assertTrue(any("asset_bundle validation" in error for error in result["errors"]))

    def test_rejects_cross_model_bundle_and_nonidentical_reopened_bbmodel(self):
        bundle = json.loads((self.root / "asset-bundle.json").read_text(encoding="utf-8"))
        bundle["asset_id"] = "three_headed_wolf"
        (self.root / "asset-bundle.json").write_text(json.dumps(bundle), encoding="utf-8")
        manifest = deepcopy(self.complete)
        manifest["asset_bundle"]["sha256"] = sha(self.root / "asset-bundle.json")
        manifest["blockbench_evidence"]["reopened_sha256"] = "0" * 64
        result = self.validator.validate_release_evidence(manifest, self.root)
        self.assertTrue(any("cross-model bundle identity" in error for error in result["errors"]))
        self.assertTrue(any("reopened .bbmodel hash" in error for error in result["errors"]))

    def test_verified_rejects_incomplete_matrix_and_unverifiable_case_evidence(self):
        manifest = deepcopy(self.complete)
        manifest["test_matrix"].pop()
        manifest["test_matrix"][0]["evidence"][0].pop("sha256")
        result = self.validator.validate_release_evidence(manifest, self.root)
        self.assertTrue(any("missing required test case" in error for error in result["errors"]))
        self.assertTrue(any("evidence sha256" in error for error in result["errors"]))

    def test_compatible_may_remain_incomplete_but_cannot_claim_verified(self):
        manifest = deepcopy(self.complete)
        manifest["support_tier"] = "compatible"
        manifest["qualification_status"] = "unverified"
        manifest["target"]["project_path"] = ""
        manifest["target"].pop("build")
        manifest["blockbench_evidence"] = {}
        manifest["test_matrix"] = []
        result = self.validator.validate_release_evidence(manifest, self.root)
        self.assertEqual(result["errors"], [])
        self.assertTrue(any("not verified" in warning for warning in result["warnings"]))

    def test_nonverified_tier_rejects_verified_qualification_status(self):
        manifest = deepcopy(self.complete)
        manifest["support_tier"] = "compatible"
        manifest["qualification_status"] = "verified"
        result = self.validator.validate_release_evidence(manifest, self.root)
        self.assertTrue(any("qualification_status cannot be verified" in error for error in result["errors"]))

    def test_every_support_tier_requires_target_platform_identity(self):
        manifest = deepcopy(self.complete)
        manifest["support_tier"] = "experimental"
        manifest["qualification_status"] = "unverified"
        manifest["target"].pop("edition")
        result = self.validator.validate_release_evidence(manifest, self.root)
        self.assertTrue(any("target.edition" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
