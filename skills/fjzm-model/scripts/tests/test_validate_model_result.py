import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_model_result.py"
VIEWS = ["front", "back", "left", "right", "top", "bottom", "three-quarter", "gameplay-distance"]


class ModelResultValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.model = self.workspace / "cat-v1-model-a0.bbmodel"
        self.reference = self.workspace / "approved-concept.png"
        self.summary = self.workspace / "summary-board.png"
        self.overlay = self.workspace / "overlay-50.png"
        self.model.write_text('{"meta":{"format_version":"4.10"}}', encoding="utf-8")
        self.reference.write_bytes(b"reference")
        self.summary.write_bytes(b"summary")
        self.overlay.write_bytes(b"overlay")
        self.view_files = {}
        for view in VIEWS:
            path = self.workspace / f"view-{view}.png"
            path.write_bytes(view.encode("utf-8"))
            self.view_files[view] = path
        self.report_path = self.workspace / "reference-fidelity-report.json"

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def report(self):
        return {
            "schema_version": "1.0",
            "model_sha256": self.digest(self.model),
            "reference_sha256": self.digest(self.reference),
            "summary_board": {"path": self.summary.name, "sha256": self.digest(self.summary)},
            "overlay": {"path": self.overlay.name, "sha256": self.digest(self.overlay), "opacity_percent": 50},
            "views": [
                {"name": name, "path": path.name, "sha256": self.digest(path), "camera": "orthographic" if name not in {"three-quarter", "gameplay-distance"} else "perspective"}
                for name, path in self.view_files.items()
            ],
            "blocking_anchors": [{"id": "head-shape", "status": "passed"}, {"id": "backpack", "status": "passed"}],
            "unapproved_parts": [],
            "missing_approved_parts": [],
            "metrics": {
                "main_proportion_error_percent": 4.5,
                "key_part_position_error_bbu": 0.4,
                "symmetric_part_error_bbu": 0.2,
                "rotation_error_degrees": 2.5,
                "clearance_pass": True,
            },
            "unintended_intersections": 0,
            "floating_parts": 0,
            "wrong_groups": 0,
            "identity_mismatch": False,
            "status": "passed",
        }

    def result(self, report):
        self.report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        return {
            "protocol_version": "1.0",
            "message_type": "result",
            "message_id": "msg-model-result-001",
            "correlation_id": "corr-model-001",
            "from_skill": "fjzm-model",
            "to_skill": "fjzm",
            "stage": "geometry",
            "idempotency_key": "demo:cat:v1:geometry:0",
            "identity": {"project_id": "demo", "asset_id": "cat", "asset_version": "v1"},
            "attempt": 0,
            "output_model": {"path": self.model.name, "sha256": self.digest(self.model)},
            "fidelity_report": {"path": self.report_path.name, "sha256": self.digest(self.report_path)},
            "geometry_signature": "geo-" + "1" * 60,
            "rig_signature": "rig-" + "2" * 60,
            "changed_surfaces": ["geometry", "base_rig_interface", "placeholder_uv"],
            "status": "passed",
        }

    def run_validator(self, payload):
        path = self.workspace / "model-result.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), str(path), "--workspace", str(self.workspace)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_valid_model_result_passes(self):
        report = self.report()
        result = self.run_validator(self.result(report))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_required_view_is_rejected(self):
        report = self.report()
        report["views"] = [v for v in report["views"] if v["name"] != "bottom"]
        result = self.run_validator(self.result(report))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("bottom", (result.stdout + result.stderr).lower())

    def test_proportion_threshold_breach_is_rejected(self):
        report = self.report()
        report["metrics"]["main_proportion_error_percent"] = 5.1
        result = self.run_validator(self.result(report))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("proportion", (result.stdout + result.stderr).lower())

    def test_failed_blocking_anchor_is_rejected(self):
        report = self.report()
        report["blocking_anchors"][0]["status"] = "failed"
        result = self.run_validator(self.result(report))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("anchor", (result.stdout + result.stderr).lower())

    def test_texture_write_is_rejected(self):
        report = self.report()
        payload = self.result(report)
        payload["changed_surfaces"].append("final_texture")
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("surface", (result.stdout + result.stderr).lower())

    def test_attempt_above_two_is_rejected(self):
        report = self.report()
        payload = self.result(report)
        payload["attempt"] = 3
        result = self.run_validator(payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("attempt", (result.stdout + result.stderr).lower())


if __name__ == "__main__":
    unittest.main()
