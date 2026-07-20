import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SuiteLayoutTests(unittest.TestCase):
    def test_plugin_manifest_registers_bundled_skills(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "fjzm-suite")
        self.assertEqual(manifest["version"], "3.0.0")
        self.assertEqual(manifest["skills"], "./skills/")

    def test_main_and_animation_skills_ship_together(self):
        main = (ROOT / "skills" / "fjzm" / "SKILL.md").read_text(encoding="utf-8")
        animation = (ROOT / "skills" / "fjzm-animation" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: fjzm", main)
        self.assertIn("**REQUIRED SUB-SKILL:** Use fjzm-animation", main)
        self.assertIn("name: fjzm-animation", animation)
        self.assertTrue((ROOT / "skills" / "fjzm-animation" / "scripts" / "validate_animation_handoff.py").is_file())

    def test_install_script_names_both_atomic_targets(self):
        installer = (ROOT / "Install-FJZMSuite.ps1").read_text(encoding="utf-8")
        self.assertIn("fjzm", installer)
        self.assertIn("fjzm-animation", installer)
        self.assertIn("Refusing partial suite installation", installer)
        self.assertIn("SKILL.md", installer)


if __name__ == "__main__":
    unittest.main()
