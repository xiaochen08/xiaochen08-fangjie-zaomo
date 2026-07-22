import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_model_handoff.py"


class ModelHandoffValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.reference = self.workspace / "approved-concept.png"
        self.blueprint = self.workspace / "geometry-blueprint.json"
        self.reference.write_bytes(b"reference")
        self.blueprint.write_text('{"units":"blockbench"}', encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def payload(self):
        return {
            "protocol_version": "1.0",
            "message_type": "handoff",
            "message_id": "msg-model-001",
            "correlation_id": "corr-model-001",
            "from_skill": "fjzm",
            "to_skill": "fjzm-model",
            "stage": "geometry",
            "idempotency_key": "demo:cat:v1:geometry:0",
            "identity": {"project_id": "demo", "asset_id": "cat", "asset_version": "v1"},
            "attempt": 0,
            "writer_lock": {"owner": "fjzm-model", "surface": "geometry", "output_version": "v1-model-a0"},
            "dependencies": [{"stage": "concept_approval", "status": "passed"}],
            "approved_design": {"approval_id": "approval-1", "approval_sha256": "a" * 64},
            "reference_artifacts": [{"path": self.reference.name, "sha256": self.digest(self.reference)}],
            "geometry_blueprint": {"path": self.blueprint.name, "sha256": self.digest(self.blueprint)},
            "authorized_surfaces": ["geometry", "base_rig_interface", "placeholder_uv"],
            "output_path": "outputs/cat-v1-model-a0.bbmodel",
            "fidelity_thresholds": {
                "blocking_anchor_pass_percent": 100,
                "main_proportion_error_percent_max": 5,
                "key_part_position_error_bbu_max": 0.5,
                "symmetric_part_error_bbu_max": 0.25,
                "rotation_error_degrees_max": 3,
            },
        }

    def run_validator(self, payload):
        path = self.workspace / "model-handoff.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), str(path), "--workspace", str(self.workspace)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_valid_model_handoff_passes(self):
        result = self.run_validator(self.payload())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_noncentral_source_is_rejected(self):
        payload = self.payload()
        payload["from_skill"] = "fjzm-texture"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fjzm", result.stdout + result.stderr)

    def test_reference_hash_mismatch_is_rejected(self):
        payload = self.payload()
        payload["reference_artifacts"][0]["sha256"] = "0" * 64
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sha256", (result.stdout + result.stderr).lower())

    def test_wrong_writer_surface_is_rejected(self):
        payload = self.payload()
        payload["writer_lock"]["surface"] = "texture"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("geometry", (result.stdout + result.stderr).lower())

    def test_unapproved_surface_is_rejected(self):
        payload = self.payload()
        payload["authorized_surfaces"].append("final_texture")
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("surface", (result.stdout + result.stderr).lower())


if __name__ == "__main__":
    unittest.main()
