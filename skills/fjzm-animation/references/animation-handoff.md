# Animation handoff contract

`animation-handoff.json` is the identity, scope, approval, and write-ownership boundary between `$fjzm` and `$fjzm-animation`.

## Required identity lock

- `project_id`: the authorized Minecraft/Mod project.
- `asset_id`: the exact model inside that project.
- `asset_version`: the input asset version.
- `model_sha256`: SHA-256 of the source `.bbmodel`.
- `model_spec_sha256`: SHA-256 of the approved `model-spec.json`.
- `rig_signature`: stable signature for bone names, parents, pivots, locators, and default pose.

Never choose a model by filename similarity, recent-file order, display name, or open editor state. All five identity fields must match before work.

## Write ownership

The source is read-only. A handoff grants `$fjzm-animation` a `single writer` lock for exactly one `write_lock_id` and one versioned output path. No other skill or process may write that version concurrently.

Never overwrite the source or write outside the approved model workspace. Record both source and output hashes in the return contract.

## Scope boundary

`standalone_revision` may change only approved animation data such as keyframes, timing, interpolation, event timing, clip metadata, and transition prototypes. It may not change geometry, UV, textures, bone names, bone hierarchy, locators, or bone topology.

If diagnosis reveals a protected change, return to `$fjzm` with the reason and affected dependent assets. `$fjzm` may issue a new `delegated_rig_and_animation` handoff only after explicit main-change approval. Any bone topology, pivot contract, hierarchy, locator, or geometry change can require particle, audio, hitbox, projectile, renderer, and controller rebinding.

## Minimum example

```json
{
  "schema_version": 1,
  "project_id": "energy_defense",
  "asset_id": "crystal_tower",
  "asset_version": "3.0.0",
  "mode": "standalone_revision",
  "source": {
    "model_path": "source/crystal_tower.bbmodel",
    "model_sha256": "64-character lowercase sha256",
    "model_spec_path": "model-spec.json",
    "model_spec_sha256": "64-character lowercase sha256",
    "rig_signature": "rig-crystal-tower-v1",
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
    "output_model_path": "versions/crystal_tower__animation-r1.bbmodel"
  },
  "integration": {
    "dependent_rebind_required": false,
    "main_change_approval": {"status": "not_required", "evidence": null}
  },
  "return_contract_path": "animation-result.json"
}
```
