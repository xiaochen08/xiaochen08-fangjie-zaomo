import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_bbmodel.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_bbmodel", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_model():
    root_uuid = "11111111-1111-4111-8111-111111111111"
    cube_uuid = "22222222-2222-4222-8222-222222222222"
    keyframe_uuid = "33333333-3333-4333-8333-333333333333"
    return {
        "meta": {"format_version": "5.0", "model_format": "free"},
        "name": "test_model",
        "resolution": {"width": 16, "height": 16},
        "elements": [
            {
                "name": "body",
                "uuid": cube_uuid,
                "type": "cube",
                "from": [-1, 0, -1],
                "to": [1, 2, 1],
                "origin": [0, 1, 0],
                "faces": {},
            }
        ],
        "groups": [
            {"name": "root", "uuid": root_uuid, "origin": [0, 0, 0]}
        ],
        "outliner": [
            {"uuid": root_uuid, "children": [cube_uuid], "isOpen": True}
        ],
        "textures": [],
        "animations": [
            {
                "name": "animation.test.idle",
                "length": 1.0,
                "loop": "loop",
                "animators": {
                    root_uuid: {
                        "name": "root",
                        "type": "bone",
                        "keyframes": [
                            {
                                "uuid": keyframe_uuid,
                                "channel": "rotation",
                                "time": 0.0,
                                "data_points": [{"x": 0, "y": 0, "z": 0}],
                            }
                        ],
                    }
                },
            }
        ],
    }


class ValidateBbmodelTests(unittest.TestCase):
    def test_valid_model_has_no_errors(self):
        validator = load_validator()
        self.assertEqual([], validator.validate_model(valid_model()))

    def test_reports_duplicate_uuid_and_dangling_outliner_reference(self):
        validator = load_validator()
        model = valid_model()
        model["groups"][0]["uuid"] = model["elements"][0]["uuid"]
        model["outliner"][0]["children"].append(
            "99999999-9999-4999-8999-999999999999"
        )

        issues = validator.validate_model(model)
        codes = {issue.code for issue in issues}

        self.assertIn("duplicate-uuid", codes)
        self.assertIn("dangling-outliner-reference", codes)

    def test_reports_unknown_animator_and_keyframe_beyond_length(self):
        validator = load_validator()
        model = valid_model()
        animation = model["animations"][0]
        animator = next(iter(animation["animators"].values()))
        animator["keyframes"][0]["time"] = 1.5
        animation["animators"] = {
            "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa": animator
        }

        issues = validator.validate_model(model)
        codes = {issue.code for issue in issues}

        self.assertIn("unknown-animator-target", codes)
        self.assertIn("keyframe-after-animation", codes)

    def test_enforces_required_animation_group_loop_and_origin(self):
        validator = load_validator()
        requirements = {
            "required_animations": [
                {"name": "animation.test.attack", "loop": "once", "min_length": 1.2}
            ],
            "required_groups": [
                {"name": "orbit", "origin": [0, 12, 0], "tolerance": 0.001}
            ],
        }

        issues = validator.validate_model(valid_model(), requirements)
        codes = {issue.code for issue in issues}

        self.assertIn("missing-required-animation", codes)
        self.assertIn("missing-required-group", codes)

    def test_reports_animation_loop_and_minimum_length_mismatch(self):
        validator = load_validator()
        requirements = {
            "required_animations": [
                {"name": "animation.test.idle", "loop": "once", "min_length": 2.0}
            ]
        }

        issues = validator.validate_model(valid_model(), requirements)
        codes = {issue.code for issue in issues}

        self.assertIn("animation-loop-mismatch", codes)
        self.assertIn("animation-too-short", codes)

    def test_reports_group_origin_mismatch(self):
        validator = load_validator()
        requirements = {
            "required_groups": [
                {"name": "root", "origin": [0, 12, 0], "tolerance": 0.001}
            ]
        }

        issues = validator.validate_model(valid_model(), requirements)

        self.assertIn("group-origin-mismatch", {issue.code for issue in issues})

    def test_cli_emits_json_and_nonzero_exit_on_failure(self):
        model = valid_model()
        model["resolution"]["width"] = 0

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.bbmodel"
            path.write_text(json.dumps(model), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

        report = json.loads(completed.stdout)
        self.assertEqual(1, completed.returncode)
        self.assertFalse(report["ok"])
        self.assertIn("invalid-resolution", {item["code"] for item in report["issues"]})


if __name__ == "__main__":
    unittest.main()
