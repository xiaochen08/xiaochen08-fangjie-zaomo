import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SuiteLayoutTests(unittest.TestCase):
    def test_plugin_manifest_registers_bundled_skills(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "fjzm-suite")
        self.assertEqual(manifest["version"], "5.2.0")
        self.assertEqual(manifest["skills"], "./skills/")

    def test_main_and_three_specialist_skills_ship_together(self):
        main = (ROOT / "skills" / "fjzm" / "SKILL.md").read_text(encoding="utf-8")
        model = (ROOT / "skills" / "fjzm-model" / "SKILL.md").read_text(encoding="utf-8")
        texture = (ROOT / "skills" / "fjzm-texture" / "SKILL.md").read_text(encoding="utf-8")
        animation = (ROOT / "skills" / "fjzm-animation" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: fjzm", main)
        self.assertIn("**REQUIRED SUB-SKILL:** Use fjzm-model", main)
        self.assertIn("**REQUIRED SUB-SKILL:** Use fjzm-texture", main)
        self.assertIn("**REQUIRED SUB-SKILL:** Use fjzm-animation", main)
        self.assertIn("name: fjzm-model", model)
        self.assertIn("name: fjzm-texture", texture)
        self.assertIn("name: fjzm-animation", animation)
        self.assertTrue((ROOT / "skills" / "fjzm-model" / "scripts" / "validate_model_handoff.py").is_file())
        self.assertTrue((ROOT / "skills" / "fjzm-texture" / "scripts" / "validate_texture_handoff.py").is_file())
        self.assertTrue((ROOT / "skills" / "fjzm-animation" / "scripts" / "validate_animation_handoff.py").is_file())

    def test_install_script_names_all_atomic_targets(self):
        installer = (ROOT / "Install-FJZMSuite.ps1").read_text(encoding="utf-8")
        self.assertIn("fjzm", installer)
        self.assertIn("fjzm-model", installer)
        self.assertIn("fjzm-texture", installer)
        self.assertIn("fjzm-animation", installer)
        self.assertIn("Refusing partial suite installation", installer)
        self.assertIn("SKILL.md", installer)

    def test_v520_offline_suite_and_four_workbuddy_packages_are_published(self):
        expected = (
            "fjzm-suite-v5.2.0.zip",
            "fjzm-workbuddy-v5.2.0.zip",
            "fjzm-model-workbuddy-v5.2.0.zip",
            "fjzm-texture-workbuddy-v5.2.0.zip",
            "fjzm-animation-workbuddy-v5.2.0.zip",
        )
        for filename in expected:
            with self.subTest(filename=filename):
                self.assertTrue((ROOT / "dist" / filename).is_file())


if __name__ == "__main__":
    unittest.main()
