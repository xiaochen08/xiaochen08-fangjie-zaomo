import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scaffold_runtime_delivery.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("scaffold_runtime_delivery.py is missing")
    spec = importlib.util.spec_from_file_location("scaffold_runtime_delivery", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeDeliveryScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.scaffold = load_module()
        self.bundle = {
            "project_id": "energy_defense",
            "asset_id": "crystal_tower",
            "asset_version": "1.0.0",
            "rig_signature": "rig-crystal-tower-v1",
        }

    def test_missing_project_creates_experimental_unverified_scaffold(self):
        result = self.scaffold.build_scaffold(
            self.bundle,
            {"edition": "java", "minecraft_version": "1.21.1", "integration_type": "fabric"},
            bundle_path="asset-bundle.json",
            bundle_sha256="a" * 64,
        )
        self.assertEqual(result["support_tier"], "experimental")
        self.assertEqual(result["qualification_status"], "unverified")
        self.assertTrue(all(case["status"] == "not_run" for case in result["test_matrix"]))
        self.assertEqual(result["blockbench_evidence"]["saved_sha256"], "")

    def test_complete_target_is_only_compatible_until_evidence_is_added(self):
        target = {
            "edition": "java",
            "minecraft_version": "1.21.1",
            "integration_type": "fabric",
            "integration_version": "0.16.10",
            "animation_runtime": "geckolib",
            "animation_runtime_version": "5.1.0",
            "project_path": "runtime-project",
            "project_commit": "0123456789abcdef",
        }
        result = self.scaffold.build_scaffold(
            self.bundle, target, bundle_path="asset-bundle.json", bundle_sha256="a" * 64
        )
        self.assertEqual(result["support_tier"], "compatible")
        self.assertNotEqual(result["support_tier"], "verified")
        self.assertEqual(result["runtime_artifacts"], [])

    def test_versioned_writer_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "runtime-delivery.json").write_text("{}", encoding="utf-8")
            destination = self.scaffold.write_versioned_json(
                {"qualification_status": "unverified"}, folder, "runtime-delivery"
            )
            self.assertEqual(destination.name, "runtime-delivery_v2.json")
            self.assertEqual(json.loads(destination.read_text(encoding="utf-8"))["qualification_status"], "unverified")


if __name__ == "__main__":
    unittest.main()
