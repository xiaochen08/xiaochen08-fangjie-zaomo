import importlib.util
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_mod_project_brief.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_mod_project_brief.py is missing")
    spec = importlib.util.spec_from_file_location("validate_mod_project_brief", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModProjectBriefValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.destination = Path(self.temp.name) / "crystal-tower-mod"
        self.complete = {
            "schema_version": 1,
            "project_status": "create",
            "route_choice": "create_mod_first",
            "route_choice_evidence": "用户选择先创建 Mod，再制作模型",
            "edition": "java",
            "target": {
                "minecraft_version": "1.21.1",
                "loader": "fabric",
                "loader_version": "0.16.10",
                "mappings": "official-compatible-mappings",
                "animation_runtime": "geckolib",
                "animation_runtime_version": "5.1.0",
                "java_version": "21",
                "gradle_version": "8.10",
            },
            "identity": {
                "namespace": "energy_defense",
                "mod_id": "energy_defense",
                "display_name": "Energy Defense",
            },
            "destination_path": str(self.destination.resolve()),
            "compatibility_evidence": [
                {
                    "source_type": "official_primary",
                    "url": "https://official.example/version-matrix",
                    "checked_at": "2026-07-17T18:00:00Z",
                }
            ],
            "creation_approval": {"status": "approved", "evidence": "用户确认在指定路径创建最小工程"},
            "toolchain": {
                "shell": "powershell7",
                "wrapper": "gradlew.bat",
                "global_install_allowed": False,
            },
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_complete_evidence_backed_new_java_mod_brief(self):
        result = self.validator.validate_brief(self.complete)
        self.assertEqual(result["errors"], [])

    def test_rejects_missing_versions_official_evidence_or_approval(self):
        brief = deepcopy(self.complete)
        brief["target"].pop("loader_version")
        brief["compatibility_evidence"][0]["source_type"] = "community_blog"
        brief["creation_approval"] = {"status": "pending", "evidence": ""}
        result = self.validator.validate_brief(brief)
        self.assertTrue(any("target.loader_version" in error for error in result["errors"]))
        self.assertTrue(any("official primary-source compatibility evidence" in error for error in result["errors"]))
        self.assertTrue(any("explicit project-creation approval" in error for error in result["errors"]))

    def test_rejects_missing_or_inconsistent_explicit_route_choice(self):
        brief = deepcopy(self.complete)
        brief.pop("route_choice")
        brief.pop("route_choice_evidence")
        result = self.validator.validate_brief(brief)
        self.assertTrue(any("explicit project route choice" in error for error in result["errors"]))

        brief = deepcopy(self.complete)
        brief["route_choice"] = "model_first"
        result = self.validator.validate_brief(brief)
        self.assertTrue(any("route_choice does not match project_status" in error for error in result["errors"]))

    def test_rejects_relative_or_existing_destination(self):
        brief = deepcopy(self.complete)
        brief["destination_path"] = "relative/project"
        result = self.validator.validate_brief(brief)
        self.assertTrue(any("absolute destination path" in error for error in result["errors"]))
        self.destination.mkdir()
        brief["destination_path"] = str(self.destination)
        result = self.validator.validate_brief(brief)
        self.assertTrue(any("destination already exists" in error for error in result["errors"]))

    def test_model_first_runtime_deferred_is_valid_but_never_created_or_verified(self):
        brief = {
            "schema_version": 1,
            "project_status": "runtime_deferred",
            "route_choice": "model_first",
            "route_choice_evidence": "用户确认先制作模型，稍后再创建或接入 Mod",
            "edition": "java",
            "deferred_reason": "用户确认先制作模型",
            "restrictions": ["no runtime integration claim", "runtime fields remain provisional"],
            "runtime_contract_path": "runtime-contract.json",
            "runtime_contract_status": "validated",
            "runtime_risk": "high",
            "production_ceiling": "runtime_neutral_source",
            "mod_first_recommendation": {
                "status": "declined",
                "evidence": "用户确认暂不创建 Mod",
            },
            "risk_acceptance": {
                "status": "approved",
                "evidence": "用户接受运行时导出延期且后续可能需要适配",
            },
        }
        result = self.validator.validate_brief(brief)
        self.assertEqual(result["errors"], [])
        brief["qualification_status"] = "verified"
        result = self.validator.validate_brief(brief)
        self.assertTrue(any("runtime_deferred cannot be verified" in error for error in result["errors"]))

    def test_high_risk_model_first_rejects_missing_runtime_contract_or_risk_evidence(self):
        brief = {
            "schema_version": 1,
            "project_status": "runtime_deferred",
            "route_choice": "model_first",
            "route_choice_evidence": "用户要求先制作复杂炮塔模型",
            "edition": "java",
            "deferred_reason": "尚未创建 Mod",
            "restrictions": ["no runtime integration claim"],
            "runtime_risk": "high",
            "production_ceiling": "runtime_neutral_source",
        }
        result = self.validator.validate_brief(brief)
        self.assertTrue(any("validated runtime-contract.json" in error for error in result["errors"]))
        self.assertTrue(any("declining create_mod_first" in error for error in result["errors"]))
        self.assertTrue(any("risk acceptance" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
