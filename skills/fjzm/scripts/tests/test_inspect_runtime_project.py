import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "inspect_runtime_project.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("inspect_runtime_project.py is missing")
    spec = importlib.util.spec_from_file_location("inspect_runtime_project", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeProjectInspectorTests(unittest.TestCase):
    def setUp(self):
        self.inspector = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def make_fabric(self, mod_minecraft="~1.21.1"):
        (self.root / "src/main/resources").mkdir(parents=True)
        (self.root / "gradle.properties").write_text(
            "minecraft_version=1.21.1\nloader_version=0.16.10\n", encoding="utf-8"
        )
        (self.root / "src/main/resources/fabric.mod.json").write_text(
            json.dumps({"schemaVersion": 1, "depends": {"fabricloader": ">=0.16.10", "minecraft": mod_minecraft}}),
            encoding="utf-8",
        )
        (self.root / "build.gradle").write_text(
            'dependencies { implementation "software.bernie.geckolib:geckolib-fabric-1.21.1:5.1.0" }\n',
            encoding="utf-8",
        )

    def test_detects_fabric_exact_versions_with_hashed_read_only_evidence(self):
        self.make_fabric()
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        result = self.inspector.inspect_project(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["profile"]["edition"], "java")
        self.assertEqual(result["profile"]["integration_type"], "fabric")
        self.assertEqual(result["profile"]["minecraft_version"], "1.21.1")
        self.assertEqual(result["profile"]["integration_version"], "0.16.10")
        self.assertEqual(result["profile"]["animation_runtime_version"], "5.1.0")
        self.assertTrue(all(len(item["sha256"]) == 64 for item in result["evidence"]))
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_detects_bedrock_resource_and_behavior_pack_pair(self):
        for folder, module_type in (("resource_pack", "resources"), ("behavior_pack", "data")):
            path = self.root / folder
            path.mkdir()
            (path / "manifest.json").write_text(
                json.dumps({
                    "format_version": 2,
                    "header": {"name": folder, "uuid": f"uuid-{folder}", "version": [1, 0, 0], "min_engine_version": [1, 21, 0]},
                    "modules": [{"type": module_type, "uuid": f"module-{folder}", "version": [1, 0, 0]}],
                }),
                encoding="utf-8",
            )
        result = self.inspector.inspect_project(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["profile"]["edition"], "bedrock")
        self.assertEqual(result["profile"]["integration_type"], "bedrock_packs")
        self.assertEqual(result["profile"]["minecraft_version"], "1.21.0")

    def test_detects_mcreator_generator_without_treating_it_as_plain_forge(self):
        (self.root / "tower.mcreator").write_text(
            json.dumps({"generator": "forge-1.20.1", "generator_version": "2024.4", "geckolib_version": "4.7"}),
            encoding="utf-8",
        )
        result = self.inspector.inspect_project(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["profile"]["integration_type"], "mcreator")
        self.assertEqual(result["profile"]["minecraft_version"], "1.20.1")
        self.assertEqual(result["profile"]["integration_version"], "2024.4")

    def test_rejects_conflicting_version_evidence(self):
        self.make_fabric(mod_minecraft="~1.20.1")
        result = self.inspector.inspect_project(self.root)
        self.assertTrue(any("conflicting minecraft_version evidence" in error for error in result["errors"]))

    def test_rejects_multiple_platform_markers_or_unknown_project(self):
        self.make_fabric()
        (self.root / "resource_pack").mkdir()
        (self.root / "resource_pack/manifest.json").write_text(
            json.dumps({"format_version": 2, "header": {"min_engine_version": [1, 21, 0]}, "modules": [{"type": "resources"}]}),
            encoding="utf-8",
        )
        result = self.inspector.inspect_project(self.root)
        self.assertTrue(any("multiple runtime project types detected" in error for error in result["errors"]))
        with tempfile.TemporaryDirectory() as empty:
            result = self.inspector.inspect_project(Path(empty))
            self.assertTrue(any("no supported runtime project markers" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
