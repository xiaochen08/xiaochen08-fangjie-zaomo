import unittest
from pathlib import Path


SKILL_MD = Path(__file__).resolve().parents[2] / "SKILL.md"
AGENT_CONFIG = Path(__file__).resolve().parents[2] / "agents" / "openai.yaml"
MODEL_BRIEF = Path(__file__).resolve().parents[2] / "references" / "model-brief.md"
USER_DIALOGUE = Path(__file__).resolve().parents[2] / "references" / "user-dialogue.md"
QUALITY_GATES = Path(__file__).resolve().parents[2] / "references" / "quality-gates.md"
CONCEPT_PROMPT = Path(__file__).resolve().parents[2] / "references" / "concept-prompt.md"
MODEL_CATEGORIES = Path(__file__).resolve().parents[2] / "references" / "model-categories.md"
PARTICLE_DESIGN = Path(__file__).resolve().parents[2] / "references" / "particle-design.md"
ANIMATION_SYSTEM = Path(__file__).resolve().parents[2] / "references" / "animation-system.md"
AUDIO_SYSTEM = Path(__file__).resolve().parents[2] / "references" / "audio-system.md"
AUDIO_RUNTIME_ADAPTERS = Path(__file__).resolve().parents[2] / "references" / "audio-runtime-adapters.md"
AUDIO_PIPELINE = Path(__file__).resolve().parents[1] / "audio_pipeline.py"
AUDIO_VALIDATOR = Path(__file__).resolve().parents[1] / "validate_audio_manifest.py"
ASSET_IDENTITY = Path(__file__).resolve().parents[2] / "references" / "asset-identity.md"
ASSET_BUNDLE = Path(__file__).resolve().parents[2] / "references" / "asset-bundle.md"
RELEASE_QUALIFICATION = Path(__file__).resolve().parents[2] / "references" / "release-qualification.md"
RUNTIME_DELIVERY = Path(__file__).resolve().parents[2] / "references" / "runtime-delivery.md"
PROJECT_INTEGRATION = Path(__file__).resolve().parents[2] / "references" / "project-integration.md"
MOD_PROJECT_BOOTSTRAP = Path(__file__).resolve().parents[2] / "references" / "mod-project-bootstrap.md"
ASSET_ECOSYSTEM = Path(__file__).resolve().parents[2] / "references" / "asset-ecosystem.md"
ASSET_WORKSPACE = Path(__file__).resolve().parents[2] / "references" / "asset-workspace.md"
MODEL_FIRST_RUNTIME_GATE = Path(__file__).resolve().parents[2] / "references" / "model-first-runtime-gate.md"
RUNTIME_CONTRACT_VALIDATOR = Path(__file__).resolve().parents[1] / "validate_runtime_contract.py"
SHADER_COMPATIBILITY = Path(__file__).resolve().parents[2] / "references" / "shader-compatibility.md"
SHADER_CONTRACT_VALIDATOR = Path(__file__).resolve().parents[1] / "validate_shader_contract.py"
WINDOWS_UTF8_PREFLIGHT = Path(__file__).resolve().parents[2] / "references" / "windows-utf8-preflight.md"
GUI_DESIGN = Path(__file__).resolve().parents[2] / "references" / "gui-design.md"
UTF8_PREFLIGHT_VALIDATOR = Path(__file__).resolve().parents[1] / "validate_encoding_preflight.py"
IMAGE_PRODUCTION = Path(__file__).resolve().parents[2] / "references" / "image-production-system.md"
ASSET_PRESENTATION = Path(__file__).resolve().parents[2] / "references" / "asset-presentation.md"
ASSET_PRESENTATION_VALIDATOR = Path(__file__).resolve().parents[1] / "validate_asset_presentation.py"
COMBAT_RUNTIME_INTEGRATION = Path(__file__).resolve().parents[2] / "references" / "combat-runtime-integration.md"


class OfficialIdentityPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.agent = AGENT_CONFIG.read_text(encoding="utf-8")

    def test_machine_call_name_is_fjzm(self):
        self.assertIn("name: fjzm", self.skill)
        self.assertNotIn("name: create-blockbench-minecraft-models", self.skill)

    def test_official_chinese_display_name_is_fangjie_zaomo(self):
        self.assertIn("# 方界造模（FJZM）", self.skill)
        self.assertIn('display_name: "方界造模 FJZM"', self.agent)

    def test_default_prompt_uses_new_call_name(self):
        self.assertIn("$fjzm", self.agent)
        self.assertNotIn("$create-blockbench-minecraft-models", self.agent)

    def test_default_prompt_reflects_version_first_and_utf8_red_gate(self):
        self.assertIn("先问 Minecraft 版本", self.agent)
        self.assertIn("UTF-8 红色门禁", self.agent)
        self.assertIn("GUI", self.agent)


class AnimationSubskillBindingPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.animation = ANIMATION_SYSTEM.read_text(encoding="utf-8")
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.combat_runtime = COMBAT_RUNTIME_INTEGRATION.read_text(encoding="utf-8") if COMBAT_RUNTIME_INTEGRATION.exists() else ""

    def test_animation_requests_require_the_specialist_subskill(self):
        phrase = "**REQUIRED SUB-SKILL:** Use fjzm-animation"
        self.assertIn(phrase, self.skill)
        self.assertLess(self.skill.index(phrase), self.skill.index("Read [concept-prompt.md]"))

    def test_missing_animation_subskill_blocks_animation_production(self):
        self.assertIn("If `fjzm-animation` is unavailable, stop animation production", self.skill)

    def test_main_creates_and_validates_identity_scoped_handoff(self):
        for phrase in (
            "animation-handoff.json",
            "validate_animation_handoff.py",
            "project_id",
            "asset_id",
            "asset_version",
            "model_sha256",
            "rig_signature",
        ):
            self.assertIn(phrase, self.skill + self.animation + self.brief)

    def test_main_remains_approval_and_integration_owner(self):
        for phrase in (
            "`fjzm` remains the approval owner",
            "single animation writer",
            "return to `$fjzm`",
            "geometry or rig-topology change",
        ):
            self.assertIn(phrase, self.animation)

    def test_specialist_result_must_return_before_effect_binding(self):
        self.assertIn("animation-result.json", self.skill)
        self.assertIn("Do not bind particles, audio, hitboxes, or projectiles to a changed rig before the result returns", self.animation)

    def test_combat_assets_require_validated_behavior_orchestration(self):
        for phrase in (
            "motion_domain: combat",
            "combat-behavior-system.json",
            "validate_combat_behavior.py",
            "weapon profiles",
            "distance and eye-height",
            "weighted",
            "hit and whiff",
            "interrupt cleanup",
        ):
            self.assertIn(phrase, self.skill + self.animation)

    def test_main_owns_runtime_combat_selection_and_gameplay_truth(self):
        self.assertIn("`$fjzm` owns runtime combat selection", self.animation)
        self.assertIn("server-authoritative", self.animation)

    def test_main_loads_a_dedicated_combat_runtime_adapter_contract(self):
        self.assertTrue(COMBAT_RUNTIME_INTEGRATION.exists())
        self.assertIn("Read [combat-runtime-integration.md](references/combat-runtime-integration.md)", self.skill)
        for phrase in (
            "eligible_series",
            "deterministic seed",
            "action registration",
            "server-authoritative",
            "hit confirm",
            "multiplayer",
            "save and reload",
            "implementation_status",
        ):
            self.assertIn(phrase, self.combat_runtime)


class TextureSubskillBindingPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.gates = QUALITY_GATES.read_text(encoding="utf-8")
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.all_text = cls.skill + cls.gates + cls.brief

    def test_detailed_texturing_requires_the_specialist_subskill(self):
        self.assertIn("**REQUIRED SUB-SKILL:** Use fjzm-texture", self.skill)
        self.assertIn("If `fjzm-texture` is unavailable, stop detailed texture production", self.skill)

    def test_graybox_requires_actual_user_approval_before_uv_and_texture(self):
        for phrase in (
            "actual Blockbench graybox",
            "front, side, back, top, and three-quarter",
            "explicit user graybox approval",
            "Silence is not graybox approval",
        ):
            self.assertIn(phrase, self.gates)

    def test_geometry_and_uv_are_frozen_before_texture_handoff(self):
        for phrase in ("geometry_signature", "uv_signature", "texture-handoff.json", "validate_texture_handoff.py"):
            self.assertIn(phrase, self.all_text)

    def test_main_remains_texture_approval_and_integration_owner(self):
        for phrase in ("`fjzm` remains the texture approval owner", "single texture writer", "return to `$fjzm`"):
            self.assertIn(phrase, self.gates)

    def test_texture_result_blocks_shader_and_release_claims(self):
        self.assertIn("texture-result.json", self.skill)
        self.assertIn("Do not qualify shaders, bundle, or release the asset before the texture result returns", self.gates)


class ApprovalGatePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")

    def test_new_models_require_an_approval_gate(self):
        self.assertIn("## Approval gate", self.skill)
        self.assertIn("explicit user approval", self.skill)

    def test_new_models_default_to_three_concept_variants(self):
        self.assertIn("three distinct Blockbench-feasible concept previews", self.skill)

    def test_blockbench_and_model_generation_are_forbidden_before_approval(self):
        self.assertIn("Do not open or control Blockbench", self.skill)
        self.assertIn("Do not create a `.bbmodel`", self.skill)

    def test_silence_and_delegated_taste_are_not_approval(self):
        self.assertIn("Silence is not approval", self.skill)
        self.assertIn("surprise me", self.skill)

    def test_bypass_requires_an_already_approved_design_anchor(self):
        self.assertIn("already-approved design anchor", self.skill)


class SingleQuestionDialoguePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.dialogue = USER_DIALOGUE.read_text(encoding="utf-8") if USER_DIALOGUE.exists() else ""
        cls.shader = SHADER_COMPATIBILITY.read_text(encoding="utf-8")
        cls.particles = PARTICLE_DESIGN.read_text(encoding="utf-8")
        cls.animation = ANIMATION_SYSTEM.read_text(encoding="utf-8")
        cls.runtime_gate = MODEL_FIRST_RUNTIME_GATE.read_text(encoding="utf-8")
        cls.quality = QUALITY_GATES.read_text(encoding="utf-8")
        cls.all_text = cls.skill + cls.brief + cls.dialogue

    def test_main_routes_all_intake_through_the_dialogue_contract(self):
        self.assertIn("Read [user-dialogue.md](references/user-dialogue.md) before asking anything", self.skill)
        self.assertIn("Ask exactly one user-facing question per turn", self.all_text)
        self.assertIn("Never bundle multiple user decisions into one question", self.all_text)

    def test_remaining_questions_stay_hidden(self):
        self.assertIn("Keep the remaining question queue internal", self.dialogue)
        self.assertIn("Do not show the full questionnaire unless the user asks", self.dialogue)

    def test_questions_use_plain_chinese_and_numbered_choices(self):
        for phrase in (
            "plain Chinese",
            "internet-friendly conversational tone",
            "explain unavoidable jargon in everyday words first",
            "2 or 3 numbered choices",
            "recommended option first",
            "回复序号就行，也可以直接说你的想法。",
        ):
            self.assertIn(phrase, self.dialogue)

    def test_user_can_reply_by_number_name_or_free_text(self):
        self.assertIn("number, option name, or free text", self.dialogue)

    def test_answered_questions_are_not_repeated(self):
        self.assertIn("Do not repeat answered questions", self.dialogue)
        self.assertIn("mark it answered and ask the next unresolved question", self.dialogue)

    def test_old_grouped_question_policy_is_removed(self):
        self.assertNotIn("in at most three grouped questions", self.skill)
        self.assertNotIn("Group them into no more than three concise questions per turn", self.brief)

    def test_specialized_preflight_references_do_not_reintroduce_question_dumps(self):
        self.assertNotIn("Ask these together", self.shader)
        self.assertNotIn("ask compactly about", self.particles)
        for text in (self.shader, self.particles, self.runtime_gate, self.animation, self.quality):
            self.assertIn("one question per turn", text)


class ShaderCompatibilityPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.shader = SHADER_COMPATIBILITY.read_text(encoding="utf-8") if SHADER_COMPATIBILITY.exists() else ""
        cls.concept = CONCEPT_PROMPT.read_text(encoding="utf-8")
        cls.quality = QUALITY_GATES.read_text(encoding="utf-8")

    def test_shader_gate_runs_before_concept_generation(self):
        gate = "Read [shader-compatibility.md](references/shader-compatibility.md) before concepts"
        prompt = "Read [concept-prompt.md](references/concept-prompt.md) before invoking imagegen"
        self.assertIn(gate, self.skill)
        self.assertLess(self.skill.index(gate), self.skill.index(prompt))

    def test_preflight_locks_renderer_shader_and_material_targets(self):
        for phrase in (
            "no-shader fallback",
            "Iris or OptiFine",
            "exact shader-pack name and version",
            "PBR material standard and version",
            "emissive behavior",
            "transparency/render layer",
        ):
            self.assertIn(phrase, self.shader)

    def test_universal_shader_compatibility_claims_are_forbidden(self):
        self.assertIn("Never claim compatibility with all shader packs", self.shader)
        self.assertIn("named targets only", self.shader)

    def test_concept_sheet_avoids_baked_directional_lighting(self):
        for phrase in ("neutral albedo", "painted-in directional highlights", "runtime lighting is not proof"):
            self.assertIn(phrase, self.concept)

    def test_runtime_matrix_covers_dark_bloom_and_transparency_risks(self):
        for phrase in (
            "no_shader_daylight",
            "no_shader_dark",
            "target_shader_daylight",
            "target_shader_dark",
            "bloom_stress",
            "transparency_overlap",
            "crushed blacks",
            "double lighting",
        ):
            self.assertIn(phrase, self.shader + self.quality)

    def test_shader_contract_validator_is_part_of_production(self):
        self.assertTrue(SHADER_CONTRACT_VALIDATOR.exists())
        self.assertIn("shader-contract.json", self.skill)
        self.assertIn("validate_shader_contract.py", self.skill)


class ModProjectBootstrapPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.bootstrap = MOD_PROJECT_BOOTSTRAP.read_text(encoding="utf-8") if MOD_PROJECT_BOOTSTRAP.exists() else ""
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")

    def test_project_status_is_asked_before_model_category(self):
        project_prompt = "Ask whether an authorized Minecraft project exists"
        category_prompt = "Start by asking which top-level model category"
        self.assertIn(project_prompt, self.skill)
        self.assertLess(self.skill.index(project_prompt), self.skill.index(category_prompt))

    def test_missing_project_requires_an_explicit_route_choice_before_model_category(self):
        for phrase in (
            "Require an explicit project route choice before the model category",
            "create_mod_first",
            "model_first",
            "Do not auto-resolve this choice",
        ):
            self.assertIn(phrase, self.skill)

    def test_model_first_route_obeys_a_runtime_risk_stage_ceiling(self):
        for phrase in (
            "runtime risk classification",
            "production ceiling",
            "runtime-neutral source",
            "runtime integration remains deferred",
        ):
            self.assertIn(phrase, self.bootstrap)

    def test_project_route_choice_and_evidence_are_recorded(self):
        for phrase in ('"route_choice"', '"route_choice_evidence"'):
            self.assertIn(phrase, self.brief)

    def test_missing_or_unknown_project_offers_but_does_not_auto_create(self):
        for phrase in (
            "Read [mod-project-bootstrap.md]",
            "offer a minimal Mod shell",
            "explicit project-creation approval",
            "absolute destination path",
            "Never create a project from silence",
        ):
            self.assertIn(phrase, self.skill if phrase.startswith("Read") else self.bootstrap)

    def test_unknown_version_uses_goals_and_official_primary_sources(self):
        for phrase in (
            "user does not know the Minecraft version",
            "latest stable",
            "existing server or modpack",
            "official primary sources",
            "do not guess compatibility",
        ):
            self.assertIn(phrase, self.bootstrap)

    def test_creation_brief_locks_complete_windows_toolchain(self):
        for phrase in (
            "Minecraft version",
            "loader and loader version",
            "mappings",
            "animation runtime and version",
            "namespace and mod_id",
            "Java and Gradle versions",
            "PowerShell 7",
            "gradlew.bat",
            "project-local wrapper",
            "no global install",
            "scripts/validate_mod_project_brief.py",
        ):
            self.assertIn(phrase, self.bootstrap)

    def test_minimal_shell_smoke_test_and_model_first_fallback_are_explicit(self):
        for phrase in (
            "minimal entrypoint",
            "assets/<namespace>",
            "runClient",
            "build",
            "runtime_deferred",
            "model-first",
            "no runtime integration claim",
        ):
            self.assertIn(phrase, self.bootstrap)
        for phrase in ("project_status", "destination_path", "compatibility_evidence", "runtime_deferred"):
            self.assertIn(phrase, self.brief)

    def test_create_mod_route_asks_minecraft_version_before_every_other_detail(self):
        for phrase in (
            "the first question must ask for the target Minecraft version",
            "No loader, Java, workspace, model, GUI, or asset question may appear before it",
            "你要做哪个 Minecraft 版本的 Mod？",
        ):
            self.assertIn(phrase, self.bootstrap + self.dialogue if hasattr(self, "dialogue") else self.bootstrap)

    def test_newer_java_is_preserved_but_must_be_proven_compatible(self):
        for phrase in (
            "Never uninstall or downgrade a newer JDK",
            "installed JDK is a candidate, not automatic proof",
            "must not be below the required minimum Java major",
            "newer Java may still be incompatible with the pinned Gradle wrapper or loader plugin",
            "side-by-side JDK",
        ):
            self.assertIn(phrase, self.bootstrap)

    def test_java_policy_links_primary_gradle_compatibility_sources(self):
        self.assertIn("https://docs.gradle.org/current/userguide/compatibility.html", self.bootstrap)
        self.assertIn("https://docs.gradle.org/current/userguide/toolchains.html", self.bootstrap)


class WindowsUtf8RedGatePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.bootstrap = MOD_PROJECT_BOOTSTRAP.read_text(encoding="utf-8")
        cls.utf8 = WINDOWS_UTF8_PREFLIGHT.read_text(encoding="utf-8") if WINDOWS_UTF8_PREFLIGHT.exists() else ""

    def test_utf8_gate_is_red_and_runs_before_project_source_generation(self):
        self.assertIn("Read [windows-utf8-preflight.md](references/windows-utf8-preflight.md)", self.skill)
        for phrase in (
            "severity: red",
            "before any Mod source, model, GUI, texture, animation, or localized resource is created",
            "Fail closed",
            "encoding-preflight.json",
        ):
            self.assertIn(phrase, self.utf8)

    def test_utf8_gate_covers_every_windows_text_boundary(self):
        for phrase in (
            "PowerShell 7",
            "UTF-8 without BOM",
            "LF line endings",
            "-Dfile.encoding=UTF-8",
            "JavaCompile",
            "Chinese sentinel",
            "strict UTF-8 decode scan",
            "console input and output",
        ):
            self.assertIn(phrase, self.utf8)

    def test_utf8_gate_has_a_machine_validator_and_two_phases(self):
        self.assertTrue(UTF8_PREFLIGHT_VALIDATOR.exists())
        self.assertIn("host_passed", self.utf8)
        self.assertIn("project_passed", self.utf8)
        self.assertIn("custom project files remain blocked", self.utf8)

    def test_utf8_gate_links_the_primary_openjdk_specification(self):
        self.assertIn("https://openjdk.org/jeps/400", self.utf8)


class GuiConceptPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.gui = GUI_DESIGN.read_text(encoding="utf-8") if GUI_DESIGN.exists() else ""
        cls.workspace = ASSET_WORKSPACE.read_text(encoding="utf-8")

    def test_gui_requests_require_three_imagegen_theme_previews(self):
        self.assertIn("Read [gui-design.md](references/gui-design.md)", self.skill)
        for phrase in (
            "REQUIRED SUB-SKILL: use imagegen",
            "three distinct Minecraft-faithful GUI theme previews",
            "Theme A",
            "Theme B",
            "Theme C",
            "explicit GUI approval",
        ):
            self.assertIn(phrase, self.gui)

    def test_gui_preview_is_minecraft_specific_and_implementation_faithful(self):
        for phrase in (
            "Minecraft pixel-art language",
            "target GUI scale",
            "slot grid",
            "nine-slice",
            "no web-dashboard styling",
            "screen-to-texture manifest",
            "actual in-game screenshot",
        ):
            self.assertIn(phrase, self.gui)

    def test_approved_gui_and_model_images_share_one_project_preview_folder(self):
        for phrase in (
            "design/approved-previews/",
            "model__",
            "gui__",
            "approval-index.json",
        ):
            self.assertIn(phrase, self.gui + self.workspace)


class ImageProductionSystemPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.system = IMAGE_PRODUCTION.read_text(encoding="utf-8") if IMAGE_PRODUCTION.exists() else ""
        cls.workspace = ASSET_WORKSPACE.read_text(encoding="utf-8")
        cls.dialogue = USER_DIALOGUE.read_text(encoding="utf-8")

    def test_asset_scope_is_confirmed_in_text_without_a_preview_image(self):
        for phrase in (
            "text-only asset scope confirmation",
            "Do not generate an asset-overview image",
            "first user-visible image batch",
            "A/B/C",
        ):
            self.assertIn(phrase, self.system)

    def test_first_image_batch_is_exactly_three_separate_choice_calls(self):
        for phrase in (
            "exactly three separate imagegen calls",
            "Variant A",
            "Variant B",
            "Variant C",
            "Do not show a partial A/B/C batch",
            "round-001__concept-choice",
        ):
            self.assertIn(phrase, self.system)

    def test_three_choices_share_one_quality_floor_and_have_no_filler(self):
        for phrase in (
            "same quality floor",
            "No sacrificial option",
            "recolor",
            "reduced detail",
            "regenerate only the failed candidate before showing the batch",
        ):
            self.assertIn(phrase, self.system)

    def test_model_preview_requires_complete_view_and_action_matrix(self):
        for phrase in (
            "front",
            "back",
            "left side",
            "right side",
            "top",
            "bottom",
            "three-quarter",
            "action/keyframe sheet",
            "exact same geometry, proportions, cube inventory, and texture",
        ):
            self.assertIn(phrase, self.system)

    def test_image_rounds_are_persistent_versioned_and_non_overwriting(self):
        for phrase in (
            "design/image-rounds/",
            "image-production-index.json",
            "prompt.md",
            "negative-prompt.md",
            "manifest.json",
            "review.json",
            "approval-evidence",
            "Never overwrite",
            "SHA-256",
        ):
            self.assertIn(phrase, self.system + self.workspace)

    def test_round_states_and_cross_conversation_resume_are_explicit(self):
        for phrase in (
            "queued",
            "generated",
            "shown",
            "revision_requested",
            "approved",
            "superseded",
            "highest-priority unresolved round",
            "future conversation",
        ):
            self.assertIn(phrase, self.system)

    def test_theme_lock_precedes_asset_and_gui_detail_rounds(self):
        for phrase in (
            "A/B/C",
            "theme lock",
            "per-asset detail rounds",
            "screen-specific GUI detail rounds",
            "one active approval question",
        ):
            self.assertIn(phrase, self.system + self.dialogue)

    def test_gui_and_model_sheets_are_generated_as_separate_rounds(self):
        self.assertIn("Do not combine model sheets and GUI screens in one image", self.system)
        self.assertIn("Read [image-production-system.md]", self.skill)


class AssetPresentationPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.presentation = ASSET_PRESENTATION.read_text(encoding="utf-8") if ASSET_PRESENTATION.exists() else ""
        cls.gates = QUALITY_GATES.read_text(encoding="utf-8")

    def test_every_mod_asset_has_the_four_required_information_layers(self):
        for phrase in (
            "item or asset display name",
            "gray and italic Mod display name",
            "usage instruction",
            "theme-consistent flavor text",
        ):
            self.assertIn(phrase, self.presentation)

    def test_styling_supports_color_layout_and_chuunibyou_modes(self):
        for phrase in (
            "themed serious",
            "light chuunibyou",
            "full chuunibyou",
            "color token",
            "line order",
            "wrap width",
        ):
            self.assertIn(phrase, self.presentation)

    def test_random_text_uses_an_approved_pool_without_per_frame_flicker(self):
        for phrase in (
            "approved curated pool",
            "4 to 8",
            "stable_per_stack",
            "must not change every rendered frame",
        ):
            self.assertIn(phrase, self.presentation)

    def test_text_is_localizable_and_not_baked_into_final_textures(self):
        for phrase in (
            "translation_key",
            "item.<mod_id>.<asset_id>",
            "tooltip.<mod_id>.<asset_id>.use",
            "runtime-rendered",
            "Do not bake final UI text into model or GUI textures",
        ):
            self.assertIn(phrase, self.presentation)

    def test_non_item_assets_use_an_appropriate_presentation_surface(self):
        for phrase in (
            "tooltip",
            "gui_info_panel",
            "hud",
            "boss_bar",
            "catalog",
        ):
            self.assertIn(phrase, self.presentation)

    def test_main_flow_and_release_gate_require_validation(self):
        self.assertIn("Read [asset-presentation.md]", self.skill)
        self.assertIn("scripts/validate_asset_presentation.py", self.skill + self.gates)
        self.assertTrue(ASSET_PRESENTATION_VALIDATOR.is_file())


class ModelFirstRuntimeGatePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.bootstrap = MOD_PROJECT_BOOTSTRAP.read_text(encoding="utf-8")
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.gate = MODEL_FIRST_RUNTIME_GATE.read_text(encoding="utf-8") if MODEL_FIRST_RUNTIME_GATE.exists() else ""

    def test_skill_routes_model_first_through_a_validated_runtime_contract(self):
        for phrase in (
            "Read [model-first-runtime-gate.md]",
            "runtime-contract.json",
            "scripts/validate_runtime_contract.py",
        ):
            self.assertIn(phrase, self.skill)

    def test_mod_creation_is_not_universally_forced_but_risk_is_classified(self):
        for phrase in (
            "Do not force Mod creation for every asset",
            "low",
            "medium",
            "high",
            "static decorative",
            "complex animated entity",
            "animated block entity",
            "projectile",
            "multiplayer synchronization",
        ):
            self.assertIn(phrase, self.gate)

    def test_high_risk_model_first_requires_declining_mod_first_and_accepting_risk(self):
        for phrase in (
            "create_mod_first is the default recommendation",
            "verbatim decline evidence",
            "explicit risk acceptance",
            "integration rework may be required",
            "no game-ready claim",
        ):
            self.assertIn(phrase, self.gate)

    def test_unknown_critical_runtime_fields_limit_work_to_concept_or_graybox(self):
        for phrase in (
            "concept_only",
            "graybox_only",
            "runtime_neutral_source",
            "platform-specific export",
            "Do not create a final rig",
        ):
            self.assertIn(phrase, self.gate)

    def test_contract_locks_runtime_role_and_cross_system_ids(self):
        for phrase in (
            "asset_role",
            "render_path",
            "rig_signature",
            "animation_ids",
            "event_ids",
            "locator_ids",
            "projectile_spawn",
            "integration-map.json",
        ):
            self.assertIn(phrase, self.gate + self.brief)

    def test_runtime_contract_validator_is_shipped(self):
        self.assertTrue(RUNTIME_CONTRACT_VALIDATOR.is_file())


class TextureQualityPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.gates = QUALITY_GATES.read_text(encoding="utf-8")

    def test_initial_brief_asks_for_resolution_and_texel_density(self):
        self.assertIn("texture resolution and texel density", self.skill)

    def test_brief_defines_texture_quality_tiers(self):
        for phrase in (
            "64x64 minimum",
            "128x128 standard",
            "256x256 detailed",
            "512x512 ultra",
            "1024x1024 and above",
        ):
            self.assertIn(phrase, self.brief)

    def test_skill_explains_tradeoffs_and_assesses_necessity(self):
        self.assertIn("Explain what low resolution loses and what high resolution costs", self.skill)
        self.assertIn("Assess whether high resolution is necessary", self.skill)

    def test_high_resolution_cannot_be_fake_upscaling(self):
        self.assertIn("Do not upscale a low-resolution texture", self.gates)

    def test_high_resolution_has_material_quality_acceptance(self):
        for phrase in (
            "consistent texel density",
            "efficient UV use",
            "readable material separation",
            "deliberate highlights, shadows, and wear",
            "identity details at gameplay distance",
        ):
            self.assertIn(phrase, self.gates)

    def test_recommendations_never_silently_drop_below_minimum(self):
        self.assertIn("Do not recommend below 64x64", self.brief)

    def test_each_recommendation_states_the_complete_texture_contract(self):
        self.assertIn(
            "atlas dimensions, texels per Blockbench unit, tradeoffs, necessity rationale, and quality commitment",
            self.skill,
        )

    def test_main_skill_pins_texture_tiers_and_floor(self):
        for phrase in (
            "64x64 minimum/1 texel per unit",
            "128x128 standard/1",
            "256x256 detailed/2",
            "512x512 ultra/4",
            "Do not recommend below 64x64",
        ):
            self.assertIn(phrase, self.skill)


class ConceptPromptPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.prompt = CONCEPT_PROMPT.read_text(encoding="utf-8") if CONCEPT_PROMPT.exists() else ""
        cls.gates = QUALITY_GATES.read_text(encoding="utf-8")

    def test_skill_requires_the_prompt_template_before_image_generation(self):
        self.assertIn("Read [concept-prompt.md]", self.skill)
        self.assertIn("before invoking imagegen", self.skill)

    def test_prompt_uses_model_sheet_views_and_cross_view_consistency(self):
        for phrase in (
            "Blockbench viewport-style model sheet",
            "front, back, left side, right side, top, bottom, and three-quarter",
            "same proportions and part count across every view",
            "action/keyframe sheet",
        ):
            self.assertIn(phrase, self.prompt)

    def test_prompt_limits_visible_design_to_buildable_geometry(self):
        for phrase in (
            "cuboids/boxes",
            "no smooth sculpting",
            "do not depict any visible feature that is absent from the build manifest",
        ):
            self.assertIn(phrase, self.prompt)

    def test_prompt_pins_texture_rendering_and_forbids_cinematic_cheats(self):
        for phrase in (
            "atlas dimensions",
            "texels per Blockbench unit",
            "nearest-neighbor pixel texture",
            "no cinematic perspective",
            "no depth of field",
            "no bloom",
            "no particles",
        ):
            self.assertIn(phrase, self.prompt)

    def test_prompt_generates_separate_unlabelled_variants(self):
        self.assertIn("Generate each variant as a separate image", self.prompt)
        self.assertIn("Do not embed A/B/C labels or any text", self.prompt)

    def test_prompt_forbids_quality_sacrifice_and_partial_choice_batches(self):
        for phrase in (
            "exactly three separate imagegen calls",
            "same quality floor",
            "No sacrificial option",
            "not merely a recolor",
            "Do not show Variant A early",
        ):
            self.assertIn(phrase, self.prompt)

    def test_prompt_separates_runtime_effects_from_model_geometry(self):
        self.assertIn("runtime-only effects are excluded from the model sheet", self.prompt)

    def test_gate_rejects_unbuildable_preview_details(self):
        self.assertIn("concept-to-build manifest", self.gates)
        self.assertIn("regenerate the preview before showing it", self.gates)
        self.assertIn("selected preview and its manifest become the design contract", self.gates)


class CategoryRoutingPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.categories = MODEL_CATEGORIES.read_text(encoding="utf-8") if MODEL_CATEGORIES.exists() else ""
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")

    def test_skill_starts_with_category_routing(self):
        self.assertIn("Read [model-categories.md]", self.skill)
        self.assertIn("Start by asking which top-level model category", self.skill)

    def test_opening_uses_progressive_disclosure_and_free_text(self):
        for phrase in (
            "Show only the compact top-level menu",
            "expand only the selected branch",
            "free-text description",
        ):
            self.assertIn(phrase, self.skill)

    def test_taxonomy_covers_major_minecraft_model_families(self):
        for heading in (
            "Entities and characters",
            "Weapons and combat equipment",
            "Wearables and equipment",
            "Items and resources",
            "Blocks and world components",
            "Machines, redstone, and automation",
            "Buildings and structures",
            "Furniture and interior props",
            "Vehicles and mounts",
            "Plants, terrain, and environment",
            "Magic, projectiles, and effect carriers",
            "Technical and display models",
        ):
            self.assertIn(heading, self.categories)

    def test_taxonomy_covers_gameplay_and_genre_routes(self):
        for route in (
            "Survival and vanilla+",
            "RPG and adventure",
            "Redstone and technical Minecraft",
            "Technology and industry",
            "Magic and fantasy",
            "Horror and dark fantasy",
            "Military and warfare",
            "Decoration and role-play",
        ):
            self.assertIn(route, self.categories)

    def test_category_choice_does_not_bypass_design_approval(self):
        self.assertIn("A category choice is not design approval", self.categories)
        self.assertIn("Continue the full brief", self.categories)

    def test_skill_description_exposes_broader_scope(self):
        for phrase in ("weapons", "items", "machines", "furniture", "structures", "vehicles"):
            self.assertIn(phrase, self.skill.split("---", 2)[1])

    def test_model_spec_can_record_the_broader_category(self):
        self.assertIn(
            '"purpose": "entity | wearable | item | block | block_entity | structure | furniture | vehicle | environment | display"',
            self.brief,
        )
        self.assertIn('"category":', self.brief)
        self.assertIn('"genre_route":', self.brief)


class AssetEcosystemPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.ecosystem = ASSET_ECOSYSTEM.read_text(encoding="utf-8") if ASSET_ECOSYSTEM.exists() else ""
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.prompt = CONCEPT_PROMPT.read_text(encoding="utf-8")

    def test_related_asset_expansion_is_required_before_concepts(self):
        self.assertIn("Read [asset-ecosystem.md]", self.skill)
        self.assertIn("before concepts", self.skill)

    def test_opening_asks_single_asset_or_approved_asset_set(self):
        for phrase in (
            "single asset or an approved asset set",
            "primary asset",
            "approved | declined | deferred",
            "Do not auto-add related assets",
        ):
            self.assertIn(phrase, self.ecosystem)

    def test_expansion_covers_combat_function_world_and_presentation_assets(self):
        for phrase in (
            "weapons, ammunition, projectiles",
            "bases, mounts, controllers, containers",
            "summons, minions, drops, loot",
            "damaged variants, detachable debris, effect carriers",
        ):
            self.assertIn(phrase, self.ecosystem)

    def test_every_related_asset_keeps_independent_identity_and_scope_approval(self):
        for phrase in (
            "independent asset_id",
            "relationship",
            "scope approval evidence",
            "suggestion is not production approval",
        ):
            self.assertIn(phrase, self.ecosystem)
        self.assertIn('"related_assets"', self.brief)
        self.assertIn('"scope_status": "suggested | approved | declined | deferred"', self.brief)

    def test_concept_images_cannot_smuggle_in_unapproved_related_assets(self):
        self.assertIn("Do not include an unapproved related asset", self.prompt)
        self.assertIn("approved asset set", self.prompt)

    def test_imagegen_is_blocked_until_related_and_damage_scope_are_answered(self):
        gate = "Do not invoke imagegen until related-asset scope and damage/destruction scope are explicitly answered"
        invocation = "before invoking imagegen"
        self.assertIn(gate, self.skill)
        self.assertIn(invocation, self.skill)
        self.assertLess(self.skill.index(gate), self.skill.index(invocation))

    def test_pre_image_confirmation_is_shown_to_the_user(self):
        for phrase in (
            "Before image generation, show the user a confirmation table",
            "primary asset",
            "approved related assets",
            "damage/destruction scope",
            "explicitly answered not applicable",
        ):
            self.assertIn(phrase, self.ecosystem)

    def test_prompt_injects_approved_ecosystem_and_damage_requirements(self):
        for field in (
            "{APPROVED_RELATED_ASSETS}",
            "{DAMAGE_DESTRUCTION_REQUIREMENTS}",
            "{REQUIRED_PREVIEW_SHEETS}",
        ):
            self.assertIn(field, self.prompt)

    def test_every_variant_visually_shows_all_approved_requirements(self):
        for phrase in (
            "Every A/B/C package must visibly demonstrate all approved requirements",
            "primary model sheet",
            "related-asset sheet",
            "damage/destruction keyframe sheet",
            "Do not replace a required visual sheet with text",
        ):
            self.assertIn(phrase, self.prompt)

    def test_generated_packages_are_presented_to_the_user_before_selection(self):
        for phrase in (
            "Present the generated packages to the user in A, then B, then C order",
            "requirements-to-image checklist",
            "ask the user to select or revise only after all required images are visible",
        ):
            self.assertIn(phrase, self.prompt)


class AssetWorkspacePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.workspace = ASSET_WORKSPACE.read_text(encoding="utf-8") if ASSET_WORKSPACE.exists() else ""
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.ecosystem = ASSET_ECOSYSTEM.read_text(encoding="utf-8")

    def test_workspace_route_is_required_before_concepts(self):
        self.assertIn("Read [asset-workspace.md]", self.skill)
        self.assertIn("before concepts", self.skill)

    def test_user_only_selects_the_windows_drive(self):
        for phrase in (
            "Ask only for the Windows drive letter",
            "Do not ask the user for a parent folder",
            "Do not choose a drive for the user",
            "D:\\FJZM-Projects\\<project_id>",
        ):
            self.assertIn(phrase, self.workspace)

    def test_one_large_project_folder_contains_mod_models_and_all_supporting_assets(self):
        for folder in (
            "mod/",
            "assets/models/",
            "design/image-rounds/",
            "design/image-production-index.json",
            "design/approved-previews/",
            "gui/",
            "contracts/",
            "evidence/",
            "backups/",
        ):
            self.assertIn(folder, self.workspace)

    def test_each_independent_model_has_one_isolated_folder(self):
        for phrase in (
            "one independent folder per model",
            "each independent `.bbmodel`",
            "sibling folder",
            "Never mix two asset_id values in one asset folder",
        ):
            self.assertIn(phrase, self.workspace)

    def test_folder_creation_does_not_bypass_model_approval(self):
        for phrase in (
            "Create the unified project folder only after explicit project-creation approval",
            "folder creation is not model-generation approval",
            "Before concept approval, store only consultation and concept materials",
            "Do not create `.bbmodel`, final textures, rigs, or animations before concept approval",
        ):
            self.assertIn(phrase, self.workspace)

    def test_asset_folder_has_a_stable_internal_layout(self):
        for folder in (
            "consultation/",
            "concepts/",
            "source/",
            "textures/",
            "animations/",
            "audio/",
            "particles/",
            "previews/",
            "exports/",
            "evidence/",
        ):
            self.assertIn(folder, self.workspace)

    def test_windows_path_creation_is_literal_safe_and_non_overwriting(self):
        for phrase in (
            "unused destination",
            "do not overwrite, merge, or silently reuse",
            "versioned sibling path",
            "PowerShell 7",
            "New-Item -ItemType Directory -LiteralPath",
            "resolved destination remains inside the approved root",
        ):
            self.assertIn(phrase, self.workspace)

    def test_model_spec_records_approved_asset_workspace(self):
        for phrase in (
            '"project_workspace"',
            '"asset_workspace"',
            '"drive"',
            '"approved_root"',
            '"asset_folder"',
            '"path_approval_evidence"',
        ):
            self.assertIn(phrase, self.brief)

    def test_pre_image_confirmation_shows_the_storage_folder(self):
        self.assertIn("asset storage folder", self.ecosystem)

class ParticleDesignPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.gates = QUALITY_GATES.read_text(encoding="utf-8")
        cls.particles = PARTICLE_DESIGN.read_text(encoding="utf-8") if PARTICLE_DESIGN.exists() else ""

    def test_particle_requirements_trigger_a_conditional_design_step(self):
        self.assertIn("Read [particle-design.md]", self.skill)
        self.assertIn("particles or runtime effects are requested or implied", self.skill)

    def test_particle_brief_asks_the_key_design_questions(self):
        for phrase in (
            "purpose/state",
            "emitter bone/group or socket",
            "trigger animation and event time",
            "spawn mode",
            "particle budget and LOD",
            "runtime implementation",
        ):
            self.assertIn(phrase, self.particles)

    def test_particle_contract_pins_spatial_timing_visual_and_budget_fields(self):
        for field in (
            '"effect_id"',
            '"emitter_group"',
            '"local_position"',
            '"local_rotation"',
            '"space"',
            '"follow"',
            '"event"',
            '"time_seconds"',
            '"spawn_mode"',
            '"stop_event"',
            '"retrigger_rule"',
            '"rate_per_second"',
            '"burst_count"',
            '"lifetime_seconds"',
            '"velocity"',
            '"spread_degrees"',
            '"gravity"',
            '"drag"',
            '"collision"',
            '"max_active_particles"',
            '"lod"',
        ):
            self.assertIn(field, self.particles)

    def test_particle_preview_does_not_contaminate_the_model_contract(self):
        for phrase in (
            "clean model sheet remains particle-free",
            "separate effect keyframe preview",
            "must not alter model geometry",
        ):
            self.assertIn(phrase, self.particles)

    def test_particle_runtime_boundary_and_evidence_are_explicit(self):
        self.assertIn("Blockbench .bbmodel does not implement runtime particles", self.particles)
        self.assertIn("particle contract", self.gates)
        self.assertIn("actual target runtime", self.gates)
        self.assertIn("do not claim the effect works from a Blockbench screenshot", self.gates)

    def test_model_spec_records_particle_contracts(self):
        self.assertIn('"particle_contracts":', self.brief)


class AnimationSystemPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.gates = QUALITY_GATES.read_text(encoding="utf-8")
        cls.animation = ANIMATION_SYSTEM.read_text(encoding="utf-8") if ANIMATION_SYSTEM.exists() else ""

    def test_animation_requirements_trigger_the_system_before_concepts(self):
        self.assertIn("Read [animation-system.md]", self.skill)
        self.assertIn("animation is requested or implied", self.skill)
        self.assertIn("before concepts", self.skill)

    def test_animation_inventory_covers_major_asset_families(self):
        for heading in (
            "Entity and boss",
            "Weapon and held item",
            "Machine and block entity",
            "Vehicle and mount",
            "Furniture, door, and structure",
        ):
            self.assertIn(heading, self.animation)

    def test_rig_and_clip_contracts_are_complete(self):
        for field in (
            '"root_group"',
            '"bone_hierarchy"',
            '"pivot"',
            '"default_pose"',
            '"attachment_sockets"',
            '"root_motion_policy"',
            '"animation_id"',
            '"length_seconds"',
            '"loop_mode"',
            '"priority"',
            '"interruptible"',
            '"blend_in_seconds"',
            '"blend_out_seconds"',
            '"phases"',
            '"tracks"',
            '"events"',
            '"contact_constraints"',
            '"clearance_constraints"',
            '"acceptance"',
        ):
            self.assertIn(field, self.animation)

    def test_state_machine_and_transition_contracts_are_complete(self):
        for field in (
            '"states"',
            '"transitions"',
            '"from"',
            '"to"',
            '"trigger"',
            '"guard"',
            '"exit_time"',
            '"cooldown_seconds"',
            '"retrigger_rule"',
            '"cleanup_events"',
        ):
            self.assertIn(field, self.animation)

    def test_animation_events_coordinate_runtime_systems(self):
        for field in (
            '"particle_contract_id"',
            '"sound_event"',
            '"projectile_event"',
            '"damage_window"',
            '"hitbox_event"',
        ):
            self.assertIn(field, self.animation)

    def test_motion_quality_and_runtime_evidence_are_explicit(self):
        for phrase in (
            "anticipation, action, follow-through, and recovery",
            "first and last loop poses",
            "sample every 0.05 seconds",
            "actual Blockbench",
            "actual target runtime",
            "Blockbench animation timeline does not implement gameplay state machines",
        ):
            self.assertIn(phrase, self.animation)

    def test_model_spec_and_quality_gates_use_the_animation_system(self):
        self.assertIn('"animation_system":', self.brief)
        for phrase in (
            "state graph",
            "loop seam",
            "transition matrix",
            "event synchronization",
            "interruption cleanup",
        ):
            self.assertIn(phrase, self.gates)

    def test_animation_system_delivery_is_versionable(self):
        self.assertIn("animation-system.json", self.animation)
        self.assertIn("animation event table", self.animation)

    def test_destructible_assets_require_damage_and_destruction_intake(self):
        for phrase in (
            "Damage and destruction gate",
            "intact → minor damage → major damage → critical → destroyed",
            "impact reaction only | staged damage | full destruction",
            "repair, respawn, persistent wreck, or despawn",
        ):
            self.assertIn(phrase, self.animation)

    def test_damage_system_separates_visual_strategies_and_runtime_health(self):
        for phrase in (
            "texture/emissive swap",
            "revealed damage groups",
            "detachable debris",
            "replacement wreck model",
            "does not implement health or damage calculation",
        ):
            self.assertIn(phrase, self.animation)

    def test_destruction_interrupts_gameplay_events_and_has_collision_evidence(self):
        for phrase in (
            "destruction overrides attack and work states",
            "cancel hitboxes, projectiles, particles, and looping sounds",
            "debris pivots and swept volumes",
            "damage-state and destruction previews",
        ):
            self.assertIn(phrase, self.animation)

    def test_model_spec_records_damage_and_destruction_contract(self):
        for phrase in (
            '"damage_system"',
            '"destructible"',
            '"visual_strategy"',
            '"terminal_state"',
            '"destruction_clip"',
        ):
            self.assertIn(phrase, self.brief)


class AudioIntakePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.brief = MODEL_BRIEF.read_text(encoding="utf-8")
        cls.animation = ANIMATION_SYSTEM.read_text(encoding="utf-8")
        cls.audio = AUDIO_SYSTEM.read_text(encoding="utf-8") if AUDIO_SYSTEM.exists() else ""

    def test_attached_audio_triggers_the_audio_workflow(self):
        self.assertIn("Read [audio-system.md]", self.skill)
        self.assertIn("audio files are attached", self.skill)

    def test_chat_attachment_is_the_primary_intake_method(self):
        for phrase in (
            "drag audio files into the conversation attachment area",
            "WAV, MP3, or OGG",
            "Do not require English filenames",
        ):
            self.assertIn(phrase, self.audio)

    def test_chinese_and_numbered_filenames_are_supported(self):
        for phrase in (
            "Chinese filenames",
            "number-only filenames",
            "user's Chinese description",
            "stable English event ID",
        ):
            self.assertIn(phrase, self.audio)

    def test_original_audio_is_preserved_until_mapping_approval(self):
        for phrase in (
            "Never rename, overwrite, convert, copy, or bind the original attachment before approval",
            "source file",
            "English event ID",
            "animation/state",
            "trigger time or condition",
        ):
            self.assertIn(phrase, self.audio)

    def test_ambiguous_numbered_files_require_preview_and_confirmation(self):
        self.assertIn("preview or inspect each file", self.audio)
        self.assertIn("Do not guess numbered-file meanings", self.audio)
        self.assertIn("explicit user approval of the mapping", self.audio)

    def test_runtime_boundary_and_projectile_impact_are_explicit(self):
        for phrase in (
            "Blockbench keyframes schedule sound events; they do not register or play mod audio by themselves",
            "projectile impact",
            "collision event",
            "not a fixed animation timestamp",
        ):
            self.assertIn(phrase, self.audio)

    def test_audio_contract_is_recorded_with_animation_events(self):
        self.assertIn('"audio_contracts":', self.brief)
        self.assertIn('"sound_event"', self.animation)
        self.assertIn("audio-manifest.json", self.audio)


class CompleteAudioSystemPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.audio = AUDIO_SYSTEM.read_text(encoding="utf-8") if AUDIO_SYSTEM.exists() else ""
        cls.adapters = AUDIO_RUNTIME_ADAPTERS.read_text(encoding="utf-8") if AUDIO_RUNTIME_ADAPTERS.exists() else ""

    def test_skill_routes_to_executable_audio_tools_and_runtime_adapters(self):
        for phrase in (
            "scripts/audio_pipeline.py",
            "scripts/validate_audio_manifest.py",
            "Read [audio-runtime-adapters.md]",
        ):
            self.assertIn(phrase, self.skill)

    def test_model_and_audio_approvals_are_independent(self):
        for phrase in (
            "Model concept approval and audio mapping approval are independent gates",
            "Changing audio alone does not revoke model approval",
            "timing, rig, or event ownership changes require audio re-approval",
        ):
            self.assertIn(phrase, self.audio)

    def test_bulk_numbered_and_variant_intake_has_explicit_states(self):
        for phrase in (
            "missing number",
            "duplicate filename",
            "unassigned",
            "random variants",
            "confirm only the changed rows",
        ):
            self.assertIn(phrase, self.audio)

    def test_audio_quality_has_quantitative_starting_gates(self):
        for phrase in (
            "peak at or below -1 dBFS",
            "leading silence under 20 ms",
            "within 3 dB",
            "loop seam",
            "These are starting gates, not platform mandates",
        ):
            self.assertIn(phrase, self.audio)

    def test_accessibility_provenance_and_budget_are_required(self):
        for phrase in (
            "subtitle_key",
            "visual_telegraph",
            "generation_model",
            "license_status",
            "source_sha256",
            "max_simultaneous_instances",
            "attenuation_distance",
            "streaming_policy",
        ):
            self.assertIn(phrase, self.audio)

    def test_runtime_matrix_covers_requested_targets_without_guessing_versions(self):
        for phrase in (
            "Fabric",
            "NeoForge",
            "Forge",
            "GeckoLib 4",
            "GeckoLib 5",
            "Bedrock",
            "MCreator",
            "Never infer APIs from a different version",
        ):
            self.assertIn(phrase, self.adapters)

    def test_runtime_adapter_defines_server_client_ownership_and_duplicate_prevention(self):
        for phrase in (
            "server-authoritative gameplay event",
            "client presentation event",
            "one playback owner",
            "multiplayer duplicate",
            "projectile collision",
        ):
            self.assertIn(phrase, self.adapters)

    def test_runtime_adapter_defines_platform_delivery_files(self):
        for phrase in (
            "sounds.json",
            "SoundEvent",
            "sound_definitions.json",
            "client entity",
            "animation controller",
            "workspace procedure",
        ):
            self.assertIn(phrase, self.adapters)

    def test_audio_tools_exist_as_focused_scripts(self):
        self.assertTrue(AUDIO_PIPELINE.exists(), "audio_pipeline.py must exist")
        self.assertTrue(AUDIO_VALIDATOR.exists(), "validate_audio_manifest.py must exist")


class AssetIdentityAndSequencePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.audio = AUDIO_SYSTEM.read_text(encoding="utf-8")
        cls.identity = ASSET_IDENTITY.read_text(encoding="utf-8") if ASSET_IDENTITY.exists() else ""

    def test_skill_locks_asset_identity_before_model_or_audio_work(self):
        self.assertIn("Read [asset-identity.md]", self.skill)
        self.assertIn("lock the target asset before creating or binding files", self.skill)

    def test_identity_never_comes_from_transient_ui_or_similarity(self):
        self.assertIn(
            "Never use the active Blockbench tab, newest file, attachment order, or visual similarity as identity",
            self.identity,
        )

    def test_each_model_has_a_complete_stable_identity(self):
        for phrase in (
            '"project_id"',
            '"asset_id"',
            '"asset_version"',
            '"model_spec_sha256"',
            '"rig_signature"',
            '"display_name_zh"',
        ):
            self.assertIn(phrase, self.identity)

    def test_multi_model_outputs_are_isolated_by_asset(self):
        for phrase in (
            "one bundle directory per asset_id",
            "Do not reuse another model's model-spec.json",
            "cross-model binding is a blocking error",
            "shared_audio_library",
        ):
            self.assertIn(phrase, self.identity)

    def test_audio_sequence_is_exact_and_non_skippable(self):
        for step in (
            "asset_identity_locked",
            "attachments_inventoried",
            "sources_inspected",
            "mapping_proposed",
            "mapping_approved",
            "copies_converted",
            "events_registered",
            "animation_bound",
            "manifest_validated",
            "runtime_tested",
        ):
            self.assertIn(step, self.identity)
        self.assertIn("Never skip, reorder, or retroactively mark a step complete", self.identity)

    def test_user_facing_mapping_always_names_the_target_model(self):
        for phrase in (
            "project_id / asset_id / asset_version",
            "model display name",
            "target model",
            "Do not show an audio mapping table without its asset identity header",
        ):
            self.assertIn(phrase, self.identity)

    def test_model_change_invalidates_only_affected_bindings(self):
        for phrase in (
            "rig_signature changes",
            "event table changes",
            "mark affected audio bindings stale",
            "do not silently retarget them",
        ):
            self.assertIn(phrase, self.identity)


class ReleaseCandidatePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.bundle = ASSET_BUNDLE.read_text(encoding="utf-8") if ASSET_BUNDLE.exists() else ""
        cls.release = RELEASE_QUALIFICATION.read_text(encoding="utf-8") if RELEASE_QUALIFICATION.exists() else ""
        cls.runtime = RUNTIME_DELIVERY.read_text(encoding="utf-8") if RUNTIME_DELIVERY.exists() else ""
        cls.project = PROJECT_INTEGRATION.read_text(encoding="utf-8") if PROJECT_INTEGRATION.exists() else ""

    def test_skill_routes_unified_validation_migration_and_release_gate(self):
        for phrase in (
            "scripts/validate_asset_bundle.py",
            "scripts/migrate_audio_manifest.py",
            "Read [release-qualification.md]",
        ):
            self.assertIn(phrase, self.skill)

    def test_bundle_contract_covers_every_resource_family_and_evidence(self):
        for phrase in (
            "model geometry",
            "texture and emissive texture",
            "animation system and event table",
            "particle contracts",
            "audio manifest",
            "runtime integration files",
            "input_hashes",
            "output_hashes",
            "approval_evidence",
            "tool_version",
        ):
            self.assertIn(phrase, self.bundle)

    def test_release_support_claims_are_evidence_tiered(self):
        for phrase in (
            "verified support",
            "compatible support",
            "experimental support",
            "Never promote a runtime by documentation alone",
        ):
            self.assertIn(phrase, self.release)

    def test_formal_release_requires_real_end_to_end_evidence(self):
        for phrase in (
            "actual Blockbench",
            "single-player",
            "dedicated server",
            "two clients",
            "two models in one project",
            "interrupt and unload",
            "projectile collision",
            "No project means no verified runtime claim",
        ):
            self.assertIn(phrase, self.release)

    def test_skill_routes_runtime_scaffold_and_release_evidence_validator(self):
        for phrase in (
            "Read [runtime-delivery.md]",
            "scripts/scaffold_runtime_delivery.py",
            "scripts/validate_release_evidence.py",
        ):
            self.assertIn(phrase, self.skill)

    def test_runtime_contract_cannot_fabricate_verified_status(self):
        for phrase in (
            "qualification_status: unverified",
            "status: not_run",
            "Never invent",
            "saved_sha256",
            "reopened_sha256",
            "project commit",
            "build artifact",
        ):
            self.assertIn(phrase, self.runtime)

    def test_runtime_contract_uses_stable_machine_case_ids(self):
        for case_id in (
            "actual_blockbench",
            "single_player",
            "dedicated_server_two_clients",
            "two_models_one_project",
            "interrupt_and_unload",
            "projectile_collision",
        ):
            self.assertIn(case_id, self.runtime)

    def test_release_gate_requires_the_executable_evidence_validator(self):
        for phrase in (
            "validate_release_evidence.py",
            "scaffold_runtime_delivery.py",
            "exact saved and reopened `.bbmodel` hash",
            "compiled build artifact",
        ):
            self.assertIn(phrase, self.release)

    def test_skill_routes_project_inspection_and_multi_asset_validation(self):
        for phrase in (
            "Read [project-integration.md]",
            "scripts/inspect_runtime_project.py",
            "scripts/validate_project_index.py",
        ):
            self.assertIn(phrase, self.skill)

    def test_project_inspection_is_read_only_and_evidence_backed(self):
        for phrase in (
            "read-only",
            "Never infer",
            "gradle.properties",
            "fabric.mod.json",
            "manifest.json",
            ".mcreator",
            "sha256",
            "conflicting version",
        ):
            self.assertIn(phrase, self.project)

    def test_project_index_covers_global_collision_claims(self):
        for phrase in (
            "project-index.json",
            "bundle_path",
            "bundle_sha256",
            "animation_id",
            "event_id",
            "effect_id",
            "output_file",
            "same approved shared_audio_library",
        ):
            self.assertIn(phrase, self.project)

    def test_runtime_delivery_requires_inspected_project_profile(self):
        for phrase in (
            "inspect_runtime_project.py",
            "project inspection report",
            "Do not type version fields from memory",
        ):
            self.assertIn(phrase, self.runtime)


class V5ModelWorkshopAndContractFlowPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL_MD.read_text(encoding="utf-8")
        cls.gates = QUALITY_GATES.read_text(encoding="utf-8")
        cls.contractflow = (SKILL_MD.parent / "references" / "contractflow-protocol.md").read_text(encoding="utf-8")

    def test_model_production_requires_model_workshop(self):
        self.assertIn("**REQUIRED SUB-SKILL:** Use fjzm-model", self.skill)
        self.assertIn("If `fjzm-model` is unavailable, stop geometry production", self.skill)

    def test_main_is_the_only_router_and_approval_owner(self):
        for phrase in (
            "sole approval owner",
            "specialists never send peer-to-peer handoffs",
            "ContractFlow v1",
            "capability-index.json",
        ):
            self.assertIn(phrase, self.skill + self.contractflow)

    def test_model_result_precedes_texture_and_animation(self):
        self.assertLess(self.skill.index("model-handoff.json"), self.skill.index("texture-handoff.json"))
        self.assertLess(self.skill.index("model-result.json"), self.skill.index("texture-handoff.json"))
        self.assertLess(self.skill.index("model-result.json"), self.skill.index("animation-handoff.json"))

    def test_three_blockbench_checkpoints_and_runtime_checkpoint_are_required(self):
        for phrase in (
            "geometry graybox checkpoint",
            "textured final checkpoint",
            "animation movement checkpoint",
            "Minecraft runtime checkpoint",
        ):
            self.assertIn(phrase, self.gates)

    def test_fidelity_evidence_requires_views_overlay_hashes_and_thresholds(self):
        for phrase in (
            "front, back, left, right, top, bottom, three-quarter, and gameplay-distance",
            "50% transparent overlay",
            "blocking anchors: 100%",
            "main proportion error: at most 5%",
            "key-part position error: at most 0.5 Blockbench units",
            "symmetric-part error: at most 0.25 Blockbench units",
            "rotation error: at most 3 degrees",
        ):
            self.assertIn(phrase, self.gates)

    def test_auto_repair_is_bounded_and_never_lowers_quality(self):
        for phrase in (
            "initial attempt plus at most two internal retries",
            "Never lower the approved quality target",
            "identity mismatch",
            "preserve every attempt",
        ):
            self.assertIn(phrase, self.contractflow)


if __name__ == "__main__":
    unittest.main()
