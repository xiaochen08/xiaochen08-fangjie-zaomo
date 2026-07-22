import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_suite_compatibility.py"


class SuiteCompatibilityTests(unittest.TestCase):
    def manifest(self):
        return {
            "suite_name": "fjzm-suite",
            "suite_version": "5.2.0",
            "protocol_version": "1.0",
            "skills": [
                {"name": "fjzm", "version": "5.2.0", "capabilities": ["orchestration", "combat_runtime_integration"]},
                {"name": "fjzm-model", "version": "5.2.0", "capabilities": ["geometry"]},
                {"name": "fjzm-texture", "version": "5.2.0", "capabilities": ["texture"]},
                {"name": "fjzm-animation", "version": "5.2.0", "capabilities": ["animation", "blender_epicfight_backend", "combat_behavior_orchestration"]},
            ],
        }

    def run_validator(self, payload):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "capability-index.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-X", "utf8", str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

    def test_complete_v5_2_suite_passes(self):
        result = self.run_validator(self.manifest())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_model_workshop_is_rejected(self):
        payload = self.manifest()
        payload["skills"] = [s for s in payload["skills"] if s["name"] != "fjzm-model"]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fjzm-model", result.stdout + result.stderr)

    def test_protocol_mismatch_is_rejected(self):
        payload = self.manifest()
        payload["protocol_version"] = "2.0"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("protocol", (result.stdout + result.stderr).lower())

    def test_skill_version_mismatch_is_rejected(self):
        payload = self.manifest()
        payload["skills"][2]["version"] = "4.2.1"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("version", (result.stdout + result.stderr).lower())

    def test_animation_backend_capability_is_required(self):
        payload = self.manifest()
        payload["skills"][3]["capabilities"] = ["animation"]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("blender_epicfight_backend", result.stdout + result.stderr)

    def test_combat_orchestration_capabilities_are_required(self):
        payload = self.manifest()
        payload["skills"][0]["capabilities"] = ["orchestration"]
        payload["skills"][3]["capabilities"] = ["animation", "blender_epicfight_backend"]
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        self.assertIn("combat_runtime_integration", output)
        self.assertIn("combat_behavior_orchestration", output)


if __name__ == "__main__":
    unittest.main()
