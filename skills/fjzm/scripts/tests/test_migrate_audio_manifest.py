import hashlib
import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "migrate_audio_manifest.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("migrate_audio_manifest.py is missing")
    spec = importlib.util.spec_from_file_location("migrate_audio_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AudioManifestMigrationTests(unittest.TestCase):
    def test_migrates_identity_without_mutating_source_or_fabricating_late_steps(self):
        migration = load_module()
        old = {
            "schema_version": 1,
            "audio_mapping_approval": {"status": "approved", "evidence": "用户确认"},
            "mappings": [{"event_id": "mymod:crystal_tower.fire", "source_file": "01.wav"}],
        }
        original = deepcopy(old)
        migrated = migration.migrate_manifest(
            old,
            project_id="energy_defense",
            asset_id="crystal_tower",
            asset_version="1.0.0",
            model_spec_path="model-spec.json",
            model_spec_sha256="a" * 64,
            rig_signature="rig-tower-v1",
        )
        self.assertEqual(old, original)
        self.assertEqual(migrated["asset_id"], "crystal_tower")
        self.assertEqual(migrated["mappings"][0]["asset_id"], "crystal_tower")
        self.assertIn("mapping_approved", migrated["workflow"]["completed_steps"])
        self.assertNotIn("events_registered", migrated["workflow"]["completed_steps"])
        self.assertEqual(migrated["migration"]["status"], "review_required")

    def test_versioned_write_never_overwrites_existing_manifest(self):
        migration = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "audio-manifest-v11.json").write_text("{}", encoding="utf-8")
            destination = migration.write_versioned_json({"schema_version": 1}, folder, "audio-manifest-v11")
            self.assertEqual(destination.name, "audio-manifest-v11_v2.json")
            self.assertEqual(json.loads(destination.read_text(encoding="utf-8"))["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
