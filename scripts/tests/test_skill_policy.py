import unittest
from pathlib import Path


SKILL_MD = Path(__file__).resolve().parents[2] / "SKILL.md"
MODEL_BRIEF = Path(__file__).resolve().parents[2] / "references" / "model-brief.md"
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
            "front, left side, back, and three-quarter",
            "same proportions and part count across every view",
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

    def test_user_selects_windows_drive_and_parent_folder(self):
        for phrase in (
            "Ask which Windows drive and parent folder to use",
            "Do not choose a drive for the user",
            "absolute proposed asset folder",
            "explicit path approval",
        ):
            self.assertIn(phrase, self.workspace)

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
            "Create the dedicated folder after explicit path approval",
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


if __name__ == "__main__":
    unittest.main()
