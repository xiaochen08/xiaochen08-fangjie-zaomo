import importlib.util
import hashlib
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_audio_manifest.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_audio_manifest.py is missing")
    spec = importlib.util.spec_from_file_location("validate_audio_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_manifest(source_sha256="a" * 64, model_spec_sha256="b" * 64):
    return {
        "schema_version": 1,
        "project_id": "energy_defense",
        "asset_id": "crystal_tower",
        "asset_version": "1.0.0",
        "model_binding": {
            "model_spec_path": "model-spec.json",
            "model_spec_sha256": model_spec_sha256,
            "rig_signature": "rig-crystal-tower-v1",
        },
        "workflow": {
            "completed_steps": [
                "asset_identity_locked",
                "attachments_inventoried",
                "sources_inspected",
                "mapping_proposed",
                "mapping_approved",
                "copies_converted",
                "events_registered",
                "animation_bound",
            ]
        },
        "target": {
            "edition": "java",
            "loader": "fabric",
            "minecraft_version": "1.21.1",
            "animation_runtime": "geckolib5",
        },
        "model_approval_id": "concept-B",
        "audio_mapping_approval": {"status": "approved", "evidence": "用户确认映射"},
        "budgets": {
            "max_simultaneous_instances": 4,
            "attenuation_distance": 32,
            "streaming_policy": "memory",
        },
        "mappings": [
            {
                "asset_id": "crystal_tower",
                "source_file": "炮塔启动.wav",
                "source_sha256": source_sha256,
                "user_label_zh": "炮塔启动",
                "event_id": "mymod:crystal_tower.activate",
                "output_file": "sounds/crystal_tower/activate.ogg",
                "role": "one_shot",
                "owner": "animation_keyframe",
                "animation_id": "animation.crystal_tower.startup",
                "time_seconds": 0.0,
                "locator": "tower_core",
                "approved": True,
                "critical_cue": True,
                "subtitle_key": "subtitles.mymod.crystal_tower.activate",
                "visual_telegraph": "core lights cyan",
                "origin": "ai_generated",
                "provenance": {
                    "provider": "example",
                    "generation_model": "example-sfx-v1",
                    "prompt": "mechanical crystal tower startup",
                    "generated_at": "2026-07-17",
                    "license_status": "commercial_use_verified",
                    "attribution": "none",
                },
            }
        ],
    }


class AudioManifestValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        (self.base / "sounds" / "crystal_tower").mkdir(parents=True)
        source = self.base / "炮塔启动.wav"
        source.write_bytes(b"source")
        model_spec = self.base / "model-spec.json"
        model_spec.write_text(
            '{"project_id":"energy_defense","asset_id":"crystal_tower","asset_version":"1.0.0","animation_system":{"rig_signature":"rig-crystal-tower-v1"}}',
            encoding="utf-8",
        )
        (self.base / "sounds" / "crystal_tower" / "activate.ogg").write_bytes(b"output")
        self.model_spec_data = {
            "project_id": "energy_defense",
            "asset_id": "crystal_tower",
            "asset_version": "1.0.0",
            "animation_system": {"rig_signature": "rig-crystal-tower-v1"},
        }
        self.complete = valid_manifest(
            hashlib.sha256(source.read_bytes()).hexdigest(),
            hashlib.sha256(model_spec.read_bytes()).hexdigest(),
        )

    def tearDown(self):
        self.temp.cleanup()

    def validate(self, manifest, sounds=None, events=None, model_spec=None):
        if model_spec is None:
            return self.validator.validate_manifest(manifest, self.base, sounds, events)
        try:
            return self.validator.validate_manifest(manifest, self.base, sounds, events, model_spec)
        except TypeError as exc:
            raise AssertionError("validator does not support model-spec identity checking") from exc

    def test_accepts_complete_manifest_with_registered_event(self):
        result = self.validate(
            deepcopy(self.complete),
            {"crystal_tower.activate": {"sounds": ["mymod:crystal_tower/activate"]}},
            [{"sound_event": "mymod:crystal_tower.activate"}],
        )
        self.assertEqual(result["errors"], [])

    def test_rejects_invalid_english_event_identifier(self):
        manifest = deepcopy(self.complete)
        manifest["mappings"][0]["event_id"] = "我的模组:炮塔启动"
        result = self.validate(manifest)
        self.assertTrue(any("event_id" in error for error in result["errors"]))

    def test_rejects_unassigned_number_only_source(self):
        manifest = deepcopy(self.complete)
        manifest["mappings"][0]["source_file"] = "01.wav"
        manifest["mappings"][0]["user_label_zh"] = ""
        (self.base / "01.wav").write_bytes(b"source")
        result = self.validate(manifest)
        self.assertTrue(any("numbered source" in error for error in result["errors"]))

    def test_loop_requires_stop_and_interruption_rules(self):
        manifest = deepcopy(self.complete)
        mapping = manifest["mappings"][0]
        mapping["role"] = "loop"
        mapping["owner"] = "state_lifecycle"
        result = self.validate(manifest)
        self.assertTrue(any("stop_event" in error for error in result["errors"]))
        self.assertTrue(any("interruption_rule" in error for error in result["errors"]))

    def test_projectile_impact_must_be_owned_by_collision(self):
        manifest = deepcopy(self.complete)
        manifest["mappings"][0]["event_id"] = "mymod:crystal_tower.projectile_impact"
        result = self.validate(manifest)
        self.assertTrue(any("projectile_collision" in error for error in result["errors"]))

    def test_critical_cue_requires_subtitle_and_visual_telegraph(self):
        manifest = deepcopy(self.complete)
        mapping = manifest["mappings"][0]
        mapping.pop("subtitle_key")
        mapping.pop("visual_telegraph")
        result = self.validate(manifest)
        self.assertTrue(any("subtitle_key" in error for error in result["errors"]))
        self.assertTrue(any("visual_telegraph" in error for error in result["errors"]))

    def test_ai_audio_requires_complete_provenance(self):
        manifest = deepcopy(self.complete)
        manifest["mappings"][0].pop("provenance")
        result = self.validate(manifest)
        self.assertTrue(any("provenance" in error for error in result["errors"]))

    def test_cross_checks_sound_registry_and_animation_event_table(self):
        result = self.validate(deepcopy(self.complete), {}, [])
        self.assertTrue(any("sounds registry" in error for error in result["errors"]))
        self.assertTrue(any("event table" in error for error in result["errors"]))

    def test_rejects_missing_approved_source_or_output(self):
        manifest = deepcopy(self.complete)
        manifest["mappings"][0]["source_file"] = "missing.wav"
        manifest["mappings"][0]["output_file"] = "sounds/missing.ogg"
        result = self.validate(manifest)
        self.assertGreaterEqual(sum("missing" in error for error in result["errors"]), 2)

    def test_rejects_mapping_bound_to_another_asset(self):
        manifest = deepcopy(self.complete)
        manifest["mappings"][0]["asset_id"] = "three_headed_wolf"
        result = self.validate(manifest)
        self.assertTrue(any("cross-model binding" in error for error in result["errors"]))

    def test_rejects_event_identifier_scoped_to_another_asset(self):
        manifest = deepcopy(self.complete)
        manifest["mappings"][0]["event_id"] = "mymod:three_headed_wolf.activate"
        result = self.validate(manifest)
        self.assertTrue(any("event_id must be scoped" in error for error in result["errors"]))

    def test_rejects_output_directory_for_another_asset(self):
        manifest = deepcopy(self.complete)
        manifest["mappings"][0]["output_file"] = "sounds/three_headed_wolf/activate.ogg"
        (self.base / "sounds" / "three_headed_wolf").mkdir()
        (self.base / "sounds" / "three_headed_wolf" / "activate.ogg").write_bytes(b"wrong")
        result = self.validate(manifest)
        self.assertTrue(any("output_file must be scoped" in error for error in result["errors"]))

    def test_rejects_out_of_order_workflow_steps(self):
        manifest = deepcopy(self.complete)
        steps = manifest["workflow"]["completed_steps"]
        steps[2], steps[4] = steps[4], steps[2]
        result = self.validate(manifest)
        self.assertTrue(any("workflow steps are out of order" in error for error in result["errors"]))

    def test_cross_checks_model_spec_identity_hash_and_rig(self):
        manifest = deepcopy(self.complete)
        wrong_spec = deepcopy(self.model_spec_data)
        wrong_spec["asset_id"] = "three_headed_wolf"
        result = self.validate(manifest, model_spec=wrong_spec)
        self.assertTrue(any("model-spec asset_id mismatch" in error for error in result["errors"]))

        manifest["model_binding"]["model_spec_sha256"] = "c" * 64
        result = self.validate(manifest, model_spec=self.model_spec_data)
        self.assertTrue(any("model_spec_sha256" in error for error in result["errors"]))

        manifest = deepcopy(self.complete)
        manifest["model_binding"]["rig_signature"] = "rig-other-model"
        result = self.validate(manifest, model_spec=self.model_spec_data)
        self.assertTrue(any("rig_signature mismatch" in error for error in result["errors"]))

    def test_variant_group_requires_one_event_and_level_match(self):
        manifest = deepcopy(self.complete)
        first = manifest["mappings"][0]
        first["variant_group"] = "fire_variants"
        first["qa"] = {"rms_dbfs": -15.0}
        second = deepcopy(first)
        second["source_file"] = "炮塔启动2.wav"
        second["source_sha256"] = hashlib.sha256(b"source2").hexdigest()
        second["output_file"] = "sounds/crystal_tower/activate2.ogg"
        second["event_id"] = "mymod:crystal_tower.wrong_event"
        second["qa"] = {"rms_dbfs": -21.0}
        (self.base / second["source_file"]).write_bytes(b"source2")
        (self.base / second["output_file"]).write_bytes(b"output2")
        manifest["mappings"].append(second)
        result = self.validate(manifest)
        self.assertTrue(any("variant_group must share one event_id" in error for error in result["errors"]))
        self.assertTrue(any("variant_group level spread exceeds 3 dB" in error for error in result["errors"]))

    def test_critical_cue_cross_checks_localizations_and_visual_event(self):
        manifest = deepcopy(self.complete)
        try:
            result = self.validator.validate_manifest(
                manifest,
                self.base,
                None,
                [{"sound_event": "mymod:crystal_tower.activate"}],
                self.model_spec_data,
                {"zh_cn": {}, "en_us": {}},
                [],
                None,
            )
        except TypeError as exc:
            raise AssertionError("validator lacks localization/visual cross-checks") from exc
        self.assertTrue(any("subtitle key missing" in error for error in result["errors"]))
        self.assertTrue(any("visual telegraph event missing" in error for error in result["errors"]))

    def test_shared_library_requires_authorized_consumer_and_event(self):
        manifest = deepcopy(self.complete)
        mapping = manifest["mappings"][0]
        mapping["shared_audio_library"] = "mechanical_common"
        mapping["shared_audio_approved"] = True
        mapping["output_file"] = "sounds/shared/mechanical_common/activate.ogg"
        shared_output = self.base / mapping["output_file"]
        shared_output.parent.mkdir(parents=True)
        shared_output.write_bytes(b"shared")
        try:
            result = self.validator.validate_manifest(
                manifest, self.base, None, None, self.model_spec_data, None, None,
                {"library_id": "mechanical_common", "version": "1.0.0", "consumers": [], "events": []},
            )
        except TypeError as exc:
            raise AssertionError("validator lacks shared library cross-checks") from exc
        self.assertTrue(any("asset is not an authorized shared-library consumer" in error for error in result["errors"]))
        self.assertTrue(any("event is absent from shared library" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
