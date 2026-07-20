# Unified asset bundle and evidence contract

Use one bundle manifest per `project_id / asset_id / asset_version`. Never place two models behind one manifest. The manifest is the final cross-model isolation gate; run `scripts/validate_asset_bundle.py` after the focused validators.

## Required resource families

Declare every delivered resource with a bundle-relative path, kind, and lowercase SHA-256:

- model geometry: editable `.bbmodel` plus required runtime geometry exports;
- texture and emissive texture: approved atlas and any emissive mask;
- animation system and event table: rig contract, clips, state graph, and central event table;
- particle contracts: emitter, timing, lifecycle, budget, and fallback data;
- audio manifest: approved mappings, source/output hashes, subtitles, and runtime registrations;
- runtime integration files: controllers, registries, code/data adapters, localization, and target-specific exports.
- model-first runtime contract: validated `runtime-contract.json` with the approved production ceiling and stable handoff IDs.

Paths must remain inside the bundle root. Embedded JSON identity and `rig_signature` must match the bundle. Animation `sound_event` and `particle_contract_id` references must resolve to the audio manifest and particle contracts.

If `model-spec.json` declares `route_choice: model_first`, the bundle must include a valid `runtime-contract.json`. The bundle remains runtime-deferred: it may contain runtime-neutral sources and contracts, but no verified/runtime-tested claim or platform-specific export until an authorized project is inspected.

## Manifest skeleton

```json
{
  "schema_version": 1,
  "project_id": "energy_defense",
  "asset_id": "crystal_tower",
  "asset_version": "1.0.0",
  "rig_signature": "rig-crystal-tower-v1",
  "resources": [
    {"kind": "model", "path": "model.bbmodel", "sha256": "64 lowercase hex"}
  ],
  "workflow_evidence": []
}
```

## Verifiable workflow evidence

Each completed step records `step`, UTC `timestamp`, `status: verified`, `input_hashes`, `output_hashes`, `approval_evidence`, and `tool_version`. Evidence steps must be an exact ordered prefix of:

1. `asset_identity_locked`
2. `attachments_inventoried`
3. `sources_inspected`
4. `mapping_proposed`
5. `mapping_approved`
6. `copies_converted`
7. `events_registered`
8. `animation_bound`
9. `manifest_validated`
10. `runtime_tested`

An empty hash list is allowed only when a step truly has no file input/output. Approval steps require evidence attributable to the user. Never infer later evidence from an older manifest or retroactively mark runtime work complete.

## Validation command

```powershell
python -X utf8 scripts/validate_asset_bundle.py '.\asset-bundle.json' --bundle-root '.\'
```

Focused model/audio validation passing does not replace this bundle-wide identity, hash, reference, and evidence check.
