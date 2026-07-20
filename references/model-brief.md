# Model brief and motion contract

Create `model-spec.json` in the task workspace before detailed modeling. Keep unknown values explicit; do not disguise guesses as user decisions.

Do not create this production specification until the user has selected a concept. Before approval, keep only a temporary consultation brief and concept prompts; do not create Blockbench artifacts.

## Minimum brief

```json
{
  "project_id": "lowercase_project_id",
  "asset_id": "stable_lowercase_asset_id",
  "asset_version": "semantic_or_project_version",
  "display_name_zh": "user-facing Chinese name",
  "asset_workspace": {
    "drive": "D:",
    "approved_root": "D:\\Minecraft-Blockbench-Models\\project_id",
    "asset_folder": "D:\\Minecraft-Blockbench-Models\\project_id\\asset_id__v1",
    "folder_status": "proposed | created",
    "path_approval_evidence": "verbatim user approval"
  },
  "asset_scope": "single | approved_set",
  "related_assets": [
    {
      "display_name_zh": "related asset name",
      "asset_id": "independent_asset_id_or_null",
      "relationship": "projectile_of | drop_of | mounted_on | variant_of | other",
      "scope_status": "suggested | approved | declined | deferred",
      "scope_approval_evidence": "verbatim user decision or null"
    }
  ],
  "name": "model_name",
  "category": "family and selected subtype from model-categories.md",
  "genre_route": "survival | rpg | technical | technology | magic | horror | military | decoration | mixed",
  "purpose": "entity | wearable | item | block | block_entity | structure | furniture | vehicle | environment | display",
  "minecraft_target": "java | bedrock | unspecified",
  "runtime": "vanilla | geckolib | custom_renderer | unspecified",
  "mod_project": {
    "project_status": "existing | create | runtime_deferred",
    "route_choice": "use_existing | create_mod_first | model_first",
    "route_choice_evidence": "verbatim user choice",
    "project_path": null,
    "destination_path": null,
    "compatibility_evidence": [],
    "brief_path": "mod-project-brief.json | null",
    "runtime_contract": {
      "path": "runtime-contract.json | null",
      "status": "not_required | provisional | validated",
      "runtime_risk": "low | medium | high | unresolved",
      "asset_role": "block | item | entity | block_entity | projectile | wearable | structure | other",
      "render_path": "vanilla_json | entity_renderer | block_entity_renderer | custom_renderer | unresolved",
      "production_ceiling": "concept_only | graybox_only | runtime_neutral_source | platform_export"
    }
  },
  "blockbench_format": "free | bedrock_entity | java_block | other",
  "scale_blocks": {"width": null, "height": null, "depth": null},
  "design_anchor": {"type": "selected_concept | reference | text", "path": null},
  "approval": {
    "status": "explicitly_approved",
    "selected_variant": "A | B | C | approved_reference",
    "evidence": "verbatim user approval message"
  },
  "style": {"shape_language": [], "materials": [], "palette": []},
  "texture_quality": {
    "tier": "minimum | standard | detailed | ultra | exceptional",
    "atlas": [128, 128],
    "texels_per_blockbench_unit": 1,
    "necessity_rationale": "model complexity, viewing distance, hardware, reuse, style"
  },
  "parts": [],
  "animations": [],
  "animation_system": {"path": "animation-system.json", "status": "provisional | approved", "rig_signature": "stable rig contract signature"},
  "damage_system": {
    "destructible": true,
    "intake_choice": "impact_reaction_only | staged_damage | full_destruction | not_applicable",
    "visual_strategy": ["texture_emissive_swap", "revealed_damage_groups", "detachable_debris", "replacement_wreck_model"],
    "states": ["intact", "minor_damage", "major_damage", "critical", "destroyed"],
    "destruction_clip": "animation.asset.destroy or null",
    "terminal_state": "repair | respawn | persistent_wreck | despawn",
    "runtime_health_owner": "target runtime or unresolved"
  },
  "runtime_effects": [],
  "particle_contracts": [],
  "audio_contracts": {
    "manifest": "audio-manifest.json",
    "mapping_status": "unassigned | proposed | approved | changed",
    "mapping_approval_evidence": null,
    "runtime_adapter": "java | bedrock | mcreator | unspecified"
  },
  "acceptance": [],
  "assumptions": [],
  "unresolved_blockers": []
}
```

For each moving part, add a motion contract:

```json
{
  "part": "shield_left",
  "motion": "orbit",
  "parent": "shield_orbit_left",
  "pivot_target": "crystal_center",
  "plane": "horizontal_xz",
  "direction": "clockwise",
  "phase_degrees": 0,
  "radius": 13,
  "minimum_clearance": 2,
  "interpolation": "linear",
  "states": ["activate", "attack", "cooldown", "retract"],
  "interrupt_rule": "restart_cooldown_on_new_attack"
}
```

When particles are required, read `particle-design.md`; add its provisional contract before concept generation and freeze the approved values under `particle_contracts` afterward.

When animation is required, read `animation-system.md`; design the provisional inventory, moving assemblies, state graph, key poses, and events before concepts, then freeze the approved rig/clip/transition contracts in `animation-system.json`.

When sound is required or audio is attached, read `audio-system.md`; inventory untouched sources, present Chinese/numbered-name mappings to stable English IDs, and freeze only approved mappings in `audio-manifest.json` and `audio_contracts`. Model approval and audio mapping approval remain independent; link both evidence records without treating either as the other.

## Decision policy

For a new design, first ask about subject/use, target edition/runtime, scale/proportions, style/material/palette, signature parts, animations/attack behavior, and references. Group them into no more than three concise questions per turn. Generate three Blockbench-feasible visual variants and wait for an explicit selection before production.

## Texture quality decision

Ask the user to choose, or recommend one tier:

| Tier | Atlas starting point | Typical density | Consequence |
|---|---:|---:|---|
| 64x64 minimum | 64x64 | 1 texel/unit | Lowest memory and strong pixel style; little room for seams, wear, small eyes, or layered shading |
| 128x128 standard | 128x128 | 1 texel/unit | Balanced Minecraft look for most medium models |
| 256x256 detailed | 256x256 | 2 texels/unit | Suitable for large bosses, multiple materials, readable cores, and controlled wear |
| 512x512 ultra | 512x512 | 4 texels/unit | More painting work and memory; use only when close viewing and design complexity justify it |

Treat 1024x1024 and above as exceptional. Require explicit justification and warn that each doubling of width and height quadruples pixel count. Atlas size alone does not define detail; record texels per Blockbench unit too.

Do not recommend below 64x64 unless the user explicitly requests a smaller atlas after seeing the loss of readable detail and accepts that exception.

Recommend high resolution only when visible surface area, distinct materials, small identity features, close gameplay distance, and target hardware support it. Prefer lower resolution for small/distant/repeated models, mobile targets, or deliberate vanilla style.

The following are not approval: no reply, urgency, “do it now,” “surprise me,” “decide for me,” a broad reference image, or permission from an earlier unrelated design. Record the user's exact approval message. If the user wants changes, update the concepts and ask again.

Treat these as blocking when they change file format, rig topology, or game integration:

- Java versus Bedrock and the animation runtime
- entity/block/item use case
- self-rotation versus orbit, target pivot, or movement plane
- required animations and attack mechanism
- strict size or performance limits

For `model_first`, read `model-first-runtime-gate.md` before concepts. Freeze the runtime risk intake before images, then create and validate `runtime-contract.json` after concept approval and before detailed production. Its stable `rig_signature`, `animation_ids`, `event_ids`, `locator_ids`, and `projectile_spawn` locator become the later `integration-map.json` inputs.

Treat palette details, minor surface wear, secondary idle motion, and hidden-side decoration as reversible unless the user marks them essential. State the assumption before proceeding.

Urgency and a request for no questions do not convert unknowns into confirmed requirements. Use a neutral `.bbmodel` source when platform is unknown, publish reversible assumptions before work, and withhold platform-specific exports until the target is known. If self-rotation versus orbit, pivot target, or movement plane is ambiguous, stop detailed work at the motion prototype because those choices change the rig.

## Complete example: crystal defense tower

- Purpose: animated block entity; runtime selected before export.
- Design: dark mechanical tower, cyan internal energy carriers, luminous top crystal, two protective wings.
- Texture: 256x256 detailed, 2 texels/unit, justified by the large surface, multiple metals, internal energy parts, and close inspection.
- State flow: idle 2.4 s loop → attack 1.6 s → cooldown 3.0 s → retract 1.25 s → idle.
- Energy: carriers travel bottom-to-top; crystal brightens; the game runtime spawns the projectile at the declared fire event.
- Wings: orbit the crystal center rather than self-rotate; share the exact pivot; rotate in the same direction; maintain 180° separation; active radius 13; elevated retract radius at least 12.5; no interpolated frame may touch the crystal.
- Evidence: editable `.bbmodel`, PNG texture, complete GIF, and actual Blockbench screenshots for attack, cooldown, and retract.

## Validator requirements example

```json
{
  "required_animations": [
    {"name": "animation.tower.idle", "loop": "loop", "min_length": 1.0},
    {"name": "animation.tower.attack", "loop": "once"},
    {"name": "animation.tower.cooldown", "loop": "once", "min_length": 3.0},
    {"name": "animation.tower.retract", "loop": "once"}
  ],
  "required_groups": [
    {"name": "shield_orbit_left", "origin": [0, 69, 0]},
    {"name": "shield_orbit_right", "origin": [0, 69, 0]}
  ]
}
```
