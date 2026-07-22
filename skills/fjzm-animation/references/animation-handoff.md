# Animation handoff contract

`animation-handoff.json` is the ContractFlow v1 identity, scope, approval, and write-ownership boundary between `$fjzm` and `$fjzm-animation`. It must route from `$fjzm`; results return only to `$fjzm`.

## Required identity lock

- `project_id`: the authorized Minecraft/Mod project.
- `asset_id`: the exact model inside that project.
- `asset_version`: the input asset version.
- `model_sha256`: SHA-256 of the source `.bbmodel`.
- `model_spec_sha256`: SHA-256 of the approved `model-spec.json`.
- `geometry_signature`: frozen visible geometry.
- `rig_signature`: stable signature for bone names, parents, pivots, and default pose.
- `uv_signature`: frozen UV interface.
- `locator_signature`: frozen locator/interface set.

Never choose a model by filename similarity, recent-file order, display name, or open editor state. All five identity fields must match before work.

## Write ownership

The source is read-only. A handoff grants `$fjzm-animation` a `single writer` lock for exactly one `write_lock_id` and one versioned output path. No other skill or process may write that version concurrently.

Never overwrite the source or write outside the approved model workspace. Record both source and output hashes in the return contract.

## Backend lock

Schema v2 requires exactly one `animation_backend`:

- `blockbench`: `ownership.output_project_path` is a versioned ASCII-safe `.bbmodel`.
- `blender_epicfight`: `ownership.output_project_path` is a versioned ASCII-safe `.blend`; also reserve `output_runtime_directory`, `rig_map_path`, and `action_library_path`. Add `backend_contract` with exact Java/Minecraft/loader/Epic Fight/Blender/exporter versions, official exporter source, target armature, coordinate system, scale, and deterministic-control policy.

Backend selection belongs to `$fjzm` and must be user-approved when it changes cost, quality, dependencies, or delivery. `$fjzm-animation` never switches the route silently. Runtime/action IDs and route-owned relative paths use lowercase ASCII-safe names; Chinese remains allowed in display text.

## Motion-domain lock

Schema v2 also requires one `motion_domain`: `ambient | mechanism | locomotion | combat | interaction | destruction`. This selects validation rules; it does not change the approved backend. For `combat`, set `request.combat_behavior_required: true` and reserve the ASCII-safe `ownership.combat_behavior_path`. The returned animation result must hash the passing `combat-behavior-system.json` before `$fjzm` integrates runtime AI.

## Scope boundary

`standalone_revision` may change only approved animation data such as keyframes, timing, interpolation, event timing, clip metadata, and transition prototypes. It may not change geometry, UV, textures, bone names, bone hierarchy, locators, or bone topology.

If diagnosis reveals a protected change, return to `$fjzm` with the reason and affected dependent assets. In v5, `$fjzm` delegates a new geometry/base-rig version to `$fjzm-model`; animation never modifies the model-owned interface. Any bone topology, origin, hierarchy, locator, or geometry change can require particle, audio, hitbox, projectile, renderer, and controller rebinding.

## Minimum example

```json
{
  "protocol_version": "1.0",
  "message_type": "handoff",
  "message_id": "msg-animation-001",
  "correlation_id": "corr-crystal-tower-001",
  "from_skill": "fjzm",
  "to_skill": "fjzm-animation",
  "stage": "animation",
  "idempotency_key": "energy_defense:crystal_tower:3.0.0:animation:0",
  "attempt": 0,
  "writer_lock": {"owner": "fjzm-animation", "surface": "animation", "output_version": "animation-r1"},
  "dependencies": [{"stage": "geometry", "status": "passed"}],
  "schema_version": 2,
  "project_id": "energy_defense",
  "asset_id": "crystal_tower",
  "asset_version": "3.0.0",
  "mode": "standalone_revision",
  "animation_backend": "blockbench",
  "motion_domain": "mechanism",
  "source": {
    "model_path": "source/crystal_tower.bbmodel",
    "model_sha256": "64-character lowercase sha256",
    "model_spec_path": "model-spec.json",
    "model_spec_sha256": "64-character lowercase sha256",
    "geometry_signature": "geometry-crystal-tower-v1",
    "rig_signature": "rig-crystal-tower-v1",
    "uv_signature": "uv-crystal-tower-v1",
    "locator_signature": "locators-crystal-tower-v1",
    "source_read_only": true
  },
  "request": {
    "animation_ids": ["animation.tower.attack"],
    "issue_report": "shield orbit clips the crystal",
    "allowed_mutations": ["keyframes", "timing", "interpolation", "event_timing"],
    "protected_mutations": ["geometry", "uv", "textures", "bone_names", "bone_hierarchy", "locators"]
  },
  "approval": {"status": "approved", "evidence": "user approval text"},
  "ownership": {
    "writer_skill": "fjzm-animation",
    "single_writer": true,
    "write_lock_id": "crystal-tower-animation-r1",
    "output_project_path": "versions/crystal_tower__animation-r1.bbmodel"
  },
  "integration": {
    "dependent_rebind_required": false,
    "main_change_approval": {"status": "not_required", "evidence": null}
  },
  "return_contract_path": "animation-result.json"
}
```
