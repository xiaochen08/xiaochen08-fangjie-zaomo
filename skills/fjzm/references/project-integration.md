# Runtime project inspection and multi-model isolation

## Read-only project inspection

Run project detection before choosing an adapter or filling runtime-delivery fields:

```powershell
python -X utf8 scripts/inspect_runtime_project.py '.\authorized-project' --json-out '.\project-inspection.json'
```

Inspection is read-only. It hashes every marker as `sha256` evidence and does not install, build, edit, rename, or generate inside the project. Never infer a version from memory, a tutorial, the newest release, or a different project.

Supported evidence includes:

- Java: `gradle.properties`, `fabric.mod.json`, Forge/NeoForge TOML markers, and Gradle dependency declarations;
- Bedrock: resource/behavior-pack `manifest.json`, module types, format version, and minimum engine version;
- MCreator: the workspace `.mcreator` generator and version fields.

If exact values disagree, report conflicting version evidence and stop. If multiple runtime types are found, do not choose one automatically. Unknown or missing markers remain blocking for integration code and verified support.

Copy detected values and the project inspection report into runtime-delivery evidence. Do not type version fields from memory.

## Multi-model project index

When two or more models share one mod, pack, workspace, namespace, or output tree, create `project-index.json`:

```json
{
  "schema_version": 1,
  "project_id": "energy_defense",
  "assets": [{
    "asset_id": "crystal_tower",
    "asset_version": "1.0.0",
    "rig_signature": "rig-crystal-tower-v1",
    "bundle_path": "assets/crystal_tower/asset-bundle.json",
    "bundle_sha256": "64 lowercase hex"
  }]
}
```

Run:

```powershell
python -X utf8 scripts/validate_project_index.py '.\project-index.json' --project-root '.\'
```

The validator re-runs unified validation inside every bundle root, cross-checks project/asset/version/rig identity, then builds global claims for `animation_id`, `event_id`, `effect_id`, and `output_file`. Duplicate asset IDs, bundle paths, hashes, cross-model identity, global collisions, or a unique identifier scoped to another known asset are errors.

An `event_id` may overlap only when every owning mapping names the same approved shared_audio_library and sets `shared_audio_approved: true`. Approval on one model never authorizes another. Animation, particle, and output collisions have no implicit sharing exception.

## Safe switching

Before switching assets, save/checkpoint the current model, print the new identity header, reload paths from `project-index.json`, and clear transient assumptions about active Blockbench tabs, locators, event IDs, audio mappings, and output directories. Re-run the project index after any bundle or shared-library change.
