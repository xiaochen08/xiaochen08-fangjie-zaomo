# Asset identity, isolation, and operation order

## Core rule

Lock the exact target asset before creating, converting, registering, or binding any model, texture, animation, particle, or audio file. Never use the active Blockbench tab, newest file, attachment order, or visual similarity as identity.

## Stable identity contract

Create one identity record per model:

```json
{
  "project_id": "energy_defense",
  "asset_id": "crystal_tower",
  "asset_version": "1.0.0",
  "display_name_zh": "棱镜水晶防御塔",
  "display_name_en": "Prism Crystal Defense Tower",
  "model_spec_path": "assets/crystal_tower/model-spec.json",
  "model_spec_sha256": "64 lowercase hex characters",
  "model_source_path": "assets/crystal_tower/crystal_tower.bbmodel",
  "model_source_sha256": "64 lowercase hex characters",
  "rig_signature": "rig-crystal-tower-v1",
  "concept_approval_id": "concept-B",
  "status": "identity_locked"
}
```

Use lowercase ASCII `project_id` and `asset_id`. `asset_id` is permanent for the model's identity; increment `asset_version` for delivered revisions. Do not recycle an ID after deletion or rename it to represent a different model.

## Per-model isolation

Use one bundle directory per asset_id:

```text
assets/<asset_id>/
├─ model-spec.json
├─ model.bbmodel
├─ animation-system.json
├─ particle-contracts.json
├─ audio-manifest.json
├─ textures/
├─ sounds/<asset_id>/
└─ evidence/
```

Do not reuse another model's model-spec.json, animation event table, rig signature, locator list, texture atlas, particle emitter, or audio manifest. A cross-model binding is a blocking error, even when two models look alike or share animation names.

Shared audio is allowed only through an explicitly approved `shared_audio_library` entry with its own library ID, version, license, files, and consumers. Copying another model's private sound path is not sharing.

## User-facing target header

Before every concept approval, model edit, audio mapping, conversion, or runtime binding, display:

```text
Target model
Project / Asset / Version: project_id / asset_id / asset_version
model display name: 棱镜水晶防御塔
Model specification: path + short SHA-256
```

Do not show an audio mapping table without its asset identity header. If the user supplies several models or a filename is ambiguous, list candidates and wait for the user to identify the target model; do not choose by recency.

## Required audio operation order

Record `workflow.completed_steps` as an exact prefix of this sequence:

1. `asset_identity_locked` — select project, target model, version, specification hash, and rig signature.
2. `attachments_inventoried` — list all sources without changing them.
3. `sources_inspected` — read-only metadata/audio inspection and hashes.
4. `mapping_proposed` — show source → Chinese meaning → English event → target model binding.
5. `mapping_approved` — capture the user's explicit approval for this asset identity.
6. `copies_converted` — create versioned working/output copies; originals remain unchanged.
7. `events_registered` — register only this asset's sound IDs and subtitles.
8. `animation_bound` — bind to this asset's verified animation/state/collision events and locators.
9. `manifest_validated` — cross-check manifest, model-spec, registry, event table, files, and hashes.
10. `runtime_tested` — verify the identified asset in the actual target runtime and multiplayer when relevant.

Never skip, reorder, or retroactively mark a step complete. A step may be repeated after a correction, but later steps become stale until the corrected step and its dependents are re-run.

For final delivery, encode the same sequence in `asset-bundle.json`. Each evidence row carries its input/output hashes, approval evidence, tool version, status, and timestamp. Run `scripts/validate_asset_bundle.py`; a conversational claim such as “done” is not evidence.

## Binding key

Every effect binding must carry this composite key:

```text
project_id + asset_id + asset_version + event_id + binding_owner
```

Every audio mapping repeats its `asset_id`. Event paths normally begin with that asset ID, for example `mymod:crystal_tower.fire`, and output files stay under `sounds/crystal_tower/`. A generic name such as `mymod:attack` is prohibited unless it belongs to an approved shared library.

## Change and stale-binding rules

When model-spec content, animation IDs, event table, locators, pivots, bone hierarchy, or rig_signature changes, compare old and new contracts. If rig_signature changes or the event table changes, mark affected audio bindings stale and do not silently retarget them. Re-propose only affected rows, obtain approval, then repeat conversion only if the audio file/output requirements changed; always repeat registration/binding validation and runtime testing.

Texture-only changes do not invalidate audio unless the visual telegraph or asset identity changes. Audio-only changes do not invalidate geometry approval.

## Multi-model batch rule

Process batches as separate identity-scoped queues. Finish or explicitly checkpoint one asset's current step before switching. On every switch, reprint the target header and reload paths from its identity record. Never retain an animation ID, locator, output directory, or approval evidence from the previous model in working assumptions.
