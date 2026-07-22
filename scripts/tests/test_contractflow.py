import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_contractflow.py"


class ContractFlowValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.source = self.workspace / "approved-reference.png"
        self.source.write_bytes(b"approved reference")
        self.sha256 = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def tearDown(self):
        self.temp.cleanup()

    def message(self):
        return {
            "protocol_version": "1.0",
            "message_type": "handoff",
            "message_id": "msg-model-001",
            "correlation_id": "corr-asset-001",
            "from_skill": "fjzm",
            "to_skill": "fjzm-model",
            "stage": "geometry",
            "idempotency_key": "demo:tower:v1:geometry:0",
            "identity": {
                "project_id": "demo",
                "asset_id": "tower",
                "asset_version": "v1",
            },
            "attempt": 0,
            "writer_lock": {
                "owner": "fjzm-model",
                "surface": "geometry",
                "output_version": "v1-model-a0",
            },
            "dependencies": [
                {"stage": "concept_approval", "status": "passed"}
            ],
            "artifacts": [
                {"path": self.source.name, "sha256": self.sha256}
            ],
            "retry": {"retryable": True, "reason_code": "technical_io"},
        }

    def run_validator(self, payload):
        contract = self.workspace / "contractflow.json"
        contract.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(SCRIPT),
                str(contract),
                "--workspace",
                str(self.workspace),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_valid_central_handoff_passes(self):
        result = self.run_validator(self.message())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_peer_to_peer_specialist_message_is_rejected(self):
        payload = self.message()
        payload["from_skill"] = "fjzm-texture"
        payload["to_skill"] = "fjzm-animation"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("central", (result.stdout + result.stderr).lower())

    def test_artifact_hash_mismatch_is_rejected(self):
        payload = self.message()
        payload["artifacts"][0]["sha256"] = "0" * 64
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sha256", (result.stdout + result.stderr).lower())

    def test_attempt_above_two_is_rejected(self):
        payload = self.message()
        payload["attempt"] = 3
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("attempt", (result.stdout + result.stderr).lower())

    def test_hard_block_cannot_be_marked_retryable(self):
        payload = self.message()
        payload["retry"] = {
            "retryable": True,
            "reason_code": "identity_mismatch",
        }
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hard-stop", (result.stdout + result.stderr).lower())

    def test_failed_dependency_blocks_handoff(self):
        payload = self.message()
        payload["dependencies"][0]["status"] = "failed"
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dependency", (result.stdout + result.stderr).lower())


if __name__ == "__main__":
    unittest.main()
